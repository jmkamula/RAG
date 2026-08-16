---
name: task-606-extractor-marker-validation-2026-08-15
description: "Task #606 — closes docx lockdown dogfood friction #6. Extractor now validates every <<MUST item:X:Y>> / <<SHOULD item:X:Y>> marker on re-upload against the canonical catalog (ALL_EVIDENCE_REQUIREMENTS ∪ DerivedSpec.direct_evidence). Mangled markers get logged + skipped instead of silently binding evidence to nonexistent ids."
metadata:
  type: project
  ship: templates
---

# Task #606 — Extractor validates marker id against catalog

## Motivation

Task #604's docx protection is a soft guard — a determined officer
can Stop Protection from the Review tab. Dogfood friction #6:

> Officer might disable protection to fix a typo elsewhere. If they
> forget AND accidentally edited a `<<MUST item:X>>` marker, the
> extractor might mis-bind. Low likelihood but worth documenting.
>
> **Suggested fix**: the extractor should defensively validate that
> each `<<MUST item:X:Y>>` marker on re-upload matches a known
> catalog checklist item id; if a marker was mangled
> (`<<MUST item:A.5.15:logica_rules>>`), log a warning and skip.

The pre-fix behavior when a marker gets mangled:
1. Extractor regex still matches (id shape is regex-compatible).
2. `DocumentFinding` gets created with `checklist_item_id='item:A.5.15:logica_rules'`.
3. Writer persists the row.
4. Downstream SSoT reader queries `posture_must_verdicts` for that
   id — the id is not in `checklist_items`, so it silently drops.
5. Tenant loses evidence, no error, no audit trail.

Post-fix: mangled markers get logged with a WARNING and the
extraction skips them cleanly. Tenant's actual evidence that
landed on VALID markers still binds; only mis-bound content is
dropped, and it gets flagged in metrics + logs.

## What shipped

`rag/intake/extractor.py`:

1. **`_valid_item_ids()`** — lazy-loaded canonical union of
   ChecklistItem ids across `ALL_EVIDENCE_REQUIREMENTS` +
   `ALL_DERIVED_SPECS[*].direct_evidence`. Walks `must_contain` +
   `should_contain` per EvidenceRequirement. Cached after first
   call (5,385 ids on the current catalog). Follows the "catalog
   membership predicate" convention documented in `CLAUDE.md`.

2. **`_catalog_recognises(item_id)`** — thin membership check.

3. **`_extract_templated_via_edit_zones`** — before creating a
   `DocumentFinding` for each edit zone's item id, runs
   `_catalog_recognises` and skips + logs on miss. New metric
   `templated_zones_mangled` tracks the count per doc.

4. **`_extract_templated_via_table`** — same treatment for
   `<!-- column: item:X:Y -->` metadata entries inside
   `<!-- TABLE-COLUMNS -->` blocks. New metric
   `templated_table_cols_mangled`.

Warnings go to the standard `logger` (already imported), so they
surface in the API server log stream + `intake_trace_log` (via
existing telemetry hooks that consume the logger).

## Verified

Small test (Arion catalog):

```
catalog size: 5,385 ids

  item:A.5.15:logical_rules:    recognized=True
  item:A.5.15:logica_rules:     recognized=False   ← mangled (missing 'l')
  item:A.5.15:LOGICAL_RULES:    recognized=False   ← wrong case
  item:A.5.16:rev_identity_ref: recognized=True
```

End-to-end (fake edit zones with 2 valid + 1 mangled):

```
edit zones matched:  3
findings emitted:    2
metrics: {
  'templated_edit_zones_total': 3,
  'templated_edit_zones_bound': 2,
  'templated_zones_scaffolding': 0,
  'templated_zones_mangled': 1,
}
```

Warning logged for the mangled marker; two valid findings emit as
expected.

## Files touched

- `rag/intake/extractor.py` — ~50 LOC (catalog builder + predicate
  + 2 validation call-sites + 2 new metrics).

Zero schema. Zero SPA / API changes. The metrics land alongside
existing `templated_*` counters in `doc.extraction_metrics` — the
downstream `intake_trace_log` writer picks them up automatically.

## Codified lesson

### 43. Silent-drop is worse than loud-skip

The pre-fix behavior was already "defensive" in a sense — a bogus
`checklist_item_id` doesn't crash the pipeline, it just doesn't
show up in `posture_must_verdicts` because the id isn't in
`checklist_items`. No error, no crash. Fine on the wire.

But for the tenant, that's the WORST outcome: they typed evidence
into a placeholder, uploaded the doc, and it silently vanished.
No log, no dashboard hint, no audit trail. They open the leaf-
detail panel next week and see "still needed."

Loud-skip is strictly better: same drop behavior, but with a
warning in the log + a metric that surfaces in `intake_trace_log`
+ (future) a tenant-facing intake-status card that says
*"3 evidence sections skipped because their markers were mangled
— review the source document."*

Rule: never let a defensive skip be silent. Someone downstream
will pay for the missing evidence; give them a breadcrumb.

## Post-ship dogfood correction — what this actually catches

Dogfood report at
`docs/dogfood/task_606_mangled_marker_dogfood_2026_08_16.md`
surfaced that Task #606's coverage is narrower than dogfood
friction #6 implied. The reader's `_arion_docx_to_edit_zones`
(readers.py:590) reconstructs zone markers from the visible
`◆ Required element — <slug>` labels in the docx — NOT from the
hidden `<<MUST item:X>>` markers Task #604 stamped with
`w:vanish`. So when a tenant mangles the hidden marker,
the reader's reconstruction still uses the unmangled slug and
Task #606's validation doesn't fire.

**What Task #606 actually catches**:
1. Direct `.md` uploads with mangled `<!-- EDIT-ZONE-START item:X -->`
   comment ids.
2. Mangled `<!-- TABLE-COLUMNS -->` metadata entries.
3. Any future reader path that uses the raw `<<MUST>>` marker as
   the id source.

**What Task #606 does NOT catch**:
- docx uploads with hidden-marker mangling (reader uses ◆ label slug).

**Value delivered anyway**:
- Metrics (`templated_zones_mangled`, `templated_table_cols_mangled`)
  land in `intake_trace_log` — instrumented for the day this fires.
- Defensive backstop for markdown-direct-upload paths.
- No downside — the catalog membership predicate is cached and cheap.

## Bigger bug surfaced by the dogfood

Task #606's dogfood also surfaced Bug B: any tenant who downloads
a docx template and re-uploads it UNEDITED currently produces
10 false `Comply` findings on A.5.15 because `_is_pure_scaffolding`
doesn't recognize the reader-reconstructed scaffolding shape
(`*Do not edit — system id*: <<...>>`, `*Standard text:*`,
`_Behavioural principle_`, `✓ Good:`, `Best practice ✓ — covered:`).
Task #603's "empty edit zones by default" made this bug much
more visible — previously prefilled zones had a
`<!-- prefilled from N -->` comment that `_is_pure_scaffolding`
recognized.

Task #607 opens to fix this: extend `_is_pure_scaffolding` to
strip known reader-reconstructed patterns before deciding
scaffolding-vs-evidence. Details in the dogfood report.

## Follow-ons

- **Task #607 (URGENT)** — Bug B fix: extend `_is_pure_scaffolding`
  to recognize reader-reconstructed patterns. Blocks any customer
  docx-upload loop.
- **Remaining docx lockdown dogfood items**:
  - #1, #4 — SDT-based placeholder (Word-native affordance).
  - #3 — Header/footer editability.
  - #5 — Multi-version Word testing.

Combined docx lockdown arc after Tasks #604 + #605 + #606:
- ✓ Markers hidden (`w:vanish`)
- ✓ Whole doc locked (`readOnly` + enforcement)
- ✓ Edit zones editable (body-level `w:permStart`/`w:permEnd`)
- ✓ Signature cells editable (cell-level `w:permStart`/`w:permEnd`)
- ✓ Catalog membership predicate ready (narrow coverage
  documented above; Task #607 will connect it to the docx path)
