"""Export strand 3 scenario results as one JSON file for the public site.

Reads <output>/scenarios/us_tariffs_results.csv, us_tariffs_germany_sectors.csv,
eu_results.csv, eu_germany_sectors.csv (scripts 34 and 36) and writes
scenarios.json into the site data folder (default <output>/site_data).
Central case: ProTEE elasticities capped at 15; the range spans all elasticity
variants (capped and uncapped ProTEE, uniform 4 and 8).
Usage: python 37_export_scenarios.py [target_folder]
"""
import json
import sys
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from config import load_config

SECTOR_DE = {
    "A01": "Landwirtschaft", "A02": "Forstwirtschaft", "A03": "Fischerei", "B05": "Kohlebergbau",
    "B06": "Erdöl- und Erdgasförderung", "B07": "Erzbergbau", "B08": "Steine und Erden",
    "B09": "Dienstleistungen für den Bergbau", "C10T12": "Nahrungsmittel, Getränke, Tabak",
    "C13T15": "Textilien, Bekleidung, Leder", "C16": "Holzwaren", "C17_18": "Papier und Druck",
    "C19": "Kokerei und Mineralölverarbeitung", "C20": "Chemische Erzeugnisse", "C21": "Pharmazeutische Erzeugnisse",
    "C22": "Gummi- und Kunststoffwaren", "C23": "Glas, Keramik, Steine und Erden", "C24A": "Eisen und Stahl",
    "C24B": "NE-Metalle", "C25": "Metallerzeugnisse", "C26": "Elektronik und Optik",
    "C27": "Elektrische Ausrüstungen", "C28": "Maschinenbau", "C29": "Kraftwagen und Kraftwagenteile",
    "C301": "Schiffbau", "C302T309": "Sonstiger Fahrzeugbau (u. a. Luftfahrt)", "C31T33": "Möbel und sonstige Waren",
    "D": "Energieversorgung", "E": "Wasser, Entsorgung", "F": "Bau", "G": "Handel", "H49": "Landverkehr",
    "H50": "Schifffahrt", "H51": "Luftfahrt", "H52": "Lagerei", "H53": "Post- und Kurierdienste",
    "I": "Gastgewerbe", "J58T60": "Verlage, Rundfunk", "J61": "Telekommunikation",
    "J62_63": "IT-Dienstleistungen", "K": "Finanzdienstleistungen", "L": "Grundstücks- und Wohnungswesen",
    "M": "Freiberufliche und technische Dienstleistungen", "N": "Sonstige Unternehmensdienstleistungen",
    "O": "Öffentliche Verwaltung", "P": "Erziehung und Unterricht", "Q": "Gesundheit und Soziales",
    "R": "Kunst und Erholung", "S": "Sonstige Dienstleistungen", "T": "Private Haushalte",
}

SCENARIOS = [
    {"id": "peak_2025_04", "group": "us", "title": "US-Zölle auf dem Höhepunkt (10. April 2025)",
     "shock": "US-Zölle wie am 10. April 2025: Zollkrieg mit China (Aufschlag 125 Prozentpunkte), für die übrigen Länder 10 % Mindestzoll während der 90-tägigen Pause sowie Zölle auf Stahl, Aluminium und Autos.",
     "partner": "USA"},
    {"id": "deal_2025_09", "group": "us", "title": "US-Zölle nach den Abkommen (5. September 2025)",
     "shock": "US-Zölle wie am 5. September 2025: Rahmenabkommen mit EU, Japan und Korea (für die EU höchstens 15 % auf die meisten Waren), hohe Aufschläge auf Indien und Brasilien, China nach der Einigung von Genf.",
     "partner": "USA"},
    {"id": "current_2026_08", "group": "us", "title": "US-Zölle aktuell (22. August 2026)",
     "shock": "US-Zölle wie am 22. August 2026: nach dem Urteil des Supreme Court gegen die IEEPA-Zölle (Februar 2026) vor allem Zölle nach Section 232 (Stahl, Aluminium, Kupfer, Autos, Lkw, Halbleiter, Pharma) und Section 301 sowie Aufschläge auf Kanada.",
     "partner": "USA"},
    {"id": "no_single_market", "group": "eu", "title": "Ohne EU-Binnenmarkt",
     "shock": "EU-Mitglieder handeln untereinander wie mit Drittstaaten: Der Binnenmarkteffekt im Warenhandel (Gravitationskoeffizient 1,1 nach Head und Mayer 2021) und im Dienstleistungshandel (0,18 nach Mayer, Vicard und Zignago 2019) entfällt.",
     "partner": "EU"},
    {"id": "trend_2030", "group": "eu", "title": "Binnenmarkt vertieft sich weiter bis 2030",
     "shock": "Die Handelskosten im EU-Warenhandel sinken zehn weitere Jahre im Tempo von 2000 bis 2019, geschätzt mit Daten zum Inlandsabsatz (ITPD-E) nach der Methode von Head und Mayer (2021).",
     "partner": "EU"},
    {"id": "services_deeper", "group": "eu", "title": "Dienstleistungsbinnenmarkt so tief wie bei Waren",
     "shock": "Der Binnenmarkteffekt im Dienstleistungshandel steigt auf das Niveau des Warenhandels in einer vergleichbaren Stichprobe (Koeffizient +0,14 nach Mayer, Vicard und Zignago 2019).",
     "partner": "EU"},
]

CHECKS = [
    {"name": "Nachrechnung eines Lehrbuchbeispiels", "result": "bestanden",
     "text": "Das NAFTA-Beispiel aus Yotov, Piermartini, Monteiro und Larch (2016) wird reproduziert: gleicher RTA-Koeffizient (0,557), Exporteffekte bis auf höchstens 0,75 Prozentpunkte."},
    {"name": "Modellmechanik", "result": "bestanden",
     "text": "Ohne Schock gibt das Modell die Ausgangslage exakt wieder; mit einem Sektor ohne Vorleistungen fällt es mit dem Ein-Sektor-Zollmodell zusammen; die Wohlfahrtsformel von Arkolakis, Costinot und Rodríguez-Clare (2012) gilt im Ein-Sektor-Fall."},
    {"name": "US-Importe aus China", "result": "plausibel",
     "text": "Modell: -24 % bei den aktuellen Zöllen. Beobachtet 2025: rund -30 % (US Census, laut PIIE und Presseberichten). Das Modell beschreibt die langfristige Anpassung, 2025 galten wechselnde Zölle."},
    {"name": "US-Zolleinnahmen", "result": "plausibel",
     "text": "Modell: 183 bis 280 Mrd. USD im Jahr, je nach Elastizität. Beobachtet: 195 Mrd. USD im Haushaltsjahr 2025 (CRFB nach Monthly Treasury Statement), als die Zölle erst teilweise galten."},
    {"name": "Wohlfahrt der USA", "result": "Abweichung",
     "text": "Ignatenko, Lashkaripour, Macedoni und Simonovska (2025, JIE) finden ohne Vergeltung einen kleinen Gewinn der USA. Hier entsteht ein Gewinn nur bei niedrigen Elastizitäten; im zentralen Fall verlieren die USA 0,1 bis 0,5 %."},
    {"name": "EU-Handelskosten seit 2000", "result": "bestanden",
     "text": "Eigene Schätzung: Die Handelskosten im EU-Binnenhandel mit Industriewaren sinken 2000 bis 2019 um 11,6 Punkte, die von Drittstaaten in die EU ebenfalls. Head und Mayer (2021, Abbildung 1) zeigen für 2000 bis 2018 einen ähnlichen Rückgang und ebenfalls keine Abschottung nach außen."},
    {"name": "Anstieg der EU-Exporte in die USA im September-Szenario", "result": "erklärt",
     "text": "Die EU-Exporte in die USA steigen um 1,4 %, obwohl die deutschen fallen. Ursache ist Handelsumlenkung: Fast zollfreie EU-Waren (Pharma, Mineralöl, Flugzeuge) und Dienstleistungen ersetzen hoch verzollte Importe aus China und Indien."},
]


def iso2_map(cfg):
    path = cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip"
    with zipfile.ZipFile(path) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))),
                         dtype=str, keep_default_na=False)
    m = dict(zip(cc.country_iso3, cc.country_iso2))
    m.update({"TWN": "TW", "ROW": ""})
    return m


def rnd(v, k=3):
    return None if v is None or not np.isfinite(v) else round(float(v), k)


def main(target=None):
    cfg = load_config()
    src = cfg["output"] / "scenarios"
    out = cfg["output"] / "site_data" if target is None else Path(target)
    out.mkdir(parents=True, exist_ok=True)
    us = pd.read_csv(src / "us_tariffs_results.csv")
    eu = pd.read_csv(src / "eu_results.csv")
    res = pd.concat([us.rename(columns={"exports_to_us_pct": "partner_pct"}),
                     eu.rename(columns={"exports_to_eu_pct": "partner_pct"})], ignore_index=True)
    sec = pd.concat([pd.read_csv(src / "us_tariffs_germany_sectors.csv").rename(
                         columns={"exports_to_us_pct": "partner_pct", "exports_to_us_2022_bn": "partner_2022_bn"}),
                     pd.read_csv(src / "eu_germany_sectors.csv").rename(
                         columns={"exports_to_eu_pct": "partner_pct", "exports_to_eu_2022_bn": "partner_2022_bn"})],
                    ignore_index=True)
    iso2 = iso2_map(cfg)

    scen_out = []
    for s in SCENARIOS:
        r = res[res.scenario == s["id"]]
        c = r[r.elasticity == "protee"].set_index("country")
        rng = r.groupby("country")["welfare_pct"].agg(["min", "max"])
        countries = {}
        for iso, row in c.iterrows():
            countries[iso] = [rnd(row.welfare_pct), rnd(rng.loc[iso, "min"]), rnd(rng.loc[iso, "max"]),
                              rnd(row.exports_pct, 2), rnd(row.partner_pct, 2), rnd(row.output_pct),
                              rnd(row.get("us_tariff_avg_pct", np.nan), 2)]
        q = sec[(sec.scenario == s["id"])]
        sectors = [[row.sector, rnd(row.output_pct, 2), rnd(row.partner_pct, 2),
                    rnd(row.get("us_tariff_pct", np.nan), 2), rnd(row.partner_2022_bn, 2), rnd(row.output_2022_bn, 1)]
                   for _, row in q.iterrows()]
        scen_out.append({**s, "countries": countries, "sectors_deu": sectors})

    data = {"built": date.today().isoformat(),
            "columns": ["welfare_pct", "welfare_min", "welfare_max", "exports_pct", "partner_pct", "output_pct", "us_tariff_pct"],
            "sector_columns": ["sector", "output_pct", "partner_pct", "us_tariff_pct", "partner_exports_2022_bn", "output_2022_bn"],
            "sector_names": SECTOR_DE, "iso2": {k: iso2.get(k, "") for k in res.country.unique() if k != "EU27"},
            "scenarios": scen_out, "checks": CHECKS}
    (out / "scenarios.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(scen_out)} scenarios -> {out / 'scenarios.json'} ({(out / 'scenarios.json').stat().st_size / 1e3:.0f} kB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
