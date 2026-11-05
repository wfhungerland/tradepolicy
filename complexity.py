"""Economic complexity measures on a country x product export matrix.

All functions take numpy arrays with countries in rows and products in columns.
Formulas follow Hidalgo et al. (2007), Hidalgo & Hausmann (2009),
Hausmann et al. (2014, Atlas of Economic Complexity) and the Growth Lab's
py-ecomplexity package. ECI/PCI use the eigenvector formulation
(Mealy, Farmer & Teytelboym 2019); see complexity_methods.md.
"""
import numpy as np


def rca(x: np.ndarray) -> np.ndarray:
    """Balassa revealed comparative advantage: (X_cp / X_c) / (X_p / X)."""
    x = np.asarray(x, dtype=float)
    total = x.sum()
    xc = x.sum(axis=1, keepdims=True)
    xp = x.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = (x / xc) / (xp / total)
    return np.nan_to_num(r)


def mcp(r: np.ndarray, threshold: float = 1.0) -> np.ndarray:
    """Binary country-product matrix: 1 if RCA >= threshold."""
    return (r >= threshold).astype(float)


def eci_pci(m: np.ndarray):
    """ECI and PCI from the eigenvector of the second largest eigenvalue.

    Returns (eci, pci). ECI is z-scored; PCI is
    scaled with ECI's moments so that ECI_c equals the mean PCI of the
    products with M_cp = 1 (py-ecomplexity convention).
    """
    kc = m.sum(axis=1)
    kp = m.sum(axis=0)
    if (kc == 0).any() or (kp == 0).any():
        raise ValueError("Zero diversity or ubiquity: drop empty rows/columns first.")
    # Mcc = D_c^-1 M D_p^-1 M' is similar to the symmetric matrix
    # S = D_c^-1/2 M D_p^-1 M' D_c^-1/2, which has the same eigenvalues.
    a = m / np.sqrt(kc)[:, None] / np.sqrt(kp)[None, :]
    s = a @ a.T
    vals, vecs = np.linalg.eigh(s)  # ascending order, real and stable
    u = vecs[:, -2]
    kc_vec = u / np.sqrt(kc)  # eigenvector of Mcc
    # Product eigenvector: PCI_p proportional to mean of ECI over exporters.
    kp_vec = (m / kp[None, :]).T @ kc_vec
    sign = np.sign(np.corrcoef(kc, kc_vec)[0, 1])
    kc_vec, kp_vec = sign * kc_vec, sign * kp_vec
    # Rescale kp so that kc = mean of kp over products with M=1 (exact identity).
    lam = vals[-2]
    kp_vec = kp_vec / lam
    mu, sd = kc_vec.mean(), kc_vec.std()
    eci = (kc_vec - mu) / sd
    pci = (kp_vec - mu) / sd
    return eci, pci


def eci_reflections(m: np.ndarray, n_iter: int = 20):
    """Method of reflections (Hidalgo & Hausmann 2009), for comparison only.

    Iterates k_c,N = mean of k_p,N-1 over a country's products and
    k_p,N = mean of k_c,N-1 over a product's exporters. Returns z-scored
    k_c,N for an even N; its ranking approaches the eigenvector ECI as N grows.
    """
    kc0 = m.sum(axis=1)
    kp0 = m.sum(axis=0)
    kc, kp = kc0.astype(float), kp0.astype(float)
    for _ in range(n_iter):
        kc, kp = (m @ kp) / kc0, (m.T @ kc) / kp0
    return (kc - kc.mean()) / kc.std()


def proximity(m: np.ndarray) -> np.ndarray:
    """Product proximity: min of the two conditional probabilities (Hidalgo et al. 2007)."""
    kp = m.sum(axis=0)
    co = m.T @ m
    with np.errstate(divide="ignore", invalid="ignore"):
        cond = co / kp[None, :]  # P(p | p')
    cond = np.nan_to_num(cond)
    phi = np.minimum(cond, cond.T)
    np.fill_diagonal(phi, 0.0)
    return phi


def density(m: np.ndarray, phi: np.ndarray) -> np.ndarray:
    """Density_cp = sum_p' M_cp' phi_pp' / sum_p' phi_pp'."""
    den = phi.sum(axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        d = (m @ phi) / den[None, :]
    return np.nan_to_num(d)


def coi_cog(m: np.ndarray, phi: np.ndarray, d: np.ndarray, pci: np.ndarray):
    """Complexity Outlook Index and Complexity Outlook Gain (Hausmann et al. 2014).

    COI_c = sum_p (1 - M_cp) d_cp PCI_p
    COG_cp = (1 - M_cp) sum_p' (1 - M_cp') phi_pp' / (sum_p'' phi_p''p') PCI_p'
    Uses standardised PCI. COI is returned unstandardised; z-score it per year.
    """
    not_m = 1.0 - m
    coi = (not_m * d * pci[None, :]).sum(axis=1)
    colsum = phi.sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        w = np.nan_to_num(pci / colsum)
    cog = not_m * (not_m @ (phi * w[:, None]))
    return coi, cog


def fitness_complexity(m: np.ndarray, n_iter: int = 200):
    """Fitness-Complexity algorithm (Tacchella et al. 2012).

    Returns (log fitness, log product complexity) after n_iter iterations,
    each normalised to mean one in every step.
    """
    f = np.ones(m.shape[0])
    q = np.ones(m.shape[1])
    for _ in range(n_iter):
        f_new = m @ q
        q_new = 1.0 / (m.T @ (1.0 / f))
        f = f_new / f_new.mean()
        q = q_new / q_new.mean()
    return np.log(f), np.log(q)


def genepy(m: np.ndarray):
    """GENEPY index of countries (Sciarra, Chiarotti, Ridolfi & Laio 2020).

    W_cp = M_cp / (k_c * k'_p) with k'_p = sum_c M_cp / k_c. The country
    proximity N = W W' (zero diagonal) gives eigenpairs (lambda_i, X_i);
    GENEPY_c = (sum_i lambda_i X_ic^2)^2 + 2 sum_i lambda_i^2 X_ic^2 for the two
    eigenvectors with the largest |lambda|. Formula checked against an
    independent implementation (lady-bluecopper/NuDHy, helpers/run_genepy.py),
    not against the published article.
    """
    kc = m.sum(axis=1)
    kp1 = (m / kc[:, None]).sum(axis=0)
    w = m / np.outer(kc, kp1)
    n = w @ w.T
    np.fill_diagonal(n, 0.0)
    vals, vecs = np.linalg.eigh(n)
    order = np.argsort(np.abs(vals))[::-1][:2]
    lam = vals[order]
    x = vecs[:, order]
    x[:, 0] = np.abs(x[:, 0])
    x2 = x ** 2
    return (x2 @ lam) ** 2 + 2 * (x2 @ lam ** 2)


def compute_year(x: np.ndarray, threshold: float = 1.0) -> dict:
    """All measures for one year. x: exports, countries x products.

    Products that no country exports with RCA >= threshold in this year get NaN
    for PCI and related measures; they are left out of the eigenvector problem.
    """
    r = rca(x)
    m_all = mcp(r, threshold)
    keep_p = m_all.sum(axis=0) > 0
    if (m_all.sum(axis=1) == 0).any():
        raise ValueError("A country has no product with RCA >= threshold: tighten the filters.")
    m = m_all[:, keep_p]
    eci, pci_k = eci_pci(m)
    phi_k = proximity(m)
    d_k = density(m, phi_k)
    coi, cog_k = coi_cog(m, phi_k, d_k, pci_k)
    fit, q_k = fitness_complexity(m)
    gen = genepy(m)

    n_c, n_p = x.shape
    pci = np.full(n_p, np.nan)
    pci[keep_p] = pci_k
    q = np.full(n_p, np.nan)
    q[keep_p] = q_k
    d = np.full((n_c, n_p), np.nan)
    d[:, keep_p] = d_k
    cog = np.full((n_c, n_p), np.nan)
    cog[:, keep_p] = cog_k
    phi = np.full((n_p, n_p), np.nan)
    phi[np.ix_(keep_p, keep_p)] = phi_k
    return {
        "rca": r, "mcp": m_all, "diversity": m_all.sum(axis=1), "ubiquity": m_all.sum(axis=0),
        "eci": eci, "pci": pci, "phi": phi, "density": d,
        "coi": (coi - coi.mean()) / coi.std(), "cog": cog,
        "fitness": fit, "fc_complexity": q, "genepy": gen,
    }
