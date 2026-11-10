"""Eight district analyses with INKAR 2025 (BBSR), for the site tab "Kreise".

Inputs: inkar_2025_kreise.parquet (district rows of INKAR 2025, Gebietsstand 2023),
<output>/kreise/us_tariffs_kreise.csv (74), export_kreise.csv (73), regional exposure NUTS 2 (64).
Quintiles: five equal groups of districts by US tariff loss per inhabitant (74); means weighted
by population. Regressions: OLS with Land fixed effects, heteroskedasticity-robust standard
errors; regressors standardised (effect of one standard deviation). All results are associations
across districts, not causal effects.
  1 skilled labour       labour-market indicators by tariff quintile
  2 demography           projected population 2022-2045 by quintile; districts with both risks
  4 votes                change of AfD vote 2017-2025 on tariff exposure and de-industrialisation
  5 broadband            change of IT and creative employment 2017-2023 on gigabit coverage 2020
  6 industrial decline   change of industry share 2019-2023 on export ratio change and energy intensity
  7 accessibility        export ratio and foreign sales per head on travel times
  8 migration            foreigners' share and employment rate by industry-share quintile
  10 poverty             SGB II rate and child poverty by tariff quintile; districts with both risks
Writes <output>/kreise/inkar_analyses.json and site data kreise_inkar.json.
Usage: python 79_inkar_analyses.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyfixest as pf

from config import load_config


def load_inkar(path):
    d = pd.read_parquet(path)
    fix = {v: v.encode("latin1").decode("utf8", "ignore") for v in d.Indikator.dropna().unique()}
    d["I"] = d.Indikator.map(fix)
    d["ags"] = d.Kennziffer.str.zfill(8).str[:5]
    return d


def get(d, name, year=None):
    s = d[d.I == name]
    y = year or s.Zeitbezug.max()
    return s[s.Zeitbezug == y].groupby("ags").Wert.first().rename(f"{name}|{y}")   # same indicator can appear in two themes


def wq(m, cols, by="q"):
    w = lambda g, c: np.average(g[c].dropna(), weights=g.loc[g[c].notna(), "pop"]) if g[c].notna().any() else np.nan
    return pd.DataFrame([{by: q, "n": len(g), **{c: w(g, c) for c in cols}} for q, g in m.groupby(by)])


def reg(m, y, xs, ctrl):
    z = m.copy()
    for x in xs:
        z[x] = (z[x] - z[x].mean()) / z[x].std()
    f = f"{y} ~ {' + '.join(xs + ctrl)} | land"
    r = pf.feols(f, data=z.dropna(subset=[y] + xs + ctrl), vcov="hetero")
    return [{"x": x, "b": float(r.coef()[x]), "se": float(r.se()[x]), "p": float(r.pvalue()[x])} for x in xs], int(r._N), float(r._r2)


def main(site=None):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    d = load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    ex = pd.read_csv(out / "export_kreise.csv", dtype={"ags": str}).set_index("ags")
    m = pd.DataFrame(index=u.index)
    m["name"], m["loss"], m["pop"] = u.name, u.loss_pc, u["pop"]
    m["q"] = pd.qcut(m.loss, 5, labels=[1, 2, 3, 4, 5]).astype(float)
    m["land"] = m.index.str[:2]
    m["ln_dens"] = np.log(get(d, "Einwohnerdichte"))
    v = lambda n, y=None: get(d, n, y).reindex(m.index).values
    items = []

    # 1 skilled labour
    m["alq"] = v("Arbeitslosenquote"); m["fk_alo"] = v("Arbeitslose mit Anforderungsniveau Fachkraft")
    m["fk_os"] = v("Offene Stellen mit Anforderungsniveau Fachkraft"); m["bq"] = v("Beschäftigtenquote")
    t = wq(m.dropna(subset=["q"]), ["alq", "fk_alo", "fk_os", "bq"])
    items.append({"id": "fachkraefte", "table": t.round(1).to_dict("records"), "cols": ["alq", "fk_alo", "fk_os", "bq"]})

    # 2 demography
    m["prog"] = v("Prognostizierte Bevölkerungsentwicklung (2022-2045)")
    t = wq(m.dropna(subset=["q"]), ["prog"])
    both = m[(m.q == 5) & (m.prog < -5)].sort_values("loss", ascending=False)
    items.append({"id": "demografie", "table": t.round(1).to_dict("records"), "cols": ["prog"],
                  "both": [[r["name"], round(r.loss), round(r.prog, 1)] for _, r in both.iterrows()]})

    # 4 votes
    m["afd17"], m["afd25"] = v("Stimmenanteile AfD", 2017), v("Stimmenanteile AfD", 2025)
    m["d_afd"] = m.afd25 - m.afd17
    m["iq13"], m["iq23"] = v("Industriequote", 2013), v("Industriequote", 2023)
    m["d_iq"] = m.iq23 - m.iq13
    m["inc"] = np.log(v("Medianeinkommen")); m["age"] = v("Durchschnittsalter der Bevölkerung")
    co, n, r2 = reg(m, "d_afd", ["loss", "d_iq"], ["alq", "inc", "age", "ln_dens"])
    items.append({"id": "wahlen", "coef": co, "n": n, "r2": r2, "mean_d": float(np.average(m.d_afd.dropna(), weights=m.loc[m.d_afd.notna(), "pop"]))})

    # 5 broadband
    m["giga20"] = v("Bandbreitenverfügbarkeit mindestens 1.000 Mbit/s", 2020)
    m["it17"], m["it23"] = v("Beschäftigte in IT- und naturwissenschaftlichen Dienstleistungsberufen", 2017), v("Beschäftigte in IT- und naturwissenschaftlichen Dienstleistungsberufen", 2023)
    m["kr17"], m["kr23"] = v("Beschäftigte in Kreativbranchen", 2017), v("Beschäftigte in Kreativbranchen", 2023)
    m["d_it"], m["d_kr"] = m.it23 - m.it17, m.kr23 - m.kr17
    c1, n1, _ = reg(m, "d_it", ["giga20"], ["it17", "ln_dens"])
    c2, n2, _ = reg(m, "d_kr", ["giga20"], ["kr17", "ln_dens"])
    items.append({"id": "breitband", "coef": c1 + c2, "labels": ["IT", "Kreativ"], "n": n1, "mean_it": float(m.d_it.mean()), "mean_kr": float(m.d_kr.mean())})

    # 6 industrial decline 2019-2023
    m["iq19"] = v("Industriequote", 2019); m["d_iq19"] = m.iq23 - m.iq19
    m["d_exq"] = 100 * (ex.quote_2024 - ex.quote_2019).reindex(m.index)
    reg2 = pd.read_csv(cfg["output"] / "regional" / "exposure_nuts2.csv").set_index("geo")
    m["energy"] = 100 * ex.nuts3.reindex(m.index).str[:4].map(reg2.energy_share).values
    co6, n6, r6 = reg(m, "d_iq19", ["d_exq", "energy"], ["iq19", "ln_dens"])
    items.append({"id": "industrie", "coef": co6, "n": n6, "r2": r6, "mean_d": float(np.average(m.d_iq19.dropna(), weights=m.loc[m.d_iq19.notna(), "pop"])),
                  "share_down": float((m.d_iq19 < 0).mean())})

    # 7 accessibility
    m["t_bab"], m["t_air"], m["t_ic"] = v("Erreichbarkeit von Autobahnen"), v("Erreichbarkeit von Flughäfen"), v("Erreichbarkeit von IC/EC/ICE-Bahnhöfen")
    m["exq"] = 100 * ex.quote_2024.reindex(m.index); m["ln_ausl"] = np.log(ex.ausl_pc.reindex(m.index))
    a1, na, ra = reg(m, "exq", ["t_bab", "t_air", "t_ic"], ["iq23", "ln_dens"])
    a2, _, _ = reg(m, "ln_ausl", ["t_bab", "t_air", "t_ic"], ["iq23", "ln_dens"])
    items.append({"id": "erreichbarkeit", "coef": a1, "coef_ln": a2, "n": na, "r2": ra,
                  "means": {k: float(m[k].mean()) for k in ("t_bab", "t_air", "t_ic")}})

    # 8 migration by industry-share quintile
    m["fq"] = pd.qcut(m.iq23, 5, labels=[1, 2, 3, 4, 5]).astype(float)
    m["ausl"], m["bq_ausl"] = v("Ausländeranteil"), v("(SDG 10) Beschäftigungsquote - Ausländer")
    t = wq(m.dropna(subset=["fq"]), ["iq23", "ausl", "bq_ausl"], by="fq")
    items.append({"id": "migration", "table": t.round(1).to_dict("records"), "cols": ["iq23", "ausl", "bq_ausl"],
                  "rho_exq": float(m[["ausl", "exq"]].corr(method="spearman").iloc[0, 1])})

    # 10 poverty
    m["sgb2"], m["kinder"] = v("SGB II - Quote"), v("(SDG 1) Armut - Kinderarmut")
    t = wq(m.dropna(subset=["q"]), ["sgb2", "kinder"])
    thr = m.sgb2.quantile(0.8)
    both = m[(m.q == 5) & (m.sgb2 >= thr)].sort_values("loss", ascending=False)
    items.append({"id": "armut", "table": t.round(1).to_dict("records"), "cols": ["sgb2", "kinder"], "thr": float(thr),
                  "both": [[r["name"], round(r.loss), round(r.sgb2, 1)] for _, r in both.iterrows()]})

    res = {"n": int(m.q.notna().sum()), "items": items}
    for it in items:
        print("##", it["id"], json.dumps({k: v for k, v in it.items() if k != "id"}, ensure_ascii=False, default=float)[:900])
    (out / "inkar_analyses.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    m.round(4).to_csv(out / "inkar_analyses_kreise.csv")
    if site:
        # map layers by NUTS 3 code (site tab Kreise)
        m["nuts3"] = u.nuts3.reindex(m.index)
        m["risk_demo"] = np.where(m.q.isna() | m.prog.isna(), np.nan, np.where((m.q == 5) & (m.prog < -5), 3, np.where(m.q == 5, 2, np.where(m.prog < -5, 1, 0))))
        m["risk_pov"] = np.where(m.q.isna() | m.sgb2.isna(), np.nan, np.where((m.q == 5) & (m.sgb2 >= thr), 3, np.where(m.q == 5, 2, np.where(m.sgb2 >= thr, 1, 0))))
        keep = ["alq", "fk_os", "prog", "risk_demo", "d_afd", "giga20", "d_it", "d_iq19", "t_air", "ausl", "bq_ausl", "sgb2", "kinder", "risk_pov"]
        mp = {r.nuts3: {k: (None if pd.isna(r[k]) else round(float(r[k]), 2)) for k in keep} for _, r in m.dropna(subset=["nuts3"]).iterrows()}
        (Path(site) / "kreise_inkar_map.json").write_text(json.dumps(mp, separators=(",", ":")), encoding="utf-8")
        p = Path(site) / "kreise_inkar.json"
        p.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":"), default=lambda x: round(float(x), 4)), encoding="utf-8")
        print(p.name, p.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
