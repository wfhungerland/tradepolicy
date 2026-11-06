"""Scenario: US tariffs 2025-26 in a multi-sector model with input-output links.

Model: Caliendo and Parro (2015), static, solved in changes (gravity_ge.cp_solve),
81 economies (80 + rest of world) and 50 sectors of OECD ICIO 2025, base year
2022. Tariff revenue is rebated to consumers, trade deficits are held fixed.
No retaliation unless stated.

Inputs
  ICIO 2025 small version, 2022 table (cfg["data"]["scenarios"]/icio/2016-2022_SML.zip)
  <output>/scenarios/us_tariffs_icio.parquet and elasticities_icio.csv (33_tariff_inputs.py)

Scenarios (US applied tariffs at the date shown, against 1 January 2025):
  peak_2025_04   10 April 2025, US-China escalation, 90-day pause for others
  deal_2025_09   5 September 2025, framework deals with EU, Japan, Korea
  current_2026_08  22 August 2026, latest date in the CEPII file
Elasticities: ProTEE sector medians capped at 15 (central); uncapped ProTEE, uniform 4 and 8 (sensitivity).

Writes <output>/scenarios/us_tariffs_results.csv (country results),
us_tariffs_germany_sectors.csv (German output and exports to the US by sector).
Usage: python 34_scenario_us_tariffs.py
"""
import zipfile

import numpy as np
import pandas as pd

import gravity_ge as gg
from config import load_config

YEAR = 2022
BASE_DATE = "20250101"
SCENARIOS = {"peak_2025_04": "20250410", "deal_2025_09": "20250905", "current_2026_08": "20260822"}
GOODS = ("A", "B", "C")          # tariffs apply only to goods sectors
DEFAULT_THETA = 5.0
THETA_CAP = 15.0     # ProTEE HS6 medians above this are product-level, not sector-level elasticities
EU = ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN",
      "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"]


def load_icio(path, year):
    with zipfile.ZipFile(path) as z:
        d = pd.read_csv(z.open(f"{year}_SML.csv"), index_col=0)
    rows = [r for r in d.index if r not in ("TLS", "VA", "OUT")]
    countries = list(dict.fromkeys(r.split("_", 1)[0] for r in rows))
    sectors = list(dict.fromkeys(r.split("_", 1)[1] for r in rows))
    N, J = len(countries), len(sectors)
    Z = d.loc[rows, rows].to_numpy().reshape(N, J, N, J)
    fd = ["HFCE", "NPISH", "GGFC", "GFCF", "INVNT", "DPABR"]
    F = np.stack([d.loc[rows, [f"{c}_{f}" for f in fd]].sum(axis=1).to_numpy() for c in countries], axis=1)
    F = np.maximum(F, 0.0).reshape(N, J, N)          # inventories and purchases abroad can be negative
    X = Z.sum(axis=3).transpose(2, 0, 1) + F.transpose(2, 0, 1)
    return countries, sectors, X, Z, F


def tariff_matrix(t, date, countries, sectors):
    """N x N x J tariffs of the US (importer) on each origin, other pairs zero.
    Origins outside ICIO are folded into ROW with US import weights."""
    N, J = len(countries), len(sectors)
    pos = {c: k for k, c in enumerate(countries)}
    spos = {s: k for k, s in enumerate(sectors)}
    d = t[t.date == date].copy()
    d["origin"] = d.exporter.where(d.exporter.isin(pos), "ROW")
    d = d[d.sector.isin(spos) & d.sector.str.startswith(GOODS) & (d.origin != "USA")]
    d["tv"] = d.tariff * d.us_imports_2024
    g = d.groupby(["origin", "sector"])[["tv", "us_imports_2024"]].sum()
    tau = np.zeros((N, N, J))
    us = pos["USA"]
    for (o, s), r in g.iterrows():
        tau[us, pos[o], spos[s]] = r.tv / r.us_imports_2024
    return tau


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    countries, sectors, X, Z, F = load_icio(cfg["data"]["scenarios"] / "icio" / "2016-2022_SML.zip", YEAR)
    N, J = len(countries), len(sectors)
    print(f"ICIO {YEAR}: {N} economies, {J} sectors, world output {X.sum() / 1e6:.1f} trillion USD")

    t = pd.read_parquet(out / "us_tariffs_icio.parquet")
    el = pd.read_csv(out / "elasticities_icio.csv").set_index("sector")["theta"]
    theta_raw = np.array([el.get(s, DEFAULT_THETA) for s in sectors])
    thetas = {"protee": np.minimum(theta_raw, THETA_CAP), "protee_uncapped": theta_raw,
              "uniform4": np.full(J, 4.0), "uniform8": np.full(J, 8.0)}

    tau0 = tariff_matrix(t, BASE_DATE, countries, sectors)
    base = gg.cp_baseline(X, Z, F, tau0)
    us, deu = countries.index("USA"), countries.index("DEU")
    eu = [countries.index(c) for c in EU if c in countries]

    rows, sector_rows = [], []
    runs = [(s, "protee") for s in SCENARIOS] + [(s, v) for s in SCENARIOS for v in ("protee_uncapped", "uniform4", "uniform8")]
    for scen, th in runs:
        tau1 = tariff_matrix(t, SCENARIOS[scen], countries, sectors)
        r = gg.cp_solve(base, tau1, thetas[th])
        to_us_old = r["X_old"][us].sum(axis=1)      # exports of each origin to the US
        to_us_new = r["X_new"][us].sum(axis=1)
        for k, c in enumerate(countries):
            rows.append({"scenario": scen, "elasticity": th, "country": c,
                         "welfare_pct": (r["W_hat"][k] - 1) * 100,
                         "exports_pct": (r["exports_hat"][k] - 1) * 100,
                         "exports_to_us_pct": (to_us_new[k] / to_us_old[k] - 1) * 100 if k != us else np.nan,
                         "output_pct": (r["Y_new"][k].sum() / base["Y"][k].sum() - 1) * 100,
                         "us_tariff_avg_pct": (tau1[us, k] * r["X_old"][us, k]).sum() / max(r["X_old"][us, k].sum(), 1e-9) * 100})
        eu_w = (r["W_hat"][eu] * base["I"][eu]).sum() / base["I"][eu].sum()
        rows.append({"scenario": scen, "elasticity": th, "country": "EU27", "welfare_pct": (eu_w - 1) * 100,
                     "exports_pct": np.nan, "exports_to_us_pct": (to_us_new[eu].sum() / to_us_old[eu].sum() - 1) * 100,
                     "output_pct": np.nan, "us_tariff_avg_pct": np.nan})
        if th == "protee":
            for j, s in enumerate(sectors):
                sector_rows.append({"scenario": scen, "sector": s,
                                    "output_pct": (r["Y_hat"][deu, j] - 1) * 100,
                                    "exports_to_us_pct": (r["X_new"][us, deu, j] / max(r["X_old"][us, deu, j], 1e-9) - 1) * 100,
                                    "us_tariff_pct": tau1[us, deu, j] * 100,
                                    "exports_to_us_2022_bn": r["X_old"][us, deu, j] / 1e3,
                                    "output_2022_bn": base["Y"][deu, j] / 1e3})
        k = {c: countries.index(c) for c in ("USA", "DEU", "CHN", "CAN", "MEX")}
        print(f"{scen:16s} {th:9s} " + " ".join(f"{c} {(r['W_hat'][i] - 1) * 100:+.2f}%" for c, i in k.items())
              + f" EU27 {(eu_w - 1) * 100:+.2f}%  ({r['iterations']} it.)", flush=True)

    pd.DataFrame(rows).round(4).to_csv(out / "us_tariffs_results.csv", index=False)
    pd.DataFrame(sector_rows).round(4).to_csv(out / "us_tariffs_germany_sectors.csv", index=False)


if __name__ == "__main__":
    main()
