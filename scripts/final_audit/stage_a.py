import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
OUT=ROOT/'outputs/final_professor_challenge_resolution';G=ROOT/'results/generated';P=G/'phase2'
from backtesting.paper_backtest import BacktestConfig,_regime_tau
from core.covariance_estimators import estimate_covariance
from models.black_litterman_model import compute_black_litterman_posterior
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
git=lambda *x:subprocess.check_output(['git',*x],cwd=ROOT,text=True).strip()
manifest=json.loads((P/'PHASE2_RUN_MANIFEST.json').read_text());cfg=BacktestConfig(**manifest['configuration'])
for n,h in manifest['output_sha256'].items():assert sha(P/n)==h
for n,h in manifest['source_sha256'].items():assert sha(ROOT/n)==h
refs={r.split()[1].removeprefix('refs/heads/'):r.split()[0] for r in git('ls-remote','--heads','origin').splitlines()}
(OUT/'GIT_BASELINES.json').write_text(json.dumps({'base':git('rev-parse','HEAD'),'protected_remote_heads':refs},indent=2))
daily=pd.read_csv(P/'phase2_daily_returns.csv',parse_dates=['Date']);dec=pd.read_csv(P/'phase2_trading_decisions.csv',parse_dates=['Date'])
rows=[];active=[];post=[]
for market in ['US','China','India']:
 ds=dec[(dec.Market==market)&(dec['Target Weight Cap']==1)]
 bl=ds[ds.Model=='Black-Litterman'].set_index('Date');ew=ds[ds.Model=='Equal-weight'].set_index('Date');assert bl.index.equals(ew.index)
 w=pd.DataFrame([json.loads(s) for s in bl['Target Weights JSON']],index=bl.index);a=w-1/w.shape[1]
 dd=daily[(daily.Market==market)&(daily['Target Weight Cap']==1)].pivot(index='Date',columns='Model',values='Net Return 10bps')
 x=dd['Black-Litterman'];y=dd['Equal-weight'];sr=lambda s:s.mean()/s.std(ddof=1)*np.sqrt(252)
 row={'Market':market,'Decisions':len(w),'Mean Absolute Active Weight':a.abs().to_numpy().mean(),'Maximum Absolute Active Weight':a.abs().to_numpy().max(),'Average L1 Active Distance':a.abs().sum(axis=1).mean(),'Return Correlation':x.corr(y),'Annual Tracking Error':(x-y).std(ddof=1)*np.sqrt(252),'Annual Arithmetic Return Difference':(x-y).mean()*252,'Sharpe Difference':sr(x)-sr(y),'Turnover Difference':(bl['L1 Turnover'].iloc[1:]-ew['L1 Turnover'].iloc[1:]).mean(),'Terminal Wealth Difference':(1+x).prod()-(1+y).prod()}
 for etf in a:
  active.append({'Market':market,'ETF':etf,'Mean Active':a[etf].mean(),'Std Active':a[etf].std(),'Minimum':a[etf].min(),'Q25':a[etf].quantile(.25),'Median':a[etf].median(),'Q75':a[etf].quantile(.75),'Maximum':a[etf].max()})
 path=G/f'price_data/{market.lower()}_adjusted_close.csv';meta=json.loads((ROOT/f'docs/phase1/{market.lower()}_adjusted_close.json').read_text());assert sha(path)==meta['sha256']
 prices=pd.read_csv(path,index_col='Date',parse_dates=True).loc['2010-01-01':];ret=prices.pct_change(fill_method=None).dropna()
 for date in w.index:
  pos=ret.index.get_loc(date);train=ret.iloc[pos-252:pos];assert len(train)==252
  cov=estimate_covariance(train);sigma=cov.to_numpy();pi=3*sigma@np.repeat(1/w.shape[1],w.shape[1]);mu=train.mean()*252;tau=_regime_tau(train,cfg);omega=np.diag(np.maximum(np.diag(sigma)*10,1e-12));q=pi+.1*(mu.to_numpy()-pi)
  posterior=compute_black_litterman_posterior(pi,cov,np.eye(len(pi)),q,omega,tau).to_numpy()
  independent=pi+np.linalg.solve((tau*sigma+omega).T,(tau*sigma).T).T@(q-pi)
  assert np.allclose(posterior,independent,atol=1e-14)
  for j,etf in enumerate(cov.index):post.append({'Market':market,'Date':str(date.date()),'ETF':etf,'Prior':pi[j],'View':q[j],'Posterior':posterior[j],'Adjustment':posterior[j]-pi[j],'Tau':tau,'Omega over Prior Variance':omega[j,j]/(tau*sigma[j,j])})
 pp=pd.DataFrame(post);pp=pp[pp.Market==market];row['Mean Absolute Posterior Adjustment']=pp.Adjustment.abs().mean();row['Minimum Omega Prior Ratio']=pp['Omega over Prior Variance'].min();row['Maximum Omega Prior Ratio']=pp['Omega over Prior Variance'].max();rows.append(row)
pd.DataFrame(rows).to_csv(OUT/'stage_a_diagnostics.csv',index=False);pd.DataFrame(active).to_csv(OUT/'stage_a_active_weights.csv',index=False);pd.DataFrame(post).to_csv(OUT/'stage_a_posterior_diagnostics.csv',index=False)
caps=pd.read_csv(P/'phase2_concentration_sensitivity.csv');cr=[]
for (market,model),g in caps.groupby(['Market','Model']):
 old=g[g['Target Weight Cap']==1].iloc[0];new=g[g['Target Weight Cap']==.4].iloc[0]
 for col in ['Mean Target HHI','Maximum Target Weight','ASI','Average Rebalance Turnover','Annualized Return','Sharpe Ratio','Max Drawdown']:
  if col in g:cr.append({'Market':market,'Model':model,'Metric':col,'Unrestricted':old[col],'Capped':new[col],'Difference':new[col]-old[col]})
pd.DataFrame(cr).to_csv(OUT/'stage_a_cap_effects.csv',index=False)
(OUT/'STAGE_A_IDENTIFICATION.md').write_text('''# Stage A: identification and benchmark fairness

Stage A reuses validated Phase 2 run ff8cacdc-95f8-458e-8d71-d12efbd9a9f9 (execution source af84ddfbc93edc7a5143c654d6319d67e3139eef; frozen commit 7553cf8bff59a4f3d8bad7d15b779707fc533fa1). All stored output hashes and source fingerprints were checked. No portfolio backtest was rerun. Missing prior/posterior diagnostics alone were reconstructed at stored decision dates from hash-matched prices, using the exact 252-session covariance and tau code.

## A1: why BL resembles 1/N

Pi=lambda Sigma w_eq and Q-Pi=0.10(mu_hist-Pi), P=I. Thus posterior-Pi = tau Sigma (tau Sigma+Omega)^(-1) 0.10(mu_hist-Pi). Omega=10 diag(Sigma) independent of tau. The marginal view/prior variance ratio is 10/tau: 200 or 1,000. These diagonal ratios are not full correlated-matrix shrinkage eigenvalues. With no view adjustment the common quadratic objective is maximized at w_eq; equal weights satisfy both caps. Small posterior adjustments therefore perturb this diversified anchor. Optimizer numerical tolerances also affect tiny active weights; this analysis does not attribute every residual basis point causally to Bayesian information.

stage_a_diagnostics.csv reports all requested market-level weight, return, risk, trading and wealth differences; active-weight distributions by ETF and per-decision priors/views/posteriors appear in the supporting CSVs. Return and Sharpe differences use zero-RF net 10-bps paths; turnover excludes initial deployment. Mean deviation means mean absolute ETF active weight, not the mechanically zero signed cross-sectional mean. Tracking error uses sample daily standard deviation times sqrt(252). Expected-return adjustments are annual-return units.

The evidence establishes strong diversification anchoring and descriptive stabilization relative to unrestricted historical-mean Markowitz. Incremental Bayesian investment value over rebalanced 1/N is not established. The historical-return views are not independently sourced forecasts.

## A2: fairness and constraints

The stored Phase 2 code calls the same backtest with identical universes, covariance estimator, windows, rebalance dates, lambda, nonnegative/full-investment constraints, accounting and cost scenarios for BL and Markowitz. Only expected-return vectors differ within each cap. stage_a_cap_effects.csv quantifies changes from cap 1 to cap 0.4 using existing validated summaries; original levels remain unchanged. The cap is a target bound, not an intraperiod holdings limit. No extra benchmark family or cap was introduced. Average target concentration is summarized by HHI; it is not independent evidence of better investment performance.

## A3: chronology

The 40% scenario is introduced in the Phase 2 implementation commit af84ddfbc93edc7a5143c654d6319d67e3139eef. The execution manifest names that exact clean source commit and records caps [1.0,0.4]. This establishes specification before that recorded execution, not preregistration or independence from earlier Phase 1 findings. No public preregistration record is evidenced. Recommended wording: “The revised research introduced a fixed 40% maximum target-weight robustness specification, applied to both optimized strategies. It was specified in the Phase 2 implementation before its recorded execution; it was not part of the March study or a preregistered design.” Subsequent interpretations are retrospective.

Residual limitation: no design here isolates a causal benefit of Bayesian updating from prior diversification and matched constraints. Stage A is RESOLVED_WITH_LIMITATIONS.
''',encoding='utf-8')
issues={'A1':'REQUIRES_SMALL_DIAGNOSTIC','A2':'RESOLVED_BY_EXISTING_EVIDENCE','A3':'REQUIRES_SMALL_DIAGNOSTIC','B1':'REQUIRES_NEW_PRESPECIFIED_TEST','B2':'REQUIRES_NEW_PRESPECIFIED_TEST','B3':'REQUIRES_SMALL_DIAGNOSTIC','B4':'REQUIRES_SMALL_DIAGNOSTIC','B5':'RESOLVED_BY_EXISTING_EVIDENCE','C1':'REQUIRES_SMALL_DIAGNOSTIC','C2':'INHERENT_RESEARCH_LIMITATION','C3':'REQUIRES_SMALL_DIAGNOSTIC','C4':'REQUIRES_SMALL_DIAGNOSTIC'}
(OUT/'PROFESSOR_CHALLENGE_RESOLUTION_REGISTER.md').write_text('# Master issue register\n\nStages execute A, B, C, then D. No manuscript editing before evidence freeze.\n\n|Issue|Initial inventory|Existing source / run|Action / current status|\n|---|---|---|---|\n'+'\n'.join(f'|{k}|{val}|'+('results/generated/phase2; run ff8cacdc-95f8-458e-8d71-d12efbd9a9f9' if k.startswith('A') or k in ['B1','B2','C1'] else 'results/generated and docs/phase1; Phase 1 manifest')+'|'+('Stage A report and CSVs; RESOLVED_WITH_LIMITATIONS' if k.startswith('A') else 'Pending targeted examination; not resolved')+'|' for k,val in issues.items()),encoding='utf-8')
(OUT/'STAGE_A_MANIFEST.json').write_text(json.dumps({'base_commit':'f9015d2430f0b910ece5ad8963c9f41c1464b604','phase2_run':manifest['run_id'],'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [P/'phase2_daily_returns.csv',P/'phase2_trading_decisions.csv',P/'phase2_concentration_sensitivity.csv',P/'PHASE2_RUN_MANIFEST.json']},'outputs':{p.name:sha(p) for p in OUT.glob('stage_a*.csv')},'checks':['All Phase 2 output hashes','All Phase 2 recorded source hashes','Three private frozen price hashes','Paired decision dates','Independent posterior linear solve'],'stage':'A'},indent=2))
print(pd.DataFrame(rows).to_string(index=False));print('Stage A checks passed')
