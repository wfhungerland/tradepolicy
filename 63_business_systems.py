"""Varieties of capitalism: trade by business system and institutional distance.

Source: Witt, M. A., Kabbach de Castro, L. R., Amaeshi, K., Mahroum, S., Bohle, D. and
Saez, L. (2018), Mapping the business systems of 61 major economies, Socio-Economic
Review 16(1), 5-38 (open access, EUI Cadmus hdl 1814/59929): nine clusters (Table 5) and
pairwise institutional distances (Table 4, Gower dissimilarity over institutional
variables around 2013; 0 = identical, higher = less similar). The matrix is parsed from
the PDF text (all 1,830 pairs; checked: each row has as many values as countries before
it). Note: the paper writes GE for Greece.

A. Trade of Germany and the EU (extra-EU) by business-system type of the partner, IMF IMTS
   1990-2024 (classification held fixed), and dependent goods by type of main supplier.
B. Gravity with institutional distance (cross-section, PPML): ITPD-E manufacturing, mean
   2017-2019, among the 61 economies, international flows only:
     X_ij = exp(a_i + b_j + d ID_ij + c ln dist_ij + contiguity + common language + colony + RTA)
   ID standardised. Then Germany: actual trade against institutional distance.
Writes <output>/business_systems/*, figures and xlsx. Usage: python 63_business_systems.py
"""
import importlib
import json
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyfixest as pf

from config import load_config

ISO = {"DZ": "DZA", "AR": "ARG", "AU": "AUS", "AT": "AUT", "BD": "BGD", "BE": "BEL", "BR": "BRA", "CA": "CAN", "CL": "CHL",
       "CN": "CHN", "CO": "COL", "CU": "CUB", "CZ": "CZE", "DK": "DNK", "EG": "EGY", "FI": "FIN", "FR": "FRA", "DE": "DEU",
       "GE": "GRC", "HK": "HKG", "HU": "HUN", "IN": "IND", "ID": "IDN", "IE": "IRL", "IL": "ISR", "IT": "ITA", "JP": "JPN",
       "KZ": "KAZ", "KR": "KOR", "KW": "KWT", "MY": "MYS", "MX": "MEX", "MA": "MAR", "NL": "NLD", "NZ": "NZL", "NG": "NGA",
       "NO": "NOR", "PK": "PAK", "PE": "PER", "PH": "PHL", "PL": "POL", "PT": "PRT", "QA": "QAT", "RO": "ROU", "RU": "RUS",
       "SA": "SAU", "SG": "SGP", "SK": "SVK", "ZA": "ZAF", "ES": "ESP", "SE": "SWE", "CH": "CHE", "TW": "TWN", "TH": "THA",
       "TR": "TUR", "UA": "UKR", "AE": "ARE", "GB": "GBR", "US": "USA", "VE": "VEN", "VN": "VNM"}
CLUSTERS = {
    "hoch koordiniert": ["JPN"],
    "koordinierte Marktwirtschaft": ["AUT", "BEL", "DNK", "FIN", "DEU", "NLD", "NOR", "SWE", "CHE"],
    "liberale Marktwirtschaft": ["AUS", "CAN", "IRL", "NZL", "GBR", "USA"],
    "europäische Peripherie": ["CZE", "FRA", "GRC", "HUN", "ITA", "POL", "PRT", "ROU", "SVK", "ESP"],
    "fortgeschrittene Schwellenländer": ["CHL", "ISR", "KOR", "ZAF", "TWN", "TUR"],
    "fortgeschrittene Stadtstaaten": ["HKG", "SGP"],
    "arabische Ölstaaten": ["KWT", "QAT", "SAU", "ARE"],
    "Schwellenländer": ["DZA", "ARG", "BGD", "BRA", "CHN", "COL", "EGY", "IND", "IDN", "KAZ", "MYS", "MEX", "MAR", "NGA",
                        "PAK", "PER", "PHL", "RUS", "THA", "UKR", "VNM"],
    "sozialistisch": ["CUB", "VEN"]}
COLORS = {"hoch koordiniert": "#001437", "koordinierte Marktwirtschaft": "#002060", "liberale Marktwirtschaft": "#5b9bd5",
          "europäische Peripherie": "#9dc3e6", "fortgeschrittene Schwellenländer": "#f4b183", "fortgeschrittene Stadtstaaten": "#ffd966",
          "arabische Ölstaaten": "#c55a11", "Schwellenländer": "#c00000", "sozialistisch": "#7f0000", "nicht erfasst": "#d9d9d9"}


def distance_matrix(raw):
    m = json.load(open(raw / "witt" / "witt_matrix.json"))
    rows = []
    for k, c in enumerate(m["order"]):
        for j, v in enumerate(m["rows"][c]):
            a, b = ISO[c], ISO[m["order"][j]]
            rows += [(a, b, v), (b, a, v)]
    return pd.DataFrame(rows, columns=["exporter", "importer", "inst_dist"])


def main():
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "business_systems"
    out.mkdir(parents=True, exist_ok=True)
    cl = {c: k for k, v in CLUSTERS.items() for c in v}
    assert len(cl) == 61
    idm = distance_matrix(raw)
    xl = {}

    # A: trade shares by type
    m56 = importlib.import_module("56_trade_by_regime")
    t = m56.imf_values(raw / "imts")
    t = t[t.partner != t.reporter]
    deu = t[(t.reporter == "DEU")].assign(who="DEU")
    eu = t[t.reporter.isin(m56.EU) & ~t.partner.isin(m56.EU)].assign(who="EU27")
    f = pd.concat([deu, eu])
    f["type"] = f.partner.map(cl).fillna("nicht erfasst")
    shares = {}
    for (who, flow), g in f.groupby(["who", "flow"]):
        s = g.groupby(["year", "type"]).value.sum().unstack(fill_value=0)
        s = s.div(s.sum(axis=1), axis=0)
        shares[(who, flow)] = s
        xl[f"{who}_{flow}"] = s.round(4)
    for who in ("DEU", "EU27"):
        s = shares[(who, "M")]
        print(f"{who} imports 2024 by type: " + ", ".join(f"{k} {v:.0%}" for k, v in s.loc[2024].sort_values(ascending=False).head(5).items()))
    dep = pd.read_csv(cfg["output"] / "scenarios" / "dependencies_hs6.csv")
    dep = dep[dep.dependent]
    dep["type"] = dep.top_supplier.map(cl).fillna("nicht erfasst")
    dd = dep.groupby(["level", "type"]).extra_imports.sum().unstack(0)
    dd = dd / dd.sum()
    xl["Abhaengigkeiten"] = dd.round(4)

    # B: gravity with institutional distance
    tr = pd.read_parquet(cfg["output"] / "scenarios" / "itpd_broad.parquet")
    tr = tr[(tr.broad_sector == "Manufacturing") & tr.year.between(2017, 2019)]
    tr = tr.groupby(["exporter", "importer"], as_index=False).trade.mean()
    c61 = set(cl)
    tr = tr[tr.exporter.isin(c61) & tr.importer.isin(c61) & (tr.exporter != tr.importer)]
    geo = pd.read_excel(raw / "witt" / "dist_cepii.xls").rename(columns={"iso_o": "exporter", "iso_d": "importer"})
    geo = geo.replace({"ROM": "ROU", "ZAR": "COD", "TMP": "TLS", "YUG": "SRB", "PAL": "PSE"})
    d = tr.merge(idm, on=["exporter", "importer"]).merge(geo[["exporter", "importer", "distw", "contig", "comlang_off", "colony"]],
                                                          on=["exporter", "importer"], how="left")
    with zipfile.ZipFile(raw / "rta_20260111_csv.zip") as z:
        r = pd.read_csv(z.open("rta_20260111.csv"), usecols=["exporter", "importer", "year", "rta"])
    d = d.merge(r[r.year == 2018].drop(columns="year"), on=["exporter", "importer"], how="left").fillna({"rta": 0})
    d["ln_dist"] = np.log(pd.to_numeric(d.distw, errors="coerce"))
    d["id_std"] = (d.inst_dist - d.inst_dist.mean()) / d.inst_dist.std()
    d["same_type"] = (d.exporter.map(cl) == d.importer.map(cl)).astype(int)
    d = d.dropna(subset=["ln_dist"])
    print(f"gravity sample: {len(d):,} pairs, {d.exporter.nunique()} countries")
    res = {}
    for name, rhs in (("geography only", "ln_dist + contig + comlang_off + colony + rta"),
                      ("with institutional distance", "id_std + ln_dist + contig + comlang_off + colony + rta"),
                      ("with same business system", "same_type + ln_dist + contig + comlang_off + colony + rta")):
        m = pf.fepois(f"trade ~ {rhs} | exporter + importer", data=d, vcov="hetero")
        res[name] = pd.DataFrame({"coef": m.coef(), "se": m.se()})
        print(name, {k: (round(v, 3), round(m.se()[k], 3)) for k, v in m.coef().items()})
        if name == "with institutional distance":
            d["pred"] = m.predict(type="response")
    tab = pd.concat(res, names=["model", "variable"]).reset_index()
    tab["effect_pct"] = (np.exp(tab.coef) - 1) * 100
    tab.round(4).to_csv(out / "gravity.csv", index=False)
    xl["Gravitation"] = tab.round(4)
    ge = d[d.exporter == "DEU"][["importer", "inst_dist", "trade", "pred"]].assign(type=lambda x: x.importer.map(cl))
    ge["actual_over_predicted"] = ge.trade / ge.pred
    ge.sort_values("inst_dist").round(4).to_csv(out / "germany_partners.csv", index=False)
    xl["Deutschland_Partner"] = ge.round(4)
    near = idm[idm.exporter == "DEU"].sort_values("inst_dist")
    print("closest to Germany:", near.head(6).round(2).values.tolist())

    # figures
    order = list(CLUSTERS) + ["nicht erfasst"]
    fig, axes = plt.subplots(2, 2, figsize=(15, 8.5), sharex=True, sharey=True)
    for a, (who, flow) in zip(axes.flat, [("DEU", "X"), ("DEU", "M"), ("EU27", "X"), ("EU27", "M")]):
        s = shares[(who, flow)] * 100
        o = [c for c in order if c in s.columns]
        a.stackplot(s.index, *[s[c] for c in o], colors=[COLORS[c] for c in o], labels=o)
        a.set_title(f"{'Deutschland' if who == 'DEU' else 'EU27, Handel mit Drittstaaten'}: {'Exporte' if flow == 'X' else 'Importe'}", loc="left", fontsize=10)
        a.set_ylim(0, 100); a.set_xlim(1990, 2024)
    axes[0, 0].legend(ncol=5, loc="lower left", bbox_to_anchor=(0, 1.12), frameon=False, fontsize=8)
    fig.suptitle("Handel nach Wirtschaftssystem der Partner (Witt u. a. 2018), Anteile in %", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Einstufung um 2013, für alle Jahre fest. Werte: IMF IMTS. Quelle: eigene Berechnungen.", fontsize=7)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.8, bottom=0.07, wspace=0.08, hspace=0.25)
    fig.savefig(out / "shares_by_type.png", dpi=200); plt.close(fig)
    fig, a = plt.subplots(figsize=(10, 6))
    for k, g in ge.groupby("type"):
        a.scatter(g.inst_dist, np.log(g.actual_over_predicted), color=COLORS[k], label=k, s=40)
        for r_ in g.itertuples():
            a.annotate(r_.importer, (r_.inst_dist, np.log(r_.actual_over_predicted)), fontsize=7, xytext=(3, 2), textcoords="offset points")
    a.axhline(0, color="#000", lw=0.5)
    a.set_xlabel("institutionelle Distanz zu Deutschland (Witt u. a. 2018)"); a.set_ylabel("log tatsächlich / Modell")
    a.set_title("Deutsche Industrieexporte 2017-2019: über (oben) oder unter dem Gravitationsmodell", loc="left", fontsize=10)
    a.legend(frameon=False, fontsize=7, ncol=2)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "germany_partners.png", dpi=200); plt.close(fig)
    with pd.ExcelWriter(out / "business_systems.xlsx") as w:
        pd.DataFrame({"Hinweis": ["Wirtschaftssysteme und institutionelle Distanz nach Witt u. a. (2018), Socio-Economic Review 16(1).",
                                  "Handel: IMF IMTS; Gravitation: ITPD-E Industrie 2017-2019, CEPII GeoDist, Larch RTA; PPML."]}).to_excel(w, sheet_name="Info", index=False)
        for k, v in xl.items():
            v.to_excel(w, sheet_name=k[:31])
        idm.pivot(index="exporter", columns="importer", values="inst_dist").to_excel(w, sheet_name="Distanzmatrix")


if __name__ == "__main__":
    main()
