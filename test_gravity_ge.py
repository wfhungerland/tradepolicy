"""Tests for gravity_ge.py (run: pytest test_gravity_ge.py)."""
import numpy as np

import gravity_ge as gg


def toy(n=8, seed=0, balanced=False):
    rng = np.random.default_rng(seed)
    X = rng.uniform(1, 10, (n, n))
    if balanced:
        X = X + X.T                     # row sums = column sums: no deficits
    X[np.diag_indices(n)] *= 20
    T = np.exp(rng.normal(0, 0.3, (n, n)))
    np.fill_diagonal(T, 1.0)
    return X, T


def test_no_shock_no_change():
    X, _ = toy()
    r = gg.ge_solve(X, np.ones_like(X), 5.0)
    assert np.allclose(r["W_hat"], 1) and np.allclose(r["X_new"], X)
    t = gg.ge_tariff(X, np.zeros_like(X), np.zeros_like(X), 4.0)
    assert np.allclose(t["W_hat"], 1) and np.allclose(t["X_new"], X)


def test_market_clearing():
    X, T = toy()
    r = gg.ge_solve(X, T, 7.0)
    Y = r["p_hat"] * X.sum(axis=1)
    assert np.allclose(r["X_new"].sum(axis=1), Y, rtol=1e-9)
    assert np.isclose(r["X_new"].sum(), Y.sum())


def test_acr_welfare_formula():
    # Arkolakis, Costinot, Rodriguez-Clare (2012): W_hat = pi_jj_hat^(-1/theta)
    X, T = toy(balanced=True)
    sigma = 5.0
    r = gg.ge_solve(X, T, sigma)
    pi0 = np.diag(X) / X.sum(axis=0)
    pi1 = np.diag(r["X_new"]) / r["X_new"].sum(axis=0)
    assert np.allclose(r["W_hat"], (pi1 / pi0) ** (-1 / (sigma - 1)), rtol=1e-8)


def test_tariff_solver_matches_cost_shock_without_revenue():
    # baseline tariffs zero and no new tariffs, a pure cost shock with balanced
    # trade: the tariff solver must reproduce ge_solve
    X, T = toy(balanced=True)
    theta = 4.0
    z = np.zeros_like(X)
    a = gg.ge_solve(X, T, theta + 1)
    b = gg.ge_tariff(X, z, z, theta, T_hat=T)
    assert np.allclose(a["W_hat"], b["W_hat"], rtol=1e-8)
    assert np.allclose(a["X_new"], b["X_new"], rtol=1e-8)


def test_tariff_hurts_target_and_raises_revenue():
    X, _ = toy(balanced=True)
    tau0 = np.zeros_like(X)
    tau1 = tau0.copy()
    tau1[1:, 0] = 0.25                  # country 0 taxes all imports
    r = gg.ge_tariff(X, tau0, tau1, 4.0)
    assert r["revenue"][0] > 0
    assert np.all(r["W_hat"][1:] < 1)   # partners lose
    assert r["exports_hat"][0] < 1      # importer's own exports fall too


def test_sinkhorn_margins():
    X, T = toy()
    Y, E = X.sum(axis=1), X.sum(axis=0)
    F = gg.sinkhorn(T, Y, E)
    assert np.allclose(F.sum(axis=1), Y) and np.allclose(F.sum(axis=0), E)
