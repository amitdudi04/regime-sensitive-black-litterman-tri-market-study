"""Freeze publication tables/figures from pinned evidence; no downloads or model reruns.

python -m scripts.phase3_final_results [--output-dir results/phase3_final]
python -m scripts.phase3_final_results --validate-only
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import uuid

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/phase3_final"
P2 = "7553cf8bff59a4f3d8bad7d15b779707fc533fa1"
P1 = "598fe0d3c0a7cd7ebaf5709ae62b7c6735b92a0d"
MARKETS = ("US", "China", "India")
MODELS = ("Black-Litterman", "Markowitz", "Equal-weight")
P2_FILES = {"principal":"phase2_strategy_summary.csv", "concentration":"phase2_concentration_sensitivity.csv",
            "cost":"phase2_transaction_cost_sensitivity.csv", "statistics":"phase2_statistical_comparisons.csv"}
P1_FILES = {"datasets":"dataset_manifest.csv", "crisis":"crisis_summary.csv",
            "factors":"factor_regression_us.csv", "tau":"tau_sensitivity.csv"}
TABLE_NAMES = {1:"dataset_definitions",2:"principal_performance",3:"concentration_robustness",
               4:"transaction_cost_sensitivity",5:"statistical_comparisons",6:"crisis_stress_tests",
               7:"us_factor_exposures",8:"tau_sensitivity"}
PERCENT_COLUMNS = {"Net Annualized Return", "Annualized Volatility", "Max Drawdown", "Mean Rebalance L1 Turnover",
                   "Gross Annualized Return", "Target Weight Cap", "Maximum Target Weight", "Buy-Hold Max Drawdown"}
TABLE_SOURCES = {1:["docs/phase1/dataset_manifest.csv","results/phase2_results/phase2_strategy_summary.csv"],
    2:["results/phase2_results/phase2_strategy_summary.csv"],3:["results/phase2_results/phase2_concentration_sensitivity.csv"],
    4:["results/phase2_results/phase2_transaction_cost_sensitivity.csv"],5:["results/phase2_results/phase2_statistical_comparisons.csv"],
    6:["docs/phase1/crisis_summary.csv"],7:["docs/phase1/factor_regression_us.csv"],8:["docs/phase1/tau_sensitivity.csv"]}


def sha(data): return hashlib.sha256(data).hexdigest()
def canonical(data): return data.replace(b"\r\n",b"\n")
def payload_hash(value): return sha(json.dumps(value,sort_keys=True,allow_nan=False).encode())


def require_pinned_bytes(actual, pinned, label):
    if canonical(actual) != canonical(pinned):
        raise ValueError(f"Evidence differs from its protected frozen commit: {label}")


def require_output_hash(data, expected, label):
    # Historical outputs were serialized on Windows; allow only LF/CRLF conversion.
    lf=canonical(data)
    if expected not in {sha(data),sha(lf),sha(lf.replace(b"\n",b"\r\n"))}:
        raise ValueError(f"Stale/mismatched source output: {label}")


def check_run_links(p1, p2, cache):
    if not p1.get("run_id") or not p2.get("run_id") or p2["run_id"] != cache.get("run_id"):
        raise ValueError("Phase 2 daily evidence belongs to a different source run")
    for market in MARKETS:
        if p1["price_snapshots"][market]["sha256"] != p2["frozen_phase1_inputs"][market]["sha256"]:
            raise ValueError("Phase 1 supplementary / Phase 2 price vintages differ")


def load_evidence():
    inputs={}
    def read(relative, commit=None, expected=None):
        path=ROOT/relative
        if not path.is_file(): raise FileNotFoundError(f"VERIFIED_SOURCE_UNAVAILABLE: {relative}")
        data=path.read_bytes()
        if commit:
            pinned=subprocess.check_output(["git","show",f"{commit}:{relative}"],cwd=ROOT)
            require_pinned_bytes(data,pinned,relative)
        if expected: require_output_hash(data,expected,relative)
        inputs[relative]={"sha256":sha(data),"canonical_lf_sha256":sha(canonical(data)),"pinned_commit":commit}
        return path
    p1=json.loads(read("docs/phase1/RUN_MANIFEST.json",P1).read_text(encoding="utf-8"))
    p2=json.loads(read("results/phase2_results/PHASE2_RUN_MANIFEST.json",P2).read_text(encoding="utf-8"))
    cache=json.loads(read("results/generated/phase2/PHASE2_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    require_pinned_bytes(json.dumps(cache,sort_keys=True).encode(),json.dumps(p2,sort_keys=True).encode(),"Phase 2 run manifest")
    check_run_links(p1,p2,cache)
    e={"p1":p1,"p2":p2,"inputs":inputs}
    for key,name in P2_FILES.items():
        e[key]=pd.read_csv(read(f"results/phase2_results/{name}",P2,p2["output_sha256"][name]))
    for key,name in P1_FILES.items():
        e[key]=pd.read_csv(read(f"docs/phase1/{name}",P1,p1["output_sha256"][name]))
    for key,name in (("daily","phase2_daily_returns.csv"),("decisions","phase2_trading_decisions.csv")):
        e[key]=pd.read_csv(read(f"results/generated/phase2/{name}",expected=p2["output_sha256"][name]),parse_dates=["Date"])
    # Preserve documentary evidence for the correction register without claiming PDF verification.
    for name in ("docs/REVIEWER_CORRECTIONS.md","docs/MANUSCRIPT_REPRODUCTION_ASSESSMENT_2026-10-31.md"):
        read(name,P1)
    return e


def asi_events(decisions):
    rows=[]
    for key,block in decisions.groupby(["Market","Model","Target Weight Cap"],sort=False):
        block=block.sort_values("Date")
        if block.Date.duplicated().any(): raise ValueError("Duplicate rebalance dates")
        weights=pd.DataFrame([json.loads(s) for s in block["Target Weights JSON"]],index=block.Date)
        if not np.isfinite(weights.to_numpy()).all(): raise ValueError("Target asset coverage differs")
        distances=weights.diff().abs().sum(axis=1,min_count=1).iloc[1:]
        for date,value in distances.items():
            rows.append({"Market":key[0],"Model":key[1],"Target Weight Cap":key[2],"Date":date,"ASI Event":float(value)})
    return pd.DataFrame(rows)


def main_wealth(daily, market, model):
    block=daily[daily.Market.eq(market)&daily.Model.eq(model)&daily["Target Weight Cap"].eq(1)].sort_values("Date")
    if block.empty or block.Date.duplicated().any(): raise ValueError("Missing/duplicate main wealth observations")
    net=block["Net Return 10bps"].to_numpy()
    if not np.isfinite(net).all() or (net<=-1).any(): raise ValueError("Invalid plotted net returns")
    return {"dates":[block.Date.iloc[0].date().isoformat()]+block.Date.dt.date.astype(str).tolist(),
            "wealth":np.r_[1.,np.cumprod(1+net)].tolist(),"observations":len(net)}


def build_tables(e):
    tables={}
    rows=[]
    for _,r in e["datasets"].iterrows():
        p=e["principal"][e["principal"].Market.eq(r.Market)]
        if (p["Metric Sample Start"].nunique()!=1 or p["Metric Sample End"].nunique()!=1
                or p["Metric Observations"].nunique()!=1 or p["Metric Sample Start"].iloc[0]!=r["OOS Start"]
                or p["Metric Sample End"].iloc[0]!=r["OOS End"] or p["Metric Observations"].iloc[0]!=r["OOS Observations"]):
            raise ValueError("Table 1 sample definitions differ from principal strategy evidence")
        rows.append({"Market":r.Market,"ETF Universe":r.Tickers,"Currency":"USD (US-listed ETFs)",
            "Common Price Start":r["Effective Price Start"],"Common Price End":r["Effective Price End"],
            "Common Price Observations":r["Price Observations"],"OOS Start":r["OOS Start"],"OOS End":r["OOS End"],
            "OOS Observations":r["OOS Observations"],"Rebalanced Strategy Benchmark":"1/N, same universe and 63-session schedule",
            "Passive ETF Reference":r["Benchmark Label"],"Evidence Phase":"Phase 1 dataset provenance + Phase 2 strategy samples"})
    tables[1]=pd.DataFrame(rows)
    renames={"Annualized Return":"Net Annualized Return","Metric Sample Start":"OOS Start","Metric Sample End":"OOS End",
             "Metric Observations":"OOS Observations","Average Rebalance Turnover":"Mean Rebalance L1 Turnover"}
    cols=["Market","Model","Target Weight Cap","Cost (bps per L1)","Annualized Return","Annualized Volatility","Sharpe Ratio",
          "Max Drawdown","Average Rebalance Turnover","ASI","Net Terminal Wealth","Initial Deployment Turnover","Initial Deployment Cost (bps)",
          "Metric Sample Start","Metric Sample End","Metric Observations"]
    tables[2]=e["principal"][cols].rename(columns=renames).assign(**{"Evidence Phase":"Phase 2 principal"})
    cols=["Market","Model","Target Weight Cap","Cost (bps per L1)","Annualized Return","Sharpe Ratio","Max Drawdown",
          "Average Rebalance Turnover","ASI","Maximum Target Weight","Mean Target HHI","Maximum End-of-Day Weight","Mean End-of-Day HHI",
          "Metric Sample Start","Metric Sample End","Metric Observations"]
    tables[3]=e["concentration"][cols].rename(columns=renames).copy()
    base=tables[3][tables[3]["Target Weight Cap"].eq(1)].set_index(["Market","Model"])["Net Annualized Return"]
    tables[3]["Return Change vs 100% Cap (bps)"]=[(r["Net Annualized Return"]-base.loc[(r.Market,r.Model)])*10000 for _,r in tables[3].iterrows()]
    tables[3]["Evidence Phase"]="Phase 2 matched constraints"
    tables[4]=e["cost"].rename(columns=renames).assign(**{"Evidence Phase":"Phase 2 cost sensitivity"})
    tables[5]=e["statistics"].copy()
    tables[5]["Bootstrap Method"]="paired 20-session circular blocks; common indices; empirical-mean-centered approximate null; 95% percentile interval"
    tables[5]["Multiplicity Adjustment"]="None; duplicated cap-inactive BL/1N rows are not independent evidence"
    tables[5]["Evidence Phase"]="Phase 2 net 10bps comparisons"
    cols=["Crisis","Market","Model","Requested Crisis Start","Requested Crisis End","Crisis First Trading Day","Crisis Last Trading Day",
          "Crisis Observations","Buy-Hold Max Drawdown","Buy-Hold Trough Date","Buy-Hold Recovery Date","Buy-Hold Recovery Trading Days",
          "Buy-Hold Peak Date","Buy-Hold Peak Wealth At Trough","Buy-Hold Recovery Target","Buy-Hold Recovery Duration"]
    tables[6]=e["crisis"][cols].assign(**{"Experiment":"Standalone frozen-holdings gross stress; not rolling main OOS",
        "Wealth Definition":"NAV 1 before first event return; buy-and-hold through recovery; no interim trades",
        "Evidence Phase":"Phase 1 supplementary"})
    rows=[]
    for _,r in e["factors"].iterrows():
        for term in ("Alpha","MKT","SMB","HML","MOM"):
            rows.append({"Market":"US","Model":r.Model,"Term":term,"Coefficient":r.Alpha if term=="Alpha" else r[term+"_beta"],
                "Coefficient Units":"daily excess-return intercept" if term=="Alpha" else "dimensionless factor beta",
                "HAC t-statistic":r.Alpha_t_stat if term=="Alpha" else r[term+"_t_stat"],
                "HAC p-value":r.P_value_Alpha if term=="Alpha" else r[term+"_p_value"],
                "Alpha Annualized Arithmetic":r.Alpha_Annualized if term=="Alpha" else None,
                "R-squared":r.R_squared,"Sample Start":r["Sample Start"],"Sample End":r["Sample End"],
                "Observations":r.Observations,"HAC Max Lags":r.HAC_MaxLags,"Factor Source":r["Factor Source"],
                "Factor Units":r["Factor Values"],"Factor Aligned SHA256":r["Factor Aligned SHA256"],
                "Return Source":"Phase 1 net US strategy; not refitted to Phase 2 paths/caps/1N",
                "Evidence Phase":"Phase 1 supplementary"})
    tables[7]=pd.DataFrame(rows)
    tables[8]=e["tau"].assign(**{"Cost (bps per L1)":10,"Experiment":"US standalone fixed tau; not adaptive main tau",
        "Omega Definition":"diagonal annualized covariance x10, independent of tau","Evidence Phase":"Phase 1 supplementary"})
    return tables


def validate_numeric_links(e,tables):
    events=asi_events(e["decisions"])
    for _,r in tables[2].iterrows():
        wealth=main_wealth(e["daily"],r.Market,r.Model)
        events_model=events[events.Market.eq(r.Market)&events.Model.eq(r.Model)&events["Target Weight Cap"].eq(1)]
        if (wealth["observations"]!=r["OOS Observations"] or not np.isclose(wealth["wealth"][-1],r["Net Terminal Wealth"],atol=1e-10)
                or wealth["dates"][0]!=r["OOS Start"] or wealth["dates"][-1]!=r["OOS End"]
                or not np.isclose(events_model["ASI Event"].mean(),r.ASI,atol=1e-12)):
            raise ValueError("Publication table does not reconcile to its daily/rebalance evidence")
    return events


def table_filename(number): return f"table_{number:02d}_{TABLE_NAMES[number]}.csv"


def manuscript_table(frame):
    frame=frame.copy()
    def fmt(value,col):
        if pd.isna(value): return "—"
        if isinstance(value,(float,np.floating)):
            if col in PERCENT_COLUMNS: return f"{100*value:.4f}%"
            if col in ("Two-sided P-value","HAC p-value"): return "<0.0001" if value<.0001 else f"{value:.4f}"
            return f"{value:.6f}"
        return str(value).replace("|"," / ").replace("\n"," ")
    return "| "+" | ".join(frame.columns)+" |\n| "+" | ".join(["---"]*len(frame.columns))+" |\n"+"\n".join(
        "| "+" | ".join(fmt(v,c) for c,v in zip(frame.columns,row))+" |" for row in frame.itertuples(index=False,name=None))


def readable_tables(t):
    show={
        1:["Market","ETF Universe","Currency","Common Price Start","Common Price End","Common Price Observations","OOS Start","OOS End","OOS Observations"],
        2:["Market","Model","Net Annualized Return","Annualized Volatility","Sharpe Ratio","Max Drawdown","Mean Rebalance L1 Turnover","ASI","Net Terminal Wealth"],
        3:["Market","Model","Target Weight Cap","Net Annualized Return","Sharpe Ratio","Mean Rebalance L1 Turnover","Mean Target HHI","Return Change vs 100% Cap (bps)"],
        4:["Market","Model","Target Weight Cap","Cost (bps per L1)","Gross Annualized Return","Net Annualized Return","Net Terminal Wealth"],
        5:["Market","Target Weight Cap","Strategy B","Sharpe Difference A minus B","95% CI Lower","95% CI Upper","Two-sided P-value","Paired Observations"],
        6:["Market","Model","Requested Crisis Start","Requested Crisis End","Buy-Hold Max Drawdown","Buy-Hold Trough Date","Buy-Hold Recovery Date","Buy-Hold Recovery Trading Days"],
        7:["Model","Term","Coefficient","HAC t-statistic","HAC p-value","Alpha Annualized Arithmetic","Observations","HAC Max Lags"],
        8:["Market","Tau","Sharpe Ratio","OOS Start","OOS End","OOS Observations"]}
    notes={1:"USD-listed ETFs. Price samples are common observed dates; OOS begins after 252 estimation sessions. Passive ETF reference and price counts are in the CSV. The research benchmark is rebalanced 1/N.",
        2:"Phase 2; net 10 bps per L1 turnover; 100% target cap; arithmetic annual mean, sample volatility, Sharpe RF=0. Wealth starts at 1 and compounds simple net returns. Rebalance turnover excludes initial cash deployment, which is separately 1 / 10 bps.",
        3:"Phase 2; matched BL/MV target bounds, 10 bps. Return change is capped minus the same strategy's 100% result, in annualized arithmetic basis points. The bound applies at rebalances, not continuously to drifting holdings.",
        4:"Phase 2; all four cost assumptions and both optimized caps. Arithmetic annual return and compounded terminal wealth are distinct metrics. Gross paths and trading decisions are reused across costs. Full cost expenditure and turnover are retained in CSV.",
        5:"Phase 2; BL minus comparator at net 10 bps, paired 20-session circular bootstrap, 2,000 iterations, seed 42. Same-date block indices preserve pairing. Approximate empirical-mean-centered null; two-sided p-values, percentile 95% intervals, no multiplicity adjustment. Capped BL/1N duplicates inactive-cap comparisons.",
        6:"Phase 1 standalone gross stress test; last target strictly before event, purchased before first event return, no further trades through recovery. Recovery target is crisis-start NAV 1, duration is trading-index positions from crisis-window maximum-drawdown trough to first subsequent recovery. This is neither recovery to the previous peak nor time from crisis start. Missing recovery is censored. Legacy weighted-log metrics are excluded.",
        7:"Phase 1 US-only daily Rp−RF on US FF3+momentum, source percentages divided by 100, intercept OLS with Newey–West/HAC maxlags 5. Sample 2011-01-04–2024-12-31, 3,521 observations. Coefficient alpha is daily; the annual alpha column multiplies by 252. Blank annual alpha for beta rows is not missing estimation evidence. These are not refitted Phase 2 capped/1N regressions.",
        8:"Phase 1 US fixed-tau net 10 bps runs, same universe/window/constraints/cost convention. Omega independent of tau. Distinct from the main strategy's ex-ante trailing-volatility tau selection; no tuning or new optimization in Phase 3."}
    result="# Final research tables\n\nMachine-readable CSVs retain source precision and explicit provenance. Percentages below are display conversions, not recalculated experiments.\n"
    for n in range(1,9):
        result+=f"\n## Table {n} — {TABLE_NAMES[n].replace('_',' ').title()}\n\n"+manuscript_table(t[n][show[n]])+"\n\n"+notes[n]+"\n"
        if n==1:
            result+="\nTable 1, benchmark definitions:\n\n"+manuscript_table(t[1][["Market","Rebalanced Strategy Benchmark","Passive ETF Reference"]])+"\n"
    return result


def write_text(path,text):
    path.write_text(text,encoding="utf-8",newline="\n")


def write_findings(out,e,tables,figures):
    ranking=[]
    for (market,bps),block in tables[4][tables[4]["Target Weight Cap"].eq(1)].groupby(["Market","Cost (bps per L1)"],sort=False):
        ranking.append({"Market":market,"Cost (bps per L1)":bps,
            "Arithmetic net-return ranking":" > ".join(block.sort_values("Net Annualized Return",ascending=False).Model),
            "Terminal-wealth ranking":" > ".join(block.sort_values("Net Terminal Wealth",ascending=False).Model)})
    main=tables[2].set_index(["Market","Model"])
    differences=[]
    for market in MARKETS:
        bl=main.loc[(market,"Black-Litterman")]; ew=main.loc[(market,"Equal-weight")]
        differences.append({"Market":market,"BL minus 1/N Net Return (annual bps)":(bl["Net Annualized Return"]-ew["Net Annualized Return"])*10000,
                            "BL minus 1/N Sharpe":bl["Sharpe Ratio"]-ew["Sharpe Ratio"]})
    count=int((tables[5]["Two-sided P-value"]<.05).sum())
    report=f'''# Final empirical findings — Phase 3

**Readiness: READY_WITH_LIMITATIONS.** The eight requested tables and eight available figures are frozen from verified prior outputs. Crisis daily-path Figure 07 is unavailable; the verified buy-and-hold crisis summary remains Table 6. No optimization, bootstrap, market download, factor refit or regime estimation was run in Phase 3. This is a publication evidence package, not a revised manuscript or a replication of the March 2026 paper.

## Evidence identity and experiment boundaries

- Principal/robustness evidence: Phase 2 run `{e['p2']['run_id']}`, executed source `{e['p2']['phase2_commit']}`, frozen on Phase 2 commit `{P2}`. Tables 2–5 and Figures 01–06 use these outputs and associated verified daily returns/decisions.
- Supplementary evidence: Phase 1 run `{e['p1']['run_id']}`, executed source `{e['p1']['git_commit']}`, archived on completed Phase 1 commit `{P1}`. Tables 6–8 and Figures 08–09 retain this provenance, not a relabelled Phase 2 fit. Table 1 links Phase 1 dataset coverage to the identical Phase 2 price vintage and OOS samples.
- Frozen price fingerprints agree across these sources. Each input is checked against its protected source commit or the corresponding pinned run-manifest hash. LF/CRLF conversion alone is tolerated for historical text files; actual and canonical hashes are both recorded.
- Machine-readable authority: `table_01_*.csv` through `table_08_*.csv`; all numerical values are selected or explicitly transformed from source evidence. `FINAL_RESEARCH_TABLES.md` is the manuscript-readable rendering. P-values below the display threshold, including machine underflow zeros, are printed as <0.0001; source precision is preserved in CSV.

## What the results support

BL has much lower target ASI than unrestricted historical-mean Markowitz in all three baskets. ASI measures changes in optimizer targets; it is not actual trading, initial deployment or evidence of a significant Sharpe gain. Rebalanced 1/N has zero target ASI but positive rebalance turnover because prices make holdings drift.

BL's returns and Sharpe closely resemble the periodically rebalanced 1/N benchmark. Their differences, derived from Table 2, are:

{manuscript_table(pd.DataFrame(differences))}

These small observed differences do not establish additional economic or causal value from Bayesian updating over 1/N. This is particularly relevant because the default equilibrium prior is an **equal-weight proxy**, not observed market-capitalization weights, and views are a mild historical-mean tilt. The experiment is strongly anchored toward equal allocations by design.

The predefined matched 40% target cap reduces Markowitz target HHI, target instability and traded turnover and narrows its Sharpe gaps with BL. US/China Markowitz Sharpe improves under the cap; India Sharpe declines. The BL cap is inactive in these realized samples. Bounds are applied identically to both optimized strategies at each matched comparison. A 40% target bound is not continuous enforcement on drifting holdings.

BL has no universal return or drawdown dominance: its US/India drawdowns are worse than unrestricted Markowitz in the primary comparison. No claim of statistically superior downside protection follows from descriptive MDDs or selected crisis events.

## Costs, arithmetic returns and compounded wealth

All four cost rates reuse the same gross paths and trading decisions. Positive costs reduce terminal wealth for unchanged paths. Lower turnover alone does not prove better net investment performance. The actual rankings by the two distinct metrics are:

{manuscript_table(pd.DataFrame(ranking))}

Thus cost changes can alter a terminal-wealth ranking without altering the arithmetic annual-return ranking. Arithmetic annual mean is daily mean ×252; terminal wealth is the product of one plus each daily net simple return. They must never be described as interchangeable growth rates. Direct modeled fee expenditure is also distinct from gross-minus-net terminal wealth, which includes growth forgone. Transaction costs are proportional to the existing drift-adjusted L1 turnover model; no execution-spread or market-impact calibration is claimed.

## Statistical uncertainty and generalization

Table 5 contains {len(tables[5])} scenario rows, with {count} unadjusted p-values below 0.05. All corresponding 95% percentile intervals include zero. The three cap-inactive BL/1N rows duplicate the main BL/1N results rather than adding independent evidence. The appropriate conclusion is failure to establish a Sharpe difference under the retained approximate paired bootstrap, not proof of equivalence or equal future performance. No new inferential framework or multiplicity adjustment was introduced.

The markets have unequal OOS periods and observation counts (Table 1). Cross-market cumulative wealth is therefore not a common-horizon comparison. These are small, overlapping baskets of **US-listed USD-denominated ETFs** with international equity exposure, not pure local-currency Chinese/Indian market returns. Generalization beyond these instruments, samples and modeled costs is limited.

## Supplementary evidence and missing material

Table 6 is a standalone historical stress test: the last pre-crisis target is purchased before the first event return, then held without trades through recovery. Recovery means the first subsequent return to crisis-start NAV 1 after the crisis-window drawdown trough; the duration is trading-index positions from trough to recovery. It is not recovery to the previous peak or time from crisis start. Missing recovery remains censored. Main rolling OOS returns are not substituted for these frozen-holdings stress paths. Legacy weighted-log summary fields are deliberately excluded.

**CRISIS_DAILY_PATH_UNAVAILABLE:** the retained verified evidence contains primary crisis drawdown/recovery summaries, not frozen-holdings daily crisis curves. Figure 07 is not generated, and no path is reconstructed from summary values. Retain the limitation or recover original verified path evidence before using such a figure.

Table 7 and Figure 08 are US-only factor evidence from Phase 1, with exact sample/factor fingerprints and HAC inference. They do not attribute China/India performance to US factors and are not regressions of Phase 2 capped or 1/N paths. Table 8/Figure 09 are the five pre-existing US fixed-tau runs, distinct from the main historical-volatility adaptive rule. Phase 1 Markov smoothed states remain ex-post descriptions, never prospective trading signals; no regime refit is part of this package.

The historical manuscript PDF is **not available in this task environment**. `MANUSCRIPT_CHANGE_REGISTER.md` therefore uses the existing documented discrepancies and marks every paper-specific entry NOT_INDEPENDENTLY_CHECKED_AGAINST_PDF. Original historical AUM/capitalization inputs, ownership evidence and March run vintages remain unrecovered. The package neither edits the original manuscript nor establishes exact March-paper reproduction.

## Figures and verification

'''
    for name,record in figures.items():
        report+=f"- **{name} ({record['phase']}):** {record['caption']}\n"
    report+='''
Every plotted numeric payload is derived from the cited original files; payload hashes, source hashes, annotations and generated figure hashes are recorded in PHASE3_RUN_MANIFEST.json. The checker regenerates the expected tables/payloads, verifies exact table contents to numerical serialization tolerance, checks table/daily/ASI links, checks SVG annotation text and rejects missing/stale/mismatched manifests. PNGs and SVGs use the same plotted data. Visual inspection is performed on the rendered PNGs before delivery.

The four protected historical branches and original paper records remain unchanged. This phase stops at evidence preparation: no manuscript drafting, SSRN upload, merge or automatic next phase is performed.
'''
    write_text(out/"FINAL_EMPIRICAL_FINDINGS.md",report)


def write_change_register(out):
    rows=[
        ("Data/sample sections","Uniform 2010–2025 coverage is documented despite unequal ETF histories","Correct","Use Table 1 exact common/OOS windows, exclusive requested end and USD-listed ETF description","table_01_dataset_definitions.csv","Original data required only to defend the historical claim"),
        ("BL method / equilibrium prior","Prior described as market-capitalization implied","Rewrite","State equal-weight proxy, Pi=lambda Sigma w_eq, mild historical tilt and actual tau/Omega rules","Phase 2 manifest configuration; Table 8 fixed-tau note","Original dated cap/AUM weights required to retain capitalization wording"),
        ("Figure 1 and Table 2","Existing documentation records inconsistent Sharpe annotations / experiment families","Correct","Replace revised-study principal table and wealth figure together from the frozen net daily paths","Table 2; Figure 01; Phase 2 daily returns","Original plot sources needed to explain historical discrepancy"),
        ("Performance conclusions","Universal superiority or significant stability-driven performance benefit","Rewrite","Report market-specific outcomes, near-1/N behavior and uncertainty; no causal Bayesian advantage established","Tables 2–5; Figures 02–06","No additional historical evidence needed for revised-study wording"),
        ("Turnover / cost section","Turnover, ASI, cost drag and net performance interpreted interchangeably","Rewrite","Separate target ASI, drift L1 turnover, initial deployment, direct fees, arithmetic mean and terminal wealth","Tables 2/4; Figures 03/05","Original turnover definition needed to reconcile the old numerical claim"),
        ("Crisis section / recovery table","Historical weighted-log and recovery conventions differ from primary buy-and-hold interpretation","Correct","Use Table 6 standalone gross stress summaries and explicit trough-to-start-NAV recovery definition; omit unsupported daily curves","table_06_crisis_stress_tests.csv; Figure 07 unavailable","Verified original daily crisis paths required before a crisis-path figure"),
        ("US factor table and international momentum claims","Factor signs/figures differ; US regression used to explain China/India","Rewrite","Use Table 7 US-only HAC results with source sample/units; remove unsupported international attribution","Table 7; Figure 08","Original regression artifacts needed to reconcile historical coefficients/sign"),
        ("SOE/private table and figure","Original dated stock-level ownership inputs unavailable; documented internal inconsistency","Remove","Do not present unreproduced ownership findings as verified evidence; retain only clearly labelled historical limitation if necessary","Phase 1 manuscript assessment and reviewer corrections","Original membership, ownership dates, returns and test artifacts required"),
        ("Statistical significance section","Documented p=0.0106 interpreted as significant at 1%; historical tests differ","Correct","Correct threshold wording; use Table 5 only for the new Sharpe comparisons with CIs and explicit approximate method","Table 5; documented Phase 1 discrepancy","Original volatility/ASI test inputs required for their reproduction"),
        ("Regime section","Smoothed full-sample states described as prospective or causal protection","Rewrite","Identify ex-post descriptive smoothed states; separate training-only tau choice from Markov diagnostics","Phase 1 run-manifest supplementary_evidence / regime conventions","Original regime runs needed to reconcile historical table; no causal claim supported"),
        ("Tau sensitivity table","Historical tau values differ from verified fixed-tau runs","Correct","Use the five verified Phase 1 fixed-tau observations; distinguish from adaptive main rule; no parameter search","Table 8; Figure 09","Original tau code/input vintage required to explain old table"),
        ("AI assistance / reproducibility declarations","Disclosure may predate substantial AI-assisted code, audit, experiments and figure preparation","Rewrite","Author should approve an accurate account of AI assistance, human review, code/run IDs, data access and frozen-input limitations","Phase 1–3 manifests and verification records","Author confirmation required; do not invent historical assistance details"),
        ("Historical March record","Original manuscript and transcribed result tables are historical evidence","Retain","Keep immutable and distinguish the new revised-study evidence from exact historical replication","results/paper_results/; source branch SHAs","Missing original inputs remain a historical-reproduction limitation"),
    ]
    columns=["Original section / figure","Documented claim or issue","Action","Verified replacement / required action","Source output / evidence","Requires original evidence?"]
    table=pd.DataFrame(rows,columns=columns)
    table["PDF Verification Status"]="NOT_INDEPENDENTLY_CHECKED_AGAINST_PDF"
    text='''# Manuscript change register

**PDF_NOT_AVAILABLE_IN_TASK_ENVIRONMENT.** No original manuscript PDF is present among the repository files or supplied attachments. All paper-specific entries below derive from the existing pinned `docs/REVIEWER_CORRECTIONS.md` and `docs/MANUSCRIPT_REPRODUCTION_ASSESSMENT_2026-10-31.md`, not a new independent reading of the PDF. Section labels are descriptive references from that documentary record, not newly verified page numbers. New-study replacements refer to generated Phase 3 tables/figures.

This is a change register only. No revised manuscript is written, no historical paper record is edited, and nothing is submitted to SSRN. The author must check the original PDF and approve substantive manuscript language and disclosures before revision.

'''+manuscript_table(table)+"\n"
    write_text(out/"MANUSCRIPT_CHANGE_REGISTER.md",text)


def validate_bundle(out,e=None):
    from scripts.phase3_figures import figure_payloads, verify_figure_annotations
    out=Path(out)
    m=json.loads((out/"PHASE3_RUN_MANIFEST.json").read_text(encoding="utf-8"))
    e=load_evidence() if e is None else e
    if m["source_runs"]!={"Phase 1":e["p1"]["run_id"],"Phase 2":e["p2"]["run_id"]}:
        raise ValueError("Stale Phase 3 source-run identity")
    if m["inputs"]!=e["inputs"]: raise ValueError("Source files changed after Phase 3 freeze")
    tables=build_tables(e); validate_numeric_links(e,tables)
    for number,expected in tables.items():
        actual=pd.read_csv(out/table_filename(number))
        pd.testing.assert_frame_equal(actual,expected,check_dtype=False,check_exact=False,atol=1e-12,rtol=1e-12)
    if (out/"FINAL_RESEARCH_TABLES.md").read_text(encoding="utf-8")!=readable_tables(tables):
        raise ValueError("Manuscript-readable table content differs from authoritative CSV definitions")
    payloads=figure_payloads(e,tables)
    if set(m["figures"])!=set(payloads): raise ValueError("Missing or mislabelled figures")
    for name,p in payloads.items():
        record=m["figures"][name]
        if record["payload_sha256"]!=payload_hash(p): raise ValueError("Figure uses stale/wrong sample or scenario")
        if record["source_files"]!=p["source"] or record["phase"]!=p["phase"]: raise ValueError("Figure provenance mismatch")
        verify_figure_annotations(out/"figures"/(name+".svg"),record["annotations"])
    for relative,expected in m["outputs"].items():
        if sha((out/relative).read_bytes())!=expected: raise ValueError(f"Final output changed: {relative}")
    return {"status":"PASS","tables":len(tables),"table_rows":{str(k):len(v) for k,v in tables.items()},
        "figures":len(payloads),"formats":["PNG 300dpi","vector SVG"],
        "numeric_table_daily_asi_links":"PASS","figure_payload_and_annotation_links":"PASS",
        "phase_provenance_and_sample_disclosure":"PASS","new_optimization_or_bootstrap_runs":0,
        "blocked_figures":{"07_crisis_drawdown_paths":"CRISIS_DAILY_PATH_UNAVAILABLE; verified summary only"},
        "manuscript_pdf":"NOT_AVAILABLE; change register documentary, not independently checked against PDF",
        "readiness":"READY_WITH_LIMITATIONS"}


def build_bundle(out=OUT):
    from scripts.phase3_figures import figure_payloads, render_figures
    out=Path(out)
    if out.exists() and any(out.iterdir()): raise FileExistsError("Preserve prior Phase 3 evidence; choose a new empty output directory")
    e=load_evidence(); tables=build_tables(e); validate_numeric_links(e,tables)
    out.mkdir(parents=True,exist_ok=True)
    for n,frame in tables.items(): frame.to_csv(out/table_filename(n),index=False,lineterminator="\n",float_format="%.17g")
    write_text(out/"FINAL_RESEARCH_TABLES.md",readable_tables(tables))
    plots=render_figures(figure_payloads(e,tables),out/"figures")
    write_findings(out,e,tables,plots); write_change_register(out)
    manifest={"run_id":str(uuid.uuid4()),"completed_at_utc":datetime.now(timezone.utc).isoformat(),
        "executed_source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        "git_dirty":bool(subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).strip()),
        "base_phase2_commit":P2,"phase1_evidence_commit":P1,
        "source_sha256":{str(p.relative_to(ROOT)).replace('\\','/'):sha(p.read_bytes()) for p in
            (Path(__file__),ROOT/"scripts/phase3_figures.py",ROOT/"requirements-phase1-lock.txt")},
        "source_runs":{"Phase 1":e["p1"]["run_id"],"Phase 2":e["p2"]["run_id"]},
        "inputs":e["inputs"],"configuration":{"Phase 2":e["p2"]["configuration"],"cost_bps":e["p2"]["cost_bps"],
            "bootstrap":e["p2"]["bootstrap"],"Phase 1 supplementary":e["p1"]["configuration"]},
        "tables":{table_filename(n):{"rows":len(tables[n]),"source_files":TABLE_SOURCES[n],
            "transforms":"explicit selection/renaming in build_tables; Table 3 additionally computes annual return delta x10000; Table 7 reshapes recorded coefficients/t/p; no estimation",
            "phase":"Phase 2" if n in (2,3,4,5) else "Phase 1 supplementary" if n in (6,7,8) else "Linked Phase 1 dataset / Phase 2 samples"} for n in tables},
        "figures":plots,"blocked_figures":{"07_crisis_drawdown_paths":"CRISIS_DAILY_PATH_UNAVAILABLE"},
        "evidence_notes":{"crisis":"Only primary buy-hold summary fields; legacy weighted-log data excluded",
            "factors":"Phase 1 US regression; not a refit to Phase 2 returns",
            "tau":"Phase 1 fixed-tau scenarios; distinct from adaptive main strategy",
            "new_market_downloads":False,"new_optimization_runs":0,"new_bootstrap_runs":0,
            "PDF_verification":"Original manuscript PDF absent; correction register uses existing documentary evidence"},
        "environment":{"python":platform.python_version(),"os":platform.platform(),
            "packages":{name:importlib.metadata.version(name) for name in ("numpy","pandas","matplotlib")}},
        "outputs":{str(p.relative_to(out)).replace('\\','/'):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}}
    write_text(out/"PHASE3_RUN_MANIFEST.json",json.dumps(manifest,indent=2)+"\n")
    validation=validate_bundle(out,e)
    write_text(out/"PHASE3_OUTPUT_VALIDATION.json",json.dumps(validation,indent=2)+"\n")
    print(json.dumps(validation,indent=2))
    return validation


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=OUT)
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args()
    if args.validate_only: print(json.dumps(validate_bundle(args.output_dir),indent=2))
    else: build_bundle(args.output_dir)
