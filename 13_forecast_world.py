"""Strand 1, step 4: can gravity forecast world trade? Out-of-sample test.

Data: IMF IMTS panel from 11_imts_download.py (all reporters x partners,
monthly, USD). Target: total exports of a fixed set of reporters with complete
data from 2002 to the last evaluation month (most of world trade). Same
models, horizons and evaluation as 12_forecast_germany.py; the bottom-up model
aggregates AR forecasts by destination.
Writes to <output>/forecast_world/: forecasts_total.parquet, quarterly.parquet,
  summary_monthly.csv, summary_monthly_excl_covid.csv, summary_quarterly.csv
Usage: python 13_forecast_world.py [max_reporters]
       (all reporters: about 1-2 hours; a number limits the panel to the
       largest exporters, for a quick test)
"""
import sys

import numpy as np
import pandas as pd

import forecast as fc
from config import load_config

FIRST_ORIGIN = 201412
START = 200201
COVERAGE = 0.9  # last month in which reporters with >= 90% of 2019 exports have data
COVID = (202003, 202106)
MODELS = ["naive", "ar", "bottom_up", "gravity"]


def main(max_reporters=None):
    cfg = load_config()
    out = cfg["output"] / "forecast_world"
    out.mkdir(exist_ok=True)
    d = pd.read_parquet(cfg["output"] / "imts" / "exports.parquet")
    d = d[(d.period >= START) & (d.value_usd > 0)]

    size = d[d.period // 100 == 2019].groupby("reporter").value_usd.sum().sort_values(ascending=False)
    reporters = list(size.index[:max_reporters]) if max_reporters else list(size.index)
    d = d[d.reporter.isin(reporters)]
    cover = d.groupby(["period", "reporter"]).value_usd.sum().gt(0).unstack(fill_value=False)
    share = cover.mul(size.reindex(cover.columns).fillna(0)).sum(axis=1) / size.reindex(cover.columns).sum()
    last = share[share >= COVERAGE].index.max()
    periods = sorted(p for p in d.period.unique() if p <= last)
    complete = [r for r in reporters if r in cover.columns and cover.reindex(periods)[r].fillna(False).all()]
    partners = sorted(d.partner.unique())
    cube, mask = fc.to_cube(d[d.period <= last], "value_usd", reporters, partners, periods)
    focus = [reporters.index(r) for r in complete]
    wshare = size.reindex(complete).sum() / size.sum()
    print(f"{len(reporters)} reporters ({len(complete)} complete, {wshare:.0%} of 2019 exports), "
          f"{len(partners)} partners, {periods[0]}-{periods[-1]}")

    tot, _ = fc.evaluate(cube, mask, periods, focus, periods.index(FIRST_ORIGIN))
    tot.to_parquet(out / "forecasts_total.parquet", index=False)
    err = tot[["origin", "h"]].copy()
    for m in MODELS:
        err[m] = (tot[m] - tot.actual) * 100
    fc.summarise_errors(err, "ar").to_csv(out / "summary_monthly.csv", index=False)
    calm = ~tot.target.between(*COVID)
    fc.summarise_errors(err[calm], "ar").to_csv(out / "summary_monthly_excl_covid.csv", index=False)

    y = pd.Series(np.log(np.where(mask, cube, 0)[focus].sum(axis=(0, 1))), index=periods)
    q = fc.quarterly(tot, y, MODELS)
    q.to_parquet(out / "quarterly.parquet", index=False)
    qe = q[["quarter", "known_months"]].rename(columns={"known_months": "h", "quarter": "origin"})
    for m in MODELS:
        qe[m] = (q[m] - q.actual) * 100
    fc.summarise_errors(qe, "ar").rename(columns={"h": "known_months"}).to_csv(
        out / "summary_quarterly.csv", index=False)
    print(pd.read_csv(out / "summary_monthly.csv").round(3).to_string(index=False))
    print(pd.read_csv(out / "summary_quarterly.csv").round(3).to_string(index=False))
    print(f"results -> {out}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
