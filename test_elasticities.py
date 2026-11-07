"""Simulation test for elasticities.py (run: pytest test_elasticities.py)."""
import numpy as np

import elasticities as el


def simulate(sigma, omega, n_var=40, n_years=13, seed=0):
    """CES demand s_it = (p_it / P_t)^(1 - sigma) with variety demand shocks, and export
    supply p_it = exp(omega * ln q_it + supply shock); solved jointly (Feenstra 1994)."""
    rng = np.random.default_rng(seed)
    # identification needs shock variances that differ across varieties (Feenstra 1994)
    sd_d = rng.uniform(0.05, 0.6, n_var)[:, None]
    sd_s = rng.uniform(0.05, 0.6, n_var)[:, None]
    beta_d = (rng.normal(0, 1, (n_var, n_years)) * sd_d).cumsum(axis=1)     # demand shifters
    beta_s = (rng.normal(0, 1, (n_var, n_years)) * sd_s).cumsum(axis=1)     # supply shifters
    rows = []
    E = 1000.0
    for t in range(n_years):
        # fixed point: x = ln q, ln p = omega x + bs; ln s = (1 - sigma) ln p + bd - ln sum
        lp = beta_s[:, t].copy()
        for _ in range(500):
            a = (1 - sigma) * lp + beta_d[:, t]
            s = np.exp(a - a.max()); s /= s.sum()
            lq = np.log(s * E) - lp
            lp_new = omega * lq + beta_s[:, t]
            if np.max(np.abs(lp_new - lp)) < 1e-12:
                break
            lp = 0.5 * lp + 0.5 * lp_new
        for i in range(n_var):
            rows.append((t, i, s[i] * E, s[i] * E / np.exp(lp[i])))
    t, e, v, q = map(np.array, zip(*rows))
    return t, e, v, q


def test_recovers_sigma():
    # median over replications within 10 %; single draws scatter (T = 12 years)
    for sigma, omega in [(3.0, 0.3), (10.0, 0.2), (5.0, 0.1)]:
        est = [el.estimate(*simulate(sigma, omega, n_var=60, seed=seed))["sigma"] for seed in range(8)]
        assert abs(np.log(np.median(est) / sigma)) < 0.10, (sigma, est)


def test_too_few_varieties():
    t, e, v, q = simulate(4.0, 0.3, n_var=4)
    assert el.estimate(t, e, v, q) is None
