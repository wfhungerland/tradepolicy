"""Subsidies worldwide and their overlap with German exports and with Chinese competition.

Data: Global Trade Alert (GTA), full export of the database downloaded by the user
(interventions.csv, November 2026). Subsidies = MAST chapters L (subsidies excl. export
subsidies) and P (export-related measures incl. export subsidies), evaluated by GTA as
harmful to foreign commercial interests (red or amber). An intervention with several
implementing jurisdictions counts for each of them. Targeted interventions (not horizontal, at most
50 HS 6-digit products listed) count at product level; broad schemes are excluded there.
Interventions list affected HS 6-digit products (HS 2012/2017); they are matched to the HS92 codes of
50_china_competition.py at 6 digits (codes that changed between revisions are missed).
Outputs in <output>/subsidies: subsidies_by_year.csv, subsidies_german_exports.csv,
subsidies_china_exposed.csv, subsidies.png; site data subsidies.json.
Usage: python 75_subsidies.py [site_data_folder]
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import load_config

EU = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
      "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal", "Romania",
      "Slovakia", "Slovenia", "Spain", "Sweden", "European Union"]
MAXP = 50                                 # targeted subsidy: at most 50 HS 6-digit products, not horizontal
GROUP = lambda j: "China" if j == "China" else "USA" if j == "United States of America" else "Deutschland" if j == "Germany" else "übrige EU" if j in EU else "übrige Welt"


def main(site=None):
    cfg = load_config()
    out = cfg["output"] / "subsidies"
    out.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(cfg["data"]["scenarios"] / "gta" / "interventions.csv", low_memory=False)
    s = d[d["Mast Chapter"].str[:2].isin(["L:", "P:"]) & d["GTA Evaluation"].isin(["Red", "Amber"])].copy()
    s["year"] = pd.to_numeric(s["Date Announced"].str[:4], errors="coerce")
    s = s.assign(impl=s["Implementing Jurisdictions"].str.split(r",\s*")).explode("impl")
    s["group"] = s.impl.map(GROUP)
    print(f"harmful subsidy interventions: {s['Intervention ID'].nunique():,}; in force {s[s['Is In Force'] == 1]['Intervention ID'].nunique():,}")
    print("top implementers:", s.impl.value_counts().head(8).to_dict())
    yr = s[s.year.between(2009, 2025)].pivot_table(index="year", columns="group", values="Intervention ID", aggfunc="nunique", fill_value=0)
    yr.to_csv(out / "subsidies_by_year.csv")
    print(yr.loc[[2009, 2015, 2020, 2025]].to_string())
    # product-level: in-force, product-specific subsidies by implementer group
    p = s[(s["Is In Force"] == 1) & s["Affected Products"].notna() & (s["Is Horizontal"].astype(str) != "True")][["Intervention ID", "group", "Affected Products"]].drop_duplicates()
    cnt = {}                                                      # (hs, group) -> number of interventions
    for iid, g, prods in p.itertuples(index=False):
        hs = set(x.strip().zfill(6) for x in str(prods).split(","))
        if len(hs) > MAXP:                                        # broad schemes (export credit, tax relief) are not targeted
            continue
        for h in hs:
            if len(h) == 6 and h.isdigit():
                cnt[(h, g)] = cnt.get((h, g), 0) + 1
    n = pd.Series(cnt).unstack(fill_value=0)
    c = pd.read_csv(cfg["output"] / "scenarios" / "china_competition_hs6.csv", dtype={"hs92": str}).set_index("hs92")
    c = c.join(n, how="left").fillna({g: 0 for g in n.columns})
    w = c.deu_exports_bn
    rows = []
    for g in ["China", "USA", "übrige EU", "Deutschland", "übrige Welt"]:
        rows.append({"gruppe": g, "share_de_exports": float(w[c[g] > 0].sum() / w.sum()), "n_products": int((c[g] > 0).sum())})
    anyf = (c[["China", "USA", "übrige EU", "übrige Welt"]] > 0).any(axis=1)
    rows.append({"gruppe": "irgendein Land außer DE", "share_de_exports": float(w[anyf].sum() / w.sum()), "n_products": int(anyf.sum())})
    ge = pd.DataFrame(rows)
    ge.to_csv(out / "subsidies_german_exports.csv", index=False)
    print("share of German exports (value) in products with in-force harmful subsidies:\n", ge.round(3).to_string(index=False))
    ex = c.exposed.fillna(False).astype(bool)
    cmp_ = pd.DataFrame({"gruppe": ["unter chinesischem Preisdruck", "übrige Waren"],
                         "share_with_cn_subsidy": [float((c.China[ex] > 0).mean()), float((c.China[~ex] > 0).mean())],
                         "share_value_with_cn_subsidy": [float(w[ex & (c.China > 0)].sum() / w[ex].sum()), float(w[~ex & (c.China > 0)].sum() / w[~ex].sum())],
                         "mean_cn_subsidies": [float(c.China[ex].mean()), float(c.China[~ex].mean())],
                         "n": [int(ex.sum()), int((~ex).sum())]})
    cmp_.to_csv(out / "subsidies_china_exposed.csv", index=False)
    print(cmp_.round(3).to_string(index=False))
    top = c[ex & (c.China > 0)].sort_values("deu_exports_bn", ascending=False).head(12)[["name_en", "deu_exports_bn", "China", "price_gap_log"]]
    print(top.round(2).to_string())
    # figure
    cols = {"China": "#C00000", "USA": "#002060", "Deutschland": "#000000", "übrige EU": "#0070C0", "übrige Welt": "#a6a6a6"}
    fig, (a, b) = plt.subplots(1, 2, figsize=(14, 5.5))
    for g in ["übrige Welt", "übrige EU", "Deutschland", "USA", "China"]:
        a.plot(yr.index, yr[g], color=cols[g], lw=2.2 if g in ("China", "USA") else 1.4, label=g)
    a.set_title("Schädliche Subventionen, neu angekündigte Maßnahmen je Jahr", loc="left", fontsize=10); a.legend(frameon=False, fontsize=8)
    a.spines[["top", "right"]].set_visible(False)
    g2 = ge.iloc[::-1]
    b.barh(g2.gruppe, 100 * g2.share_de_exports, color=["#595959", "#a6a6a6", "#000000", "#0070C0", "#002060", "#C00000"][:len(g2)][::-1])
    for i, v in enumerate(100 * g2.share_de_exports):
        b.text(v + 1, i, f"{v:.0f} %", va="center", fontsize=8)
    b.set_title("Anteil der deutschen Exporte in Waren mit geltender Subvention, %", loc="left", fontsize=10)
    b.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Subventionen im Welthandel (Global Trade Alert)", x=0.01, ha="left", fontsize=12)
    fig.text(0.01, 0.01, "Quelle: eigene Berechnungen auf Basis von Global Trade Alert (Kapitel L und P, rot/gelb bewertet, Stand November 2026) und CEPII BACI. "
             "Rechts: nur gezielte Maßnahmen in Kraft (höchstens 50 Warencodes); deutsche Exporte 2024 nach HS 6.", fontsize=7)
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(out / "subsidies.png", dpi=150); plt.close(fig)
    if site:
        j = {"years": yr.index.astype(int).tolist(), "by_year": {g: yr[g].astype(int).tolist() for g in yr.columns},
             "de_exports": ge.to_dict("records"), "china_exposed": cmp_.to_dict("records"),
             "top": [{"hs": h, "name": r.name_en, "deu_bn": round(r.deu_exports_bn, 2), "n_cn": int(r.China)} for h, r in top.iterrows()],
             "n_total": int(s["Intervention ID"].nunique()), "n_force": int(s[s["Is In Force"] == 1]["Intervention ID"].nunique())}
        f = Path(site) / "subsidies.json"
        f.write_text(json.dumps(j, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f.name, f.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
