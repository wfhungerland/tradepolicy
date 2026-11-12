"""Map for the newswolf post: US tariff loss per inhabitant by district, GRW C areas outlined.

Inputs: <output>/kreise/us_tariffs_kreise_imputed.csv (89, suppressed districts imputed and hatched),
grw_kreise.csv (80), NUTS 2024 district geometries. Writes PNG and SVG to paper/newswolf/.
Usage: python tools/newswolf_karte.py
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.patches import Patch, Polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import regional as rg
from config import load_config

BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]
INK, INK2, ACC = "#0b0b0b", "#52514e", "#eb6834"


def main():
    cfg = load_config()
    out = cfg["output"] / "kreise"
    i = pd.read_csv(out / "us_tariffs_kreise_imputed.csv", dtype={"ags": str}).set_index("ags")
    g = pd.read_csv(out / "grw_kreise.csv", dtype={"ags": str}).set_index("ags").reindex(i.index)
    i = i.dropna(subset=["nuts3"])
    shapes, _ = rg.load_nuts(cfg["data"]["scenarios"] / "regional" / "nuts3_2024_10m.geojson")
    de = {k: v for k, v in shapes.items() if k.startswith("DE")}
    bins = [0, 100, 250, 500, 1000, 2000, 1e9]
    fig, ax = plt.subplots(figsize=(8.8, 8.2))
    rg.choropleth(ax, de, i.set_index("nuts3").loss_pc.to_dict(), bins, BLUE, extent=rg.EXTENT_DE, lw=0.2)
    imp = [Polygon(r, closed=True) for n in i[i.imputed].nuts3 for r in de.get(n, [])]
    ax.add_collection(PatchCollection(imp, facecolor="none", edgecolor="white", hatch="////", lw=0))
    c = [Polygon(r, closed=True) for n in i[g.share_c.reindex(i.index) >= 0.5].nuts3 for r in de.get(n, [])]
    ax.add_collection(PatchCollection(c, facecolor="none", edgecolor=ACC, lw=1.1))
    lab = ["unter 100", "100 bis 250", "250 bis 500", "500 bis 1.000", "1.000 bis 2.000", "2.000 und mehr"]
    hand = [Patch(color=x) for x in BLUE] + [Patch(facecolor="none", edgecolor=ACC, lw=1.1), Patch(facecolor="#6da7ec", hatch="////", edgecolor="white")]
    fig.legend(handles=hand, labels=lab + ["C-Fördergebiet (GRW)", "geschätzt"], frameon=False, fontsize=7.5, loc="lower right",
              title="€ je Einwohner und Jahr", title_fontsize=8, bbox_to_anchor=(0.98, 0.07))
    fig.text(0.03, 0.965, "Die Zollverluste liegen im Süden und Westen,\ndie Fördergebiete vor allem im Osten", fontsize=12, weight="bold",
             color=INK, va="top")
    fig.text(0.03, 0.905, "US-Zölle (Stand August 2026): langfristiger Produktionsverlust der Industrie je Einwohner, 400 Kreise",
             fontsize=8, color=INK2)
    fig.text(0.03, 0.012, "Quelle: eigene Berechnungen mit Caliendo-Parro-Modell; Regionaldatenbank 42111-04-02-4 (2024), Eurostat sbs_r_nuts2021,\n"
             "BBSR Raumgliederungen 2023 (GRW-Status). Kartengrundlage: © EuroGeographics (GISCO). Schraffiert: geheime Werte, geschätzt.",
             fontsize=6.3, color=INK2)
    fig.subplots_adjust(left=0.0, right=0.76, top=0.89, bottom=0.05)
    stem = ROOT / "paper" / "newswolf" / "karte_zollverlust_kreise"
    fig.savefig(f"{stem}.svg"); fig.savefig(f"{stem}.png", dpi=250); plt.close(fig)
    print("written", stem)


if __name__ == "__main__":
    main()
