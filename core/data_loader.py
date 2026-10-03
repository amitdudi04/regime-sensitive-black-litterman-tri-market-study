import pandas as pd
import numpy as np
import yfinance as yf


def _extract_adjusted_close(data: pd.DataFrame, tickers):
    """Return a single price matrix with one column per requested ticker."""
    if data is None or len(data) == 0:
        return pd.DataFrame()

    tickers = list(tickers)

    if isinstance(data.columns, pd.MultiIndex):
        level0 = data.columns.get_level_values(0)
        if "Adj Close" in level0:
            prices = data["Adj Close"].copy()
        elif "Close" in level0:
            prices = data["Close"].copy()
        else:
            raise ValueError("Yahoo Finance response does not contain Adj Close or Close data.")
    else:
        if "Adj Close" in data.columns:
            prices = data[["Adj Close"]].copy()
            prices.columns = [tickers[0]]
        elif "Close" in data.columns:
            prices = data[["Close"]].copy()
            prices.columns = [tickers[0]]
        else:
            # yfinance may return ticker-labelled columns for a single field.
            available = [t for t in tickers if t in data.columns]
            if not available:
                raise ValueError("Yahoo Finance response does not contain a recognized price column.")
            prices = data[available].copy()

    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])

    prices = prices.reindex(columns=[t for t in tickers if t in prices.columns])
    prices = prices.sort_index().replace([np.inf, -np.inf], np.nan)

    # Research rule: do not manufacture prices by forward-filling missing observations.
    # The canonical backtest operates on the common observed trading calendar.
    prices = prices.dropna(how="any")
    return prices


def download_market_data(tickers, start_date, end_date):
    """
    Download adjusted closing prices for the requested instruments.

    Missing prices are not forward-filled. The returned frame contains only dates for
    which every requested instrument has an observed price, preventing artificial
    zero-return observations from entering the empirical backtest.
    """
    try:
        data = yf.download(
            list(tickers),
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
        )
        return _extract_adjusted_close(data, tickers)
    except Exception as exc:
        raise RuntimeError(
            f"Market-data download failed for {list(tickers)} "
            f"between {start_date} and {end_date}: {exc}"
        ) from exc
