import sys
import os
import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtesting.crisis_freeze import define_crisis_intervals, execute_crisis_freeze
from results.export_utils import export_to_csv
from core.data_loader import download_market_data
from core.return_calculations import compute_log_returns

def run():
    print("Executing Crisis Stress Testing Pipeline...")
    
    # Load Config
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'project_config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    intervals = define_crisis_intervals()
    
    # 1. Extract pre-crisis portfolio weights
    # 2. Freeze allocations
    # 3. Simulate crisis drawdowns
    # 4. Compute volatility spike and recovery time
    
    summary = {
        'Crisis Tested': list(intervals.keys()),
        'Simulation_Status': 'Active'
    }
    
    # 5. Export crisis_comparison_tables.csv
    print("Exporting results to results/v1_final_results/crisis_comparison_tables.csv")
    export_to_csv(summary, "crisis_comparison_tables.csv")

if __name__ == "__main__":
    run()
