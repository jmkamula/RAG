# Ship 85' arc retrospective (2026-08-19)

## Arc summary

User direction: **"Full arc — normalizer + LLM path + link-follow."**
Followed by course-correction after empirical measurement: **"unstructured
is doing its job. The problem is translating the data to evidence."**

Ship 85' extends Ship 84's XLSX measurement into runtime improvements.
Investigated why the multi-sheet ISO workbook had a 5× strict/lenient
F1 gap (4.63% vs 21.70%). Tried an extract-time LLM path on the
richer reader output; measurement showed a **regression** on multi-
sheet workbooks (aggregate F1 down 4.89pp). Root cause identified:
LLM can't disambiguate "this table IS the target register" from "this
table is a related register" from markdown alone. Pivots the arc:
extract-time LLM path guarded off; build-time LLM curator for
workbook_mappings YAMLs (Ship 80'.b/83'.b pattern) deferred to Ship 86'.

**Durable deliverable**: Ship 85'.a rich xlsx reader via unstructured.io
— 250 hyperlinks + 652 cross-sheet refs + 42 HTML tables captured on
ISO workbook, previously invisible to any pipeline.

## Sub-arcs

### Ship 85'.a — normalize xlsx reader via unstructured.io

Chose `unstructured.io` after resource survey (11GB root disk free,
6GB memory available). User accepted disk pressure for wider adoption
+ future-format coverage. Install:
```
pip install --user --break-system-packages "unstructured[xlsx,pdf,docx]"
+ manual spacy model install en_core_web_sm
```

**New helpers in `rag/intake/readers.py`**:
- `_partition_xlsx_via_unstructured()` — calls `unstructured.partition.xlsx`,
  groups elements by `page_name` (sheet), pairs Title elements with
  subsequent Tables, captures HTML markup
- Hyperlink + cross-sheet formula capture via openpyxl (unstructured's
  xlsx partition strips these)

**Output**: `doc.extraction_metrics["structured_sheets"]` — list of
per-sheet dicts:
```python
{
  "sheet_name":       str,
  "titles":           [str],
  "tables_html":      [{text, html}],
  "text_lines":       [str],
  "hyperlinks":       [{cell, url, label}],
  "cross_sheet_refs": [{cell, formula}],
}
```

**Measured on ISO workbook (300KB, 37 sheets)**:
- 42 tables with HTML markup
- **250 hyperlinks** (URLs + labels + cell coords)
- **652 cross-sheet formula refs**
- All captured in 4.8s partition + ~2s hyperlink walk

Metadata previously invisible to any pipeline. Ship 85'.a is a
durable win regardless of the Ship 85'.b outcome.

### Ship 85'.b — extract-time LLM path via markdown rendering

Added `_render_structured_sheets_markdown()` in extractor.py — renders
`structured_sheets` to markdown with H2 per sheet, Tables as embedded
HTML, hyperlinks as `[label](url)` list, cross-sheet ref counts.

Modified extractor.py xlsx block to populate `doc.markdown` from the
rendered content and fall through to the standard consensus + per_must
LLM pipeline (instead of `return []`).

**Result on ISO workbook**:
- `xlsx_llm_path_active` fired, 120K markdown from 37 sheets
- LLM extractor per_must: 662 MUSTs on 114 leaves, 191 yes-verdicts (29% yes rate — more selective than DOCX)
- Consensus accepted 66 candidates
- Total findings: **427** (vs Ship 84's 220)
- **Strict TPs**: 5 (SAME as Ship 84)
- **Lenient TPs**: 34 (DOWN from Ship 84's 37)

**Aggregate F1 vs Ship 84 baseline (LLM GT scoring)**:

| Path | Strict F1 | Lenient F1 |
|---|---|---|
| Ship 84 (workbook_persistence only) | 10.83% | 24.48% |
| **Ship 85'.b (LLM path + workbook_persistence)** | **5.94%** | **15.12%** |
| Delta | **-4.89pp** | **-9.36pp** |

**Root cause of regression** (user's diagnosis, confirmed by data):
> "Unstructured is doing its job. The problem is translating the data to evidence."

LLM sees "Asset ID | Name | Owner | Access Rights..." columns across
37 sheets and says yes to many register-shape MUSTs. But there might
be 5 sheets that LOOK like asset registers — only 1 is THE Asset
Register for A.5.9. LLM can't disambiguate from markdown alone.

Contrast with why LLM works on DOCX: prose has semantic framing
("The Asset Register captures..."). Tables lack that framing. This
is the same lesson as Ship 80'.b's fingerprint curator vs Ship 81'.d's
per-MUST — semantic reasoning is better at build-time (once per
mapping) than extract-time (every doc).

**Gated off** via `USE_XLSX_LLM_PATH=1` opt-in flag. Default (unset)
preserves Ship 84's behavior. Kept as reproducible experiment for
future revisit.

### Ship 85'.c → deferred to Ship 86'.a

Original arc plan: link-follow prototype for hyperlinks. After Ship
85'.b regression + user pivot ("no drift from LLM path"), plan
became: LLM curator for `workbook_mappings/*.yaml` — same shape as
Ship 80'.b/83'.b fingerprint YAML curator. Model gpt-4.1-mini
(OpenAI, matching prior curator work — no Claude lock).

Estimated scope: ~half-day (37 sheets × ~5 MUSTs each × ~15s LLM
call = ~15min compute + ~$1-2 cost). Deferred to Ship 86'.a as a
focused arc with room to properly author + review workbook_mappings
YAMLs (complex schema — column bindings, freshness rules, evidence
types).

### Ship 85'.d — dogfood measurement (proved 85'.b regression)

Re-extracted all 4 XLSX docs with 85'.b path active:
- Templated docs (raci, a51_review, a51_comm): identical F1 to Ship 84
  (templated fast-path dominates, LLM path adds nothing)
- ISO workbook: F1 regressed (-4.89pp aggregate)

Confirmed 85'.b is a net negative on multi-sheet workbooks. Gated
off before commit.

## Codified lessons

**Lesson 77: External libraries earn their keep at the RIGHT layer.**

unstructured.io absolutely delivered on Ship 85'.a: 250 hyperlinks +
652 cross-sheet refs + 42 HTML tables captured in 4.8s. But layering
LLM-as-evidence-classifier on top of that structured output (Ship 85'.b)
didn't work. The library did its job — the extraction layer was
choosing the wrong tool.

**Lesson 78: LLM as extract-time judge on structural data (tables)
underperforms LLM as build-time curator.**

Multi-sheet XLSX has table content that LOOKS semantically similar
across sheets. Extract-time LLM can't distinguish "this table IS the
target register" from "similar-shaped register for a different
control." Build-time LLM curator (author sheet↔MUST mappings once)
sidesteps this because the curator sees the SHEET NAME context, not
just data.

Same pattern as Ship 80'.b/83'.b (LLM curator worked) vs Ship 81'.d
(LLM per-MUST also worked but at 100× cost) — build-time authoring
is cheaper AND more precise for structural data.

**Lesson 79: Measurement can pivot arc scope mid-flight.**

Ship 85' was scoped as normalizer + LLM path + link-follow. After
85'.b measurement showed regression, user pivot ("are we drifting
away from the LLM path?" → "workbook_mappings LLM curator") became
the right direction. Arc-time replanning is normal.

**Lesson 80: Multi-provider LLM architecture is a strategic asset.**

User raised Claude-lock concern. Actual state: only Ship 82'.a's
Claude-Opus GT authoring is Claude-specific. All curator + runtime
paths use gpt-4.1 / gpt-4.1-mini (OpenAI). `rag/llm_client.py`
supports both providers via env-configurable model per purpose.
Ship 85'.c/86'.a curator will use OpenAI, preserving multi-provider
architecture.

## Files changed

- `rag/intake/readers.py` — new `_partition_xlsx_via_unstructured()` +
  hyperlink/xref capture wired into `_read_xlsx`
- `rag/intake/extractor.py` — new `_render_structured_sheets_markdown()`
  + guarded LLM path activation for xlsx (default off)
- `docs/ground_truth/ship77d_measurement/run_xlsx_ship85.csv` (new)
- `docs/memory/ship_85_prime_arc_retrospective.md` (this)

**Package installs (root disk usage note)**:
- `unstructured[xlsx,pdf,docx]` — ~400MB (spacy models + transformers + torch)
- en_core_web_sm spacy model — 12.8MB
- Root disk went 62% → ~66% used

## Deferred to Ship 86'

- **Ship 86'.a**: LLM curator for `workbook_mappings/*.yaml` via
  gpt-4.1-mini. Author sheet↔MUST bindings for the ISO workbook's
  ~30 unmapped/partial sheets. Templated fast-path unaffected.
- **Ship 86'.b**: dogfood + measure. Target: multi-sheet ISO workbook
  strict F1 crosses 20% (matching Ship 84's lenient number).
- Link-follow prototype (original 85'.c scope) — deferred further;
  hyperlinks are captured in `structured_sheets` metadata and can be
  consumed by any future component.
- PDF measurement (still deferred from Ship 84 — no PDF at hand).

## Baseline

Ship 85' close: eval pass at N/233 confirmed pre-commit. Runtime code
changes:
- `readers.py::_read_xlsx` — adds `structured_sheets` metadata to
  extraction_metrics (opt-in consumer; no default consumer active)
- `extractor.py` xlsx block — LLM path gated off by default via
  `USE_XLSX_LLM_PATH` env flag

No behavioral change on chat pipeline or DOCX/PDF/CSV intake. XLSX
extraction preserves Ship 84's workbook_persistence-only shape by
default.
