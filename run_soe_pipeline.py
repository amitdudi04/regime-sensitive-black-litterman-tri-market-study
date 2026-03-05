import os
import json
import pandas as pd
import yfinance as yf
from core.soe_private_analysis import (
    run_china_soe_pipeline, run_china_private_pipeline, run_combined_china_pipeline,
    _hypothesis_tests, run_crisis_structural_tests, generate_structural_summary,
    export_study_tables
)
from core.ownership_classification import SOE_TICKERS, PRIVATE_TICKERS

def main():
    print("Initializing SOE vs Private Portfolio Analysis...")
    os.makedirs('results', exist_ok=True)
    
    # Use china_asset_universe.csv
    univ = pd.read_csv('results/china_asset_universe.csv')
    csv_tickers = univ['Ticker'].dropna().tolist()
    
    # Add hardcoded universe from classification just in case
    all_tickers = list(set(SOE_TICKERS + PRIVATE_TICKERS + csv_tickers))
    
    print(f"Downloading prices for {len(all_tickers)} tickers...")
    data = yf.download(all_tickers, start='2010-01-01', end='2025-01-01', progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        level_0 = data.columns.get_level_values(0)
        level_1 = data.columns.get_level_values(1)
        if "Adj Close" in level_0:
            prices = data["Adj Close"]
        elif "Close" in level_0:
            prices = data["Close"]
        elif "Adj Close" in level_1:
            prices = data.xs("Adj Close", axis=1, level=1)
        elif "Close" in level_1:
            prices = data.xs("Close", axis=1, level=1)
        else:
            raise ValueError(f"No valid price column for {all_tickers}")
    else:
        if "Adj Close" in data.columns:
            prices = data["Adj Close"]
        elif "Close" in data.columns:
            prices = data["Close"]
        else:
            raise ValueError(f"No valid price column for {all_tickers}")
            
    assert prices.shape[0] > 0, "Downloaded DataFrame is empty (rows)"
    assert prices.shape[1] > 0, "Downloaded DataFrame is empty (columns)"

    print("Running Pipelines (SOE, Private, Combined)...")
    # Crisis period is 2015-2016, so let's run main pipeline from 2017 to avoid overlap if desired, 
    # but empirical_study uses 2010-2025 for overall backtest. Let's use 2010 to 2025.
    soe_res = run_china_soe_pipeline(prices, start_date='2010-01-01', end_date='2025-01-01')
    priv_res = run_china_private_pipeline(prices, start_date='2010-01-01', end_date='2025-01-01')
    comb_res = run_combined_china_pipeline(prices, start_date='2010-01-01', end_date='2025-01-01')
    
    metrics_summary = {
        'soe': {'metrics': soe_res['metrics']},
        'private': {'metrics': priv_res['metrics']},
        'combined': {'metrics': comb_res['metrics']}
    }
    
    print("1. Exporting Summary CSV, Excel report, and LaTeX tables...")
    latex_str = export_study_tables(metrics_summary, 'results/soe_vs_private')
    with open('results/latex_tables_output.tex', 'w') as f:
        f.write(latex_str)
        
    print("2. Running Statistical hypothesis tests...")
    tests = _hypothesis_tests(soe_res, priv_res)
    with open('results/statistical_test_output.json', 'w') as f:
        json.dump(tests, f, indent=4)
        
    print("3. Generating Crisis comparison tables...")
    crisis_res = run_crisis_structural_tests(prices)
    
    rows = []
    for universe_name, data_ in crisis_res.items():
        row = {'Universe': universe_name}
        row.update(data_['crisis_metrics'])
        rows.append(row)
    df_crisis = pd.DataFrame(rows)
    df_crisis.to_csv('results/crisis_comparison_tables.csv', index=False)
    
    print("4. Generating Structural interpretation output...")
    summary_text = generate_structural_summary(soe_res['metrics'], priv_res['metrics'], tests)
    with open('results/structural_interpretation_output.txt', 'w') as f:
        f.write(summary_text)

    print("\nSUCCESS! All requested outputs generated in results/:")
    print(" - Summary CSV (results/soe_vs_private_china_ownership_summary_china_ownership_summary.csv)")
    print(" - Excel report (results/soe_vs_private.xlsx)")
    print(" - LaTeX tables (results/latex_tables_output.tex)")
    print(" - Statistical test output (results/statistical_test_output.json)")
    print(" - Crisis comparison tables (results/crisis_comparison_tables.csv)")
    print(" - Structural interpretation output (results/structural_interpretation_output.txt)")

if __name__ == '__main__':
    main()
