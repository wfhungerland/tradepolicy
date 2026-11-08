"""Export trade by partner regime and UN alignment (56_trade_by_regime.py) as regime.json.
Usage: python 57_export_regime.py [target_folder]
"""
import json
import sys
from pathlib import Path

import pandas as pd

from config import load_config

REG = ["liberale Demokratie", "Wahldemokratie", "Wahlautokratie", "geschlossene Autokratie", "keine Einstufung"]
ALI = ["näher an den USA", "näher an China", "keine Einstufung"]


def main(target=None):
    cfg = load_config()
    src = cfg["output"] / "regime"
    out = Path(target) if target else cfg["output"] / "site_data"
    x = pd.read_excel(src / "regime.xlsx", sheet_name=None, index_col=0)
    series = {}
    for who in ("DEU", "EU27"):
        for flow in ("X", "M"):
            for dim, cats in (("regime", REG), ("bloc", ALI)):
                d = x[f"{who}_{flow}_{dim}"].reindex(columns=cats).fillna(0)
                series[f"{who}_{flow}_{dim}"] = {"years": [int(y) for y in d.index],
                                                 "values": [[round(float(v), 4) for v in d[c]] for c in cats]}
            f = x[f"{who}_{flow}_fix2024"].iloc[:, 0]
            series[f"{who}_{flow}_fixed"] = [round(float(v), 4) for v in f]
            series[f"{who}_{flow}_libdem"] = [round(float(v), 4) for v in x[f"{who}_{flow}_libdem"].iloc[:, 0]]
    b = pd.read_csv(src / "breadth_hs6.csv")
    breadth = {"years": sorted(int(y) for y in b.year.unique()),
               "regimes": {str(r): {"any_export": [round(float(v), 4) for v in (g.two_way + g.export_only)],
                                    "two_way": [round(float(v), 4) for v in g.two_way]}
                           for r, g in b.sort_values("year").groupby("regime")}}
    dep = pd.read_csv(src / "dependencies.csv")
    deps = {lv: {dim: {r["class"]: [int(r.n_goods), round(float(r.imports_bn), 2), round(float(r.share_value), 4)]
                       for _, r in g.iterrows()} for dim, g in h.groupby("dimension")} for lv, h in dep.groupby("level")}
    data = {"categories": {"regime": REG, "bloc": ALI}, "series": series, "breadth": breadth, "dependencies": deps}
    out.mkdir(parents=True, exist_ok=True)
    p = out / "regime.json"
    p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{p.name}: {p.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
