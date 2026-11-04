"""Step 3: Germany against the large exporters, 1995-2024.

Reads the output of 02_complexity.py and writes tables (CSV) and figures (PNG)
to <output>/germany_<level>/.

Tables
  eci_focus.csv           ECI, rank, ECI with pooled PCI, diversity, COI by year
  eci_gap.csv             ECI of Germany minus ECI of each peer, by year
  pci_quintiles.csv       export shares by pooled-PCI quintile, by country and year
  export_pci.csv          export-weighted mean pooled PCI of each country's basket
  entries_exits.csv       products gained / lost between first and last year
  entries_exits_list.csv  Germany's gained and lost products with PCI and density
  relatedness_test.csv    entry probability by density decile (5-year steps)
  opportunities.csv       Germany's top products by Complexity Outlook Gain, last year
Usage: python 03_germany.py [hs4|hs6]
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import load_config

FOCUS_COLOR = "#2a78d6"
PEER_COLOR = "#b5b4ad"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
GRID = "#e6e5e0"
QUINTILE_COLORS = ["#cde2fb", "#86b6ef", "#5598e7", "#2a78d6", "#184f95"]

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": TEXT2, "axes.labelcolor": TEXT2, "xtick.color": TEXT2,
    "ytick.color": TEXT2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "font.size": 10, "figure.dpi": 150, "savefig.bbox": "tight",
})


def line_focus(df, value, focus, peers, title, ylabel, path, invert=False):
    """Germany highlighted, peers as thin grey lines with end labels."""
    fig, ax = plt.subplots(figsize=(8, 5))
    wide = df.pivot(index="year", columns="iso3", values=value)
    for p in peers:
        if p in wide:
            ax.plot(wide.index, wide[p], color=PEER_COLOR, lw=1.2)
            ax.annotate(p, (wide.index[-1], wide[p].iloc[-1]), xytext=(4, 0),
                        textcoords="offset points", va="center", fontsize=8, color=TEXT2)
    ax.plot(wide.index, wide[focus], color=FOCUS_COLOR, lw=2.2)
    ax.annotate(focus, (wide.index[-1], wide[focus].iloc[-1]), xytext=(4, 0),
                textcoords="offset points", va="center", fontsize=9, color=TEXT, weight="bold")
    if invert:
        ax.set_ylim(wide.max().max() + 1, 0.5)
    ax.set_title(title, loc="left", color=TEXT)
    ax.set_ylabel(ylabel)
    fig.savefig(path)
    plt.close(fig)


def main(level="hs4"):
    cfg = load_config()
    c = cfg["complexity"]
    focus, peers = c["focus"], [p for p in c["peers"] if p != c["focus"]]
    src = cfg["output"] / f"complexity_{level}"
    out = cfg["output"] / f"germany_{level}"
    out.mkdir(exist_ok=True)

    countries = pd.read_parquet(src / "countries.parquet")
    products = pd.read_parquet(src / "products.parquet")
    cp = pd.read_parquet(src / "country_products.parquet")
    years = sorted(countries["year"].unique())
    y0, y1 = years[0], years[-1]
    group = [focus, *peers]

    # 1. ECI, rank and related country measures
    sel = countries[countries["iso3"].isin(group)]
    sel.to_csv(out / "eci_focus.csv", index=False)
    line_focus(sel, "eci_rank", focus, peers, f"ECI rank among {countries.iso3.nunique()} countries",
               "rank (1 = most complex)", out / "eci_rank.png", invert=True)
    line_focus(sel, "eci_fixed_pci", focus, peers,
               "Mean complexity of exported products, fixed (pooled) PCI",
               "mean pooled PCI of products with RCA >= 1", out / "eci_fixed_pci.png")
    line_focus(sel, "coi", focus, peers, "Complexity Outlook Index (z-score)", "COI",
               out / "coi.png")
    line_focus(sel, "diversity", focus, peers, "Diversity: number of products with RCA >= 1",
               "products", out / "diversity.png")

    # 2. Gap Germany minus peer, small multiples
    wide = sel.pivot(index="year", columns="iso3", values="eci")
    gap = wide[peers].rsub(wide[focus], axis=0)
    gap.to_csv(out / "eci_gap.csv")
    ncol = 5
    nrow = int(np.ceil(len(peers) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(12, 2.6 * nrow), sharex=True, sharey=True)
    for ax, p in zip(np.ravel(axes), peers):
        ax.axhline(0, color=TEXT2, lw=0.8)
        ax.plot(gap.index, gap[p], color=FOCUS_COLOR, lw=2)
        ax.set_title(f"{focus} minus {p}", loc="left", fontsize=9, color=TEXT)
    for ax in np.ravel(axes)[len(peers):]:
        ax.set_visible(False)
    fig.suptitle("ECI gap (positive = Germany more complex)", x=0.01, ha="left", color=TEXT)
    fig.savefig(out / "eci_gap.png")
    plt.close(fig)

    # 3. Export structure by complexity quintile (fixed pooled PCI)
    pooled = products.groupby("prod")["pci"].mean()
    quint = pd.qcut(pooled, 5, labels=[1, 2, 3, 4, 5])
    cpq = cp.assign(q=cp["prod"].map(quint), pci_pooled=cp["prod"].map(pooled))
    shares = (cpq.groupby(["iso3", "year", "q"], observed=True)["exports"].sum()
              / cpq.groupby(["iso3", "year"])["exports"].sum()).rename("share").reset_index()
    shares.to_csv(out / "pci_quintiles.csv", index=False)
    s = shares[shares.iso3 == focus].pivot(index="year", columns="q", values="share")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.stackplot(s.index, s.T.values, colors=QUINTILE_COLORS, edgecolor="#fcfcfb", lw=1,
                 labels=[f"Q{q}" for q in s.columns])
    ax.set_ylim(0, 1)
    ax.set_title(f"{focus}: export shares by product complexity quintile (Q5 = most complex)",
                 loc="left", color=TEXT)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1), frameon=False, reverse=True)
    fig.savefig(out / "pci_quintiles_deu.png")
    plt.close(fig)

    wavg = (cpq.assign(w=cpq.exports * cpq.pci_pooled).groupby(["iso3", "year"])
            .apply(lambda g: g.w.sum() / g.exports[g.pci_pooled.notna()].sum(), include_groups=False)
            .rename("export_pci").reset_index())
    wavg.to_csv(out / "export_pci.csv", index=False)
    line_focus(wavg, "export_pci", focus, peers,
               "Export-weighted mean complexity of the export basket (pooled PCI)",
               "pooled PCI", out / "export_pci.png")

    # 4. Products gained and lost, first vs last year
    first = cpq[cpq.year == y0].set_index(["iso3", "prod"])
    last = cpq[cpq.year == y1].set_index(["iso3", "prod"])
    both = first[["mcp", "density", "rca", "exports"]].join(
        last[["mcp", "rca", "exports", "pci_pooled"]], lsuffix="_0", rsuffix="_1")
    both["status"] = np.select(
        [(both.mcp_0 == 0) & (both.mcp_1 == 1), (both.mcp_0 == 1) & (both.mcp_1 == 0),
         (both.mcp_0 == 1) & (both.mcp_1 == 1)], ["entry", "exit", "kept"], "never")
    summary = (both.groupby(["iso3", "status"])
               .agg(n=("pci_pooled", "size"), mean_pci=("pci_pooled", "mean"),
                    mean_density_start=("density", "mean"))
               .reset_index())
    summary.to_csv(out / "entries_exits.csv", index=False)
    lst = both.loc[focus].query("status in ['entry', 'exit']").reset_index()
    names_file = cfg["output"] / "products_hs6.parquet"
    if level == "hs6" and names_file.exists():
        names = pd.read_parquet(names_file).set_index("hs6")["description"]
        lst["description"] = lst["prod"].map(names)
    lst.sort_values(["status", "exports_1"], ascending=[True, False]).to_csv(
        out / "entries_exits_list.csv", index=False)

    # 5. Relatedness test: does density predict entry? (all focus countries, 5-year steps)
    rows = []
    for t in years:
        if t + 5 > y1:
            break
        a = cp[cp.year == t].set_index(["iso3", "prod"])
        b = cp[cp.year == t + 5].set_index(["iso3", "prod"])["mcp"].rename("mcp_next")
        j = a.join(b)
        rows.append(j[j.mcp == 0][["density", "mcp_next"]])
    rel = pd.concat(rows)
    rel["decile"] = pd.qcut(rel.density, 10, labels=False, duplicates="drop") + 1
    rel_tab = rel.groupby("decile").agg(entry_rate=("mcp_next", "mean"), n=("mcp_next", "size"),
                                        density_mean=("density", "mean")).reset_index()
    rel_tab.to_csv(out / "relatedness_test.csv", index=False)

    # 6. Opportunities: Germany's products not yet exported with RCA >= 1, last year
    opp = cpq[(cpq.year == y1) & (cpq.iso3 == focus) & (cpq.mcp == 0)].copy()
    opp.sort_values("cog", ascending=False).head(50).to_csv(out / "opportunities.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(opp.density, opp.pci_pooled, s=14, color=FOCUS_COLOR, alpha=0.5,
               edgecolor="#fcfcfb", lw=0.5)
    ax.set_xlabel("density (relatedness to current exports)")
    ax.set_ylabel("product complexity (pooled PCI)")
    ax.set_title(f"{focus} {y1}: products without RCA, relatedness vs complexity",
                 loc="left", color=TEXT)
    fig.savefig(out / "opportunities.png")
    plt.close(fig)

    d = sel[sel.iso3 == focus].set_index("year")
    print(f"{focus} ECI rank: {int(d.eci_rank.loc[y0])} in {y0}, {int(d.eci_rank.loc[y1])} in {y1}")
    print(f"results -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hs4")
