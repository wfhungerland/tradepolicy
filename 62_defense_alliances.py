"""Defence procurement and geopolitics in trade.

A. Kiel Military Procurement Tracker, 3rd release (Wolff et al. 2026; orders January 2020
   to January 2026): order value by origin of the supplier's headquarters for Germany,
   the UK and Poland (sheets A6, A13, A18): domestic only, domestic with foreign partner,
   other European, non-European.
B. Friend-shoring test in structural gravity (PPML, Yotov et al. 2016), goods trade
   ITPD-E 2010-2023 incl. domestic flows:
     X_ijt = exp(a_it + b_jt + g_ij + sum_p d_p (DIST_ij x P_t) + c ALLY_ijt + e RTA_ijt
                 + INTL_ijt x year)
   DIST_ij: distance of the two countries' UN General Assembly ideal points in 2015
   (Bailey, Strezhnev and Voeten 2017), standardised; P_t: 2018-2021 (US-China trade
   war, pandemic) and 2022-2023 (war in Ukraine), relative to 2010-2017. A negative d_p
   means that trade between politically distant countries fell relative to close pairs,
   as found by Gopinath et al. (2025) with bloc definitions. A second run uses blocs
   (different side of the US-China midpoint in 2015). Main sample: manufacturing (avoids
   the commodity price swings of 2021-2023 in mining and energy); all goods as a check.
   Note: on the UN scale the US is an outlier and China sits within the Global South, so
   the "blocs" separate the West from most other countries rather than two camps. ALLY: defence pact (ATOP 5.1,
   1815-2018, carried forward after 2018) or joint NATO membership (accession years
   entered by hand, including Montenegro 2017, North Macedonia 2020, Finland 2023).
Writes <output>/defense/*.csv, defense.png/pdf, defense.xlsx. Usage: python 62_defense_alliances.py
"""
import itertools
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyfixest as pf

from config import load_config

NATO = {**{c: 1949 for c in ["BEL", "CAN", "DNK", "FRA", "ISL", "ITA", "LUX", "NLD", "NOR", "PRT", "GBR", "USA"]},
        "GRC": 1952, "TUR": 1952, "DEU": 1955, "ESP": 1982, "CZE": 1999, "HUN": 1999, "POL": 1999,
        **{c: 2004 for c in ["BGR", "EST", "LVA", "LTU", "ROU", "SVK", "SVN"]}, "ALB": 2009, "HRV": 2009,
        "MNE": 2017, "MKD": 2020, "FIN": 2023, "SWE": 2024}
YEARS = range(2010, 2024)


def procurement(raw):
    x = pd.ExcelFile(raw / "defense" / "kiel_mpt_2026.xlsx")
    rows = []
    for sheet, buyer in (("A6 DE Orders by Origin", "DEU"), ("A13 UK Orders by Origin", "GBR"), ("A18 PL Orders by Origin", "POL")):
        d = pd.read_excel(x, sheet_name=sheet, header=None)
        hdr = d.index[d.iloc[:, 1].astype(str).eq("Month")][0]
        d.columns = d.iloc[hdr]
        d = d.iloc[hdr + 1:].dropna(subset=["Month"])
        d = d[pd.to_datetime(d.Month, errors="coerce").notna()]
        d["year"] = pd.to_datetime(d.Month).dt.year
        cols = [c for c in d.columns if c not in ("Month", "year") and isinstance(c, str)]
        g = d.groupby("year")[cols].sum().astype(float)
        g.columns = ["domestic", "domestic_with_foreign", "other_european", "non_european"]
        g["buyer"] = buyer
        rows.append(g.reset_index())
    p = pd.concat(rows)
    tot = p.groupby("buyer")[["domestic", "domestic_with_foreign", "other_european", "non_european"]].sum()
    return p, tot.div(tot.sum(axis=1), axis=0)


def alliances(raw, ideal):
    a = pd.read_csv(raw / "defense" / "atop" / "ATOP 5.1 (.csv)" / "atop5_1ddyr.csv", usecols=["year", "defense", "stateA", "stateB"])
    cow = ideal.drop_duplicates("ccode").set_index("ccode").iso
    a["i"], a["j"] = a.stateA.map(cow), a.stateB.map(cow)
    a = a[(a.defense == 1) & a.year.between(2010, 2018)].dropna(subset=["i", "j"])
    pairs = {}
    for y in YEARS:
        s = a[a.year == min(y, 2018)]
        pairs[y] = set(zip(s.i, s.j)) | set(zip(s.j, s.i))
        nat = [c for c, yy in NATO.items() if yy <= y]
        pairs[y] |= set(itertools.permutations(nat, 2))
    return pairs


def main():
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "defense"
    out.mkdir(parents=True, exist_ok=True)
    proc, shares = procurement(raw)
    proc.round(3).to_csv(out / "procurement_by_origin.csv", index=False)
    print("procurement by origin of supplier, share of order value 2020 to January 2026:")
    print((shares * 100).round(1).to_string())

    ideal = pd.read_csv(raw / "vdem" / "un_ideal_2025.csv").rename(columns={"iso3c": "iso", "IdealPointFP": "p"})
    p15 = ideal[ideal.year == 2015].set_index("iso").p
    pu, pc = p15["USA"], p15["CHN"]
    side = ((p15 - pc) / (pu - pc) >= 0.5).astype(int)
    T = pd.read_parquet(cfg["output"] / "scenarios" / "itpd_broad.parquet")
    T = T[T.year.isin(YEARS)]
    res = {}
    for sample, secs in (("manufacturing", ["Manufacturing"]), ("all goods", ["Agriculture", "Mining and Energy", "Manufacturing"])):
        t = T[T.broad_sector.isin(secs)].groupby(["exporter", "importer", "year"], as_index=False).trade.sum()
        res.update(estimate(t, p15, side, raw, ideal, sample))
    tab = pd.concat(res, names=["model", "variable"]).reset_index()
    tab = tab[~tab.variable.str.startswith("intl")]
    tab["effect_pct"] = (np.exp(tab.coef) - 1) * 100
    tab.round(4).to_csv(out / "friendshoring.csv", index=False)
    figures(out, shares, proc, tab)


def estimate(t, p15, side, raw, ideal, sample):
    dom = set(t[t.exporter == t.importer].exporter)
    keep = dom & set(p15.index)
    t = t[t.exporter.isin(keep) & t.importer.isin(keep)].copy()
    intl = t.exporter != t.importer
    dist = (t.exporter.map(p15) - t.importer.map(p15)).abs()
    t["dist"] = np.where(intl, (dist - dist[intl].mean()) / dist[intl].std(), 0)
    t["cross"] = np.where(intl, (t.exporter.map(side) != t.importer.map(side)).astype(int), 0)
    t["p1"] = t.year.between(2018, 2021).astype(int)
    t["p2"] = (t.year >= 2022).astype(int)
    for v in ("dist", "cross"):
        t[f"{v}_p1"], t[f"{v}_p2"] = t[v] * t.p1, t[v] * t.p2
    al = alliances(raw, ideal)
    t["ally"] = [int(intl_ and (i, j) in al[y]) for i, j, y, intl_ in zip(t.exporter, t.importer, t.year, intl)]
    with zipfile.ZipFile(raw / "rta_20260111_csv.zip") as z:
        r = pd.read_csv(z.open("rta_20260111.csv"), usecols=["exporter", "importer", "year", "rta"])
    t = t.merge(r[r.year.isin(YEARS)], on=["exporter", "importer", "year"], how="left")
    t["rta"] = t.rta.fillna(0)
    for y in YEARS[1:]:
        t[f"intl_{y}"] = (intl & (t.year == y)).astype(int)
    t["it"], t["jt"], t["ij"] = t.exporter + t.year.astype(str), t.importer + t.year.astype(str), t.exporter + t.importer
    t = t[t.groupby("ij").trade.transform("sum") > 0]
    border = " + ".join(f"intl_{y}" for y in YEARS[1:])
    print(f"{sample}: {len(t):,} observations, {t.exporter.nunique()} countries")
    res = {}
    for name, rhs in (("distance", "dist_p1 + dist_p2"), ("blocs", "cross_p1 + cross_p2")):
        m = pf.fepois(f"trade ~ {rhs} + ally + rta + {border} | it + jt + ij", data=t, vcov={"CRV1": "ij"})
        res[f"{name}, {sample}"] = pd.DataFrame({"coef": m.coef(), "se": m.se()})
        print(sample, name, {k: (round(m.coef()[k], 3), round(m.se()[k], 3)) for k in m.coef().index if not k.startswith("intl")})
    return res


def figures(out, shares, proc, tab):

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    cols = {"domestic": "#002060", "domestic_with_foreign": "#5b9bd5", "other_european": "#a6a6a6", "non_european": "#c00000"}
    lab = {"domestic": "nur heimische Firmen", "domestic_with_foreign": "heimisch mit ausländischem Partner",
           "other_european": "andere europäische Länder", "non_european": "außereuropäisch"}
    names = {"DEU": "Deutschland", "GBR": "Vereinigtes Königreich", "POL": "Polen"}
    left = np.zeros(len(shares))
    for c in cols:
        axes[0].barh([names[b] for b in shares.index], shares[c] * 100, left=left, color=cols[c], label=lab[c])
        left += shares[c].to_numpy() * 100
    axes[0].set_xlim(0, 100); axes[0].invert_yaxis()
    axes[0].set_title("Rüstungsaufträge 2020 bis Januar 2026 nach Sitz des Lieferanten, in %", loc="left", fontsize=10)
    axes[0].legend(ncol=2, frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0, -0.08))
    b = tab[tab.model == "blocs, manufacturing"].set_index("variable")
    for k, (v, l) in enumerate((("cross_p1", "2018-2021"), ("cross_p2", "2022-2023"))):
        axes[1].bar(k, b.effect_pct[v], color="#c00000", yerr=[[b.effect_pct[v] - (np.exp(b.coef[v] - 1.96 * b.se[v]) - 1) * 100],
                                                              [(np.exp(b.coef[v] + 1.96 * b.se[v]) - 1) * 100 - b.effect_pct[v]]], capsize=4)
        axes[1].text(k, 0.5, f"{b.effect_pct[v]:+.1f} %", ha="center", va="bottom", fontsize=9)
    axes[1].axhline(0, color="#000", lw=0.5); axes[1].set_xticks([0, 1], ["2018-2021", "2022-2023"])
    axes[1].set_title("Industriegüterhandel zwischen USA-nahen und übrigen Ländern (UN 2015)\nrelativ zum Handel innerhalb der Gruppen, ggü. 2010-2017, in %", loc="left", fontsize=10)
    for a in axes:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.suptitle("Rüstung und Geopolitik im Handel", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quellen: Kiel Military Procurement Tracker, 3. Release (Wolff u. a. 2026); USITC ITPD-E 2025; UN-Idealpunkte "
             "(Bailey, Strezhnev und Voeten 2017); ATOP 5.1; Larch RTA; eigene PPML-Schätzung mit Paar-, Exporteur-Jahr- und Importeur-Jahr-Effekten.", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(out / "defense.png", dpi=200); fig.savefig(out / "defense.pdf"); plt.close(fig)
    with pd.ExcelWriter(out / "defense.xlsx") as w:
        (shares * 100).round(1).to_excel(w, sheet_name="Beschaffung_Herkunft")
        proc.round(3).to_excel(w, sheet_name="Beschaffung_Jahre", index=False)
        tab.round(4).to_excel(w, sheet_name="Friendshoring", index=False)


if __name__ == "__main__":
    main()
