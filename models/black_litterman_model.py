import numpy as np
import pandas as pd


def compute_implied_equilibrium_returns(
    cov_matrix,
    equilibrium_weights,
    lambda_risk_aversion,
):
    """
    Compute Black-Litterman equilibrium-implied returns:

        Pi = lambda * Sigma * w_eq

    equilibrium_weights may contain a justified capitalization/AUM prior or an
    explicitly labelled proxy. The function does not infer market capitalization
    from price or trading volume.
    """
    sigma = pd.DataFrame(cov_matrix, dtype=float)
    w = np.asarray(equilibrium_weights, dtype=float)

    if sigma.shape[0] != sigma.shape[1]:
        raise ValueError("cov_matrix must be square")
    if len(w) != sigma.shape[0]:
        raise ValueError("equilibrium_weights length must match covariance dimension")
    if not np.isfinite(w).all() or w.sum() <= 0:
        raise ValueError("equilibrium_weights must be finite with positive total weight")

    w = w / w.sum()
    pi = float(lambda_risk_aversion) * sigma.to_numpy().dot(w)
    return pd.Series(pi, index=sigma.index, dtype=float)


def compute_black_litterman_posterior(pi, cov_matrix, P, Q, Omega, tau):
    """Compute the Black-Litterman posterior expected-return vector."""
    if tau is None or float(tau) <= 0:
        raise ValueError("tau must be strictly positive")

    sigma_df = pd.DataFrame(cov_matrix, dtype=float)
    sigma = sigma_df.to_numpy()
    pi = pd.Series(pi, index=sigma_df.index, dtype=float)

    if P is None or len(P) == 0:
        return pi.copy()

    P = np.asarray(P, dtype=float)
    Q = np.asarray(Q, dtype=float)
    Omega = np.asarray(Omega, dtype=float)

    if P.shape[1] != sigma.shape[0]:
        raise ValueError("P column count must match covariance dimension")
    if P.shape[0] != len(Q):
        raise ValueError("P row count must match Q length")
    if Omega.shape != (len(Q), len(Q)):
        raise ValueError("Omega must be square with dimension equal to number of views")

    inv_tau_sigma = np.linalg.inv(float(tau) * sigma)
    inv_omega = np.linalg.inv(Omega)

    precision = inv_tau_sigma + P.T @ inv_omega @ P
    rhs = inv_tau_sigma @ pi.to_numpy() + P.T @ inv_omega @ Q
    posterior = np.linalg.solve(precision, rhs)

    return pd.Series(posterior, index=sigma_df.index, dtype=float)
