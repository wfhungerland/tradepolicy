"""Step 1: build country x HS6 x year export totals from the BACI raw CSV files.

Reads every BACI_HS92_Y*_V*.csv in data.baci_raw, sums exports over
destinations and writes
  <output>/exports_hs6.parquet   year, iso3, hs6, v (thousand USD)
  <output>/population.parquet    year, iso3, pop (thousands), from CEPII Gravity
  <output>/products_hs6.parquet  hs6, description
Run once; later steps read these files. Takes roughly 10-20 minutes.
"""
import re

import pandas as pd

from config import load_config

# BACI uses non-standard ISO3 codes for a few economies; map them for the
# population merge with CEPII Gravity.
ISO3_FIX = {"S19": "TWN"}


def read_country_codes(folder):
    path = next(folder.glob("country_codes_V*.csv"))
    cc = pd.read_csv(path, dtype=str, keep_default_na=False)
    return dict(zip(cc["country_code"].astype(int), cc["country_iso3"]))


def read_year(path, codes):
    df = pd.read_csv(path, usecols=["t", "i", "k", "v"], dtype={"k": str})
    df["k"] = df["k"].str.strip().str.zfill(6)
    out = df.groupby(["t", "i", "k"], as_index=False)["v"].sum()
    out["iso3"] = out["i"].map(codes)
    out = out.rename(columns={"t": "year", "k": "hs6"})
    return out[["year", "iso3", "hs6", "v"]]


def build_population(cfg):
    folder = cfg["data"]["gravity_raw"]
    path = next(p for p in folder.glob("Gravity_V*.csv"))
    pop = pd.read_csv(path, usecols=["year", "iso3_o", "pop_o"])
    pop = (pop.dropna().groupby(["year", "iso3_o"], as_index=False)["pop_o"].max()
           .rename(columns={"iso3_o": "iso3", "pop_o": "pop"}))
    return pop


def main():
    cfg = load_config()
    raw = cfg["data"]["baci_raw"]
    out = cfg["output"]
    codes = read_country_codes(raw)
    y0, y1 = cfg["years"]["start"], cfg["years"]["end"]

    files = sorted(raw.glob("BACI_HS92_Y*_V*.csv"))
    frames = []
    for f in files:
        year = int(re.search(r"_Y(\d{4})_", f.name).group(1))
        if y0 <= year <= y1:
            print(f"reading {f.name}")
            frames.append(read_year(f, codes))
    exports = pd.concat(frames, ignore_index=True)
    missing = exports["iso3"].isna().sum()
    if missing:
        print(f"warning: {missing} rows with unknown country code dropped")
        exports = exports.dropna(subset=["iso3"])
    exports["iso3"] = exports["iso3"].replace(ISO3_FIX)
    exports.to_parquet(out / "exports_hs6.parquet", index=False)
    print(f"exports: {len(exports):,} rows, years {exports.year.min()}-{exports.year.max()}")

    prod_file = next(raw.glob("product_codes_HS92_V*.csv"), None)
    if prod_file is not None:
        prods = pd.read_csv(prod_file, dtype=str)
        prods.columns = ["hs6", "description"]
        prods["hs6"] = prods["hs6"].str.zfill(6)
        prods.to_parquet(out / "products_hs6.parquet", index=False)

    pop = build_population(cfg)
    pop.to_parquet(out / "population.parquet", index=False)
    print(f"population: {pop.iso3.nunique()} countries, years {pop.year.min()}-{pop.year.max()}")


if __name__ == "__main__":
    main()
