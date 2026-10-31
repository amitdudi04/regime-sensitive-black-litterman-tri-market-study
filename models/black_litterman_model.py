import numpy as np
import pandas as pd
from core.validation import covariance_matrix


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
    sigma = covariance_matrix(cov_matrix)
    if isinstance(equilibrium_weights, pd.Series):
        if equilibrium_weights.index.has_duplicates or set(equilibrium_weights.index) != set(sigma.index):
            raise ValueError("Prior assets must match covariance assets")
        equilibrium_weights = equilibrium_weights.reindex(sigma.index)
    w = np.asarray(equilibrium_weights, dtype=float)
    if w.ndim != 1 or (w < 0).any() or not np.isfinite(lambda_risk_aversion) or lambda_risk_aversion <= 0:
        raise ValueError("Prior must be nonnegative and risk aversion finite positive")

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
    if tau is None or not np.isfinite(tau) or float(tau) <= 0:
        raise ValueError("tau must be strictly positive")

    sigma_df = covariance_matrix(cov_matrix)
    sigma = sigma_df.to_numpy()
    pi = pd.Series(pi, index=sigma_df.index, dtype=float)
    if not np.isfinite(pi).all():
        raise ValueError("Prior returns must be finite and cover every asset")

    if P is None or len(P) == 0:
        return pi.copy()

    P = np.asarray(P, dtype=float)
    Q = np.asarray(Q, dtype=float)
    Omega = np.asarray(Omega, dtype=float)
    if (P.ndim != 2 or Q.ndim != 1 or Omega.ndim != 2
            or not all(np.isfinite(x).all() for x in (P, Q, Omega))):
        raise ValueError("Views require finite P matrix, Q vector and Omega matrix")

    if P.shape[1] != sigma.shape[0]:
        raise ValueError("P column count must match covariance dimension")
    if P.shape[0] != len(Q):
        raise ValueError("P row count must match Q length")
    if Omega.shape != (len(Q), len(Q)):
        raise ValueError("Omega must be square with dimension equal to number of views")

    covariance_matrix(Omega)
    if np.linalg.eigvalsh(Omega).min() <= 0:
        raise ValueError("Omega must be positive definite")
    # Gaussian conditioning identity avoids inverses and supports singular PSD Sigma.
    prior_cov = float(tau) * sigma
    posterior = pi.to_numpy() + prior_cov @ P.T @ np.linalg.solve(
        Omega + P @ prior_cov @ P.T, Q - P @ pi.to_numpy()
    )

    return pd.Series(posterior, index=sigma_df.index, dtype=float)
