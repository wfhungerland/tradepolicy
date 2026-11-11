"""District profile ("Kreis-Steckbrief") for the site: all district indicators of the
project in one file, with German median and rank.

Merges the outputs of 66 (energy), 67 (broadband), 68 (OSM infrastructure), 73 (export ratio),
74 (US tariffs), 79 (INKAR analyses), 80 (GRW) and selected INKAR 2025 indicators.
Rank 1 = highest value. Writes site data kreise_steckbrief.json (keyed by NUTS 3).
Usage: python 81_kreis_steckbrief.py site_data_folder
"""
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config

ink = importlib.import_module("79_inkar_analyses")
LAND = {"01": "Schleswig-Holstein", "02": "Hamburg", "03": "Niedersachsen", "04": "Bremen", "05": "Nordrhein-Westfalen", "06": "Hessen",
        "07": "Rheinland-Pfalz", "08": "Baden-Württemberg", "09": "Bayern", "10": "Saarland", "11": "Berlin", "12": "Brandenburg",
        "13": "Mecklenburg-Vorpommern", "14": "Sachsen", "15": "Sachsen-Anhalt", "16": "Thüringen"}
# key: (group, label de, label en, unit, decimals)
IND = {
    "pop": ("struktur", "Einwohner", "Inhabitants", "", 0),
    "bip_pc": ("struktur", "BIP je Einwohner 2022", "GDP per head 2022", " Tsd. EUR", 1),
    "inc": ("struktur", "Medianeinkommen Vollzeit 2023", "Median full-time earnings 2023", " EUR", 0),
    "alq": ("struktur", "Arbeitslosenquote 2023", "Unemployment rate 2023", " %", 1),
    "age": ("struktur", "Durchschnittsalter 2023", "Mean age 2023", " Jahre", 1),
    "prog": ("struktur", "Bevölkerung 2022 bis 2045 (Prognose)", "Population 2022 to 2045 (projection)", " %", 1),
    "iq23": ("industrie", "Industriebeschäftigte je 100 Einwohner von 15 bis 64", "Industry employees per 100 inhabitants 15-64", "", 1),
    "exq": ("industrie", "Exportquote der Industrie 2024", "Manufacturing export ratio 2024", " %", 1),
    "ausl_pc": ("industrie", "Auslandsumsatz der Industrie je Einwohner 2024", "Foreign sales of manufacturing per head 2024", " EUR", 0),
    "dm": ("zoelle", "US-Zölle: Produktion der Industrie", "US tariffs: manufacturing output", " %", 2),
    "loss_pc": ("zoelle", "US-Zölle: Produktionsverlust je Einwohner", "US tariffs: output loss per head", " EUR", 0),
    "loss_mio": ("zoelle", "US-Zölle: Produktionsverlust insgesamt", "US tariffs: total output loss", " Mio. EUR", 0),
    "gwst": ("finanzen", "Gewerbesteuer je Einwohner 2023", "Local business tax per head 2023", " EUR", 0),
    "gwst_share": ("finanzen", "Gewerbesteuer im Verhältnis zur Steuerkraft", "Business tax relative to tax capacity", " %", 1),
    "schulden": ("finanzen", "Kommunale Schulden je Einwohner 2023", "Municipal debt per head 2023", " EUR", 0),
    "sgb2": ("finanzen", "SGB-II-Quote 2023", "SGB II rate 2023", " %", 1),
    "grw_c": ("finanzen", "Bevölkerung in GRW-C-Fördergebieten", "Population in GRW C aid areas", " %", 0),
    "solar_kw_pc": ("energie", "Photovoltaik je Einwohner, Ende 2025", "Solar PV per head, end-2025", " kW", 2),
    "wind_kw_pc": ("energie", "Windkraft an Land je Einwohner, Ende 2025", "Onshore wind per head, end-2025", " kW", 2),
    "renew_share": ("energie", "Anteil Erneuerbarer an der Leistung", "Renewable share of capacity", " %", 0),
    "lignite": ("energie", "Braunkohlekraftwerke", "Lignite power plants", " MW", 0),
    "ehv_km": ("netze", "Höchstspannungsleitungen je 100 km²", "Extra-high-voltage lines per 100 km²", " km", 1),
    "rail_el": ("netze", "Elektrifizierter Anteil der Bahnstrecken", "Electrified share of railways", " %", 0),
    "bab_km": ("netze", "Autobahnen je 100 km²", "Motorways per 100 km²", " km", 1),
    "hh_gigabit": ("netze", "Haushalte mit Gigabit, Juni 2026", "Households with gigabit, June 2026", " %", 0),
    "gw_ftth": ("netze", "Gewerbegebiete mit Glasfaser, Juni 2026", "Industrial estates with fibre, June 2026", " %", 0),
    "rail_4g": ("netze", "4G entlang der Schiene, bester Betreiber", "4G along railways, best operator", " %", 0),
    "t_air": ("netze", "Fahrzeit zum nächsten Flughafen", "Travel time to nearest airport", " min", 0),
    "afd25": ("gesellschaft", "Zweitstimmen AfD 2025", "AfD party-list vote 2025", " %", 1),
    "ausl": ("gesellschaft", "Ausländeranteil 2023", "Foreigners' share 2023", " %", 1),
    "kinder": ("gesellschaft", "Kinderarmut 2023", "Child poverty 2023", " %", 1),
}


def main(site):
    cfg = load_config()
    o = cfg["output"] / "kreise"
    rd = lambda f, key="ags": pd.read_csv(o / f, dtype={key: str, "ags": str, "kreis": str})
    ex = rd("export_kreise.csv").set_index("ags")
    df = pd.DataFrame(index=ex.index)
    df["name"], df["nuts3"], df["pop"] = ex.name, ex.nuts3, ex["pop"]
    df["exq"], df["ausl_pc"] = 100 * ex.quote_2024, ex.ausl_pc
    u = rd("us_tariffs_kreise.csv").set_index("ags")
    df["dm"], df["loss_pc"], df["loss_mio"] = u.dm, u.loss_pc, u.loss_mio
    m = rd("inkar_analyses_kreise.csv").set_index("ags")
    for c in ("alq", "prog", "iq23", "gwst", "gwst_share", "schulden", "sgb2", "t_air", "afd25", "ausl", "kinder", "age"):
        df[c] = m[c]
    d = ink.load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    df["bip_pc"] = ink.get(d, "Bruttoinlandsprodukt je Einwohner")
    df["inc"] = ink.get(d, "Medianeinkommen")
    g = rd("grw_kreise.csv").set_index("ags")
    df["grw_c"] = 100 * g.share_c
    e = rd("energy_kreise.csv")
    e = e[e.jahr == 2025].set_index("kreis")
    df["solar_kw_pc"], df["wind_kw_pc"], df["renew_share"], df["lignite"] = e.solar_kw_pc, e.wind_kw_pc, 100 * e.renew_share, e.lignite
    n = rd("netze_kreise.csv").set_index("ags")
    for c in ("hh_gigabit", "gw_ftth", "rail_4g"):
        df[c] = n[c]
    inf = pd.read_csv(o / "infra_kreise.csv", index_col=0)
    inf = inf.reindex(df.nuts3.values)
    for c in ("ehv_km", "rail_el", "bab_km"):
        df[c] = inf[c].values
    df["land"] = df.index.str[:2].map(LAND)
    df = df.dropna(subset=["nuts3"])
    med = {k: (None if df[k].dropna().empty else float(df[k].median())) for k in IND}
    out = {"indicators": {k: {"g": v[0], "de": v[1], "en": v[2], "u": v[3], "d": v[4], "med": med[k], "n": int(df[k].notna().sum())} for k, v in IND.items()},
           "kreise": {}}
    rank = {k: df[k].rank(ascending=False, method="min") for k in IND}
    for k in ("lignite", "grw_c"):                      # many zeros: a rank among equal zeros says nothing
        rank[k] = rank[k].where(df[k] > 0)
    for ags, r in df.iterrows():
        out["kreise"][r.nuts3] = {"n": r["name"], "ags": ags, "land": r.land,
                                  "v": {k: (None if pd.isna(r[k]) else round(float(r[k]), 3)) for k in IND},
                                  "r": {k: (None if pd.isna(rank[k][ags]) else int(rank[k][ags])) for k in IND}}
    p = Path(site) / "kreise_steckbrief.json"
    p.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(out["kreise"]), "districts;", p.name, p.stat().st_size // 1024, "kB")
    print({k: out["indicators"][k]["n"] for k in IND})


if __name__ == "__main__":
    main(sys.argv[1])
