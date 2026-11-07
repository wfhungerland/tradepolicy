"""Build the small, fixed inputs for the monthly US tariff update (42_update_us_scenarios.py).

The monthly job cannot rebuild the baseline itself: the OECD ICIO tables cannot be
downloaded by script and MAcMap is 2.7 GB. This script stores what the job needs
in one folder (default <output>/update_assets, about 10 MB):

  baseline.npz       Caliendo-Parro baseline (gravity_ge.cp_baseline) on ICIO 2022 with
                     MAcMap 2019 tariffs and the US schedule of 1 Jan 2025, plus
                     countries, sectors, elasticity variants and EU membership
  us_weights.parquet US imports 2024 by exporter and HS6 (BACI HS22), the weights for
                     aggregating the CEPII tariffs to ICIO sectors
  hs6_icio_map.csv   HS 2022 six-digit code -> ICIO sector
Run after any change to the baseline (scripts 33, 34, 39).
Usage: python 41_update_assets.py [target_folder]
"""
import importlib
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import gravity_ge as gg
from config import load_config

m34 = importlib.import_module("34_scenario_us_tariffs")
m33 = importlib.import_module("33_tariff_inputs")


def main(target=None):
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    dst = Path(target) if target else cfg["output"] / "update_assets"
    dst.mkdir(parents=True, exist_ok=True)
    countries, sectors, X, Z, F = m34.load_icio(cfg["data"]["scenarios"] / "icio" / "2016-2022_SML.zip", m34.YEAR)
    t = pd.read_parquet(out / "us_tariffs_icio.parquet")
    tau0 = m34.baseline_tariffs(out, t, countries, sectors)
    base = gg.cp_baseline(X, Z, F, tau0)
    el = pd.read_csv(out / "elasticities_icio.csv").set_index("sector")["theta"]
    raw = np.array([el.get(s, m34.DEFAULT_THETA) for s in sectors])
    np.savez_compressed(
        dst / "baseline.npz", countries=np.array(countries), sectors=np.array(sectors),
        eu=np.array([c in m34.EU for c in countries]),
        theta_protee=np.minimum(raw, m34.THETA_CAP), theta_protee_uncapped=raw,
        theta_uniform4=np.full(len(sectors), 4.0), theta_uniform8=np.full(len(sectors), 8.0),
        **{k: np.asarray(v, dtype=np.float64) for k, v in base.items()})
    us, _ = m33.baci_weights(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip", m33.WEIGHT_YEAR)
    us.to_parquet(dst / "us_weights.parquet", index=False)
    shutil.copy(out / "hs6_icio_map.csv", dst / "hs6_icio_map.csv")
    for f in sorted(dst.iterdir()):
        print(f"{f.name:22s} {f.stat().st_size / 1e6:6.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
