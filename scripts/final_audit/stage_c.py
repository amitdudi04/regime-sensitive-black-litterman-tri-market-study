import sys,json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));O=R/'outputs/final_professor_challenge_resolution';G=R/'results/generated';P=G/'phase2'
from backtesting.paper_backtest import _l1_turnover
from pipelines.phase2_experiments import apply_costs
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=pd.read_csv(P/'phase2_daily_returns.csv',parse_dates=['Date']);dec=pd.read_csv(P/'phase2_trading_decisions.csv',parse_dates=['Date']);dates=sorted(set.intersection(*(set(d[d.Market==m].Date) for m in d.Market.unique())));start=min(dates);end=max(dates);rows=[]
for (market,model,cap),g in d.groupby(['Market','Model','Target Weight Cap']):
 s=g.set_index('Date')['Net Return 10bps'].reindex(dates);assert s.notna().all();wealth=(1+s).cumprod();dd=wealth/np.maximum.accumulate(np.r_[1,wealth])[1:]-1
 t=dec[(dec.Market==market)&(dec.Model==model)&(dec['Target Weight Cap']==cap)].set_index('Date');w=pd.DataFrame([json.loads(v) for v in t['Target Weights JSON']],index=t.index);a=w.diff().abs().sum(axis=1);a.iloc[0]=np.nan;mask=(t.index>=start)&(t.index<=end);first=t.index[0];valid=mask&(t.index!=first)
 rows.append(dict(Market=market,Model=model,Cap=cap,Start=str(start.date()),End=str(end.date()),N=len(s),AnnualReturn=s.mean()*252,Volatility=s.std(ddof=1)*np.sqrt(252),Sharpe=s.mean()/s.std(ddof=1)*np.sqrt(252),MaxDrawdown=dd.min(),DecisionDifferences=int(valid.sum()),ASI=a.loc[valid].mean(),Turnover=t.loc[valid,'L1 Turnover'].mean()))
pd.DataFrame(rows).to_csv(O/'stage_c_common_period.csv',index=False)
records=[]
for market in ['us','china','india']:
 p=G/f'price_data/{market}_adjusted_close.csv';m=json.loads((p.with_suffix('.json')).read_text());a=json.loads((R/f'docs/phase1/{market}_adjusted_close.json').read_text());assert sha(p)==m['sha256']==a['sha256'];records.append(dict(Identifier=str(p.relative_to(R)),Provider=m['source'],Retrieval=m.get('downloaded_at_utc','unknown'),SHA256=sha(p),Available=True,Redistribution='Not authorized; private snapshot excluded'))
p=G/'factor_data/us_daily_2011-01-04_2024-12-31.csv';m=json.loads(p.with_suffix('.json').read_text());a=json.loads((R/'docs/phase1/factor_us_daily_2011-01-04_2024-12-31.json').read_text());assert sha(p)==m['sha256']==a['sha256'];records.append(dict(Identifier=str(p.relative_to(R)),Provider=m['source'],Retrieval=m['retrieved_at_utc'],SHA256=sha(p),Available=True,Redistribution='Permission not established; private snapshot excluded'))
pd.DataFrame(records).to_csv(O/'stage_c_input_availability.csv',index=False)
a=pd.Series([.6,.4]);b=pd.Series([.5,.5]);assert np.isclose(_l1_turnover(b,a),.2);assert np.isclose(_l1_turnover(b,None),1)
date=pd.Timestamp('2020-01-02');net=apply_costs(pd.Series([.02],index=[date]),pd.Series([.2],index=[date]),10);assert np.isclose(net.iloc[0],1.02*(1-.0002)-1)
(O/'STAGE_C_COMPARABILITY_REPRODUCIBILITY.md').write_text(f'''# Stage C comparability and reproducibility

## C1 common-calendar robustness

stage_c_common_period.csv intersects actual stored return dates: {start.date()} through {end.date()}, {len(dates)} sessions, net 10 bps per L1. Strategies and original training schedules remain unchanged. Wealth is rebased to 1 immediately before the evaluation slice; original trade charges inside the slice are retained, without a newly imposed initial deployment. This is a conditional common-period comparison, not a new deploy-on-start strategy. ASI includes changes whose current decision falls within the interval, using its actual previous target even if earlier; turnover is the actual in-period trade excluding original initial deployment. Each metric has its decision count. Cross-market calendar matching does not equalize exposures or establish country causality. RESOLVED_WITH_LIMITATIONS.

## C2 ETF and currency interpretation

All assets are US-listed USD-traded ETFs. Labels describe underlying national exposures; USD investor returns include any embedded currency translation and fund design. They are not local-currency national index returns. Constituent overlaps remain. No isolated currency factor or domestic market-efficiency effect is identified. Existing manuscript caveats are correct and should remain. INHERENT_RESEARCH_LIMITATION; RESOLVED_WITH_LIMITATIONS.

## C3 turnover and fees

At rebalance k, drifted pretrade holdings h have sum 1; target w has sum 1. L1 T=sum abs(w-h); purchases equal sales, so one-way turnover=T/2. Initial cash deployment is special: purchases=1, sales=0, T_initial=1; do not halve that charge mechanically. Current net growth=(1+r_gross)(1-c_L1 T). To charge the identical rebalance fee using half-L1 q=T/2 requires c_oneway=2 c_L1. A quoted 10 bps per L1 equals 20 bps per half-L1 on fully invested rebalances. This is a proportional weight-cost convention, not an implicit dollar fee-funding solver.

Analytical implementation check: pretrade [0.6,0.4] to target [0.5,0.5] gives T=0.2, purchases=sales=0.1. At c=0.001 fee fraction=0.0002. Gross return .02 gives net growth 1.019796 (net return .019796). Initial deployment turnover=1. All assertions passed against actual _l1_turnover and apply_costs. Direct fees sum pretrade net NAV times fee fraction. Terminal wealth impact also includes foregone future growth and differs from total direct fees. No model change. RESOLVED.

## C4 frozen inputs

All four snapshots exist privately and match archived hashes. Exact identifiers, provider, retrieval timestamps and SHA-256 are in stage_c_input_availability.csv. No raw datasets are included in this public package. Redistribution permission is not established. Independent researchers must obtain access under provider terms; this audit does not certify a license or legal right to redistribute. No new data downloaded.

Reproduction: use pinned requirements-phase1-lock.txt, exact archived source commits and configurations in the run manifests; acquire Yahoo Finance adjusted-close observations for the stated ETFs and Kenneth French daily FF3/momentum factors through authorized access. Align common observed dates within each basket; do not fill missing observations. Factor source percentages convert once to decimals. Compare acquired bytes and metadata with archived hashes before claiming exact reproduction. Later provider vintages can differ. Equivalent newly acquired data can test the revised specification but cannot by themselves reproduce the frozen experiment. March price vintages, priors and ownership inputs remain unavailable; revised-specification reproducibility and March reproduction are separate claims. RESOLVED_WITH_LIMITATIONS.
''',encoding='utf-8')
(O/'STAGE_C_MANIFEST.json').write_text(json.dumps({p.name:sha(p) for p in O.glob('stage_c*.csv')},indent=2));print('Stage C passed',start,end,len(dates))
