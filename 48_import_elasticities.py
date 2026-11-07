"""Import demand elasticities by HS6 good for the EU and Germany (elasticities.py).

Data: CEPII BACI HS92 V202601, 2012-2024, values (thousand USD) and quantities (tons).
Importer EU27: imports of all 27 members summed by exporter, good and year; Germany:
German imports. Varieties are exporting countries. Goods with fewer than six varieties
or four years are skipped.

Outputs in <output>/scenarios:
  import_elasticities_hs92.csv  level, hs92, sigma, omega, rho, n_var, n_years, feasible
  import_elasticities_icio.csv  ICIO goods sector: import-weighted median of sigma - 1
                                (comparable to the trade elasticity theta) and ProTEE
Usage: python 48_import_elasticities.py
"""
import importlib
import zipfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

import elasticities as el
from config import load_config

YEARS = range(2012, 2025)
EU = importlib.import_module("44_dependencies").EU


def load(path):
    with zipfile.ZipFile(path) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str,
                         keep_default_na=False)
        iso = dict(zip(cc.country_code, cc.country_iso3.replace({"S19": "TWN"})))
        eu_codes = {c for c, i in iso.items() if i in EU}
        parts = []
        for y in YEARS:
            name = next(n for n in z.namelist() if f"_Y{y}_" in n)
            b = pd.read_csv(z.open(name), dtype={"i": str, "j": str, "k": str}, usecols=["t", "i", "j", "k", "v", "q"])
            b = b[b.j.isin(eu_codes) & ~b.i.isin(eu_codes) | (b.j == "276")]
            b["imp"] = np.where(b.j == "276", "DEU", "EU27")
            # EU27 rows: extra-EU suppliers only; Germany: all suppliers
            de = b[b.j == "276"].assign(imp="DEU")
            eu = b[b.j.isin(eu_codes) & ~b.i.isin(eu_codes)].assign(imp="EU27")
            parts.append(pd.concat([de, eu]).groupby(["imp", "t", "i", "k"], as_index=False)[["v", "q"]].sum())
            print(y, end=" ", flush=True)
    print()
    d = pd.concat(parts, ignore_index=True)
    d["exporter"] = d.i.map(iso)
    return d


def _one(args):
    (lv, k), g = args
    r = el.estimate(g.t.to_numpy(), g.exporter.to_numpy(), g.v.to_numpy(), g.q.to_numpy())
    return None if r is None else {"level": lv, "hs92": k, **r, "imports": float(g.v.sum())}


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    d = load(cfg["data"]["scenarios"] / "baci92" / "BACI_HS92_V202601.zip")
    groups = list(d.groupby(["imp", "k"]))
    print(f"{len(groups)} importer x good cells")
    with ProcessPoolExecutor() as ex:
        res = [r for r in ex.map(_one, groups, chunksize=50) if r is not None]
    e = pd.DataFrame(res)
    e.round(4).to_csv(out / "import_elasticities_hs92.csv", index=False)
    for lv, g in e.groupby("level"):
        print(f"{lv}: {len(g)} goods, median sigma {g.sigma.median():.2f}, import-weighted median "
              f"{weighted_median(g.sigma, g.imports):.2f}, feasible {g.feasible.mean():.0%}, "
              f"share sigma < 3: {(g.sigma < 3).mean():.0%}")

    # ICIO sectors: HS92 -> HS07 -> ISIC3 -> ICIO, and comparison with ProTEE
    m33 = importlib.import_module("33_tariff_inputs")
    conc = cfg["data"]["scenarios"] / "conc"
    h07_h92 = pd.read_csv(next(conc.glob("*H3_to_H0*.CSV")), dtype=str, encoding="latin1", usecols=[0, 2])
    h07_h92.columns = ["hs07", "hs92"]
    _, hs07, _ = m33.concordance(conc)
    m = h07_h92.merge(hs07, on="hs07").drop_duplicates("hs92")[["hs92", "sector"]]
    e = e.merge(m, on="hs92", how="left")
    rows = []
    for (lv, s), g in e.dropna(subset=["sector"]).groupby(["level", "sector"]):
        rows.append({"level": lv, "sector": s, "theta_own": round(weighted_median(g.sigma - 1, g.imports), 3),
                     "n_goods": len(g)})
    sec = pd.DataFrame(rows)
    pro = pd.read_csv(out / "elasticities_icio.csv").rename(columns={"theta": "theta_protee"})
    sec = sec.merge(pro[["sector", "theta_protee"]], on="sector", how="left")
    sec.to_csv(out / "import_elasticities_icio.csv", index=False)
    eu = sec[sec.level == "EU27"].dropna()
    from scipy.stats import spearmanr
    print(f"EU27 sectors: rank correlation own theta vs ProTEE {spearmanr(eu.theta_own, eu.theta_protee).statistic:.2f}")
    print(eu.sort_values("theta_own").to_string(index=False))


def weighted_median(x, w):
    x, w = np.asarray(x), np.asarray(w)
    o = np.argsort(x)
    cw = np.cumsum(w[o]) / w.sum()
    return float(x[o][np.searchsorted(cw, 0.5)])


if __name__ == "__main__":
    main()
