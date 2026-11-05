"""Step 7: compare our ECI and PCI with the Atlas of Economic Complexity.

Downloads the Harvard Growth Lab rankings and HS92 product data from Harvard
Dataverse (once, into <output>/atlas/), then compares them with the main HS4
run of 02_complexity.py:
  - correlation of ECI across countries, by year (common countries)
  - ECI rank of Germany and peers in both sources
  - top 10 countries in the first and last common year
  - correlation of PCI across HS4 products, by year
Writes to <output>/atlas_comparison/:
  eci_correlation.csv, ranks_focus.csv, top10.csv, pci_correlation.csv,
  rank_deu_atlas.png
Sources:
  Growth Lab (2026), Growth Projections and Complexity Rankings,
    doi:10.7910/DVN/XTAQMC, Harvard Dataverse.
  Growth Lab (2026), International Trade Data (HS, 92),
    doi:10.7910/DVN/T4CHWJ, Harvard Dataverse.
Usage: python 07_atlas_comparison.py
"""
import urllib.request

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from config import load_config

DATAVERSE = "https://dataverse.harvard.edu/api/access/datafile/{}"
FILES = {  # Dataverse file ids (dataset versions of February 2026)
    "rankings.csv": 13439575,
    "hs92_country_year.csv": 13685109,
    "hs92_product_year_4.csv": 13685116,
}
FOCUS_COLOR = "#2a78d6"
ATLAS_COLOR = "#eb6834"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
GRID = "#e6e5e0"


def fetch(folder):
    folder.mkdir(exist_ok=True)
    for name, fid in FILES.items():
        target = folder / name
        if not target.exists():
            print(f"downloading {name}")
            urllib.request.urlretrieve(DATAVERSE.format(fid), target)


def main():
    cfg = load_config()
    c = cfg["complexity"]
    group = [c["focus"], *c["peers"]]
    atlas_dir = cfg["output"] / "atlas"
    out = cfg["output"] / "atlas_comparison"
    out.mkdir(exist_ok=True)
    fetch(atlas_dir)

    ours = pd.read_parquet(cfg["output"] / "complexity_hs4" / "countries.parquet")
    ours_p = pd.read_parquet(cfg["output"] / "complexity_hs4" / "products.parquet")
    rk = pd.read_csv(atlas_dir / "rankings.csv")
    rk = rk[rk.in_rankings.astype(str) == "True"].rename(columns={"country_iso3_code": "iso3"})
    rk = rk[["iso3", "year", "eci_hs92", "eci_rank_hs92"]].dropna()
    ap = pd.read_csv(atlas_dir / "hs92_product_year_4.csv", dtype={"product_hs92_code": str})
    ap = ap.rename(columns={"product_hs92_code": "prod", "pci": "pci_atlas"})

    # 1. ECI correlation by year on common countries
    m = ours.merge(rk, on=["iso3", "year"], how="inner")
    rows = []
    for year, g in m.groupby("year"):
        rows.append({"year": year, "n_common": len(g),
                     "pearson": pearsonr(g.eci, g.eci_hs92).statistic,
                     "spearman": spearmanr(g.eci, g.eci_hs92).statistic})
    eci_corr = pd.DataFrame(rows)
    eci_corr.to_csv(out / "eci_correlation.csv", index=False)

    # 2. Ranks of Germany and peers; our rank re-computed on the common set
    m["rank_ours_common"] = m.groupby("year")["eci"].rank(ascending=False).astype(int)
    m["rank_atlas_common"] = m.groupby("year")["eci_hs92"].rank(ascending=False).astype(int)
    focus = m[m.iso3.isin(group)][["year", "iso3", "eci", "eci_rank", "rank_ours_common",
                                    "eci_hs92", "eci_rank_hs92", "rank_atlas_common"]]
    focus.to_csv(out / "ranks_focus.csv", index=False)

    # 3. Top 10 in first and last common year
    y0, y1 = m.year.min(), m.year.max()
    top = []
    for year in (y0, y1):
        g = m[m.year == year]
        top.append(pd.DataFrame({
            "year": year, "rank": range(1, 11),
            "ours": g.nsmallest(10, "rank_ours_common").iso3.values,
            "atlas": g.nsmallest(10, "rank_atlas_common").iso3.values,
        }))
    top = pd.concat(top)
    top.to_csv(out / "top10.csv", index=False)

    # 4. PCI correlation by year on common HS4 products
    pm = ours_p.merge(ap[["prod", "year", "pci_atlas"]], on=["prod", "year"], how="inner").dropna()
    pci_corr = pm.groupby("year").apply(
        lambda g: pd.Series({"n_common": len(g), "pearson": pearsonr(g.pci, g.pci_atlas).statistic,
                             "spearman": spearmanr(g.pci, g.pci_atlas).statistic}),
        include_groups=False).reset_index()
    pci_corr.to_csv(out / "pci_correlation.csv", index=False)

    # Figure: Germany's rank in both sources (common country set)
    d = focus[focus.iso3 == c["focus"]].set_index("year")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(d.index, d.rank_ours_common, color=FOCUS_COLOR, lw=2.2, label="this project (HS4)")
    ax.plot(d.index, d.rank_atlas_common, color=ATLAS_COLOR, lw=2.2, label="Atlas (HS92)")
    ax.set_ylim(max(d.rank_ours_common.max(), d.rank_atlas_common.max()) + 1, 0.5)
    ax.set_ylabel("ECI rank (common countries)", color=TEXT2)
    ax.set_title(f"{c['focus']}: ECI rank, this project vs Atlas", loc="left", color=TEXT)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(color=GRID)
    ax.legend(frameon=False)
    fig.savefig(out / "rank_deu_atlas.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(eci_corr.iloc[[0, len(eci_corr) // 2, -1]].round(3).to_string(index=False))
    print(pci_corr.iloc[[0, -1]].round(3).to_string(index=False))
    print(top.to_string(index=False))
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
