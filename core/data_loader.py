import time

import numpy as np
import pandas as pd
import yfinance as yf
from core.validation import validate_panel


def _extract_adjusted_close(data: pd.DataFrame, tickers):
    """Return a single price matrix with one column per requested ticker."""
    if data is None or len(data) == 0:
        return pd.DataFrame()

    tickers = list(tickers)

    if isinstance(data.columns, pd.MultiIndex):
        level0 = data.columns.get_level_values(0)
        if "Adj Close" in level0:
            prices = data["Adj Close"].copy()
        else:
            raise ValueError("Required Adj Close field unavailable; raw Close is not an adjusted proxy")
    else:
        if "Adj Close" in data.columns:
            prices = data[["Adj Close"]].copy()
            prices.columns = [tickers[0]]
        else:
            raise ValueError("Required Adj Close field unavailable; ambiguous field-only data rejected")

    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    prices = prices.reindex(columns=[ticker for ticker in tickers if ticker in prices.columns])
    # Provider ordering can be normalized; duplicate dates and invalid prices cannot.
    prices = prices.sort_index()
    validate_panel(prices, kind="prices", allow_missing=True)

    # Keep row-level missing values until the complete requested universe is assembled.
    # The final downloader drops dates on the common observed trading calendar only after
    # individually retried tickers have been joined.
    return prices


def download_market_data(tickers, start_date, end_date):
    """
    Download adjusted closing prices for the requested instruments.

    The bulk request is attempted first. If Yahoo returns only a subset of tickers,
    missing instruments are retried individually. A partial universe is never returned:
    every requested ticker must be present before the common observed calendar is built.
    Missing prices are not forward-filled.
    """
    requested = list(tickers)
    if not requested or len(set(requested)) != len(requested):
        raise ValueError("tickers must be a non-empty list of unique symbols")

    try:
        data = yf.download(
            requested,
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
        )
        prices = _extract_adjusted_close(data, requested)
    except Exception:
        prices = pd.DataFrame()

    downloaded = {
        ticker: prices[[ticker]].copy()
        for ticker in requested
        if ticker in prices.columns and prices[ticker].notna().any()
    }
    missing = [ticker for ticker in requested if ticker not in downloaded]

    for ticker in missing:
        last_error = None
        for attempt in range(2):
            try:
                single_data = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    auto_adjust=False,
                    progress=False,
                )
                single_prices = _extract_adjusted_close(single_data, [ticker])
                if ticker in single_prices.columns and single_prices[ticker].notna().any():
                    downloaded[ticker] = single_prices[[ticker]].copy()
                    break
                last_error = RuntimeError("Yahoo returned no usable price rows")
            except Exception as exc:
                last_error = exc
            if attempt == 0:
                time.sleep(0.5)
        if ticker not in downloaded:
            raise RuntimeError(
                f"Market-data download failed for required ticker {ticker!r} "
                f"between {start_date} and {end_date}; no partial universe was returned. "
                f"Last error: {last_error}"
            ) from last_error

    result = pd.concat([downloaded[ticker] for ticker in requested], axis=1)
    result = result.reindex(columns=requested).sort_index().dropna(how="any")
    if result.empty:
        raise RuntimeError(
            f"No common observed trading dates for {requested} between {start_date} and {end_date}"
        )
    validate_panel(result, kind="prices")
    if (result.index < pd.Timestamp(start_date)).any() or (result.index >= pd.Timestamp(end_date)).any():
        raise ValueError("Provider returned dates outside the requested interval")
    result.attrs["alignment"] = {
        ticker: {"first_observed": frame[ticker].first_valid_index().date().isoformat(),
                 "last_observed": frame[ticker].last_valid_index().date().isoformat(),
                 "observed_count": int(frame[ticker].notna().sum()),
                 "missing_rows_before_common_alignment": int(frame[ticker].isna().sum())}
        for ticker, frame in downloaded.items()
    }
    return result
