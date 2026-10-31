# Final publication readiness

**Status: READY_FOR_AUTHOR_APPROVAL.** Prepared 31 October 2026 for the existing SSRN paper 6479462. This means ready for an author decision, not cleared for upload without that decision. No SSRN action has been performed.

## Actual changes and preserved candidate

No manuscript correction was necessary on the verified evidence. The Phase 4 DOCX, PDF, 15 native equations, references, source and all prior evidence remain byte-identical to commit `74674ec8e6e9cfd33dbcd666ff5e7bdab813b626`. No new manuscript version or re-export was generated. Read the preserved files in `../phase4_manuscript/`; the ZIP carries unchanged reference copies under `phase4_manuscript/`, not a newly revised Phase 5 manuscript.

The manuscript remains 36 pages, eight logical tables in 11 physical panels, eight unchanged figures and 15 editable equations. This review checked display precision, metadata, qualified references, claims, declarations, provenance and packaging only. No research code, output, parameter, figure, regression, bootstrap or market-data vintage was changed or rerun.

## Final numerical and format checks

| Frozen table | Source rows covered |
|---|---:|
| Dataset | 3 |
| Principal performance | 9 |
| Matched concentration | 12 |
| Cost sensitivity | 60 |
| Statistical comparisons | 12 |
| Crisis summaries | 6 |
| US factor exposures | 10 |
| Fixed tau | 5 |

All source rows have traceable displayed cells. All 800 saved DOCX table cells match the build manifest; 811 source-cell records were independently checked for source value, declared rounding/unit conversion and presence in the PDF. All 833 provenance records still point to the recorded source hashes. All 166 substantive DOCX paragraphs match PDF text after Unicode/whitespace normalization and removal of page-footer fields. Eight embedded image hashes match frozen PNG sources. All twelve reported intervals include zero and no paired Sharpe p-value is below 0.05; no numerical inconsistency was identified.

All 36 PDF pages are present and nonblank with continuous numbering. The complete Phase 4 visual inspection is retained because its PDF hash matches exactly. Phase 5 additionally inspected cached final rendered pages 1, 8–10, 21, 25, 31 and 35–36: identity/abstract, native equations, a wide cost table, uncertainty figure, tau exhibit, declarations and references remain legible. Table headings, units and captions are unchanged from the validated layout. No redesign, equation edit, clipping correction or conversion was needed. A fresh renderer/export would add avoidable pagination risk to unchanged files.

## Metadata requiring author decisions

The manuscript title and author match [SSRN record 6479462](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6479462). The source PDF and revised candidate identify Amit Kumar Dudi, Independent Researcher, amitkumardudi04@gmail.com; first version March 2026, revised 31 October 2026. These are retained, not newly certified by the author.

The search-indexed official SSRN record lists **SRM INSTITUE OF SCIENCE AND TECHNOLOGY**, whereas the paper says **Independent Researcher**. The author must select the correct current affiliation and reconcile the record and manuscript if necessary; do not silently fix the institution's displayed spelling or infer an affiliation. SSRN's indexed record dates (written March 17, posted April 1, last revised April 3, 2026) describe the existing version, not an uploaded October revision. Direct SSRN retrieval returned HTTP 403; title/author/affiliation/date comparison therefore uses the official page's search-indexed extract, not a signed-in or live account verification. Current contact/profile data require author confirmation.

The candidate abstract/keywords accurately describe the revised evidence; the old online abstract describes historical claims and is not expected to match an unsubmitted revision. On approval, use the candidate abstract and keywords verbatim as the proposed updated metadata. Record identifier 6479462 and DOI 10.2139/ssrn.6479462 refer to the existing paper; they are not evidence of revision acceptance. The identifier is supplied in this package; no unnecessary identifier/footer edit was made to the PDF.

## Targeted bibliography resolutions

**Memmel (2003).** The author's [Deutsche Bundesbank publication list](https://www.bundesbank.de/en/christoph-memmel) directly confirms the title, year, Finance Letters volume 1 and pages 21–23. This strengthens the earlier indirect corroboration. Original journal-article full text, issue number and any journal DOI remain unverified. The [author's SSRN record](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=412588) is indexed as unavailable for download; it is not presented as the journal original. Retain the existing defensible volume/pages citation without inventing fields. The manuscript's UZH URL leads to the Ledoit–Wolf article that corroborates it, not Memmel's own article; that qualification remains explicit.

**Meucci (2010).** The [extended author PDF](https://cdn.interactiveadvisors.com/documents/third-party/ssrn-id1117574.pdf), title page, dates its version October 12, 2010 and explicitly identifies a shorter Wiley encyclopedia treatment. The [publisher record](https://doi.org/10.1002/9780470061602.eqf14009) identifies the shorter entry as *Black–Litterman Approach*, in *Encyclopedia of Quantitative Finance*, edited by Rama Cont, first published May 15, 2010. The existing citation expressly labels the October author version and links its SSRN record; that qualified citation is defensible and is preserved. Do not attach the shorter chapter's DOI/title to the longer author version as though they were identical objects. No publisher page range is invented. The author should confirm which version was consulted; a switch to the shorter publisher entry would require updating that reference in a later approved manuscript edit. Publisher metadata were visible in its indexed record; direct Wiley access was restricted.

**Grinold and Kahn.** [McGraw-Hill's second-edition listing](https://www.mheducation.com/highered/mhp/product/active-portfolio-management-quantitative-approach-producing-superior-returns-selecting-superior-returns-controlling-risk.html) explicitly distinguishes copyright 2000 from release on October 26, 1999. Thus 1999/2000 is explained by release versus copyright/cataloguing, not evidence of an unidentified third edition. The current 2000 second-edition citation is supported and retained. The author's copy/version actually consulted remains to be confirmed.

No broad bibliography re-audit was performed. The preserved 26-reference citation map still has no missing keys, uncited entries or duplicate keys. No bibliography change requiring new in-text citation edits was made. Reference-source summaries above are limited to metadata/version identification.

## Claims and reproducibility

The abstract, results, discussion and conclusion agree: BL has smaller target instability and turnover than unrestricted historical-mean MV in these baskets, behaves nearly like periodic 1/N, and has mixed risk-adjusted outcomes. Matched caps reduce MV concentration and turnover. No paired Sharpe difference is established as significant at 5%; nonsignificance does not prove equivalence. Crisis results are event-specific; US factors do not explain untested China/India momentum; the March numerical record is not exactly reproduced. No unsupported universal protection or incremental-alpha claim was found.

The paper identifies the Phase 3 freeze `da5d40acfc0e71cac51f0fd8bc288606c6c7aa71` and underlying Phase 1/2 source runs/commits. It identifies Yahoo Finance Adj Close inputs, checksum-matched local snapshots, common dates, vendor revision/redistribution limits and the difference between frozen-input reproduction and new downloads. Exact input hashes reside in `docs/phase1/dataset_manifest.csv` and run manifests; result hashes and file identities are in the Phase 3 manifest, Phase 4 traceability and this package's checksum file. The paper refers to these manifests rather than printing every hash in prose. No fresh snapshot availability or redistribution permission is asserted.

## Declarations and remaining limitations

AI assistance is disclosed on the front page and in the end declaration, including code/testing/workflow/table/figure/document support. Human review is explicitly still required. Funding and conflicts are reported as historical declarations requiring current confirmation. Exact approval wording and decisions are in AUTHOR_APPROVAL_CHECKLIST.md; no author approval is inferred from completion of Phase 5.

Retained research qualifications remain small overlapping USD ETF universes, unequal periods, assumed prior/views/uncertainty, stylized costs without impact/capacity estimates, approximate unadjusted bootstrap inference, selected standalone crises without archived daily curves, US-only factors, a limited fixed-tau grid, and missing original March vintages/capitalization/ownership/test artifacts. They qualify the study's scope rather than contradicting its frozen results.

## Git and package integrity

New branch: `research/revised-paper-phase5-submission-review`, created from `74674ec8e6e9cfd33dbcd666ff5e7bdab813b626`. Six protected remote branch baselines are recorded in FINAL_SUBMISSION_CHECKSUMS.json and checked before and after publishing the new branch. All Phase 3 and Phase 4 committed file bytes match the base; only four new Phase 5 preparation files are committed. No merge, force-push, amendment, historical overwrite or other-repository change is authorized or performed.

The checksum file records the unchanged manuscript source revision, empirical freeze, source/evidence hashes, candidate/supporting file hashes and check counts. It excludes its own hash and the enclosing ZIP hash to avoid circularity. The final Phase 5 branch SHA is supplied in the delivery message; the manuscript-source SHA remains the verified Phase 4 commit. A future author-approved edit must be re-exported and rechecked; this package does not preapprove that edit.

**Decision:** technically ready for author approval. Affiliation/contact/version, final interpretations, actual human oversight and AI wording, current funding/conflicts, consulted bibliography versions and lawful data-access wording remain author decisions. No submission has occurred and no additional research phase is started.
