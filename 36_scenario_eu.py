"""Scenario: EU single market, in the same multi-sector model as the US tariffs.

Model: Caliendo and Parro (2015) via gravity_ge.cp_solve, OECD ICIO 2025, base
year 2022, EU27. Elasticities: ProTEE sector medians capped at 15, services 5 (central);
uncapped ProTEE, uniform 4 and uniform 8 as sensitivity.

Shocks are set in terms of the gravity coefficient on intra-EU border flows
(beta), so that flows between EU members change by exp(dbeta) at given
multilateral resistance; in the model this is a change in iceberg costs of
kappa_hat = exp(-dbeta / theta_j) for every pair of distinct EU members.

Scenarios
  no_single_market   EU members treat each other like outsiders: goods
                     dbeta = -1.1, the standard EU effect for goods in 2018
                     (Head and Mayer 2021, JEP, beta_EUB - beta_CET); services
                     dbeta = -0.18 (Mayer, Vicard and Zignago 2019, as reported
                     in Head and Mayer 2021)
  trend_2030         intra-EU goods integration continues for ten years at the
                     2000-2019 pace estimated in 35_eu_border_effects.py
                     (change in beta_EUB per year, by broad sector)
  services_deeper    services integration catches up with goods on a
                     comparable sample: dbeta = 0.32 - 0.18 = +0.14 (Mayer,
                     Vicard and Zignago 2019 via Head and Mayer 2021)
Writes <output>/scenarios/eu_results.csv and eu_germany_sectors.csv.
Usage: python 36_scenario_eu.py
"""
import importlib

import numpy as np
import pandas as pd

import gravity_ge as gg
from config import load_config

us_mod = importlib.import_module("34_scenario_us_tariffs")
EU = us_mod.EU
GOODS_EU_EFFECT = 1.1      # Head and Mayer (2021), p. 31
SERVICES_EU_EFFECT = 0.18  # Mayer, Vicard and Zignago (2019), reported in Head and Mayer (2021), p. 32
SERVICES_GOODS_GAP = 0.32 - 0.18
TREND_YEARS = 10


def broad(sector):
    if sector.startswith("A"):
        return "Agriculture"
    if sector.startswith("B"):
        return "Mining and Energy"
    if sector.startswith("C"):
        return "Manufacturing"
    return "Services"


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    countries, sectors, X, Z, F = us_mod.load_icio(cfg["data"]["scenarios"] / "icio" / "2016-2022_SML.zip",
                                                   us_mod.YEAR)
    N, J = len(countries), len(sectors)
    el = pd.read_csv(out / "elasticities_icio.csv").set_index("sector")["theta"]
    theta_raw = np.array([el.get(s, us_mod.DEFAULT_THETA) for s in sectors])
    thetas = {"protee": np.minimum(theta_raw, us_mod.THETA_CAP), "protee_uncapped": theta_raw,
              "uniform4": np.full(J, 4.0), "uniform8": np.full(J, 8.0)}
    tau0 = us_mod.baseline_tariffs(out, pd.read_parquet(out / "us_tariffs_icio.parquet"), countries, sectors)
    base = gg.cp_baseline(X, Z, F, tau0)
    eu = np.array([c in EU for c in countries])
    pair = np.outer(eu, eu) & ~np.eye(N, dtype=bool)          # [n, i] distinct EU members
    kind = np.array([broad(s) for s in sectors])

    # trend per year in beta_EUB, 2000-2019, from 35_eu_border_effects.py
    be = pd.read_csv(out / "eu_border_effects.csv")
    be = be[be.type == "EUB"]
    slope = {s: np.polyfit(g.year, g.beta, 1)[0] for s, g in be.groupby("sector")}
    print("trend in beta_EUB per year:", {k: round(v, 4) for k, v in slope.items()})

    def dbeta_vec(scen):
        if scen == "no_single_market":
            return np.where(kind == "Services", -SERVICES_EU_EFFECT, -GOODS_EU_EFFECT)
        if scen == "trend_2030":
            return np.array([TREND_YEARS * slope.get(k, 0.0) if k in ("Agriculture", "Manufacturing") else 0.0
                             for k in kind])
        if scen == "services_deeper":
            return np.where(kind == "Services", SERVICES_GOODS_GAP, 0.0)
        raise ValueError(scen)

    deu, us = countries.index("DEU"), countries.index("USA")
    rows, sec_rows = [], []
    for scen, th in [(s, v) for s in ("no_single_market", "trend_2030", "services_deeper") for v in thetas]:
        theta = thetas[th]
        db = dbeta_vec(scen)
        kappa = np.ones((N, N, J))
        kappa[pair] = np.exp(-db / theta)[None, :]
        r = gg.cp_solve(base, tau0, theta, kappa_hat=kappa)
        intra_old = (r["X_old"][pair]).sum()
        intra_new = (r["X_new"][pair]).sum()
        for k, c in enumerate(countries):
            to_eu_old = r["X_old"][eu, k].sum() - (r["X_old"][k, k].sum() if eu[k] else 0)
            to_eu_new = r["X_new"][eu, k].sum() - (r["X_new"][k, k].sum() if eu[k] else 0)
            rows.append({"scenario": scen, "elasticity": th, "country": c, "welfare_pct": (r["W_hat"][k] - 1) * 100,
                         "exports_pct": (r["exports_hat"][k] - 1) * 100,
                         "exports_to_eu_pct": (to_eu_new / to_eu_old - 1) * 100,
                         "output_pct": (r["Y_new"][k].sum() / base["Y"][k].sum() - 1) * 100})
        w_eu = (r["W_hat"][eu] * base["I"][eu]).sum() / base["I"][eu].sum()
        rows.append({"scenario": scen, "elasticity": th, "country": "EU27", "welfare_pct": (w_eu - 1) * 100,
                     "exports_pct": np.nan, "exports_to_eu_pct": (intra_new / intra_old - 1) * 100, "output_pct": np.nan})
        for j, s in enumerate(sectors if th == "protee" else []):
            sec_rows.append({"scenario": scen, "sector": s, "output_pct": (r["Y_hat"][deu, j] - 1) * 100,
                             "exports_to_eu_pct": ((r["X_new"][eu, deu, j].sum() - r["X_new"][deu, deu, j])
                                                   / max(r["X_old"][eu, deu, j].sum() - r["X_old"][deu, deu, j], 1e-9) - 1) * 100,
                             "exports_to_eu_2022_bn": (r["X_old"][eu, deu, j].sum() - r["X_old"][deu, deu, j]) / 1e3,
                             "output_2022_bn": base["Y"][deu, j] / 1e3})
        print(f"{scen:17s} {th:15s} DEU {(r['W_hat'][deu] - 1) * 100:+.2f}%  EU27 {(w_eu - 1) * 100:+.2f}%  "
              f"USA {(r['W_hat'][us] - 1) * 100:+.3f}%  intra-EU trade {(intra_new / intra_old - 1) * 100:+.1f}%", flush=True)
    pd.DataFrame(rows).round(4).to_csv(out / "eu_results.csv", index=False)
    pd.DataFrame(sec_rows).round(4).to_csv(out / "eu_germany_sectors.csv", index=False)


if __name__ == "__main__":
    main()
