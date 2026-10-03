import numpy as np
import pandas as pd
import pandas_datareader.data as web
import statsmodels.api as sm


def load_factor_data(index_dates):
    """
    Load US daily Fama-French 3 factors plus Momentum from the Kenneth French library.

    These are US factors. The function uses exact-date intersection only. It deliberately avoids backward
    filling because doing so can inject future factor observations into earlier dates.
    """
    index_dates = pd.DatetimeIndex(index_dates).sort_values()
    if len(index_dates) == 0:
        raise ValueError("index_dates must contain at least one date")

    start = index_dates.min().strftime("%Y-%m-%d")
    end = index_dates.max().strftime("%Y-%m-%d")

    ff3 = web.DataReader("F-F_Research_Data_Factors_daily", "famafrench", start, end)[0]
    mom = web.DataReader("F-F_Momentum_Factor_daily", "famafrench", start, end)[0]

    ff3.index = pd.to_datetime(ff3.index.astype(str))
    mom.index = pd.to_datetime(mom.index.astype(str))

    ff3 = ff3.rename(columns={"Mkt-RF": "MKT"})
    mom = mom.rename(columns={"Mom   ": "MOM", "Mom": "MOM"})

    keep_ff3 = [c for c in ["MKT", "SMB", "HML", "RF"] if c in ff3.columns]
    if "MOM" not in mom.columns:
        raise ValueError("Momentum factor column was not found in the Kenneth French response")

    factors = ff3[keep_ff3].join(mom[["MOM"]], how="inner") / 100.0
    factors = factors.loc[factors.index.intersection(index_dates)].sort_index()

    required = {"MKT", "SMB", "HML", "MOM", "RF"}
    missing = required.difference(factors.columns)
    if missing:
        raise ValueError(f"Missing factor columns: {sorted(missing)}")
    if factors.empty:
        raise ValueError("No exact trading-date overlap between portfolio returns and factor data")

    return factors


def run_factor_regression(portfolio_returns, model_name="Portfolio", hac_maxlags=5):
    """
    Estimate the daily four-factor model with Newey-West/HAC inference.

    Rp - Rf = alpha + beta_MKT*MKT + beta_SMB*SMB
              + beta_HML*HML + beta_MOM*MOM + epsilon

    Alpha is returned on both daily and annualized arithmetic scales. HAC affects
    standard errors, t-statistics and p-values; coefficient estimates remain OLS.
    """
    if not isinstance(portfolio_returns, pd.Series):
        portfolio_returns = pd.Series(portfolio_returns)

    portfolio_returns = portfolio_returns.dropna().sort_index()
    factors = load_factor_data(portfolio_returns.index)

    data = portfolio_returns.rename("Portfolio").to_frame().join(factors, how="inner").dropna()
    if len(data) <= hac_maxlags + 5:
        raise ValueError("Insufficient observations for the requested HAC lag length")

    y = data["Portfolio"] - data["RF"]
    x = sm.add_constant(data[["MKT", "SMB", "HML", "MOM"]])

    model = sm.OLS(y, x).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": int(hac_maxlags)},
    )

    alpha_daily = float(model.params["const"])
    return {
        "Model": model_name,
        "Observations": int(model.nobs),
        "HAC_MaxLags": int(hac_maxlags),
        "Alpha": alpha_daily,
        "Alpha_Annualized": alpha_daily * 252.0,
        "Alpha_t_stat": float(model.tvalues["const"]),
        "P_value_Alpha": float(model.pvalues["const"]),
        "R_squared": float(model.rsquared),
        "MKT_beta": float(model.params["MKT"]),
        "MKT_t_stat": float(model.tvalues["MKT"]),
        "SMB_beta": float(model.params["SMB"]),
        "SMB_t_stat": float(model.tvalues["SMB"]),
        "HML_beta": float(model.params["HML"]),
        "HML_t_stat": float(model.tvalues["HML"]),
        "MOM_beta": float(model.params["MOM"]),
        "MOM_t_stat": float(model.tvalues["MOM"]),
    }
