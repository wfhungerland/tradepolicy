"""Checks of forecast.py. Run: python -m pytest test_forecast.py"""
import numpy as np
import pandas as pd

import forecast as fc


def gravity_data(i_n=6, j_n=9, t_n=30, seed=1):
    rng = np.random.default_rng(seed)
    a = rng.normal(0, 0.5, (i_n, 1)) + 0.01 * np.arange(t_n)[None, :]
    g = rng.normal(0, 0.5, (j_n, 1)) + 0.1 * np.sin(np.arange(t_n) / 3)[None, :]
    m = rng.normal(0, 1, (i_n, j_n))
    mu = np.exp(a[:, None, :] + g[None, :, :] + m[:, :, None]) * 50
    x = rng.poisson(mu).astype(float)
    x[0, 1, :] = 0.0  # a pair that never trades
    return x


def test_ppml_fe3_matches_pyfixest():
    import pyfixest as pf

    x = gravity_data()
    a, g, m = fc.ppml_fe3(x, tol=1e-12)
    fitted = np.exp(a[:, None, :] + g[None, :, :] + m[:, :, None])
    i, j, t = np.indices(x.shape)
    df = pd.DataFrame({"y": x.ravel(), "it": (i * 100 + t).ravel(), "jt": (j * 100 + t).ravel(),
                       "ij": (i * 100 + j).ravel()})
    keep = x.sum(axis=2)[i, j].ravel() > 0
    fit = pf.fepois("y ~ 1 | it + jt + ij", data=df[keep])
    ref = np.asarray(fit.predict(type="response"))
    ours = np.where(np.isfinite(fitted), fitted, 0.0).ravel()[keep]
    assert np.allclose(ours, ref, rtol=1e-5, atol=1e-6)


def test_margins_hold_with_mask():
    x = gravity_data()
    mask = np.ones_like(x, dtype=bool)
    mask[2, 3, 5:10] = False
    a, g, m = fc.ppml_fe3(x, mask, tol=1e-12)
    fit = np.exp(a[:, None, :] + g[None, :, :] + m[:, :, None]) * mask
    fit = np.nan_to_num(fit)
    obs = np.where(mask, x, 0)
    assert np.allclose(fit.sum(axis=1), obs.sum(axis=1), rtol=1e-6)
    assert np.allclose(fit.sum(axis=0), obs.sum(axis=0), rtol=1e-6)


def test_ar_yoy_recovers_ar_process():
    rng = np.random.default_rng(0)
    n = 300
    g = np.zeros(n)
    for s in range(1, n):
        g[s] = 0.8 * g[s - 1] + rng.normal(0, 0.01)
    season = np.tile(np.linspace(0, 0.3, 12), n // 12 + 1)[:n]
    y = season.copy()
    for s in range(12, n):
        y[s] = y[s - 12] + g[s]
    t = n - 2
    f = fc.ar_yoy(y, t, 1, p=1)
    assert abs(f - (y[t + 1 - 12] + 0.8 * g[t])) < 0.01


def test_dm_detects_better_model():
    rng = np.random.default_rng(3)
    e_good = rng.normal(0, 1, 200)
    e_bad = rng.normal(0, 2, 200)
    stat, p = fc.diebold_mariano(e_good, e_bad, 1)
    assert stat < 0 and p < 0.01
