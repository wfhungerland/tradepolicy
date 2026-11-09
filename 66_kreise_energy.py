"""Electricity generation capacity by German district (Kreis), 1990-2026.

Data: Marktstammdatenregister (Bundesnetzagentur, Datenlizenz Deutschland 2.0), aggregated
to districts on the user's server by tools/server_fetch_kreise.py (capacity in operation
at year end, gross MW, by energy source; units without municipality key, notably offshore
wind, are not assigned). District key -> NUTS 3 and population/area from Destatis
("Kreisfreie Städte und Landkreise nach Fläche, Bevölkerung und Bevölkerungsdichte",
31.12.2024). Maps on GISCO NUTS 2024 level 3.
Indicators per district: solar and wind kW per inhabitant, renewable share of installed
capacity, fossil capacity (lignite, hard coal, gas, oil, other gases, waste), growth of
solar and wind 2015-2025.
Writes <output>/kreise/energy_kreise.csv, maps and site data (kreise_energy.json).
Usage: python 66_kreise_energy.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import regional as rg
from config import load_config

GROUPS = {"Solare Strahlungsenergie": "solar", "Wind": "wind", "Biomasse": "bio", "Wasser": "hydro",
          "Braunkohle": "lignite", "Steinkohle": "coal", "Erdgas": "gas", "Mineralölprodukte": "fossil_other",
          "andere Gase": "fossil_other", "nicht biogener Abfall": "fossil_other", "Wärme": "other", "Wasserstoff": "other",
          "Kernenergie": "nuclear", "Speicher": "storage"}
RENEW = ["solar", "wind", "bio", "hydro"]
FOSSIL = ["lignite", "coal", "gas", "fossil_other"]


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "kreise"
    rraw = cfg["data"]["scenarios"] / "regional"
    out = cfg["output"] / "kreise"
    out.mkdir(parents=True, exist_ok=True)
    m = pd.read_csv(raw / "mastr_kreis_jahr.csv", dtype={"kreis": str})
    m["g"] = m.energietraeger.map(GROUPS).fillna("other")
    k = pd.read_excel(raw / "kreise.xlsx", sheet_name=1, header=None, skiprows=3)
    k = k.iloc[:, [0, 2, 3, 4, 5]]
    k.columns = ["ags", "name", "nuts3", "area", "pop"]
    k = k[k.ags.astype(str).str.len() == 5].dropna(subset=["nuts3"])
    k["ags"] = k.ags.astype(str)
    matched = m[m.jahr == 2025].kreis.isin(k.ags)
    share = m[(m.jahr == 2025) & matched].brutto_mw.sum() / m[m.jahr == 2025].brutto_mw.sum()
    print(f"capacity 2025 matched to current districts: {share:.1%}; unmatched keys: {m[(m.jahr == 2025) & ~matched].kreis.nunique()}")
    p = m[m.kreis.isin(k.ags)].pivot_table(index=["kreis", "jahr"], columns="g", values="brutto_mw", aggfunc="sum").fillna(0)
    for c in RENEW + FOSSIL + ["nuclear", "storage", "other"]:
        if c not in p:
            p[c] = 0.0
    p = p.reset_index().merge(k, left_on="kreis", right_on="ags")
    p["renew"] = p[RENEW].sum(axis=1)
    p["fossil"] = p[FOSSIL].sum(axis=1)
    p["total"] = p.renew + p.fossil + p.nuclear + p.other
    p["solar_kw_pc"] = p.solar * 1000 / p["pop"]
    p["wind_kw_pc"] = p.wind * 1000 / p["pop"]
    p["renew_share"] = p.renew / p.total
    p.round(4).to_csv(out / "energy_kreise.csv", index=False)
    y = p[p.jahr == 2025].set_index("nuts3")
    y15 = p[p.jahr == 2015].set_index("nuts3")
    y["sw_growth"] = (y.solar + y.wind) / (y15.solar + y15.wind).reindex(y.index)
    tot = y[["solar", "wind", "lignite", "coal", "gas"]].sum() / 1000
    print("Germany 2025, GW:", tot.round(1).to_dict())
    print("most wind per head:", y.sort_values("wind_kw_pc", ascending=False).head(5)[["name", "wind_kw_pc"]].round(1).values.tolist())
    print("most solar per head:", y.sort_values("solar_kw_pc", ascending=False).head(5)[["name", "solar_kw_pc"]].round(1).values.tolist())
    print("lignite districts:", y[y.lignite > 0].sort_values("lignite", ascending=False)[["name", "lignite"]].round(0).values.tolist()[:8])

    shapes, names = rg.load_nuts(rraw / "nuts3_2024_10m.geojson")   # NUTS 2024 matches the Destatis district list
    de = {g: s for g, s in shapes.items() if g.startswith("DE")}
    specs = {"solar_kw_pc": ([0, 0.5, 1, 1.5, 2, 3, 99], "Photovoltaik, kW je Einwohner, Ende 2025", "{:.1f}"),
             "wind_kw_pc": ([0, 0.1, 0.5, 1, 2, 4, 999], "Windkraft an Land, kW je Einwohner, Ende 2025", "{:.1f}"),
             "renew_share": ([0, 0.5, 0.7, 0.8, 0.9, 0.95, 1.01], "Anteil erneuerbarer Energien an der installierten Leistung, Ende 2025", "{:.0%}")}
    cols = ["#deebf7", "#9dc3e6", "#5b9bd5", "#2e75b6", "#1f4e79", "#002060"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 8))
    for a, (key, (bins, title, fmt)) in zip(axes, specs.items()):
        rg.choropleth(a, de, y[key].to_dict(), bins, cols, extent=rg.EXTENT_DE, lw=0.15)
        rg.legend_bins(a, bins, cols, fmt=fmt, loc="lower left")
        a.set_title(title, fontsize=10, loc="left")
    fig.suptitle("Stromerzeugung nach Kreisen", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis des Marktstammdatenregisters (Bundesnetzagentur, Datenlizenz Deutschland 2.0) und "
             "Destatis; Windkraft auf See ohne Kreiszuordnung. Kartengrundlage: © EuroGeographics (GISCO).", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "energy_maps.png", dpi=160); plt.close(fig)
    if site:
        paths, h = rg.svg_paths(de, extent=rg.EXTENT_DE, width=500, tol=600)
        years = sorted(p.jahr.unique())
        data = {"height": h, "width": 500, "paths": paths,
                "kreise": {g: {"n": r["name"], "ags": r.ags, "pop": int(r["pop"]),
                               "sol": round(r.solar_kw_pc, 2), "win": round(r.wind_kw_pc, 2), "ren": round(r.renew_share, 3),
                               "lig": round(r.lignite), "coa": round(r.coal), "gas": round(r.gas), "gro": None if pd.isna(r.sw_growth) else round(r.sw_growth, 2)}
                           for g, r in y.iterrows()},
                "germany": {"years": [int(v) for v in years],
                            **{c: [round(float(p[p.jahr == yy][c].sum()) / 1000, 2) for yy in years] for c in ["solar", "wind", "bio", "hydro", "lignite", "coal", "gas", "fossil_other", "nuclear"]}}}
        f = Path(site) / "kreise_energy.json"
        f.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{f.name}: {f.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
