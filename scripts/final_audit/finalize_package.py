import json,csv,re,hashlib,subprocess,zipfile,unicodedata
from pathlib import Path
from docx import Document
from lxml import etree
from pypdf import PdfReader
R=Path.cwd()/'work/repository';O=R/'outputs/final_professor_challenge_resolution';base='f9015d2430f0b910ece5ad8963c9f41c1464b604'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();git=lambda *a:subprocess.check_output(['git',*a],cwd=R,text=True).strip()
a=Document(R/'outputs/phase7_academic_finalization/Black_Litterman_Academic_Revision_Final.docx');b=Document(O/'FINAL_MANUSCRIPT.docx');pdf=PdfReader(O/'FINAL_MANUSCRIPT.pdf');ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
canon=lambda e:etree.tostring(e,method='c14n',exclusive=True)
assert len(b.tables)==11 and all([[c.text for c in r.cells] for r in x.rows]==[[c.text for c in r.cells] for r in y.rows] for x,y in zip(a.tables,b.tables))
ma=a.element.findall('.//m:oMath',ns);mb=b.element.findall('.//m:oMath',ns);assert len(ma)==len(mb)==15 and all(canon(x)==canon(y) for x,y in zip(ma,mb))
def media(p):
 with zipfile.ZipFile(p) as z:return sorted(sha_bytes(z.read(n)) for n in z.namelist() if n.startswith('word/media/'))
sha_bytes=lambda x:hashlib.sha256(x).hexdigest()
assert media(O/'FINAL_MANUSCRIPT.docx')==media(R/'outputs/phase7_academic_finalization/Black_Litterman_Academic_Revision_Final.docx')
assert [p.text for p in a.paragraphs[-26:]]==[p.text for p in b.paragraphs[-26:]]
def norm(s):return ''.join(x.lower() for x in unicodedata.normalize('NFKC',s).replace('\u00ad','') if x.isalnum())
pt=''
for i,p in enumerate(pdf.pages,1):
 lines=p.extract_text().splitlines()
 if lines[0].strip()==str(i):lines=lines[1:]
 elif lines[-1].strip()==str(i):lines=lines[:-1]
 else:raise AssertionError(i)
 assert len(''.join(lines))>100;pt+='\n'+'\n'.join(lines)
for p in b.paragraphs:
 if p.text and not p._p.findall('.//m:oMath',ns):assert norm(p.text) in norm(pt),p.text[:80]
assert not pdf.is_encrypted
fonts={}
def fontcheck(f):
 f=f.get_object()
 if '/DescendantFonts' in f:
  for x in f['/DescendantFonts']:fontcheck(x)
 else:
  fd=f.get('/FontDescriptor');fd=fd.get_object() if fd else {};fonts[str(f.get('/BaseFont'))]=any(k in fd for k in ['/FontFile','/FontFile2','/FontFile3'])
for p in pdf.pages:
 for f in p['/Resources'].get('/Font',{}).get_object().values():fontcheck(f)
assert all(fonts.values())
manifest=json.loads((R/'outputs/phase4_manuscript/MANUSCRIPT_BUILD_MANIFEST.json').read_text())
for t,r,c,v in manifest['expected_table_cells']:assert b.tables[t].rows[r].cells[c].text==v
old=list(csv.DictReader((R/'outputs/phase4_manuscript/MANUSCRIPT_RESULT_TRACEABILITY.csv').open(encoding='utf-8')))
for r in old:assert sha(R/r['source_path'])==r['source_sha256']
new=list(csv.DictReader((O/'FINAL_TRACEABILITY.csv').open(encoding='utf-8')))
# Keep the exact inherited traceability schema along with new source rows.
rows=old+new
for name in ['stage_a_diagnostics.csv','stage_b_sharpe_blocks.csv','stage_b_decision_uncertainty.csv','stage_b_factor_audit.csv']:
 data=list(csv.DictReader((O/name).open(encoding='utf-8')))
 for i,r in enumerate(data,2):rows.append({'kind':'audit_diagnostic_row','source_path':'outputs/final_professor_challenge_resolution/'+name,'source_sha256':sha(O/name),'source_row_1based':str(i),'source_value':json.dumps(r,sort_keys=True),'manuscript_text':'Section 6.9; see diagnostic table for full precision'})
fields=list(dict.fromkeys(k for r in rows for k in r))
with (O/'FINAL_TRACEABILITY.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
issues=[('A1','Why does BL nearly equal 1/N?','stage_a_diagnostics.csv; stage_a_posterior_diagnostics.csv','Regenerated missing posterior diagnostics only; active-weight and path comparisons','No changed historical result','6.9, prior discussion','No incremental Bayesian value identified','RESOLVED_WITH_LIMITATIONS'),('A2','Are Markowitz comparisons matched and how does the cap affect results?','stage_a_cap_effects.csv; Phase 2 source/manifest','Reused stored concentration and performance values','Historical levels unchanged','6.3, discussion','No causal isolation of stabilization','RESOLVED_WITH_LIMITATIONS'),('A3','When was the 40% cap specified?','af84ddfbc93edc7a5143c654d6319d67e3139eef; Phase 2 manifest','Inspected introduction and clean execution source','No numerical change','5.7 and 6.3','No preregistration record','RESOLVED'),('B1','What uncertainty surrounds ASI and turnover?','stage_b_decision_uncertainty.csv','New paired decision-block inference under advance specification','New intervals/p-values; 40–55 differences','6.2 and 6.9','Few dependent decisions; unadjusted approximate inference','RESOLVED_WITH_LIMITATIONS'),('B2','Are Sharpe conclusions block-sensitive?','stage_b_sharpe_blocks.csv','New 10/40 blocks; reused 20','No significant differences; minimum p=.102','6.9','Approximate inference; no equivalence claim','RESOLVED_WITH_LIMITATIONS'),('B3','Can crisis paths and recovery be reconstructed?','stage_b_crisis_paths.csv; stage_b_crisis_reconciliation.csv','Reconstructed conditional paths, reconciled six summaries','All six unchanged within 1e-12','5.10,6.6,6.9,limitations','Original selection timeline missing; selection dates unverified','UNRESOLVED_SOURCE_EVIDENCE'),('B4','Are US factor estimates and extreme fit correct?','stage_b_factor_audit.csv; archived Phase 1 returns/factors','Independent OLS/HAC; same-sample new 1/N diagnostic','Coefficients/R2/t match; new 1/N fit','5.11,6.9','Processed factor source; no raw percent response; US-only','RESOLVED_WITH_LIMITATIONS'),('B5','Why weak tau sensitivity?','docs/phase1/tau_sensitivity.csv; model source','Retained fixed values; inspected update algebra','No rerun or altered fixed values','6.8,6.9','Only five fixed values; no general robustness inference','RESOLVED_WITH_LIMITATIONS'),('C1','Does common-calendar evaluation alter comparison?','stage_c_common_period.csv','Sliced stored paths on common dates','New conditional 2,553-session metrics','6.9,limitations','Not reinitialized strategies; unequal exposures','RESOLVED_WITH_LIMITATIONS'),('C2','Do ETF labels imply domestic-market or currency causality?','Phase 7 data and limitations; dataset manifest','Retained and clarified USD ETF interpretation','None','data,6.9,limitations','Country effects not identified','RESOLVED_WITH_LIMITATIONS'),('C3','How do L1/half-L1 and fees reconcile?','stage_c.py analytical assertions; Stage C report','Checked solvable .6/.4 to .5/.5 rebalance','T=.2; 10 bps/L1 fee=.0002','6.9','Weight-cost convention not dollar-funding solver','RESOLVED'),('C4','Are frozen inputs available and reproducible?','stage_c_input_availability.csv','Verified four archived hashes; no datasets redistributed','All four match','6.9,reproducibility','Permission unestablished; later vintage may differ','RESOLVED_WITH_LIMITATIONS'),('D1-D6','Does the manuscript reflect frozen evidence and render correctly?','FINAL_MANUSCRIPT; FINAL_TRACEABILITY.csv','Updated affected prose after A/B/C commits; render and integrity checks','Added diagnostics only; historic tables unchanged','Affected methods/results,6.9,limitations','Author declarations pending','RESOLVED_WITH_LIMITATIONS'),('AUTHOR','Are human and AI-policy approvals complete?','Retained declarations','Preserved explicit pending statements','None','front matter,declarations','Personal attestations and policy review unconfirmed','AUTHOR_APPROVAL_PENDING')]
reg='# Professor challenge resolution register\n\nBase f9015d2430f0b910ece5ad8963c9f41c1464b604. A frozen in e9cdefd; B in 6716205; C in 5480fdc. The initial inventory is preserved in Stage A commit e9cdefd. Final statuses below distinguish resolution from qualification and missing evidence. Existing Phase 2 run ff8cacdc-95f8-458e-8d71-d12efbd9a9f9 and Phase 1 run 693ec4b2-0e95-4367-afef-904dbac8f9c3 supply the source histories.\n\n|ID|Professor challenge|Evidence|Actual action / new check|Numerical impact|Manuscript impact|Residual limitation|Status|\n|---|---|---|---|---|---|---|---|\n'+'\n'.join('|'+ '|'.join(r)+'|' for r in issues)
(O/'PROFESSOR_CHALLENGE_RESOLUTION_REGISTER.md').write_text(reg,encoding='utf-8')
(O/'FINAL_RESEARCH_FINDINGS.md').write_text('''# Authoritative final research findings

Status: RESEARCH_READY_WITH_LIMITATIONS. Author and SSRN/AI-policy clearance remain pending.

1. BL remains extremely close to rebalanced 1/N because of the equal-weight reverse-optimized prior, mild historically generated views and large Omega. Mean absolute active ETF weights are .001828 US, .000426 China and .000558 India; marginal Omega/prior ratios are 200–1,000. No incremental Bayesian alpha is established.
2. Matched 40% target constraints reduce Markowitz concentration and turnover. The specification was introduced in Phase 2 before its recorded execution, without evidence of preregistration. Historical values are unchanged.
3. New exploratory paired decision-block ASI/turnover intervals are negative for BL-minus-Markowitz under both caps. Small decision samples and serial dependence limit inference; unadjusted Monte Carlo p=0 means zero exceedances in finite draws, not a true probability of zero. BL has nonzero ASI versus constant targets, and comparison with 1/N does not establish general turnover superiority.
4. All Sharpe intervals include zero at daily block lengths 10,20,40; minimum approximate p=.102. Failure to reject is not equivalence.
5. Six conditional crisis paths reconcile existing investment summaries. The original archived weight vectors exist, but missing crisis target-selection timelines prevent full independent reproduction of pre-event selection. US crisis evidence remains unfavorable to BL; no missing vectors invented.
6. Independent US OLS/Bartlett HAC calculations reproduce archived coefficients, t-statistics and R2. BL's high fit and market t-value are reproduced, with positive residual variance; same-sample 1/N is a new supplementary diagnostic. No China/India factor conclusions follow.
7. Five fixed-tau values remain unchanged; tau does not cancel because Omega is independent of tau. Large uncertainty and the mild view tilt predict weak sensitivity.
8. Common-calendar results cover 2014-11-07–2024-12-31, 2,553 sessions, net 10 bps per L1. These are slices of existing strategies, not new training/deployment experiments. Full market/model results including both caps are in stage_c_common_period.csv.
9. L1 rebalance turnover is twice half-L1, so the same fee requires twice the coefficient under half-L1. Initial deployment remains purchased weight one. Direct fees differ from terminal-wealth impact.
10. All four private input snapshots match archived hashes. Raw inputs are excluded because redistribution authorization is unestablished. Revised specification, exact frozen-run reproduction and March-paper reproduction are distinct claims.

No historical table or figure value was corrected in this audit; new diagnostics are explicitly supplementary. No full backtests or new market-price downloads were run. The manuscript preserves eight logical tables, eight figure assets and 15 editable equations. Remaining limitations are documented in the issue register, not labeled fully resolved.
''',encoding='utf-8')
(O/'FINAL_VALIDATION.md').write_text(f'''# Final validation

RESEARCH_READY_WITH_LIMITATIONS. A, B, C were committed in sequence before manuscript authoring. No main merge, reset, force-push or SSRN upload. No new market downloads or complete portfolio backtests. All previous tracked files except the additive .gitattributes rule remain unchanged.

Checks executed: Phase 2 output/source hashes; three frozen prices; independent posterior solve; paired decision-date assertions and predetermined block resampling; 10/40 daily bootstrap sensitivity with 20 reused; independent cumulative-growth crisis reconstruction and six row matches to 1e-12; numpy OLS/HAC replication; common-date complete paths; four input hashes; analytical L1 and fee checks. No broad 89-test suite rerun.

DOCX/PDF: {len(pdf.pages)} pages; every nonempty non-equation body paragraph found in PDF after Unicode/whitespace normalization. All 800 recorded table cells identical, all 11 table panels preserved, all 8 media files identical, 15 editable OMML equations canonical-identical, 26 reference texts identical. PDF is unencrypted, selectable and all used fonts embedded: {fonts}.

Layout: retained US Letter/TNR/one-inch margins; body baseline reduced to readable 18 pt, author details 12 pt single spacing; abstract now fits page 1; unnecessary front-matter forced break removed; compatible consecutive section boundaries allow continuous flow. Table fonts were not reduced. All pages rendered; visual review included equations, exhibits, new audit prose and reference ending. Landscape transitions retain some whitespace to preserve readable wide exhibits. Final changes re-rendered and checked separately. No blank pages or observed clipping/overlap.

Numerical traceability: inherited 833 records plus newly linked common-period and audit rows; exact CSV hashes and row identifiers retained. Missing crisis selection timeline and raw factor percent response are explicitly qualified. Personal declarations and AI-policy clearance remain pending; no Paperpal report or SSRN approval is claimed.
''',encoding='utf-8')
(O/'FINAL_CHECKSUMS.json').write_text(json.dumps({'status':'RESEARCH_READY_WITH_LIMITATIONS','base_commit':base,'stage_a_commit':'e9cdefd','stage_b_commit':'6716205','stage_c_commit':'5480fdc','self_excluded':True,'files':{p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in O.iterdir() if p.name!='FINAL_CHECKSUMS.json'},'source_scripts':{str(p.relative_to(R)):sha(p) for p in (R/'scripts/final_audit').glob('*.py')},'protected_heads':json.loads((O/'GIT_BASELINES.json').read_text())['protected_remote_heads']},indent=2),encoding='utf-8')
print('Document validation passed',len(pdf.pages),'pages; trace rows',len(rows))
