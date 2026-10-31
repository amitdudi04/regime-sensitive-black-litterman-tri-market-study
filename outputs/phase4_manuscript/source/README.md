# Manuscript source

Run `build_manuscript.py` using Python with python-docx and lxml, pointing --repo at the frozen research repository if moved. This reads the eight Phase 3 CSV files and eight original PNG figures and creates DOCX, cell traceability and build manifest. It performs no numerical research experiment.

On the recorded Windows environment, run export_word_pdf.ps1 with absolute -Docx and -Pdf paths using Microsoft Word COM; this updates page fields and exports the matching PDF. The installed Microsoft MML2OMML.XSL supports native equations. Then run render_via_word_pdf.py DOCX PDF scratch-render-directory using the bundled document runtime. Its recorded paths identify this environment; update them when moving installations. All rendered page PNGs stay in work/ as QA intermediates, not delivered research outputs.

Run revision_review.py after final export to regenerate the revision log, reviewer checklist, reference audit and narrow manuscript checks. It checks the recorded original PDF path and hash and protected origin refs. Update only the path if relocating the same original bytes. It does not refit or download anything. Visual QA must also be completed; the final validation note records that separate step.

The build is reproducible in content, not guaranteed byte-identical across Word/font/library versions; PDF metadata and pagination can change. Read MANUSCRIPT_BUILD_MANIFEST.json and MANUSCRIPT_AUDIT.json for the frozen reviewed outputs and provenance.
