"""Impute manufacturing sales and foreign sales for the 14 districts suppressed in 2024.

Regionaldatenbank 42111-04-02-4 suppresses sales and/or foreign sales of 14 districts in 2024,
among them large car locations (Wolfsburg, Ingolstadt, Dingolfing-Landau, Böblingen). The totals of
the Regierungsbezirke (or of the Land where there are none) are published, so the suppressed
districts of each group are known together as a residual:
  R_U = U(group) - sum of published district sales,  R_A = A(group) - sum of published foreign sales.
Allocation within the group:
  sales (where suppressed): the residual is dominated by one large plant (VW, Audi, BMW) whose
      sales are high relative to value added. Each suppressed district except the one with the largest
      gross value added of the secondary sector (INKAR, VGR der Länder, 2022) gets that value added
      times the median ratio of sales to secondary value added among published districts of its Land;
      the largest district takes the rest of R_U;
  foreign sales: R_A in proportion to sales x own export ratio of the latest published year (if
      none was ever published, the group residual ratio R_A / R_U).
The imputed values are estimates; they are flagged and used as a robustness variant (86) and in
the paper, not in the published site maps.
Writes <output>/kreise/export_kreise_imputed.csv and us_tariffs_kreise_imputed.csv.
Usage: python 89_kreise_impute.py
"""
import importlib

import pandas as pd

import regional as rg
from config import load_config

i79 = importlib.import_module("79_inkar_analyses")
k74 = importlib.import_module("74_kreise_us_tariffs")
r86 = importlib.import_module("86_kreise_robustness")
GROUP = {"03": 3, "05": 3, "06": 3, "08": 3, "09": 3}       # Länder with Regierungsbezirke: group = first 3 digits


def main():
    cfg = load_config()
    out = cfg["output"] / "kreise"
    path = cfg["data"]["scenarios"] / "kreise" / "rdb_42111-04-02-4.csv"
    raw = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    raw["v"] = pd.to_numeric(raw.value, errors="coerce")
    tot = raw[(raw.time == "2024") & raw["1_variable_code"].isin(["REGBEZ", "DLAND"])] \
        .pivot_table(index="1_variable_attribute_code", columns="value_variable_label", values="v")
    p = rg.rdb_kreise(path)
    hist = p.dropna()
    lastq = (hist.ausl / hist.umsatz).groupby(level="ags").last()
    base = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    k = base[["name", "nuts3", "nuts2", "pop"]].copy()
    k["U"] = p.umsatz.xs(2024, level="year").reindex(k.index)
    k["A"] = p.ausl.xs(2024, level="year").reindex(k.index)
    k["grp"] = [a[:GROUP.get(a[:2], 2)] for a in k.index]
    d = i79.load_inkar(cfg["data"]["scenarios"] / "inkar" / "inkar_2025_kreise.parquet")
    gva = i79.get(d, "Anteil Bruttowertschöpfung Sekundärer Sektor", 2022) / 100 * i79.get(d, "Bruttoinlandsprodukt in 1000 Euro", 2022)
    ratio = (p.umsatz.xs(2022, level="year") / gva).dropna()
    land_ratio = ratio.groupby(ratio.index.str[:2]).median()
    k["imputed"] = k.A.isna()
    rows = []
    for g, x in k[k.imputed].groupby("grp"):
        allx = k[k.grp == g]
        RU = tot.loc[g, "Umsatz"] - allx.U.sum()
        RA = tot.loc[g, "Auslandsumsatz"] - allx.A.sum()
        mu = x.index[x.U.isna()]
        if len(mu):
            g_ = gva.reindex(mu)
            big = g_.idxmax()
            small = [a for a in mu if a != big]
            est = g_[small] * land_ratio[g[:2]]
            k.loc[small, "U"] = est
            k.loc[big, "U"] = RU - est.sum()
            assert k.loc[big, "U"] > 0, f"negative remainder in group {g}"
        ru_ratio = RA / (RU + x.U.drop(mu, errors="ignore").sum())
        qt = lastq.reindex(x.index).fillna(ru_ratio)
        w = k.loc[x.index, "U"] * qt
        k.loc[x.index, "A"] = RA * w / w.sum()
        rows.append({"group": g, "districts": ", ".join(x.name), "residual_sales_bn": RU / 1e6, "residual_foreign_bn": RA / 1e6})
    print(pd.DataFrame(rows).round(2).to_string(index=False))
    k["q"] = k.A / k.U
    print(k[k.imputed][["name", "U", "A", "q"]].assign(U=lambda x: x.U / 1e6, A=lambda x: x.A / 1e6).round(3).to_string())
    k.round(4).to_csv(out / "export_kreise_imputed.csv")
    dm, loss = r86.downscale(k, k74.mix_shock(cfg), k.q, k.U / 1000)
    res = k[["name", "nuts3", "nuts2", "pop", "imputed"]].assign(quote_2024=k.q, umsatz_mio_2024=k.U / 1000, dm=dm, loss_mio=loss,
                                                                 loss_pc=loss * 1e6 / k["pop"])
    res.round(5).to_csv(out / "us_tariffs_kreise_imputed.csv")
    print(f"total loss with imputed districts: {res.loss_mio.sum():,.0f} EUR million (baseline {base.loss_mio.sum():,.0f}); "
          f"imputed districts {res[res.imputed].loss_mio.sum():,.0f}")
    rk = res.loss_pc.rank(ascending=False)
    print(res[res.imputed].assign(rank=rk).sort_values("loss_pc", ascending=False)[["name", "dm", "loss_pc", "loss_mio", "rank"]].round(1).to_string())


if __name__ == "__main__":
    main()
