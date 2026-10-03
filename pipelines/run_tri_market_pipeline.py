"""Command-line entry point for the tri-market portfolio study."""

from pipelines.tri_market_pipeline import run_tri_market_study


def run():
    packet = run_tri_market_study()
    print(packet["summary"].to_string(index=False))
    print("\nGenerated files: results/generated/")


if __name__ == "__main__":
    run()
