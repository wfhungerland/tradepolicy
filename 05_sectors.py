"""Step 5: sector view of Germany and peers, HS4 and HS6.

Products are grouped into sectors by HS chapter. For each country, sector and
level (hs4, hs6) the script compares the first and last year:
  world market share, number of products with RCA >= 1, products gained and
  lost, and the mean pooled PCI of gained and lost products.
Writes to <output>/sectors/:
  sectors.csv              all countries in the focus group, both levels
  sectors_deu.png          Germany: world market share by sector, first vs last year
  sectors_deu_entries.png  Germany: products gained and lost by sector (HS6)
Requires 02_complexity.py to have run for hs4 and hs6.
Usage: python 05_sectors.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import load_config

# HS chapter ranges (inclusive) -> sector
SECTORS = [
    ((1, 24), "Food and agriculture"),
    ((25, 27), "Minerals and fuels"),
    ((28, 29), "Basic chemicals"),
    ((30, 30), "Pharmaceuticals"),
    ((31, 38), "Other chemicals"),
    ((39, 40), "Plastics and rubber"),
    ((41, 49), "Leather, wood, paper"),
    ((50, 67), "Textiles, apparel, footwear"),
    ((68, 71), "Stone, glass, precious metals"),
    ((72, 83), "Metals"),
    ((84, 84), "Machinery"),
    ((85, 85), "Electrical and electronics"),
    ((87, 87), "Motor vehicles"),
    ((86, 89), "Other transport"),
    ((90, 92), "Instruments and medical"),
    ((93, 99), "Other manufactures"),
]

FOCUS_COLOR = "#2a78d6"
LIGHT = "#9ec5f4"
LOSS = "#e34948"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
GRID = "#e6e5e0"


def sector_of(prod: str) -> str:
    ch = int(prod[:2])
    for (lo, hi), name in SECTORS:
        if lo <= ch <= hi:
            return name
    return "Other manufactures"


def summarise(cfg, level):
    src = cfg["output"] / f"complexity_{level}"
    cp = pd.read_parquet(src / "country_products.parquet")
    products = pd.read_parquet(src / "products.parquet")
    pooled = products.groupby("prod")["pci"].mean()
    y0, y1 = cp.year.min(), cp.year.max()

    world = products[products.year.isin([y0, y1])].copy()
    world["sector"] = world["prod"].map(sector_of)
    world = world.groupby(["year", "sector"])["world_exports"].sum()

    cp = cp[cp.year.isin([y0, y1])].copy()
    cp["sector"] = cp["prod"].map(sector_of)
    cp["pci"] = cp["prod"].map(pooled)
    a = cp[cp.year == y0].set_index(["iso3", "prod"])
    b = cp[cp.year == y1].set_index(["iso3", "prod"])
    j = a[["sector", "mcp", "exports", "pci"]].join(b[["mcp", "exports"]], rsuffix="_1")
    j["entry"] = (j.mcp == 0) & (j.mcp_1 == 1)
    j["exit"] = (j.mcp == 1) & (j.mcp_1 == 0)

    rows = []
    for (iso, sec), g in j.groupby([j.index.get_level_values("iso3"), "sector"]):
        rows.append({
            "level": level, "iso3": iso, "sector": sec, "n_products": len(g),
            f"world_share_{y0}": g.exports.sum() / world.loc[(y0, sec)],
            f"world_share_{y1}": g.exports_1.sum() / world.loc[(y1, sec)],
            f"export_share_{y1}": np.nan,  # filled below
            f"rca_products_{y0}": int(g.mcp.sum()), f"rca_products_{y1}": int(g.mcp_1.sum()),
            "entries": int(g.entry.sum()), "exits": int(g.exit.sum()),
            "pci_entries": g.loc[g.entry, "pci"].mean(), "pci_exits": g.loc[g.exit, "pci"].mean(),
            f"exports_entries_{y1}": g.loc[g.entry, "exports_1"].sum(),
            f"exports_exits_{y1}": g.loc[g.exit, "exports_1"].sum(),
        })
    out = pd.DataFrame(rows)
    tot = j.groupby(level="iso3")["exports_1"].sum()
    sec_tot = j.groupby([j.index.get_level_values("iso3"), "sector"])["exports_1"].sum()
    out[f"export_share_{y1}"] = [sec_tot.loc[(r.iso3, r.sector)] / tot.loc[r.iso3]
                                 for r in out.itertuples()]
    return out, y0, y1


def main():
    cfg = load_config()
    focus = cfg["complexity"]["focus"]
    out = cfg["output"] / "sectors"
    out.mkdir(exist_ok=True)

    parts = []
    for level in ("hs4", "hs6"):
        df, y0, y1 = summarise(cfg, level)
        parts.append(df)
    res = pd.concat(parts, ignore_index=True)
    res.to_csv(out / "sectors.csv", index=False)

    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": TEXT2, "xtick.color": TEXT2, "ytick.color": TEXT2,
                         "font.size": 10, "figure.dpi": 150, "savefig.bbox": "tight"})

    # Germany: world market share by sector, dumbbell (HS4)
    d = res[(res.iso3 == focus) & (res.level == "hs4")].sort_values(f"world_share_{y1}")
    fig, ax = plt.subplots(figsize=(8, 6))
    yy = np.arange(len(d))
    ax.hlines(yy, d[f"world_share_{y0}"] * 100, d[f"world_share_{y1}"] * 100, color=GRID, lw=3)
    ax.scatter(d[f"world_share_{y0}"] * 100, yy, color=LIGHT, s=50, label=str(y0), zorder=3)
    ax.scatter(d[f"world_share_{y1}"] * 100, yy, color=FOCUS_COLOR, s=50, label=str(y1), zorder=3)
    ax.set_yticks(yy, d.sector)
    ax.set_xlabel("share of world exports in the sector, %")
    ax.set_title(f"{focus}: world market share by sector", loc="left", color=TEXT)
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID)
    fig.savefig(out / "sectors_deu.png")
    plt.close(fig)

    # Germany: products gained and lost by sector (HS6)
    d = res[(res.iso3 == focus) & (res.level == "hs6")].copy()
    d["net"] = d.entries - d.exits
    d = d.sort_values("net")
    fig, ax = plt.subplots(figsize=(8, 6))
    yy = np.arange(len(d))
    ax.barh(yy, d.entries, color=FOCUS_COLOR, height=0.6, label="gained")
    ax.barh(yy, -d.exits, color=LOSS, height=0.6, label="lost")
    ax.axvline(0, color=TEXT2, lw=0.8)
    ax.set_yticks(yy, d.sector)
    ax.set_xlabel("number of HS6 products")
    ax.set_title(f"{focus}: products gained and lost with RCA >= 1, {y0}-{y1}",
                 loc="left", color=TEXT)
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID)
    fig.savefig(out / "sectors_deu_entries.png")
    plt.close(fig)

    cols = ["level", "sector", f"world_share_{y0}", f"world_share_{y1}", f"export_share_{y1}",
            "entries", "exits", "pci_entries", "pci_exits"]
    print(res[res.iso3 == focus][cols].round(3).to_string(index=False))
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
