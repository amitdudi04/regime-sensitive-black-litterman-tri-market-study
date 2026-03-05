import os

def combine_files():
    files = {
        'bl': 'portfolio_optimization/models/black_litterman.py',
        'viz': 'visualizations.py',
        'bt': 'backtesting.py',
        'rob': 'robustness.py',
        'main': 'main.py',
        'emp': 'empirical_study.py'
    }
    
    contents = {}
    for name, path in files.items():
        with open(path, 'r', encoding='utf-8') as f:
            contents[name] = f.read()
            
    # Exact Safe Replacements for circular internal imports
    to_remove = [
        "from portfolio_optimization import BlackLittermanOptimizer\n",
        "from backtesting import run_comprehensive_backtest\n",
        "from robustness import (\n    run_tau_sensitivity, \n    run_lambda_sensitivity,\n    HistoricalStressTester\n)\n",
        "from robustness import run_tau_sensitivity, run_lambda_sensitivity, HistoricalStressTester\n",
        "import visualizations as viz\n",
        "from visualizations import plot_tau_sensitivity, plot_lambda_sensitivity, plot_stress_test\n",
        "from backtesting import PortfolioBacktester\n",
        "from backtesting import run_comprehensive_backtest\n",
        "from stress_testing import HistoricalStressTester\n",
        "import empirical_study\n"
    ]
    
    for k in contents.keys():
        for imp in to_remove:
            contents[k] = contents[k].replace(imp, '')
            contents[k] = contents[k].replace('viz.plot_', 'plot_')
            contents[k] = contents[k].replace('viz.create_visualizations', 'create_visualizations')
            
    imports_str = """
# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings('ignore')

# Set reproducibility seed
np.random.seed(42)
"""

    bl_str = "\n# ==============================================================================\n# 2. BLACK-LITTERMAN CLASS & OPTIMIZATION\n# ==============================================================================\n"
    bt_str = "\n# ==============================================================================\n# 3. BACKTESTING & TRANSACTION COSTS\n# ==============================================================================\n"
    rob_str = "\n# ==============================================================================\n# 4. ROBUSTNESS & STRESS TESTING\n# ==============================================================================\n"
    viz_str = "\n# ==============================================================================\n# 5. VISUALIZATIONS & DASHBOARD\n# ==============================================================================\n"
    main_str = "\n# ==============================================================================\n# 6. FINAL SUMMARY & MAIN EXECUTION\n# ==============================================================================\n"
    emp_str = "\n# ==============================================================================\n# 7. TRI-MARKET EMPIRICAL STUDY (US, CHINA, INDIA)\n# ==============================================================================\n"
    
    # We leave the extra external imports in the files. Python handles re-imports fine.
    # It ensures we don't accidentally corrupt code logic with regex.

    # main.py duplicate seed replacement
    contents['main'] = contents['main'].replace("np.random.seed(42)", "# Seed set globally")

    final_script = "\n".join([
        imports_str, 
        bl_str, contents['bl'], 
        viz_str, contents['viz'], 
        bt_str, contents['bt'], 
        rob_str, contents['rob'], 
        main_str, contents['main'],
        emp_str, contents['emp']
    ])
    
    md = f"""# Empirical Evaluation of Black–Litterman Portfolio Optimization Across Developed (US) and Emerging (China and India) Equity Markets with Robustness, Transaction Costs, and Crisis Stability Analysis.

## 1. Tri-Market Structural Framework

### Black-Litterman Model
The Black-Litterman (BL) model overcomes the sensitivity of traditional Markowitz Mean-Variance optimization by using a Bayesian approach to combine market equilibrium implied returns with subjective investor views.

Let $N$ be the number of assets.
1. **Implied Equilibrium Returns ($\\Pi$)**:
   $$ \\Pi = \\lambda \\Sigma w_{{mkt}} $$
   Where $\\lambda$ is the risk aversion coefficient, $\\Sigma$ is the $N \\times N$ covariance matrix, and $w_{{mkt}}$ are the market capitalization weights (now synthesized directly via CSI 300 proxy volumes).

2. **Investor Views ($Q$ and $P$)**:
   Let $K$ be the number of views.
   $P$ is a $K \\times N$ matrix mapping views to assets.
   $Q$ is a $K \\times 1$ vector of expected returns for those views.
   $\\Omega$ is a $K \\times K$ diagonal covariance matrix representing the uncertainty in the views.

3. **Combined Expected Returns ($E[R]$)**:
   $$ E[R] = [(\\tau \\Sigma)^{{-1}} + P^T \\Omega^{{-1}} P]^{{-1}} [(\\tau \\Sigma)^{{-1}} \\Pi + P^T \\Omega^{{-1}} Q] $$
   Where $\\tau$ is a scalar indicating the uncertainty of the prior (equilibrium) returns.

### Robustness & Stress Testing
- **Tau ($\\tau$) Sensitivity**: Analyzes the allocation drift and Sharpe ratio decay as the model's reliance on investor views ($\\tau \\to \\infty$) versus market equilibrium ($\\tau \\to 0$) shifts.
- **Lambda ($\\lambda$) Sensitivity**: Analyzes how fundamental risk aversion impacts the base equilibrium returns and the ultimate allocation spread.
- **2008 & 2015 Financial Crisis Stress Tests**: Isolates a historical maximum drawdown event (2008 Lehman Brothers US, 2015 China Stock Bubble Burst) by locking pre-crisis portfolio target weights and observing pure out-of-sample geometrically compounded drawdown depths against the benchmark.

### Benchmark Comparison (S&P 500 & Shanghai Composite)
To validate the model practically, we map the cumulative Out-Of-Sample compounded tracking returns explicitly against the S&P 500 (US) and Shanghai Composite Index (China). We apply standard Geometric Compounding algorithms over continuously sliding observation window arrays.

### Transaction Costs & Backtesting
Realistic evaluation requires moving beyond theoretical gross returns. Frictional drag is accounted for using:
$$ C_{{t}} = \\sum_{{i=1}}^{{N}} |w_{{i,t}} - w_{{i, t-1}}| \\times (c_{{trade}} + c_{{slippage}}) $$
Where $c_{{trade}}$ is the proportional broker sequence fee and $c_{{slippage}}$ encapsulates implicit execution spread widening.  
*Note: Over active rebalancing intervals, Gross Returns represent the mathematical theoretical threshold, whilst Net Returns map the true achievable payout.*

---

## 2. Expected Tri-Market Outputs

Executing the final compiled script will generate cross-border analytics:

| Filename | Type | Description |
|----------|------|-------------|

## 4. Master Executable Python Script

> **Instructions:** Copy the monolithic code block below and save it as `main_black_litterman.py`. Run it directly via `python main_black_litterman.py`. Dependencies required: `numpy`, `pandas`, `scipy`, `matplotlib`, `yfinance`, `seaborn`.

```python
{final_script}
```
"""
    with open('FINAL_BLACK_LITTERMAN_IMPLEMENTATION.md', 'w', encoding='utf-8') as f:
        f.write(md)

combine_files()
