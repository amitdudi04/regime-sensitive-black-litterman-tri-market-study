from functools import lru_cache
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pandas_datareader.data as web
from pandas_datareader.famafrench import FamaFrenchReader
import statsmodels.api as sm

FACTOR_CACHE = Path(__file__).resolve().parents[1] / "results/generated/factor_data"


class HTTPSFrenchReader(FamaFrenchReader):
    @property
    def url(self):
        return super().url.replace("http://", "https://", 1)


@lru_cache(maxsize=16)
def _download_factor_range(start: str, end: str) -> pd.DataFrame:
    """Download and normalize each French factor table once per requested date range."""
    path = FACTOR_CACHE / f"us_daily_{start}_{end}.csv"
    meta_path = path.with_suffix(".json")
    if path.is_file() and meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if hashlib.sha256(path.read_bytes()).hexdigest() != meta["sha256"]:
            raise ValueError("Factor snapshot checksum mismatch")
        return pd.read_csv(path, index_col="Date", parse_dates=True)
    ff3 = HTTPSFrenchReader("F-F_Research_Data_Factors_daily", start, end).read()[0]
    mom = HTTPSFrenchReader("F-F_Momentum_Factor_daily", start, end).read()[0]

    ff3.index = pd.to_datetime(ff3.index.astype(str))
    mom.index = pd.to_datetime(mom.index.astype(str))
    ff3 = ff3.rename(columns={"Mkt-RF": "MKT"})
    mom = mom.rename(columns={"Mom   ": "MOM", "Mom": "MOM"})

    keep_ff3 = [column for column in ["MKT", "SMB", "HML", "RF"] if column in ff3.columns]
    if "MOM" not in mom.columns:
        raise ValueError("Momentum factor column was not found in the Kenneth French response")
    factors = ff3[keep_ff3].join(mom[["MOM"]], how="inner") / 100.0

    required = {"MKT", "SMB", "HML", "MOM", "RF"}
    missing = required.difference(factors.columns)
    if missing:
        raise ValueError(f"Missing factor columns: {sorted(missing)}")
    factors = factors.sort_index()
    if factors.index.has_duplicates or not np.isfinite(factors.to_numpy()).all():
        raise ValueError("Invalid factor observations")
    FACTOR_CACHE.mkdir(parents=True, exist_ok=True)
    factors.to_csv(path, index_label="Date", float_format="%.17g")
    meta_path.write_text(json.dumps({
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Kenneth French US daily FF3 and momentum, HTTPS",
        "requested_start": start, "requested_end": end,
        "units": "decimal daily returns, source percent divided by 100",
    }, indent=2), encoding="utf-8")
    return pd.read_csv(path, index_col="Date", parse_dates=True)


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
    factors = _download_factor_range(start, end).copy()
    factors = factors.loc[factors.index.intersection(index_dates)].sort_index()

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

    if (not isinstance(hac_maxlags, int) or hac_maxlags < 0
            or portfolio_returns.index.has_duplicates):
        raise ValueError("HAC lags must be nonnegative integer and dates unique")
    portfolio_returns = portfolio_returns.dropna().sort_index()
    factors = load_factor_data(portfolio_returns.index)

    data = portfolio_returns.rename("Portfolio").to_frame().join(factors, how="inner").dropna()
    if not np.isfinite(data.to_numpy()).all():
        raise ValueError("Nonfinite factor regression input")
    if len(data) <= hac_maxlags + 5:
        raise ValueError("Insufficient observations for the requested HAC lag length")

    y = data["Portfolio"] - data["RF"]
    x = sm.add_constant(data[["MKT", "SMB", "HML", "MOM"]])

    model = sm.OLS(y, x).fit(
        cov_type="HAC",
        cov_kwds={"maxlags": int(hac_maxlags)},
    )

    alpha_daily = float(model.params["const"])
    # Stable identity for the exact aligned factor input, without redistributing
    # the external Kenneth French dataset itself.
    aligned_factors = data[["MKT", "SMB", "HML", "MOM", "RF"]].to_csv(
        float_format="%.17g", index_label="Date"
    ).encode("utf-8")
    factor_sha256 = hashlib.sha256(aligned_factors).hexdigest()
    return {
        "Model": model_name,
        "Sample Start": data.index.min().date().isoformat(),
        "Sample End": data.index.max().date().isoformat(),
        "Factor Source": "Kenneth French Data Library US daily FF3 and momentum",
        "Factor Aligned SHA256": factor_sha256,
        "Factor Values": "percent source values divided by 100 into decimal daily returns",
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
        **{f"{name}_p_value": float(model.pvalues[name]) for name in ("MKT", "SMB", "HML", "MOM")},
    }
