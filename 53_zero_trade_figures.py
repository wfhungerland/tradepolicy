"""Figures for the zero-trade matrices (52_zero_trade.py).

Matrices: rows = exporters (export view), importers (import view) or reporters (two-way
view), columns = partners; countries ordered by their number of trade partners at country
level (most connected first), the same order on both axes. Cell colours: white = no trade
in the period; for the median view black/white at country level (trade in at least half
of the years), grey shares at HS levels; for the mean view grey = share of years (country
level) or average share of codes traded (HS levels). Any positive value gets at least a
light grey so that white always means zero.
Germany: stacked bars per year, shares of all partners (country level) or all partner x
code cells (HS levels): two-way, export only, import only, none.
Writes <output>/zero_trade/zero_trade_matrices.pdf, PNGs per page, germany.pdf/png and
zero_trade.xlsx. Usage: python 53_zero_trade_figures.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from config import load_config

LEVELS = [("country", "Länder (IMF)"), ("section", "HS-Abschnitte (21)"), ("hs2", "HS2 (Kapitel)"),
          ("hs4", "HS4 (Positionen)"), ("hs6", "HS6 (Unterpositionen)")]
PERIODS = [(None, "alle Jahre"), (2001, "seit 2001\nChina in der WTO"), (2004, "seit 2004\nEU-Osterweiterung"),
           (2008, "seit 2008\nFinanzkrise"), (2020, "seit 2020\nPandemie")]
VIEWS = [("x", "Exporte (Zeile exportiert an Spalte)"), ("m", "Importe (Zeile importiert von Spalte)"),
         ("two", "beidseitig (Handel in beide Richtungen, je Code)")]
FLOOR = 0.12
COLORS = {"two_way": "#002060", "export_only": "#5b9bd5", "import_only": "#a6a6a6", "none": "#f2f2f2"}
NAMES = {"two_way": "beidseitig", "export_only": "nur Export", "import_only": "nur Import", "none": "kein Handel"}
SOURCE = {"country": "IMF IMTS (Spiegeldaten)", "default": "CEPII BACI HS92 V202601"}


def load(path):
    z = np.load(path)
    return z["years"], list(z["countries"]), z["x"], z["two"]


def shade(v, gamma=1.0):
    """0 -> white (1.0), (0, 1] -> grey from light (1 - FLOOR) to black; gamma < 1
    spreads small shares (HS levels, where most pairs trade few codes)."""
    g = np.where(v > 0, 1 - (FLOOR + (1 - FLOOR) * np.clip(v, 0, 1) ** gamma), 1.0)
    return np.dstack([g, g, g])


def summary(years, cube, start, stat, binary):
    sel = cube[years >= start] if start else cube
    if stat == "mean":
        return sel.mean(axis=0)
    if binary:
        return (sel.mean(axis=0) >= 0.5).astype(float)
    return np.median(sel, axis=0)


def main():
    cfg = load_config()
    out = cfg["output"] / "zero_trade"
    # order: breadth of trade at HS6 (codes x partners, exports plus imports, mean over
    # years); countries not in BACI follow by their number of IMF partners
    _, cb, x6, _ = load(out / "matrices_hs6.npz")
    m6 = x6.mean(axis=0)
    breadth = dict(zip(cb, m6.sum(axis=0) + m6.sum(axis=1)))
    _, cc, xc, _ = load(out / "matrices_country.npz")
    mc = xc.mean(axis=0)
    deg = dict(zip(cc, mc.sum(axis=0) + mc.sum(axis=1)))
    rank_baci = {c: r for r, c in enumerate(sorted(cb, key=lambda c: -breadth[c]))}
    rank_imf = {c: r for r, c in enumerate(sorted(cc, key=lambda c: (-breadth.get(c, -1), -deg[c])))}
    pdf = PdfPages(out / "zero_trade_matrices.pdf")
    xl = {}
    for lv, title in LEVELS:
        years, countries, x, two = load(out / f"matrices_{lv}.npz")
        rank = rank_imf if lv == "country" else rank_baci
        order = np.argsort([rank[c] for c in countries])
        ordered = np.array(countries)[order]
        first = years[0]
        periods = [(s, (f"seit {first}\nWiedervereinigung" if (s is None and first == 1990) else
                        f"seit {first}\n(alle Jahre)" if s is None else lab)) for s, lab in PERIODS]
        binary = lv == "country"
        for vw, vtitle in VIEWS:
            cube = {"x": x, "m": np.transpose(x, (0, 2, 1)), "two": two}[vw][:, order][:, :, order]
            fig, axes = plt.subplots(2, 5, figsize=(16.5, 7.6))
            for r, stat in enumerate(("median", "mean")):
                for c, (start, plab) in enumerate(periods):
                    a = axes[r, c]
                    v = summary(years, cube, start, stat, binary)
                    np.fill_diagonal(v, 0)
                    a.imshow(shade(v, 1.0 if binary else 0.5), interpolation="nearest")
                    a.set_xticks([]); a.set_yticks([])
                    for k, s in enumerate(ordered):
                        if s == "DEU":
                            a.plot([-6, -1], [k, k], color="#c00000", lw=1.2, clip_on=False)
                            a.plot([k, k], [-6, -1], color="#c00000", lw=1.2, clip_on=False)
                    if r == 0:
                        a.set_title(plab, fontsize=9)
                    if c == 0:
                        a.set_ylabel("Median" if stat == "median" else "Mittelwert", fontsize=10)
                    filled = (v > 0).sum() / (len(v) * (len(v) - 1))
                    a.text(0.0, -0.03, f"{filled:.0%} der Paare > 0", transform=a.transAxes, fontsize=7, va="top")
                    if lv == "country" or (start is None and stat == "mean"):
                        xl[f"{lv}_{vw}_{stat}_{start or first}"] = pd.DataFrame(v, index=ordered, columns=ordered)
            fig.suptitle(f"Null-Handel-Matrix: {title}, {vtitle}, {years[0]}-{years[-1]}", fontsize=12, x=0.01, ha="left")
            note = ("Schwarz: Handel in mindestens der Hälfte der Jahre (Median) bzw. Anteil der Jahre mit Handel (Mittelwert); "
                    "weiß: kein Handel." if binary else
                    "Grauwert: Anteil der Codes der Ebene, die gehandelt werden (schwarz = alle, Wurzelskala, siehe Legende); weiß: kein Handel.")
            fig.text(0.01, 0.01, note + " Länder nach Breite des Handels sortiert (Partner mal HS6-Codes, Exporte plus Importe), gleiche Reihenfolge auf beiden Achsen; "
                     "rote Marke: Deutschland. Jeder positive Wert mindestens hellgrau. Quelle: eigene Berechnungen auf Basis von "
                     + SOURCE.get(lv, SOURCE["default"]) + f", {len(countries)} Länder.", fontsize=7, wrap=True)
            fig.subplots_adjust(left=0.03, right=0.95, top=0.88, bottom=0.07, wspace=0.08, hspace=0.18)
            cax = fig.add_axes([0.962, 0.25, 0.008, 0.5])
            vals = np.linspace(0, 1, 201)
            cax.imshow(shade(vals[::-1, None], 1.0 if binary else 0.5), aspect="auto", extent=(0, 1, 0, 1))
            cax.set_xticks([]); cax.yaxis.tick_right()
            cax.set_yticks([0, 0.25, 0.5, 0.75, 1])
            cax.set_yticklabels(["0", "25 %", "50 %", "75 %", "100 %"], fontsize=7)
            pdf.savefig(fig)
            fig.savefig(out / f"matrix_{lv}_{vw}.png", dpi=200)
            plt.close(fig)
            print(lv, vw)
    pdf.close()

    # Germany: stacked bars
    fig, axes = plt.subplots(len(LEVELS), 1, figsize=(10, 2.4 * len(LEVELS)), sharex=True)
    for a, (lv, title) in zip(axes, LEVELS):
        g = pd.read_csv(out / f"germany_{lv}.csv")
        xl[f"Deutschland_{lv}"] = g
        bottom = np.zeros(len(g))
        for k in ("two_way", "export_only", "import_only", "none"):
            a.bar(g.year, g[k] * 100, bottom=bottom, color=COLORS[k], label=NAMES[k], width=0.8,
                  edgecolor="#bfbfbf" if k == "none" else None, linewidth=0.3)
            bottom += g[k].to_numpy() * 100
        a.set_ylim(0, 100); a.set_ylabel("%"); a.set_title(title, loc="left", fontsize=10)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    axes[0].legend(ncol=4, loc="lower left", bbox_to_anchor=(0, 1.15), frameon=False, fontsize=9)
    fig.suptitle("Deutschland: Handel mit allen Partnern bzw. Partner-Code-Paaren, in %", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.005, "Länderebene: Anteil der Partnerländer (IMF IMTS, ab 1990). HS-Ebenen: Anteil aller Kombinationen aus "
             "Partnerland und Code (CEPII BACI HS92, ab 1995). Beidseitig: Deutschland exportiert und importiert denselben Code "
             "mit demselben Partner.", fontsize=7, wrap=True)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.savefig(out / "germany.pdf"); fig.savefig(out / "germany.png", dpi=200)
    plt.close(fig)
    with pd.ExcelWriter(out / "zero_trade.xlsx") as w:
        pd.DataFrame({"Hinweis": [
            "Null-Handel-Matrizen nach Helpman, Melitz und Rubinstein (2008), eigene Berechnungen.",
            "Blätter Deutschland_*: Anteile je Jahr. Übrige Blätter: Matrizen, Zeilen = Exporteur (x), Importeur (m) oder "
            "Berichtsland (two), Spalten = Partner; Länderebene alle Zeiträume, HS-Ebenen Mittelwert über alle Jahre.",
            "Quellen: IMF IMTS (Länderebene), CEPII BACI HS92 V202601 (HS-Ebenen, Etalab-Lizenz 2.0)."]}).to_excel(
            w, sheet_name="Info", index=False)
        for k, d in xl.items():
            d.round(4).to_excel(w, sheet_name=k[:31], index=not k.startswith("Deutschland"))
    print("done")


if __name__ == "__main__":
    main()
