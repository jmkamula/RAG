---
name: table-heavy-docx-rescue
description: "SHIPPED 2026-06-09 (eba649c): docx reader rebuilds sections from mammoth markdown when paragraph-walk captures dramatically less content. Section narrowing now non-subtractive below 25-control threshold."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

python-docx's `doc.paragraphs` walk captures narrative paragraphs
but NOT the content of tables. For procedure docs heavy on tables
(risk matrix, treatment table, RACI, asset register), this means
the operative content is invisible to the section-based extractor —
which iterates `raw_sections` built from paragraphs.

Mammoth's `convert_to_markdown` captures everything: tables emit as
cell text, lists become bullets, headings come through. The full
markdown lives on `doc.markdown`.

The bug: the docx reader populated both `raw_sections` (from
paragraph walk) AND `doc.markdown`. `_extract_full` (small docs)
correctly used `doc.markdown if doc.markdown else doc.full_text`.
But `_extract_sections` (large docs) used only `raw_sections`,
silently losing 90%+ of content for table-heavy docs.

## What ships

**Rescue in the docx reader** (`rag/intake/readers.py:_read_docx`):
when `md_chars > max(2000, paragraph_chars * 3)`, rebuild
`raw_sections` from markdown chunks via
`_chunk_markdown_to_sections(target_chars=20000)` (~5K tokens per
chunk). Splits on `\n\n` first, then `\n`, then hard byte cuts for
tables emitted as one long line (mammoth often emits docx tables as
single un-broken blocks).

**Non-subtractive section narrowing** (`extractor.py:_scope_controls_to_section`):
gates the subtractive narrowing behind `_SECTION_NARROW_THRESHOLD=25`.
When doc_mappings has already narrowed to ~6-15 controls, the
per-section heading-keyword and explicit-ref narrowing only discards
legitimate candidates. Pre-doc_mappings flows (large `controls`
lists from `_scope_controls`) still get narrowed.

## Trigger case (2026-06-09)

`Risk-Integrated Risk Assessment and Treatment -Procedure.docx`:
107K tokens, 8 sections by paragraph walk. Pre-fix: paragraph_chars
= 9523, only 1 LLM call fired (one section had explicit ref "8.2";
others were skipped by the narrower), 1 finding extracted.

Post-fix: paragraph_chars 9523 → md_chars 427959 triggers rescue,
22 chunks built, 22 LLM calls (~2.7 min), 4 findings extracted
(6.1.2/6.1.3/8.2/8.3 all Comply) + 2 xfw proposals (Art.32.2,
Art.35). 4× yield from one pipeline fix.

## Cost / trade-offs

- 22 LLM calls × 2-5s = 1-2 min per large doc. Acceptable for
  substantive extraction; cost ~$0.03 per upload at haiku rates.
- Some chunks contain binary/base64 blobs (mammoth emits embedded
  image data inline). The LLM correctly refuses these → dropped via
  JSON-parse errors + hallucination filter. No false positives.
- Markdown chunks carry no `heading` field (mammoth doesn't emit `#`
  reliably for docx-style headings). The LLM gets raw content and
  the document-level context block; section-level structural hints
  are lost. Acceptable trade-off.

## When to revisit

- If a future doc format produces similar paragraph-vs-content
  gap (PDF tables come to mind), apply the same pattern.
- The 25-control narrowing threshold is a heuristic. If
  doc_mappings starts returning larger scopes (50+ controls per
  doc), consider re-enabling narrowing with a different signal.
- Markdown rescue is currently docx-only. PDF / odt / rtf would
  benefit from the same approach if/when those readers ship.

## Related

- [[doc-curation-engine-v1]] — the doc_mappings layer this defers to.
- [[doc-discovery-vocabulary-gap-fix]] — earlier same-pipeline fix.
- [[extractor-section-fallback]] — earlier same-narrowing-pattern fix.
- [[intake-quality-telemetry]] — surface for catching the next
  under-extraction without manual code review.
