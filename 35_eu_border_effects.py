"""EU integration: time-varying border effects with flows to self.

Follows Head and Mayer (2021), "The United States of Europe: A Gravity Model
Evaluation of the Four Freedoms", Journal of Economic Perspectives 35(2), 23-48:
PPML on import shares (flow / importer's total expenditure incl. domestic),
exporter-year, importer-year and pair fixed effects, and three sets of
year-specific border dummies:
  EUB_t  border flow, origin and destination both EU members in year t
  CET_t  border flow from a non-member into an EU member
  ROW_t  border flow into a non-member (any origin)
ROW in the first year is the omitted reference. Trade cost changes relative to
that reference: exp(-beta / eps) - 1, eps = 5 (Head and Mayer 2014 median).

Data: ITPD-E R2025 broad sectors (31_itpd_panel.py). Domestic flows in ITPD-E
are sparse before 1995 (services before 2000) and break after 2015 for some
large economies (China, Japan, Taiwan; see results_strand3.md), so the default
window is 2000-2019 on a balanced set of countries with positive domestic flows
in every year, excluding countries with breaks.

Writes <output>/scenarios/eu_border_effects.csv (sector, year, type, beta, se,
tau_change_pct) and eu_border_effects.png.
Usage: python 35_eu_border_effects.py
"""
import numpy as np
import pandas as pd
import pyfixest as pf

from config import load_config

EPS = 5.0
YEARS = range(2000, 2020)
SECTORS = ["Manufacturing", "Agriculture", "Mining and Energy", "Services"]
BREAKS = {"CHN", "JPN", "TWN"}          # domestic flows with level breaks in ITPD-E
EU15 = ["AUT", "BEL", "DNK", "FIN", "FRA", "DEU", "GRC", "IRL", "ITA", "LUX", "NLD", "PRT", "ESP", "SWE", "GBR"]
ACCESSION = {**{c: 1958 for c in EU15}, "CZE": 2004, "EST": 2004, "CYP": 2004, "LVA": 2004, "LTU": 2004,
             "HUN": 2004, "MLT": 2004, "POL": 2004, "SVK": 2004, "SVN": 2004, "BGR": 2007, "ROU": 2007,
             "HRV": 2013}
EXIT = {"GBR": 2020}


def eu_member(iso, year):
    start = ACCESSION.get(iso)
    return start is not None and start <= year < EXIT.get(iso, 9999)


def panel(b, sector):
    d = b[(b.broad_sector == sector) & b.year.isin(YEARS)].copy()
    dom = d[(d.exporter == d.importer) & (d.trade > 0)]
    full = dom.groupby("exporter").year.nunique()
    keep = set(full[full == len(YEARS)].index) - BREAKS
    d = d[d.exporter.isin(keep) & d.importer.isin(keep)]
    # complete the grid of pairs with zeros so that shares and PPML use all pairs
    idx = pd.MultiIndex.from_product([sorted(keep), sorted(keep), list(YEARS)], names=["exporter", "importer", "year"])
    d = d.set_index(["exporter", "importer", "year"])["trade"].reindex(idx, fill_value=0.0).reset_index()
    d["share"] = d.trade / d.groupby(["importer", "year"]).trade.transform("sum")
    eu_i = np.array([eu_member(i, y) for i, y in zip(d.exporter, d.year)])
    eu_n = np.array([eu_member(n, y) for n, y in zip(d.importer, d.year)])
    border = (d.exporter != d.importer).to_numpy()
    d["typ"] = np.where(~border, "self", np.where(eu_n & eu_i, "EUB", np.where(eu_n, "CET", "ROW")))
    d["pair"] = d.exporter + "_" + d.importer
    d["exp_year"] = d.exporter + d.year.astype(str)
    d["imp_year"] = d.importer + d.year.astype(str)
    y0 = min(YEARS)
    names = []
    for typ in ("EUB", "CET", "ROW"):
        for y in YEARS:
            if typ == "ROW" and y == y0:
                continue
            col = f"{typ}_{y}"
            d[col] = ((d.typ == typ) & (d.year == y)).astype(float)
            names.append(col)
    return d, names, len(keep)


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    b = pd.read_parquet(out / "itpd_broad.parquet")
    rows = []
    for sector in SECTORS:
        d, names, n = panel(b, sector)
        m = pf.fepois(f"share ~ {' + '.join(names)} | pair + exp_year + imp_year", data=d, vcov={"CRV1": "pair"},
                      fixef_maxiter=200000, fixef_tol=1e-7, fixef_rm="singleton")
        co, se = m.coef(), m.se()
        print(f"{sector}: {n} countries, {len(d)} obs", flush=True)
        for y in YEARS:
            for typ in ("EUB", "CET", "ROW"):
                col = f"{typ}_{y}"
                beta = 0.0 if col not in co else float(co[col])
                s = np.nan if col not in se else float(se[col])
                rows.append({"sector": sector, "year": y, "type": typ, "beta": beta, "se": s,
                             "tau_change_pct": (np.exp(-beta / EPS) - 1) * 100, "n_countries": n})
    res = pd.DataFrame(rows)
    res.round(5).to_csv(out / "eu_border_effects.csv", index=False)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    label = {"EUB": "EU origin to EU destination", "CET": "Non-EU origin to EU destination",
             "ROW": "All origins to non-EU destination"}
    color = {"EUB": "#0070C0", "CET": "#C00000", "ROW": "#000000"}
    for ax, sector in zip(axes.ravel(), SECTORS):
        r = res[res.sector == sector]
        for typ in ("EUB", "CET", "ROW"):
            q = r[r.type == typ]
            ax.plot(q.year, q.tau_change_pct, marker="o", ms=3, color=color[typ], label=label[typ])
        ax.axhline(0, color="#8c8c8c", lw=0.8, ls="--")
        ax.set_title(f"{sector} ({int(r.n_countries.iloc[0])} countries)", fontsize=10)
        ax.set_ylabel(f"Change in trade costs, % (base: non-EU {min(YEARS)})", fontsize=8)
    axes[0, 0].legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(out / "eu_border_effects.png", dpi=150)
    last = res[res.year == max(YEARS)].pivot(index="sector", columns="type", values="tau_change_pct")
    print(last.round(1))


if __name__ == "__main__":
    main()
