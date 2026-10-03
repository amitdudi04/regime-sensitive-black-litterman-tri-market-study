from pipelines.tri_market_pipeline import run_tri_market_study


def main():
    print("Regime-Sensitive Black-Litterman Portfolio Allocation")
    packet = run_tri_market_study()
    print("\nTri-market summary:")
    print(packet["summary"].to_string(index=False))
    print("\nGenerated files: results/generated/")


if __name__ == "__main__":
    main()
