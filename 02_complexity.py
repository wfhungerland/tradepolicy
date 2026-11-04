"""Step 2: compute complexity measures for the main specification.

Main run: HS4, RCA >= 1, 3-year centred moving average, fixed panel.
Writes to <output>/complexity_<level>/:
  countries.parquet          year x country: exports, diversity, ECI, COI, fitness, ...
  products.parquet           year x product: ubiquity, PCI, fitness-complexity
  country_products.parquet   year x product for Germany and peers: RCA, M, density, COG
  proximity_last_year.parquet
Usage: python 02_complexity.py           (HS4, main run)
       python 02_complexity.py hs6       (HS6 run)
"""
import sys

from config import load_config
import panel


def main(level="hs4"):
    cfg = load_config()
    res = panel.run(cfg, {"level": level})
    out = cfg["output"] / f"complexity_{level}"
    out.mkdir(exist_ok=True)
    res["countries"].to_parquet(out / "countries.parquet", index=False)
    res["products"].to_parquet(out / "products.parquet", index=False)
    res["country_products"].to_parquet(out / "country_products.parquet", index=False)
    res["proximity_last"].to_parquet(out / "proximity_last_year.parquet")
    print(f"{level}: {res['n_countries']} countries, {res['n_products']} products -> {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hs4")
