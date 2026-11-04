"""Build the fixed country x product panel and run the complexity measures by year.

A specification (dict) sets: level ("hs4" or "hs6"), threshold (RCA cut-off),
window (moving-average years), exclude (ISO3 codes to drop). See
complexity_methods.md, section "Recommended specification".
"""
import numpy as np
import pandas as pd

import complexity as cx

MAIN_SPEC = {"name": "main", "level": "hs4", "threshold": 1.0, "window": 3, "exclude": []}


def load_exports(cfg, level):
    ex = pd.read_parquet(cfg["output"] / "exports_hs6.parquet")
    if level == "hs4":
        ex["prod"] = ex["hs6"].str[:4]
    elif level == "hs6":
        ex["prod"] = ex["hs6"]
    else:
        raise ValueError(level)
    return ex.groupby(["year", "iso3", "prod"], as_index=False)["v"].sum()


def select_panel(ex, pop, cfg, level, exclude=()):
    """Fixed sets of countries and products, identical in every year."""
    c = cfg["complexity"]
    years = sorted(ex["year"].unique())

    by_cy = ex.groupby(["iso3", "year"])["v"].sum().unstack("year").reindex(columns=years)
    present_all = by_cy.notna().all(axis=1) & (by_cy.fillna(0) > 0).all(axis=1)
    big = by_cy.mean(axis=1) >= c["min_exports_thousand_usd"]
    mean_pop = pop.groupby("iso3")["pop"].mean()
    populous = mean_pop.reindex(by_cy.index) >= c["min_population_thousands"]
    countries = by_cy.index[present_all & big & populous.fillna(False)]
    countries = [x for x in countries if x not in set(exclude)]

    sub = ex[ex["iso3"].isin(countries)]
    by_py = sub.groupby(["prod", "year"])["v"].sum().unstack("year").reindex(columns=years)
    floor = c[f"min_world_exports_{level}"]
    products = by_py.index[(by_py.fillna(0) > 0).all(axis=1) & (by_py.mean(axis=1) >= floor)]
    return sorted(countries), sorted(products), years


def to_cube(ex, countries, products, years):
    """Array years x countries x products, zeros for missing flows."""
    sub = ex[ex["iso3"].isin(countries) & ex["prod"].isin(products)]
    idx = pd.MultiIndex.from_product([years, countries, products], names=["year", "iso3", "prod"])
    s = sub.set_index(["year", "iso3", "prod"])["v"].reindex(idx, fill_value=0.0)
    return s.to_numpy().reshape(len(years), len(countries), len(products))


def smooth(cube, window):
    """Centred moving average over years; shorter windows at the ends."""
    if window <= 1:
        return cube
    half = window // 2
    out = np.empty_like(cube)
    for t in range(cube.shape[0]):
        lo, hi = max(0, t - half), min(cube.shape[0], t + half + 1)
        out[t] = cube[lo:hi].mean(axis=0)
    return out


def run(cfg, spec=None, keep_products_for=None):
    """Run one specification. Returns dict of DataFrames.

    keep_products_for: ISO3 codes for which the full product-level results
    (RCA, M, density, COG) are kept. Default: focus country and peers.
    """
    spec = {**MAIN_SPEC, **(spec or {})}
    c = cfg["complexity"]
    if keep_products_for is None:
        keep_products_for = [c["focus"], *c["peers"]]

    ex = load_exports(cfg, spec["level"])
    pop = pd.read_parquet(cfg["output"] / "population.parquet")
    countries, products, years = select_panel(ex, pop, cfg, spec["level"], spec["exclude"])
    cube = smooth(to_cube(ex, countries, products, years), spec["window"])
    keep_idx = [countries.index(x) for x in keep_products_for if x in countries]

    country_rows, product_rows, cp_rows = [], [], []
    mcp_all = {}
    for t, year in enumerate(years):
        r = cx.compute_year(cube[t], spec["threshold"])
        mcp_all[year] = r["mcp"]
        country_rows.append(pd.DataFrame({
            "year": year, "iso3": countries, "exports": cube[t].sum(axis=1),
            "diversity": r["diversity"], "eci": r["eci"], "coi": r["coi"],
            "fitness": r["fitness"],
        }))
        product_rows.append(pd.DataFrame({
            "year": year, "prod": products, "world_exports": cube[t].sum(axis=0),
            "ubiquity": r["ubiquity"], "pci": r["pci"], "fc_complexity": r["fc_complexity"],
        }))
        for i in keep_idx:
            cp_rows.append(pd.DataFrame({
                "year": year, "iso3": countries[i], "prod": products,
                "exports": cube[t, i], "rca": r["rca"][i], "mcp": r["mcp"][i],
                "density": r["density"][i], "cog": r["cog"][i],
            }))
        if year == years[-1]:
            last_phi = pd.DataFrame(r["phi"], index=products, columns=products)

    countries_df = pd.concat(country_rows, ignore_index=True)
    products_df = pd.concat(product_rows, ignore_index=True)
    cp_df = pd.concat(cp_rows, ignore_index=True) if cp_rows else pd.DataFrame()

    # Fixed yardstick over time: pooled PCI (mean over all years), and each
    # country's mean pooled PCI over the products it exports with RCA >= threshold.
    pooled = products_df.groupby("prod")["pci"].mean().reindex(products).to_numpy()
    pooled_ok = ~np.isnan(pooled)
    fixed = []
    for year in years:
        m = mcp_all[year][:, pooled_ok]
        fixed.append((m @ pooled[pooled_ok]) / m.sum(axis=1))
    countries_df["eci_fixed_pci"] = np.concatenate(fixed)
    countries_df["eci_rank"] = countries_df.groupby("year")["eci"].rank(ascending=False).astype(int)

    return {
        "spec": spec, "countries": countries_df, "products": products_df,
        "country_products": cp_df, "proximity_last": last_phi,
        "n_countries": len(countries), "n_products": len(products),
    }
