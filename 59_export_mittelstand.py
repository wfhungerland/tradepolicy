"""Export the Mittelstand analysis (58_mittelstand.py) as mittelstand.json for the site.
Usage: python 59_export_mittelstand.py [target_folder]
"""
import json
import sys
from pathlib import Path

import pandas as pd

from config import load_config

NACE = {"TOTAL": ("Alle Unternehmen", "All enterprises"), "C": ("Verarbeitendes Gewerbe", "Manufacturing"),
        "G46": ("Großhandel", "Wholesale trade"), "G45": ("Kfz-Handel", "Motor vehicle trade"), "G47": ("Einzelhandel", "Retail trade"),
        "C10": ("Nahrungsmittel", "Food"), "C11": ("Getränke", "Beverages"), "C13": ("Textilien", "Textiles"),
        "C14": ("Bekleidung", "Wearing apparel"), "C15": ("Leder", "Leather"), "C16": ("Holz", "Wood"), "C17": ("Papier", "Paper"),
        "C18": ("Druck", "Printing"), "C19": ("Mineralöl", "Refined petroleum"), "C20": ("Chemie", "Chemicals"),
        "C21": ("Pharma", "Pharmaceuticals"), "C22": ("Gummi, Kunststoff", "Rubber, plastics"), "C23": ("Glas, Keramik, Steine", "Glass, ceramics, stone"),
        "C24": ("Metallerzeugung", "Basic metals"), "C25": ("Metallerzeugnisse", "Fabricated metal products"),
        "C26": ("Elektronik, Optik", "Electronics, optics"), "C27": ("Elektrische Ausrüstungen", "Electrical equipment"),
        "C28": ("Maschinenbau", "Machinery"), "C29": ("Kraftwagen, Teile", "Motor vehicles, parts"), "C30": ("Sonstiger Fahrzeugbau", "Other transport equipment"),
        "C31": ("Möbel", "Furniture"), "C32": ("Sonstige Waren", "Other manufacturing"), "C33": ("Reparatur, Installation", "Repair, installation")}
PARTNERS = ["WORLD", "INT_EU", "EXT_EU", "US", "CN_X_HK", "UK", "CH", "FR", "NL", "PL", "IT", "AT", "JP", "KR", "IN", "TR", "BR", "MX", "RU"]
ISO = {"US": "USA", "CN_X_HK": "CHN", "UK": "GBR", "CH": "CHE", "FR": "FRA", "NL": "NLD", "PL": "POL", "IT": "ITA", "AT": "AUT",
       "JP": "JPN", "KR": "KOR", "IN": "IND", "TR": "TUR", "BR": "BRA", "MX": "MEX", "RU": "RUS"}


def main(target=None):
    cfg = load_config()
    src = cfg["output"] / "mittelstand"
    out = Path(target) if target else cfg["output"] / "site_data"
    p = pd.read_csv(src / "by_partner.csv")
    p = p[p.partner.isin(PARTNERS)]
    years = sorted(int(y) for y in p.year.unique())
    part = {}
    for (geo, unit, flow, partner), g in p.groupby(["geo", "unit", "stk_flow", "partner"]):
        g = g.set_index("year").reindex(years)
        part.setdefault(f"{geo}_{flow}_{unit}", {})[partner] = {
            "share": [None if pd.isna(v) else round(float(v), 4) for v in g.sme_share],
            "total": [None if pd.isna(v) else round(float(v), 1) for v in g.total]}
    a = pd.read_csv(src / "by_activity.csv")
    ya = int(a.year.max())
    a = a[(a.year == ya) & a.nace_r2.isin(NACE)]
    act = {pt: [[r.nace_r2, round(float(r.sme_share), 4), round(float(r.total) / 1e6, 2)] for r in g.sort_values("total", ascending=False).itertuples()
                if pd.notna(r.sme_share)] for pt, g in a.groupby("partner")}
    e = pd.read_csv(src / "exposure_sectors.csv").fillna(0)
    s = pd.read_csv(src / "summary.csv")
    data = {"years": years, "activity_year": ya, "partners": PARTNERS, "iso": ISO, "nace": NACE, "by_partner": part,
            "by_activity": act, "summary": [round(float(v), 4) for v in s.Wert],
            "us_loss_bn": round(float(e.loss_bn.sum()), 1), "china_exposed_bn": round(float(e.exposed_bn.sum()), 1)}
    out.mkdir(parents=True, exist_ok=True)
    f = out / "mittelstand.json"
    f.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{f.name}: {f.stat().st_size // 1024} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
