"""Do targeted Chinese subsidies concentrate on goods where Germany faces Chinese price pressure,
also within industries?

Unit: HS 6-digit good (HS92) with German exports (50_china_competition.py). Outcome: number of
targeted Chinese subsidies in force (75_subsidies.py: GTA chapters L and P, red/amber, not
horizontal, at most 50 products). Regressor: exposed (price pressure as defined in 50).
Models: PPML on the count, without and with HS 2-digit (chapter) and HS 4-digit (heading) fixed
effects, with and without controls (log German and Chinese exports), for all goods and for goods
with German exports >= 100 million USD (the size threshold of the exposure definition, so that
exposed goods are compared with goods of similar size).
Result (November 2026): the raw gap (25 vs 10 subsidies per good) is a size effect; among goods
of similar size (25 vs 20) and within chapters the difference is small and not significant.
Standard errors clustered by HS 4-digit heading.
Writes <output>/subsidies/regression.csv.
"""
import importlib

import numpy as np
import pandas as pd
import pyfixest as pf

from config import load_config


def counts(cfg):
    sub = importlib.import_module("75_subsidies")
    d = pd.read_csv(cfg["data"]["scenarios"] / "gta" / "interventions.csv", low_memory=False,
                    usecols=["Intervention ID", "Mast Chapter", "GTA Evaluation", "Implementing Jurisdictions", "Affected Products", "Is Horizontal", "Is In Force"])
    s = d[d["Mast Chapter"].str[:2].isin(["L:", "P:"]) & d["GTA Evaluation"].isin(["Red", "Amber"]) & (d["Is In Force"] == 1)
          & d["Affected Products"].notna() & (d["Is Horizontal"].astype(str) != "True") & d["Implementing Jurisdictions"].str.contains("China", na=False)]
    cnt = {}
    for prods in s["Affected Products"]:
        hs = set(x.strip().zfill(6) for x in str(prods).split(","))
        if len(hs) <= sub.MAXP:
            for h in hs:
                cnt[h] = cnt.get(h, 0) + 1
    return pd.Series(cnt, name="n_cn")


def main():
    cfg = load_config()
    c = pd.read_csv(cfg["output"] / "scenarios" / "china_competition_hs6.csv", dtype={"hs92": str})
    c = c.join(counts(cfg), on="hs92").fillna({"n_cn": 0})
    c = c[c.deu_exports_bn > 0].copy()
    c["exposed"] = c.exposed.fillna(False).astype(int)
    c["any_cn"] = (c.n_cn > 0).astype(int)
    c["ln_de"] = np.log(c.deu_exports_bn)
    c["ln_cn"] = np.log(c.chn_exports_bn.clip(lower=1e-6))
    c["hs2"], c["hs4"] = c.hs92.str[:2], c.hs92.str[:4]
    rows = []
    for sample, x in (("alle Waren", c), ("Waren mit deutschen Exporten >= 100 Mio. USD", c[c.deu_exports_bn >= 0.1])):
        for fe, lab in (("", "keine"), ("| hs2", "HS-Kapitel"), ("| hs4", "HS-Position")):
            for ctrl in ("", " + ln_de + ln_cn"):
                f = f"n_cn ~ exposed{ctrl} {fe}"
                m = pf.fepois(f, data=x, vcov={"CRV1": "hs4"})
                b, se, p = m.coef()["exposed"], m.se()["exposed"], m.pvalue()["exposed"]
                rows.append({"stichprobe": sample, "fe": lab, "kontrollen": "ja" if ctrl else "nein", "coef": b, "se": se, "p": p,
                             "effekt_pct": 100 * (np.exp(b) - 1), "n": int(m._N), "mean_exposed": x[x.exposed == 1].n_cn.mean(), "mean_other": x[x.exposed == 0].n_cn.mean()})
    r = pd.DataFrame(rows)
    r.round(4).to_csv(cfg["output"] / "subsidies" / "regression.csv", index=False)
    print(f"goods: {len(c)}, exposed {c.exposed.sum()}")
    print(r.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
