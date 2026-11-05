"""Strand 1, step 3: can gravity forecast German exports? Out-of-sample test.

Data: Comext panel from 10_comext_panel.py (EU27 exporters x all partners,
monthly, EUR). Target: Germany's total exports and its exports to the 30
largest partners. Forecast origins from FIRST_ORIGIN to the last complete
month; horizons 1, 2, 3 and 6 months; data are the current vintage
(pseudo real time, no revisions).
Models: naive (unchanged year-on-year growth), AR (direct, BIC lags),
bottom-up AR over partners, gravity (PPML with exporter-month, importer-month
and pair fixed effects on a 60-month rolling window, fixed effects forecast
with AR). Quarterly nowcasts with 0, 1 or 2 known months follow from the
monthly forecasts; with AR this is the bridge approach.
Writes to <output>/forecast_germany/:
  forecasts_total.parquet, forecasts_partners.parquet, quarterly.parquet
  summary_monthly.csv, summary_quarterly.csv, summary_partners.csv
  summary_monthly_excl_covid.csv
Usage: python 12_forecast_germany.py   (roughly 10-30 minutes)
"""
import numpy as np
import pandas as pd

import forecast as fc
from config import load_config

EU27 = ["AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR", "HU",
        "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"]
FOCUS = "DE"
FIRST_ORIGIN = 201412
COVID = (202003, 202106)
MODELS = ["naive", "ar", "bottom_up", "gravity"]


def main():
    cfg = load_config()
    src = cfg["output"] / "comext"
    out = cfg["output"] / "forecast_germany"
    out.mkdir(exist_ok=True)

    d = pd.read_parquet(src / "exports.parquet")
    d = d[(d.sitc1 == "T") & d.reporter.isin(EU27)]
    status = pd.read_csv(src / "status.csv")
    incomplete = set(status.loc[status.de_intra_rows == 0, "period"])
    periods = sorted(p for p in d.period.unique() if p not in incomplete)
    last = periods[-1]
    periods = [p for p in periods if p <= last]
    partners = sorted(d.partner.unique())
    cube, mask = fc.to_cube(d, "value_eur", EU27, partners, periods)
    first = periods.index(FIRST_ORIGIN)
    print(f"{len(EU27)} exporters, {len(partners)} partners, {periods[0]}-{periods[-1]}")

    tot, part = fc.evaluate(cube, mask, periods, [EU27.index(FOCUS)], first)
    part["partner"] = [partners[j] for j in part.partner]
    tot.to_parquet(out / "forecasts_total.parquet", index=False)
    part.to_parquet(out / "forecasts_partners.parquet", index=False)

    err = tot[["origin", "h"]].copy()
    for m in MODELS:
        err[m] = (tot[m] - tot.actual) * 100  # log points x 100 ~ percent
    fc.summarise_errors(err, "ar").to_csv(out / "summary_monthly.csv", index=False)
    calm = ~tot.target.between(*COVID)
    fc.summarise_errors(err[calm], "ar").to_csv(out / "summary_monthly_excl_covid.csv", index=False)

    y = pd.Series(np.log(np.where(mask, cube, 0)[EU27.index(FOCUS)].sum(axis=0)), index=periods)
    q = fc.quarterly(tot, y, MODELS)
    q.to_parquet(out / "quarterly.parquet", index=False)
    qe = q[["quarter", "known_months"]].rename(columns={"known_months": "h", "quarter": "origin"})
    for m in MODELS:
        qe[m] = (q[m] - q.actual) * 100
    fc.summarise_errors(qe, "ar").rename(columns={"h": "known_months"}).to_csv(
        out / "summary_quarterly.csv", index=False)

    rows = []
    for (p, h), g in part.groupby(["partner", "h"]):
        r = {m: np.sqrt(np.nanmean((g[m] - g.actual) ** 2)) for m in ["naive", "ar", "gravity"]}
        rows.append({"partner": p, "h": h, **r, "gravity_vs_ar": r["gravity"] / r["ar"]})
    ps = pd.DataFrame(rows)
    ps.to_csv(out / "summary_partners.csv", index=False)

    s = pd.read_csv(out / "summary_monthly.csv")
    print(s.round(3).to_string(index=False))
    print(pd.read_csv(out / "summary_quarterly.csv").round(3).to_string(index=False))
    print(ps.groupby("h").gravity_vs_ar.agg(["median", lambda v: (v < 1).mean()]).round(3))
    print(f"results -> {out}")


if __name__ == "__main__":
    main()
