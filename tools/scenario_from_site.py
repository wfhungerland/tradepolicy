"""Rebuild German scenario output files from the published site data (no model run).

The district scripts (64, 73-81) only need the Caliendo-Parro output change of each German
sector. When a session lacks the full strand 3 inputs (for example because the WITS
concordances cannot be downloaded), this script writes the German rows of
us_tariffs_output_all.csv, china_dependency_output_all.csv and transport_output_all.csv from
site/data/scenarios.json (sectors_deu: sector, output_pct, partner_pct, us_tariff_pct,
partner exports 2022, output 2022). Other countries are not in the site file, so NUTS 2
results for non-German regions stay missing.
Usage: python tools/scenario_from_site.py <path to tradepolicy-site/site/data/scenarios.json>
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import load_config

FILES = {"us_tariffs_output_all.csv": ["peak_2025_04", "deal_2025_09", "current_2026_08", "retaliation_eu", "retaliation_all"],
         "china_dependency_output_all.csv": ["china_dependencies"],
         "transport_output_all.csv": ["red_sea_2024", "red_sea_closed", "panama_closed"]}


def main(path):
    d = json.load(open(path, encoding="utf-8"))
    cols = d["sector_columns"]
    sc = {s["id"]: s for s in d["scenarios"]}
    out = load_config()["output"] / "scenarios"
    out.mkdir(parents=True, exist_ok=True)
    for fn, ids in FILES.items():
        rows = [dict(zip(cols, r), scenario=i, country="DEU") for i in ids if i in sc for r in sc[i]["sectors_deu"]]
        pd.DataFrame(rows).to_csv(out / fn, index=False)
        print(fn, len(rows), "rows")


if __name__ == "__main__":
    main(sys.argv[1])
