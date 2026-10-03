"""Backward-compatible entry point for the canonical paper-v1 reconciliation run."""

from pipelines.paper_v1_pipeline import run_paper_v1_study


def run():
    packet = run_paper_v1_study()
    print("Recomputed tri-market outputs written to results/recomputed/")
    print(packet["summary"].to_string(index=False))


if __name__ == "__main__":
    run()
