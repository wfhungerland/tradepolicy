# Gravity for short-horizon trade forecasts

Results of strand 1. The literature review is in `literature_gravity_nowcasting.md`; the code is `forecast.py` and `10_comext_panel.py` to `13_forecast_world.py`.

## Question and design

Can a gravity model with high-dimensional fixed effects forecast monthly or quarterly trade better than simple benchmarks? The review found no study that tests this directly and argued that, with exporter-time and importer-time fixed effects, all time variation sits in the fixed effects, so a gravity forecast is only as good as the forecast of those effects. The test below makes that argument operational.

- **Gravity model.** PPML with exporter-month, importer-month and pair fixed effects, estimated on a rolling 60-month window at every forecast origin. Estimates equal those of pyfixest (`test_forecast.py`). Exporter and importer effects are forecast with the same AR model as the benchmark, then combined with the pair effects into bilateral flows and summed to the target.
- **Benchmarks.** Naive (unchanged year-on-year growth, the "last value" in a seasonal series), direct AR on year-on-year growth with lags chosen by BIC, and bottom-up AR (AR forecasts by destination, summed). Quarterly nowcasts with one or two months of the quarter known fill the missing months with model forecasts; with AR this is the bridge approach.
- **Evaluation.** Forecast origins December 2014 to the last month; horizons 1, 2, 3 and 6 months; errors in log points times 100 (about percent); RMSE relative to AR; Diebold-Mariano tests with the Harvey-Leybourne-Newbold correction. Data are the current vintage (pseudo real time): revisions are ignored, which favours all models equally.

## World trade (IMF IMTS)

Monthly exports of 210 reporters to 214 partners, USD, January 2002 to July 2026. Target: total exports of the 203 reporters with complete data (100% of 2019 world exports). 139 forecast origins.

Relative RMSE against AR (below 1 = better than AR), full sample:

| Horizon | Naive | Bottom-up AR | Gravity |
|---|---|---|---|
| 1 month | 0.98 | 0.97 | 1.03 |
| 2 months | 0.95 | 0.94 | 0.98 |
| 3 months | 0.94 | 0.93 | 0.97 |
| 6 months | 1.04 | 0.95 | 1.18 |

AR RMSE: 5.6% at one month, 10.7% at six months. No difference to AR is significant at the 10% level. Excluding March 2020 to June 2021 gives the same picture: gravity between 0.88 and 1.12 of AR, never significantly better; bottom-up AR is the best model at two to six months (0.86 to 0.91, p = 0.09 at three months).

Quarterly (46 quarters):

| Months of the quarter known | Naive | Bridge (AR) RMSE | Bottom-up AR | Gravity |
|---|---|---|---|---|
| 0 (forecast) | 0.99 | 5.5% | 0.99 | 1.13 |
| 1 | 1.22 | 2.6% | 0.97 | 1.19 |
| 2 | 0.91 | 2.1% | 0.92 | 0.93 |

Gravity is worse than the bridge equation when one month of the quarter is known (1.19, p = 0.11) and when no month is known (1.13).

## Germany (Comext)

Pending: the full Comext panel (EU27 exporters x partners, EUR) is built on the local machine with `10_comext_panel.py`, followed by `12_forecast_germany.py`. A dry run of the same code on IMF data for the EU27 (USD, which adds exchange-rate noise) gave the same ranking: gravity 1.01 to 1.14 of AR, significantly worse at one month (p = 0.01); bottom-up AR 0.92 to 1.00; gravity better than AR for the minority of partners (27% to 47% of the 30 largest, depending on the horizon).

## Assessment so far

Gravity with three-way fixed effects does not improve on univariate benchmarks for aggregate trade at monthly or quarterly horizons, and it is clearly worse at six months, where errors in forecasting many exporter and importer effects add up. This matches the literature review. The modest gains of the bottom-up AR suggest that, if anything helps, it is disaggregation by destination, not the gravity structure.

Caveats: values are nominal (USD or EUR), so price and exchange-rate movements are part of the target; the evaluation ignores revisions and publication lags; the model has no time-varying covariates (tariffs, sanctions), where gravity could add information in scenario forecasts after policy shocks.
