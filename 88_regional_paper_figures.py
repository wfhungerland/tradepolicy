"""Figures for the working paper on US tariffs and German districts (paper/regional_paper.md).

Inputs from <output>/kreise: us_tariffs_kreise.csv (74), inkar_analyses_kreise.csv (79),
gewerbesteuer_elasticity.csv (87); NUTS 2024 district geometries.
  fig1_map.png          manufacturing output change (%) and loss per inhabitant by district
  fig2_concentration.png cumulative share of the loss over districts ranked by loss per inhabitant
  fig3_industry.png     loss per inhabitant against industry employment rate
  fig4_elasticity.png   elasticity of local business tax to manufacturing sales, all models, 95 % intervals
Writes to paper/figures_regional/ (in the repository, small PNG files).
Usage: python 88_regional_paper_figures.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import regional as rg
from config import load_config

INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]   # sequential, light to dark
S1, S2 = "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})


def style(ax):
    ax.grid(axis="both", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def main():
    cfg = load_config()
    out = cfg["output"] / "kreise"
    fig_dir = Path(__file__).resolve().parent / "paper" / "figures_regional"
    fig_dir.mkdir(parents=True, exist_ok=True)
    u = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    m = pd.read_csv(out / "inkar_analyses_kreise.csv", dtype={"ags": str}).set_index("ags")
    v = u.dropna(subset=["dm"])

    # 1 maps
    shapes, _ = rg.load_nuts(cfg["data"]["scenarios"] / "regional" / "nuts3_2024_10m.geojson")
    de = {g: s for g, s in shapes.items() if g.startswith("DE")}
    y = v.set_index("nuts3")
    fig, axes = plt.subplots(1, 2, figsize=(10, 6.6))
    specs = [("dm", [-99, -3, -2.5, -2, -1.5, -1, 99], BLUE[::-1], "{:.1f}", "a) Manufacturing output, change in %"),
             ("loss_pc", [0, 100, 250, 500, 1000, 2000, 1e9], BLUE, "{:.0f}", "b) Output loss per inhabitant, EUR")]
    for a, (c, bins, cols, fmt, t) in zip(axes, specs):
        rg.choropleth(a, de, y[c].to_dict(), bins, cols, extent=rg.EXTENT_DE, lw=0.15)
        from matplotlib.patches import Patch
        lab = [f"{fmt.format(bins[k])} to {fmt.format(bins[k + 1])}" for k in range(len(cols))]
        lab[0], lab[-1] = f"below {fmt.format(bins[1])}", f"{fmt.format(bins[-2])} and more"
        a.legend(handles=[Patch(color=x) for x in cols] + [Patch(color="#bfbfbf")], labels=lab + ["not published"],
                 frameon=False, fontsize=7, loc="lower left")
        a.set_title(t, fontsize=10, loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig1_map.png", dpi=200); plt.close(fig)

    # 2 concentration
    s = v.sort_values("loss_pc", ascending=False)
    cx = np.r_[0, np.arange(1, len(s) + 1) / len(s)]
    cp = np.r_[0, s["pop"].cumsum() / s["pop"].sum()]
    cl = np.r_[0, s.loss_mio.cumsum() / s.loss_mio.sum()]
    fig, ax = plt.subplots(figsize=(5.2, 4))
    style(ax)
    ax.plot(100 * cx, 100 * cl, color=S1, lw=2, label="districts")
    ax.plot(100 * cp, 100 * cl, color=S2, lw=2, label="population")
    ax.plot([0, 100], [0, 100], color=INK2, lw=0.8, ls=(0, (3, 3)))
    k = int(round(0.2 * len(s)))
    ax.plot([20], [100 * cl[k]], "o", ms=6, color=S1, mec="#fcfcfb", mew=2)
    ax.annotate(f"top fifth of districts: {100 * cl[k]:.0f} % of the loss", (20, 100 * cl[k]), xytext=(28, 42),
                fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
    ax.set_xlabel("Cumulative share, districts ranked by loss per inhabitant, %")
    ax.set_ylabel("Cumulative share of the output loss, %")
    ax.legend(frameon=False, loc="lower right", title="share of", title_fontsize=8)
    ax.set_xlim(0, 100); ax.set_ylim(0, 101)
    fig.tight_layout(); fig.savefig(fig_dir / "fig2_concentration.png", dpi=200); plt.close(fig)

    # 3 industry employment
    z = m.dropna(subset=["loss", "iq23"])
    rho = z[["loss", "iq23"]].corr(method="spearman").iloc[0, 1]
    fig, ax = plt.subplots(figsize=(5.2, 4))
    style(ax)
    ax.scatter(z.iq23, z.loss, s=14, color=S1, alpha=0.7, edgecolor="#fcfcfb", lw=0.4)
    ax.set_yscale("log")
    ax.set_xlabel("Industry employees per 100 inhabitants aged 15-64 (2023)")
    ax.set_ylabel("Output loss per inhabitant, EUR (log scale)")
    for nm in ("Regensburg, Stadt", "Ludwigshafen am Rhein, kreisfreie Stadt", "Wolfsburg, Stadt", "Jena, Stadt", "Oder-Spree"):
        r = z[z.name == nm]
        if len(r):
            ax.annotate(nm.split(",")[0].replace(" am Rhein", ""), (r.iq23.iloc[0], r.loss.iloc[0]), xytext=(4, 2),
                        textcoords="offset points", fontsize=7, color=INK2)
    ax.text(0.02, 0.97, f"Spearman rank correlation {rho:.2f}, {len(z)} districts", transform=ax.transAxes,
            fontsize=8, color=INK, va="top")
    fig.tight_layout(); fig.savefig(fig_dir / "fig3_industry.png", dpi=200); plt.close(fig)

    # 4 elasticities
    e = pd.read_csv(out / "gewerbesteuer_elasticity.csv")
    lab = {"levels": "Levels, district and year effects", "levels_popweighted": "Levels, population-weighted",
           "lags_sum": "First differences, sum of lags 0-2", "longdiff": "Long difference 2010-12 to 2021-23",
           "placebo_lead": "Same model: current year's sales", "tercile_1": "Least industrial third",
           "tercile_2": "Middle third", "tercile_3": "Most industrial third"}
    e = e[e.model.isin(lab)]
    pl = e[e.model == "placebo_lead"].iloc[0]
    rows = [(lab[r.model], r.b, r.se, S1) for r in e.itertuples()]
    i = [k for k, r in enumerate(e.model) if r == "placebo_lead"][0]
    rows.insert(i + 1, ("Placebo: next year's sales (same model)", pl.b_lead, pl.se_lead, S2))
    rows = rows[::-1]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    style(ax); ax.grid(axis="y", visible=False)
    yy = np.arange(len(rows))
    for y0, (_, b0, s0, c0) in zip(yy, rows):
        ax.errorbar([b0], [y0], xerr=[1.96 * s0], fmt="o", color=c0, ecolor=c0, elinewidth=2, ms=6, mec="#fcfcfb", mew=1.5)
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(yy, [r[0] for r in rows], fontsize=8)
    ax.set_xlabel("Elasticity of Gewerbesteuer per inhabitant\nto manufacturing sales per inhabitant (95 % interval)")
    ax.xaxis.label.set_size(8)
    fig.tight_layout(); fig.savefig(fig_dir / "fig4_elasticity.png", dpi=200); plt.close(fig)
    print("figures written to", fig_dir)


if __name__ == "__main__":
    main()
