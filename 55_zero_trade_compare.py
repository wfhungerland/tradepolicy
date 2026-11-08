"""Germany's trade breadth compared with other countries, the EU and the euro area.

From the matrices of 52_zero_trade.py: for every country and year the shares of all
partners (country level) or all partner x code cells (HS levels) with two-way trade,
exports only, imports only and no trade. EU27 and euro area (EA21, composition of 2026
including Bulgaria) are means over their members, unweighted and weighted by 2024 goods
exports (BACI); members missing from a level's fixed country set are left out (IMF
country level: nine members that did not report from 1990 or were reported jointly).
Writes <output>/zero_trade/compare_<level>.csv, compare.pdf/png and adds the shares of all
countries to compare_all.csv. Usage: python 55_zero_trade_compare.py
"""
import importlib
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from config import load_config

EU = importlib.import_module("44_dependencies").EU
EA = ["AUT", "BEL", "BGR", "HRV", "CYP", "EST", "FIN", "FRA", "DEU", "GRC", "IRL", "ITA", "LVA", "LTU", "LUX",
      "MLT", "NLD", "PRT", "SVK", "SVN", "ESP"]
GROUP_A = ["USA", "JPN", "FRA", "ITA", "GBR", "CAN", "CHN", "KOR"]
GROUP_B = ["FRA", "ITA", "ESP", "NLD", "POL", "AUT"]
LEVELS = [("country", "Länder (IMF)"), ("section", "HS-Abschnitte"), ("hs2", "HS2"), ("hs4", "HS4"), ("hs6", "HS6")]
CATS = [("two_way", "beidseitig", "#002060"), ("export_only", "nur Export", "#5b9bd5"),
        ("import_only", "nur Import", "#a6a6a6"), ("none", "kein Handel", "#f2f2f2")]
NAMES = {"DEU": "Deutschland", "EU27": "EU27, Ø Mitglieder", "EU27w": "EU27, exportgewichtet",
         "EA21": "Euroraum, Ø Mitglieder", "EA21w": "Euroraum, exportgewichtet", "USA": "USA", "JPN": "Japan",
         "FRA": "Frankreich", "ITA": "Italien", "GBR": "Vereinigtes Königreich", "CAN": "Kanada", "CHN": "China",
         "KOR": "Korea", "ESP": "Spanien", "NLD": "Niederlande", "POL": "Polen", "AUT": "Österreich"}


def shares(x, two):
    n = x.shape[1] - 1
    e, m, w = x.sum(axis=2) / n, x.sum(axis=1) / n, two.sum(axis=2) / n
    return {"two_way": w, "export_only": e - w, "import_only": m - w, "none": 1 - e - m + w}


def export_weights(cfg):
    path = cfg["data"]["scenarios"] / "baci92" / "BACI_HS92_V202601.zip"
    with zipfile.ZipFile(path) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str,
                         keep_default_na=False)
        iso = dict(zip(cc.country_code.astype(int), cc.country_iso3))
        b = pd.read_csv(z.open(next(n for n in z.namelist() if "_Y2024_" in n)), usecols=["i", "v"])
    return b.groupby("i").v.sum().rename(index=iso).groupby(level=0).sum()


def main():
    cfg = load_config()
    out = cfg["output"] / "zero_trade"
    wts = export_weights(cfg)
    allrows = []
    data = {}
    for lv, _ in LEVELS:
        z = np.load(out / f"matrices_{lv}.npz")
        years, countries = z["years"], list(z["countries"])
        s = shares(z["x"], z["two"])
        frame = pd.concat([pd.DataFrame(s[k], index=years, columns=countries).stack().rename(k) for k in s], axis=1)
        frame.index.names = ["year", "entity"]
        frame = frame.reset_index()
        rows = [frame]
        for name, members in (("EU27", EU), ("EA21", EA)):
            sub = frame[frame.entity.isin(members)]
            w = sub.entity.map(wts).fillna(0)
            un = sub.groupby("year")[[k for k, *_ in CATS]].mean().reset_index().assign(entity=name)
            wt = (sub[[k for k, *_ in CATS]].mul(w, axis=0).groupby(sub.year).sum()
                  .div(w.groupby(sub.year).sum(), axis=0).reset_index().assign(entity=name + "w"))
            rows += [un, wt]
            print(f"{lv}: {name} {sub.entity.nunique()} of {len(members)} members")
        f = pd.concat(rows, ignore_index=True)
        f["level"] = lv
        data[lv] = f
        allrows.append(f)
        f.round(5).to_csv(out / f"compare_{lv}.csv", index=False)
    pd.concat(allrows).round(5).to_csv(out / "compare_all.csv", index=False)

    pdf = PdfPages(out / "compare.pdf")
    # overview: latest year, horizontal stacked bars, all levels
    ents = ["DEU", "EU27", "EU27w", "EA21", "EA21w"] + GROUP_A + [g for g in GROUP_B if g not in GROUP_A]
    fig, axes = plt.subplots(1, len(LEVELS), figsize=(17, 6.5), sharey=True)
    for a, (lv, title) in zip(axes, LEVELS):
        f = data[lv]
        y = f.year.max()
        f = f[f.year == y].set_index("entity")
        left = np.zeros(len(ents))
        for k, lab, col in CATS:
            v = np.array([f[k].get(e, np.nan) for e in ents]) * 100
            a.barh(range(len(ents)), v, left=left, color=col, label=lab, edgecolor="#bfbfbf" if k == "none" else None,
                   linewidth=0.3)
            left = left + np.nan_to_num(v)
        a.set_yticks(range(len(ents)), [NAMES[e] for e in ents], fontsize=8)
        a.invert_yaxis(); a.set_xlim(0, 100); a.set_title(f"{title}, {y}", fontsize=10, loc="left")
        a.axhline(0.5, color="#000", lw=0.5); a.axhline(4.5, color="#000", lw=0.5)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    axes[0].legend(ncol=4, loc="lower left", bbox_to_anchor=(0, 1.08), frameon=False, fontsize=9)
    fig.suptitle("Handel nach Partnern bzw. Partner-Code-Paaren im Vergleich, in %", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "EU27 und Euroraum (21 Mitglieder, Stand 2026): Mittel der Mitgliedstaaten, ungewichtet bzw. nach "
             "Exporten 2024 gewichtet; auf Länderebene fehlen neun Mitglieder ohne Daten seit 1990. Quelle: eigene "
             "Berechnungen auf Basis von IMF IMTS und CEPII BACI HS92 V202601.", fontsize=7)
    fig.subplots_adjust(left=0.11, right=0.99, top=0.82, bottom=0.1, wspace=0.08)
    pdf.savefig(fig); fig.savefig(out / "compare_latest.png", dpi=200); plt.close(fig)
    # time series per level: small multiples
    for lv, title in LEVELS:
        for gname, group in (("G7, China, Korea", GROUP_A), ("große EU-Länder", GROUP_B)):
            es = ["DEU", "EU27", "EA21"] + group
            ncol = 4
            nrow = int(np.ceil(len(es) / ncol))
            fig, axes = plt.subplots(nrow, ncol, figsize=(16, 2.6 * nrow), sharex=True, sharey=True)
            for a, e in zip(axes.flat, es):
                f = data[lv][data[lv].entity == e].sort_values("year")
                bottom = np.zeros(len(f))
                for k, lab, col in CATS:
                    a.bar(f.year, f[k] * 100, bottom=bottom, color=col, width=0.85,
                          edgecolor="#bfbfbf" if k == "none" else None, linewidth=0.2, label=lab)
                    bottom += f[k].to_numpy() * 100
                a.set_title(NAMES[e], fontsize=9, loc="left"); a.set_ylim(0, 100)
                for sp in ("top", "right"):
                    a.spines[sp].set_visible(False)
            for a in list(axes.flat)[len(es):]:
                a.axis("off")
            list(axes.flat)[0].legend(ncol=4, loc="lower left", bbox_to_anchor=(0, 1.2), frameon=False, fontsize=8)
            fig.suptitle(f"{title}: Deutschland, EU, Euroraum und {gname}, in %", x=0.01, ha="left", fontsize=12)
            fig.tight_layout(rect=(0, 0, 1, 0.93))
            pdf.savefig(fig); plt.close(fig)
    pdf.close()
    latest = pd.concat([d[d.year == d.year.max()] for d in data.values()])
    print(latest[latest.entity.isin(["DEU", "EU27", "EA21", "USA", "CHN", "FRA"])].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
