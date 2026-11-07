"""Export derived results as small JSON files for the public website.

Writes everything the static site (repo tradepolicy-site) needs into one
folder, by default <output>/site_data. Copy that folder to site/data in the
site repository and push. Only derived results leave this repo, never raw data.

Files
  meta.json       build date, specification, sources
  eci.json        per country and year: ECI, rank, fixed-PCI ECI, diversity,
                  COI, fitness rank, GENEPY rank
  products.json   HS4 products: code, name, sector, group, map position,
                  pooled PCI, world exports in the last year
  edges.json      product space links (maximum spanning tree and strong links)
  countries/XXX.json  per country: products with RCA >= 1 in snapshot years,
                  gained and lost products, opportunities (COG, density, PCI),
                  world market share by sector
  forecast.json   strand 1 summary tables (Germany and world)
Usage: python 20_export_site.py [target_folder]
"""
import importlib
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

import complexity as cx
import panel
from config import load_config

sectors = importlib.import_module("05_sectors")
pspace = importlib.import_module("06_product_space")

SNAPSHOTS = [1995, 2000, 2005, 2010, 2015, 2020, 2024]
ATLAS_PRODUCTS = "https://dataverse.harvard.edu/api/access/datafile/13438093"  # product_hs92.csv
N_OPPORTUNITIES = 60


def rnd(x, k=3):
    return None if x is None or not np.isfinite(x) else round(float(x), k)


def dump(obj, path):
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":"),
                               default=lambda o: o.item() if hasattr(o, "item") else str(o)),
                    encoding="utf-8")


def product_names(cfg):
    target = cfg["output"] / "atlas" / "product_hs92.csv"
    target.parent.mkdir(exist_ok=True)
    if not target.exists():
        urllib.request.urlretrieve(ATLAS_PRODUCTS, target)
    p = pd.read_csv(target, dtype=str)
    p = p[p.product_level == "4"]
    names = dict(zip(p.product_hs92_code, p.product_name))
    names_en = dict(names)
    de = Path(__file__).resolve().parent / "product_names_de.csv"
    if de.exists():   # German names for the site, see product_names_de.csv
        d = pd.read_csv(de, dtype=str)
        names.update(dict(zip(d.hs4, d.name_de)))
    ex = Path(__file__).resolve().parent / "product_examples_de.csv"
    examples = {}
    if ex.exists():   # one or two everyday examples per heading, see product_examples_de.csv
        e = pd.read_csv(ex, dtype=str, keep_default_na=False)
        examples = dict(zip(e.hs4, e.examples_de))
    return names, dict(zip(p.product_hs92_code, p.product_name_short)), examples, names_en


def country_codes(cfg):
    path = next(cfg["data"]["baci_raw"].glob("country_codes_V*.csv"))
    cc = pd.read_csv(path, dtype=str, keep_default_na=False)
    cc["country_iso3"] = cc.country_iso3.replace({"S19": "TWN"})
    cc.loc[cc.country_iso3 == "TWN", "country_iso2"] = "TW"
    return cc.drop_duplicates("country_iso3").set_index("country_iso3")


def main(target=None):
    cfg = load_config()
    out = cfg["output"] / "site_data" if target is None else Path(target)
    (out / "countries").mkdir(parents=True, exist_ok=True)

    print("running main specification for all countries")
    res = panel.run(cfg, panel.MAIN_SPEC, keep_products_for="all")
    countries, products, cp = res["countries"], res["products"], res["country_products"]
    countries_all = sorted(countries.iso3.unique())
    years = sorted(countries.year.unique())
    y0, y1 = years[0], years[-1]
    snaps = [y for y in SNAPSHOTS if y in years]
    if y1 not in snaps:
        snaps.append(y1)

    for col in ("fitness", "genepy"):
        countries[f"{col}_rank"] = countries.groupby("year")[col].rank(ascending=False).astype(int)

    # products
    names, short, examples, names_en = product_names(cfg)
    prods = sorted(products["prod"].unique())
    pidx = {p: i for i, p in enumerate(prods)}
    pooled = products.groupby("prod")["pci"].mean().reindex(prods)
    world_last = products[products.year == y1].set_index("prod")["world_exports"].reindex(prods)

    # product space layout (same construction as 06_product_space.py)
    phi = res["proximity_last"].fillna(0.0)
    phi.index = phi.index.astype(str)
    phi.columns = phi.columns.astype(str)
    tree, g = pspace.build_graph(phi)
    init = nx.kamada_kawai_layout(tree, weight=None)
    pos = nx.spring_layout(tree, pos=init, seed=pspace.SEED, iterations=20, k=1.0 / np.sqrt(len(tree)))
    xs = np.array([pos[p][0] for p in prods])
    ys = np.array([pos[p][1] for p in prods])
    xs = (xs - xs.min()) / (xs.max() - xs.min())
    ys = (ys - ys.min()) / (ys.max() - ys.min())
    sec_names = [s for _, s in sectors.SECTORS]
    sec_names = list(dict.fromkeys(sec_names))
    groups = list(pspace.GROUP_COLORS)
    prod_rows = []
    for i, p in enumerate(prods):
        sec = sectors.sector_of(p)
        prod_rows.append([p, names.get(p, p), short.get(p, ""), sec_names.index(sec),
                          groups.index(pspace.GROUPS[sec]), rnd(xs[i], 4), rnd(ys[i], 4),
                          rnd(pooled.iloc[i], 3), rnd(world_last.iloc[i] / 1e6, 3), examples.get(p, ""), names_en.get(p, p)])
    dump({"columns": ["code", "name", "short", "sector", "group", "x", "y", "pci", "world_bn_usd", "examples", "name_en"],
          "sectors": sec_names, "groups": groups, "group_colors": list(pspace.GROUP_COLORS.values()),
          "rows": prod_rows}, out / "products.json")
    tree_edges = [[pidx[u], pidx[v]] for u, v in tree.edges]
    extra = [[pidx[u], pidx[v]] for u, v in g.edges if not tree.has_edge(u, v)]
    dump({"tree": tree_edges, "extra": extra}, out / "edges.json")

    # countries: time series
    cc = country_codes(cfg)
    eci = {"years": years, "countries": {}}
    for iso, d in countries.groupby("iso3"):
        d = d.set_index("year").reindex(years)
        eci["countries"][iso] = {
            "name": cc.country_name.get(iso, iso), "iso2": cc.country_iso2.get(iso, ""),
            "eci": [rnd(v) for v in d.eci], "rank": [int(v) for v in d.eci_rank],
            "fixed": [rnd(v) for v in d.eci_fixed_pci], "diversity": [int(v) for v in d.diversity],
            "coi": [rnd(v) for v in d.coi], "fitness_rank": [int(v) for v in d.fitness_rank],
            "genepy_rank": [int(v) for v in d.genepy_rank],
            "exports_bn_usd": [rnd(v / 1e6, 2) for v in d.exports],
        }
    eci["n_countries"] = len(eci["countries"])
    dump(eci, out / "eci.json")

    # countries: product detail
    cp["sector"] = cp["prod"].map(sectors.sector_of)
    world = products.assign(sector=products["prod"].map(sectors.sector_of)).groupby(
        ["year", "sector"])["world_exports"].sum()
    for iso, d in cp.groupby("iso3"):
        rec = {"iso3": iso, "snapshots": snaps, "rca": {}}
        for y in snaps:
            rec["rca"][str(y)] = [pidx[p] for p in d[(d.year == y) & (d.mcp == 1)]["prod"]]
        a = d[d.year == y0].set_index("prod")
        b = d[d.year == y1].set_index("prod")
        rec["gained"] = [pidx[p] for p in b.index if b.mcp[p] == 1 and a.mcp.get(p, 0) == 0]
        rec["lost"] = [pidx[p] for p in b.index if b.mcp[p] == 0 and a.mcp.get(p, 0) == 1]
        opp = b[b.mcp == 0].assign(pci=lambda t: t.index.map(pooled)).dropna(subset=["cog"])
        opp = opp.sort_values("cog", ascending=False).head(N_OPPORTUNITIES)
        rec["opportunities"] = [[pidx[p], rnd(r.density), rnd(r.cog), rnd(r.pci)] for p, r in opp.iterrows()]
        sec = []
        for s in sec_names:
            v0 = d[(d.year == y0) & (d.sector == s)].exports.sum() / world.get((y0, s), np.nan)
            v1 = d[(d.year == y1) & (d.sector == s)].exports.sum() / world.get((y1, s), np.nan)
            sec.append([rnd(v0, 4), rnd(v1, 4)])
        rec["sector_share"] = sec
        dump(rec, out / "countries" / f"{iso}.json")

    # strand 1 summaries
    fc = {}
    for name in ("forecast_germany", "forecast_world"):
        folder = cfg["output"] / name
        fc[name] = {}
        for f in ("summary_monthly", "summary_monthly_excl_covid", "summary_quarterly"):
            path = folder / f"{f}.csv"
            if path.exists():
                fc[name][f] = pd.read_csv(path).round(3).replace({np.nan: None}).to_dict(orient="records")
    dump(fc, out / "forecast.json")

    dump({"built": date.today().isoformat(), "years": [y0, y1], "level": "HS4",
          "spec": {k: v for k, v in panel.MAIN_SPEC.items() if k != "exclude"},
          "n_countries": len(countries_all), "n_products": len(prods),
          "sources": [
              "BACI HS92 V202601 (CEPII), Etalab Open Licence 2.0",
              "Eurostat Comext, re-use with acknowledgement",
              "IMF International Trade in Goods (IMTS)",
              "Harvard Growth Lab, Atlas of Economic Complexity, product names (translated), CC BY 4.0",
              "OECD Inter-Country Input-Output Tables 2025 (Szenarien)",
              "USITC ITPD-E Release 2025, public domain (Szenarien)",
              "CEPII US import tariffs 2025-2026 (Guimbard 2026), CC BY-NC 4.0 (Szenarien)",
              "CEPII ProTEE 0.1, trade elasticities (Szenarien)",
          ]}, out / "meta.json")
    total = sum(f.stat().st_size for f in out.rglob("*.json"))
    print(f"{len(countries_all)} countries, {len(prods)} products, {total / 1e6:.1f} MB -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
