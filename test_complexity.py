"""Checks of complexity.py on synthetic data. Run: python -m pytest test_complexity.py"""
import numpy as np
from scipy.stats import spearmanr

import complexity as cx


def synthetic(n_c=60, n_p=300, seed=0):
    """Nested export structure: capable countries export more, complex products are rare."""
    rng = np.random.default_rng(seed)
    cap = rng.uniform(0, 1, n_c)
    req = rng.uniform(0, 1, n_p)
    prob = 1 / (1 + np.exp(-12 * (cap[:, None] - req[None, :])))
    size = rng.lognormal(0, 1, (n_c, n_p))
    return np.where(rng.uniform(size=prob.shape) < prob, size * 100, 0.0) + 1e-3, cap


def reference_eci_pci(m):
    """py-ecomplexity approach: eigenvector of Mpp via np.linalg.eig."""
    kc, kp = m.sum(1), m.sum(0)
    m1, m2 = m / kc[:, None], m / kp[None, :]
    mpp = m2.T @ m1
    vals, vecs = np.linalg.eig(mpp)
    kpv = np.real(vecs[:, np.real(vals).argsort()[-2]])
    kcv = m1 @ kpv
    s = np.sign(np.corrcoef(kc, kcv)[0, 1])
    kcv, kpv = s * kcv, s * kpv
    return (kcv - kcv.mean()) / kcv.std(), (kpv - kcv.mean()) / kcv.std()


def test_eci_matches_reference():
    x, _ = synthetic()
    m = cx.mcp(cx.rca(x))
    eci, pci = cx.eci_pci(m)
    ref_eci, _ = reference_eci_pci(m)
    assert np.allclose(eci, ref_eci, atol=1e-8)


def test_eci_is_mean_pci_of_exports():
    x, _ = synthetic()
    m = cx.mcp(cx.rca(x))
    eci, pci = cx.eci_pci(m)
    assert np.allclose(eci, (m @ pci) / m.sum(1), atol=1e-8)


def test_eci_recovers_capability_and_reflections_agree():
    x, cap = synthetic()
    m = cx.mcp(cx.rca(x))
    eci, _ = cx.eci_pci(m)
    assert spearmanr(eci, cap).statistic > 0.9
    assert spearmanr(eci, cx.eci_reflections(m, 30)).statistic > 0.99


def test_proximity_density_ranges():
    x, _ = synthetic()
    m = cx.mcp(cx.rca(x))
    phi = cx.proximity(m)
    d = cx.density(m, phi)
    assert np.allclose(phi, phi.T) and phi.min() >= 0 and phi.max() <= 1
    assert d.min() >= 0 and d.max() <= 1 + 1e-12


def test_cog_matches_reference_formula():
    x, _ = synthetic(20, 50)
    m = cx.mcp(cx.rca(x))
    _, pci = cx.eci_pci(m)
    phi = cx.proximity(m)
    d = cx.density(m, phi)
    _, cog = cx.coi_cog(m, phi, d, pci)
    ref = (1 - m) * ((1 - m) @ (phi * (pci / phi.sum(axis=1))[:, None]))
    assert np.allclose(cog, ref)
    c, p = 3, 7
    manual = (1 - m[c, p]) * sum((1 - m[c, q]) * phi[q, p] / phi[q].sum() * pci[q] for q in range(50))
    assert np.isclose(cog[c, p], manual)


def test_fitness_correlates_with_eci():
    x, _ = synthetic()
    m = cx.mcp(cx.rca(x))
    eci, _ = cx.eci_pci(m)
    fit, _ = cx.fitness_complexity(m)
    assert spearmanr(eci, fit).statistic > 0.7


def test_genepy_matches_reference_and_recovers_capability():
    x, cap = synthetic()
    m = cx.mcp(cx.rca(x))
    g = cx.genepy(m)
    # reference: direct transcription of the published formula
    kc = m.sum(1)
    kp1 = (m / kc[:, None]).sum(0)
    w = m / np.outer(kc, kp1)
    n = w @ w.T
    np.fill_diagonal(n, 0)
    vals, vecs = np.linalg.eigh(n)
    o = np.argsort(vals)[::-1][:2]
    lam, xv = vals[o], vecs[:, o]
    ref = np.array([(lam[0] * abs(xv[c, 0]) ** 2 + lam[1] * xv[c, 1] ** 2) ** 2
                    + 2 * (lam[0] ** 2 * xv[c, 0] ** 2 + lam[1] ** 2 * xv[c, 1] ** 2)
                    for c in range(m.shape[0])])
    assert np.allclose(g, ref)
    assert spearmanr(g, cap).statistic > 0.7
