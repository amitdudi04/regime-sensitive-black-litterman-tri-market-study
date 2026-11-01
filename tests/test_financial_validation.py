"""Independent financial oracles. Tolerances: 1e-12 identities; 2e-6 SLSQP weights."""
import hashlib
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from core.data_loader import _extract_adjusted_close
from core.return_calculations import compute_simple_returns, compute_log_returns
from core.covariance_estimators import estimate_covariance
from models.black_litterman_model import compute_black_litterman_posterior as posterior
from models.black_litterman_model import compute_implied_equilibrium_returns as implied
from models.optimizer import compute_mean_variance_weights as optimize
from backtesting.paper_backtest import (BacktestConfig, run_paper_backtest,
    _buy_and_hold_daily_returns, _drifted_weights, _l1_turnover)
from backtesting.allocation_stability_index import compute_asi
from analysis.crisis_analysis import calculate_crisis_metrics
from analysis.statistical_tests import circular_block_bootstrap_sharpe_difference as bootstrap
from analysis.statistical_tests import circular_block_bootstrap
from analysis.factor_regression import run_factor_regression, _download_factor_range
from analysis.regime_detection import fit_markov_regime_model
from analysis.tau_sensitivity import run_tau_sensitivity
from pipelines.tri_market_pipeline import _performance, _load_or_download_prices
from scripts.validate_generated_outputs import verify_run_files


def panel(n=100):
    return pd.DataFrame(np.random.default_rng(82).normal(.0003, .01, (n, 2)),
                        index=pd.bdate_range("2020-01-01", periods=n), columns=["A", "B"])


class TestDataContracts(unittest.TestCase):
    def test_simple_and_log_price_path(self):
        prices = pd.DataFrame({"A": [100, 80, 100], "B": [50, 55, 44]},
                              index=pd.bdate_range("2020-01-01", periods=3))
        np.testing.assert_allclose(compute_simple_returns(prices), [[-.2, .1], [.25, -.2]], atol=1e-12)
        np.testing.assert_allclose(np.expm1(compute_log_returns(prices)), compute_simple_returns(prices), atol=1e-12)

    def test_prices_reject_missing_nonpositive_nonfinite(self):
        for invalid in (np.nan, 0, -1, np.inf):
            prices = panel(3) + 100
            prices.iloc[1, 0] = invalid
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                compute_simple_returns(prices)

    def test_dates_reject_duplicates_unsorted_nat_timezone(self):
        for idx in (["2020-01-01"] * 3, ["2020-01-03", "2020-01-02", "2020-01-01"],
                    ["2020-01-01", None, "2020-01-03"], pd.date_range("2020-01-01", periods=3, tz="UTC")):
            values = panel(3)
            values.index = pd.DatetimeIndex(idx)
            with self.subTest(idx=idx), self.assertRaises(ValueError):
                run_paper_backtest(values, BacktestConfig(window_size=2))

    def test_raw_close_and_ambiguous_columns_rejected(self):
        for data in (pd.DataFrame({"Close": [100]}), pd.DataFrame({"A": [100]}),
                     pd.DataFrame([[100]], columns=pd.MultiIndex.from_tuples([("Close", "A")]))):
            with self.subTest(columns=data.columns), self.assertRaises(ValueError):
                _extract_adjusted_close(data, ["A"])

    def test_adjusted_close_takes_precedence(self):
        prices = pd.DataFrame({"Adj Close": [80., 100.], "Close": [100., 100.]},
                              index=pd.bdate_range("2020-01-01", periods=2))
        self.assertAlmostEqual(compute_simple_returns(_extract_adjusted_close(prices, ["A"])).iloc[0, 0], .25)

    def test_cache_rejects_ambiguous_old_provenance(self):
        with tempfile.TemporaryDirectory() as temp, patch("pipelines.tri_market_pipeline.RESULTS_DIR", Path(temp)):
            with patch("pipelines.tri_market_pipeline.download_market_data", return_value=panel(4) + 100):
                _load_or_download_prices("Test", ["A", "B"], "2020-01-01", "2020-02-01")
            path = Path(temp) / "price_data/test_adjusted_close.json"
            meta = json.loads(path.read_text())
            meta["price_field"] = "Adj Close or Close"
            path.write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                _load_or_download_prices("Test", ["A", "B"], "2020-01-01", "2020-02-01")

    def test_cache_checksum_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as temp, patch("pipelines.tri_market_pipeline.RESULTS_DIR", Path(temp)):
            with patch("pipelines.tri_market_pipeline.download_market_data", return_value=panel(4) + 100):
                _load_or_download_prices("Test", ["A", "B"], "2020-01-01", "2020-02-01")
            path = Path(temp) / "price_data/test_adjusted_close.csv"
            path.write_text(path.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "checksum"):
                _load_or_download_prices("Test", ["A", "B"], "2020-01-01", "2020-02-01")

    def test_covariance_centering_annualization_and_labels(self):
        # Symmetric four corners give population covariance diag(.0001,.0001);
        # shrinking an isotropic matrix leaves it unchanged. ddof=0 is LW's convention.
        values = pd.DataFrame([[.01,.01], [.01,-.01], [-.01,.01], [-.01,-.01]],
                              index=pd.bdate_range("2020-01-01", periods=4), columns=["B", "A"])
        cov = estimate_covariance(values + .05)
        np.testing.assert_allclose(cov, np.eye(2) * .0252, atol=1e-12)
        np.testing.assert_allclose(cov, estimate_covariance(values, 1) * 252, atol=1e-12)
        self.assertEqual(list(cov.columns), ["B", "A"])


class TestModelIdentities(unittest.TestCase):
    def test_one_asset_posterior_precision_oracle(self):
        # Prior variance tau*Sigma=.002, Omega=.008 => 20% view, 80% prior.
        self.assertAlmostEqual(posterior([.06], [[.04]], [[1]], [.10], [[.008]], .05).iloc[0], .068)

    def test_view_limits_zero_tilt_and_tau(self):
        for tau in (1e-14, .01, .2):
            self.assertAlmostEqual(posterior([.06], [[.04]], [[1]], [.06], [[.008]], tau).iloc[0], .06)
        self.assertAlmostEqual(posterior([.06], [[.04]], [[1]], [.1], [[1e12]], .05).iloc[0], .06)
        self.assertAlmostEqual(posterior([.06], [[.04]], [[1]], [.1], [[1e-14]], .05).iloc[0], .1)

    def test_two_asset_relative_view_oracle(self):
        # Independent prior variances .002 each; relative-view variance .004.
        # Gain=(.25,-.25), innovation .08 => posterior (.08,.04).
        np.testing.assert_allclose(posterior([.06,.06], np.eye(2)*.04, [[1,-1]], [.08], [[.004]], .05), [.08,.04], atol=1e-12)

    def test_singular_and_ill_conditioned_covariance(self):
        for cov in (np.zeros((2,2)), np.diag([1e-20,.04])):
            result = posterior([.06,.06], cov, np.eye(2), [.1,.1], np.eye(2)*.01, .05)
            self.assertTrue(np.isfinite(result).all())
            self.assertAlmostEqual(result.iloc[0], .06)

    def test_implied_label_alignment_and_normalization(self):
        cov = pd.DataFrame(np.diag([.04,.09]), index=["A","B"], columns=["A","B"])
        np.testing.assert_allclose(implied(cov, pd.Series({"B": 4., "A": 6.}), 2.5), [.06,.09])

    def test_negative_prior_and_invalid_matrices_rejected(self):
        with self.assertRaises(ValueError):
            implied(np.eye(2), [-.5,1.5], 3)
        for cov in ([[1,2],[0,1]], [[1,0],[0,-1]], [[np.nan,0],[0,1]]):
            with self.subTest(cov=cov), self.assertRaises(ValueError):
                optimize([.1,.1], cov)
        for tau in (0,-1,np.nan,np.inf):
            with self.subTest(tau=tau), self.assertRaises(ValueError):
                posterior([.1], [[.04]], [[1]], [.1], [[.01]], tau)

    def test_posterior_invalid_view_inputs(self):
        for p,q,o in (([1],[.1],[[.01]]), ([[1]],[np.nan],[[.01]]), ([[1]],[.1],[[0]]), ([[1]],[.1],[[-.1]])):
            with self.subTest(inputs=(p,q,o)), self.assertRaises(ValueError):
                posterior([.1], [[.04]], p, q, o, .05)

    def test_optimizer_analytic_interior_solution(self):
        # Diagonal variances .04,.09 and mu=.08,.11, lambda=3:
        # wA=(3*.09+.08-.11)/(3*(.04+.09))=8/13.
        result = optimize([.08,.11], np.diag([.04,.09]), risk_aversion=3)
        np.testing.assert_allclose(result, [8/13,5/13], atol=2e-6)

    def test_optimizer_binding_bounds(self):
        np.testing.assert_allclose(optimize([1.,0.], np.eye(2)*.01, max_weight=.7), [.7,.3], atol=2e-6)
        with self.assertRaises(ValueError):
            optimize([.1,.1], np.eye(2), max_weight=.4)

    def test_optimizer_permutations_match(self):
        mu = pd.Series({"A":.08,"B":.11})
        cov = pd.DataFrame(np.diag([.04,.09]), index=mu.index, columns=mu.index)
        np.testing.assert_allclose(optimize(mu,cov), optimize(mu,cov.loc[["B","A"],["B","A"]]), atol=1e-12)


class TestInvestmentAccounting(unittest.TestCase):
    def test_buy_hold_exact_wealth_and_zero_drift_turnover(self):
        assets = panel(3)
        assets.iloc[:] = [[.2,0],[0,.2],[-.5,.1]]
        weights = pd.Series({"A":.5,"B":.5})
        realized = _buy_and_hold_daily_returns(assets, weights)
        # End holdings .5*1.2*.5=.3 and .5*1.2*1.1=.66 => NAV=.96.
        self.assertAlmostEqual((1+realized).prod(), .96)
        drifted = _drifted_weights(weights, assets)
        self.assertEqual(_l1_turnover(drifted, drifted), 0)
        self.assertAlmostEqual(drifted["A"], .3/.96)
        self.assertEqual(_l1_turnover(weights, None), 1)

    def test_costs_compound_at_initial_and_later_trades(self):
        cfg = BacktestConfig(window_size=60, rebalance_freq=11, transaction_cost_rate=.001)
        packet = run_paper_backtest(panel(), cfg)
        zero = run_paper_backtest(panel(), replace(cfg, transaction_cost_rate=0))
        for model in ("black_litterman", "markowitz"):
            daily = packet["daily_returns"]
            label = "Black-Litterman" if model == "black_litterman" else "Markowitz"
            cost = packet["turnover"][label] * .001
            net_wealth = (1+daily[model+"_net"]).prod()
            gross_wealth = (1+daily[model+"_gross"]).prod()
            self.assertAlmostEqual(net_wealth, gross_wealth * (1-cost).prod(), places=12)
            self.assertLessEqual(net_wealth, gross_wealth)
            np.testing.assert_allclose(zero["daily_returns"][model+"_net"], zero["daily_returns"][model+"_gross"], atol=1e-12)
            for date in cost.index:
                self.assertAlmostEqual(1+daily.loc[date,model+"_net"], (1-cost[date])*(1+daily.loc[date,model+"_gross"]), places=12)

    def test_maximum_drawdown_includes_initial_wealth(self):
        for returns, expected in (([-.2],-.2), ([-.2,-.25],-.4), ([.1,-.2],-.2),
                                   ([-.2,.25],-.2), ([0,0],0), ([-.2,0],-.2)):
            series = pd.Series(returns, index=pd.bdate_range("2020-01-01",periods=len(returns)))
            with self.subTest(returns=returns):
                self.assertAlmostEqual(_performance(series)["Max Drawdown"], expected)

    def test_asi_exact_mean_l1_and_invalid_missing_weights(self):
        self.assertAlmostEqual(compute_asi([[.5,.5],[.8,.2],[.6,.4]]), .5)
        with self.assertRaises(ValueError):
            compute_asi([[.5,.5],[np.nan,.2]])

    def test_backtest_invalid_data_and_configuration(self):
        for invalid in (np.nan, np.inf, -1, -2):
            data = panel()
            data.iloc[1,0] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                run_paper_backtest(data, BacktestConfig(window_size=60))
        for kwargs in ({"rebalance_freq":0}, {"window_size":1}, {"risk_aversion":-1}, {"tau_low_vol":np.nan}, {"transaction_cost_rate":-.1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                BacktestConfig(**kwargs)

    def test_priors_missing_duplicate_nat_negative_and_future_leakage(self):
        data = panel()
        cfg = BacktestConfig(window_size=60, rebalance_freq=10)
        prior = pd.DataFrame([[8.,2.],[1.,9.]], index=data.index[[58,85]], columns=["A","B"])
        base = run_paper_backtest(data,cfg,prior)
        changed = prior.copy()
        changed.iloc[-1] = [9,1]
        other = run_paper_backtest(data,cfg,changed)
        pd.testing.assert_frame_equal(base["daily_returns"].iloc[:20], other["daily_returns"].iloc[:20])
        self.assertAlmostEqual(base["equilibrium_prior_history"].iloc[0]["A"], .8)
        reordered = run_paper_backtest(data,cfg,prior[["B","A"]])
        pd.testing.assert_frame_equal(base["daily_returns"],reordered["daily_returns"])
        invalid = [prior[["A"]], pd.concat([prior,prior]), prior.set_axis([pd.NaT,data.index[85]])]
        for values in ([-1,2], [0,0], [np.inf,1]):
            p = prior.copy(); p.iloc[0] = values; invalid.append(p)
        for p in invalid:
            with self.subTest(prior=p), self.assertRaises(ValueError):
                run_paper_backtest(data,cfg,p)

    def test_crisis_first_loss_and_recovery_censoring(self):
        for path, mdd, trough, recovery in (([-.2,.25],-.2,0,1), ([-.1,-.1,.3],-.19,1,2),
                    ([-.4,0,0],-.4,0,None), ([.1,-.5,1],-.5,1,2), ([-.1,.2,-.5,1],-.5,2,3)):
            pre = [.001,-.001]*10
            values = pd.DataFrame({"A":pre+path, "B":pre+path}, index=pd.bdate_range("2020-01-01",periods=20+len(path)))
            weights = pd.DataFrame([[.5,.5]], index=[values.index[19]], columns=values.columns)
            result = calculate_crisis_metrics(values, weights, str(values.index[20].date()), str(values.index[-1].date()))
            with self.subTest(path=path):
                self.assertAlmostEqual(result["Buy-Hold Max Drawdown"],mdd)
                self.assertEqual(result["Buy-Hold Trough Date"], str(values.index[20+trough].date()))
                self.assertEqual(result["Buy-Hold Recovery Date"], None if recovery is None else str(values.index[20+recovery].date()))


class TestInferenceAndOutputs(unittest.TestCase):
    def test_circular_wrapping_and_pairing_known_indices(self):
        a = np.linspace(-.01,.02,10)
        b = np.array([.01,-.01,.02,-.02,.01,-.01,.02,-.02,.03,-.01])
        with patch("analysis.statistical_tests.np.random.default_rng") as generator:
            generator.return_value.integers.return_value = np.array([9,9])
            result = bootstrap(a,b,block_size=6,iterations=2)
        # Two six-session blocks start at index 9, wrap and truncate to 10.
        idx=[9,0,1,2,3,4,9,0,1,2]
        expected=(a[idx].mean()/a[idx].std(ddof=1)-b[idx].mean()/b[idx].std(ddof=1))*np.sqrt(252)
        np.testing.assert_allclose(result["bootstrap_differences"],[expected,expected],atol=1e-12)

    def test_hac_t_statistics_against_explicit_sandwich(self):
        dates=panel(120).index
        factors=pd.DataFrame(np.random.default_rng(9).normal(0,.01,(120,4)),index=dates,columns=["MKT","SMB","HML","MOM"])
        factors["RF"]=.0001
        y=.0002+factors.MKT+.003*np.sin(np.arange(120))
        x=np.column_stack([np.ones(120),factors[["MKT","SMB","HML","MOM"]]])
        beta=np.linalg.lstsq(x,y,rcond=None)[0]
        score=x*(np.asarray(y)-x@beta)[:,None]
        meat=score.T@score
        for lag in range(1,6):
            cross=score[lag:].T@score[:-lag]
            meat+=(1-lag/6)*(cross+cross.T)
        bread=np.linalg.inv(x.T@x)
        standard_errors=np.sqrt(np.diag(bread@meat@bread))
        with patch("analysis.factor_regression.load_factor_data",return_value=factors):
            result=run_factor_regression(y+factors.RF)
        np.testing.assert_allclose([result["Alpha_t_stat"]]+[result[c+"_t_stat"] for c in ("MKT","SMB","HML","MOM")],beta/standard_errors,atol=1e-9)

    def test_bootstrap_identical_serial_returns_seed_and_confidence_interval(self):
        x = panel(150)["A"].rolling(3).mean().dropna()
        result = bootstrap(x,x,block_size=10,iterations=100)
        self.assertEqual(result["observed_sharpe_difference"],0)
        self.assertEqual(result["p_value"],1)
        self.assertEqual(result["percentile_ci_95"],[0,0])
        np.testing.assert_array_equal(result["bootstrap_differences"],bootstrap(x,x,block_size=10,iterations=100)["bootstrap_differences"])

    def test_bootstrap_shift_direction_and_swap_symmetry(self):
        x = panel(150)["A"]
        pos, neg = bootstrap(x+.001,x,iterations=100), bootstrap(x,x+.001,iterations=100)
        self.assertGreater(pos["observed_sharpe_difference"],0)
        self.assertLess(neg["observed_sharpe_difference"],0)
        self.assertEqual(pos["p_value"],neg["p_value"])
        errors = pos["bootstrap_differences"]-pos["bootstrap_differences"].mean()
        self.assertEqual(pos["p_value"],np.mean(np.abs(errors)>=abs(pos["observed_sharpe_difference"])))

    def test_bootstrap_constant_and_invalid_parameters(self):
        with self.assertRaises(ValueError):
            bootstrap(np.ones(100),np.ones(100),iterations=100)
        for kwargs in ({"block_size":0}, {"block_size":-1}, {"block_size":1.5}, {"iterations":0}, {"iterations":1}, {"iterations":1.5}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                bootstrap(panel()["A"],panel()["B"],**kwargs)
        with self.assertRaises(ValueError):
            circular_block_bootstrap([1,2,3],0)

    def test_factor_ols_excess_return_units_and_alpha(self):
        n=120; dates=panel(n).index
        f = pd.DataFrame(np.random.default_rng(7).normal(0,.01,(n,4)),index=dates,columns=["MKT","SMB","HML","MOM"])
        f["RF"] = .0001
        returns = .0002 + f[["MKT","SMB","HML","MOM"]] @ np.array([1.1,.2,-.3,.4]) + f.RF
        with patch("analysis.factor_regression.load_factor_data",return_value=f):
            result=run_factor_regression(returns)
        np.testing.assert_allclose([result[c+"_beta"] for c in ("MKT","SMB","HML","MOM")],[1.1,.2,-.3,.4],atol=1e-12)
        self.assertAlmostEqual(result["Alpha"],.0002)
        self.assertAlmostEqual(result["Alpha_Annualized"],.0504)
        self.assertEqual(result["Observations"],120)

    def test_factor_download_percentage_conversion(self):
        dates=panel(20).index
        ff=pd.DataFrame({"Mkt-RF":1.,"SMB":2.,"HML":3.,"RF":.01},index=dates)
        mom=pd.DataFrame({"Mom":4.},index=dates)
        _download_factor_range.cache_clear()
        with tempfile.TemporaryDirectory() as temp, patch("analysis.factor_regression.FACTOR_CACHE",Path(temp)), patch("analysis.factor_regression.HTTPSFrenchReader") as reader:
            reader.return_value.read.side_effect=[{0:ff},{0:mom}]
            result=_download_factor_range("2020-01-01","2020-02-01")
            np.testing.assert_allclose(result.iloc[0], [.01,.02,.03,.0001,.04])
        _download_factor_range.cache_clear()

    def test_fixed_tau_changes_only_tau_configuration(self):
        cfg=BacktestConfig(window_size=60,rebalance_freq=10)
        actual=run_paper_backtest
        with patch("analysis.tau_sensitivity.run_paper_backtest",side_effect=actual) as runner:
            run_tau_sensitivity(panel(),cfg,[.01,.2])
        for call,tau in zip(runner.call_args_list,[.01,.2]):
            self.assertEqual(call.args[1],replace(cfg,tau_low_vol=tau,tau_high_vol=tau))
            pd.testing.assert_frame_equal(call.args[0],panel())

    def test_regime_labels_follow_variance_and_reject_failed_fit(self):
        class Fit:
            params={"sigma2[0]":.04,"sigma2[1]":.01}
            mle_retvals={"converged":True}
            smoothed_marginal_probabilities=pd.DataFrame({0:[.8]*100,1:[.2]*100},index=panel().index)
        with patch("analysis.regime_detection.MarkovRegression") as model:
            fit=Fit(); model.return_value.fit.return_value=fit
            states,_=fit_markov_regime_model(panel()["A"])
            self.assertTrue(states.Regime.eq("High_Vol").all())
            fit.mle_retvals={"converged":False}
            with self.assertRaises(RuntimeError):
                fit_markov_regime_model(panel()["A"])

    def test_stale_or_tampered_output_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); path=root/"data.csv"; path.write_text("a\n1\n")
            (root/"RUN_MANIFEST.json").write_text(json.dumps({"run_id":"test", "output_sha256":{"data.csv":hashlib.sha256(path.read_bytes()).hexdigest()}}))
            verify_run_files(root)
            path.write_text("a\n2\n")
            with self.assertRaises(ValueError):
                verify_run_files(root)
