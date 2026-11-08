"""Regional economic history and EU cohesion policy (NUTS 2 and 3).

A. History: GDP per head by NUTS 3 and NUTS 2 region, 1980-2024, from ARDECO (JRC/DG
   REGIO, variable SUVGDP, EUR at current prices, latest vintage), relative to the
   population-weighted mean of all regions in the data each year (index = 100). Figures
   before 1991 for East German regions are ARDECO back-estimates. Measures: maps for
   1980, 1990, 2000, 2010 and 2024; sigma convergence (dispersion of log index);
   East-West gap in Germany.
B. Cohesion policy: EU payments by NUTS 2 region and year (Commission cohesion open data,
   "Historic EU payments annual timeseries - regionalised and modelled", 1989-2023).
   Regression discontinuity at the 75 % threshold for "less developed" regions in the
   2014-2020 period (Becker, Egger and von Ehrlich 2010 for 1989-2006): running variable
   GDP per head in PPS relative to the EU average, mean 2007-2009 (Eurostat nama_10r_2gdp,
   current NUTS 2021 boundaries, which differ in places from those used for eligibility);
   outcomes: payments per head 2014-2023 (first stage) and growth of GDP per head relative
   to the EU average 2013-2022 (reduced form). Local linear regression with triangular
   kernel, bandwidth 15 points, robustness 10 and 20.
Writes <output>/regional/history_*.csv/png, cohesion_*.csv/png, site data.
Usage: python 65_regional_history_cohesion.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import regional as rg
from config import load_config

MAP_YEARS = [1980, 1990, 2000, 2010, 2024]
EAST = ("DE3", "DE4", "DE8", "DED", "DEE", "DEG")   # Berlin, Brandenburg, Mecklenburg-Vorpommern, Saxony, Saxony-Anhalt, Thuringia


def ardeco(raw, level):
    d = pd.read_csv(raw / "ardeco" / f"SUVGDP_{level}.csv")
    d = d[d.VERSIONS == d.VERSIONS.max()]
    d = d[d.YEAR <= 2024][["TERRITORY_ID", "YEAR", "VALUE"]].rename(columns={"TERRITORY_ID": "geo", "YEAR": "year", "VALUE": "gdp_pc"})
    return d.drop_duplicates(["geo", "year"])


def rdd(x, y, c=75, h=15):
    """Local linear RD estimate of the jump at c (below minus above), triangular kernel."""
    m = (np.abs(x - c) <= h) & np.isfinite(y)
    x, y = x[m], y[m]
    w = 1 - np.abs(x - c) / h
    d = (x < c).astype(float)
    X = np.column_stack([np.ones_like(x), d, x - c, d * (x - c)])
    W = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * W[:, None], y * W, rcond=None)
    res = y - X @ beta
    bread = np.linalg.inv((X * w[:, None]).T @ X)
    meat = (X * (w * res)[:, None]).T @ (X * (w * res)[:, None])
    se = np.sqrt(np.diag(bread @ meat @ bread))
    return beta[1], se[1], int(m.sum())


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "regional"
    out = cfg["output"] / "regional"
    out.mkdir(parents=True, exist_ok=True)
    pop = rg.read_eurostat(raw / "demo_r_d2jan.tsv.gz")
    pop = pop[(pop.sex == "T") & (pop.age == "TOTAL") & (pop.geo.str.len() == 4)][["geo", "year", "value"]].rename(columns={"value": "pop"})

    # A: history
    hist = {}
    for level in (2, 3):
        d = ardeco(raw, level)
        d = d[~d.geo.str.endswith("Z") & ~d.geo.str[:2].isin(["UK", "TR", "AL", "ME", "MK", "RS", "LI", "IS"])]
        d["idx"] = d.gdp_pc / d.groupby("year").gdp_pc.transform("mean") * 100
        hist[level] = d
    d2 = hist[2].merge(pop, on=["geo", "year"], how="left")
    sig = hist[3].groupby("year").idx.apply(lambda s: np.log(s[s > 0]).std()).rename("sigma_nuts3")
    sig2 = hist[2].groupby("year").idx.apply(lambda s: np.log(s[s > 0]).std()).rename("sigma_nuts2")
    de = hist[3][hist[3].geo.str.startswith("DE")].copy()
    de["east"] = de.geo.str[:3].isin(EAST) & ~de.geo.str.startswith("DE30")
    de = de[de.year >= 1991]                     # ARDECO has no East German regions before 1991
    ew = de.groupby(["year", "east"]).idx.mean().unstack()
    ew.columns = ["west", "east"]
    ew["east_in_pct_of_west"] = ew.east / ew.west * 100
    hs = pd.concat([sig, sig2, ew], axis=1)
    hs.round(4).to_csv(out / "history_summary.csv")
    print("dispersion of log GDP per head (NUTS 3):", {y: round(hs.sigma_nuts3[y], 3) for y in MAP_YEARS})
    print("East German NUTS 3 regions in % of West (without Berlin):", {y: round(hs.east_in_pct_of_west[y], 1) for y in (1991, 2000, 2010, 2024)})
    shapes3, names3 = rg.load_nuts(raw / "nuts3_2021_10m.geojson")
    bins = [0, 50, 75, 90, 110, 125, 150, 1e9]
    cols = ["#7f0000", "#e06666", "#fce4d6", "#f2f2f2", "#deebf7", "#5b9bd5", "#002060"]
    fig, axes = plt.subplots(2, len(MAP_YEARS), figsize=(18, 8.5), gridspec_kw={"height_ratios": [1, 1]})
    for k, y in enumerate(MAP_YEARS):
        v = hist[3][hist[3].year == y].set_index("geo").idx.to_dict()
        rg.choropleth(axes[0, k], shapes3, v, bins, cols, extent=rg.EXTENT_EU, lw=0.05)
        rg.choropleth(axes[1, k], shapes3, v, bins, cols, extent=rg.EXTENT_DE, lw=0.1)
        axes[0, k].set_title(str(y), fontsize=11)
    rg.legend_bins(axes[0, 0], bins, cols, fmt="{:.0f}", title="Index, Mittel = 100")
    fig.suptitle("BIP je Einwohner nach Kreisen und Regionen (NUTS 3), relativ zum Mittel aller Regionen", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis von ARDECO (JRC, Variable SUVGDP, laufende Preise in Euro); Werte vor 1991 für "
             "Ostdeutschland sind Rückrechnungen. Kartengrundlage: © EuroGeographics (GISCO).", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "history_maps.png", dpi=150); plt.close(fig)

    # B: cohesion
    pay = pd.read_csv(raw / "cohesion" / "payments.csv")
    pay = pay.groupby(["NUTS2_ID", "Year"]).EU_Payment_annual.sum().rename("pay").reset_index().rename(columns={"NUTS2_ID": "geo", "Year": "year"})
    pp = pay.merge(pop, on=["geo", "year"], how="left")
    gdp = rg.read_eurostat(raw / "nama_10r_2gdp.tsv.gz")
    pps = gdp[(gdp.unit == "PPS_EU27_2020_HAB") & (gdp.geo.str.len() == 4)]
    eu = gdp[(gdp.unit == "PPS_EU27_2020_HAB") & (gdp.geo == "EU27_2020")].set_index("year").value
    pps = pps.assign(rel=lambda x: x.value / x.year.map(eu) * 100)
    def period(run_years, g0, g1, p0, p1, label):
        run = pps[pps.year.between(*run_years)].groupby("geo").rel.mean().rename("x")
        a, b = pps[pps.year == g0].set_index("geo").rel, pps[pps.year == g1].set_index("geo").rel
        growth = ((np.log(b) - np.log(a)) * 100).rename("y_growth")
        p_ = pp[pp.year.between(p0, p1)].groupby("geo").agg(pay=("pay", "sum"), pop=("pop", "mean"))
        p_["pay_pc"] = p_.pay / p_["pop"]
        return pd.concat([run, growth, p_.pay_pc], axis=1).dropna().assign(period=label)
    # 2007-2013: eligibility on 2000-2002 data; 2014-2020: on 2007-2009 data
    rd = pd.concat([period((2000, 2002), 2006, 2015, 2007, 2016, "2007-2013"), period((2007, 2009), 2013, 2022, 2014, 2023, "2014-2020")])
    rd = rd[~rd.index.str[:2].isin(["UK"])]
    res = []
    for h in (10, 15, 20):
        for var, lab in (("pay_pc", "Zahlungen je Einwohner in der Periode (+3 Jahre), EUR"), ("y_growth", "Wachstum BIP je Einw. rel. zur EU über 9 Jahre, %")):
            b, se, n = rdd(rd.x.to_numpy(), rd[var].to_numpy(), h=h)
            res.append({"bandwidth": h, "outcome": lab, "jump_below_75": b, "se": se, "n": n})
    res = pd.DataFrame(res)
    res.round(3).to_csv(out / "cohesion_rdd.csv", index=False)
    print(res.round(2).to_string(index=False))
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for a, var, lab in ((axes[0], "pay_pc", "EU-Zahlungen je Einwohner 2014-2023, EUR"), (axes[1], "y_growth", "Wachstum des BIP je Einwohner relativ zur EU, 2013-2022, %")):
        s = rd[(rd.x > 40) & (rd.x < 125)]
        a.scatter(s.x, s[var], s=12, color=np.where(s.x < 75, "#c00000", "#002060"), alpha=0.6)
        bins_ = np.arange(40, 126, 5)
        mb = s.groupby(pd.cut(s.x, bins_))[var].mean()
        a.plot([iv.mid for iv in mb.index], mb.values, color="#000", lw=1.5)
        a.axvline(75, color="#000", ls="--", lw=0.8)
        a.set_xlabel("BIP je Einwohner in KKS, % des EU-Durchschnitts, drei Jahre vor der Periode"); a.set_title(lab, loc="left", fontsize=10)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.suptitle("Kohäsionspolitik 2007-2013 und 2014-2020 (gepoolt): Sprung an der 75-%-Schwelle", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis der Kohäsionsdaten der EU-Kommission (historische Zahlungen, regionalisiert) und Eurostat "
             "(nama_10r_2gdp, demo_r_d2jan); Linie: Mittelwerte in 5-Punkte-Klassen.", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(out / "cohesion_rdd.png", dpi=170); plt.close(fig)
    shapes2, names2 = rg.load_nuts(raw / "nuts2_2021.geojson")
    lastpop = pop.dropna().sort_values("year").groupby("geo")["pop"].last()
    cum = pp[pp.year.between(1989, 2023)].groupby("geo").pay.sum() / lastpop
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw={"width_ratios": [1.45, 1]})
    b2 = [0, 1000, 2500, 5000, 10000, 15000, 1e9]
    c2 = ["#deebf7", "#9dc3e6", "#5b9bd5", "#2e75b6", "#1f4e79", "#002060"]
    for a, ext in zip(axes, (rg.EXTENT_EU, rg.EXTENT_DE)):
        rg.choropleth(a, shapes2, cum.to_dict(), b2, c2, extent=ext)
    rg.legend_bins(axes[0], b2, c2, fmt="{:,.0f}", title="EUR je Einwohner")
    fig.suptitle("EU-Kohäsionszahlungen 1989-2023 je Einwohner (Bevölkerung 2023)", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: Kohäsionsdaten der EU-Kommission (historische Zahlungen, regional zugeordnet, nominal); Eurostat; Kartengrundlage: © EuroGeographics.", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "cohesion_map.png", dpi=170); plt.close(fig)
    de_top = cum[cum.index.str.startswith("DE")].sort_values(ascending=False)
    print("cohesion payments per head 1989-2023, Germany top:", de_top.head(5).round(0).to_dict())

    # ports
    port = rg.read_eurostat(raw / "tran_r_mago_nm.tsv.gz")
    port = port[(port.geo.str.len() == 4) & (port.tra_meas == "FR_LD_NLD")]
    pl = port[port.year == port.year.max()].groupby("geo").value.sum()
    print("ports (NUTS 2, latest year, 1000 t):", pl.sort_values(ascending=False).head(8).round(0).to_dict())
    if site:
        paths, h = rg.svg_paths(shapes2)
        idx2 = hist[2].pivot(index="geo", columns="year", values="idx")
        data = {"height": h, "paths": paths, "years": [int(y) for y in idx2.columns],
                "gdp_index": {g: [None if pd.isna(v) else round(float(v), 1) for v in r] for g, r in idx2.iterrows()},
                "names": {g: names2.get(g, g) for g in idx2.index},
                "cohesion_pc": {g: round(float(v)) for g, v in cum.dropna().items()},
                "ports_kt": {g: round(float(v)) for g, v in pl.items()},
                "summary": {c: [None if pd.isna(v) else round(float(v), 4) for v in col] for c, col in hs.reset_index().rename(columns={"index": "year"}).items()},
                "rdd": res.round(3).to_dict(orient="records")}
        p = Path(site) / "regional_history.json"
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
