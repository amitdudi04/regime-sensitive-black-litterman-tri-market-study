"""Check Phase 2 output identities and reconstruct gross holdings from frozen inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from backtesting.allocation_stability_index import compute_asi
from backtesting.paper_backtest import _drifted_weights, _l1_turnover
from core.return_calculations import compute_simple_returns
from pipelines.tri_market_pipeline import _performance, _total_costs


def validate_phase2(root):
    root = Path(root)
    manifest = json.loads((root/"PHASE2_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    for name, expected in manifest["output_sha256"].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Phase 2 output changed after completion: {name}")
    summary = pd.read_csv(root/"phase2_strategy_summary.csv")
    concentration = pd.read_csv(root/"phase2_concentration_sensitivity.csv")
    costs = pd.read_csv(root/"phase2_transaction_cost_sensitivity.csv")
    stats = pd.read_csv(root/"phase2_statistical_comparisons.csv")
    daily = pd.read_csv(root/"phase2_daily_returns.csv",parse_dates=["Date"])
    decisions = pd.read_csv(root/"phase2_trading_decisions.csv",parse_dates=["Date"])
    if [len(t) for t in (summary,concentration,costs,stats)] != [9,12,60,12]:
        raise ValueError("Missing or duplicate Phase 2 scenario rows")
    keys = ["Market","Model","Target Weight Cap","Cost (bps per L1)"]
    if costs.duplicated(keys).any() or stats.duplicated(["Market","Target Weight Cap","Strategy B"]).any():
        raise ValueError("Ambiguous scenario keys")
    for table in (summary, concentration):
        joined = table.merge(costs,on=keys,suffixes=("_table","_cost"),validate="one_to_one")
        if len(joined)!=len(table): raise ValueError("Summary scenario absent from costs")
        for col in table.columns.difference(keys):
            if pd.api.types.is_numeric_dtype(table[col]):
                if not np.allclose(joined[col+"_table"],joined[col+"_cost"],atol=1e-12,rtol=1e-10):
                    raise ValueError(f"Tables disagree for {col}")
            elif not joined[col+"_table"].equals(joined[col+"_cost"]):
                raise ValueError(f"Tables disagree for {col}")
    from pipelines.phase2_experiments import ROOT, load_frozen_prices, concentration_metrics
    from pipelines.tri_market_pipeline import MARKETS, _load_project_config
    for market, spec in MARKETS.items():
        prices, meta = load_frozen_prices(market,spec,_load_project_config())
        if meta["sha256"] != manifest["frozen_phase1_inputs"][market]["sha256"]:
            raise ValueError("Manifest uses a different price vintage")
        assets = compute_simple_returns(prices)
        expected_dates=assets.index[manifest["configuration"]["window_size"]:]
        for (model, cap), block in daily[daily.Market.eq(market)].groupby(["Model","Target Weight Cap"]):
            block = block.set_index("Date")
            if not block.index.equals(expected_dates): raise ValueError("Mismatched OOS dates")
            trades = decisions[decisions.Market.eq(market)&decisions.Model.eq(model)&decisions["Target Weight Cap"].eq(cap)].set_index("Date")
            expected_trade_dates = expected_dates[::manifest["configuration"]["rebalance_freq"]]
            if not trades.index.equals(expected_trade_dates): raise ValueError("Rebalance schedule mismatch")
            weights = pd.DataFrame([json.loads(s) for s in trades["Target Weights JSON"]],index=trades.index).reindex(columns=spec["tickers"])
            if (not np.isfinite(weights.to_numpy()).all() or (weights < -1e-7).any().any()
                    or (weights > cap+1e-7).any().any() or not np.allclose(weights.sum(axis=1),1,atol=1e-7)):
                raise ValueError("Invalid or out-of-bound target weights")
            if model == "Equal-weight" and not np.allclose(weights,1/len(spec["tickers"]),atol=1e-12):
                raise ValueError("Equal-weight targets differ from 1/N")
            previous_target=previous_block=None
            for i,(date,target) in enumerate(weights.iterrows()):
                end=weights.index[i+1] if i+1<len(weights) else None
                holding=assets.loc[(assets.index>=date)&((assets.index<end) if end is not None else True)]
                wealth=(1+holding).cumprod().mul(target,axis=1).sum(axis=1)
                exact=wealth/wealth.shift(1,fill_value=1)-1
                if not np.allclose(exact,block.loc[holding.index,"Gross Return"],atol=1e-12,rtol=0):
                    raise ValueError("Gross returns do not reconcile to fixed holdings")
                pretrade=_drifted_weights(previous_target,previous_block)
                if not np.isclose(_l1_turnover(target,pretrade),trades.loc[date,"L1 Turnover"],atol=1e-12):
                    raise ValueError("Turnover does not reconcile to drift")
                previous_target,previous_block=target,holding
            prior_terminal=np.inf
            for bps in manifest["cost_bps"]:
                net=block[f"Net Return {bps}bps"]
                factor=pd.Series(1.,index=block.index)
                factor.loc[trades.index]=1-trades["L1 Turnover"]*bps/10000
                if not np.allclose(1+net,(1+block["Gross Return"])*factor,atol=1e-12,rtol=0):
                    raise ValueError("Cost scenario violates Phase 1 wealth identity")
                row=costs[costs.Market.eq(market)&costs.Model.eq(model)&costs["Target Weight Cap"].eq(cap)&costs["Cost (bps per L1)"].eq(bps)]
                if len(row)!=1: raise ValueError("Missing scenario")
                row=row.iloc[0]
                expected={**_performance(net),"Gross Annualized Return":block["Gross Return"].mean()*252,
                    "Net Terminal Wealth":(1+net).prod(),"ASI":compute_asi(weights),
                    "Average Rebalance Turnover":trades["L1 Turnover"].iloc[1:].mean(),
                    "Total Costs Per Initial NAV":_total_costs(net,trades["L1 Turnover"],bps/10000),
                    "Initial Deployment Turnover":1.,"Initial Deployment Cost (bps)":bps,
                    "Sum Cost Fractions":trades["L1 Turnover"].sum()*bps/10000,
                    **concentration_metrics(weights,assets)}
                for name,value in expected.items():
                    if isinstance(value,str): valid=row[name]==value
                    else: valid=np.isclose(row[name],value,atol=1e-10,rtol=1e-9)
                    if not valid: raise ValueError(f"Daily/table inconsistency: {market}/{model}/{cap}/{bps}/{name}")
                if expected["Net Terminal Wealth"]>prior_terminal+1e-12:
                    raise ValueError("Increasing costs increased terminal wealth")
                prior_terminal=expected["Net Terminal Wealth"]
        for _,row in stats[stats.Market.eq(market)].iterrows():
            cap=row["Target Weight Cap"]
            a=costs[costs.Market.eq(market)&costs.Model.eq("Black-Litterman")&costs["Target Weight Cap"].eq(cap)&costs["Cost (bps per L1)"].eq(10)].iloc[0]
            comparator_cap=cap if row["Strategy B"]=="Markowitz" else 1.
            b=costs[costs.Market.eq(market)&costs.Model.eq(row["Strategy B"])&costs["Target Weight Cap"].eq(comparator_cap)&costs["Cost (bps per L1)"].eq(10)].iloc[0]
            if (not np.isclose(row["Sharpe Difference A minus B"],a["Sharpe Ratio"]-b["Sharpe Ratio"],atol=1e-10)
                    or row["Paired Observations"]!=len(expected_dates) or not 0<=row["Two-sided P-value"]<=1
                    or row["95% CI Lower"]>row["95% CI Upper"]):
                raise ValueError("Statistical sample/statistic mismatch")
    return {"status":"PASS","strategy_rows":9,"concentration_rows":12,"cost_rows":60,"statistical_rows":12,
            "price_vintage":"verified frozen Phase 1; no downloads","gross_wealth_and_cost_identities":"PASS",
            "table_return_decision_alignment":"PASS"}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=Path(__file__).resolve().parents[1]/"results/generated/phase2")
    print(json.dumps(validate_phase2(parser.parse_args().output_dir),indent=2))
