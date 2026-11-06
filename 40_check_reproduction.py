"""Compare local strand 3 results with the reference values computed in the cloud
session of 2026-11-06 (reference_results.csv, committed with the code).

Reads the result files in <output>/scenarios and prints every key whose value
differs by more than the tolerance (absolute 0.005 for percentages, relative
0.1 % for elasticities). Exit code 1 if anything differs or is missing.
Usage: python 40_check_reproduction.py
"""
import sys

import pandas as pd

from config import load_config

TOL_ABS = 0.005


def local_value(out, file, key):
    d = pd.read_csv(out / file)
    parts = key.split("|")
    if file == "eu_border_effects.csv":
        sector, typ, year, col = parts
        q = d[(d.sector == sector) & (d.type == typ) & (d.year == int(year))]
    elif file == "elasticities_icio.csv":
        q, col = d[d.sector == parts[0]], parts[1]
    else:
        scen, country, col = parts
        q = d[(d.scenario == scen) & (d.country == country) & (d.elasticity == "protee")]
    return float(q[col].iloc[0]) if len(q) else None


def main():
    out = load_config()["output"] / "scenarios"
    ref = pd.read_csv("reference_results.csv")
    bad = 0
    for r in ref.itertuples():
        try:
            v = local_value(out, r.file, r.key)
        except FileNotFoundError:
            v = None
        tol = abs(r.value) * 1e-3 + 1e-9 if r.file == "elasticities_icio.csv" else TOL_ABS
        if v is None or abs(v - r.value) > tol:
            bad += 1
            print(f"DIFF {r.file:28s} {r.key:45s} reference {r.value:10.4f}  local {v}")
    print(f"{len(ref) - bad} of {len(ref)} values reproduced")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
