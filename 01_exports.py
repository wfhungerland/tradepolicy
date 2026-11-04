"""Step 1: build country x HS6 x year export totals from the BACI raw CSV files.

Reads every BACI_HS92_Y*_V*.csv in data.baci_raw, sums exports over
destinations and writes
  <output>/exports_hs6.parquet   year, iso3, hs6, v (thousand USD)
  <output>/population.parquet    year, iso3, pop (thousands), from CEPII Gravity
  <output>/products_hs6.parquet  hs6, description
Run once; later steps read these files. Takes roughly 10-20 minutes.
An existing exports_hs6.parquet is reused; pass --force to rebuild it.
"""
import re
import sys

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


def find_gravity_file(cfg):
    """Look for the CEPII Gravity file (CSV, Stata or Parquet), also in subfolders."""
    folders = [cfg["data"]["gravity_raw"], cfg["data"]["gravity"]]
    for folder in folders:
        for pattern in ("Gravity_V*.csv", "Gravity_V*.dta", "Gravity_V*.parquet",
                        "*ravity*.csv", "*ravity*.dta", "*ravity*.parquet"):
            hits = sorted(folder.rglob(pattern))
            if hits:
                return hits[0]
    listing = "\n".join(f"  {f}" for d in folders for f in sorted(d.rglob("*"))[:30])
    raise FileNotFoundError(
        "No CEPII Gravity file (csv/dta/parquet) found in the gravity folders. "
        f"Files seen:\n{listing}"
    )


def build_population(cfg):
    path = find_gravity_file(cfg)
    print(f"population from {path}")
    cols = ["year", "iso3_o", "pop_o"]
    if path.suffix == ".csv":
        pop = pd.read_csv(path, usecols=cols)
    elif path.suffix == ".dta":
        pop = pd.read_stata(path, columns=cols)
    else:
        pop = pd.read_parquet(path, columns=cols)
    pop = (pop.dropna().groupby(["year", "iso3_o"], as_index=False)["pop_o"].max()
           .rename(columns={"iso3_o": "iso3", "pop_o": "pop"}))
    return pop


def main():
    cfg = load_config()
    raw = cfg["data"]["baci_raw"]
    out = cfg["output"]
    codes = read_country_codes(raw)
    y0, y1 = cfg["years"]["start"], cfg["years"]["end"]

    target = out / "exports_hs6.parquet"
    if target.exists() and "--force" not in sys.argv:
        print(f"{target.name} exists, skipping BACI (use --force to rebuild)")
    else:
        build_exports(raw, codes, y0, y1, target)

    prod_file = next(raw.glob("product_codes_HS92_V*.csv"), None)
    if prod_file is not None:
        prods = pd.read_csv(prod_file, dtype=str)
        prods.columns = ["hs6", "description"]
        prods["hs6"] = prods["hs6"].str.zfill(6)
        prods.to_parquet(out / "products_hs6.parquet", index=False)

    pop = build_population(cfg)
    pop.to_parquet(out / "population.parquet", index=False)
    print(f"population: {pop.iso3.nunique()} countries, years {pop.year.min()}-{pop.year.max()}")


def build_exports(raw, codes, y0, y1, target):
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
    exports.to_parquet(target, index=False)
    print(f"exports: {len(exports):,} rows, years {exports.year.min()}-{exports.year.max()}")


if __name__ == "__main__":
    main()
