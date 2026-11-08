"""Regional exposure to trade shocks in the EU (NUTS 2): a shift-share approach.

Following Autor, Dorn and Hanson (2013) and, for Germany, Dauth, Findeisen and Suedekum
(2014): a region's exposure is the employment-weighted change in its industries,
  shock_r = sum_s (L_rs / L_r) x dY_cs,
with L_rs employment in local units of industry s in region r (Eurostat structural
business statistics by NUTS 2, sbs_r_nuts2021, latest year 2021-2023 per region and
industry, NACE Rev. 2 two-digit) and dY_cs the long-run change of output of industry s
in country c in the Caliendo-Parro scenarios (central elasticities): US tariffs as of
August 2026, Chinese stop of dependent goods, Red Sea rerouting as in 2024. The business
economy only (industry, construction, market services); agriculture and the public sector
are not in the statistics. Assumes that within a country an industry's regions are hit
alike. Also: share of employment in energy-intensive industries (paper, refined
petroleum, chemicals, non-metallic minerals, basic metals; NACE C17, C19, C20, C23, C24),
a proxy for exposure to the gas price shock of 2022.
Writes <output>/regional/exposure_nuts2.csv, maps (PNG) and site data (regional_exposure.json).
Usage: python 64_regional_exposure.py [site_data_folder]
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

NACE_ICIO = {"B05": "B05", "B06": "B06", "B07": "B07", "B08": "B08", "B09": "B09",
             "C10": "C10T12", "C11": "C10T12", "C12": "C10T12", "C13": "C13T15", "C14": "C13T15", "C15": "C13T15",
             "C16": "C16", "C17": "C17_18", "C18": "C17_18", "C19": "C19", "C20": "C20", "C21": "C21", "C22": "C22",
             "C23": "C23", "C24": ["C24A", "C24B"], "C25": "C25", "C26": "C26", "C27": "C27", "C28": "C28", "C29": "C29",
             "C30": ["C301", "C302T309"], "C31": "C31T33", "C32": "C31T33", "C33": "C31T33", "D35": "D",
             "E36": "E", "E37": "E", "E38": "E", "E39": "E", "F41": "F", "F42": "F", "F43": "F",
             "G45": "G", "G46": "G", "G47": "G", "H49": "H49", "H50": "H50", "H51": "H51", "H52": "H52", "H53": "H53",
             "I55": "I", "I56": "I", "J58": "J58T60", "J59": "J58T60", "J60": "J58T60", "J61": "J61", "J62": "J62_63",
             "J63": "J62_63", "K64": "K", "K65": "K", "K66": "K", "L68": "L", **{f"M{k}": "M" for k in range(69, 76)},
             **{f"N{k}": "N" for k in range(77, 83)}, "P85": "P", "Q86": "Q", "Q87": "Q", "Q88": "Q",
             **{f"R{k}": "R" for k in range(90, 94)}, "S95": "S", "S96": "S"}
CTRY = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP", "CZ": "CZE", "DK": "DNK", "EE": "EST", "FI": "FIN",
        "FR": "FRA", "DE": "DEU", "EL": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA", "LV": "LVA", "LT": "LTU", "LU": "LUX",
        "MT": "MLT", "NL": "NLD", "PL": "POL", "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN", "ES": "ESP", "SE": "SWE",
        "NO": "NOR", "CH": "CHE", "TR": "TUR", "IS": "ISL"}
ENERGY = ["C17", "C19", "C20", "C23", "C24"]
SCEN = {"us_tariffs": ("us_tariffs_output_all.csv", "current_2026_08", "US-Zölle (Stand August 2026)"),
        "china_stop": ("china_dependency_output_all.csv", "china_dependencies", "Lieferstopp Chinas bei abhängigen Waren"),
        "red_sea": ("transport_output_all.csv", "red_sea_2024", "Umleitung um das Rote Meer wie 2024")}
# positive values: output rises where domestic producers replace dearer or missing imports


def main(site=None):
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "regional"
    out = cfg["output"] / "regional"
    out.mkdir(parents=True, exist_ok=True)
    s = rg.read_eurostat(raw / "sbs_r_nuts2021.tsv.gz")
    s = s[(s.indic_sbs == "EMP_LOC_NR") & (s.geo.str.len() == 4) & s.nace_r2.isin(NACE_ICIO) & ~s.geo.str.endswith("Z")]
    s = s.sort_values("year").groupby(["geo", "nace_r2"]).tail(1)          # latest year per region and industry
    rows = []
    for _, r in s.iterrows():
        secs = NACE_ICIO[r.nace_r2]
        secs = secs if isinstance(secs, list) else [secs]
        for sec in secs:
            rows.append({"geo": r.geo, "nace": r.nace_r2, "sector": sec, "emp": r.value / len(secs)})
    e = pd.DataFrame(rows)
    e["iso"] = e.geo.str[:2].map(CTRY)
    e = e.dropna(subset=["iso"])
    tot = e.groupby("geo").emp.sum().rename("emp_total")
    res = tot.to_frame()
    res["iso"] = res.index.str[:2].map(CTRY)
    res["energy_share"] = e[e.nace.isin(ENERGY)].groupby("geo").emp.sum().reindex(res.index).fillna(0) / res.emp_total
    res["manuf_share"] = e[e.nace.str.startswith("C")].groupby("geo").emp.sum().reindex(res.index).fillna(0) / res.emp_total
    for key, (fn, scen, _) in SCEN.items():
        o = pd.read_csv(cfg["output"] / "scenarios" / fn)
        o = o[o.scenario == scen][["country", "sector", "output_pct"]]
        m = e.merge(o, left_on=["iso", "sector"], right_on=["country", "sector"], how="left")
        m["w"] = m.emp * m.output_pct
        res[key] = m.groupby("geo").w.sum() / m.groupby("geo").emp.sum()
        res[f"{key}_jobs"] = m.groupby("geo").w.sum() / 100
    res.round(5).to_csv(out / "exposure_nuts2.csv")
    shapes, names = rg.load_nuts(raw / "nuts2_2021.geojson")
    res["name"] = [names.get(g, g) for g in res.index]
    de = res[res.iso == "DEU"]
    for key, (_, _, lab) in SCEN.items():
        print(f"{lab}: EU regions min {res[key].min():.2f} % ({res[key].idxmin()} {res.name[res[key].idxmin()]}), "
              f"Germany {de[key].min():.2f} to {de[key].max():.2f} %, worst DE {de[key].idxmin()} {de.name[de[key].idxmin()]}")
    print(f"energy-intensive employment: Germany max {de.energy_share.max():.1%} ({de.energy_share.idxmax()} "
          f"{de.name[de.energy_share.idxmax()]}), EU max {res.energy_share.max():.1%} ({res.energy_share.idxmax()})")

    # maps
    red = ["#7f0000", "#c00000", "#e06666", "#f4b183", "#fce4d6", "#deebf7", "#5b9bd5"]
    blue = ["#fce4d6", "#f2f2f2", "#deebf7", "#9dc3e6", "#5b9bd5", "#2e75b6", "#002060"]
    specs = {"us_tariffs": ([-9, -0.6, -0.45, -0.3, -0.15, 0, 0.15, 9], red, "{:.2f}"),
             "china_stop": ([-9, 0, 0.05, 0.1, 0.15, 0.2, 0.25, 9], blue, "{:.2f}"),
             "red_sea": ([-9, 0, 0.02, 0.04, 0.06, 0.08, 0.1, 9], blue, "{:.2f}"),
             "energy_share": ([0, 0.01, 0.02, 0.04, 0.06, 0.08, 1], ["#deebf7", "#9dc3e6", "#5b9bd5", "#2e75b6", "#1f4e79", "#002060"], "{:.0%}")}
    titles = {**{k: v[2] + ": Produktion, gewichtet mit der regionalen Branchenstruktur, in %" for k, v in SCEN.items()},
              "energy_share": "Anteil energieintensiver Industrien an der Beschäftigung (Papier, Raffinerien, Chemie, Glas/Keramik, Metalle)"}
    for key, (bins, cols, fmt) in specs.items():
        fig, axes = plt.subplots(1, 2, figsize=(15, 7.5), gridspec_kw={"width_ratios": [1.45, 1]})
        vals = res[key].to_dict()
        for a, ext in zip(axes, (rg.EXTENT_EU, rg.EXTENT_DE)):
            rg.choropleth(a, shapes, vals, bins, cols, extent=ext)
        rg.legend_bins(axes[0], bins, cols, fmt=fmt, title="")
        fig.suptitle(titles[key], x=0.01, ha="left", fontsize=11)
        fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis von Eurostat (sbs_r_nuts2021, NUTS 2021), Caliendo-Parro-Modell "
                 "(OECD ICIO 2022); Kartengrundlage: © EuroGeographics für die Verwaltungsgrenzen (GISCO). Grau: keine Daten.", fontsize=7)
        fig.tight_layout(rect=(0, 0.03, 1, 0.95))
        fig.savefig(out / f"map_{key}.png", dpi=170); plt.close(fig)
    if site:
        paths, h = rg.svg_paths(shapes)
        data = {"height": h, "paths": paths,
                "regions": {g: {"n": r["name"], "us": round(r.us_tariffs, 3), "cn": round(r.china_stop, 3), "rs": round(r.red_sea, 3),
                                "en": round(r.energy_share, 4), "mf": round(r.manuf_share, 4), "emp": int(r.emp_total)}
                            for g, r in res.iterrows() if pd.notna(r.us_tariffs)}}
        p = Path(site) / "regional_exposure.json"
        p.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"{p.name}: {p.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
