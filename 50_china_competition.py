"""Competition between German and Chinese exports, HS6 good by good (Schott 2008).

Data: CEPII BACI HS92 V202601 (values in thousand USD, quantities in tons). Destinations
exclude Germany and China themselves.

Measures:
  overlap     export similarity index of Finger and Kreinin (1979):
              sum over goods of min(share in German exports, share in Chinese exports)
  price gap   Chinese over German unit value for the same good and destination,
              ln(uv_CHN / uv_DEU), averaged over destinations with German export values
              as weights (Schott 2008 compares China with OECD exporters to the US)
  ladder      quality-ladder length, simplified after Khandelwal (2010): spread of log
              unit values between the 90th and 10th percentile of supplier countries
              into the EU27 (extra- and intra-EU, suppliers >= 1 million USD). Khandelwal
              estimates quality from demand; unit-value spreads are a common proxy.
  China share China's share of world exports of the good (destinations as above)
Exposed goods: German exports >= 100 million USD, China share up by >= 5 points since
2012, Chinese unit value at least half the German one (gap > ln 0.5), ladder shorter
than the median.
Outputs in <output>/scenarios: china_competition_hs6.csv, china_competition_summary.csv.
Usage: python 50_china_competition.py
"""
import importlib
import zipfile

import numpy as np
import pandas as pd

from config import load_config

YEARS = (2012, 2018, 2024)
EU = importlib.import_module("44_dependencies").EU
DEU, CHN = "276", "156"


def load(path):
    with zipfile.ZipFile(path) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str,
                         keep_default_na=False)
        names = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("product_codes"))), dtype=str)
        iso = dict(zip(cc.country_code, cc.country_iso3.replace({"S19": "TWN"})))
        eu = {c for c, i in iso.items() if i in EU}
        exp, imp = {}, None
        for y in YEARS:
            b = pd.read_csv(z.open(next(n for n in z.namelist() if f"_Y{y}_" in n)),
                            dtype={"i": str, "j": str, "k": str}, usecols=["i", "j", "k", "v", "q"])
            exp[y] = b[~b.j.isin([DEU, CHN])]
            if y == YEARS[-1]:
                imp = b[b.j.isin(eu)].groupby(["i", "k"], as_index=False)[["v", "q"]].sum()
            print(y, end=" ", flush=True)
    print()
    names.columns = ["k", "name_en"]
    return exp, imp, names


def similarity(b):
    s = b[b.i.isin([DEU, CHN])].groupby(["i", "k"]).v.sum().unstack(0, fill_value=0)
    s = s / s.sum()
    return float(np.minimum(s[DEU], s[CHN]).sum())


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    exp, imp, names = load(cfg["data"]["scenarios"] / "baci92" / "BACI_HS92_V202601.zip")
    y0, y1 = YEARS[0], YEARS[-1]
    summary = [{"year": y, "export_similarity": similarity(exp[y])} for y in YEARS]

    # China share and German exports by good
    def shares(b):
        w = b.groupby("k").v.sum()
        return pd.DataFrame({"world": w, "deu": b[b.i == DEU].groupby("k").v.sum(),
                             "chn": b[b.i == CHN].groupby("k").v.sum()}).fillna(0)
    s0, s1 = shares(exp[y0]), shares(exp[y1])
    g = pd.DataFrame({"deu_exports_bn": s1.deu / 1e6, "chn_exports_bn": s1.chn / 1e6,
                      "chn_share": s1.chn / s1.world, "deu_share": s1.deu / s1.world})
    g["chn_share_2012"] = (s0.chn / s0.world).reindex(g.index)
    g["deu_share_2012"] = (s0.deu / s0.world).reindex(g.index)

    # price gap: same good and destination, both with positive quantity
    b = exp[y1][exp[y1].i.isin([DEU, CHN]) & (exp[y1].q > 0) & (exp[y1].v > 0)].copy()
    b["luv"] = np.log(b.v / b.q)
    p = b.pivot_table(index=["k", "j"], columns="i", values=["luv", "v"])
    p = p.dropna()
    gap = (p[("luv", CHN)] - p[("luv", DEU)]).rename("gap").to_frame()
    gap["w"] = p[("v", DEU)]
    gap = gap.reset_index()
    g["price_gap_log"] = gap.groupby("k").apply(lambda d: np.average(d.gap, weights=d.w), include_groups=False)
    g["n_markets_both"] = gap.groupby("k").size()

    # quality-ladder length in EU imports
    m = imp[(imp.v >= 1000) & (imp.q > 0)].copy()
    m["luv"] = np.log(m.v / m.q)
    lad = m.groupby("k").luv.agg(lambda x: x.quantile(0.9) - x.quantile(0.1) if len(x) >= 5 else np.nan)
    g["ladder"] = lad
    g = g.join(names.set_index("k"))
    g.index.name = "hs92"

    ladder_median = g.loc[g.deu_exports_bn > 0.1, "ladder"].median()
    g["exposed"] = ((g.deu_exports_bn >= 0.1) & (g.chn_share - g.chn_share_2012 >= 0.05)
                    & (g.price_gap_log > np.log(0.5)) & (g.ladder < ladder_median))
    g.round(5).to_csv(out / "china_competition_hs6.csv")

    big = g[g.deu_exports_bn >= 0.1].dropna(subset=["price_gap_log"])
    w = big.deu_exports_bn
    tot = g.deu_exports_bn.sum()
    overlap = g.loc[g.chn_exports_bn >= 0.001, "deu_exports_bn"].sum() / tot
    summary = pd.DataFrame(summary)
    extra = {"deu_exports_bn_2024": tot, "share_deu_exports_china_also_exports": overlap,
             "median_price_ratio_chn_deu": float(np.exp(big.price_gap_log.median())),
             "weighted_median_price_ratio": float(np.exp(weighted_median(big.price_gap_log, w))),
             "ladder_median": ladder_median, "n_exposed": int(g.exposed.sum()),
             "exposed_deu_exports_bn": float(g.loc[g.exposed, "deu_exports_bn"].sum())}
    for k, v in extra.items():
        print(f"{k}: {v:.3f}")
    print(summary.round(3).to_string(index=False))
    pd.concat([summary, pd.DataFrame([extra])]).to_csv(out / "china_competition_summary.csv", index=False)
    # validation: price gap should fall with ladder length (Khandelwal: China competes in
    # short-ladder goods) and China share should rise faster where Chinese prices are close
    from scipy.stats import spearmanr
    print("rank corr ladder vs price gap:", round(spearmanr(big.ladder, big.price_gap_log, nan_policy="omit").statistic, 3))
    d = big.chn_share - big.chn_share_2012
    print("rank corr price gap vs change in China share:", round(spearmanr(big.price_gap_log, d, nan_policy="omit").statistic, 3))
    print("rank corr change China share vs change German share:",
          round(spearmanr(d, big.deu_share - big.deu_share_2012, nan_policy="omit").statistic, 3))
    cols = ["name_en", "deu_exports_bn", "chn_share_2012", "chn_share", "price_gap_log", "ladder"]
    print(g[g.exposed].sort_values("deu_exports_bn", ascending=False)[cols].head(15).round(3).to_string())


def weighted_median(x, w):
    x, w = np.asarray(x), np.asarray(w)
    o = np.argsort(x)
    return float(x[o][np.searchsorted(np.cumsum(w[o]) / w.sum(), 0.5)])


if __name__ == "__main__":
    main()
