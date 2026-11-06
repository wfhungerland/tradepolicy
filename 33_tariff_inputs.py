"""Tariff and elasticity inputs for the US tariff scenario, by ICIO 2025 sector.

1. Concordance HS 2022 -> HS 2007 -> ISIC Rev. 3 (WITS tables) -> ICIO 2025
   sectors (ISIC Rev. 4 based, hand mapping ISIC3_TO_ICIO below).
2. US applied tariffs 2025-26 (CEPII, Guimbard 2026) by exporter, HS6 and
   date, aggregated to exporter x ICIO sector with US import weights from
   BACI HS22, 2024 (fixed weights, so changes reflect tariffs, not trade
   diversion).
3. Trade elasticities: ProTEE 0.1 (Fontagne, Guimbard, Orefice 2022, JIE)
   at HS6 (HS 2007), aggregated to ICIO sectors as the world-trade-weighted
   median of |sigma|. Sectors without estimates (services) get the default 5.

Writes to <output>/scenarios:
  us_tariffs_icio.parquet  date, exporter (ISO3), sector, tariff (0.25 = 25 %)
  elasticities_icio.csv    sector, theta, n_hs6, share_trade_covered
  hs6_icio_map.csv         HS 2022 six-digit code -> ICIO sector
Inputs in cfg["data"]["scenarios"]: usa_tariffs_20260907.zip, ProTEE_0_1.csv,
BACI_HS22_V202601.zip, conc/ with the WITS files Concordance_H6_to_H3 and
Concordance_H3_to_I3 (30_scenario_download.py fetches them).
Usage: python 33_tariff_inputs.py
"""
import zipfile

import numpy as np
import pandas as pd

from config import load_config

DEFAULT_THETA = 5.0
WEIGHT_YEAR = 2024


def isic3_to_icio(c):
    """ISIC Rev. 3 four-digit code -> ICIO 2025 sector code (None if no goods sector)."""
    d2, d3 = c[:2], c[:3]
    simple = {"01": "A01", "02": "A02", "05": "A03", "10": "B05", "11": "B06", "12": "B07",
              "13": "B07", "14": "B08", "15": "C10T12", "16": "C10T12", "17": "C13T15",
              "18": "C13T15", "19": "C13T15", "20": "C16", "21": "C17_18", "22": "C17_18",
              "23": "C19", "25": "C22", "26": "C23", "28": "C25", "30": "C26", "31": "C27",
              "32": "C26", "34": "C29", "36": "C31T33", "37": "E", "40": "D", "74": "M",
              "92": "R", "93": "S"}
    if d2 == "24":
        return "C21" if c.startswith("2423") else "C20"
    if d2 == "27":
        return "C24A" if d3 in ("271",) or c.startswith("2731") else "C24B"
    if d2 == "29":
        return "C27" if d3 == "293" else "C28"
    if d2 == "33":
        return "C31T33" if c.startswith("3311") else "C26"
    if d2 == "35":
        return "C301" if d3 == "351" else "C302T309"
    return simple.get(d2)


def concordance(folder):
    def read(name):
        path = next(folder.glob(f"*{name}*.CSV"))
        return pd.read_csv(path, dtype=str, encoding="latin1", usecols=[0, 2])
    h22_07 = read("H6_to_H3")
    h22_07.columns = ["hs22", "hs07"]
    h07_i3 = read("H3_to_I3")
    h07_i3.columns = ["hs07", "isic3"]
    m = h22_07.merge(h07_i3, on="hs07", how="left")
    m["sector"] = m.isic3.fillna("").map(isic3_to_icio)
    # an HS 2022 code can map to several HS 2007 codes: take the most frequent sector
    hs22 = (m.dropna(subset=["sector"]).groupby("hs22")["sector"]
            .agg(lambda s: s.value_counts().index[0]).rename("sector").reset_index())
    hs07 = h07_i3.assign(sector=h07_i3.isic3.map(isic3_to_icio))[["hs07", "sector"]].dropna()
    return hs22, hs07, h22_07


def baci_weights(path, year):
    """US imports by exporter (ISO3) and HS 2022 code, and world trade by HS 2022 code."""
    with zipfile.ZipFile(path) as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))),
                         dtype=str, keep_default_na=False)
        name = next(n for n in z.namelist() if f"_Y{year}_" in n)
        b = pd.read_csv(z.open(name), dtype={"i": str, "j": str, "k": str},
                        usecols=["i", "j", "k", "v"])
    iso = dict(zip(cc.country_code, cc.country_iso3))
    world = b.groupby("k")["v"].sum().rename("world_v")
    us = b[b.j == "842"].groupby(["i", "k"], as_index=False)["v"].sum()
    us["exporter"] = us.i.map(iso)
    return us.rename(columns={"k": "hs22"})[["exporter", "hs22", "v"]], world


def main():
    cfg = load_config()
    src = cfg["data"]["scenarios"]
    out = cfg["output"] / "scenarios"
    out.mkdir(parents=True, exist_ok=True)

    hs22, hs07, h22_07 = concordance(src / "conc")
    hs22.to_csv(out / "hs6_icio_map.csv", index=False)
    print(f"HS 2022 codes mapped to ICIO sectors: {len(hs22)}")

    us, world = baci_weights(src / "BACI_HS22_V202601.zip", WEIGHT_YEAR)

    # tariffs: exporter x HS6 x date -> exporter x sector x date, US-import weighted
    with zipfile.ZipFile(src / "usa_tariffs_20260907.zip") as z:
        z.extract("usa_tariffs_20260907.parquet", out)
    t = pd.read_parquet(out / "usa_tariffs_20260907.parquet",
                        columns=["exporter_iso", "date_inforce", "hs6_rev2022", "ave"])
    t = t.rename(columns={"exporter_iso": "exporter", "hs6_rev2022": "hs22"})
    t = t.merge(hs22, on="hs22", how="inner").merge(us, on=["exporter", "hs22"], how="inner")
    t = t[t.v > 0]
    t["tv"] = t.ave * t.v
    g = t.groupby(["date_inforce", "exporter", "sector"], as_index=False)[["tv", "v"]].sum()
    g["tariff"] = g.tv / g.v
    g = g.rename(columns={"date_inforce": "date", "v": "us_imports_2024"})
    g[["date", "exporter", "sector", "tariff", "us_imports_2024"]].to_parquet(
        out / "us_tariffs_icio.parquet", index=False)
    print(f"tariff cells: {len(g)}, dates: {g.date.nunique()}")

    # elasticities: ProTEE (HS 2007) with world trade weights mapped from HS 2022
    p = pd.read_csv(src / "ProTEE_0_1.csv", dtype={"HS6": str}).rename(columns={"HS6": "hs07"})
    p = p.dropna(subset=["sigma"])
    w07 = (h22_07.merge(world.rename_axis("hs22").reset_index(), on="hs22")
           .groupby("hs07")["world_v"].sum())
    p = p.merge(hs07, on="hs07").assign(w=lambda d: d.hs07.map(w07).fillna(0.0), theta=lambda d: -d.sigma)
    rows = []
    for s, d in p.groupby("sector"):
        d = d.sort_values("theta")
        cw = d.w.cumsum() / d.w.sum() if d.w.sum() > 0 else np.arange(1, len(d) + 1) / len(d)
        med = float(d.theta.iloc[int(np.searchsorted(cw.to_numpy(), 0.5))])
        rows.append((s, round(med, 3), len(d)))
    el = pd.DataFrame(rows, columns=["sector", "theta", "n_hs6"])
    el.to_csv(out / "elasticities_icio.csv", index=False)
    print(el.to_string(index=False))


if __name__ == "__main__":
    main()
