# Phase 4 manuscript validation

Status: **READY_FOR_AUTHOR_REVIEW**. This is a complete revised working paper, not an SSRN-approved revision. No SSRN submission, merge, numerical-model edit, historical-results edit or new market-data acquisition was performed.

## Coverage and evidence

- 36 pages; complete title/abstract, introduction, literature, questions, dataset, methodology, results, discussion, limitations, future work, reproducibility/version history, conclusion, declarations and bibliography.
- Eight logical tables, represented as 11 physical panels (Table 1A/B; Table 4A/B/C). All source rows represented: dataset 3; principal 9; constraints 12; cost 60; inference 12; crisis 6; factor 10; tau 5.
- Eight figures, sequentially numbered; exact source PNG bytes embedded in DOCX. Source 08 → manuscript 7; source 09 → manuscript 8. No crisis curve invented.
- Fifteen editable numbered native Office equations. Return, covariance, objective, prior/posterior, drift, fees, ASI, inference, crisis and factor conventions are explicitly defined.
- 833 provenance records, including empirical table cells, numerical prose, figures and source-configuration definitions. CSV row numbers include the header as row 1; source hashes and raw/display conversions are recorded.
- 800 actual saved DOCX table cells equal their expected generated values. Every traced displayed empirical value is present in the PDF. All 29 frozen Phase 3 files equal the base Git blob bytes; no empirical outputs were overwritten.
- 166 substantive prose/caption/reference paragraphs matched completely from DOCX into PDF after Unicode/whitespace normalization. All table values separately checked; all 8 image hashes match. PDF was exported directly from the final Word document. Native equation appearance and figure axes/labels require visual review in addition to text checks.

## Interpretation review

Passed: exact unequal OOS dates/US-listed USD instruments; equal-weight proxy and historically derived views; common annual units; chronological 252/63 framework; target ASI versus drift-adjusted L1 trades; initial deployment and single multiplicative fee deduction; matched 40% targets; periodic drifted 1/N; arithmetic means versus wealth and fee totals; approximate bootstrap/percentile/unadjusted inference; all intervals include zero and no p below .05; no exact-equivalence claim; separate gross crisis tests and start-NAV recovery; Phase 1 US-only factors/fixed tau; ex-post regimes versus training-only tau; withdrawn ownership evidence; qualified implementation contribution; distinct historical and revised reproduction claims.

The original PDF was found and all 36 pages inspected. Earlier Phase 3 PDF-unavailable status is historical and is not repeated as a present blocker. One prior audit allegation was corrected: original p.22 table and p.23 narrative both show BL momentum t = −0.856. No original opposite-sign contradiction is asserted. The original file hash still matches `38621c631b7645124dacbde12fd18892baee95830eb2d6ff91079d3d86785a07`.

## Citation audit

26 references; zero unresolved citations and zero uncited entries; no duplicate keys. Publisher/primary-author/registry metadata are linked in REFERENCE_VERIFICATION_AND_AUTHOR_REVIEW.md. Corrected Fernandes and Idzorek metadata; separate LW 2004a/b. Memmel original article/issue retrieval remains incomplete; optional final Meucci publisher chapter fields and the author's preferred Grinold/Kahn edition remain manual-review items. Metadata gaps are disclosed rather than invented.

## Formatting and conversion

Word-native DOCX → Microsoft Word ExportAsFixedFormat PDF. The packaged document-skill rasterizer uses that native PDF with bundled Poppler at 130 dpi, since bundled LibreOffice is unavailable on this Windows installation. Native MathML→OMML uses Microsoft's installed MML2OMML stylesheet. No equation images are substituted. Continuous page numbering, portrait prose and landscape wide exhibits, repeated table headers, non-splitting rows, deliberate decimal precision and proportional unchanged figures are used.

Visual QA: see the final completion note below; numerical extraction alone does not certify visual layout. Wide exhibits intentionally use separate landscape pages with whitespace so type remains readable. The script and source text/references, native export wrapper and rendering wrapper are retained under source/. Cross-system pagination may differ with Word/font versions; frozen PDF is the reviewed layout. The DOCX's substantive content is editable.

## Preservation and Git safety

Base `da5d40acfc0e71cac51f0fd8bc288606c6c7aa71` verified before authoring. Active new branch: `research/revised-paper-phase4-manuscript`. All five protected origin refs equal their recorded baselines in MANUSCRIPT_AUDIT.json; remote refs are checked again after publication. Changes are confined to Phase 4 outputs and their byte-preservation attribute. No force-push, amend or protected ref movement. Historical PDF, paper_results, Phase 1–3 evidence and financial-model code are unchanged. Final branch commit is reported in the delivery message; no self-referential commit hash is embedded in its own contents.

## Remaining research limitations

Small overlapping ETF baskets, USD proxy exposures and unequal dates; vendor adjustment/vintage and universe-selection limits; assumed proxy prior, historical tilt and uncertainty settings; stylized costs without execution/impact/capacity evidence; finite-sample approximate inference and unadjusted multiplicity; selected gross stress events and absent archived daily crisis curves; US-only factor fit; restricted fixed-tau range; missing original March vintages, capitalization, ownership and hypothesis-test artifacts. These limit interpretation and historical replication, while the narrower revised-study evidence remains traceable.

## Author approval before submission

1. Review and accept all revised methods, mixed results, interpretations, withdrawals and reference changes.
2. Confirm author contact/affiliation and revision date.
3. Confirm current funding and conflict-of-interest declarations; historical statements are not assumed current.
4. Approve the accurate AI-assistance/oversight declaration and actual human-review account, including front disclosure and applicable institutional/SSRN requirements.
5. Resolve or knowingly retain the explicitly qualified manual bibliography items; confirm scholarly sources actually consulted.
6. Confirm lawful access/distribution arrangements for frozen vendor inputs and the intended public availability wording.

No task blocker remains for creating this author-review package. These decisions remain outstanding for publication; author approval has not been fabricated. No claim of official SSRN approval or exact March numerical reproduction is made.

## Final visual QA completion

All 36 pages of the final PDF were rendered at 130 dpi and visually inspected, including every table/figure, caption, source note, equation, footer and reference page. No blank, clipped or unreadable exhibit remains. Table 1 panels share a landscape page; the Table 8 note stays with its table; wide plots preserve original image proportions. Final PDF SHA-256: `7eb078d2bf96edf95304e451d989575712ae6e4a946d1930566cff464f436aff`. The two manuscript formats contain the same substantive paper.
