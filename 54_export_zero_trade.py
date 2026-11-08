"""Export the zero-trade matrices (52_zero_trade.py) for the site.

One file per level, data/zerotrade_<level>.json: countries in display order (same rule
as 53_zero_trade_figures.py), period starts, and for each view (x, two), statistic
(median, mean) and period a matrix of bytes (0 = no trade, 1-255 = share, any positive
share at least 1), base64-encoded row by row. The import view is the transpose of x and
is built in the browser. data/zerotrade_germany.json holds Germany's yearly shares.
Usage: python 54_export_zero_trade.py [target_folder]
"""
import base64
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config

fig = importlib.import_module("53_zero_trade_figures")
LEVELS = ["country", "section", "hs2", "hs4", "hs6"]
STARTS = [None, 2001, 2004, 2008, 2020]


def main(target=None):
    cfg = load_config()
    src = cfg["output"] / "zero_trade"
    out = Path(target) if target else cfg["output"] / "site_data"
    _, cb, x6, _ = fig.load(src / "matrices_hs6.npz")
    m6 = x6.mean(axis=0)
    breadth = dict(zip(cb, m6.sum(axis=0) + m6.sum(axis=1)))
    ger = {}
    for lv in LEVELS:
        years, countries, x, two = fig.load(src / f"matrices_{lv}.npz")
        mc = x.mean(axis=0)
        deg = dict(zip(countries, mc.sum(axis=0) + mc.sum(axis=1)))
        order = sorted(range(len(countries)), key=lambda k: (-breadth.get(countries[k], -1), -deg[countries[k]]))
        binary = lv == "country"
        mats = {}
        for vw, cube in (("x", x), ("two", two)):
            cube = cube[:, order][:, :, order]
            for stat in ("median", "mean"):
                for s in STARTS:
                    v = fig.summary(years, cube, s, stat, binary)
                    np.fill_diagonal(v, 0)
                    b = np.where(v > 0, np.maximum(1, np.round(v * 255)), 0).astype(np.uint8)
                    mats[f"{vw}_{stat}_{s or int(years[0])}"] = base64.b64encode(b.tobytes()).decode()
        data = {"level": lv, "years": [int(years[0]), int(years[-1])], "countries": [countries[k] for k in order],
                "starts": [s or int(years[0]) for s in STARTS], "binary": binary, "matrices": mats}
        p = out / f"zerotrade_{lv}.json"
        p.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        g = pd.read_csv(src / f"germany_{lv}.csv")
        ger[lv] = {"years": g.year.tolist(), **{c: g[c].round(4).tolist() for c in ("two_way", "export_only", "import_only", "none")}}
        print(f"{p.name}: {p.stat().st_size // 1024} kB, {len(countries)} countries")
    (out / "zerotrade_germany.json").write_text(json.dumps(ger, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
