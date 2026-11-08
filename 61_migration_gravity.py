"""Migration networks and trade: a structural gravity estimate with diaspora stocks.

Data: UN DESA International Migrant Stock 2024 (bilateral, by destination and origin,
1990, 1995, ..., 2020, 2024; UN M49 codes mapped to ISO3 with the BACI country table),
USITC ITPD-E release 2025 (goods: agriculture, mining, manufacturing, incl. domestic
flows; 2023 is used with the 2024 stocks), Larch regional trade agreements (RTA).

Model (PPML, Yotov et al. 2016; Fally 2015):
  X_ijt = exp(a_it + b_jt + g_ij + beta1 ln(1 + M_ijt) + beta2 ln(1 + M_jit) + c RTA_ijt
              + sum_t d_t INTL_ijt)
M_ijt: people born in exporter i living in importer j ("diaspora of the exporter"),
M_jit: people born in j living in i ("immigrants from the importer in the exporter").
Pair fixed effects absorb distance, language and colonial ties; beta is identified from
changes in migrant stocks within a pair over time. Domestic flows identify the border
trend (INTL x year). Stocks of zero are kept through ln(1 + M).
Literature: meta-analysis of Genc et al. (2012): elasticities of trade with respect to
migrant stocks average about 0.1 to 0.2; with pair fixed effects estimates are smaller.
Writes <output>/migration/*.csv, migration.png/pdf, migration.xlsx.
Usage: python 61_migration_gravity.py
"""
import zipfile

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyfixest as pf

from config import load_config

YEARS = {1990: 1990, 1995: 1995, 2000: 2000, 2005: 2005, 2010: 2010, 2015: 2015, 2020: 2020, 2024: 2023}


def migrant_stocks(raw, baci):
    x = pd.read_excel(raw / "migration" / "ims2024.xlsx", sheet_name="Table 1", header=10)
    x = x.rename(columns={x.columns[4]: "dest", x.columns[6]: "orig"})
    years = [c for c in x.columns[7:15]]
    d = x[["dest", "orig"] + years].copy()
    d.columns = ["dest", "orig"] + [int(float(c)) for c in years]
    with zipfile.ZipFile(baci) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str, keep_default_na=False)
    iso = dict(zip(cc.country_code.astype(int), cc.country_iso3))
    iso.update({158: "TWN", 251: "FRA", 250: "FRA", 756: "CHE", 757: "CHE", 579: "NOR", 578: "NOR", 840: "USA", 842: "USA",
                699: "IND", 356: "IND"})
    d["dest"], d["orig"] = d.dest.map(iso), d.orig.map(iso)
    d = d.dropna(subset=["dest", "orig"])
    d = d[d.dest.str.fullmatch(r"[A-Z]{3}") & d.orig.str.fullmatch(r"[A-Z]{3}") & (d.dest != d.orig)]
    m = d.melt(id_vars=["orig", "dest"], var_name="year", value_name="stock")
    m["stock"] = pd.to_numeric(m.stock, errors="coerce").fillna(0)
    return m.groupby(["orig", "dest", "year"], as_index=False).stock.sum()


def main():
    cfg = load_config()
    raw = cfg["data"]["scenarios"]
    out = cfg["output"] / "migration"
    out.mkdir(parents=True, exist_ok=True)
    ms = migrant_stocks(raw, raw / "baci92" / "BACI_HS92_V202601.zip")
    t = pd.read_parquet(cfg["output"] / "scenarios" / "itpd_broad.parquet")
    t = t[t.broad_sector.isin(["Agriculture", "Mining and Energy", "Manufacturing"]) & t.year.isin(YEARS.values())]
    t = t.groupby(["exporter", "importer", "year"], as_index=False).trade.sum()
    t["year"] = t.year.map({v: k for k, v in YEARS.items()})
    # countries in both sources and with domestic flows
    dom = set(t[t.exporter == t.importer].exporter)
    keep = dom & (set(ms.orig) | set(ms.dest))
    t = t[t.exporter.isin(keep) & t.importer.isin(keep)]
    d = t.merge(ms.rename(columns={"orig": "exporter", "dest": "importer", "stock": "m_ij"}), on=["exporter", "importer", "year"], how="left")
    d = d.merge(ms.rename(columns={"orig": "importer", "dest": "exporter", "stock": "m_ji"}), on=["exporter", "importer", "year"], how="left")
    d[["m_ij", "m_ji"]] = d[["m_ij", "m_ji"]].fillna(0)
    intl = d.exporter != d.importer
    d["ln_mij"] = np.where(intl, np.log1p(d.m_ij), 0)
    d["ln_mji"] = np.where(intl, np.log1p(d.m_ji), 0)
    with zipfile.ZipFile(raw / "rta_20260111_csv.zip") as z:
        r = pd.read_csv(z.open("rta_20260111.csv"), usecols=["exporter", "importer", "year", "rta"])
    r = r[r.year.isin(YEARS.values())]
    r["year"] = r.year.map({v: k for k, v in YEARS.items()})
    d = d.merge(r, on=["exporter", "importer", "year"], how="left")
    d["rta"] = d.rta.fillna(0)
    for y in sorted(YEARS)[1:]:
        d[f"intl_{y}"] = (intl & (d.year == y)).astype(int)
    d["it"] = d.exporter + "_" + d.year.astype(str)
    d["jt"] = d.importer + "_" + d.year.astype(str)
    d["ij"] = d.exporter + "_" + d.importer
    # drop pairs that never trade (no information with pair fixed effects)
    d = d[d.groupby("ij").trade.transform("sum") > 0]
    print(f"{len(d):,} observations, {d.exporter.nunique()} countries, years {sorted(d.year.unique())}")
    border = " + ".join(f"intl_{y}" for y in sorted(YEARS)[1:])
    res = {}
    for name, rhs, fe in (("pair FE", f"ln_mij + ln_mji + rta + {border}", "it + jt + ij"),
                          ("pair FE, exporter diaspora only", f"ln_mij + rta + {border}", "it + jt + ij")):
        m = pf.fepois(f"trade ~ {rhs} | {fe}", data=d, vcov={"CRV1": "ij"})
        co, se = m.coef(), m.se()
        res[name] = pd.DataFrame({"coef": co, "se": se})
        print(name, {k: (round(co[k], 3), round(se[k], 3)) for k in co.index if k.startswith(("ln_", "rta"))})
    # cross-section (2020) without pair FE, as in much of the literature: distance proxied by pair-level controls
    # is not available here, so this run keeps exporter and importer effects only and is reported for comparison
    cs = d[(d.year == 2020) & (d.exporter != d.importer)]
    m = pf.fepois("trade ~ ln_mij + ln_mji + rta | exporter + importer", data=cs, vcov="hetero")
    res["cross-section 2020, no distance"] = pd.DataFrame({"coef": m.coef(), "se": m.se()})
    print("cross-section 2020 (no distance control)", m.coef().round(3).to_dict())
    tab = pd.concat(res, names=["model", "variable"]).reset_index()
    tab.round(4).to_csv(out / "estimates.csv", index=False)

    # Germany: diaspora networks and implied trade effect of the main model
    b1, b2 = res["pair FE"].coef["ln_mij"], res["pair FE"].coef["ln_mji"]
    g = ms[ms.year == 2024]
    abroad = g[g.orig == "DEU"].set_index("dest").stock.rename("germans_abroad")
    inde = g[g.dest == "DEU"].set_index("orig").stock.rename("immigrants_in_germany")
    net = pd.concat([abroad, inde], axis=1).fillna(0)
    # level effects relative to zero migrants would extrapolate far outside the data; only changes are reported
    net = net.sort_values("immigrants_in_germany", ascending=False)
    net.round(1).to_csv(out / "germany_networks.csv")
    print(net.head(12).round(0).to_string())
    # change 2015 -> 2024: implied effect of the rise in immigration on German imports and exports
    g15 = ms[(ms.year == 2015) & (ms.dest == "DEU")].set_index("orig").stock
    ch = pd.DataFrame({"2015": g15, "2024": inde}).fillna(0)
    ch["imports_pct"] = (np.exp(b1 * (np.log1p(ch["2024"]) - np.log1p(ch["2015"]))) - 1) * 100
    ch["exports_pct"] = (np.exp(b2 * (np.log1p(ch["2024"]) - np.log1p(ch["2015"]))) - 1) * 100
    ch = ch.sort_values("2024", ascending=False)
    ch.round(2).to_csv(out / "germany_change_2015_2024.csv")
    print(ch.head(10).round(1).to_string())

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    top = net.head(15)
    axes[0].barh(top.index, top.immigrants_in_germany / 1e6, color="#002060", label="in Deutschland lebend, geboren in")
    axes[0].barh(top.index, -top.germans_abroad / 1e6, color="#a6a6a6", label="in Deutschland geboren, lebend in")
    axes[0].invert_yaxis(); axes[0].axvline(0, color="#000", lw=0.5)
    axes[0].set_title("Migrantenbestände 2024, Mio. Personen", loc="left", fontsize=10)
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    est = tab[tab.variable.isin(["ln_mij", "ln_mji"])]
    lab = {"ln_mij": "Diaspora des Exportlands im Importland", "ln_mji": "Zuwanderer aus dem Importland im Exportland"}
    yy = np.arange(len(est))
    axes[1].errorbar(est.coef, yy, xerr=1.96 * est.se, fmt="o", color="#002060")
    axes[1].set_yticks(yy, [f"{lab[v]}\n({mo})" for mo, v in zip(est.model, est.variable)], fontsize=7)
    axes[1].axvline(0, color="#000", lw=0.5); axes[1].axvspan(0.1, 0.2, color="#e7e6e6", zorder=0)
    axes[1].set_title("Elastizität des Handels bezüglich Migrantenbestand (95-%-Intervall);\ngrau: Bereich der Metaanalyse von Genc u. a. (2012)", loc="left", fontsize=10)
    for a in axes:
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.suptitle("Migration und Handel", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quellen: UN DESA International Migrant Stock 2024; USITC ITPD-E 2025; Larch RTA; eigene PPML-Schätzung.", fontsize=7)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(out / "migration.png", dpi=200); fig.savefig(out / "migration.pdf"); plt.close(fig)
    with pd.ExcelWriter(out / "migration.xlsx") as w:
        tab.round(4).to_excel(w, sheet_name="Schaetzungen", index=False)
        net.round(1).to_excel(w, sheet_name="Deutschland_Netzwerke")
        ch.round(2).to_excel(w, sheet_name="Deutschland_2015_2024")


if __name__ == "__main__":
    main()
