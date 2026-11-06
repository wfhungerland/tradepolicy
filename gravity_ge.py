"""Structural gravity: estimation helpers and general equilibrium counterfactuals.

The GE solver is the Armington endowment economy of Anderson and van Wincoop
(2003) as used in the GE-PPML procedure of Yotov, Piermartini, Monteiro and
Larch (2016, Advanced Guide, ch. 2) and Anderson, Larch and Yotov (2018,
World Economy). It is written in changes ("exact hat algebra", Dekle, Eaton
and Kortum 2008), which gives the same fixed point as iterating PPML with
fixed effects but needs only the baseline trade matrix and the change in trade
costs. 32_validate_yotov.py checks the equivalence on the book's NAFTA example.

Notation
  X      N x N baseline flows, rows exporters i, columns importers j, with
         domestic flows on the diagonal (model-consistent: use PPML fitted values)
  T_hat  N x N change in t_ij^(1-sigma), the trade cost term as it enters gravity
         (for a coefficient change: exp(b * (x_cfl - x_bln)))
  sigma  elasticity of substitution; trade elasticity is 1 - sigma
  Expenditure is E_j = phi_j * Y_j with phi_j fixed at baseline (trade
  imbalances scale with output), as in Yotov et al. (2016).

Tariffs: with tariff revenue (Caliendo and Parro 2015 style, one sector) the
function ge_tariff below adds rebated revenue to expenditure.
"""
import numpy as np
import pandas as pd


# ---------------------------------------------------------------- estimation

def fepois(df, formula, vcov=None):
    """PPML with high-dimensional fixed effects via pyfixest."""
    import pyfixest as pf
    return pf.fepois(formula, data=df, vcov=vcov or "iid")


def normalise_pair_fe(pair_fe, exporter, importer):
    """Pair fixed effects are identified only up to a_i + b_j. Shift them so
    that every domestic pair is 0 (gamma_ij - gamma_ii), as in Yotov et al."""
    s = pd.Series(pair_fe, index=pd.MultiIndex.from_arrays([exporter, importer]))
    s = s[~s.index.duplicated()]
    dom = {i: v for (i, j), v in s.items() if i == j}
    out = np.array([v - dom.get(i, np.nan) for (i, j), v in zip(zip(exporter, importer), pair_fe)])
    return out


# ---------------------------------------------------------------- GE solver

def sinkhorn(t, Y, E, tol=1e-13, max_iter=100000):
    """Flows X_ij = a_i * b_j * t_ij with row sums Y and column sums E. This is
    what PPML with exporter and importer fixed effects returns for a given
    trade cost term t (Fally 2015)."""
    a, b = np.ones(len(Y)), np.ones(len(E))
    for _ in range(max_iter):
        a_new = Y / (t @ b)
        b = E / (t.T @ a_new)
        if np.max(np.abs(a_new / a - 1)) < tol:
            a = a_new
            break
        a = a_new
    else:
        raise RuntimeError("sinkhorn did not converge")
    return a[:, None] * b[None, :] * t


def _flows(S, E, p, T_hat, sigma):
    """New flows given price changes p (vector), shares S = X/E0 (columns sum
    to 1), new expenditure E. Returns flows and P_hat^(1-sigma) per importer."""
    a = S * T_hat * (p ** (1 - sigma))[:, None]
    denom = a.sum(axis=0)
    return a / denom * E[None, :], denom


def _expenditure(phi, p, Y0):
    """E_j = phi_j * Y_j, scaled so that world expenditure equals world
    output (with phi fixed they drift apart slightly in a counterfactual)."""
    E = phi * p * Y0
    return E * (p * Y0).sum() / E.sum()


def ge_solve(X, T_hat, sigma, ref=None, conditional=False, tol=1e-12, max_iter=20000):
    """Solve the counterfactual. Returns a dict of arrays (length N unless noted):

    p_hat        factory-gate price change (= nominal output change)
    P_hat        consumer price index change
    W_hat        real GDP (welfare) change p_hat / P_hat
    X_new        N x N counterfactual flows
    exports_hat  change in total foreign sales (excl. domestic)
    Normalisation: ref (index) keeps that country's P_hat = 1, as in Yotov et
    al.; None keeps world nominal output unchanged. Real changes do not depend
    on the normalisation. conditional=True holds prices and output fixed
    (the book's "conditional GE").
    """
    X = np.asarray(X, float)
    T_hat = np.asarray(T_hat, float)
    Y0, E0 = X.sum(axis=1), X.sum(axis=0)
    phi = E0 / Y0
    S = X / E0[None, :]
    p = np.ones(len(Y0))
    if not conditional:
        for it in range(max_iter):
            Xn, _ = _flows(S, _expenditure(phi, p, Y0), p, T_hat, sigma)
            z = Xn.sum(axis=1) / (p * Y0)          # excess demand ratio
            p_new = p * z ** (1.0 / sigma)
            p_new /= (p_new * Y0).sum() / Y0.sum()  # world output numeraire
            if np.max(np.abs(p_new / p - 1)) < tol:
                p = p_new
                break
            p = p_new
        else:
            raise RuntimeError("GE solver did not converge")
    if conditional:
        # prices and output fixed; both multilateral resistances adjust, so
        # flows are X * T_hat rescaled to the baseline row and column totals
        Xn = sinkhorn(X * T_hat, Y0, E0)
        off = ~np.eye(len(Y0), dtype=bool)
        return {"p_hat": p, "P_hat": None, "W_hat": None, "X_new": Xn,
                "exports_hat": (Xn * off).sum(axis=1) / (X * off).sum(axis=1),
                "Y_hat": p, "E_hat": np.ones_like(p)}
    E = _expenditure(phi, p, Y0)
    Xn, denom = _flows(S, E, p, T_hat, sigma)
    P = denom ** (1.0 / (1 - sigma))
    if ref is not None and not conditional:
        p, P = p / P[ref], P / P[ref]
        Xn, _ = _flows(S, _expenditure(phi, p, Y0), p, T_hat, sigma)
    off = ~np.eye(len(Y0), dtype=bool)
    exports0 = (X * off).sum(axis=1)
    return {"p_hat": p, "P_hat": P, "W_hat": p / P, "X_new": Xn,
            "exports_hat": (Xn * off).sum(axis=1) / exports0,
            "Y_hat": p, "E_hat": E / E0}


def ge_tariff(X, tau0, tau1, theta, T_hat=None, tol=1e-12, max_iter=20000):
    """One-sector GE with ad valorem tariffs and rebated revenue.

    X is valued at importer (tariff-inclusive) prices; tau0, tau1 are N x N
    baseline and new tariff rates (0.25 = 25 %); theta > 0 is the trade
    elasticity with respect to tariffs (flows scale with (1+tau)^-theta, i.e.
    sigma - 1 = theta in Armington). Deficits are held fixed in levels
    relative to world output (Caliendo and Parro 2015, one sector, no input
    output). Welfare is real income: (wage income + revenue + deficit) / P.
    """
    X = np.asarray(X, float)
    tau0, tau1 = np.asarray(tau0, float), np.asarray(tau1, float)
    T_hat = np.ones_like(X) if T_hat is None else np.asarray(T_hat, float)
    n = X.shape[0]
    E0 = X.sum(axis=0)                       # gross expenditure incl. tariffs
    sales0 = (X / (1 + tau0)).sum(axis=1)    # producer revenue = output Y
    rev0 = (X * tau0 / (1 + tau0)).sum(axis=0)
    D0 = E0 - rev0 - sales0                  # deficit
    S = X / E0[None, :]
    c_hat = ((1 + tau1) / (1 + tau0)) ** (-theta) * T_hat
    w = np.ones(n)
    for it in range(max_iter):
        a = S * c_hat * (w ** (-theta))[:, None]
        share = a / a.sum(axis=0)
        # expenditure solves E = w*Y0 + D + sum_i share_ij * t_ij/(1+t_ij) * E
        keep = (share / (1 + tau1)).sum(axis=0)
        E = (w * sales0 + D0) / keep   # world output is the numeraire
        Xn = share * E[None, :]
        demand = (Xn / (1 + tau1)).sum(axis=1)
        z = demand / (w * sales0)
        w_new = w * z ** (1.0 / (1 + theta))
        w_new /= (w_new * sales0).sum() / sales0.sum()
        if np.max(np.abs(w_new / w - 1)) < tol:
            w = w_new
            break
        w = w_new
    else:
        raise RuntimeError("tariff GE solver did not converge")
    a = S * c_hat * (w ** (-theta))[:, None]
    P_hat = (a.sum(axis=0)) ** (-1.0 / theta)
    share = a / a.sum(axis=0)
    keep = (share / (1 + tau1)).sum(axis=0)
    E = (w * sales0 + D0) / keep
    Xn = share * E[None, :]
    rev1 = (Xn * tau1 / (1 + tau1)).sum(axis=0)
    inc0, inc1 = sales0 + rev0 + D0, w * sales0 + rev1 + D0
    off = ~np.eye(n, dtype=bool)
    return {"w_hat": w, "P_hat": P_hat, "W_hat": (inc1 / inc0) / P_hat, "X_new": Xn,
            "exports_hat": ((Xn / (1 + tau1)) * off).sum(axis=1) / ((X / (1 + tau0)) * off).sum(axis=1),
            "revenue": rev1, "revenue0": rev0}
