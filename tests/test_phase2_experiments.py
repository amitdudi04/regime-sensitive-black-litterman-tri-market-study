import unittest
import contextlib
import hashlib
import io
import json
import tempfile
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd

from backtesting.paper_backtest import BacktestConfig, run_paper_backtest
from pipelines.phase2_experiments import (equal_weight_path, model_paths, apply_costs,
    concentration_metrics, summary_row, statistical_row, load_frozen_prices)
from pipelines.phase2_experiments import run_phase2
from scripts.validate_phase2_outputs import validate_phase2


def sample(n=320):
    return pd.DataFrame(np.random.default_rng(17).normal(.0003,.01,(n,3)),
        index=pd.bdate_range("2020-01-01",periods=n),columns=["A","B","C"])


class TestPhase2(unittest.TestCase):
    def test_equal_weight_drifts_then_rebalances_on_common_schedule(self):
        returns=pd.DataFrame([[0,0],[0,0],[.2,0],[0,0],[0,.2],[0,0]],
            index=pd.bdate_range("2020-01-01",periods=6),columns=["A","B"])
        path=equal_weight_path(returns,BacktestConfig(window_size=2,rebalance_freq=2))
        np.testing.assert_allclose(path["gross"],[.1,0,.1,0],atol=1e-12)
        np.testing.assert_allclose(path["turnover"],[1,1/11],atol=1e-12)
        self.assertTrue(path["gross"].index.equals(returns.index[2:]))
        self.assertAlmostEqual((1+path["gross"]).prod(),1.21)
        self.assertTrue((path["weights"]==.5).all().all())

    def test_costs_reuse_gross_paths_and_reconcile_wealth(self):
        path=equal_weight_path(sample(),BacktestConfig(window_size=252,rebalance_freq=20))
        original=path["gross"].copy()
        previous=np.inf
        for bps in (0,5,10,20):
            net=apply_costs(path["gross"],path["turnover"],bps)
            wealth=(1+net).prod()
            self.assertLessEqual(wealth,previous)
            self.assertAlmostEqual(wealth,(1+original).prod()*(1-path["turnover"]*bps/10000).prod(),places=12)
            self.assertAlmostEqual(1+net.iloc[0],(1+original.iloc[0])*(1-bps/10000))
            previous=wealth
        pd.testing.assert_series_equal(path["gross"],original)

    def test_matched_caps_and_only_two_optimizer_calls(self):
        cfg=BacktestConfig()
        with patch("pipelines.phase2_experiments.run_paper_backtest",wraps=run_paper_backtest) as runner:
            paths=model_paths(sample(),cfg)
        self.assertEqual(runner.call_count,2)
        self.assertEqual(runner.call_args_list[0].args[1],replace(cfg,max_weight=1.,transaction_cost_rate=0))
        self.assertEqual(runner.call_args_list[1].args[1],replace(cfg,max_weight=.4,transaction_cost_rate=0))
        for model in ("Black-Litterman","Markowitz"):
            self.assertLessEqual(paths[(model,.4)]["weights"].max().max(),.4+1e-7)
        self.assertEqual(len({tuple(p["gross"].index) for p in paths.values()}),1)

    def test_cap_feasibility_and_target_vs_drift_concentration(self):
        with self.assertRaisesRegex(ValueError,"infeasible"):
            model_paths(sample().iloc[:,:2],BacktestConfig())
        for n in (4,5): self.assertGreaterEqual(.4*n,1)
        returns=sample(2); returns.iloc[:]=[[1,0,0],[0,0,0]]
        weights=pd.DataFrame([[.4,.3,.3]],index=[returns.index[0]],columns=returns.columns)
        concentration=concentration_metrics(weights,returns)
        self.assertAlmostEqual(concentration["Mean Target HHI"],.34)
        self.assertAlmostEqual(concentration["Maximum End-of-Day Weight"],4/7)

    def test_cost_reconstruction_matches_phase1_net_path(self):
        cfg=BacktestConfig()
        packet=run_paper_backtest(sample(),cfg)
        for model,prefix in (("Black-Litterman","black_litterman"),("Markowitz","markowitz")):
            reconstructed=apply_costs(packet["daily_returns"][prefix+"_gross"],packet["turnover"][model],10)
            np.testing.assert_allclose(reconstructed,packet["daily_returns"][prefix+"_net"],atol=1e-12)

    def test_statistical_dates_must_match_without_silent_dropping(self):
        a=sample()["A"].iloc[252:]
        with self.assertRaisesRegex(ValueError,"identical"):
            statistical_row("Test",1.,"Equal-weight",a,a.iloc[1:])
        result=statistical_row("Test",1.,"Equal-weight",a,a,bootstrap={"block_size":20,"iterations":30,"seed":42})
        self.assertEqual(result["Paired Observations"],len(a))
        self.assertEqual(result["Sharpe Difference A minus B"],0)
        self.assertEqual(result["Two-sided P-value"],1)

    def test_summary_metrics_and_costs_match_known_path(self):
        returns=sample()
        path=equal_weight_path(returns,BacktestConfig())
        row=summary_row("Test","Equal-weight",1.,path,returns,0)
        self.assertAlmostEqual(row["Annualized Return"],path["gross"].mean()*252)
        self.assertAlmostEqual(row["Net Terminal Wealth"],(1+path["gross"]).prod())
        self.assertAlmostEqual(row["Mean Target HHI"],1/3)
        self.assertEqual(row["Total Costs Per Initial NAV"],0)
        self.assertEqual(row["ASI"],0)

    def test_missing_frozen_inputs_never_download(self):
        with patch("pipelines.phase2_experiments.ROOT",Path("missing-phase2-input")), patch("core.data_loader.yf.download") as download:
            with self.assertRaisesRegex(FileNotFoundError,"FROZEN_PHASE1_INPUT_UNAVAILABLE"):
                load_frozen_prices("US",{"tickers":["SPY"]},{})
        download.assert_not_called()

    def test_output_tables_reconcile_and_reject_changed_summary(self):
        def frozen(market,spec,config):
            values=np.random.default_rng(31).normal(.0003,.01,(320,len(spec["tickers"])))
            prices=pd.DataFrame(100*np.cumprod(1+values,axis=0),index=pd.bdate_range("2020-01-01",periods=320),columns=spec["tickers"])
            return prices,{"sha256":"synthetic-test-only"}
        with tempfile.TemporaryDirectory() as temp, patch("pipelines.phase2_experiments.load_frozen_prices",side_effect=frozen), contextlib.redirect_stdout(io.StringIO()):
            out=Path(temp)
            run_phase2(out)
            self.assertEqual(validate_phase2(out)["status"],"PASS")
            summary=out/"phase2_strategy_summary.csv"
            table=pd.read_csv(summary)
            table.loc[0,"Annualized Return"]+=.01
            table.to_csv(summary,index=False)
            manifest_path=out/"PHASE2_RUN_MANIFEST.json"
            manifest=json.loads(manifest_path.read_text())
            manifest["output_sha256"][summary.name]=hashlib.sha256(summary.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,"Tables disagree"):
                validate_phase2(out)
