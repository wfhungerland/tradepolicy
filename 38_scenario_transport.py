"""Scenario: transport cost shocks from closed sea passages (Red Sea, Panama).

Steps
1. Shortest sea routes between the main ports of the 80 ICIO economies, with and
   without the closed passages (sea_routes.py, marnet network). Rest of world:
   no change.
2. Calibration to the natural experiment of the 1967-75 Suez closure (Feyrer
   2021, Journal of Development Economics): goods trade falls with sea distance
   with an elasticity of about 0.5, half the typical cross-sectional estimate.
   With sector trade elasticity theta_j this is an iceberg cost change of
   kappa_hat = (d1 / d0) ** (delta / theta_j), delta = 0.5 (central) or 1.0
   (cross-sectional, upper bound). Applied to goods sectors on every pair whose
   route gets longer.
   Not used for the central case: time costs of 0.6 to 2.1 % per day
   (Hummels and Schaur 2013) imply a distance elasticity of about 2.5 in this
   model, five times Feyrer's, because they treat all goods as seaborne and as
   time-sensitive as the parts in their sample (see results_strand3.md).
3. Extra sailing days (reported only): extra km / (14 knots = 622 km per day).
4. Same Caliendo-Parro model as the tariff and EU scenarios (ICIO 2022,
   ProTEE elasticities capped at 15).

Scenarios
  red_sea_closed   Suez Canal and Bab el-Mandeb closed for all ships
  red_sea_2024     partial rerouting as observed: the shock is scaled by the
                   fall in Suez Canal transits from 2023 to 2024 (IMF PortWatch,
                   value set in RED_SEA_2024_SHARE)
  panama_closed    Panama Canal closed
Range: AVE per day 0.6 and 2.1 % (central elasticities) and the elasticity
variants (central AVE).
Writes <output>/scenarios/transport_results.csv, transport_germany_sectors.csv,
transport_routes.csv (extra days by pair).
Usage: python 38_scenario_transport.py
"""
import importlib

import numpy as np
import pandas as pd

import gravity_ge as gg
import sea_routes as sr
from config import load_config

us_mod = importlib.import_module("34_scenario_us_tariffs")
exp_mod = importlib.import_module("37_export_scenarios")

KM_PER_DAY = 14 * 1.852 * 24
DELTA = {"central": 0.5, "high": 1.0}    # elasticity of goods trade to sea distance
# Suez transits 2024 vs 2023: about 13,200 vs 26,000 ships (-49 %, AP data as reported
# by PortNews); Suez oil flows -51 % (S&P Global). Half of the shock as central value.
RED_SEA_2024_SHARE = 0.5
SCENARIOS = {"red_sea_closed": ("suez", "babalmandab"), "red_sea_2024": ("suez", "babalmandab"),
             "panama_closed": ("panama",)}


def route_change(cfg, countries, closed):
    """Extra days and distance ratio d1/d0 for every country pair (origin, destination)."""
    iso2 = exp_mod.iso2_map(cfg)
    folder = cfg["data"]["scenarios"] / "searoute"
    net = sr.SeaNetwork(folder / "marnet_searoute.geojson")
    codes = {c: iso2.get(c, "") for c in countries if iso2.get(c)}
    ports = sr.country_ports(folder / "ports.geojson", sorted(set(codes.values())))
    ports = {k: v for k, v in ports.items() if k in ports}
    base = sr.distance_matrix(net, ports)
    cut = sr.distance_matrix(net, ports, closed)
    N = len(countries)
    days = np.zeros((N, N))
    ratio = np.ones((N, N))
    for a, ca in enumerate(countries):
        for b, cb in enumerate(countries):
            pa, pb = codes.get(ca), codes.get(cb)
            if a == b or pa not in ports or pb not in ports or pa == pb:
                continue
            d0, d1 = base[(pa, pb)], cut[(pa, pb)]
            if np.isfinite(d0) and np.isfinite(d1):
                days[a, b] = max(0.0, d1 - d0) / KM_PER_DAY
                ratio[a, b] = max(1.0, d1 / d0) if d0 > 0 else 1.0
    return days, ratio


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
    goods = np.array([s[0] in "ABC" for s in sectors])
    base = gg.cp_baseline(X, Z, F, np.zeros((N, N, J)))
    deu = countries.index("DEU")
    eu = np.array([c in us_mod.EU for c in countries])

    rows, sec_rows, route_rows = [], [], []
    share_2024 = RED_SEA_2024_SHARE
    for scen, closed in SCENARIOS.items():
        days, ratio = route_change(cfg, countries, closed)
        scale = share_2024 if scen == "red_sea_2024" else 1.0
        for a in range(N):
            for b in range(a + 1, N):
                if days[a, b] > 0 and scen != "red_sea_2024":
                    route_rows.append({"scenario": scen, "a": countries[a], "b": countries[b],
                                       "extra_days": round(days[a, b], 2), "distance_ratio": round(ratio[a, b], 4)})
        affected = days > 0
        runs = [("central", "protee"), ("high", "protee"),
                ("central", "protee_uncapped"), ("central", "uniform4"), ("central", "uniform8")]
        for ave, th in runs:
            kappa = np.ones((N, N, J))
            lr = scale * np.log(ratio).T                                  # [destination, origin]
            kappa[:, :, goods] = np.exp(lr[:, :, None] * DELTA[ave] / thetas[th][goods][None, None, :])
            r = gg.cp_solve(base, np.zeros((N, N, J)), thetas[th], kappa_hat=kappa)
            variant = th if ave == "central" else f"delta_{ave}"
            for k, c in enumerate(countries):
                dest = affected[k]                                       # destinations on longer routes
                old = r["X_old"][dest, k].sum()
                new = r["X_new"][dest, k].sum()
                rows.append({"scenario": scen, "elasticity": variant, "country": c,
                             "welfare_pct": (r["W_hat"][k] - 1) * 100,
                             "exports_pct": (r["exports_hat"][k] - 1) * 100,
                             "exports_rerouted_pct": (new / old - 1) * 100 if old > 0 else np.nan,
                             "output_pct": (r["Y_new"][k].sum() / base["Y"][k].sum() - 1) * 100})
            w_eu = (r["W_hat"][eu] * base["I"][eu]).sum() / base["I"][eu].sum()
            rows.append({"scenario": scen, "elasticity": variant, "country": "EU27", "welfare_pct": (w_eu - 1) * 100,
                         "exports_pct": np.nan, "exports_rerouted_pct": np.nan, "output_pct": np.nan})
            if variant == "protee":
                dest = affected[deu]
                for j, s in enumerate(sectors):
                    old = r["X_old"][dest, deu, j].sum()
                    sec_rows.append({"scenario": scen, "sector": s, "output_pct": (r["Y_hat"][deu, j] - 1) * 100,
                                     "exports_rerouted_pct": (r["X_new"][dest, deu, j].sum() / old - 1) * 100 if old > 0 else np.nan,
                                     "exports_rerouted_2022_bn": old / 1e3, "output_2022_bn": base["Y"][deu, j] / 1e3})
                top = {c: (r["W_hat"][countries.index(c)] - 1) * 100 for c in ("DEU", "CHN", "IND", "USA", "JPN", "EGY")}
                print(f"{scen:15s} scale {scale:.2f}  " + "  ".join(f"{c} {v:+.3f}%" for c, v in top.items())
                      + f"  EU27 {(w_eu - 1) * 100:+.3f}%  DEU partners on longer routes: {int(affected[deu].sum())}", flush=True)
    pd.DataFrame(rows).round(4).to_csv(out / "transport_results.csv", index=False)
    pd.DataFrame(sec_rows).round(4).to_csv(out / "transport_germany_sectors.csv", index=False)
    pd.DataFrame(route_rows).to_csv(out / "transport_routes.csv", index=False)


if __name__ == "__main__":
    main()
