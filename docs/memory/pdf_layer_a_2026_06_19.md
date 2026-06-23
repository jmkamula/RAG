---
name: pdf-layer-a-2026-06-19
description: "SHIPPED 2026-06-19 (9150a0b): PDF reader Layer A — pdfplumber markdown + tables, mirroring the docx mammoth pattern. Closes the 0% PDF bind rate by capturing structured table content (audit reports, control matrices) the prior paragraph-only extraction dropped. Smoke test on Arion's worst PDF (214427 Client Report 27001, Czech audit report): 15,558 → 43,074 chars (2.8×), 48 tables now visible to LLM. No new deps, no schema migration."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

PDF was the weakest link on the intake quality dashboard (0% bound
rate vs ~14% docx, 92% workbook). Root cause: `_read_pdf` used
`page.extract_text()` (paragraph-only) with no markdown fallback,
unlike `_read_docx` which has mammoth markdown + table-heavy rescue.

## What landed (rag/intake/readers.py)

- `_read_pdf` rebuilt to produce a per-page markdown rendering:
  text + tables via `pdfplumber.extract_tables()` formatted as
  GitHub markdown
- New `_pdf_table_to_markdown(table)` helper:
  - Pipe-injection safe (cells with `|` get replaced with `/`)
  - Handles None / merged cells (padded with single space)
  - Single-row tables collapse to "header · value" prose
- Reuses `_chunk_markdown_to_sections` for table-heavy rescue
- Reuses `_synthesise_table_prose` for grounding-quote sentences
- Sets `ParsedDocument.markdown`, `source_sha256`, `converter` (matches docx)

## Why pdfplumber, not Marker/Vision/PyMuPDF

Documented in MVP step 1 trade-off (docs/road_to_mvp.md):
- Zero new deps (pdfplumber already in use)
- Zero new infra
- Architectural symmetry with docx → mammoth
- Quality ceiling ~70-80% of Marker/Vision but closes most of the gap

Upgrade triggers documented in the strategy doc:
- Scanned PDFs returning empty → OCR layer
- Multi-column or complex layouts → Vision direct or Marker
- SOC 2 audit report onboarding → Vision (per-PDF budget acceptable)

## Smoke test

Arion's worst PDF — 214427_Client Report 27001 (Czech ISO 27001
audit report, table-dominated, the 0%-bound-rate offender):

```
Before: 15,558 chars extract_text(), 0 tables visible
After:  43,074 chars markdown (2.8×), 48 tables formatted
```

## Eval impact

198/199 (#5 LLM-stochastic). No regression from the reader path —
the eval suite doesn't exercise upload extraction directly, only
chat queries. The lift will materialise when PDFs are re-extracted
(via the re-extract endpoint shipped 2026-06-23, commit 3fde996).

## Related

- [[intake-pipeline-architecture]] — the architecture diagram needs
  a refresh row noting PDF now matches docx in markdown coverage
- [[reextract-endpoint-2026-06-23]] — the operational path to leverage
  Layer A on existing PDF uploads
- [[per-must-binding-in-extractor-2026-06-15]] — the per-MUST binding
  that Layer A's markdown + tables now feeds
- docs/road_to_mvp.md — MVP step 1 (PDF Layer A is the first MVP item)
