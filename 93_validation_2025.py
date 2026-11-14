"""First check of the US tariff scenario against 2025: exports to the US by product group and Land.

Data: Destatis 51000-0036, exports of each Land to the United States by product group (GP 2019, 2-digit),
2019-2025, one file per Land (rdb_51000-0036_US_LL.csv), and 51000-0034, exports of each Land to all
destinations by product group, both fetched by .github/workflows/fetch-genesis.yml (branch data-genesis).
Model: Caliendo-Parro scenario current_2026_08 (34), German sector results: change of exports to the US
(partner_pct) and of output (output_pct), from site/data/scenarios.json; GP divisions mapped to ICIO sectors
(24 basic metals split equally between C24A and C24B by averaging their shocks; 30 to C301 and C302T309 average).
Tests (Spearman, weighted where noted):
  1 sectors: modelled change of exports to the US vs observed change 2024-2025, nationally, manufacturing
    divisions 10-33; also with 2023-2025 to look past front-loading in early 2025;
  2 Länder x sectors: observed change of US exports vs the national modelled change of the sector;
  3 Länder: modelled % output loss (74, published and imputed) vs observed change of US exports, and vs the
    change of US exports predicted by each Land's 2024 product mix and the national observed change by product
    (shift-share of the observed shock), which isolates the composition channel the model works through.
Writes <output>/kreise/validation_2025.json and a table by product group (validation_2025_products.csv).
Usage: python 93_validation_2025.py <folder with the GENESIS files> <path to scenarios.json>
"""
import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config

GP2ICIO = {"10": ["C10T12"], "11": ["C10T12"], "12": ["C10T12"], "13": ["C13T15"], "14": ["C13T15"], "15": ["C13T15"],
           "16": ["C16"], "17": ["C17_18"], "18": ["C17_18"], "19": ["C19"], "20": ["C20"], "21": ["C21"], "22": ["C22"],
           "23": ["C23"], "24": ["C24A", "C24B"], "25": ["C25"], "26": ["C26"], "27": ["C27"], "28": ["C28"], "29": ["C29"],
           "30": ["C301", "C302T309"], "31": ["C31T33"], "32": ["C31T33"]}


def read(files, value="WERTA"):
    d = pd.concat([pd.read_csv(f, sep=";", dtype=str, encoding="utf-8-sig") for f in files])
    d = d[d.value_variable_code == value].copy()
    d["v"] = pd.to_numeric(d.value.str.replace(",", "."), errors="coerce")
    pcol = [c for c in d.columns if c.endswith("_variable_code") and d[c].iloc[0] == "GP19B2"][0].replace("_code", "_attribute_code")
    d["gp"] = d[pcol].str.replace("GP19-", "", regex=False)
    d["land"] = d["1_variable_attribute_code"]
    return d


def sp(a, b):
    z = pd.concat([a, b], axis=1).dropna()
    return float(z.iloc[:, 0].corr(z.iloc[:, 1], method="spearman")), len(z)


def main(folder, scen):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    us = read(sorted(glob.glob(str(Path(folder) / "rdb_51000-0036_US_*.csv"))))
    us = us[us.land.isin([f"{i:02d}" for i in range(1, 17)])]
    sc = json.load(open(scen, encoding="utf-8"))
    cur = [x for x in sc["scenarios"] if x["id"] == "current_2026_08"][0]
    m = pd.DataFrame(cur["sectors_deu"], columns=sc["sector_columns"]).set_index("sector")
    mod_x = {gp: float(np.mean([m.loc[s, "partner_pct"] for s in v])) for gp, v in GP2ICIO.items()}
    mod_y = {gp: float(np.mean([m.loc[s, "output_pct"] for s in v])) for gp, v in GP2ICIO.items()}
    man = us[us.gp.isin(GP2ICIO)]
    nat = man.groupby(["gp", "time"]).v.sum().unstack()
    names = man.groupby("gp")[[c for c in man.columns if c.endswith("attribute_label")][-1]].first()
    nat = nat.dropna(subset=["2024", "2025"])
    t = pd.DataFrame({"name": names, "us_2024_bn": nat["2024"] / 1e6, "obs_25_24": 100 * (nat["2025"] / nat["2024"] - 1),
                      "obs_25_23": 100 * (nat["2025"] / nat["2023"] - 1), "model_us_exports": pd.Series(mod_x),
                      "model_output": pd.Series(mod_y)})
    res = {"sectors": {}}
    for c in ("obs_25_24", "obs_25_23"):
        r, n = sp(t.model_us_exports, t[c])
        res["sectors"][c] = {"rho": r, "n": n}
    big = t[t.us_2024_bn > 1]
    res["sectors"]["obs_25_24_big"] = dict(zip(("rho", "n"), sp(big.model_us_exports, big.obs_25_24)))
    t = t.dropna(subset=["obs_25_24"])
    ex = t.drop(index=["21", "24", "25"], errors="ignore")             # pharmaceuticals and metals: tariffs phased in late
    res["sectors"]["obs_25_24_excl_pharma_metals"] = dict(zip(("rho", "n"), sp(ex.model_us_exports, ex.obs_25_24)))
    w = t.us_2024_bn / t.us_2024_bn.sum()
    res["sectors"]["weighted_corr"] = float(np.cov(t.model_us_exports, t.obs_25_24, aweights=w)[0, 1] /
                                            np.sqrt(np.cov(t.model_us_exports, aweights=w) * np.cov(t.obs_25_24, aweights=w)))
    print(t.sort_values("us_2024_bn", ascending=False).round(1).to_string())
    # 2 Land x sector
    ls = man.groupby(["land", "gp", "time"]).v.sum().unstack()
    ls = ls[(ls["2024"] > 50000)]                                    # at least EUR 50 million in 2024
    ls["obs"] = 100 * (ls["2025"] / ls["2024"] - 1)
    ls["model"] = ls.index.get_level_values("gp").map(mod_x)
    res["land_sector"] = dict(zip(("rho", "n"), sp(ls.model, ls.obs)))
    # 3 Länder
    lt = us.groupby(["land", "time"]).v.sum().unstack()
    obs_l = 100 * (lt["2025"] / lt["2024"] - 1)
    natchg = (nat["2025"] / nat["2024"] - 1)
    mix = man[man.time == "2024"].groupby(["land", "gp"]).v.sum().unstack().fillna(0)
    pred_l = 100 * (mix * natchg).sum(axis=1) / mix.sum(axis=1)
    b = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    i = pd.read_csv(out / "us_tariffs_kreise_imputed.csv", dtype={"ags": str}).set_index("ags")
    g = lambda x: 100 * x.loss_mio.groupby(x.index.str[:2]).sum() / x.umsatz_mio_2024.groupby(x.index.str[:2]).sum()
    res["laender"] = {"model_vs_obs": dict(zip(("rho", "n"), sp(-g(b), obs_l))), "model_imp_vs_obs": dict(zip(("rho", "n"), sp(-g(i), obs_l))),
                      "mix_pred_vs_obs": dict(zip(("rho", "n"), sp(pred_l, obs_l))), "model_vs_mix_pred": dict(zip(("rho", "n"), sp(-g(i), pred_l)))}
    res["national"] = {"us_exports_manuf_25_24": float(100 * (nat["2025"].sum() / nat["2024"].sum() - 1)),
                       "model_us_exports_manuf": float((t.model_us_exports * w).sum())}
    print(json.dumps(res, indent=1))
    t.round(3).to_csv(out / "validation_2025_products.csv")
    (out / "validation_2025.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
