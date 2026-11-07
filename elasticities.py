"""Import demand (substitution) elasticities between supplier countries, product by product.

Estimator of Feenstra (1994) as implemented by Broda and Weinstein (2006, QJE): for one
importer and one HS6 good, varieties are supplier countries. With a reference variety k,
first differences over years and differences to k,
  Y = (D_k ln p)^2,  X1 = (D_k ln s)^2,  X2 = (D_k ln p)(D_k ln s),
where p is the unit value and s the variety's share in the good's imports. The model of
CES demand and upward-sloping export supply implies
  Y = theta1 X1 + theta2 X2 + u,
  theta1 = rho / ((sigma - 1)^2 (1 - rho)),  theta2 = (2 rho - 1) / ((sigma - 1)(1 - rho)),
  rho = omega (sigma - 1) / (1 + omega sigma)  (omega: inverse export supply elasticity).
Estimation follows the hybrid approach of Soderbery (2015, JIE): limited information
maximum likelihood (LIML) with variety indicators as instruments, which removes most of
the small-sample bias of the original two-stage estimator, and a constant for measurement
error in unit values (Broda and Weinstein 2006). When the LIML solution is infeasible
(sigma <= 1 or rho outside [0, 1)), sigma and rho are found by a constrained grid search
on the variety means, as in Broda and Weinstein (2006). The simulation test
(test_elasticities.py, 60 varieties, 12 annual changes) recovers the median sigma within
10 % for sigma between 3 and 10 when export supply is elastic (omega <= 0.3); with steep
supply (omega = 0.5) single estimates scatter widely, a known weakness of the approach.
"""
import numpy as np

SIGMA_GRID = np.exp(np.linspace(np.log(1.05), np.log(131.5), 160))
RHO_STEPS = 60
MIN_VARIETIES = 5
MIN_YEARS = 4


def _theta(sigma, rho):
    return rho / ((sigma - 1) ** 2 * (1 - rho)), (2 * rho - 1) / ((sigma - 1) * (1 - rho))


def _from_theta(t1, t2):
    """Closed form: rho and sigma from theta1 > 0 and theta2; None if infeasible."""
    if t1 <= 0:
        return None
    disc = 0.25 - 1.0 / (4.0 + t2 * t2 / t1)
    if disc < 0:
        return None
    for rho in (0.5 + np.sqrt(disc), 0.5 - np.sqrt(disc)):
        if not 0 <= rho < 1:
            continue
        if t2 == 0:
            continue
        sigma = 1 + (2 * rho - 1) / ((1 - rho) * t2)
        if sigma > 1:
            return sigma, rho
    return None


def _wls(y, X, w):
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)
    return beta


def _liml(o):
    """LIML of Y on X1, X2 and a constant, instruments: variety indicators."""
    cols = ["Y", "X1", "X2"]
    W = o[cols].to_numpy()
    Wm = W - W.mean(axis=0)
    Wd = W - o.groupby("e")[cols].transform("mean").to_numpy()
    kappa = np.min(np.real(np.linalg.eigvals(np.linalg.solve(Wd.T @ Wd, Wm.T @ Wm))))
    X = np.column_stack([W[:, 1], W[:, 2], np.ones(len(W))])
    Xd = np.column_stack([Wd[:, 1], Wd[:, 2], np.zeros(len(W))])
    return np.linalg.solve(X.T @ (X - kappa * Xd), X.T @ (W[:, 0] - kappa * Wd[:, 0]))


def estimate(year, exporter, value, qty):
    """One importer x good. Arrays of equal length (one row per year and exporter).
    Returns dict(sigma, omega, rho, n_var, n_years, feasible) or None."""
    import pandas as pd
    d = pd.DataFrame({"t": year, "e": exporter, "v": value, "q": qty})
    d = d[(d.v > 0) & (d.q > 0)]
    if d.e.nunique() < MIN_VARIETIES + 1 or d.t.nunique() < MIN_YEARS:
        return None
    d["lp"] = np.log(d.v / d.q)
    d["ls"] = np.log(d.v / d.groupby("t").v.transform("sum"))
    d = d.sort_values(["e", "t"])
    g = d.groupby("e")
    d["dp"], d["ds"], d["dt"] = g.lp.diff(), g.ls.diff(), g.t.diff()
    d = d[d.dt == 1]
    # reference variety: present in every differenced year, largest total value
    years = d.t.unique()
    full = d.groupby("e").t.nunique()
    cand = full[full == len(years)].index
    if len(cand) == 0:
        return None
    k = d[d.e.isin(cand)].groupby("e").v.sum().idxmax()
    ref = d[d.e == k].set_index("t")[["dp", "ds"]]
    o = d[d.e != k].join(ref, on="t", rsuffix="_k").dropna()
    o["Y"] = (o.dp - o.dp_k) ** 2
    o["X1"] = (o.ds - o.ds_k) ** 2
    o["X2"] = (o.dp - o.dp_k) * (o.ds - o.ds_k)
    n_obs = o.groupby("e").Y.transform("size")
    o = o[n_obs >= MIN_YEARS - 1]
    b = o.groupby("e").agg(Y=("Y", "mean"), X1=("X1", "mean"), X2=("X2", "mean"), T=("Y", "size"))
    if len(b) < MIN_VARIETIES:
        return None
    w = b["T"].to_numpy(float) ** 1.5
    y, x1, x2 = b.Y.to_numpy(), b.X1.to_numpy(), b.X2.to_numpy()
    try:
        beta = _liml(o)
    except np.linalg.LinAlgError:
        beta = _wls(y, np.column_stack([x1, x2, np.ones_like(y)]), w)
    sol = _from_theta(beta[0], beta[1])
    feasible = sol is not None and sol[0] < SIGMA_GRID[-1]
    if not feasible:
        # constrained LIML (Soderbery 2015): minimise the ratio of between-variety to
        # within-variety residual variation over the feasible region
        eid = o.e.to_numpy()
        codes, inv = np.unique(eid, return_inverse=True)
        cnt = np.bincount(inv).astype(float)
        Yo, X1o, X2o = o.Y.to_numpy(), o.X1.to_numpy(), o.X2.to_numpy()
        best = (np.inf, None, None)
        for s in SIGMA_GRID:
            for r in np.linspace(0, 0.99 * (s - 1) / s, RHO_STEPS):
                t1, t2 = _theta(s, r)
                u = Yo - t1 * X1o - t2 * X2o
                ue = np.bincount(inv, weights=u) / cnt
                between = np.sum(cnt * (ue - u.mean()) ** 2)
                within = np.sum((u - ue[inv]) ** 2)
                obj = between / within if within > 0 else np.inf
                if obj < best[0]:
                    best = (obj, s, r)
        sol = (best[1], best[2])
    sigma, rho = sol
    omega = rho / ((sigma - 1) - rho * sigma) if (sigma - 1) - rho * sigma > 0 else np.inf
    return {"sigma": float(sigma), "rho": float(rho), "omega": float(omega), "n_var": int(len(b)),
            "n_years": int(len(years)), "feasible": bool(feasible)}
