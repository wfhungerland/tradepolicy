"""Who lives in the districts hit hardest by US tariffs? A profile with INKAR.

Data: INKAR 2025 (BBSR, Gebietsstand 31.12.2023; full CSV from the user, district rows
extracted to inkar_2025_kreise.parquet), and the district US tariff exposure of
74_kreise_us_tariffs.py (manufacturing output loss per inhabitant, US tariffs August 2026).
Districts are split into five equal groups (quintiles) by the loss per inhabitant; for each
group the population-weighted mean of selected INKAR indicators (latest year) is shown,
plus Spearman correlations across districts.
Writes <output>/kreise/profile_us_tariffs.csv and site data kreise_profile.json.
Usage: python 78_kreise_profile.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config

IND = {"Arbeitslosenquote": ("Arbeitslosenquote, %", "Unemployment rate, %"),
       "Medianeinkommen": ("Medianeinkommen Vollzeit, EUR je Monat", "Median full-time earnings, EUR per month"),
       "Industriequote": ("Industriebeschäftigte je 100 Einwohner von 15 bis 64", "Industry employees per 100 inhabitants aged 15-64"),
       "Bruttoinlandsprodukt je Einwohner": ("BIP je Einwohner, Tsd. EUR", "GDP per head, EUR thousand"),
       "Durchschnittsalter der Bevölkerung": ("Durchschnittsalter, Jahre", "Mean age, years"),
       "Beschäftigte am AO mit akademischem Berufsabschluss": ("Beschäftigte mit Hochschulabschluss, %", "Employees with university degree, %"),
       "pop_growth": ("Bevölkerung 2013 bis 2023, %", "Population 2013 to 2023, %"),
       "Wahlbeteiligung": ("Wahlbeteiligung Bundestag 2025, %", "Turnout federal election 2025, %"),
       "Stimmenanteile AfD": ("Zweitstimmen AfD 2025, %", "AfD party-list vote 2025, %")}


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "inkar"
    out = cfg["output"] / "kreise"
    d = pd.read_parquet(raw / "inkar_2025_kreise.parquet")
    fix = {v: v.encode("latin1").decode("utf8", "ignore") for v in d.Indikator.dropna().unique()}   # read as latin1, file is UTF-8
    d["Indikator"] = d.Indikator.map(fix)
    d["ags"] = d.Kennziffer.str.zfill(8).str[:5]                  # INKAR district keys have 8 digits (AGS + 000)
    pop = d[d.Indikator == "Bevölkerung gesamt"].pivot_table(index="ags", columns="Zeitbezug", values="Wert")
    x = pd.DataFrame(index=pop.index)
    for name in IND:
        if name == "pop_growth":
            x[name] = 100 * (pop[2023] / pop[2013] - 1)
            continue
        s = d[d.Indikator == name]
        y = s.Zeitbezug.max()
        x[name] = s[s.Zeitbezug == y].set_index("ags").Wert
        print(f"{name}: year {y}, {x[name].notna().sum()} districts, mean {x[name].mean():.1f}")
    x["pop"] = pop[2023]
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")[["name", "loss_pc", "dm"]]
    m = x.join(u, how="inner").dropna(subset=["loss_pc"])
    m["q"] = pd.qcut(m.loss_pc, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    wmean = lambda g, c: np.average(g[c].dropna(), weights=g.loc[g[c].notna(), "pop"])
    rows = []
    for q, g in m.groupby("q"):
        r = {"quintile": q, "n": len(g), "loss_pc_min": g.loss_pc.min(), "loss_pc_max": g.loss_pc.max(), "loss_pc_mean": wmean(g, "loss_pc")}
        r.update({c: wmean(g, c) for c in IND})
        rows.append(r)
    t = pd.DataFrame(rows)
    corr = {c: m[[c, "loss_pc"]].corr(method="spearman").iloc[0, 1] for c in IND}
    t.round(3).to_csv(out / "profile_us_tariffs.csv", index=False)
    print(t.round(1).T.to_string())
    print("Spearman with loss per inhabitant:", {k: round(v, 2) for k, v in corr.items()})
    if site:
        j = {"labels": {k: v for k, v in IND.items()}, "quintiles": t.round(2).to_dict("records"), "spearman": {k: round(v, 2) for k, v in corr.items()},
             "n": int(len(m))}
        p = Path(site) / "kreise_profile.json"
        p.write_text(json.dumps(j, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(p.name, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
