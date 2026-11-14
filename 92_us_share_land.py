"""US share of exports by Land, 2008-2025, and the US-share variant of the district tariff exposure.

Data: Destatis GENESIS 51000-0032 (exports by Land and partner country, EUR thousand), fetched by the
workflow .github/workflows/fetch-genesis.yml (branch data-genesis, data/genesis). Exports by Land include
goods of all origins in that Land (Ursprungsland-Prinzip by Land of production); "Ausland" and "Restposition"
are dropped.
Variant: within the downscaling of 74, the district export ratio q_k is replaced by q_k x (u_L / u_DE), with
u_L the US share of the exports of Land L (2024) and u_DE the national share. Districts in Länder that sell
more to the US get a larger share of the regional loss; regional totals stay as in 74 (the NUTS 2 shock is
national-mix based), so the variant moves the loss between districts of a region only where a region spans
Länder, and between regions not at all. A second version scales the NUTS 2 shock too (m_r x u_L / u_DE), which
moves the loss between Länder; the national total is then rescaled to the baseline.
Writes <output>/kreise/us_share_land.csv and us_tariffs_kreise_usshare.csv.
Usage: python 92_us_share_land.py <path to rdb_51000-0032.csv>
"""
import importlib
import sys

import pandas as pd

from config import load_config

k74 = importlib.import_module("74_kreise_us_tariffs")
r86 = importlib.import_module("86_kreise_robustness")
LAND = {"01": "Schleswig-Holstein", "02": "Hamburg", "03": "Niedersachsen", "04": "Bremen", "05": "Nordrhein-Westfalen",
        "06": "Hessen", "07": "Rheinland-Pfalz", "08": "Baden-Württemberg", "09": "Bayern", "10": "Saarland", "11": "Berlin",
        "12": "Brandenburg", "13": "Mecklenburg-Vorpommern", "14": "Sachsen", "15": "Sachsen-Anhalt", "16": "Thüringen"}


def us_share(path):
    d = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig")
    d = d[(d.value_variable_code == "WERTA") & d["1_variable_attribute_code"].isin(LAND)]
    d["v"] = pd.to_numeric(d.value, errors="coerce")
    tot = d.groupby(["1_variable_attribute_code", "time"]).v.sum()
    us = d[d["2_variable_attribute_code"] == "STLAH400"].groupby(["1_variable_attribute_code", "time"]).v.sum()
    s = pd.DataFrame({"exports": tot, "us": us}).reset_index().rename(columns={"1_variable_attribute_code": "land"})
    s["share"] = s.us / s.exports
    return s


def main(path):
    cfg = load_config()
    out = cfg["output"] / "kreise"
    s = us_share(path)
    s.to_csv(out / "us_share_land.csv", index=False)
    w = s.pivot(index="land", columns="time", values="share")
    nat = s.groupby("time")[["exports", "us"]].sum()
    nat = nat.us / nat.exports
    print("US share of German exports:", nat.round(3).loc[["2008", "2019", "2024", "2025"]].to_dict())
    tab = pd.DataFrame({"Land": [LAND[x] for x in w.index], "2019": w["2019"], "2024": w["2024"], "2025": w["2025"],
                        "rel_2024": w["2024"] / nat["2024"]}).sort_values("2024", ascending=False)
    exp = s.pivot(index="land", columns="time", values="us")
    tab["us_exports_change_2025_pct"] = 100 * (exp["2025"] / exp["2024"] - 1)
    print(tab.round(3).to_string())
    base = pd.read_csv(out / "us_tariffs_kreise.csv", dtype={"ags": str}).set_index("ags")
    k = base[["name", "nuts3", "nuts2", "pop"]].copy()
    rel = k.index.str[:2].map(tab.rel_2024)
    q, u = base.quote_2024, base.umsatz_mio_2024
    m0 = k74.mix_shock(cfg)
    dm1, l1 = r86.downscale(k, m0, q * rel, u)                       # within-region reallocation only
    dm2, l2 = r86.downscale(k, m0 * pd.Series(rel, index=k.index).groupby(k.nuts2).mean(), q * rel, u)
    l2 = l2 * base.loss_mio.sum() / l2.sum()                          # same national total as the baseline
    res = k.assign(loss_pc_base=base.loss_pc, loss_pc_us1=l1 * 1e6 / k["pop"], loss_pc_us2=l2 * 1e6 / k["pop"], rel=rel)
    res.round(4).to_csv(out / "us_tariffs_kreise_usshare.csv")
    v = res.dropna(subset=["loss_pc_base"])
    for c in ("loss_pc_us1", "loss_pc_us2"):
        print(c, "rank corr. with baseline:", round(v.loss_pc_base.corr(v[c], method="spearman"), 3))
    byland = pd.DataFrame({"base": base.loss_mio.groupby(k.index.str[:2]).sum(), "us2": l2.groupby(k.index.str[:2]).sum()})
    byland.index = [LAND[x] for x in byland.index]
    print((byland / 1000).round(2).assign(change_pct=lambda x: 100 * (x.us2 / x.base - 1)).round(1).sort_values("base", ascending=False).to_string())


if __name__ == "__main__":
    main(sys.argv[1])
