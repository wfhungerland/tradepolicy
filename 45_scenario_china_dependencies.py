"""Scenario: China stops supplying the EU with the products the EU depends on.

Dependent products from 44_dependencies.py (EU27 level, Commission criteria). For each
ICIO sector j, f_j = share of EU imports from China in that sector that fall on
dependent products (value, BACI HS22 2024, mapped HS6 -> ICIO). The supply stop is an
iceberg cost on flows from China to every EU member chosen so that these flows fall by
f_j at given prices: kappa_hat = (1 - f_j) ** (-1 / theta_j). Same Caliendo-Parro model
and baseline as the other scenarios; range over the elasticity variants.

Criticality for German industries: share of each industry's costs spent on inputs
from China in dependent products, sum over input sectors k of
G_DEU[k, j] * pi[DEU, CHN, k] * f_k (direct use only, ICIO 2022).
Caveat: the model lets buyers switch to other suppliers along a CES demand curve.
Hard bottlenecks (inputs without short-run substitutes) cost much more; the result is
a long-run lower bound, not an estimate of a sudden cut-off.
Writes <output>/scenarios/china_dependency_results.csv, china_dependency_germany.csv.
Usage: python 45_scenario_china_dependencies.py
"""
import importlib
import zipfile

import numpy as np
import pandas as pd

import gravity_ge as gg
from config import load_config

m34 = importlib.import_module("34_scenario_us_tariffs")
m44 = importlib.import_module("44_dependencies")
F_CAP = 0.95


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    dep = pd.read_csv(out / "dependencies_hs6.csv", dtype={"hs6": str})
    dep = set(dep[(dep.level == "EU27") & dep.dependent].hs6)
    b = m44.load_baci(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip", m44.YEAR)
    hs = pd.read_csv(out / "hs6_icio_map.csv", dtype=str).rename(columns={"hs22": "hs6"})
    flows = b[b.imp.isin(m44.EU) & (b.exp == "CHN")].merge(hs, on="hs6")
    flows["dep"] = flows.hs6.isin(dep)
    f = flows.groupby("sector").apply(lambda g: g.loc[g.dep, "v"].sum() / g.v.sum(), include_groups=False)
    print("share of EU imports from China that are dependent products, by ICIO sector (top 8):")
    print((f.sort_values(ascending=False).head(8) * 100).round(1).to_string())

    countries, sectors, X, Z, F = m34.load_icio(cfg["data"]["scenarios"] / "icio" / "2016-2022_SML.zip", m34.YEAR)
    N, J = len(countries), len(sectors)
    t = pd.read_parquet(out / "us_tariffs_icio.parquet")
    tau0 = m34.baseline_tariffs(out, t, countries, sectors)
    base = gg.cp_baseline(X, Z, F, tau0)
    el = pd.read_csv(out / "elasticities_icio.csv").set_index("sector")["theta"]
    raw = np.array([el.get(s, m34.DEFAULT_THETA) for s in sectors])
    thetas = {"protee": np.minimum(raw, m34.THETA_CAP), "protee_uncapped": raw,
              "uniform4": np.full(J, 4.0), "uniform8": np.full(J, 8.0)}
    # goods sectors only: a few HS codes map to ISIC service codes (films, art), whose
    # ICIO flows are services
    fj = np.array([min(f.get(s, 0.0), F_CAP) if s[0] in "ABC" else 0.0 for s in sectors])
    chn, deu = countries.index("CHN"), countries.index("DEU")
    eu = np.array([c in m34.EU for c in countries])

    rows, sec = [], []
    for v, th in thetas.items():
        kappa = np.ones((N, N, J))
        kappa[np.ix_(eu, [chn], np.arange(J))] = ((1 - fj) ** (-1 / th))[None, None, :]
        r = gg.cp_solve(base, tau0, th, kappa_hat=kappa)
        for k, c in enumerate(countries):
            rows.append({"scenario": "china_dependencies", "elasticity": v, "country": c,
                         "welfare_pct": (r["W_hat"][k] - 1) * 100, "exports_pct": (r["exports_hat"][k] - 1) * 100,
                         "output_pct": (r["Y_new"][k].sum() / base["Y"][k].sum() - 1) * 100,
                         "imports_from_china_pct": (r["X_new"][k, chn].sum() / max(r["X_old"][k, chn].sum(), 1e-9) - 1) * 100})
        w = (r["W_hat"][eu] * base["I"][eu]).sum() / base["I"][eu].sum()
        rows.append({"scenario": "china_dependencies", "elasticity": v, "country": "EU27", "welfare_pct": (w - 1) * 100,
                     "exports_pct": np.nan, "output_pct": np.nan,
                     "imports_from_china_pct": (r["X_new"][eu, chn].sum() / r["X_old"][eu, chn].sum() - 1) * 100})
        if v == "protee":
            crit = np.einsum("kj,k,k->j", base["G"][deu], base["pi"][deu, chn, :], fj)
            for j, s in enumerate(sectors):
                sec.append({"sector": s, "output_pct": (r["Y_hat"][deu, j] - 1) * 100, "output_2022_bn": base["Y"][deu, j] / 1e3,
                            "dependent_china_input_share_pct": crit[j] * 100, "dependent_share_of_china_imports_pct": fj[j] * 100})
        print(f"{v:16s} DEU {(r['W_hat'][deu] - 1) * 100:+.3f}%  EU27 {(w - 1) * 100:+.3f}%  CHN {(r['W_hat'][chn] - 1) * 100:+.3f}%  "
              f"USA {(r['W_hat'][countries.index('USA')] - 1) * 100:+.3f}%")
    pd.DataFrame(rows).round(4).to_csv(out / "china_dependency_results.csv", index=False)
    s = pd.DataFrame(sec).round(4)
    s.to_csv(out / "china_dependency_germany.csv", index=False)
    print(s.sort_values("dependent_china_input_share_pct", ascending=False).head(8).to_string(index=False))


if __name__ == "__main__":
    main()
