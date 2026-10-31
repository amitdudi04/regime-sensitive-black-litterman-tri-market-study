# Original versus revised format audit

Prepared 1 November 2026. **POLICY_REVIEW_REQUIRED — author-review candidate, NOT APPROVED FOR SSRN UPLOAD.**

## Authority and inspection

The user-supplied `C:\Users\amitk\Downloads\ssrn-6479462 (7).pdf` is the authoritative March 2026 formatting reference. It was actually read, measured with PDF text/font coordinates, rendered, and visually inspected across all 36 pages. Its SHA-256 is `38621c631b7645124dacbde12fd18892baee95830eb2d6ff91079d3d86785a07`. The input was not edited. The filename differs from the anticipated `(7)(3)` name in the prompt; the subsequently supplied file is the reference used.

The complete Phase 6 manuscript at `8acbd1218adafe974415557a9338300268e973c7` was the editorial source. The original's visual conventions were used without restoring its superseded calculations, claims, ownership analysis or abstract. No research experiment was rerun.

## Measured specification and implementation

| Element | Original PDF observation | Final implementation / reason for difference |
|---|---|---|
| Page geometry | All 36 pages: 612 × 792 pt, US Letter, portrait | US Letter; portrait prose, retained landscape wide exhibits |
| Margins | Typical body left x=72.024 pt; right edge approximately 540 pt; visible upper glyphs around 74 pt and body bottom near 718 pt | 72 pt (1 inch) on all sides; portrait text width 468 pt and landscape width 648 pt. PDF coordinates support this inference but do not reveal original Word settings directly |
| Body | Predominantly Times New Roman, 12 pt | Times New Roman, 12 pt, black |
| Title / Abstract heading | 15.96 pt bold; left aligned | 16 pt bold; title wraps naturally over two lines |
| Author and date | 14.04 pt regular | 14 pt; proposed affiliation and unapproved-candidate labels retained |
| Main headings | 14.04 pt bold | 14 pt bold, genuine Word heading styles |
| Subheadings | 12 pt bold | 12 pt bold, numbered hierarchy retained |
| Body line spacing | Typical measured baseline steps 20.64–20.78 pt | Exact 20.7 pt body baseline spacing |
| Paragraphs | Justified; no first-line indent; approximately 6 pt extra paragraph gap | Justified, no first-line indent, 6 pt after; 12 pt before headings; widow/orphan control |
| Mathematics | Cambria Math with fractions, subscripts and superscripts | All 15 existing editable OMML equations preserved; centered equations with right-aligned numbers; Cambria Math |
| Tables | Thin black full grids, white cells, bold headers; original wide tables have cramped wrapping | White cells and thin black 0.5 pt grids restored; source cell font sizes retained for legibility, fitted column widths and padding; landscape where needed; repeated headers and rows prevented from splitting |
| Captions and notes | Original figure captions include 9 pt bold blue text; some mixed-font spans | Consistent black 12 pt bold captions and 10 pt notes improve readability. Genuine Caption style. Figure-internal lettering remains in the unchanged verified PNG assets |
| Figures | In-text placement; variable widths | Eight unchanged images, centered and proportionally sized; caption and source note accompany each figure |
| Header/footer | No visible running header or page number in original | No running header; centered Arabic footer numbering retained to navigate the longer verified revision |
| References | Numbered bibliography with hanging indentation | Existing 26 alphabetical author-year references retained, with 0.25-inch hanging indent. No bibliographic content or citation system changed solely for cosmetic imitation |
| Pagination | Original 36 pages; Phase 6 37 pages | Final 46 pages. Original-style spacing, corrected content, readable wide exhibits and declarations determine pagination; no forced target page count |

The original JEL line was not reinstated. The revised abstract and keywords remain those of the verified revision. The current revision date is 1 November 2026; dated historical validation statements remain dated 31 October 2026. Author approval is not inferred from formatting.

## Render review and corrections

The final PDF was exported using Microsoft Word and rendered through the document render wrapper with Poppler at 130 dpi. All final page content was visually inspected. Review caught and corrected (1) clipped inline figures caused by exact body line spacing inherited by image paragraphs, (2) prose beginning with “Table” or “Figure” incorrectly styled as captions, (3) cell-level borders overriding the intended consistent table grid, and (4) Figure 6's source note overflowing onto a separate page. Figure 6 was reduced proportionally to 4.8 inches high; its labels remain readable and its note now fits on page 31.

After the last adjustment all 46 pages were rendered again. Pixel comparison excluding footer numbers confirmed that page 31 was the only changed body image relative to the fully inspected 47-page draft; the obsolete note-only page was removed. That changed page was visually reinspected, and sequential footer numbers were checked by extraction. This records the actual review method rather than implying a separate human certification.

Final page coverage: 1–2 front matter; 3–8 motivation, literature, questions and data; 9 Table 1; 10–16 methods and all 15 equations; 17–31 primary tables/figures and uncertainty; 32–37 crisis, factor and tau diagnostics; 38–42 discussion, limitations, reproducibility, conclusion and declarations; 43–46 remaining declarations and bibliography. No blank or corrupted pages, clipped equations or columns, split table rows, orphaned headings, overlapping content or missing figure panels were observed. Landscape section transitions and front matter leave intentional white space. The final bibliography ends on a short final page; no content was compressed to eliminate it.

The embedded Calibri-Bold font resource is used only for extracted whitespace in heading structures; visible manuscript text is Times New Roman or Cambria Math. The source figures retain their own rasterized plotting fonts. No font files are distributed.

## Preservation and provenance

All 8 logical tables (11 physical panels), 800 recorded table cells, 8 image byte hashes, 15 canonical editable equation XML structures and 26 reference texts match the verified source. All 833 traceability source hashes and 811 source-cell records passed; displayed values are present in the PDF. All 215 nonempty, non-equation body paragraphs, including captions, notes and references, were found in PDF text after whitespace/Unicode normalization. Equation XML identity and rendered inspection supplement the text comparison.

The 58 tracked historical evidence and manuscript files checked against the Phase 6 base remain byte-identical. All eight protected remote branch heads match their recorded baselines in FINAL_DOCUMENT_CHECKSUMS.json. Changes are confined to the new Phase 7 output package and a `.gitattributes` entry preserving its bytes on checkout. No SSRN operation was performed.
