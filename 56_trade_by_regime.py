"""Trade by the partner's type of government and geopolitical alignment.

Classifications (partner and year):
  regime     V-Dem Regimes of the World (v2x_regime, V-Dem v16, CC BY-SA 4.0): closed
             autocracy, electoral autocracy, electoral democracy, liberal democracy
             (Lührmann, Tannenberg and Lindberg 2018); plus the Liberal Democracy Index
             (v2x_libdem) for import-weighted averages
  alignment  UN General Assembly ideal points (Bailey, Strezhnev and Voeten 2017; data
             1946-2025, CC0): position a = (p - p_CHN) / (p_USA - p_CHN) each year;
             a >= 0.5 closer to the US, else closer to China. With three bands most
             of Europe and Japan would fall in between (Germany 0.66, Japan 0.54 in
             2024), because the US is an outlier on this scale.
Data: <data>/vdem/vdemdata (git clone of github.com/vdeminstitute/vdemdata, version
16.0; the download form on v-dem.net asks for personal data), <data>/vdem/
un_ideal_2025.csv (Harvard Dataverse doi:10.7910/DVN/LEJUQZ, file 14098429), IMF IMTS
(52_zero_trade.py) for values, zero-trade matrices (52) and dependencies (44).
Outputs in <output>/regime: shares_<who>.csv, breadth_<level>.csv, dependencies.csv,
regime.pdf/png, regime.xlsx. Usage: python 56_trade_by_regime.py
"""
import importlib
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from config import load_config

EU = importlib.import_module("44_dependencies").EU
REG = {0: "geschlossene Autokratie", 1: "Wahlautokratie", 2: "Wahldemokratie", 3: "liberale Demokratie",
       -1: "keine Einstufung"}
REG_COL = {3: "#002060", 2: "#5b9bd5", 1: "#f4b183", 0: "#c00000", -1: "#d9d9d9"}
ALI = {2: "näher an den USA", 0: "näher an China", -1: "keine Einstufung"}
ALI_COL = {2: "#002060", 0: "#c00000", -1: "#d9d9d9"}


def vdem(raw):
    cache = raw / "vdem_core_1990.csv"
    if not cache.exists():
        import pyreadr
        d = pyreadr.read_r(raw / "vdemdata" / "data" / "vdem.RData")["vdem"]
        d = d[d.year >= 1990][["country_text_id", "year", "v2x_regime", "v2x_libdem", "v2x_polyarchy"]]
        d.to_csv(cache, index=False)
    d = pd.read_csv(cache).rename(columns={"country_text_id": "iso"})
    d["year"] = d.year.astype(int)
    return d


def alignment(raw):
    u = pd.read_csv(raw / "un_ideal_2025.csv")[["iso3c", "year", "IdealPointFP"]].rename(
        columns={"iso3c": "iso", "IdealPointFP": "p"})
    ref = u[u.iso.isin(["USA", "CHN"])].pivot(index="year", columns="iso", values="p")
    u = u.join(ref, on="year")
    u["a"] = (u.p - u.CHN) / (u.USA - u.CHN)
    u["bloc"] = np.where(u.a >= 0.5, 2, 0)
    return u[["iso", "year", "a", "bloc"]]


def imf_values(raw):
    rows = []
    for ind in ("XG_FOB_USD", "MG_CIF_USD"):
        for _, el in ET.iterparse(raw / f"{ind}.xml"):
            if el.tag.endswith("Series"):
                rep, cp = el.attrib.get("COUNTRY"), el.attrib.get("COUNTERPART_COUNTRY")
                if rep == "DEU" or rep in EU:
                    for o in el:
                        v = o.attrib.get("OBS_VALUE")
                        if v not in (None, "", "NaN"):
                            rows.append((rep, cp, ind[0], int(o.attrib["TIME_PERIOD"][:4]), float(v)))
                el.clear()
    d = pd.DataFrame(rows, columns=["reporter", "partner", "flow", "year", "value"])
    return d[d.partner.str.fullmatch(r"[A-Z]{3}") & d.year.between(1990, 2024)]


def classify(d, col, vd, al):
    d = d.merge(vd[["iso", "year", "v2x_regime", "v2x_libdem"]].rename(columns={"iso": col}), on=[col, "year"], how="left")
    d = d.merge(al[["iso", "year", "bloc"]].rename(columns={"iso": col}), on=[col, "year"], how="left")
    d["regime"] = d.v2x_regime.fillna(-1).astype(int)
    d["bloc"] = d.bloc.fillna(-1).astype(int)
    return d


def main():
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "regime"
    out.mkdir(parents=True, exist_ok=True)
    vd, al = vdem(raw / "vdem"), alignment(raw / "vdem")
    xl = {}

    # A: shares of trade by partner regime and alignment
    t = imf_values(raw / "imts")
    deu = t[(t.reporter == "DEU") & (t.partner != "DEU")].assign(who="DEU")
    eu = t[t.reporter.isin(EU) & ~t.partner.isin(EU)].assign(who="EU27")
    flows = classify(pd.concat([deu, eu]), "partner", vd, al)
    shares = {}
    for who in ("DEU", "EU27"):
        for flow in ("X", "M"):
            f = flows[(flows.who == who) & (flows.flow == flow)]
            for dim in ("regime", "bloc"):
                s = f.groupby(["year", dim]).value.sum().unstack(fill_value=0)
                s = s.div(s.sum(axis=1), axis=0)
                shares[(who, flow, dim)] = s
                xl[f"{who}_{flow}_{dim}"] = s.rename(columns=REG if dim == "regime" else ALI).round(4)
            # trade shifts with the 2024 classification held fixed (separates changes in
            # trade from reclassified partners, e.g. the UK and Korea in 2024)
            fix = vd[vd.year == 2024].set_index("iso").v2x_regime
            auto = f.partner.map(fix).isin([0, 1])
            fx = (f.value * auto).groupby(f.year).sum() / f.value.groupby(f.year).sum()
            xl[f"{who}_{flow}_fix2024"] = fx.rename("autocracies_2024_classification").round(4).to_frame()
            shares[(who, flow, "fixed")] = fx
            lib = f.dropna(subset=["v2x_libdem"])
            w = (lib.v2x_libdem * lib.value).groupby(lib.year).sum() / lib.value.groupby(lib.year).sum()
            xl[f"{who}_{flow}_libdem"] = w.rename("libdem_weighted").round(4).to_frame()
            print(f"{who} {flow}: autocracies' share 1990 {shares[(who, flow, 'regime')].loc[1990, [0, 1]].sum():.0%} "
                  f"-> 2024 {shares[(who, flow, 'regime')].loc[2024, [0, 1]].sum():.0%}; trade-weighted LDI "
                  f"{w.loc[1990]:.2f} -> {w.loc[2024]:.2f}; with 2024 classification fixed {fx.loc[1990]:.0%} -> {fx.loc[2024]:.0%}")

    # B: breadth of Germany's trade by partner regime (zero-trade matrices)
    breadth = {}
    for lv in ("country", "hs6"):
        z = np.load(cfg["output"] / "zero_trade" / f"matrices_{lv}.npz")
        years, cs, x, two = z["years"], list(z["countries"]), z["x"], z["two"]
        k = cs.index("DEU")
        rows = []
        for ti, y in enumerate(years):
            reg = vd[vd.year == y].set_index("iso").v2x_regime
            g = np.array([reg.get(c, -1) if c != "DEU" else -2 for c in cs])
            for r in (3, 2, 1, 0):
                sel = g == r
                if sel.sum() == 0:
                    continue
                e, m, w = x[ti, k, sel], x[ti, sel, k], two[ti, k, sel]
                rows.append({"year": int(y), "regime": r, "n_partners": int(sel.sum()), "two_way": w.mean(),
                             "export_only": e.mean() - w.mean(), "import_only": m.mean() - w.mean(),
                             "none": 1 - e.mean() - m.mean() + w.mean()})
        b = pd.DataFrame(rows)
        breadth[lv] = b
        b.round(4).to_csv(out / f"breadth_{lv}.csv", index=False)
        xl[f"Breite_{lv}"] = b.round(4)
        last = b[b.year == b.year.max()].set_index("regime")
        print(f"breadth {lv} {b.year.max()}: two-way share " + ", ".join(f"{REG[r]} {last.two_way[r]:.0%}" for r in last.index))

    # C: dependencies by regime and alignment of the main supplier (2024)
    dep = pd.read_csv(cfg["output"] / "scenarios" / "dependencies_hs6.csv", dtype={"hs6": str})
    dep = dep[dep.dependent].assign(year=2024)
    dep = classify(dep, "top_supplier", vd, al)
    rows = []
    for lv, g in dep.groupby("level"):
        for dim, names in (("regime", REG), ("bloc", ALI)):
            for c, h in g.groupby(dim):
                rows.append({"level": lv, "dimension": dim, "class": names[c], "n_goods": len(h),
                             "imports_bn": h.extra_imports.sum() / 1e6, "share_value": h.extra_imports.sum() / g.extra_imports.sum()})
    dd = pd.DataFrame(rows)
    dd.round(4).to_csv(out / "dependencies.csv", index=False)
    xl["Abhaengigkeiten"] = dd.round(4)
    print(dd.round(3).to_string(index=False))

    # figures
    pdf = PdfPages(out / "regime.pdf")
    for dim, names, cols, title in (("regime", REG, REG_COL, "Regimetyp (V-Dem)"), ("bloc", ALI, ALI_COL, "Nähe in UN-Abstimmungen")):
        fig, axes = plt.subplots(2, 2, figsize=(14, 8), sharex=True, sharey=True)
        for a, (who, flow) in zip(axes.flat, [("DEU", "X"), ("DEU", "M"), ("EU27", "X"), ("EU27", "M")]):
            s = shares[(who, flow, dim)] * 100
            order = [c for c in ([3, 2, 1, 0, -1] if dim == "regime" else [2, 0, -1]) if c in s.columns]
            a.stackplot(s.index, *[s[c] for c in order], colors=[cols[c] for c in order], labels=[names[c] for c in order])
            a.set_title(f"{'Deutschland' if who == 'DEU' else 'EU27, Handel mit Drittstaaten'}: "
                        f"{'Exporte' if flow == 'X' else 'Importe'}", loc="left", fontsize=10)
            if dim == "regime":
                fx = shares[(who, flow, "fixed")] * 100
                a.plot(fx.index, 100 - fx, color="#000", lw=1.2, ls="--", label="Grenze Autokratien bei fester Einstufung 2024")
            a.set_ylim(0, 100); a.set_xlim(1990, 2024)
            for yv, lab in ((2001, "WTO China"), (2008, "Finanzkrise"), (2020, "Pandemie")):
                a.axvline(yv, color="#fff", lw=0.8)
        axes[0, 0].legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.1), frameon=False, fontsize=9)
        fig.suptitle(f"Handel nach {title} der Partner, Anteile in %", x=0.01, ha="left", fontsize=12)
        fig.text(0.01, 0.01, ("V-Dem Regimes of the World (v16)" if dim == "regime" else
                              "UN-Idealpunkte nach Bailey, Strezhnev und Voeten (2017): Lage zwischen China (0) und USA (1), "
                              "Grenze 0,5") + "; Werte: IMF IMTS. Quelle: eigene Berechnungen.", fontsize=7)
        fig.subplots_adjust(left=0.05, right=0.98, top=0.8, bottom=0.08, wspace=0.08, hspace=0.25)
        pdf.savefig(fig); fig.savefig(out / f"shares_{dim}.png", dpi=200); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    b = breadth["hs6"]
    for a, (cols, lab) in zip(axes, ((("two_way", "export_only"), "Anteil der Partner-Code-Paare mit deutschen Exporten"),
                                     (("two_way",), "Anteil der Partner-Code-Paare mit Handel in beide Richtungen"))):
        for r in (3, 2, 1, 0):
            s = b[b.regime == r]
            a.plot(s.year, s[list(cols)].sum(axis=1) * 100, color=REG_COL[r], lw=2, label=REG[r])
        a.set_title("HS6: " + lab, loc="left", fontsize=10)
        a.set_ylabel("%")
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    axes[1].legend(frameon=False, fontsize=9)
    fig.suptitle("Breite des deutschen Handels nach Regimetyp der Partner (Einstufung des jeweiligen Jahres)", x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    pdf.savefig(fig); fig.savefig(out / "breadth.png", dpi=200); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.8))
    for a, dim, names, cols in ((axes[0], "regime", REG, REG_COL), (axes[1], "bloc", ALI, ALI_COL)):
        for yi, lv in enumerate(("EU27", "DEU")):
            g = dd[(dd.level == lv) & (dd.dimension == dim)].set_index("class")
            left = 0
            for c in ([3, 2, 1, 0, -1] if dim == "regime" else [2, 0, -1]):
                v = g.share_value.get(names[c], 0) * 100
                a.barh(yi, v, left=left, color=cols[c], label=names[c] if yi == 0 else None)
                if v > 6:
                    a.text(left + v / 2, yi, f"{v:.0f} %", ha="center", va="center", color="#fff" if cols[c] in ("#002060", "#c00000") else "#000", fontsize=8)
                left += v
        a.set_yticks([0, 1], ["EU27", "Deutschland"]); a.set_xlim(0, 100)
        a.set_title("nach Regimetyp des Hauptlieferanten" if dim == "regime" else "nach UN-Nähe des Hauptlieferanten", loc="left", fontsize=10)
        a.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, -0.15), frameon=False, fontsize=8)
    fig.suptitle("Abhängige Waren 2024: Importwert nach Hauptlieferant, in %", x=0.01, ha="left", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    pdf.savefig(fig); fig.savefig(out / "dependencies.png", dpi=200); plt.close(fig)
    pdf.close()
    with pd.ExcelWriter(out / "regime.xlsx") as w:
        pd.DataFrame({"Hinweis": [
            "Handel nach Regimetyp (V-Dem v16, CC BY-SA 4.0) und UN-Abstimmungsnähe (Bailey, Strezhnev und Voeten 2017, CC0).",
            "Werte: IMF IMTS (Exporte fob, Importe cif, Berichtsland Deutschland bzw. EU-Mitglieder mit Drittstaaten).",
            "Breite: Null-Handel-Matrizen (Länderebene IMF, HS6 BACI). Abhängigkeiten: Kriterien der EU-Kommission, BACI 2024."]}).to_excel(
            w, sheet_name="Info", index=False)
        for k, d in xl.items():
            d.to_excel(w, sheet_name=k[:31])


if __name__ == "__main__":
    main()
