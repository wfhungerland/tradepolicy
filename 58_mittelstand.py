"""The Mittelstand in trade: how exposed are small and medium-sized enterprises (SMEs)?

Data: Eurostat trade by enterprise characteristics (TEC), from the registers linked to
customs data: ext_tec10 (size class x partner country) and ext_tec01 (size class x
economic activity NACE Rev. 2 x partner zone), 2012-2024, values in thousand euro and
numbers of enterprises. SMEs: fewer than 250 employees (classes 0-9, 10-49, 50-249).
Shares refer to the total including enterprises of unknown size. Enterprises are classed
by their main activity: exports of a manufacturer through a wholesaler count under
wholesale trade (NACE G), which carries a large part of SME exports.

Exposure (Germany):
  US tariffs   model change in exports to the US by ICIO sector (scenario current_2026_08,
               34_scenario_us_tariffs.py) applied to SME and large-firm exports of the
               matching manufacturing activity outside the EU (ext_tec01, EXT_EU); assumes
               that within an activity SMEs and large firms lose the same share
  China        German exports of goods under Chinese price pressure (50_china_competition.py)
               by ICIO sector, split by the SME share of the activity's exports outside
               the EU
  imports      SME share of imports from China against imports from the world (ext_tec10)
Writes <output>/mittelstand/*.csv, mittelstand.pdf/png, mittelstand.xlsx.
Usage: python 58_mittelstand.py
"""
import importlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from config import load_config

SME = ["LT10", "10-49", "50-249"]
NACE_ICIO = {"C10": "C10T12", "C11": "C10T12", "C12": "C10T12", "C13": "C13T15", "C14": "C13T15", "C15": "C13T15",
             "C16": "C16", "C17": "C17_18", "C18": "C17_18", "C19": "C19", "C20": "C20", "C21": "C21", "C22": "C22",
             "C23": "C23", "C24": ["C24A", "C24B"], "C25": "C25", "C26": "C26", "C27": "C27", "C28": "C28", "C29": "C29",
             "C30": ["C301", "C302T309"], "C31": "C31T33", "C32": "C31T33", "C33": "C31T33"}
PARTNERS = {"WORLD": "Welt", "INT_EU": "EU-Binnenmarkt", "EXT_EU": "außerhalb der EU", "US": "USA", "CN_X_HK": "China",
            "UK": "Vereinigtes Königreich", "CH": "Schweiz", "FR": "Frankreich", "NL": "Niederlande", "PL": "Polen",
            "IT": "Italien", "AT": "Österreich", "JP": "Japan", "IN": "Indien", "TR": "Türkei", "RU": "Russland"}


def read_tec(raw, name):
    d = pd.read_csv(raw / f"{name}.tsv.gz", sep="\t")
    k = d.columns[0]
    dims = k.split("\\")[0].split(",")
    s = d[k].str.split(",", expand=True)
    s.columns = dims
    v = d.drop(columns=k)
    v.columns = [c.strip() for c in v.columns]
    v = v.apply(lambda c: pd.to_numeric(c.astype(str).str.extract(r"([-\d.]+)")[0], errors="coerce"))
    out = pd.concat([s.drop(columns="freq"), v], axis=1).melt(id_vars=[c for c in dims if c != "freq"],
                                                                  var_name="year", value_name="value")
    out["year"] = out.year.astype(int)
    return out


def sme_share(d, keys):
    p = d.pivot_table(index=keys, columns="sizeclas", values="value", aggfunc="sum")
    return pd.DataFrame({"sme": p[SME].sum(axis=1, min_count=1), "large": p.get("GE250"), "unknown": p.get("UNK"),
                         "total": p["TOTAL"]})


def main():
    cfg = load_config()
    raw = cfg["data"]["scenarios"] / "eurostat"
    out = cfg["output"] / "mittelstand"
    out.mkdir(parents=True, exist_ok=True)
    xl = {}
    t10 = read_tec(raw, "ext_tec10")
    t01 = read_tec(raw, "ext_tec01")

    # A: SME shares by partner, Germany and EU, values and numbers of enterprises
    a = t10[t10.geo.isin(["DE", "EU"])]
    sa = sme_share(a, ["geo", "unit", "stk_flow", "partner", "year"])
    sa["sme_share"] = sa.sme / sa.total
    sa = sa.reset_index()
    sa.round(4).to_csv(out / "by_partner.csv", index=False)
    last = sa.year.max()
    v = sa[(sa.unit == "THS_EUR") & (sa.year == last)]
    tab = v.pivot_table(index="partner", columns=["geo", "stk_flow"], values="sme_share")
    tab = tab.loc[[p for p in PARTNERS if p in tab.index]].rename(index=PARTNERS)
    xl["KMU-Anteil_Partner"] = tab.round(3)
    print(f"SME share of exports and imports by partner, {last}:")
    print((tab * 100).round(1).to_string())
    nr = sa[(sa.unit == "NR_ENT") & (sa.geo == "DE") & (sa.stk_flow == "EXP") & (sa.year == last)].set_index("partner")
    print(f"German exporting enterprises {last}: world {nr.total.get('WORLD'):,.0f} (SMEs {nr.sme_share.get('WORLD'):.0%}), "
          f"to the US {nr.total.get('US'):,.0f}, to China {nr.total.get('CN_X_HK'):,.0f}")

    # B: SME shares by activity (Germany, exports outside the EU and to the world)
    b = t01[(t01.geo == "DE") & (t01.unit == "THS_EUR") & (t01.stk_flow == "EXP")]
    sb = sme_share(b, ["partner", "nace_r2", "year"])
    sb["sme_share"] = sb.sme / sb.total
    sb = sb.reset_index()
    sb.round(4).to_csv(out / "by_activity.csv", index=False)
    yb = sb.year.max()
    act = sb[(sb.year == yb) & (sb.partner == "EXT_EU")].set_index("nace_r2")
    xl["KMU-Anteil_Branche"] = sb[sb.year == yb].pivot_table(index="nace_r2", columns="partner", values="sme_share").round(3)
    print(f"SME share of exports outside the EU, {yb}: total {act.sme_share['TOTAL']:.0%}, manufacturing "
          f"{act.sme_share['C']:.0%}, wholesale {act.sme_share.get('G46', np.nan):.0%}; share of wholesale in all "
          f"exports outside the EU {act.total.get('G', np.nan) / act.total['TOTAL']:.0%}")

    # map activities to ICIO sectors (SME and large-firm values summed per sector)
    rows = []
    for n, s in NACE_ICIO.items():
        if n not in act.index:
            continue
        for sec in (s if isinstance(s, list) else [s]):
            k = len(s) if isinstance(s, list) else 1
            rows.append({"sector": sec, "sme": act.sme[n] / k, "large": act.large[n] / k, "total": act.total[n] / k})
    sec = pd.DataFrame(rows).groupby("sector").sum()
    sec["sme_share"] = sec.sme / sec.total

    # C: US tariffs
    us = pd.read_csv(cfg["output"] / "scenarios" / "us_tariffs_germany_sectors.csv")
    us = us[us.scenario == "current_2026_08"].set_index("sector")
    c = sec.join(us[["exports_to_us_pct", "exports_to_us_2022_bn"]], how="inner")
    c["loss_bn"] = -c.exports_to_us_pct / 100 * c.exports_to_us_2022_bn
    c["loss_sme_bn"] = c.loss_bn * c.sme_share
    sme_loss_share = c.loss_sme_bn.sum() / c.loss_bn.sum()
    us_direct = v[(v.geo == "DE") & (v.stk_flow == "EXP")].set_index("partner").sme_share
    print(f"US tariffs: manufacturing exports to the US fall by USD {c.loss_bn.sum():.1f} bn; SMEs carry "
          f"{sme_loss_share:.0%} (SME share of all German exports to the US {us_direct.get('US'):.0%}, of manufacturing "
          f"exports outside the EU {c.sme.sum() / c.total.sum():.0%})")

    # D: China price pressure
    m33 = importlib.import_module("33_tariff_inputs")
    conc = cfg["data"]["scenarios"] / "conc"
    h07_h92 = pd.read_csv(next(conc.glob("*H3_to_H0*.CSV")), dtype=str, encoding="latin1", usecols=[0, 2])
    h07_h92.columns = ["hs07", "hs92"]
    _, hs07, _ = m33.concordance(conc)
    hmap = h07_h92.merge(hs07, on="hs07").drop_duplicates("hs92")[["hs92", "sector"]]
    comp = pd.read_csv(cfg["output"] / "scenarios" / "china_competition_hs6.csv", dtype={"hs92": str}).merge(hmap, on="hs92")
    ex = comp[comp.exposed].groupby("sector").deu_exports_bn.sum().rename("exposed_bn")
    d = sec.join(ex, how="inner")
    d["exposed_sme_bn"] = d.exposed_bn * d.sme_share
    print(f"China price pressure: exposed German exports USD {d.exposed_bn.sum():.0f} bn in manufacturing sectors; "
          f"SMEs {d.exposed_sme_bn.sum() / d.exposed_bn.sum():.0%}")

    # E: imports from China
    imp = v[(v.geo == "DE") & (v.stk_flow == "IMP")].set_index("partner").sme_share
    print(f"Imports {last}: SME share from China {imp.get('CN_X_HK'):.0%}, from the world {imp.get('WORLD'):.0%}")

    expo = c[["sme_share", "exports_to_us_pct", "exports_to_us_2022_bn", "loss_bn", "loss_sme_bn"]].join(
        d[["exposed_bn", "exposed_sme_bn"]], how="outer")
    expo.round(4).to_csv(out / "exposure_sectors.csv")
    xl["Betroffenheit_Branchen"] = expo.round(3)
    summary = pd.DataFrame([
        {"Kennzahl": f"KMU-Anteil an den deutschen Exporten, Welt, {last}", "Wert": us_direct.get("WORLD")},
        {"Kennzahl": f"KMU-Anteil an den deutschen Exporten in die USA, {last}", "Wert": us_direct.get("US")},
        {"Kennzahl": f"KMU-Anteil an den deutschen Exporten nach China, {last}", "Wert": us_direct.get("CN_X_HK")},
        {"Kennzahl": "Anteil der KMU am Exportrückgang in die USA (Industrie, Zollstand August 2026)", "Wert": sme_loss_share},
        {"Kennzahl": "Anteil der KMU an Exporten unter Preisdruck aus China (Industrie)", "Wert": d.exposed_sme_bn.sum() / d.exposed_bn.sum()},
        {"Kennzahl": f"KMU-Anteil an den Importen aus China, {last}", "Wert": imp.get("CN_X_HK")},
        {"Kennzahl": f"KMU-Anteil an den Importen, Welt, {last}", "Wert": imp.get("WORLD")}])
    summary.round(4).to_csv(out / "summary.csv", index=False)
    xl["Kennzahlen"] = summary.round(4).set_index("Kennzahl")

    # figures
    pdf = PdfPages(out / "mittelstand.pdf")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6), sharey=True)
    order = [p for p in PARTNERS if p in tab.index.map({v: k for k, v in PARTNERS.items()})]
    for a_, flow, title in ((axes[0], "EXP", "Exporte"), (axes[1], "IMP", "Importe")):
        for k, (geo, col) in enumerate((("DE", "#002060"), ("EU", "#a6a6a6"))):
            vals = [tab.loc[PARTNERS[p], (geo, flow)] * 100 if (geo, flow) in tab.columns else np.nan for p in order]
            a_.barh(np.arange(len(order)) + (k - 0.5) * 0.4, vals, height=0.4, color=col,
                    label="Deutschland" if geo == "DE" else "EU27")
        a_.set_yticks(range(len(order)), [PARTNERS[p] for p in order]); a_.invert_yaxis()
        a_.set_title(f"{title}: Anteil der KMU, {last}, in %", loc="left", fontsize=10)
        for sp in ("top", "right"):
            a_.spines[sp].set_visible(False)
    axes[0].legend(frameon=False)
    fig.suptitle("Mittelstand im Außenhandel: Anteil von Unternehmen mit weniger als 250 Beschäftigten", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: Eurostat, Handel nach Unternehmensmerkmalen (ext_tec10); Anteile am Gesamtwert einschließlich "
             "Unternehmen unbekannter Größe. Großhändler zählen als eigene Unternehmen.", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    pdf.savefig(fig); fig.savefig(out / "by_partner.png", dpi=200); plt.close(fig)
    fig, a_ = plt.subplots(figsize=(12, 6))
    e = expo.dropna(subset=["sme_share"]).sort_values("sme_share")
    a_.barh(e.index, e.sme_share * 100, color="#002060")
    a_.set_title(f"KMU-Anteil an den Exporten außerhalb der EU nach Branche (ICIO), {yb}, in %", loc="left", fontsize=10)
    for sp in ("top", "right"):
        a_.spines[sp].set_visible(False)
    fig.tight_layout()
    pdf.savefig(fig); fig.savefig(out / "by_sector.png", dpi=200); plt.close(fig)
    pdf.close()
    with pd.ExcelWriter(out / "mittelstand.xlsx") as w:
        pd.DataFrame({"Hinweis": [
            "Mittelstand im Außenhandel: KMU = weniger als 250 Beschäftigte. Quelle: Eurostat TEC (ext_tec10, ext_tec01).",
            "Betroffenheit: Modellrückgang der Exporte in die USA je Branche (Zollstand August 2026) und Exporte unter Preisdruck "
            "aus China, aufgeteilt nach dem KMU-Anteil der Branche an den Exporten außerhalb der EU."]}).to_excel(w, sheet_name="Info", index=False)
        for k, df in xl.items():
            df.to_excel(w, sheet_name=k[:31])


if __name__ == "__main__":
    main()
