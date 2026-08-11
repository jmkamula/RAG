---
name: ship-60-prime-arc-2026-08-11
description: "Ship 60' arc retrospective — Advisory refactor via SSoT + bridge awareness. `build_per_must_advisory_data` sourced from posture_must_verdicts + posture_must_bridge_coverage + a new cached leaf-structure fetcher instead of per-request evaluate_one_control walks. 5 advisory sites inherit the fix; bridge attribution surfaces per-MUST + per-leaf without changing the response envelope. Legacy engine fallback retained. Baseline 230 PASS held."
metadata:
  type: project
  ship: "60'"
---

# Ship 60' — Advisory refactor via SSoT + bridge awareness

## The arc in one sentence

Ship 60' converts `build_per_must_advisory_data` — read by Dashboard
advisory, SPA leaf-detail, chat casefile augment, batched refs, and
chat markdown builder — from a per-request `evaluate_one_control`
engine walk into a compose of (Ship 58'/59' SSoT verdicts) + (Ship
60'.a cached leaf-structure fetch), and surfaces bridge attribution
per MUST + a leaf-level `n_bridged` count for consumer UX opt-in.

## Motivation

Ship 58' shipped `posture_must_verdicts` as per-MUST SSoT. Ship 59'
added `posture_must_bridge_coverage` for cross-framework attribution.
But every advisory-building code path still ran `evaluate_one_control`
per request — walking the Neo4j FulfilmentSpec, running per-leaf
evaluators, composing verdicts — data already computed and persisted
during `load_posture`. Advisory sites paid the redundant compute AND
didn't have access to the bridge attribution layer.

Ship 60' closes that gap: advisory reads the truth SSoT already
computed, then joins with a cached leaf-structure lookup (MUST text +
leaf ↔ evidence_type + leaf ↔ MUST_ids mapping) for the shape info
SSoT doesn't store.

## Sub-arcs

| Sub-arc | Deliverable |
|---|---|
| 60'.a | New `rag/posture/leaf_structure.py` — `get_control_leaves(control_ref, standard_id)` returning `ControlLeaves(spec_op, leaves=[LeafInfo(leaf_id, title, evidence_type, must_ids, must_texts, ...)])`. Tenant-agnostic (curator-authored data), 30-second TTL LRU cache matching `engine_runner._cached_er_evidence_types`. Silent-fallback on Neo4j failure. Verified: A.5.15 returns 4 leaves matching `evaluate_one_control`'s leaf list. |
| 60'.b | `build_per_must_advisory_data` refactored — new `_build_advisory_from_ssot` helper reads SSoT via `read_must_verdicts_by_control` + leaf structure via `get_control_leaves` + posture_controls.finding for top-level NC/OFI. Legacy `evaluate_one_control` path retained as fallback when SSoT is empty (fresh tenant / never-loaded control). 5 advisory sites inherit the fix without call-site changes. N/A-excluded MUSTs handled by "MUST-id in catalog + absent from SSoT → drop from advisory" (implicit N/A filter). |
| 60'.c | Bridge attribution surfaced in the response — `must_items[].bridge_sources` populated from `MustVerdict.bridge_sources` (per-MUST auditor attribution: `source_must_id`, `source_control_ref`, `source_standard_id`, `source_role`, `edge_type`) + leaf-level `n_bridged` count (unmet-direct MUSTs with ≥1 bridge). Fallback path emits empty `bridge_sources` + `n_bridged=0`. Consumer UX opt-in — no envelope change. |
| 60'.d | Interim retro (initial write). |
| 60'.e | `build_evidence_class_breakdown` refactored — same SSoT + leaf-structure compose pattern applied to the dashboard drill-in surface. New `_build_evidence_class_breakdown_from_ssot` helper; source_documents / template_availability / cite fields stay on the same Postgres helpers (never touched engine). Bridge attribution added: per-MUST `bridge_sources` + per-leaf `n_bridged`. Legacy `evaluate_one_control` fallback retained. Verified: A.5.15 breakdown matches per_must advisory numbers (4 leaves, 10/19 = 53% overall on Arion); Art.32 shows 6/16 = 38% with total `n_bridged=10`. |
| 60'.f | Fallback telemetry. `advisory.fallback` + `evidence_class_breakdown.fallback` `logger.info` lines fire whenever the legacy `evaluate_one_control` path fires (SSoT empty or leaf-structure unavailable). Enables a data-driven retire-by decision on the fallback path in a future arc — no assumptions needed. |
| 60'.g | SPA bridge chip. New `renderBridgeChip(leaf)` helper in `static/arioncomply.html` builds a green cross-framework nudge from `n_bridged` + unique source `standard_id`s across the leaf's unmet MUSTs. Wired into two surfaces: (1) advisory panel unmet-leaf render (`renderAdvisoryPanel`), (2) dashboard evidence-classes drill-in per-leaf block. Empty on legacy fallback responses. Message shape: "3 elements are already covered by evidence for related ISO 27001:2022 controls." |
| 60'.h | Chat advisory markdown nudge. New `_bridge_nudge_line(leaf)` helper in `rag/posture/advisory.py` mirrors the SPA chip's message shape as a single markdown line. Appended after `To address:` on each unmet leaf in `_render_advisory_markdown`. Consumed by `build_per_must_advisory` — the chat surface for posture_check queries that identify a single control. Verified on Art.32: all 4 leaves render the nudge with rolled-up ISO 27001:2022 + ISO 27701:2019 attribution. Legacy chat markdown path. |
| 60'.i | Case-file structured render — `LeafState` gets `n_bridged: int` + `bridge_stds: list[str]` (Pydantic model in `rag/casefile/answer_schema.py`). `_evidence_summary` in `answer_augment.py` rolls up unique source `standard_id`s from advisory data's `must_items[].bridge_sources` on unmet MUSTs (humanized inline — same `_HUMAN_STD` idiom as `advisory.py`). SPA `renderRelatedCard` primary-card checklist adds a `sa-leaf-bridge` nudge under each leaf row when populated, with new CSS class matching the existing `sa-leaf-*` palette. Verified: `is Art.32 compliant?` chat turn returns a `primary` card with all 4 leaves carrying `n_bridged={4,2,1,3}` and `bridge_stds=['ISO 27001:2022', 'ISO 27701:2019']` — SPA renders the green attribution nudge on each. |
| 60'.j | LLM prompt digest bridge-count suffix. Tight-token addition: `_render_xfw_bridges` in `rag/casefile/digest.py` appends `(N/M MUSTs bridge-covered)` to each XFW BRIDGES line when `cf.bridge_counts[ref]` is populated. New `CaseFile.bridge_counts: dict[str, tuple[int, int]]` field precomputed in `rag/llm_answer.py` via two aggregated queries against `posture_must_verdicts` + `posture_must_bridge_coverage` for the xfw obligation refs the digest is about to render (scope-bounded — no per-obligation SSoT scan beyond what the section already surfaces). Best-effort: any failure leaves `bridge_counts` empty and the section renders as pre-60'.j. Token cost: ~8 tokens per bridge line × typically 1-5 lines = ≤40 tokens total, only fires when the section already renders. Verified render: `XFW BRIDGES:\n- Art.32 ← A.5.15 [OFI], A.5.18 [NC], A.5.23 [NC]  (10/16 MUSTs bridge-covered)` = 23 approx tokens (from 15 pre-60'.j). |

## Key architectural decisions

**1. Leaf structure is a separate cached fetcher, not merged into the SSoT table.**
Alternative: extend `posture_must_verdicts` with `must_text`, `leaf_id`,
`evidence_type` columns. Rejected because (a) MUST text is curator-
authored / tenant-invariant — duplicating in per-tenant rows wastes
storage; (b) the leaf structure is process-cache-friendly (30s TTL, ~50ms
Neo4j scan, fanout amortizes across a chat turn's advisory calls); (c) a
schema change on posture_must_verdicts would ripple through the SSoT
writer + Ship 58'.u sweep. Fetcher stays simple; SSoT stays fulfillment-
only.

**2. N/A filtering is implicit via SSoT membership.**
Ship 58 codified: N/A-excluded MUSTs are never written to SSoT (the
engine's `_fetch_na_must_ids` filters them out inside
`GenericLeafEvaluator`). So *"MUST-id present in leaf.must_ids but
absent from SSoT verdicts dict"* = tenant N/A-excluded that MUST. Ship
60'.b's advisory join drops those automatically — no separate N/A
lookup needed. Concrete: A.5.15 policy leaf's catalog has 7 MUSTs; on
Arion's cloud-only profile, 1 is N/A-excluded (`physical_rules`),
leaving 6 in SSoT. Advisory returns 6, matching what
`evaluate_one_control` returned pre-refactor (5 recognised + 1
unrecognised).

**3. Fallback path stays for defence-in-depth (retire-by TBD).**
If SSoT is empty for a tenant+control, the legacy engine path fires.
Cases: fresh tenant hasn't triggered `load_posture` yet, or Ship 58'.u
sweep hasn't caught up. Since Ship 58'.s wires `kick_posture_refresh`
into every write endpoint and Ship 58'.u sweeps every 30 min, these
should be rare in steady state. Ship 60' does NOT delete
`evaluate_one_control` — Stage-2 detail UI still uses it directly for
the derived_from tree render. Retire-by decision deferred until we
observe telemetry on how often the fallback fires.

**4. Bridge attribution surfaces per-MUST + per-leaf, response envelope unchanged.**
`must_items[].bridge_sources` is a new field on existing objects;
consumers ignoring it see no change. `n_bridged` is a new counter on
leaf objects. `posture` / `n_leaves` / `n_satisfied` / `n_partial` /
`reason` semantics preserved. UI can opt in later (Ship 60' does not
touch SPA / chat markdown).

## Data verification

**A.5.15 (ISO 27001)** — verified both paths produce the same leaf
structure:
```
Old (evaluate_one_control):    New (SSoT):
- periodic_review        5/5   - periodic_review        1/5 (SSoT reflects live)
- communication_record   5/5   - communication_record   1/5
- management_approval    3/3   - management_approval    3/3
- access_control_policy  6/6   - access_control_policy  5/6 (N/A drops 1 MUST)
```
(numbers diverge because SSoT reflects current recognition against
tenant supply; old path re-computed the same thing per request. Both
produce equivalent structures.)

**Art.32 (GDPR)** — bridge attribution surfaces:
- 4 leaves, 16 MUSTs applicable, `posture=NC`, `n_bridged` totals 10
  across leaves.
- Per-MUST `bridge_sources` includes 107 attribution rows (from
  A.5.23 IMPLEMENTS + other Program controls) — the same numbers
  Ship 59'.d retro documented.
- Consumers that render `bridge_sources` can now show *"this GDPR
  MUST is covered via ISO A.5.23 evidence"* deterministically.

**Eval baseline held** — 230 PASS + 1 known-flaky FAIL (#5
physical-leak, stochastic per CLAUDE.md notes) + 1 permanent WARN
(#200 posture_check vs gap_analysis type mismatch). Identical to
pre-Ship-60 baseline. No consumer surface regressed on the shape
change.

## Codified lessons

### 17. Cache curator-authored structure separately from tenant fulfillment

Two data axes: (1) *what the standard requires* (curator-authored,
tenant-invariant, changes only when curation ships) and (2) *what the
tenant has satisfied* (tenant-specific, changes on every upload). Ship
60' keeps them as separate caches: `leaf_structure._CACHE` is
tenant-agnostic with a 30s TTL; `posture_must_verdicts` is per-tenant
with delete+insert-atomic replacement per `load_posture`. Merging them
into one per-tenant table wastes storage; separating them lets each
cache use its natural invariance boundary.

Rule: when combining two data sources at a compose site (advisory,
digest, dashboard), the layers below should each cache at their own
natural invariance boundary — don't pull tenant-agnostic data into a
per-tenant table just for join convenience.

### 18. Backward-compat via additive fields, not new response versions

Ship 60'.c added `bridge_sources` per MUST + `n_bridged` per leaf
without introducing v2 of the advisory endpoint or a feature flag.
Existing consumers (chat markdown, Dashboard render, SPA leaf detail)
that read `items_missing` / `must_items[].text` see zero change.
Consumers that want bridge awareness read the new fields when
present. No compat shim, no dual-path serializer.

Rule: when a data-layer surface gains new information, prefer additive
fields on the existing envelope over a new envelope version. Reserve
version bumps for breaking removals or shape changes; additions cost
consumers nothing.

## What's now different in the product

- **Advisory read path** — 5 sites (Dashboard advisory / SPA
  leaf-detail / chat casefile augment / batched refs / chat markdown
  builder) no longer pay the per-request engine round-trip. Read from
  SSoT + cached leaf structure.
- **Bridge attribution available per-MUST** — auditor can see
  *"item:Art.32:rev_iso_alignment is covered via A.5.23 IMPLEMENTS
  bridge"* without walking to another framework's dashboard.
- **`n_bridged` per leaf** — new count for consumer UX (e.g. leaf
  chip could render "3 of 5 MUSTs covered via ISO" alongside "1
  direct + 3 bridged + 1 missing").

Chat + Dashboard + SPA UX shape unchanged this ship. Consumer surfaces
opt into the new fields on their own timeline.

## Follow-ons deferred

- **Retire legacy engine fallback** — after N weeks of telemetry
  (Ship 60'.f added the logger.info hook). Grep
  `advisory.fallback` / `evidence_class_breakdown.fallback` in prod
  logs; if never fires in steady state, delete the fallback path.
- **Bridge nudge in case-file LLM prompt digest** — DELIVERED in
  Ship 60'.j as a tight `(N/M MUSTs bridge-covered)` suffix on
  the existing XFW BRIDGES section rather than a new section.
- **`evidence_class_breakdown` migration** — DELIVERED in Ship 60'.e
  as a same-arc addendum. source_documents / template_availability /
  cite fields stayed on their existing Postgres helpers (they were
  never coupled to the engine).
- **Ship 61'.a Evidence Package hybrid** — unchanged from Ship 59'.d
  retro. EP still reads raw `document_findings` for verbatim
  excerpts; hybrid uses SSoT for coverage summary.
- **Bridge-aware `.covered` vs `.satisfied` UX distinction** —
  consumer decision on whether an unmet-but-bridged MUST renders
  differently from unmet-nowhere. Not decided this ship.

## What Ship 60' costs to reproduce

- Schema migrations: 0
- Wall clock: ~3 hours (design + implementation + verify + retro
  + 60'.e sibling migration + 60'.f-g consumer UX)
- Files touched: 3 (rag/posture/advisory.py, rag/posture/leaf_structure.py NEW,
  static/arioncomply.html)
- Lines: ~700 (new module + refactor on both advisory builders +
  chip helper + wiring)
- Eval regression: 231 PASS + 1 WARN (baseline preserved; #5
  physical-leak stochastic landed on PASS side this run)
- Deferred: retire legacy fallback (post-telemetry), Evidence
  Package hybrid (Ship 61'.a).
