"""Forecasting tools for strand 1: benchmarks, gravity with fixed effects, tests.

Conventions
- Series are monthly log levels y_t (natural log of export values).
- All models forecast the year-on-year log change g_t = y_t - y_{t-12} and map it
  back to levels: y_hat_{t+h} = y_{t+h-12} + g_hat_{t+h}. This handles
  seasonality without seasonal adjustment and works for horizons h <= 12.
- An "origin" t is the last month whose data the forecaster knows.

Models
- naive_yoy: no change in year-on-year growth (g_hat_{t+h} = g_t).
- ar_yoy: direct AR(p) on g, one regression per horizon, p chosen by BIC.
- gravity: structural gravity with exporter-month, importer-month and pair
  fixed effects, estimated by Poisson pseudo-maximum likelihood on a rolling
  window; the exporter and importer effects are forecast with ar_yoy and
  combined with the pair effects.

With only fixed effects on the right-hand side, the PPML first-order conditions
are the three margins (exporter-month, importer-month and pair totals of fitted
equal observed flows). They are solved by iterative proportional fitting, which
gives the same estimates as ppmlhdfe or pyfixest (see test_forecast.py).
"""
import numpy as np
import pandas as pd

MAX_LAGS = 6


# --------------------------------------------------------------------------
# univariate benchmarks
# --------------------------------------------------------------------------

def yoy(y: np.ndarray) -> np.ndarray:
    g = np.full_like(y, np.nan, dtype=float)
    g[12:] = y[12:] - y[:-12]
    return g


def naive_yoy(y: np.ndarray, t: int, h: int) -> float:
    """Forecast of y[t+h] using data up to t: unchanged year-on-year growth."""
    return y[t + h - 12] + (y[t] - y[t - 12])


def _ols(x, z):
    beta, *_ = np.linalg.lstsq(x, z, rcond=None)
    resid = z - x @ beta
    return beta, resid


def ar_yoy(y: np.ndarray, t: int, h: int, p: int | None = None, start: int = 0) -> float:
    """Direct AR forecast of y[t+h] from data y[start..t].

    g_{s+h} = c + sum_{k<p} phi_k g_{s-k} + e, estimated on all s with s+h <= t.
    If p is None it is chosen by BIC among 1..MAX_LAGS.
    """
    g = yoy(y[: t + 1])
    first = start + 12
    best = None
    lags = [p] if p is not None else range(1, MAX_LAGS + 1)
    for q in lags:
        s_idx = np.arange(first + q - 1, t - h + 1)
        if len(s_idx) < 3 * q + 10:
            continue
        x = np.column_stack([np.ones(len(s_idx))] + [g[s_idx - k] for k in range(q)])
        z = g[s_idx + h]
        beta, resid = _ols(x, z)
        n = len(z)
        bic = n * np.log(resid @ resid / n) + (q + 1) * np.log(n)
        if best is None or bic < best[0]:
            xt = np.concatenate([[1.0], [g[t - k] for k in range(q)]])
            best = (bic, xt @ beta)
    if best is None:
        return naive_yoy(y, t, h)
    return y[t + h - 12] + best[1]


# --------------------------------------------------------------------------
# gravity with high-dimensional fixed effects
# --------------------------------------------------------------------------

def ppml_fe3(x: np.ndarray, mask: np.ndarray | None = None, tol: float = 1e-9,
             max_iter: int = 2000):
    """PPML with exporter-time, importer-time and pair fixed effects.

    x: flows, array (exporters, importers, periods), zeros allowed.
    mask: boolean array of the same shape, True where the flow is observed.
    Returns log effects (a, g, m) with shapes (I, T), (J, T), (I, J) such that
    E[x_ijt] = exp(a_it + g_jt + m_ij). Importer effects are normalised to mean
    zero across importers in every period; pairs with no positive flow in the
    window get m = -inf.
    """
    x = np.asarray(x, dtype=float)
    if mask is None:
        mask = np.isfinite(x)
    w = mask.astype(float)
    x = np.where(mask, x, 0.0)
    i_n, j_n, t_n = x.shape
    A = np.ones((i_n, t_n))
    G = np.ones((j_n, t_n))
    P = np.ones((i_n, j_n))
    tot_it = x.sum(axis=1)
    tot_jt = x.sum(axis=0)
    tot_ij = x.sum(axis=2)
    P[tot_ij == 0] = 0.0
    for _ in range(max_iter):
        fit = A[:, None, :] * G[None, :, :] * P[:, :, None] * w
        s = fit.sum(axis=1)
        A = np.where(s > 0, A * tot_it / np.where(s > 0, s, 1), A)
        fit = A[:, None, :] * G[None, :, :] * P[:, :, None] * w
        s = fit.sum(axis=0)
        G = np.where(s > 0, G * tot_jt / np.where(s > 0, s, 1), G)
        fit = A[:, None, :] * G[None, :, :] * P[:, :, None] * w
        s = fit.sum(axis=2)
        ratio = np.where(s > 0, tot_ij / np.where(s > 0, s, 1), 0.0)
        P = P * ratio
        dev = np.abs(fit.sum(axis=1) - tot_it).max() / max(tot_it.max(), 1e-12)
        if dev < tol:
            break
    with np.errstate(divide="ignore"):
        a, g, m = np.log(A), np.log(G), np.log(P)
    # normalise: importer effects mean zero across importers with finite values
    g_fin = np.where(np.isfinite(g), g, np.nan)
    c = np.nanmean(g_fin, axis=0)
    g = g - c[None, :]
    a = a + c[None, :]
    return a, g, m


def gravity_forecast(x: np.ndarray, mask: np.ndarray, h: int, p: int | None = 2):
    """Forecast all flows h periods after the last period of x.

    Fixed effects are estimated on the whole window x (I, J, W) and each
    exporter and importer effect series is forecast with ar_yoy.
    Returns an (I, J) array of forecast flows.
    """
    return gravity_from_fe(*ppml_fe3(x, mask), h, p)


def gravity_from_fe(a, g, m, h: int, p: int | None = 2):
    """Forecast flows h periods ahead from estimated log fixed effects."""
    t = a.shape[1] - 1
    a_hat = np.array([ar_yoy(row, t, h, p) if np.isfinite(row).all() else np.nan for row in a])
    g_hat = np.array([ar_yoy(row, t, h, p) if np.isfinite(row).all() else np.nan for row in g])
    with np.errstate(invalid="ignore"):
        out = np.exp(a_hat[:, None] + g_hat[None, :] + m)
    return np.nan_to_num(out, nan=0.0)


# --------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------

def diebold_mariano(e1: np.ndarray, e2: np.ndarray, h: int) -> tuple[float, float]:
    """Diebold-Mariano test of equal squared-error loss, with the
    Harvey-Leybourne-Newbold small-sample correction. Negative statistic:
    model 1 more accurate. Returns (statistic, two-sided p-value)."""
    from scipy.stats import t as student_t

    d = e1 ** 2 - e2 ** 2
    d = d[np.isfinite(d)]
    n = len(d)
    dm = d.mean()
    dc = d - dm
    lrv = dc @ dc / n
    for k in range(1, h):
        lrv += 2 * (dc[k:] @ dc[:-k]) / n
    stat = dm / np.sqrt(lrv / n)
    stat *= np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    pval = 2 * student_t.sf(abs(stat), df=n - 1)
    return float(stat), float(pval)


def summarise_errors(errors: pd.DataFrame, benchmark: str, h_col: str = "h") -> pd.DataFrame:
    """RMSE by model and horizon, relative RMSE and DM test against benchmark.

    errors: columns [h_col, 'origin', model_1, model_2, ...] with forecast errors.
    """
    rows = []
    models = [c for c in errors.columns if c not in (h_col, "origin")]
    for h, g in errors.groupby(h_col):
        base = g[benchmark].to_numpy()
        rmse_b = np.sqrt(np.nanmean(base ** 2))
        for mdl in models:
            e = g[mdl].to_numpy()
            rmse = np.sqrt(np.nanmean(e ** 2))
            stat, pval = (np.nan, np.nan) if mdl == benchmark else diebold_mariano(e, base, int(h))
            rows.append({h_col: h, "model": mdl, "n": int(np.isfinite(e).sum()), "rmse": rmse,
                         "rel_rmse": rmse / rmse_b, "dm_stat": stat, "dm_pvalue": pval})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# out-of-sample evaluation
# --------------------------------------------------------------------------

def to_cube(df: pd.DataFrame, value: str, exporters: list, partners: list, periods: list):
    """Long data (reporter, partner, period, value) to array (I, J, T) and mask.

    Cells without a record are treated as observed zeros when the reporter
    reports anything in that period, and as missing otherwise.
    """
    idx = pd.MultiIndex.from_product([exporters, partners, periods],
                                     names=["reporter", "partner", "period"])
    s = df.set_index(["reporter", "partner", "period"])[value]
    s = s.groupby(level=[0, 1, 2]).sum().reindex(idx)
    cube = s.to_numpy().reshape(len(exporters), len(partners), len(periods))
    reported = np.isfinite(cube).any(axis=1, keepdims=True)
    mask = np.broadcast_to(reported, cube.shape).copy()
    cube = np.where(mask, np.nan_to_num(cube, nan=0.0), np.nan)
    for k, p in enumerate(partners):  # no self-trade
        if p in exporters:
            mask[exporters.index(p), k, :] = False
    return cube, mask


def evaluate(cube, mask, periods, focus, first_origin, horizons=(1, 2, 3, 6), window=60,
             top_partners=30, log_every=12):
    """Pseudo out-of-sample forecasts of the focus exporters' total exports.

    cube, mask: (I, J, T) flows and observation mask; periods: list of T labels;
    focus: list of exporter indices whose summed exports are the target;
    first_origin: index of the first forecast origin.
    Models: naive_yoy and ar_yoy on the total, bottom_up (ar_yoy on each of the
    top partners plus the rest), gravity (PPML fixed effects on a rolling window).
    Returns (total_forecasts, partner_forecasts) as long DataFrames with log
    forecasts and log actuals.
    """
    x = np.where(mask, cube, 0.0)
    tot = x[focus].sum(axis=(0, 1))
    y = np.log(tot)
    by_partner = x[focus].sum(axis=0)  # (J, T)
    t_n = len(periods)
    rows, prow = [], []
    for t in range(first_origin, t_n - 1):
        lo = max(0, t - window + 1)
        share = by_partner[:, lo:t + 1].sum(axis=1)
        top = [j for j in np.argsort(share)[::-1][:top_partners] if (by_partner[j, :t + 1] > 0).all()]
        rest = np.setdiff1d(np.arange(by_partner.shape[0]), top)
        series = {j: np.log(by_partner[j]) for j in top}
        series["rest"] = np.log(by_partner[rest].sum(axis=0))
        fe = ppml_fe3(cube[:, :, lo:t + 1], mask[:, :, lo:t + 1])
        for h in horizons:
            if t + h >= t_n:
                continue
            grav = gravity_from_fe(*fe, h)
            g_focus = grav[focus].sum(axis=0)
            f_bu = {k: ar_yoy(v, t, h) for k, v in series.items()}
            rows.append({
                "origin": periods[t], "target": periods[t + h], "h": h, "actual": y[t + h],
                "naive": naive_yoy(y, t, h), "ar": ar_yoy(y, t, h),
                "bottom_up": np.log(sum(np.exp(v) for v in f_bu.values())),
                "gravity": np.log(g_focus.sum()),
            })
            for j in top:
                yj = series[j]
                prow.append({
                    "origin": periods[t], "target": periods[t + h], "h": h, "partner": j,
                    "actual": yj[t + h], "naive": naive_yoy(yj, t, h), "ar": f_bu[j],
                    "gravity": np.log(g_focus[j]) if g_focus[j] > 0 else np.nan,
                })
        if log_every and (t - first_origin) % log_every == 0:
            print(f"  origin {periods[t]} done")
    return pd.DataFrame(rows), pd.DataFrame(prow)


def quarterly(fc_df: pd.DataFrame, y: pd.Series, models: list) -> pd.DataFrame:
    """Quarterly nowcasts and forecasts from monthly forecasts.

    y: monthly log actuals indexed by period (YYYYMM). For each quarter and
    information set (months of the quarter already known: 0, 1, 2) the
    quarterly log total combines known months with forecasts of the others
    made at the same origin. info 0 = forecast made at the end of the
    previous quarter. With the AR model, info 1 and 2 are the classic bridge
    approach of filling the missing months of a quarter.
    """
    lvl = np.exp(y)
    per = list(y.index)
    out = []
    for k, p in enumerate(per):
        if p % 100 not in (3, 6, 9, 12):
            continue
        months = per[k - 2:k + 1] if k >= 2 else None
        if months is None:
            continue
        for known in (0, 1, 2):
            origin = per[per.index(months[0]) - 1 + known]
            f = fc_df[fc_df.origin == origin]
            if f.empty:
                continue
            rec = {"quarter": p, "known_months": known,
                   "actual": np.log(lvl.loc[months].sum())}
            ok = True
            for mdl in models:
                total = lvl.loc[months[:known]].sum()
                for m in months[known:]:
                    r = f[f.target == m]
                    if r.empty:
                        ok = False
                        break
                    total += np.exp(r[mdl].iloc[0])
                rec[mdl] = np.log(total) if ok else np.nan
            if ok:
                out.append(rec)
    return pd.DataFrame(out)
