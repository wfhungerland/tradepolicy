"""Validation with monthly data to the latest month: German exports to the US by HS chapter vs the model.

Data: Destatis 51000-0008 (Germany, months, partner country, goods by HS chapter = Warenverzeichnis 2-digit),
exports to the US, 2023 to the latest month, fetched by .github/workflows/fetch-genesis.yml.
Windows (12 months each, so seasonality cancels): before = the 12 months ending one month before the first
tariff month considered (April 2025), i.e. April 2024 to March 2025 is avoided because of front-loading; we use
the 12 months ending August 2024 as the base and the latest 12 months as the outcome, plus the 12 months from
April 2025 as a second outcome.
HS chapters are mapped to ICIO manufacturing sectors (approximation; chapters 84 and 85 split as noted below);
the model value is the change of German exports to the US by sector (partner_pct, scenario current_2026_08).
Writes <output>/kreise/validation_monthly.json and validation_monthly_sectors.csv.
Usage: python 94_validation_monthly.py <rdb_51000-0008.csv> <scenarios.json>
"""
import json
import sys

import numpy as np
import pandas as pd

from config import load_config

HS = {**{c: "C10T12" for c in range(16, 25)}, 25: "C23", 27: "C19", **{c: "C20" for c in [28, 29, 31, 32, 33, 34, 35, 36, 38]},
      30: "C21", 37: "C20", 39: "C22", 40: "C22", **{c: "C13T15" for c in range(41, 44)}, 44: "C16", 45: "C16", 46: "C16",
      47: "C17_18", 48: "C17_18", 49: "C17_18", **{c: "C13T15" for c in range(50, 68)}, 68: "C23", 69: "C23", 70: "C23",
      72: "C24", 73: "C25", 74: "C24", 75: "C24", 76: "C24", 78: "C24", 79: "C24", 80: "C24", 81: "C24", 82: "C25", 83: "C25",
      84: "C28", 85: "C26_27", 86: "C302T309", 87: "C29", 88: "C302T309", 89: "C301", 90: "C26", 91: "C26",
      92: "C31T33", 94: "C31T33", 95: "C31T33", 96: "C31T33"}
COMBINE = {"C24": ["C24A", "C24B"], "C26_27": ["C26", "C27"]}


def main(path, scen):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    d = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    d = d[d.value_variable_code == "WERTA"].copy()
    d["v"] = pd.to_numeric(d.value, errors="coerce")
    d["ym"] = d.time.astype(int) * 100 + d["1_variable_attribute_code"].str[5:].astype(int)
    d["hs"] = pd.to_numeric(d["4_variable_attribute_code"].str[2:], errors="coerce")
    last = int(d[d.v > 0].ym.max())
    ly, lm = divmod(last, 100)
    months = lambda y, m: [(y + (m - 1 - k) // 12) * 100 + (m - 1 - k) % 12 + 1 for k in range(12)]
    win = {"base": months(2024, 8), "latest": months(ly, lm), "from_apr25": months(2026, 3)}
    d["sector"] = d.hs.map(HS)
    sc = json.load(open(scen, encoding="utf-8"))
    cur = [x for x in sc["scenarios"] if x["id"] == "current_2026_08"][0]
    m = pd.DataFrame(cur["sectors_deu"], columns=sc["sector_columns"]).set_index("sector").partner_pct
    for k, v in COMBINE.items():
        m[k] = m[v].mean()
    s = pd.DataFrame({w: d[d.ym.isin(ms)].groupby("sector").v.sum() for w, ms in win.items()})
    s = s[s.base > 0]
    s["obs_latest"] = 100 * (s.latest / s.base - 1)
    s["obs_from_apr25"] = 100 * (s.from_apr25 / s.base - 1)
    s["model"] = s.index.map(m)
    s["base_bn"] = s.base / 1e6
    tot = {w: float(d[d.ym.isin(ms)].v.sum()) for w, ms in win.items()}
    res = {"last_month": last, "total_change_latest": 100 * (tot["latest"] / tot["base"] - 1),
           "total_change_from_apr25": 100 * (tot["from_apr25"] / tot["base"] - 1)}
    for c in ("obs_latest", "obs_from_apr25"):
        z = s.dropna(subset=["model", c])
        w = z.base / z.base.sum()
        res[c] = {"spearman": float(z.model.corr(z[c], method="spearman")), "n": len(z),
                  "weighted_corr": float(np.cov(z.model, z[c], aweights=w)[0, 1] / np.sqrt(np.cov(z.model, aweights=w) * np.cov(z[c], aweights=w))),
                  "spearman_excl_pharma_metals": float(z.drop(index=["C21", "C24", "C25"], errors="ignore")[["model", c]].corr(method="spearman").iloc[0, 1])}
    print(s.sort_values("base_bn", ascending=False)[["base_bn", "obs_latest", "obs_from_apr25", "model"]].round(1).to_string())
    print(json.dumps(res, indent=1))
    s.round(3).to_csv(out / "validation_monthly_sectors.csv")
    (out / "validation_monthly.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
