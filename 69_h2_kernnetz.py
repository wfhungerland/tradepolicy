"""Hydrogen core network (Wasserstoff-Kernnetz) as approved by the Federal Network Agency
on 22.10.2024: new-build and conversion pipelines by Land and by planned commissioning year.

Data: Bundesnetzagentur, approval decision, annexes 3 (new build) and 4 (conversion of
natural-gas pipelines) in the amended version ("geaendert_Anlage3/4.xlsx"). The annexes give
start and end town, length, diameter, investment and Land, but no geometry; maps by district
are therefore not possible. Segments that run through several Länder are split equally
between them (approximation); "AWZ" (offshore exclusive economic zone) is kept separately.
The BNetzA headline figure (9,040 km) also contains segments not listed in these annexes.
Writes <output>/h2/h2_kernnetz_laender.csv, h2_kernnetz_jahre.csv and h2_kernnetz.png.
"""
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import load_config

LAND = {"Baden-Württemberg": "BW", "Bayern": "BY", "Berlin": "BE", "Brandenburg": "BB", "Bremen": "HB", "Hamburg": "HH",
        "Hessen": "HE", "Mecklenburg-Vorpommern": "MV", "Niedersachsen": "NI", "Nordrhein-Westfalen": "NW",
        "Rheinland-Pfalz": "RP", "Saarland": "SL", "Sachsen": "SN", "Sachsen-Anhalt": "ST", "Schleswig-Holstein": "SH",
        "Thüringen": "TH", "AWZ D Nordsee": "AWZ", "AWZ D Ostsee": "AWZ"}


def year(v):
    if hasattr(v, "year"):
        return v.year
    m = re.findall(r"(20\d\d)", str(v))
    return int(m[-1]) if m else None


def read(path, kind):
    d = pd.read_excel(path, header=3)
    d.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in d.columns]
    d = d[d["Antrags-ID"].astype(str).str.match(r"^[A-Z]{2,4}\d")]
    km = pd.to_numeric(d["Länge (km)"], errors="coerce")
    inv = pd.to_numeric(d[[c for c in d.columns if c.startswith("Investitionskosten")][0]], errors="coerce")
    yc = [c for c in d.columns if "Inbetriebnahme" in c][0]
    rows = []
    for (_, r), k, i in zip(d.iterrows(), km, inv):
        parts = [LAND.get(p.strip()) for p in str(r["Bundesland"]).split("/")]
        parts = [p for p in parts if p] or ["unbekannt"]
        for p in parts:
            rows.append({"id": r["Antrags-ID"], "art": kind, "land": p, "km": (k or 0) / len(parts) if pd.notna(k) else 0,
                         "inv_mio": (i / len(parts)) if pd.notna(i) else 0, "jahr": year(r[yc]), "dn": r.get("Nenndurchmesser (DN)")})
    return pd.DataFrame(rows)


def main():
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "h2"
    out = cfg["output"] / "h2"
    out.mkdir(parents=True, exist_ok=True)
    d = pd.concat([read(raw / "geaendert_Anlage3.xlsx", "Neubau"), read(raw / "geaendert_Anlage4.xlsx", "Umstellung")])
    print(f"segments: {d.id.nunique()}, km {d.km.sum():,.0f} (new {d[d.art == 'Neubau'].km.sum():,.0f}, conversion {d[d.art == 'Umstellung'].km.sum():,.0f}), "
          f"investment {d.inv_mio.sum() / 1000:,.1f} bn EUR")
    land = d.pivot_table(index="land", columns="art", values="km", aggfunc="sum", fill_value=0)
    land["gesamt"] = land.sum(axis=1)
    land["inv_mio"] = d.groupby("land").inv_mio.sum()
    land = land.sort_values("gesamt", ascending=False)
    land.round(0).to_csv(out / "h2_kernnetz_laender.csv")
    print(land.round(0).to_string())
    yr = d.dropna(subset=["jahr"]).pivot_table(index="jahr", columns="art", values="km", aggfunc="sum", fill_value=0).sort_index().cumsum()
    yr.round(0).to_csv(out / "h2_kernnetz_jahre.csv")
    print("cumulative km by year:\n", yr.round(0).to_string())

    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.5))
    l = land.drop(index=[i for i in land.index if i in ("unbekannt",)])
    a.barh(l.index[::-1], l.get("Umstellung", 0)[::-1], color="#9dc3e6", label="Umstellung von Erdgasleitungen")
    a.barh(l.index[::-1], l.get("Neubau", 0)[::-1], left=l.get("Umstellung", 0)[::-1], color="#002060", label="Neubau")
    a.set_title("Länge nach Ländern, km", loc="left", fontsize=10); a.legend(frameon=False, fontsize=8, loc="lower right")
    a.spines[["top", "right"]].set_visible(False)
    b.stackplot(yr.index, yr.get("Umstellung", 0), yr.get("Neubau", 0), colors=["#9dc3e6", "#002060"], labels=["Umstellung", "Neubau"])
    b.set_title("Geplante Inbetriebnahme, kumulierte km", loc="left", fontsize=10); b.legend(frameon=False, fontsize=8, loc="upper left")
    b.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Wasserstoff-Kernnetz: genehmigte Leitungen", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis der Genehmigung der Bundesnetzagentur vom 22.10.2024 (Anlagen 3 und 4, geänderte Fassung). "
             "Länderübergreifende Abschnitte zu gleichen Teilen aufgeteilt; AWZ = ausschließliche Wirtschaftszone (See).", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(out / "h2_kernnetz.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
