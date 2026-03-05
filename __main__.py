import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(__file__))

# Enable module running capabilities
if __name__ == "__main__":
    print("Regime-Sensitive Black–Litterman Tri-Market Portfolio Allocation Study")
    print("Please execute a specific module pipeline.")
    print("Example: python -m pipelines.run_tri_market_pipeline")
