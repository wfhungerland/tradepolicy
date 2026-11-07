"""Strategic dependencies of the EU and of Germany at HS6, following the European
Commission (2021, SWD(2021) 352) as summarised in CEPII Policy Brief 2023-41.

A product (HS 2022, six digits) is a dependency if all three hold:
  1. concentration: HHI of extra-EU import sources (shares of supplier countries) > 0.4
  2. importance:    extra-EU imports / total imports (extra + intra-EU) > 0.5
  3. no substitute: extra-EU imports / total exports of the EU > 1
The Commission restricts its 137 products to "sensitive ecosystems"; that mapping is
not public, so this script reports all products and their split by HS section.
Germany: the same with German imports, partners outside the EU; criterion 2 uses
German imports from outside the EU over all German imports, criterion 3 German exports.

For each dependency: main supplier and its share, China's share, and the share of
imports whose sea route to Hamburg passes the Red Sea or the Strait of Malacca
(closing the passage lengthens the route, sea_routes.py).
Data: CEPII BACI HS22, 2024 (value, thousand USD).
Writes <output>/scenarios/dependencies_hs6.csv (both levels) and dependencies_summary.csv.
Usage: python 44_dependencies.py
"""
import importlib
import zipfile

import numpy as np
import pandas as pd

import sea_routes as sr
from config import load_config

YEAR = 2024
EU = ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA",
      "LVA", "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"]
HS_SECTIONS = [(1, 5, "Tiere"), (6, 14, "Pflanzen"), (15, 15, "Fette"), (16, 24, "Nahrungsmittel"), (25, 27, "Mineralien, Energie"),
               (28, 38, "Chemie, Pharma"), (39, 40, "Kunststoff, Kautschuk"), (41, 43, "Leder"), (44, 49, "Holz, Papier"),
               (50, 63, "Textilien"), (64, 67, "Schuhe"), (68, 71, "Steine, Glas, Edelmetalle"), (72, 83, "Metalle"),
               (84, 85, "Maschinen, Elektronik"), (86, 89, "Fahrzeuge"), (90, 92, "Instrumente"), (93, 99, "Sonstiges")]


def section(hs6):
    ch = int(hs6[:2])
    return next(s for lo, hi, s in HS_SECTIONS if lo <= ch <= hi)


def load_baci(path, year):
    with zipfile.ZipFile(path) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str, keep_default_na=False)
        b = pd.read_csv(z.open(next(n for n in z.namelist() if f"_Y{year}_" in n)), dtype={"i": str, "j": str, "k": str},
                        usecols=["i", "j", "k", "v"])
    iso = dict(zip(cc.country_code, cc.country_iso3.replace({"S19": "TWN"})))
    b["exp"], b["imp"] = b.i.map(iso), b.j.map(iso)
    return b.rename(columns={"k": "hs6"})[["exp", "imp", "hs6", "v"]]


def dependencies(b, importers, level):
    """importers: list of ISO3 forming the importing block; 'extra' = partners outside the EU."""
    imp = b[b.imp.isin(importers)]
    extra = imp[~imp.exp.isin(EU)]
    tot_imp = imp.groupby("hs6").v.sum()
    by_src = extra.groupby(["hs6", "exp"]).v.sum()
    ext = by_src.groupby(level=0).sum()
    share = by_src / ext.reindex(by_src.index.get_level_values(0)).to_numpy()
    hhi = (share ** 2).groupby(level=0).sum()
    top = share.groupby(level=0).idxmax().map(lambda t: t[1])
    top_share = share.groupby(level=0).max()
    chn = share.xs("CHN", level=1) if "CHN" in share.index.get_level_values(1) else pd.Series(dtype=float)
    exports = b[b.exp.isin(importers)].groupby("hs6").v.sum()
    d = pd.DataFrame({"extra_imports": ext, "total_imports": tot_imp, "hhi": hhi, "top_supplier": top,
                      "top_share": top_share, "china_share": chn}).fillna({"china_share": 0.0})
    d["exports"] = exports.reindex(d.index).fillna(0.0)
    d["extra_share"] = d.extra_imports / d.total_imports
    d["import_export_ratio"] = d.extra_imports / d.exports.replace(0, np.nan)
    d["c1"], d["c2"] = d.hhi > 0.4, d.extra_share > 0.5
    d["c3"] = (d.import_export_ratio > 1) | (d.exports == 0)
    d["dependent"] = d.c1 & d.c2 & d.c3
    d["level"] = level
    return d, share


def route_exposure(cfg, share, deps):
    """Share of extra-EU imports of each dependent product on sea routes to Hamburg
    through the Red Sea or the Strait of Malacca."""
    folder = cfg["data"]["scenarios"] / "searoute"
    net = sr.SeaNetwork(folder / "marnet_searoute.geojson")
    with zipfile.ZipFile(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip") as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))), dtype=str, keep_default_na=False)
    iso2 = dict(zip(cc.country_iso3.replace({"S19": "TWN"}), cc.country_iso2))
    iso2["TWN"] = "TW"
    srcs = sorted({e for h in deps for e in share.loc[h].index if e not in EU})
    codes = {e: iso2.get(e) for e in srcs if iso2.get(e)}
    ports = sr.country_ports(folder / "ports.geojson", sorted(set(codes.values()) | {"DE"}))
    hub = net.nearest(ports["DE"][0], ports["DE"][1])
    via = {}
    for name, closed in (("red_sea", ("suez", "babalmandab")), ("malacca", ("malacca",))):
        d0, d1 = net.distances(hub), net.distances(hub, closed)
        via[name] = {}
        for e, c in codes.items():
            if c in ports:
                n = net.nearest(ports[c][0], ports[c][1])
                via[name][e] = d1.get(n, np.inf) > d0.get(n, np.inf) * 1.01
    out = {}
    for h in deps:
        s = share.loc[h]
        out[h] = {k: float(sum(v for e, v in s.items() if via[k].get(e, False))) for k in via}
    return pd.DataFrame(out).T


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    b = load_baci(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip", YEAR)
    names = pd.read_csv(zipfile.ZipFile(cfg["data"]["scenarios"] / "BACI_HS22_V202601.zip").open(
        "product_codes_HS22_V202601.csv"), dtype=str).set_index("code")["description"]
    res, shares = [], {}
    for level, importers in (("EU27", EU), ("DEU", ["DEU"])):
        d, share = dependencies(b, importers, level)
        shares[level] = share
        dep = d[d.dependent].index
        expo = route_exposure(cfg, share, dep)
        d = d.join(expo)
        res.append(d)
        dd = d[d.dependent]
        print(f"{level}: {len(dd)} dependent products of {len(d)}; extra imports {dd.extra_imports.sum() / 1e6:.1f} bn USD "
              f"({dd.extra_imports.sum() / d.extra_imports.sum():.1%} of extra imports); China main supplier for "
              f"{(dd.top_supplier == 'CHN').sum()} products, {dd.loc[dd.top_supplier == 'CHN', 'extra_imports'].sum() / 1e6:.1f} bn USD; "
              f"via Red Sea {np.average(dd.red_sea, weights=dd.extra_imports):.0%}, via Malacca {np.average(dd.malacca, weights=dd.extra_imports):.0%}")
    r = pd.concat(res).reset_index().rename(columns={"index": "hs6"})
    r["section"] = r.hs6.map(section)
    r["name_en"] = r.hs6.map(names)
    r.round(4).to_csv(out / "dependencies_hs6.csv", index=False)
    s = (r[r.dependent].groupby(["level", "section"]).agg(products=("hs6", "size"), extra_imports_bn=("extra_imports", "sum"))
         .assign(extra_imports_bn=lambda x: (x.extra_imports_bn / 1e6).round(2)).reset_index())
    s.to_csv(out / "dependencies_summary.csv", index=False)
    print(s.pivot(index="section", columns="level", values="products").fillna(0).astype(int).to_string())


if __name__ == "__main__":
    main()
