import pandas as pd


def segment_soe_private(china_equities_df, ownership_mapping_dict):
    """Split available Chinese equity columns into explicitly mapped SOE/private groups."""
    soe_tickers = [
        ticker for ticker, classification in ownership_mapping_dict.items()
        if classification == "SOE"
    ]
    private_tickers = [
        ticker for ticker, classification in ownership_mapping_dict.items()
        if classification == "Private"
    ]

    available = set(china_equities_df.columns)
    soe_df = china_equities_df[[ticker for ticker in soe_tickers if ticker in available]]
    private_df = china_equities_df[
        [ticker for ticker in private_tickers if ticker in available]
    ]
    return soe_df, private_df


def evaluate_structural_segment(returns_df):
    """
    Compute simple descriptive return and volatility summaries for a segment.

    This helper is not a complete SOE-vs-private hypothesis test and should not be
    treated as a reproduction of the working-paper ownership results.
    """
    returns_df = pd.DataFrame(returns_df).dropna(how="all")
    if returns_df.empty:
        raise ValueError("returns_df contains no usable observations")

    volatility = returns_df.std(ddof=1) * (252 ** 0.5)
    total_return = (1.0 + returns_df).prod() - 1.0

    return {
        "Return": float(total_return.mean()),
        "Volatility": float(volatility.mean()),
        "Assets": int(returns_df.shape[1]),
        "Observations": int(returns_df.shape[0]),
    }
