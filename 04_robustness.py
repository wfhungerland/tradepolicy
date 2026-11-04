"""Step 4: robustness of Germany's position to the main choices.

Variants: RCA threshold 0.75 / 1.25 / 2, smoothing window 1 / 5 years, HS6
instead of HS4, re-export hubs dropped. Fitness-Complexity is computed in every
run alongside ECI. Writes to <output>/robustness/:
  ranks.csv     year x spec x country: ECI, ECI rank, fitness rank (focus and peers)
  summary.csv   per spec: Germany's ECI rank and fitness rank in first and last
                year, and the Spearman correlation of ECI with the main run
Usage: python 04_robustness.py   (the HS6 run takes the longest)
"""
import pandas as pd
from scipy.stats import spearmanr

from config import load_config
import panel


def specs(cfg):
    hubs = cfg["complexity"]["hubs"]
    return [
        {"name": "main"},
        {"name": "rca_0.75", "threshold": 0.75},
        {"name": "rca_1.25", "threshold": 1.25},
        {"name": "rca_2", "threshold": 2.0},
        {"name": "window_1", "window": 1},
        {"name": "window_5", "window": 5},
        {"name": "no_hubs", "exclude": hubs},
        {"name": "hs6", "level": "hs6"},
    ]


def main():
    cfg = load_config()
    c = cfg["complexity"]
    group = [c["focus"], *c["peers"]]
    out = cfg["output"] / "robustness"
    out.mkdir(exist_ok=True)

    results = {}
    for spec in specs(cfg):
        print(f"running {spec['name']}")
        res = panel.run(cfg, spec, keep_products_for=[])
        df = res["countries"].copy()
        df["fitness_rank"] = df.groupby("year")["fitness"].rank(ascending=False).astype(int)
        df["spec"] = spec["name"]
        results[spec["name"]] = df

    main_df = results["main"].set_index(["year", "iso3"])
    rows, ranks = [], []
    for name, df in results.items():
        ranks.append(df[df.iso3.isin(group)])
        d = df[df.iso3 == c["focus"]].set_index("year")
        y0, y1 = d.index.min(), d.index.max()
        j = df.set_index(["year", "iso3"])[["eci"]].join(main_df[["eci"]], rsuffix="_main",
                                                          how="inner")
        rho = j.groupby(level="year").apply(lambda g: spearmanr(g.eci, g.eci_main).statistic)
        rho_fit = df.groupby("year").apply(
            lambda g: spearmanr(g.eci, g.fitness).statistic, include_groups=False)
        rows.append({
            "spec": name, "n_countries": df.iso3.nunique(),
            f"deu_eci_rank_{y0}": int(d.eci_rank.loc[y0]), f"deu_eci_rank_{y1}": int(d.eci_rank.loc[y1]),
            f"deu_fitness_rank_{y0}": int(d.fitness_rank.loc[y0]),
            f"deu_fitness_rank_{y1}": int(d.fitness_rank.loc[y1]),
            "spearman_eci_vs_main_mean": rho.mean(), "spearman_eci_vs_fitness_mean": rho_fit.mean(),
        })
    pd.concat(ranks).to_csv(out / "ranks.csv", index=False)
    summary = pd.DataFrame(rows)
    summary.to_csv(out / "summary.csv", index=False)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
