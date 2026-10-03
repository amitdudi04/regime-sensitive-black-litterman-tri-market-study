import numpy as np
import pandas as pd
from scipy.optimize import minimize


def compute_mean_variance_weights(
    expected_returns,
    cov_matrix,
    risk_aversion=3.0,
    min_weight=0.0,
    max_weight=1.0,
):
    """
    Solve the same long-only, fully-invested mean-variance utility problem for
    every expected-return model.

    max_w  w' mu - (lambda/2) w' Sigma w

    Keeping the objective and constraints identical is essential: the empirical
    BL-vs-Markowitz comparison should differ through expected returns, not through
    model-specific regularization.
    """
    expected_returns = pd.Series(expected_returns, dtype=float)
    cov = pd.DataFrame(
        cov_matrix,
        index=expected_returns.index,
        columns=expected_returns.index,
        dtype=float,
    )

    n = len(expected_returns)
    if n == 0:
        raise ValueError("expected_returns cannot be empty")
    if min_weight * n > 1.0 or max_weight * n < 1.0:
        raise ValueError("Weight bounds are incompatible with a fully invested portfolio")

    init_guess = np.repeat(1.0 / n, n)
    bounds = tuple((float(min_weight), float(max_weight)) for _ in range(n))
    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1.0},)

    mu = expected_returns.to_numpy()
    sigma = cov.to_numpy()

    def objective(w):
        port_return = float(np.dot(w, mu))
        port_var = float(w @ sigma @ w)
        return -(port_return - (float(risk_aversion) / 2.0) * port_var)

    result = minimize(
        objective,
        init_guess,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not result.success:
        raise RuntimeError(f"SLSQP portfolio optimization failed: {result.message}")

    weights = pd.Series(result.x, index=expected_returns.index, dtype=float)
    if not np.isfinite(weights.values).all():
        raise RuntimeError("Optimizer returned non-finite weights")
    if abs(float(weights.sum()) - 1.0) > 1e-7:
        raise RuntimeError("Optimizer returned a portfolio that is not fully invested")
    return weights


def compute_black_litterman_weights(
    posterior_returns,
    cov_matrix,
    lambda_risk_aversion=3.0,
    min_weight=0.0,
    max_weight=1.0,
):
    """Apply the identical optimizer to Black-Litterman posterior returns."""
    return compute_mean_variance_weights(
        posterior_returns,
        cov_matrix,
        risk_aversion=lambda_risk_aversion,
        min_weight=min_weight,
        max_weight=max_weight,
    )
