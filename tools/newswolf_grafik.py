import re, pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.drawing.image import Image as XLImage
from openpyxl.chart import BarChart, Reference

OUT = "/home/user/scen_out/kreise"; DIR = "/home/user/tradepolicy/paper/grafik/"
STEM = "(2026-11-12) Hoechste Zollverluste liegen ausserhalb der Foerdergebiete"
i = pd.read_csv(f"{OUT}/us_tariffs_kreise_imputed.csv", dtype={"ags": str}).set_index("ags")
g = pd.read_csv(f"{OUT}/grw_kreise.csv", dtype={"ags": str}).set_index("ags")
x = i.join(g[["share_c", "share_cd", "status"]]).sort_values("loss_pc", ascending=False)
med = float(x.loss_pc.median())
top = x.head(15).copy()
def short(n):
    n = re.sub(r", (Stadt|Stadtkreis|kreisfreie Stadt)$", "", n)
    return n.replace(" am Rhein", "")
top["label"] = [short(n) for n in top.name]
top["grw"] = top.status.map({"C": "C-Fördergebiet", "D": "D-Fördergebiet", "teilweise": "teilweise", "keine": "kein Fördergebiet"})

# --- chart
INK, INK2, GRID, ACC, GREY = "#0b0b0b", "#52514e", "#e4e3df", "#256abf", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig, ax = plt.subplots(figsize=(7.2, 6.0))
y = np.arange(len(top))[::-1]
for yy, r in zip(y, top.itertuples()):
    col = GREY if r.status in ("C", "D", "teilweise") else ACC
    ax.barh(yy, r.loss_pc, color=col, height=0.7, hatch="////" if r.imputed else None, edgecolor="white" if r.imputed else col, lw=0)
    ax.text(r.loss_pc + 150, yy, f"{r.loss_pc:,.0f}".replace(",", ".") + (" (geschätzt)" if r.imputed else ""), va="center", fontsize=8, color=INK)
ax.set_yticks(y, top.label, fontsize=8.5)
ax.axvline(med, color=INK2, lw=0.8, ls=(0, (3, 3)))
ax.text(med + 120, len(top) - 0.35, f"Median aller Kreise: {med:,.0f} €".replace(",", "."), fontsize=7.5, color=INK2, va="bottom")
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.set_xlim(0, 16500)
ax.set_xticks(range(0, 16001, 4000), [f"{v:,}".replace(",", ".") for v in range(0, 16001, 4000)], fontsize=8, color=INK2)
oder = list(top.label).index("Oder-Spree")
ax.annotate("einziger Kreis im C-Fördergebiet", (top.loss_pc.iloc[oder] + 1500, y[oder]), xytext=(6200, y[oder] + 1.4),
            fontsize=7.5, color=GREY, arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))
fig.text(0.02, 0.965, "14 der 15 am stärksten getroffenen Kreise liegen in keinem Fördergebiet", fontsize=11.5, weight="bold", color=INK)
fig.text(0.02, 0.93, "US-Zölle (Stand August 2026): langfristiger Produktionsverlust der Industrie, € je Einwohner und Jahr",
         fontsize=8.5, color=INK2)
fig.text(0.02, 0.015, "Quelle: eigene Berechnungen mit Caliendo-Parro-Modell; Regionaldatenbank 42111-04-02-4 (2024),\nEurostat sbs_r_nuts2021, "
         "BBSR Raumgliederungen 2023 (GRW-Status).\nSchraffiert: Werte geheim gehalten, aus Summen der Regierungsbezirke geschätzt.",
         fontsize=6.8, color=INK2)
fig.subplots_adjust(left=0.2, right=0.97, top=0.9, bottom=0.13)
fig.savefig(DIR + STEM + ".svg"); fig.savefig(DIR + STEM + ".png", dpi=300); plt.close(fig)

# --- workbook
F = lambda **k: Font(name="Arial", **k)
wb = Workbook(); info = wb.active; info.title = "Info"
src = [("S1", "Statistische Ämter des Bundes und der Länder, Regionaldatenbank Deutschland, Tabelle 42111-04-02-4 (Umsatz und Auslandsumsatz, Betriebe ab 20 Beschäftigte), Stand 2024",
        "https://www.regionalstatistik.de/genesis/online?operation=table&code=42111-04-02-4"),
       ("S2", "Eurostat, sbs_r_nuts2021 (Beschäftigte nach NACE-Abteilung und NUTS-2-Region)", "https://ec.europa.eu/eurostat/databrowser/view/sbs_r_nuts2021/default/table"),
       ("S3", "CEPII, US applied tariffs 2025-26 (Guimbard 2026), Datei usa_tariffs_20260907", "https://www.cepii.fr/DATA_DOWNLOAD/usa_tariffs/usa_tariffs_20260907.zip"),
       ("S4", "OECD, Inter-Country Input-Output Tables, Ausgabe 2025", "https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html"),
       ("S5", "BBSR, INKAR 2025 mit Raumgliederungen Referenz 2023 (GRW-Status je Gemeinde)", "https://www.inkar.de/"),
       ("S6", "Destatis, Kreisfreie Städte und Landkreise nach Fläche, Bevölkerung (31.12.2024)",
        "https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/Administrativ/04-kreise.html")]
rows = [("14 der 15 am stärksten getroffenen Kreise liegen in keinem Fördergebiet", True),
        ("Botschaft: Die höchsten Produktionsverluste je Einwohner durch die US-Zölle liegen in Industriekreisen, die keine GRW-Regionalförderung erhalten.", False),
        ("", False),
        ("Abdeckung: Deutschland, 15 Kreise mit dem höchsten Verlust je Einwohner (von 400) | Einheit: € je Einwohner und Jahr, langfristiger Modellwert | Stand: 11.2026", False),
        ("Definitionen: Verlust = Rückgang der Industrieproduktion (Betriebe ab 20 Beschäftigte) im Caliendo-Parro-Modell, über Branchenmix der NUTS-2-Region und Exportquote des Kreises auf Kreise verteilt.", False),
        ("GRW-Status: Anteil der Bevölkerung in C- bzw. D-Fördergebieten der Gemeinschaftsaufgabe Regionale Wirtschaftsstruktur 2022-2027; Status nach Mehrheit der Bevölkerung.", False),
        ("Flag e: Werte geheim gehalten, aus Summen des Regierungsbezirks geschätzt (Skript 89_kreise_impute.py).", False),
        ("", False), ("Quellen", True)]
for r, (t, b) in enumerate(rows, 1):
    info.cell(r, 1, t).font = F(bold=b, size=12 if r == 1 else 10)
for k, (sid, txt, url) in enumerate(src, len(rows) + 1):
    c = info.cell(k, 1, f"[{sid}] {txt}, abgerufen 12.11.2026")
    c.hyperlink = url; c.font = F(color="0000FF", underline="single", size=10)
info.column_dimensions["A"].width = 150
img = XLImage(DIR + STEM + ".png"); img.width, img.height = 720, 600
info.add_image(img, f"A{len(rows) + len(src) + 3}")

d = wb.create_sheet("Data")
head = ["Rang", "Kreis", "AGS", "Produktionsverlust (Mio. €)", "Bevölkerung (Personen)", "Verlust je Einwohner (€)", "Bevölkerung im C-Gebiet (Anteil)",
        "Bevölkerung im C- oder D-Gebiet (Anteil)", "GRW-Status", "Source", "Flag"]
for j, h in enumerate(head, 1):
    d.cell(1, j, h).font = F(bold=True)
for r, (ags, t) in enumerate(top.iterrows(), 2):
    vals = [r - 1, t.label, ags, round(float(t.loss_mio), 2), int(t["pop"]), f"=D{r}*1000000/E{r}", float(t.share_c), float(t.share_cd), t.grw,
            "S1, S2, S3, S4, S5, S6", "e" if t.imputed else ""]
    for j, v in enumerate(vals, 1):
        c = d.cell(r, j, v); c.font = F(color="0000FF") if j in (4, 5, 7, 8) else F()
    d.cell(r, 4).number_format = "#,##0.0"; d.cell(r, 5).number_format = "#,##0"; d.cell(r, 6).number_format = "#,##0"
    d.cell(r, 7).number_format = "0%"; d.cell(r, 8).number_format = "0%"
n = len(top) + 1
d.cell(n + 2, 1, "Median aller 400 Kreise (€ je Einwohner, inkl. geschätzter Werte)").font = F()
d.cell(n + 2, 6, round(med, 1)).font = F(color="0000FF"); d.cell(n + 2, 6).number_format = "#,##0"
d.cell(n + 3, 1, "Blaue Werte: aus den Quellen berechnete Eingaben (Skripte 74, 80, 89 im Repo wfhungerland/tradepolicy); schwarze Werte: Formeln.").font = F(italic=True, size=9)
for col, w in zip("ABCDEFGHIJK", (6, 22, 8, 16, 16, 16, 16, 20, 18, 22, 6)):
    d.column_dimensions[col].width = w
ch = BarChart(); ch.type = "bar"; ch.style = 10; ch.title = "Verlust je Einwohner (€)"
ch.add_data(Reference(d, min_col=6, min_row=1, max_row=n), titles_from_data=True)
ch.set_categories(Reference(d, min_col=2, min_row=2, max_row=n)); ch.y_axis.title = "€ je Einwohner"
ch.x_axis.scaling.orientation = "maxMin"; ch.legend = None; ch.height, ch.width = 10, 18
d.add_chart(ch, "M2")
wb.save(DIR + STEM + ".xlsx")
print("ok", med)
