"""What does the tariff structure add? Decomposition of the district loss and a uniform benchmark shock.

The loss per inhabitant of district k is the product of manufacturing intensity and tariff intensity:
  loss_k / pop_k = (U_k / pop_k) x s_k,   s_k = -dm_k / 100 (percentage output loss of 74).
Benchmark: a uniform shock that lowers manufacturing output in every district by the national average
(total loss / total sales, -1.65 %). Its loss per inhabitant ranks districts exactly like manufacturing
sales per inhabitant, so any difference to the tariff result comes from the tariff structure (industry mix
of the region and export ratio of the district).
Outputs:
  variance decomposition of ln(loss per inhabitant) into ln(sales per inhabitant) and ln(s);
  Spearman correlations of loss, intensity and tariff intensity with the INKAR profile and GRW status;
  OLS of unemployment, SGB II rate and log earnings on tariff intensity with density and Land effects;
  profile by quintile of tariff intensity s; GRW and top-fifth shares under the benchmark.
Writes <output>/kreise/decomposition.json and paper/figures_regional/fig6_decomposition.png.
Usage: python 91_decomposition.py
"""
import importlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import load_config

i79 = importlib.import_module("79_inkar_analyses")
INK, INK2, GRID, S1, S2 = "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#eb6834"


def main():
    cfg = load_config()
    out = cfg["output"] / "kreise"
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags").dropna(subset=["dm"])
    grw = pd.read_csv(out / "grw_kreise.csv", dtype={"ags": str}).set_index("ags").reindex(u.index)
    d = i79.load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    g = lambda n, y=None: i79.get(d, n, y).reindex(u.index)
    k = pd.DataFrame({"name": u.name, "pop": u["pop"], "loss_pc": u.loss_pc, "upc": u.umsatz_mio_2024 * 1e6 / u["pop"], "s": -u.dm,
                      "loss_mio": u.loss_mio, "sales": u.umsatz_mio_2024})
    sbar = k.loss_mio.sum() / k.sales.sum()                              # national average loss rate
    k["bench_pc"] = sbar * k.upc
    k["bench_mio"] = sbar * k.sales
    prof = pd.DataFrame({"iq": g("Industriequote", 2023), "gdp": g("Bruttoinlandsprodukt je Einwohner"), "inc": g("Medianeinkommen"),
                         "alq": g("Arbeitslosenquote"), "sgb2": g("SGB II - Quote"),
                         "prog": g("Prognostizierte Bevölkerungsentwicklung (2022-2045)"), "c": grw.share_c})
    lab = {"iq": "Industry employment", "gdp": "GDP per head", "inc": "Median earnings", "alq": "Unemployment rate",
           "sgb2": "SGB II rate", "prog": "Population projection 2045", "c": "Population share in GRW C areas"}
    rho = {m: {c: float(k[m].corr(prof[c], method="spearman")) for c in prof} for m in ("loss_pc", "upc", "s")}
    # variance decomposition of ln loss: cov(ln upc, ln loss)/var(ln loss) + cov(ln s, ln loss)/var(ln loss) = 1
    ll, lu, ls = np.log(k.loss_pc), np.log(k.upc), np.log(k.s)
    share_upc, share_s = float(np.cov(lu, ll)[0, 1] / ll.var()), float(np.cov(ls, ll)[0, 1] / ll.var())
    top = lambda loss, pc: float(loss[pc.sort_values(ascending=False).index[: int(round(0.2 * len(pc)))]].sum() / loss.sum())
    q = pd.qcut(k.s, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    w = lambda x, c: float(np.average(x[c].dropna(), weights=x["pop"][x[c].notna()]))
    kk = k.join(prof)
    by_s = [{"q": int(i), "n": len(x), "s": w(x, "s"), "upc": w(x, "upc") / 1000, "gdp": w(x, "gdp"), "inc": w(x, "inc"),
             "alq": w(x, "alq"), "sgb2": w(x, "sgb2"), "c": 100 * w(x, "c")} for i, x in kk.groupby(q)]
    res = {"sbar_pct": 100 * float(sbar), "s_range": [float(k.s.min()), float(k.s.median()), float(k.s.max())],
           "var_share_intensity": share_upc, "var_share_tariff": share_s,
           "rho_loss_bench": float(k.loss_pc.corr(k.bench_pc, method="spearman")), "rho": rho,
           "top_fifth_share": {"tariff": top(k.loss_mio, k.loss_pc), "benchmark": top(k.bench_mio, k.bench_pc)},
           "loss_share_c": {"tariff": float((k.loss_mio * prof.c).sum() / k.loss_mio.sum()),
                            "benchmark": float((k.bench_mio * prof.c).sum() / k.bench_mio.sum())},
           "loss_share_cd": {"tariff": float((k.loss_mio * grw.share_cd).sum() / k.loss_mio.sum()),
                             "benchmark": float((k.bench_mio * grw.share_cd).sum() / k.bench_mio.sum())},
           "by_tariff_quintile": by_s}
    # tariff intensity and weakness, within Länder and controlling for density (OLS, robust s.e.)
    import statsmodels.formula.api as smf
    z = kk.assign(ln_dens=np.log(g("Einwohnerdichte")), ln_inc=np.log(prof.inc), land=k.index.str[:2]).dropna(subset=["alq", "sgb2", "ln_inc"])
    res["reg_s"] = {}
    for y in ("alq", "sgb2", "ln_inc"):
        r = smf.ols(f"{y} ~ s + ln_dens + C(land)", data=z).fit(cov_type="HC1")
        res["reg_s"][y] = {"b": float(r.params["s"]), "se": float(r.bse["s"]), "p": float(r.pvalues["s"]), "n": int(r.nobs)}
    res["s_city_median"] = {"city": float(k.s[u.typ == "Kreisfreie Stadt"].median()), "rural": float(k.s[u.typ != "Kreisfreie Stadt"].median())}
    res["rho_s_density"] = float(k.s.corr(g("Einwohnerdichte"), method="spearman"))
    print("regressions of weakness on tariff intensity:", json.dumps(res["reg_s"]), res["s_city_median"], round(res["rho_s_density"], 2))
    pd.set_option("display.width", 200)
    print(json.dumps({x: y for x, y in res.items() if x not in ("rho", "by_tariff_quintile")}, indent=1))
    print(pd.DataFrame(rho).round(2))
    print(pd.DataFrame(by_s).round(2).to_string(index=False))
    (out / "decomposition.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

    # figure: Spearman correlations with the profile, loss vs. its two factors
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    cols = list(lab)
    y = np.arange(len(cols))[::-1]
    series = [("upc", "Manufacturing sales per inhabitant (uniform shock)", S1, 0.18),
              ("s", "Tariff intensity: % output loss", S2, -0.18)]
    for m, name, col, off in series:
        ax.scatter([rho[m][c] for c in cols], y + off, s=36, color=col, edgecolor="#fcfcfb", lw=1, zorder=3, label=name)
        for c, yy in zip(cols, y + off):
            ax.plot([0, rho[m][c]], [yy, yy], color=col, lw=2, zorder=2)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(y, [lab[c] for c in cols], fontsize=8)
    ax.set_xlabel("Spearman rank correlation across districts", fontsize=8)
    ax.set_xlim(-0.6, 0.9)
    ax.legend(frameon=False, fontsize=7, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=1)
    fig.tight_layout()
    fig.savefig(Path(__file__).resolve().parent / "paper" / "figures_regional" / "fig6_decomposition.png", dpi=200); plt.close(fig)


if __name__ == "__main__":
    main()
