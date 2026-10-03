import numpy as np
import pandas as pd
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression


def fit_markov_regime_model(market_returns):
    """
    Fit a two-state Markov-switching model with state-dependent variance.

    Returned smoothed probabilities are for ex-post conditional analysis.
    Smoothed probabilities use the full sample and must not be fed into an
    ex-ante trading decision without a separate filtered-probability design.
    """
    returns_clean = pd.Series(market_returns).dropna().sort_index()
    if len(returns_clean) < 50:
        raise ValueError("Insufficient observations for two-state regime estimation")

    model = MarkovRegression(
        returns_clean,
        k_regimes=2,
        trend="c",
        switching_variance=True,
    )
    res = model.fit(disp=False)

    vol_0 = float(res.params.get("sigma2[0]", np.nan))
    vol_1 = float(res.params.get("sigma2[1]", np.nan))
    if not np.isfinite([vol_0, vol_1]).all():
        raise RuntimeError("Could not identify finite regime variances")

    high_vol_state = 1 if vol_1 > vol_0 else 0
    low_vol_state = 1 - high_vol_state

    smoothed = res.smoothed_marginal_probabilities
    classifications = pd.DataFrame(index=returns_clean.index)
    classifications["Prob_Low_Vol"] = smoothed[low_vol_state]
    classifications["Prob_High_Vol"] = smoothed[high_vol_state]
    classifications["Regime"] = np.where(
        classifications["Prob_High_Vol"] > 0.5,
        "High_Vol",
        "Low_Vol",
    )
    return classifications, res


def compute_regime_performance(bl_returns, mv_returns, regime_classifications):
    """Compute annualized descriptive performance within ex-post regime labels."""
    df = pd.DataFrame({
        "BL_Return": pd.Series(bl_returns),
        "MV_Return": pd.Series(mv_returns),
    }).join(regime_classifications[["Regime"]], how="inner").dropna()

    rows = []
    for regime in ["Low_Vol", "High_Vol"]:
        block = df[df["Regime"] == regime]
        if block.empty:
            continue

        record = {"Regime": regime, "Observations": int(len(block))}
        for col, prefix in [("BL_Return", "BL"), ("MV_Return", "Markowitz")]:
            ann_return = float(block[col].mean() * 252.0)
            ann_vol = float(block[col].std(ddof=1) * np.sqrt(252.0))
            record[f"{prefix} Return"] = ann_return
            record[f"{prefix} Volatility"] = ann_vol
            record[f"{prefix} Sharpe"] = ann_return / ann_vol if ann_vol > 0 else np.nan
        rows.append(record)

    return pd.DataFrame(rows)
