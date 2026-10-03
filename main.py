from pipelines.paper_v1_pipeline import run_paper_v1_study


def main():
    print("Regime-Sensitive Black-Litterman Portfolio Allocation")
    print("Running canonical paper-v1 reconciliation pipeline...")
    packet = run_paper_v1_study()
    print("\nRecomputed summary:")
    print(packet["summary"].to_string(index=False))
    print("\nOutputs: results/recomputed/")


if __name__ == "__main__":
    main()
