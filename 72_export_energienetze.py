"""Site data for the hydrogen core network and the transmission grid expansion charts.
Reads the outputs of 69_h2_kernnetz.py and 70_netzausbau.py.
Usage: python 72_export_energienetze.py site_data_folder
"""
import json
import sys
from pathlib import Path

import pandas as pd

from config import load_config


def main(site):
    o = load_config()["output"]
    full = pd.read_csv(o / "h2" / "h2_kernnetz_laender.csv", index_col=0)
    land = full.drop(index=["unbekannt"], errors="ignore")       # nationwide items (e.g. compressors) only in the totals
    yr = pd.read_csv(o / "h2" / "h2_kernnetz_jahre.csv", index_col=0)
    st = pd.read_csv(o / "netzausbau" / "status.csv")
    plan = pd.read_csv(o / "netzausbau" / "plan_jahre.csv", index_col=0).iloc[:, 0]
    plan = plan.reindex(range(int(plan.index.min()), int(plan.index.max()) + 1)).ffill()
    d = {"h2": {"land": land.index.tolist(), "neu": land.Neubau.round(0).tolist(), "um": land.Umstellung.round(0).tolist(),
                "inv": land.inv_mio.round(0).tolist(), "inv_total": round(float(full.inv_mio.sum())), "km_total": round(float(full.gesamt.sum())), "years": yr.index.astype(int).tolist(),
                "cum_neu": yr.Neubau.round(0).tolist(), "cum_um": yr.Umstellung.round(0).tolist()},
         "nab": {"status": st.status.tolist(), "km": st.km.tolist(), "years": plan.index.astype(int).tolist(), "cum": plan.round(0).tolist(),
                 "stand": "30.06.2026", "undated_km": 2806, "undated_n": 11}}
    p = Path(site) / "energienetze.json"
    p.write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(p, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
