"""US tariff exposure by labour market region (BBSR Arbeitsmarktregionen, 223 regions).

Districts are where plants are; labour market regions group districts by commuting, so they are
closer to where the workers who lose income live. Inputs: district losses of 74 (published data)
and 89 (with the 14 suppressed districts imputed), INKAR 2025 district rows, BBSR Raumgliederungen
Referenz 2023 (sheet Kreisreferenz, KAM2023 = labour market region of each district), GRW shares (80).
Aggregation: losses and sales are summed; indicators are rebuilt from district totals (GDP, population
15-64, industry employees, unemployed via rate x labour force proxy = population-weighted rates).
Results: concentration (share of the most exposed fifth of regions), top regions, Spearman correlations
with the profile, GRW shares, and the change against the district level.
Writes <output>/kreise/amr_us_tariffs.csv, amr_summary.json, paper/figures_regional/fig5_amr_map.png,
site data kreise_amr.json (value of each district's labour market region, by NUTS 3 code).
Usage: python 90_amr.py [site_data_folder]
"""
import importlib
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import regional as rg
from config import load_config

i79 = importlib.import_module("79_inkar_analyses")
BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]


def top_share(loss, pop, k=0.2):
    lpc = loss / pop
    s = loss[lpc.sort_values(ascending=False).index]
    n = int(round(k * len(s)))
    return float(s.iloc[:n].sum() / s.sum())


def main(site=None):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    ref = pd.read_excel(cfg["data"]["scenarios"] / "inkar" / "BBSR_Raumgliederungen_Referenz_2023.xlsx", sheet_name="Kreisreferenz",
                        dtype={"KRS2023": str, "KAM2023": str}).iloc[1:]
    ref["ags"] = ref.KRS2023.str.zfill(8).str[:5]
    amr = ref.set_index("ags")[["KAM2023", "KAM_NAME"]].rename(columns={"KAM2023": "amr", "KAM_NAME": "amr_name"})
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    imp = pd.read_csv(out / "us_tariffs_kreise_imputed.csv", dtype={"ags": str}).set_index("ags")
    grw = pd.read_csv(out / "grw_kreise.csv", dtype={"ags": str}).set_index("ags")
    d = i79.load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    g = lambda n, y=None: i79.get(d, n, y).reindex(u.index)
    k = u[["name", "nuts3", "pop", "loss_mio", "umsatz_mio_2024"]].join(amr)
    assert k.amr.notna().all(), "district without labour market region"
    k["loss_imp"] = imp.loss_mio.reindex(k.index)
    k["sales_imp"] = imp.umsatz_mio_2024.reindex(k.index)
    k["gdp"] = g("Bruttoinlandsprodukt in 1000 Euro", 2022)
    k["wa"] = g("Erwerbsfähige Bevölkerung (15 bis unter 65 Jahre)", 2023)
    k["ind"] = g("Industriequote", 2023) / 100 * k.wa
    k["wa_ind"] = k.wa.where(k.ind.notna())                # working-age population where the industry rate is published
    k["alq_w"] = g("Arbeitslosenquote") * k.wa
    k["inc_w"] = g("Medianeinkommen") * k.wa
    k["c_pop"], k["cd_pop"] = grw.share_c.reindex(k.index) * k["pop"], grw.share_cd.reindex(k.index) * k["pop"]
    k["gwst"] = g("Gewerbesteuer", 2023) * k["pop"]
    k["stk"] = g("Steuerkraft", 2023) * k["pop"]
    k["complete"] = k.loss_mio.notna()
    s = lambda c: k.groupby("amr")[c].sum(min_count=1)
    a = pd.DataFrame({"name": k.groupby("amr").amr_name.first(), "districts": k.groupby("amr").size(),
                      "complete": k.groupby("amr").complete.all(), "pop": s("pop"), "loss_mio": s("loss_mio"),
                      "loss_imp": s("loss_imp"), "sales": s("umsatz_mio_2024"), "sales_imp": s("sales_imp")})
    a["loss_pc"] = a.loss_mio * 1e6 / a["pop"]
    a["loss_pc_imp"] = a.loss_imp * 1e6 / a["pop"]
    a["dm_imp"] = -100 * a.loss_imp / a.sales_imp
    a["gdp_pc"] = s("gdp") / a["pop"]                       # EUR thousand per inhabitant
    a["iq"] = 100 * s("ind") / s("wa_ind")
    a["alq"] = s("alq_w") / s("wa")
    a["inc"] = s("inc_w") / s("wa")
    a["share_c"], a["share_cd"] = s("c_pop") / a["pop"], s("cd_pop") / a["pop"]
    a["gwst_share"] = 100 * s("gwst") / s("stk")
    # main measure: with imputed districts (every region complete); published-only regions as a check
    v = a.dropna(subset=["loss_pc_imp"])
    rho = {c: float(v.loss_pc_imp.corr(v[c], method="spearman")) for c in ("iq", "gdp_pc", "inc", "alq", "gwst_share")}
    q = pd.qcut(v.loss_pc_imp, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    w = lambda x, c: float(np.average(x[c].dropna(), weights=x["pop"][x[c].notna()]))
    quint = [{"q": int(i), "n": len(x), "loss_pc": w(x, "loss_pc_imp"), "gdp_pc": w(x, "gdp_pc"), "iq": w(x, "iq"), "alq": w(x, "alq"),
              "share_c": 100 * w(x, "share_c"), "share_cd": 100 * w(x, "share_cd")} for i, x in v.groupby(q)]
    kd = imp.dropna(subset=["loss_mio"])
    summ = {"n_amr": len(a), "loss_bn_imp": float(v.loss_imp.sum() / 1000),
            "top_fifth_share_amr": top_share(v.loss_imp, v["pop"]), "top_fifth_share_kreise": top_share(kd.loss_mio, kd["pop"]),
            "top_fifth_share_kreise_published": top_share(u.loss_mio.dropna(), u["pop"][u.loss_mio.notna()]),
            "cv_amr": float(v.loss_pc_imp.std() / v.loss_pc_imp.mean()),
            "cv_kreise": float((kd.loss_mio / kd["pop"]).std() / (kd.loss_mio / kd["pop"]).mean()),
            "median_amr": float(v.loss_pc_imp.median()), "rho": rho,
            "rho_published_complete": float(a[a.complete].loss_pc.corr(a[a.complete].loss_pc_imp, method="spearman")),
            "loss_share_c": float((v.loss_imp * v.share_c).sum() / v.loss_imp.sum()),
            "loss_share_cd": float((v.loss_imp * v.share_cd).sum() / v.loss_imp.sum()),
            "by_quintile": quint,
            "top": [[r["name"], int(r.districts), round(r.loss_pc_imp), round(r.dm_imp, 2), round(100 * r.share_c)] for _, r in v.sort_values("loss_pc_imp", ascending=False).head(15).iterrows()]}
    print(json.dumps({x: y for x, y in summ.items() if x not in ("top", "by_quintile")}, indent=1))
    print(pd.DataFrame(quint).round(1).to_string(index=False))
    print("top regions:", summ["top"][:12])
    a.round(4).to_csv(out / "amr_us_tariffs.csv")
    (out / "amr_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")

    # map: each district coloured by its labour market region
    shapes, _ = rg.load_nuts(cfg["data"]["scenarios"] / "regional" / "nuts3_2024_10m.geojson")
    de = {x: y for x, y in shapes.items() if x.startswith("DE")}
    val = {r.nuts3: a.loss_pc_imp[r.amr] for r in k.dropna(subset=["nuts3"]).itertuples()}
    bins = [0, 100, 250, 500, 1000, 2000, 1e9]
    fig, ax = plt.subplots(figsize=(5.4, 6.6))
    rg.choropleth(ax, de, val, bins, BLUE, extent=rg.EXTENT_DE, lw=0.0)
    from matplotlib.patches import Patch
    lab = [f"{bins[i]:.0f} to {bins[i + 1]:.0f}" for i in range(len(BLUE))]
    lab[0], lab[-1] = "below 100", "2000 and more"
    ax.legend(handles=[Patch(color=c) for c in BLUE], labels=lab, frameon=False, fontsize=7, loc="lower left",
              title="EUR per inhabitant", title_fontsize=8)
    fig.tight_layout()
    fig_dir = Path(__file__).resolve().parent / "paper" / "figures_regional"
    fig.savefig(fig_dir / "fig5_amr_map.png", dpi=200); plt.close(fig)
    if site:
        mp = {r.nuts3: {"amr": r.amr_name, "lpc": round(float(a.loss_pc_imp[r.amr]), 1)} for r in k.dropna(subset=["nuts3"]).itertuples()}
        p = Path(site) / "kreise_amr.json"
        p.write_text(json.dumps({"kreise": mp, "summary": {x: summ[x] for x in ("n_amr", "top_fifth_share_amr", "top_fifth_share_kreise", "rho")}},
                                ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(p.name, p.stat().st_size // 1024, "kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
