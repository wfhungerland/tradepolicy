"""Baseline tariffs of all countries from MAcMap-HS6 2019, by ICIO sector.

MAcMap-HS6 (ITC-CEPII), as distributed by CEPII with Fontagne, Guimbard and
Orefice (2022): ad valorem equivalent of the applied (preferential) tariff by
importer, exporter and HS6 (revision 2007), 2019. The 3.6 GB CSV is read in
streaming batches from the zip.

Aggregation to importer x exporter x ICIO sector with bilateral trade weights
from BACI HS22, 2024 (mapped to HS 2007). Economies outside ICIO are folded
into ROW with the same weights. Pairs without weights get the simple mean.
Writes <output>/scenarios/macmap_2019_icio.parquet (importer, exporter, sector,
tariff, weight).
Usage: python 39_macmap_baseline.py
"""
import importlib
import zipfile

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pacsv

from config import load_config

ti = importlib.import_module("33_tariff_inputs")
YEAR = 2019
WEIGHT_YEAR = 2024


def main():
    cfg = load_config()
    src = cfg["data"]["scenarios"]
    out = cfg["output"] / "scenarios"
    _, hs07, h22_07 = ti.concordance(src / "conc")
    sector07 = dict(zip(hs07.hs07, hs07.sector))

    # bilateral BACI weights in HS 2007 codes (first HS 2007 code of each HS 2022 code)
    with zipfile.ZipFile(src / "BACI_HS22_V202601.zip") as z:
        cc = pd.read_csv(z.open(next(n for n in z.namelist() if n.startswith("country_codes"))),
                         dtype=str, keep_default_na=False)
        b = pd.read_csv(z.open(next(n for n in z.namelist() if f"_Y{WEIGHT_YEAR}_" in n)),
                        dtype={"i": str, "j": str, "k": str}, usecols=["i", "j", "k", "v"])
    iso = dict(zip(cc.country_code, cc.country_iso3.replace({"S19": "TWN"})))
    first07 = h22_07.drop_duplicates("hs22").set_index("hs22")["hs07"]
    b["hs07"] = b.k.map(first07)
    b["exporter"], b["importer"] = b.i.map(iso), b.j.map(iso)
    w = b.dropna(subset=["hs07"]).groupby(["importer", "exporter", "hs07"])["v"].sum()
    print(f"BACI weights: {len(w) / 1e6:.1f} M cells")

    icio_countries = None
    try:
        with zipfile.ZipFile(src / "icio" / "2016-2022_SML.zip") as z:
            head = pd.read_csv(z.open("2022_SML.csv"), nrows=0, index_col=0)
        icio_countries = sorted({c.split("_", 1)[0] for c in head.columns if "_" in c and c != "OUT"})
    except FileNotFoundError:
        pass
    keep = set(icio_countries or [])

    parts = []
    convert = pacsv.ConvertOptions(column_types={"importer": pa.string(), "exporter": pa.string(),
                                                 "hs6_2007": pa.string(), "year": pa.int16(), "adv": pa.float64()})
    with zipfile.ZipFile(src / "macmap" / "Tariffs_2001_2019.zip") as z, \
            z.open(f"Tariffs_2001_2019/mmhs6_{YEAR}.csv") as f:
        reader = pacsv.open_csv(f, read_options=pacsv.ReadOptions(block_size=128 << 20), convert_options=convert)
        n = 0
        for batch in reader:
            d = batch.to_pandas()
            n += len(d)
            d["sector"] = d.hs6_2007.map(sector07)
            d = d.dropna(subset=["sector", "adv"])
            d = d[d.importer != d.exporter]
            d["weight"] = w.reindex(pd.MultiIndex.from_frame(d[["importer", "exporter", "hs6_2007"]])).fillna(0.0).to_numpy()
            if keep:
                d["importer"] = d.importer.where(d.importer.isin(keep), "ROW")
                d["exporter"] = d.exporter.where(d.exporter.isin(keep), "ROW")
            d["tw"] = d.adv * d.weight
            d["one"] = 1.0
            parts.append(d.groupby(["importer", "exporter", "sector"])[["tw", "weight", "adv", "one"]].sum())
            print(f"{n / 1e6:6.1f} M rows", end="\r", flush=True)
    print()
    g = pd.concat(parts).groupby(level=[0, 1, 2]).sum()
    g["tariff"] = np.where(g.weight > 0, g.tw / g.weight.where(g.weight > 0, 1), g.adv / g.one)
    g = g.reset_index()[["importer", "exporter", "sector", "tariff", "weight"]]
    g.to_parquet(out / "macmap_2019_icio.parquet", index=False)
    avg = g.assign(tw=g.tariff * g.weight).groupby("importer")[["tw", "weight"]].sum()
    avg = (avg.tw / avg.weight * 100).round(1)
    print("trade-weighted average tariff 2019, %:", avg.reindex(["USA", "DEU", "CHN", "IND", "BRA", "JPN", "ROW"]).to_dict())


if __name__ == "__main__":
    main()
