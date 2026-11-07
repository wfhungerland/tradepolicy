"""Export the dependency analysis (scripts 44, 45) as dependencies.json for the site.
Usage: python 46_export_dependencies.py [target_folder]
"""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

from config import load_config

TOP = 40


def main(target=None):
    cfg = load_config()
    src = cfg["output"] / "scenarios"
    out = Path(target) if target else cfg["output"] / "site_data"
    d = pd.read_csv(src / "dependencies_hs6.csv", dtype={"hs6": str})
    de4 = {r["hs4"]: r["name_de"] for r in csv.DictReader(open(Path(__file__).parent / "product_names_de.csv", encoding="utf-8"))}
    levels = {}
    for lv in ("EU27", "DEU"):
        a = d[d.level == lv]
        dep = a[a.dependent].sort_values("extra_imports", ascending=False)
        sect = dep.groupby("section").agg(n=("hs6", "size"), n_chn=("top_supplier", lambda s: int((s == "CHN").sum())),
                                          bn=("extra_imports", "sum")).reset_index().sort_values("n", ascending=False)
        levels[lv] = {
            "n_products": int(len(a)), "n_dependent": int(len(dep)),
            "extra_imports_bn": round(dep.extra_imports.sum() / 1e6, 1),
            "share_of_extra_imports": round(dep.extra_imports.sum() / a.extra_imports.sum(), 4),
            "n_china_main": int((dep.top_supplier == "CHN").sum()),
            "china_main_bn": round(dep.loc[dep.top_supplier == "CHN", "extra_imports"].sum() / 1e6, 1),
            "red_sea_share": round(float((dep.red_sea * dep.extra_imports).sum() / dep.extra_imports.sum()), 3),
            "malacca_share": round(float((dep.malacca * dep.extra_imports).sum() / dep.extra_imports.sum()), 3),
            "sections": [[r.section, int(r.n), int(r.n_chn), round(r.bn / 1e6, 2)] for r in sect.itertuples()],
            "columns": ["hs6", "name_de_hs4", "name_en", "top_supplier", "top_share", "china_share", "extra_imports_bn",
                        "hhi", "extra_share", "red_sea", "malacca"],
            "products": [[r.hs6, de4.get(r.hs6[:4], ""), r.name_en, r.top_supplier, round(r.top_share, 3), round(r.china_share, 3),
                          round(r.extra_imports / 1e6, 3), round(r.hhi, 3), round(r.extra_share, 3), round(r.red_sea, 3),
                          round(r.malacca, 3)] for r in dep.itertuples()],
        }
    g = pd.read_csv(src / "china_dependency_germany.csv").merge(
        pd.read_csv(src / "china_dependence_germany_total.csv")[["sector", "dependent_total_pct", "china_va_total_pct", "direct_dependent_pct"]], on="sector")
    g = g[g.output_2022_bn >= 5].sort_values("dependent_total_pct", ascending=False).head(12)
    data = {"year": 2024, "levels": levels,
            "germany_industries_columns": ["sector", "direct_dependent_pct", "output_change_pct", "output_2022_bn",
                                           "dependent_incl_indirect_pct", "china_value_added_pct"],
            "germany_industries": [[r.sector, round(r.direct_dependent_pct, 3), round(r.output_pct, 2),
                                    round(r.output_2022_bn, 1), round(r.dependent_total_pct, 3), round(r.china_va_total_pct, 2)]
                                   for r in g.itertuples()]}
    (out / "dependencies.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"dependencies.json: {(out / 'dependencies.json').stat().st_size / 1e3:.0f} kB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
