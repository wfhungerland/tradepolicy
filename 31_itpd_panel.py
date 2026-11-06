"""Convert ITPD-E R2025 (8.7 GB CSV inside the zip) to compact Parquet files.

Reads the zip in streaming batches, so memory use stays low. Writes to
<output>/scenarios:
  itpd_industry.parquet  exporter, importer, year, industry_id, trade
                         (million USD; zeros and names dropped)
  itpd_industries.csv    industry_id, broad_sector, industry_descr
  itpd_countries.csv     iso3, name, first and last year
  itpd_broad.parquet     exporter, importer, year, broad_sector, trade
                         (4 broad sectors, including domestic flows)

ITPD-E uses static ISO3 codes (exporter_iso3) next to dynamic ones for
countries that split or merged (exporter_iso3_dynamic). We keep the static code.
Usage: python 31_itpd_panel.py
"""
import zipfile

import pandas as pd
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

from config import load_config

ZIP_NAME = "ITPD_E_R2025.zip"
CSV_NAME = "ITPD_E_R2025.csv"
KEEP = ["exporter_iso3", "importer_iso3", "year", "industry_id", "trade"]


def main():
    cfg = load_config()
    out = cfg["output"] / "scenarios"
    out.mkdir(parents=True, exist_ok=True)
    src = cfg["data"]["scenarios"] / ZIP_NAME

    schema = pa.schema([("exporter", pa.string()), ("importer", pa.string()),
                        ("year", pa.int16()), ("industry_id", pa.int16()), ("trade", pa.float64())])
    writer = pq.ParquetWriter(out / "itpd_industry.parquet", schema, compression="zstd")
    industries, countries, broad_parts = {}, {}, []
    n_rows = 0
    convert = pacsv.ConvertOptions(column_types={"year": pa.int16(), "industry_id": pa.int16(),
                                                 "trade": pa.float64()})
    with zipfile.ZipFile(src) as z, z.open(CSV_NAME) as f:
        reader = pacsv.open_csv(f, read_options=pacsv.ReadOptions(block_size=64 << 20),
                                convert_options=convert)
        for batch in reader:
            df = batch.to_pandas()
            n_rows += len(df)
            for r in df.drop_duplicates("industry_id")[["industry_id", "broad_sector", "industry_descr"]].itertuples():
                industries.setdefault(r.industry_id, (r.broad_sector, r.industry_descr))
            for side in ("exporter", "importer"):
                g = df.groupby([f"{side}_iso3", f"{side}_name"])["year"].agg(["min", "max"])
                for (iso, name), (lo, hi) in g.iterrows():
                    a, b, _ = countries.get(iso, (lo, hi, name))
                    countries[iso] = (min(a, lo), max(b, hi), name)
            broad_parts.append(df.groupby(["exporter_iso3", "importer_iso3", "year", "broad_sector"],
                                          as_index=False)["trade"].sum())
            df = df[df.trade > 0][KEEP].rename(columns={"exporter_iso3": "exporter", "importer_iso3": "importer"})
            writer.write_table(pa.Table.from_pandas(df, schema=schema, preserve_index=False))
            print(f"{n_rows / 1e6:6.1f} M rows", end="\r", flush=True)
    writer.close()
    print()

    pd.DataFrame([(k, *v) for k, v in sorted(industries.items())],
                 columns=["industry_id", "broad_sector", "industry_descr"]).to_csv(
        out / "itpd_industries.csv", index=False)
    pd.DataFrame([(k, v[2], v[0], v[1]) for k, v in sorted(countries.items())],
                 columns=["iso3", "name", "first_year", "last_year"]).to_csv(out / "itpd_countries.csv", index=False)
    broad = pd.concat(broad_parts).groupby(["exporter_iso3", "importer_iso3", "year", "broad_sector"],
                                           as_index=False)["trade"].sum()
    broad = broad.rename(columns={"exporter_iso3": "exporter", "importer_iso3": "importer"})
    broad.to_parquet(out / "itpd_broad.parquet", index=False)
    print(f"{n_rows / 1e6:.1f} M rows read, {len(industries)} industries, {len(countries)} countries")


if __name__ == "__main__":
    main()
