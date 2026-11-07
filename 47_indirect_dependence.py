"""Direct and indirect dependence of German industries on China (OECD ICIO 2022).

Total requirements from the global Leontief inverse L = (I - A)^-1, with A the
input coefficients of all 81 x 50 country-sectors (Z divided by gross output).
For German industry j:
  china_va_total   value added created in China per unit of output of j, over all
                   stages of the supply chain (v_CHN' L), the standard measure of
                   foreign value-added content (Johnson and Noguera 2012, JIE)
  dependent_total  estimate for dependent goods: the direct cost share of dependent inputs
                   from China (below) scaled by the industry's ratio of total to direct-route
                   Chinese value added (the same supply-chain multiplier)
  direct_dep       first-round share only: inputs bought directly from China, weighted
                   by f_k (as on the site so far), for comparison
All three as % of the industry's gross output.
Writes <output>/scenarios/china_dependence_germany_total.csv.
Usage: python 47_indirect_dependence.py
"""
import importlib

import numpy as np
import pandas as pd

from config import load_config

m34 = importlib.import_module("34_scenario_us_tariffs")
m44 = importlib.import_module("44_dependencies")


def dependent_share(cfg, out):
    dep = pd.read_csv(out / "dependencies_hs6.csv", dtype={"hs6": str})
    dep = set(dep[(dep.level == "EU27") & dep.dependent].hs6)
    b = m44.load_baci(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip", m44.YEAR)
    hs = pd.read_csv(out / "hs6_icio_map.csv", dtype=str).rename(columns={"hs22": "hs6"})
    fl = b[b.imp.isin(m44.EU) & (b.exp == "CHN")].merge(hs, on="hs6")
    fl["dep"] = fl.hs6.isin(dep)
    return fl.groupby("sector").apply(lambda g: g.loc[g.dep, "v"].sum() / g.v.sum(), include_groups=False)


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    countries, sectors, X, Z, F = m34.load_icio(cfg["data"]["scenarios"] / "icio" / "2016-2022_SML.zip", m34.YEAR)
    N, J = len(countries), len(sectors)
    NJ = N * J
    Zm = Z.reshape(NJ, NJ)                              # rows: supplying (i, k), columns: using (n, j)
    out_v = X.sum(axis=0).reshape(NJ)                    # gross output of (i, k): all sales
    out_v = np.maximum(out_v, 1e-6)
    A = Zm / out_v[None, :]
    v = 1 - A.sum(axis=0)                                # value-added share per country-sector
    v = np.clip(v, 0, 1)
    Lmat = np.linalg.inv(np.eye(NJ) - A)
    chn, deu = countries.index("CHN"), countries.index("DEU")
    rows_chn = np.arange(chn * J, (chn + 1) * J)
    cols_deu = np.arange(deu * J, (deu + 1) * J)
    f = dependent_share(cfg, out)
    fk = np.array([f.get(s, 0.0) if s[0] in "ABC" else 0.0 for s in sectors])
    vL = v[rows_chn, None] * Lmat[np.ix_(rows_chn, cols_deu)]            # [k, j]
    total = vL.sum(axis=0)
    direct = (A[np.ix_(rows_chn, cols_deu)] * fk[:, None]).sum(axis=0)
    # Chinese value added that reaches German industry j through its direct purchases from
    # China: each unit of Chinese output k carries c_k of Chinese value added (all Chinese
    # stages behind it). The rest of the total arrives via third countries and via other
    # German industries.
    c = (v[rows_chn, None] * Lmat[np.ix_(rows_chn, rows_chn)]).sum(axis=0)          # [k]
    direct_va = (A[np.ix_(rows_chn, cols_deu)] * c[:, None]).sum(axis=0)
    # check: total foreign value added content of German exports, Leontief identity
    all_va = (v[:, None] * Lmat[:, cols_deu]).sum(axis=0)
    assert np.allclose(all_va, 1, atol=1e-6), "value added does not add up to output"
    dep_total = direct * np.where(direct_va > 0, total / np.maximum(direct_va, 1e-12), 1.0)
    y = out_v[cols_deu]
    d = pd.DataFrame({"sector": sectors, "output_2022_bn": y / 1e3, "china_va_total_pct": total * 100,
                      "dependent_total_pct": dep_total * 100, "direct_dependent_pct": direct * 100,
                      "china_va_direct_pct": direct_va * 100,
                      "f_dependent_pct": fk * 100})
    d.round(4).to_csv(out / "china_dependence_germany_total.csv", index=False)
    big = d[d.output_2022_bn >= 5].sort_values("dependent_total_pct", ascending=False)
    print(big.head(12).round(2).to_string(index=False))
    w = d.output_2022_bn
    print(f"German economy, output-weighted: Chinese value added {np.average(d.china_va_total_pct, weights=w):.2f} %, "
          f"dependent inputs incl. indirect {np.average(d.dependent_total_pct, weights=w):.2f} %, direct dependent "
          f"{np.average(d.direct_dependent_pct, weights=w):.2f} %; Chinese value added via direct purchases "
          f"{np.average(d.china_va_direct_pct, weights=w):.2f} %, so {1 - np.average(d.china_va_direct_pct, weights=w) / np.average(d.china_va_total_pct, weights=w):.0%} of it comes via third countries or other German industries")


if __name__ == "__main__":
    main()
