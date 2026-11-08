"""Export the China competition analysis (50_china_competition.py) as competition.json.
Usage: python 51_export_china_competition.py [target_folder]
"""
import csv
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config

m44 = importlib.import_module("44_dependencies")


def main(target=None):
    cfg = load_config()
    src = cfg["output"] / "scenarios"
    out = Path(target) if target else cfg["output"] / "site_data"
    g = pd.read_csv(src / "china_competition_hs6.csv", dtype={"hs92": str})
    s = pd.read_csv(src / "china_competition_summary.csv")
    de4 = {r["hs4"]: r["name_de"] for r in csv.DictReader(open(Path(__file__).parent / "product_names_de.csv", encoding="utf-8"))}
    g["section"] = g.hs92.map(m44.section)
    big = g[g.deu_exports_bn >= 0.1]
    sec = []
    for name, d in big.groupby("section"):
        w = d.deu_exports_bn
        sec.append([name, round(float(w.sum()), 1), round(float(d.loc[d.exposed, "deu_exports_bn"].sum()), 1),
                    round(float((d.chn_share * w).sum() / w.sum()), 4), round(float((d.chn_share_2012 * w).sum() / w.sum()), 4),
                    round(float((d.deu_share * w).sum() / w.sum()), 4), round(float((d.deu_share_2012 * w).sum() / w.sum()), 4)])
    sec.sort(key=lambda r: -r[2])
    ex = g[g.exposed].sort_values("deu_exports_bn", ascending=False)
    x = s.iloc[-1]
    esi = s.dropna(subset=["year"])
    data = {
        "year": 2024, "base_year": 2012,
        "similarity": [[int(r.year), round(r.export_similarity, 4)] for r in esi.itertuples()],
        "deu_exports_bn": round(float(x.deu_exports_bn_2024), 1),
        "price_ratio_median": round(float(x.median_price_ratio_chn_deu), 3),
        "price_ratio_weighted": round(float(x.weighted_median_price_ratio), 3),
        "ladder_median": round(float(x.ladder_median), 3),
        "n_exposed": int(x.n_exposed), "exposed_bn": round(float(x.exposed_deu_exports_bn), 1),
        "sections_columns": ["section", "deu_exports_bn", "exposed_bn", "chn_share", "chn_share_2012", "deu_share", "deu_share_2012"],
        "sections": sec,
        "columns": ["hs92", "name_de_hs4", "name_en", "deu_exports_bn", "chn_share_2012", "chn_share", "deu_share_2012",
                    "deu_share", "price_ratio", "ladder"],
        "products": [[r.hs92, de4.get(r.hs92[:4], ""), r.name_en, round(r.deu_exports_bn, 3), round(r.chn_share_2012, 3),
                      round(r.chn_share, 3), round(r.deu_share_2012, 3), round(r.deu_share, 3),
                      round(float(np.exp(r.price_gap_log)), 3), round(r.ladder, 3)] for r in ex.itertuples()],
    }
    out.mkdir(parents=True, exist_ok=True)
    p = out / "competition.json"
    p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{p.name}: {p.stat().st_size // 1024} kB")
    for r in sec[:8]:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
