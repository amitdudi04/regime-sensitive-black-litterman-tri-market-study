from pathlib import Path
import json,csv,re
from docx import Document
from docx.shared import Pt,Inches
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
R=Path(__file__).resolve().parents[2];O=R/'outputs/final_professor_challenge_resolution';d=Document(R/'outputs/phase7_academic_finalization/Black_Litterman_Academic_Revision_Final.docx');edits=[];trace=[]
def replace(p,s):
 old=p.text;p.clear();p.add_run(s);edits.append(dict(old=old,new=s))
def add(anchor,s,heading=False):
 e=OxmlElement('w:p');anchor._p.addnext(e);p=Paragraph(e,anchor._parent);p.style=d.styles['Heading 2' if heading else 'Normal'];p.add_run(s);return p
for p in d.paragraphs:
 s=p.text
 if not s:continue
 new=s.replace('predefined 40%','fixed revised-study 40%').replace('same predefined 40%','same fixed revised-study 40%')
 new=new.replace('The 40% target cap is predefined, not searched for using realized performance.','The revised research introduced a fixed 40% target-cap robustness specification in Phase 2 before its recorded execution. It was not part of the March study or a preregistered design.')
 new=new.replace('verified daily crisis curves are not available in the archived evidence, so no crisis wealth figure is reconstructed.','daily crisis paths have now been reconstructed from archived frozen weight vectors and hash-matched prices, and all six summary rows reconcile. The original crisis target-selection timelines remain unavailable, so selection dates cannot be independently reverified.')
 new=new.replace('Daily frozen-holdings curves were not retained in the verified archive, so no crisis curve is inserted. The analysis therefore retains the verified summary evidence and explicitly acknowledges the missing daily paths.','The audit reconstructed daily frozen-holdings wealth paths from archived vectors and frozen prices. All six buy-and-hold summary rows reconcile. The archived target-selection timeline remains unavailable; the reconstruction is conditional on the recorded weight vectors.')
 new=new.replace('the retained summary archive does not contain verified daily frozen-holdings curves.','the original target-selection timelines are unavailable even though daily paths conditional on archived weights have been reconstructed.')
 new=new.replace('No new significance test of ASI or volatility is inferred from them.','New paired decision-level ASI and turnover uncertainty estimates are reported in the audit appendix; they do not reproduce the March study’s unavailable tests. No new volatility test is inferred.')
 new=new.replace('reported in the audit appendix','reported in Section 6.9 and the accompanying evidence tables')
 new=new.replace('no verified daily crisis curve is supplied.','reconstructed daily paths are supplied in the audit evidence package, conditional on archived frozen vectors.')
 new=new.replace('Inference uses one predefined block length, replication count, seed and approximate centering convention.','The primary Sharpe inference uses a fixed replication count and seed with approximate centering; the audit adds a limited block-length sensitivity and decision-level resampling.')
 new=new.replace('No backtest, bootstrap distribution or market-data download is repeated to prepare this manuscript.','The final audit adds narrowly specified resampling and diagnostic calculations from frozen evidence; no portfolio backtest or market-data download is repeated.')
 new=new.replace('Different observed histories generate unequal effective samples, preventing a common-horizon cross-market ranking.','Different observed histories generate unequal main samples; Section 6.9 adds a common-calendar robustness check without equalizing portfolio exposures.')
 new=new.replace('A common-period international design could distinguish horizon effects from differences in exposures.','A future international design could further separate exposure differences from currency and calendar effects.')
 if new!=s:replace(p,new)
for p in d.paragraphs:
 if p.text.startswith('The retained Phase 1 regressions'):
  replace(p,p.text.replace('They do not estimate exposures for Phase 2 capped or 1/N portfolios.','They do not estimate exposures for Phase 2 capped portfolios; a new same-sample 1/N comparison is supplied in the final audit.'))
# Insert compact evidence synthesis before discussion.
anchor=next(p for p in d.paragraphs if p.text.startswith('7 Discussion'))
prev=anchor._p.getprevious();p=Paragraph(prev,anchor._parent)
p=add(p,'6.9 Final identification and robustness audit',True)
p=add(p,'The final audit uses the frozen Phase 2 daily paths and decision records. No portfolio parameters were retuned. BL’s mean absolute ETF active weight relative to 1/N is 0.001828 in the US, 0.000426 in China and 0.000558 in India. Annualized tracking errors are approximately 0.0361%, 0.0215% and 0.0091%, respectively. These small differences support strong diversification anchoring, without establishing incremental Bayesian investment value.')
p=add(p,'With P equal to the identity, the posterior adjustment is tau Sigma (tau Sigma + Omega) inverse times 0.10(mu_hist − Pi). Omega equals ten times the diagonal annual covariance and is independent of tau. Marginal view-to-prior variance ratios are 200 or 1,000 under the adaptive rule. These ratios describe diagonal variances, not the eigenvalues of the correlated update. Small adjustments explain the weak fixed-tau sensitivity and near-equal-weight allocations.')
p=add(p,'Paired uncertainty for target ASI and actual turnover uses consecutive rebalance decisions, excluding initial deployment, rather than daily observations. Circular blocks of three decisions, 5,000 draws and seed 20261101 yield percentile 95% intervals and approximate mean-centered p-values. Only 40–55 paired differences are available per market. The supplementary CSV reports all strategy/cap comparisons; p-values are unadjusted, and cap-inactive duplicates provide no independent evidence. All BL-minus-Markowitz ASI and turnover intervals lie below zero under both caps; these exploratory intervals remain subject to those limitations.')
p=add(p,'Sharpe sensitivity uses the original paired bootstrap with 10-, 20- and 40-session blocks, 2,000 draws and seed 42. Existing 20-session evidence is reused. All intervals include zero; the smallest approximate p-value is 0.102. This supports the limited-significance conclusion under the tested block choices, without establishing equivalence.')
p=add(p,'All six crisis buy-and-hold paths reconcile from frozen prices and archived weight vectors. Independent least-squares and lag-5 Bartlett HAC calculations reproduce the US factor estimates, including BL’s high R-squared and market t-statistic. Residual variance is positive. A new same-sample 1/N regression provides a supplementary anchoring comparison; factor conclusions remain US-specific. Missing original crisis selection timelines prevent independent verification of the archived vectors’ selection dates.')
p=add(p,'A common-calendar robustness check intersects stored net returns from 7 November 2014 through 31 December 2024, covering 2,553 sessions. Existing strategies and training schedules remain intact. Wealth is rebased at the slice boundary without a new initial trade. The following results are annualized arithmetic returns, sample volatilities, zero-RF Sharpe ratios and maximum drawdowns; USD ETF exposure differences remain material.')
common=list(csv.DictReader((O/'stage_c_common_period.csv').open()))
for r in common:
 if float(r['Cap'])!=1:continue
 text=f"{r['Market']}, {r['Model']}: return {float(r['AnnualReturn'])*100:.4f}%, volatility {float(r['Volatility'])*100:.4f}%, Sharpe {float(r['Sharpe']):.6f}, maximum drawdown {float(r['MaxDrawdown'])*100:.4f}%."
 p=add(p,text)
 for col in ['AnnualReturn','Volatility','Sharpe','MaxDrawdown']:trace.append(dict(manuscript_text=text,source='stage_c_common_period.csv',market=r['Market'],model=r['Model'],cap=r['Cap'],column=col,value=r[col]))
p=add(p,'A fully invested rebalance has L1 turnover equal to twice one-way turnover. Matching the existing 10-bps-per-L1 fee requires 20 bps per half-L1. Initial deployment is purchased weight one and is charged separately. Direct fees sum pretrade net NAV times the fee fraction; terminal-wealth impact also includes foregone growth. Four private input snapshots match archived hashes; redistribution permission remains unestablished. Later provider vintages can test the specification but cannot establish exact frozen-run or March-version reproduction.')
# Economical typography without reducing research table fonts.
for i,p in enumerate(d.paragraphs):
 f=p.paragraph_format
 if p._p.xpath('.//m:oMath') or p._p.xpath('.//w:drawing'):continue
 if p.style.name=='Normal' and p.text and not p.text.startswith(('Source:','BL =')):
  f.line_spacing=Pt(18);f.space_after=Pt(5)
 if i in range(1,6):
  f.line_spacing=1;f.space_after=Pt(4)
  for r in p.runs:r.font.size=Pt(12)
 if p.text.startswith(('Figure ','Table ')):f.keep_with_next=True
 for r in p.runs:
  r.font.name='Times New Roman'
# Remove forced body-start page break after front matter.
for p in d.paragraphs:
 for br in p._p.xpath('.//w:br[@w:type="page"]'):br.getparent().remove(br)
for i,s in enumerate(d.sections):
 if i and s.page_width==d.sections[i-1].page_width:s.start_type=WD_SECTION_START.CONTINUOUS
# Default font on newly added body paragraphs is inherited 12 pt TNR.
d.save(O/'FINAL_MANUSCRIPT.docx')
(O/'MANUSCRIPT_EDITS.json').write_text(json.dumps(edits,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'FINAL_TRACEABILITY.csv').open('w',newline='',encoding='utf-8') as f:
 fields=['manuscript_text','source','market','model','cap','column','value'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(trace)
print('Draft saved; added common-period statements',len(trace))
