"""
Quick verification of the fixed crisis recovery duration logic.
Runs each market's stress tester in isolation and prints results.
"""
import sys, os
sys.path.insert(0, r'g:\stock portfolio')

import logging
logging.basicConfig(level=logging.WARNING)

from pipelines.dual_market import MARKET_CONFIG
from legacy.core_legacy.stress_testing import HistoricalStressTester
from legacy.core_legacy.optimizer import BlackLittermanOptimizer

CRISIS_NAMES = {
    'US': '2008 US GFC (test: 2008-01 to 2013-12)',
    'CHINA': '2015 China Crash (test: 2015-06 to 2016-02)',
    'INDIA': '2020 India COVID (test: 2020-02 to 2020-06)',
}

print("=" * 70)
print("CRISIS RECOVERY DURATION  -- POST-FIX VALIDATION")
print("Peak correctly set to portfolio value at crisis start (t0).")
print("Duration = trading days from trough to recovery.")
print("=" * 70)

for market in ['US', 'CHINA', 'INDIA']:
    print(f"\n[{market}] {CRISIS_NAMES[market]}")
    cfg = MARKET_CONFIG[market]

    opt = BlackLittermanOptimizer(
        cfg['tickers'], cfg['start'], cfg['end'], use_market_cap_weights=True
    )

    tester = HistoricalStressTester(
        cfg['stress_tickers'],
        train_start=cfg['stress_train_start'],
        train_end=cfg['stress_train_end'],
        test_start=cfg['stress_test_start'],
        test_end=cfg['stress_test_end'],
        benchmark=cfg['benchmark'],
        global_prices=opt.prices
    )
    tester.run_training_phase(cfg['views'], cfg['confidence'])
    tester.run_stress_test()

    for model in ['black_litterman', 'markowitz']:
        res = tester.results.get(model, {})
        mname = 'Black-Litterman' if model == 'black_litterman' else 'Markowitz'
        dd = res.get('Max Drawdown', float('nan'))
        vol_spike = res.get('Volatility Spike (x)', float('nan'))
        uw = res.get('Max Underwater Days', 'N/A')
        print(f"  {mname:<20} MaxDD={dd*100:.2f}%  VolSpike={vol_spike:.2f}x  Recovery={uw} trading days")

print("\n" + "=" * 70)
print("Validation complete.")
