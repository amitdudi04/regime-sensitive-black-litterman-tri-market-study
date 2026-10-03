"""Generate charts from the latest tri-market research run."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "generated"
OUT = RESULTS / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def _require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"Required input is missing: {path}. "
            "Run python -m pipelines.run_tri_market_pipeline first."
        )
    return path


def _save(name):
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close()


def performance_figure():
    summary = pd.read_csv(_require(RESULTS / "tri_market_summary.csv"))
    subset = summary[
        summary["Model"].isin(["Black-Litterman", "Markowitz"])
    ].copy()

    markets = ["US", "China", "India"]
    x = np.arange(len(markets))
    width = 0.35

    bl = [
        float(
            subset[
                (subset.Market == market)
                & (subset.Model == "Black-Litterman")
            ]["Sharpe Ratio"].iloc[0]
        )
        for market in markets
    ]
    mv = [
        float(
            subset[
                (subset.Market == market)
                & (subset.Model == "Markowitz")
            ]["Sharpe Ratio"].iloc[0]
        )
        for market in markets
    ]

    plt.figure(figsize=(8, 4.8))
    plt.bar(x - width / 2, bl, width, label="Black-Litterman")
    plt.bar(x + width / 2, mv, width, label="Markowitz")
    plt.xticks(x, markets)
    plt.ylabel("Annualized Sharpe ratio")
    plt.title("Out-of-sample risk-adjusted performance")
    plt.legend()
    _save("sharpe_by_market.png")


def asi_figure():
    summary = pd.read_csv(_require(RESULTS / "tri_market_summary.csv"))
    subset = summary[
        summary["Model"].isin(["Black-Litterman", "Markowitz"])
    ].copy()

    markets = ["US", "China", "India"]
    x = np.arange(len(markets))
    width = 0.35

    bl = [
        float(
            subset[
                (subset.Market == market)
                & (subset.Model == "Black-Litterman")
            ]["ASI"].iloc[0]
        )
        for market in markets
    ]
    mv = [
        float(
            subset[
                (subset.Market == market)
                & (subset.Model == "Markowitz")
            ]["ASI"].iloc[0]
        )
        for market in markets
    ]

    plt.figure(figsize=(8, 4.8))
    plt.bar(x - width / 2, bl, width, label="Black-Litterman")
    plt.bar(x + width / 2, mv, width, label="Markowitz")
    plt.xticks(x, markets)
    plt.ylabel("Mean L1 weight change")
    plt.title("Allocation Stability Index")
    plt.legend()
    _save("allocation_stability_index.png")


def rolling_sharpe_figures(window=252):
    for market in ["us", "china", "india"]:
        daily = pd.read_csv(
            _require(RESULTS / market / "daily_oos_returns.csv"),
            index_col=0,
            parse_dates=True,
        )

        plt.figure(figsize=(9, 4.8))
        for column, label in [
            ("black_litterman_net", "Black-Litterman"),
            ("markowitz_net", "Markowitz"),
        ]:
            returns = daily[column].dropna()
            rolling_mean = returns.rolling(window).mean() * 252.0
            rolling_vol = returns.rolling(window).std(ddof=1) * np.sqrt(252.0)
            rolling_sharpe = rolling_mean / rolling_vol
            plt.plot(rolling_sharpe.index, rolling_sharpe, label=label)

        plt.axhline(0.0, linewidth=0.8)
        plt.ylabel("Rolling annualized Sharpe")
        plt.title(f"{market.upper()} — {window}-day rolling Sharpe")
        plt.legend()
        _save(f"{market}_rolling_sharpe.png")


def factor_figure():
    factors = pd.read_csv(_require(RESULTS / "factor_regression_us.csv"))
    if "Factor_Regression_Error" in factors:
        factors = factors[factors["Factor_Regression_Error"].isna()]
    if factors.empty:
        raise RuntimeError("No successful factor-regression rows are available.")

    beta_cols = ["MKT_beta", "SMB_beta", "HML_beta", "MOM_beta"]
    labels = ["MKT", "SMB", "HML", "MOM"]
    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 4.8))
    for offset, model in [
        (-width / 2, "Black-Litterman"),
        (width / 2, "Markowitz"),
    ]:
        row = factors[factors["Model"] == model]
        if row.empty:
            continue
        values = [float(row[col].iloc[0]) for col in beta_cols]
        plt.bar(x + offset, values, width, label=model)

    plt.xticks(x, labels)
    plt.ylabel("Factor beta")
    plt.title("US four-factor exposure")
    plt.legend()
    _save("factor_exposure.png")


def main():
    performance_figure()
    asi_figure()
    rolling_sharpe_figures()
    factor_figure()
    print(f"Figures written to {OUT}")


if __name__ == "__main__":
    main()
