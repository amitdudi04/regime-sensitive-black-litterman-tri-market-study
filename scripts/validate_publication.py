"""Validate committed publication evidence without downloading or refitting models."""
from pathlib import Path
import argparse,csv,hashlib,json,re
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
def validate(private=False):
 O=R/'outputs/final_professor_challenge_resolution';m=json.loads((O/'FINAL_CHECKSUMS.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 # The author-review PDF was deliberately removed from the public tree.
 # Its historical hash remains in the immutable manifest; do not weaken checks for other evidence.
 archived_not_distributed = {'FINAL_MANUSCRIPT.pdf'}
 for n,v in m['files'].items():
  p=O/n
  if n in archived_not_distributed and not p.exists():
   print('ARCHIVED_NOT_DISTRIBUTED:',n,'historical_sha256:',v['sha256'])
   continue
  assert p.exists(),f'Missing required public evidence: {n}'
  assert sha(p)==v['sha256'],n
 for n,v in m['source_scripts'].items():assert sha(R/n.replace('\\','/'))==v,n
 frozen=R/'results/phase3_final'
 fm=json.loads((frozen/'PHASE3_RUN_MANIFEST.json').read_text())
 for n,h in fm['outputs'].items():assert sha(frozen/n)==h,n
 for n,h in fm['source_sha256'].items():
  data=(R/n).read_bytes().replace(b'\r\n',b'\n')
  assert h in {hashlib.sha256(data).hexdigest(),hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()},n
 principal=pd.read_csv(R/'results/phase3_final/table_02_principal_performance.csv');assert len(principal)==9
 assert np.allclose(principal['Sharpe Ratio'],principal['Net Annualized Return']/principal['Annualized Volatility'])
 blocks=pd.read_csv(O/'stage_b_sharpe_blocks.csv');assert set(blocks.Block)=={10,20,40};assert (blocks.Lower<=0).all() and (blocks.Upper>=0).all();assert blocks.P.min()>=.05
 docs=[R/'README.md',*(R/'docs'/n for n in ['METHODOLOGY.md','RESULTS.md','REPRODUCIBILITY.md','RESEARCH_HISTORY.md']),R/'results/final/README.md',R/'results/historical/README.md']
 for p in docs:
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   if not link.startswith(('http:','https:','#','mailto:')):assert (p.parent/link.split('#')[0]).exists(),(p,link)
 if private:
  records=list(csv.DictReader((O/'stage_c_input_availability.csv').open()))
  for r in records:assert sha(R/r['Identifier'].replace('\\','/'))==r['SHA256']
  d=pd.read_csv(R/'results/generated/phase2/phase2_daily_returns.csv',parse_dates=['Date'])
  for _,r in principal.iterrows():
   s=d[(d.Market==r.Market)&(d.Model==r.Model)&(d['Target Weight Cap']==1)].sort_values('Date')['Net Return 10bps'];w=(1+s).cumprod();dd=w/np.maximum.accumulate(np.r_[1,w])[1:]-1
   assert np.isclose((1+s).prod(),r['Net Terminal Wealth']);assert np.isclose(dd.min(),r['Max Drawdown']);assert np.isclose(s.mean()*252,r['Net Annualized Return'])
 print(json.dumps({'public_evidence':'PASS','principal_rows':len(principal),'private_inputs_and_daily_accounting':'PASS' if private else 'NOT_REQUESTED','documentation_links':'PASS'}))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private-inputs',action='store_true');a=p.parse_args();validate(a.private_inputs)
