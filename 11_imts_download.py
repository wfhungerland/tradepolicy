"""Strand 1, step 2: monthly bilateral exports of all countries from IMF IMTS.

Downloads IMF International Trade in Goods (IMTS, formerly DOTS), indicator
XG_FOB_USD (exports, FOB, US dollars), monthly, from January 2000, one request
per reporting country, via the IMF SDMX 2.1 API. Writes
  <output>/imts/raw/<ISO3>.csv     one file per reporter (resumable)
  <output>/imts/exports.parquet    reporter, partner, period, value_usd
Regional and world aggregates (codes G..., GX...) are dropped.
Source: IMF, International Trade in Goods (by partner country), IMTS.
Usage: python 11_imts_download.py   (a few minutes; rerun to resume)
"""
import io
import time
import urllib.request

import pandas as pd

from config import load_config

API = "https://api.imf.org/external/sdmx/2.1/data/IMF.STA,IMTS/{key}?startPeriod={start}&detail=dataonly"
HEADERS = {"Accept": "application/vnd.sdmx.data+csv", "User-Agent": "tradepolicy-research"}


def get(key: str, start: str) -> pd.DataFrame:
    req = urllib.request.Request(API.format(key=key, start=start), headers=HEADERS)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return pd.read_csv(io.BytesIO(r.read()))
        except Exception as exc:  # network hiccup: wait and retry
            if attempt == 3:
                raise
            print(f"  retry after error: {exc}")
            time.sleep(2 ** attempt * 5)


def is_aggregate(code: str) -> bool:
    return code.startswith("GX") or (code.startswith("G") and code[1:].isdigit())


def main():
    cfg = load_config()
    out = cfg["output"] / "imts"
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    # reporters: all countries that report exports to the world aggregate
    world = get(".XG_FOB_USD.G001.M", "2020-01")
    reporters = sorted(c for c in world.COUNTRY.unique() if not is_aggregate(c))
    print(f"{len(reporters)} reporters")
    for iso in reporters:
        target = raw / f"{iso}.csv"
        if target.exists():
            continue
        df = get(f"{iso}.XG_FOB_USD..M", "2000-01")
        df[["COUNTRY", "COUNTERPART_COUNTRY", "TIME_PERIOD", "OBS_VALUE"]].to_csv(target, index=False)
        print(f"{iso}: {len(df):,} rows")
        time.sleep(0.5)

    parts = [pd.read_csv(f) for f in sorted(raw.glob("*.csv"))]
    d = pd.concat(parts, ignore_index=True)
    d.columns = ["reporter", "partner", "period", "value_usd"]
    d = d[~d.partner.map(is_aggregate)]
    d["period"] = d.period.str.replace("-M", "").astype(int)
    d.to_parquet(out / "exports.parquet", index=False)
    print(f"panel: {len(d):,} rows, {d.reporter.nunique()} reporters, "
          f"{d.partner.nunique()} partners, {d.period.min()}-{d.period.max()}")


if __name__ == "__main__":
    main()
