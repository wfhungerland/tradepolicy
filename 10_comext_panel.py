"""Strand 1, step 1: monthly bilateral export panel from Eurostat Comext.

Reads the bulk files full_v2_YYYYMM.7z (January 2002 onwards) under
data.comext, keeps exports (FLOW 2) and writes
  <output>/comext/months/YYYYMM.parquet   one file per month (resumable)
  <output>/comext/exports.parquet         reporter, partner, period, sitc1, value_eur
sitc1 is the first digit of the SITC code; "T" marks the official TOTAL rows,
"X" confidential products without SITC. The script also flags months in which
the reporter DE has no intra-EU records (incomplete latest releases).
Takes roughly 1-2 hours for 2002-2026; reruns skip finished months.
Usage: python 10_comext_panel.py
"""
import re
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import py7zr

from config import load_config

COLS = ["REPORTER", "PARTNER", "TRADE_TYPE", "PRODUCT_NC", "PRODUCT_SITC", "FLOW", "VALUE_EUR"]


def process(archive: Path, target: Path) -> dict:
    tmp = Path(tempfile.mkdtemp())
    try:
        with py7zr.SevenZipFile(archive) as z:
            z.extractall(tmp)
        dat = next(tmp.glob("*.dat"))
        d = pd.read_csv(dat, usecols=COLS, dtype=str)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    period = int(re.search(r"(\d{6})", archive.name).group(1))
    d = d[d.FLOW == "2"]
    d["value_eur"] = pd.to_numeric(d.VALUE_EUR, errors="coerce").fillna(0.0)
    is_total = d.PRODUCT_NC == "TOTAL"
    first = d.PRODUCT_SITC.str[:1]
    d["sitc1"] = first.where(first.str.isdigit().fillna(False), "X")
    d.loc[is_total, "sitc1"] = "T"
    out = (d.groupby(["REPORTER", "PARTNER", "sitc1"], as_index=False)["value_eur"].sum()
           .rename(columns={"REPORTER": "reporter", "PARTNER": "partner"}))
    out["period"] = period
    out.to_parquet(target, index=False)
    de = d[d.REPORTER == "DE"]
    return {"period": period, "de_intra_rows": int((de.TRADE_TYPE == "I").sum())}


def main():
    cfg = load_config()
    src = cfg["data"]["comext"]
    out = cfg["output"] / "comext"
    months = out / "months"
    months.mkdir(parents=True, exist_ok=True)
    archives = sorted(p for p in src.rglob("full_v2_*.7z") if re.fullmatch(r"full_v2_\d{6}\.7z", p.name))
    archives = [a for a in archives if not a.name.endswith("52.7z")]  # drop annual files (month 52)
    print(f"{len(archives)} monthly files found")
    status = []
    for a in archives:
        target = months / (re.search(r"(\d{6})", a.name).group(1) + ".parquet")
        if target.exists():
            continue
        print(f"processing {a.name}")
        status.append(process(a, target))
    if status:
        st = pd.DataFrame(status)
        old = out / "status.csv"
        if old.exists():
            st = pd.concat([pd.read_csv(old), st]).drop_duplicates("period", keep="last")
        st.sort_values("period").to_csv(old, index=False)
    panel = pd.concat([pd.read_parquet(f) for f in sorted(months.glob("*.parquet"))], ignore_index=True)
    panel.to_parquet(out / "exports.parquet", index=False)
    st = pd.read_csv(out / "status.csv")
    incomplete = st.loc[st.de_intra_rows == 0, "period"].tolist()
    print(f"panel: {len(panel):,} rows, {panel.period.min()}-{panel.period.max()}")
    if incomplete:
        print(f"months without intra-EU records for DE (treated as incomplete): {incomplete}")


if __name__ == "__main__":
    main()
