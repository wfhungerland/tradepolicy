"""Compare own import demand elasticities (48_import_elasticities.py) with the
ESCAP-World Bank estimates (Soderbery method, HS 2012, base year 2012, 185 reporters).

Input: <data>/escap/escap.zip (full_matrix7_2012.csv: reporter, HS12, elas), WITS
concordance HS 2012 -> HS 1988/92. Germany: ESCAP reporter DEU. EU27: median of the
ESCAP values of the 27 members per good (ESCAP has no EU aggregate).
Writes <output>/scenarios/escap_comparison.csv and prints rank correlations.
Usage: python 49_compare_escap.py
"""
import importlib
import zipfile

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from config import load_config

EU = importlib.import_module("44_dependencies").EU


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    with zipfile.ZipFile(cfg["data"]["scenarios"] / "escap" / "escap.zip") as z:
        e = pd.read_csv(z.open("full_matrix7_2012.csv"), dtype={"HS12": str})
    conc = pd.read_csv(next((cfg["data"]["scenarios"] / "conc").glob("*H4_to_H0*.CSV")), dtype=str,
                       encoding="latin1", usecols=[0, 2])
    conc.columns = ["HS12", "hs92"]
    # keep one-to-one links only, so goods are comparable
    conc = conc[~conc.HS12.duplicated(keep=False) & ~conc.hs92.duplicated(keep=False)]
    e = e.merge(conc, on="HS12")
    esc = pd.concat([e[e.reporter == "DEU"].assign(level="DEU")[["level", "hs92", "elas"]],
                     e[e.reporter.isin(EU)].groupby("hs92", as_index=False).elas.median().assign(level="EU27")])
    own = pd.read_csv(out / "import_elasticities_hs92.csv", dtype={"hs92": str})
    m = own.merge(esc, on=["level", "hs92"])
    m.round(4).to_csv(out / "escap_comparison.csv", index=False)
    for lv, g in m.groupby("level"):
        print(f"{lv}: {len(g)} goods matched one-to-one; median own {g.sigma.median():.2f}, ESCAP {g.elas.median():.2f}; "
              f"rank corr {spearmanr(g.sigma, g.elas).statistic:.2f} (all), "
              f"{spearmanr(g[g.feasible].sigma, g[g.feasible].elas).statistic:.2f} (LIML feasible only); "
              f"both < 2: {((g.sigma < 2) & (g.elas < 2)).mean():.0%}, own < 2 but ESCAP >= 3: {((g.sigma < 2) & (g.elas >= 3)).mean():.0%}")
        g2 = g.assign(hs2=g.hs92.str[:2]).groupby("hs2").agg(own=("sigma", "median"), escap=("elas", "median"))
        print(f"   rank corr of HS2 chapter medians: {spearmanr(g2.own, g2.escap).statistic:.2f} ({len(g2)} chapters)")


if __name__ == "__main__":
    main()
