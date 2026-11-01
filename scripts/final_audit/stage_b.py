exec(open(__file__.replace('stage_b.py','stage_a.py'),encoding='utf-8-sig').read().split('rows=[];active=[];post=[]')[0].replace("(OUT/'GIT_BASELINES.json').write_text(json.dumps({'base':git('rev-parse','HEAD'),'protected_remote_heads':refs},indent=2))",''))
from analysis.statistical_tests import circular_block_bootstrap_sharpe_difference
rows=[]
for market in ['US','China','India']:
 for cap in [1,.4]:
  def decisions(model,c):
   d=dec[(dec.Market==market)&(dec.Model==model)&(dec['Target Weight Cap']==c)].set_index('Date');w=pd.DataFrame([json.loads(s) for s in d['Target Weights JSON']],index=d.index)
   return d,w
  a,wa=decisions('Black-Litterman',cap)
  for model in ['Markowitz','Equal-weight']:
   b,wb=decisions(model,cap if model=='Markowitz' else 1);assert a.index.equals(b.index)
   for metric,x,y in [('ASI',wa.diff().abs().sum(axis=1).iloc[1:],wb.diff().abs().sum(axis=1).iloc[1:]),('Turnover',a['L1 Turnover'].iloc[1:],b['L1 Turnover'].iloc[1:])]:
    z=(x-y).to_numpy();n=len(z);rng=np.random.default_rng(20261101);idx=(rng.integers(0,n,(5000,int(np.ceil(n/3)),1))+np.arange(3)).reshape(5000,-1)[:,:n]%n;boot=z[idx].mean(axis=1);lo,hi=np.quantile(boot,[.025,.975]);rows.append(dict(Market=market,Cap=cap,Comparator=model,Metric=metric,N=n,MeanDifference=z.mean(),Lower=lo,Upper=hi,P=float((abs(boot-boot.mean())>=abs(z.mean())).mean()),Block=3,Draws=5000,Seed=20261101))
pd.DataFrame(rows).to_csv(OUT/'stage_b_decision_uncertainty.csv',index=False)
rows=[];existing=pd.read_csv(P/'phase2_statistical_comparisons.csv')
for _,r in existing.iterrows():
 def path(model,cap):return daily[(daily.Market==r.Market)&(daily.Model==model)&(daily['Target Weight Cap']==cap)].set_index('Date')['Net Return 10bps']
 a=path('Black-Litterman',r['Target Weight Cap']);b=path(r['Strategy B'],r['Target Weight Cap'] if r['Strategy B']=='Markowitz' else 1);assert a.index.equals(b.index)
 for block in [10,20,40]:
  if block==20:obs,lo,hi,p=r['Sharpe Difference A minus B'],r['95% CI Lower'],r['95% CI Upper'],r['Two-sided P-value']
  else:
   v=circular_block_bootstrap_sharpe_difference(a,b,block,2000,42);obs=v['observed_sharpe_difference'];lo,hi=v['percentile_ci_95'];p=v['p_value']
  rows.append(dict(Market=r.Market,Cap=r['Target Weight Cap'],Comparator=r['Strategy B'],Block=block,N=len(a),Draws=2000,Seed=42,Observed=obs,Lower=lo,Upper=hi,P=p,Reused=block==20))
pd.DataFrame(rows).to_csv(OUT/'stage_b_sharpe_blocks.csv',index=False)
crisis=pd.read_csv(G/'crisis_summary.csv');paths=[];checks=[]
for _,r in crisis.iterrows():
 prices=pd.read_csv(G/f'price_data/{r.Market.lower()}_adjusted_close.csv',index_col='Date',parse_dates=True);rets=prices.pct_change(fill_method=None).dropna();w=pd.Series(json.loads(r['Frozen Weights'])).reindex(rets.columns);start=pd.Timestamp(r['Requested Crisis Start']);end=pd.Timestamp(r['Requested Crisis End']);z=rets.loc[start:];wealth=(1+z).cumprod().mul(w,axis=1).sum(axis=1);ev=wealth.loc[:end];dd=ev/np.maximum.accumulate(np.r_[1,ev.to_numpy()])[1:]-1;trough=dd.idxmin();rec=wealth.loc[trough:];rec=rec[rec>=1];date=rec.index[0] if len(rec) else pd.NaT;duration=int(wealth.index.get_loc(date)-wealth.index.get_loc(trough)) if len(rec) else None
 assert np.isclose(dd.min(),r['Buy-Hold Max Drawdown'],atol=1e-12);assert str(trough.date())==r['Buy-Hold Trough Date'];assert str(date.date())==r['Buy-Hold Recovery Date'];assert duration==r['Buy-Hold Recovery Trading Days']
 paths.extend(dict(Crisis=r.Crisis,Model=r.Model,Date=str(d.date()),NAV=v) for d,v in wealth.items());checks.append(dict(Crisis=r.Crisis,Model=r.Model,MDD=dd.min(),Trough=str(trough.date()),Recovery=str(date.date()),Duration=duration,WeightDateEvidence='Frozen JSON archived in crisis summary; original pre-event optimizer history not retained'))
pd.DataFrame(paths).to_csv(OUT/'stage_b_crisis_paths.csv',index=False);pd.DataFrame(checks).to_csv(OUT/'stage_b_crisis_reconciliation.csv',index=False)
f=pd.read_csv(G/'factor_data/us_daily_2011-01-04_2024-12-31.csv',index_col='Date',parse_dates=True);old=pd.read_csv(G/'us/daily_oos_returns.csv',index_col=0,parse_dates=True);assert f.index.equals(old.index)
X=np.column_stack([np.ones(len(f)),f[['MKT','SMB','HML','MOM']].to_numpy()]);inv=np.linalg.inv(X.T@X);rows=[];stored=pd.read_csv(G/'factor_regression_us.csv')
for model,s in [('Black-Litterman',old.black_litterman_net),('Markowitz',old.markowitz_net),('Equal-weight',daily[(daily.Market=='US')&(daily.Model=='Equal-weight')].set_index('Date')['Net Return 10bps'])]:
 assert s.index.equals(f.index);y=(s-f.RF).to_numpy();beta=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@beta;score=X*e[:,None];S=score.T@score
 for lag in range(1,6):
  cross=score[lag:].T@score[:-lag];S+=(1-lag/6)*(cross+cross.T)
 se=np.sqrt(np.diag(inv@S@inv));t=beta/se;r2=1-e@e/((y-y.mean())@(y-y.mean()))
 if model!='Equal-weight':
  r=stored[stored.Model==model].iloc[0];assert np.isclose(r.R_squared,r2,atol=1e-12)
  for j,name in enumerate(['Alpha','MKT','SMB','HML','MOM']):assert np.isclose(beta[j],r['Alpha' if j==0 else name+'_beta'],atol=1e-12);assert np.isclose(t[j],r['Alpha_t_stat' if j==0 else name+'_t_stat'],rtol=1e-8)
 for j,name in enumerate(['Alpha','MKT','SMB','HML','MOM']):rows.append(dict(Model=model,Term=name,Coefficient=beta[j],HAC_SE=se[j],HAC_t=t[j],N=len(y),R2=r2,ResidualVariance=e@e/(len(y)-5),DesignConditionNumber=np.linalg.cond(X),FactorCorrelationCondition=np.linalg.cond(np.corrcoef(X[:,1:].T)),NewDiagnostic=model=='Equal-weight'))
pd.DataFrame(rows).to_csv(OUT/'stage_b_factor_audit.csv',index=False)
print('B checks passed; all six crisis summaries reconciled; independent OLS/HAC matched. Min block p',pd.read_csv(OUT/'stage_b_sharpe_blocks.csv').P.min())
