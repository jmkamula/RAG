---
name: ship-72-prime-arc-retrospective-2026-08-16
description: "Ship 72' arc close-out (72'.a → 72'.e). Extractor-side SSoT: consolidates scattered `is this a valid tenant finding?` rules into one FindingContract module + is_scaffolding predicate + catalog_recognises. 5 extractor call sites migrated, 1 test suite pins the SSoT, contract-native metrics land automatically in intake_trace_log. Closes the pre-existing docx round-trip false-Comply bug + establishes the pattern for future domain rules."
metadata:
  type: project
  ship: "72'"
---

# Ship 72' arc close-out

Four sub-arcs + closer over ~1 day (2026-08-16). Zero schema migrations.
Opens directly out of Task #606's mangled-marker dogfood, which
surfaced a bigger pre-existing bug (Task #607 as originally scoped)
and taught us to stop reaching for narrow scope by default.

## Sub-arcs

| Sub | What shipped | Files | Retro |
|-----|---|---|---|
| 72'.a | Introduce `FindingContract` + `is_scaffolding` + reader ▽/△ rail fix + migrate templated edit-zone + table-column paths | `finding_contract.py` (new) + `extractor.py` + `readers.py` | [[ship-72-prime-a-2026-08-16]] |
| 72'.b | Migrate LLM parser + legacy templated full-section paths | `extractor.py::_parse_llm_response` + `_extract_templated_via_full_section` | [[ship-72-prime-b-2026-08-16]] |
| 72'.c | Migrate xlsx path (2 call sites) + workbook_persistence catalog check | `extractor.py::_extract_templated_xlsx` + `workbook_persistence.py::_findings_for_pass` | [[ship-72-prime-c-2026-08-16]] |
| 72'.d | Snapshot tests (11 cases) + contract-native metric counters | `tests/test_finding_contract.py` (new) + `finding_contract.py` + `extractor.py` metric wiring | [[ship-72-prime-d-2026-08-16]] |
| 72'.e | This retro | — | (self) |

## Catalyst — the dogfood that opened Ship 72'

Task #606 was scoped as "add catalog membership check to
extractor_via_edit_zones + _via_table" (a narrow, call-site-local
fix). The mangled-marker dogfood proved it doesn't fire on the
docx path (reader uses ◆ label slug, not hidden `<<MUST>>` marker),
but it also surfaced a pre-existing structural bug: **any unedited
docx round-trip produced N false `Comply` findings per template**
because `_is_pure_scaffolding` didn't recognize the reader-
reconstructed scaffolding shape. Task #603's "empty edit zones by
default" made the bug much more visible; Task #603 didn't create
it.

Ship 72' was opened because the reflexive fix would have been
"extend `_is_pure_scaffolding` in the templated path" — the exact
scope-narrowing move that creates lattices of case-specific
handling. Instead the arc consolidated the rules into ONE canonical
layer and migrated consumers one at a time.

Pattern mirror: Ship 60' did the same shape for downstream
posture STATE (advisory → SSoT reader; findings → SSoT reader; EP
→ SSoT reader). Ship 72' does it for upstream finding VALIDITY
(templated → contract; LLM → contract; xlsx → contract; workbook
→ contract's predicate inline).

## The delta

**Before Ship 72':**

| Site                               | Scaffolding check         | Catalog check       | Ref resolution     |
|------------------------------------|---------------------------|---------------------|--------------------|
| `_extract_templated_via_edit_zones` | `_is_pure_scaffolding`    | Task #606 local     | `item_control_ref` |
| `_extract_templated_via_table`      | (only `col_has_data[i]`)  | Task #606 local     | `item_control_ref` |
| `_extract_templated_via_full_section` | Local placeholder-only  | none                | `item_control_ref` |
| `_extract_templated_xlsx` (×2)      | (only `col_has_data[i]` / `if not content`) | none | `item_control_ref` |
| `_parse_llm_response`               | Local hallucination check | `valid_items_by_ctrl` (per-control) | pre-resolved |
| `workbook_persistence._findings_for_pass` | none                | `_standard_for` (partial) | pre-resolved |

**After Ship 72':**

| Site                               | Scaffolding check | Catalog check | Ref resolution |
|------------------------------------|-------------------|---------------|----------------|
| All routing paths                  | `is_scaffolding`  | `catalog_recognises` | `item_control_ref` OR pre-resolved |

One predicate implementation. One catalog membership check. Six
extractor sites consume the SSoT; adding a new scaffolding pattern
is a one-file edit that every site picks up.

## Numbers

- **Bug fixed**: 39 false `Comply` findings per unedited docx
  round-trip across 4 sample leaves → 0.
- **Extractor sites migrated**: 6 (`.bind()` routing) + 1
  (inline `catalog_recognises`) = 7.
- **Sites NOT migrated**: 3 deterministic paths (consensus,
  critic, fingerprints) parked for a future sub-ship.
- **Snapshot test cases**: 11 (5 predicate + 4 contract + 2
  round-trip integration).
- **Contract-native metrics**: 4 counters (one per `SkipReason`)
  auto-surfaced in `doc.extraction_metrics` → `intake_trace_log`.
- **LOC delta**: `finding_contract.py` new (~350 LOC) +
  extractor call sites reduced by ~120 LOC of duplicated logic.

## Codified lessons

The arc produced two new codified lessons + reinforced an existing
one.

### 44. Domain rules at the highest layer, not the call site

When a bug surfaces at one call site, the temptation is to patch
that site's local check. That's a scope-narrowing move dressed as
expedience. If the underlying concept ("what is scaffolding?",
"what is a valid marker?", "what is tenant evidence?") is shared
across the app, codify at the highest layer where it's meaningful
— one predicate, one canonical set, used everywhere.

Applies retroactively to Task #606 (should have consolidated
`catalog_recognises` across every extractor rather than only
touching two sites).

### 45. Test the SSoT, not just the consumers

The old scattered private rules were tested (or not) at each call
site. When we consolidated onto the FindingContract SSoT, the
right test surface became the CONTRACT ITSELF — not each extractor's
integration test. `tests/test_finding_contract.py` pins the
predicate behavior directly + adds two integration snapshots for
end-to-end coverage. Total: 11 cases lock the entire SSoT.

Adding a new scaffolding pattern? One-file change in the predicate
+ one line in the test's `shapes` list. Adding a new `SkipReason`?
One enum value + one metric counter (via `_METRIC_KEY_PREFIX`
interpolation) automatically.

### Reinforced: Lesson 40 (Ship 60' arc) — dead-code paths are
### load-bearing bugs

The docx renderer had two dead-code paths (`<<DOC_CONTROL>>`
marker handling; `_render_marker_line` for MUST/SHOULD markers)
consumed one layer upstream. Ship 72'.a surfaced a THIRD one:
`_is_pure_scaffolding` was silently no-op'ing because the caller
(reader-reconstructed zones) emitted a shape the predicate didn't
recognize. The predicate returned False; the extractor took that
as "yes, tenant evidence"; findings emitted. No error, no crash.

Same failure mode as Ship 60'.d/e revealed: when one layer thinks
another has already handled the case, silent drift becomes silent
production bugs.

## What's left in the neighborhood

Follow-on to Ship 72' arc (not blocking any customer):

- **Deterministic path migration** — three sites still construct
  `DocumentFinding` directly: `_extract_via_consensus`,
  `_run_critic_verifier_pass`, `_extract_via_fingerprints`. Same
  migration shape as 72'.b/c. Metrics + snapshot tests would
  automatically surface any drift.
- **Metric consumer migration** — `intake_trace_log` schema
  currently has the pre-existing per-path counters
  (`templated_zones_scaffolding` etc.). Consolidating onto the
  contract-native `contract_skip_<reason>` counters is a downstream
  arc when we next touch the intake telemetry schema.

## Follow-ons parked from prior arcs

- **Task #595** — 22-article GDPR bridge-coverage gap. Independent
  arc, curator triage.
- **docx dogfood friction #1 / #4 / #3 / #5** — SDT-based
  placeholders, header/footer editability, multi-version Word
  testing. All docx-side; not blocking.

## Session shape

Ship 72' opened directly out of the "why do we keep dropping to
narrower scope" conversation. The 4-sub-arc + retro cadence in
one day continues the pattern of Ships 30-32 and 68-71: a
measurement-driven arc with sub-arcs that consume the SSoT one at a
time. The Ship 72' twist: the arc opener explicitly rejected the
narrow patch in favor of the SSoT + migration shape.

Codified lesson 44 is the durable takeaway. Every time a bug
surfaces at one call site, the question to ask before patching is:
*is this concept shared across the app? if so, this fix belongs
at the highest layer where the concept is meaningful, not here.*
