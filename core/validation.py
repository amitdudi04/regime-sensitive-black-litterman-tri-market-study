"""Explicit input contracts; never impute or silently delete investment observations."""
import numpy as np
import pandas as pd


def validate_panel(frame, *, kind="returns", allow_missing=False):
    frame = pd.DataFrame(frame, dtype=float).copy()
    if frame.empty or frame.columns.has_duplicates:
        raise ValueError("Panel must be nonempty with unique asset columns")
    idx = frame.index
    if (not isinstance(idx, pd.DatetimeIndex) or idx.hasnans or idx.has_duplicates
            or not idx.is_monotonic_increasing or idx.tz is not None):
        raise ValueError("Panel requires ordered, unique, timezone-naive dates without NaT")
    values = frame.to_numpy()
    observed = values[~np.isnan(values)] if allow_missing else values
    if not np.isfinite(observed).all():
        raise ValueError("Panel contains missing or nonfinite observations")
    if kind == "prices" and (observed <= 0).any():
        raise ValueError("Adjusted prices must be positive")
    if kind == "returns" and (observed <= -1).any():
        raise ValueError("Simple returns must be greater than -100%")
    return frame


def covariance_matrix(cov, assets=None):
    matrix = pd.DataFrame(cov, dtype=float)
    if isinstance(cov, pd.DataFrame):
        if (cov.index.has_duplicates or cov.columns.has_duplicates
                or set(cov.index) != set(cov.columns)):
            raise ValueError("Covariance requires matching unique asset labels")
        if assets is not None and set(assets) != set(cov.index):
            raise ValueError("Covariance assets do not match expected returns")
        order = list(assets) if assets is not None else list(cov.index)
        matrix = matrix.loc[order, order]
    elif assets is not None:
        matrix = pd.DataFrame(cov, index=assets, columns=assets, dtype=float)
    values = matrix.to_numpy()
    if (not len(matrix) or values.shape[0] != values.shape[1]
            or not np.isfinite(values).all()):
        raise ValueError("Covariance must be finite, nonempty and square")
    scale = max(float(np.max(np.abs(values))), np.finfo(float).tiny)
    if (not np.allclose(values, values.T, rtol=0, atol=1e-12 * scale)
            or np.linalg.eigvalsh(values).min() < -1e-12 * scale):
        raise ValueError("Covariance must be symmetric positive semidefinite")
    return matrix


def normalized_weights(weights):
    weights = pd.DataFrame(weights, dtype=float)
    if (weights.empty or weights.columns.has_duplicates
            or not np.isfinite(weights.to_numpy()).all()
            or (weights < -1e-10).any().any()
            or not np.allclose(weights.sum(axis=1), 1, atol=1e-7, rtol=0)):
        raise ValueError("Weights must be finite, long-only, fully invested with unique assets")
    return weights
