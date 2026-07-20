---
name: ship-11-prime-c-content-shape-filter-2026-07-20
description: "Ship 11'.c — MUST-aware content-shape filter for extractor findings (Patterns 1 + 3 from Ship 11'.a)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 11'.c (2026-07-20) — Layer-1 pre-critic filter (technically
post-LLM in the current pipeline, since the critic runs the LLM;
this filter drops the LLM's confirmed excerpts). Targets Patterns
1 (field labels) and 3 (fingerprint fragments) from Ship 11'.a.

## Motivation

The Ship 10 HITL review found ~16 rejects across Patterns 1 and 3:

- **Pattern 1 — field labels** from RoPA / DPIA tables:
  `"Subprocessors   Any third parties involved"`,
  `"Retention Period   Timeframe for keeping the data"`,
  `"International Transfers   Details of transfers outside the EU/EEA"`
- **Pattern 3 — fingerprint fragments** — section headers +
  cross-refs:
  `"Return, Transfer or Deletion of PII (A.8.3.2 / B.8.4.2)"`,
  `"Data Subject Rights Handling Procedure (DOC051)"`

The critic-verifier confirms these because they ARE verbatim in
the source. The verbatim gate can't distinguish structural markup
from substantive prose.

## What shipped

**`_looks_like_field_or_header(quote, must_id=None) -> (drop, reason)`**
in `rag/intake/extractor.py`. Deterministic detector that returns
True for four failure shapes:

1. **`section_header_with_ctrl_refs`** — trailing parenthetical of
   control refs (e.g. `(A.8.3.2 / B.8.4.2)`) + no sentence
   terminator. Universal drop.
2. **`doc_cross_ref`** — trailing `(DOC051)` / `(DOC-014)` +
   no sentence terminator. Universal drop.
3. **`table_field_label`** — 3+ consecutive whitespace runs
   (mammoth's markdown table-cell separator on collapsed rows).
   **MUST-aware**: preserved when bound to `reg_` / `scope_` /
   `ropa_` MUST (RoPA field IS the register field). Dropped for
   `rev_` / `proc_` / other prefixes and for unbound sources.
4. **`bullet_fragment`** — starts with `- ` / `* ` / `•`, no
   sentence terminator, < 100 chars. Drop.

Companion helper: `_must_prefix(must_id) -> str` extracts the
semantic prefix (`reg_`, `proc_`, `rev_`, etc.) from a MUST id
like `item:A.7.2.4:reg_lawful_basis_link`. Requires colon-shape;
bare identifiers return empty.

**Wired into two finding-emission paths:**

- `_run_critic_verifier_pass` (default extractor) — filter runs
  after `_evidence_grounded` verbatim check + before dedup.
  Telemetry: `doc.extraction_metrics["dropped_content_shape"]`.
- `_parse_llm_response` (legacy LLM pass-1) — filter runs after
  `_looks_like_metadata_block`. Telemetry:
  `dropped_content_shape` counter + accumulated onto
  `doc.extraction_metrics`.

## MUST-aware design rationale

Table-field-shape quotes bound to `reg_` / `scope_` / `ropa_`
MUSTs are LEGITIMATE — a RoPA row IS the register field that
these MUSTs expect as evidence. Dropping them would lose real
coverage.

Table-field-shape quotes bound to `rev_` (review record) or
`proc_` (procedure content) MUSTs are noise — the MUST semantic
demands substantive prose (review artefact / procedure text),
not a table cell.

This addresses a nuance my Ship 10 approvals got WRONG:
- Ship 10 approved `"Purpose of Processing   Why the data is
  being processed"` bound to `A.7.2.1:rev_coverage_check` — a
  `rev_` MUST. Ship 11'.c correctly rejects this: the table field
  documents "purpose is documented", but doesn't evidence "coverage
  check performed" (which needs a review record).
- Ship 10 approved `"Legal Basis / Lawful basis..."` bound to
  `A.7.2.2:rev_basis_currency` — same reasoning. Correctly caught.

## Coverage against Ship 10 dataset

From the 16 Pattern-1/3 rejects:

| Shape | Ship 10 rejects | 11'.c catches |
|---|---|---|
| Table field label (3+ whitespace) | 5 | 5 ✓ |
| Section header with ctrl-refs | 4 | 4 ✓ |
| Doc cross-refs | 1 | 1 ✓ |
| Single-space field label ("International Transfers Details...") | 3 | ⛔ 0 — waits for 11'.d anchor-semantic |
| Bullet fragment (colon-separator noun phrase) | 3 | ⛔ 0 — same |

**Coverage: 10 of 16 (63%) of Patterns 1+3.** Remaining 6 need
Ship 11'.d anchor-semantic filter.

**Bonus catch: 2 Ship 10 approvals I got wrong** — RoPA #1 (A.7.2.1
rev_coverage_check) and #2 (A.7.2.2 rev_basis_currency) — table
fields bound to `rev_` MUSTs. Filter tightens discipline over my
lenient Ship 10 judgment.

## Tests

`tests/test_content_shape_filter.py` — 30 assertions across 6
test functions:

- `_must_prefix` — 10 cases (all MUST prefix families + bare ids +
  None)
- Universal drops — 4 cases (section headers + doc cross-refs,
  with and without MUST bindings)
- MUST-aware table field labels — 6 cases (rev_/proc_/reg_/ropa_/
  scope_/no-MUST)
- Prose preserved — 5 cases (full sentences, bullets with periods,
  prose mentioning control refs)
- Bullet fragments — 4 cases (bare stubs + long bullets +
  terminated bullets)
- Ship 10 replay — 4 catches + 2 misses (documented as expected
  waits for 11'.d)

All PASS.

## Baseline

Full eval running. This gate is additive-drop: it removes
findings that would otherwise be emitted. Existing document_
findings rows are unaffected (filter only applies during new
extraction).

## Ship 11' progress

| Sub-arc | Status |
|---|---|
| 11'.a Extractor quality plan | ✓ |
| 11'.b Bridge source-quality gate | ✓ |
| **11'.c Content-shape filter (MUST-aware)** | **✓** |
| 11'.d Critic prompt enhancement (anchor-semantic + MUST-prefix taxonomy) | next |
| 11'.e Re-extraction measurement checkpoint | pending |
| 11'.f Arc retrospective | pending |

## Related

- [[ship-11-prime-a-extractor-quality-plan-2026-07-20]] — parent
  design memo
- [[ship-11-prime-b-bridge-source-quality-gate-2026-07-20]] — 11'.b
- Ship 10 HITL review (2026-07-20) — the reject dataset this
  filter was designed against
