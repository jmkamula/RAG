---
name: ship-69-prime-arc-retrospective-2026-08-14
description: "Ship 69' arc close-out (69'.a → 69'.e). Bridge attribution granularity: retarget whole-article edges to named sub-clauses, create the stub nodes that were missing, and surface security-dimension aspects in the Evidence Package UX — all data-driven by a 200-LOC audit classifier that scoped the entire arc."
metadata:
  type: project
  ship: "69'"
---

# Ship 69' arc close-out

Four sub-arcs + closer over a single session on 2026-08-14. Total
wall clock: ~4 hours. Zero schema migrations.

Opens the door directly out of Ship 68'.b's honesty gambit ("retire
the fake coverage claim; reframe as asserted mapping"). Ship 69'
does the follow-on precision work: MAKE the assertion narrower
where the curator rationale already justifies it.

## Sub-arcs

| Sub | What shipped | Files | Retro |
|-----|---|---|---|
| 69'.a | Audit classifier over 452 edges; per-edge CSV + count distribution | `scripts/curation/audit_bridge_rationale.py` + `results/bridge_rationale_audit.csv` | [[ship-69-prime-a-2026-08-14]] |
| 69'.b | Retarget 50 IMPLEMENTS edges to named sub-clauses; parent-article union in the SSoT reader | `enrichment/relationships/relationship_catalog.py` + `rag/posture/must_verdicts.py` + `rag/posture/evidence_package.py` + `scripts/curation/retarget_bridges_69b.py` | [[ship-69-prime-b-2026-08-14]] |
| 69'.d | 12 GDPR stub nodes + retarget the remaining 13 edges | `scripts/curation/create_gdpr_stubs_69d.py` | [[ship-69-prime-d-2026-08-14]] |
| 69'.c | Dimension aspects extracted from rationale text; group-level italic sentence in EP | `rag/output/dimensions.py` + `rag/posture/evidence_package.py` | [[ship-69-prime-c-2026-08-14]] |
| 69'.e | This retro | — | (self) |

Sub-arc order matters: 69'.a's audit CSV is the input to 69'.b and
69'.d retargeters. 69'.d created the stubs that turned 13 more
edges into 69'.b-shaped retargets — so the two sub-arcs share
tooling. 69'.c stood independently because dimensions layer on
top of the (now narrower) attribution without depending on any of
the previous three.

## The 452 → 452 numbers

The bridge edge count didn't change across the arc — every edit
was a target retargeting, not a creation or a deletion. But the
attribution granularity moved:

| State                       | Whole-article edges | Sub-clause edges | Unspec / dim |
|-----------------------------|--------------------:|------------------:|-------------:|
| Pre-arc (post Ship 68'.b)   |               ~452  |                 0 |          n/a |
| Post 69'.b                  |                402  |                50 |          n/a |
| Post 69'.d                  |                389  |                63 |          n/a |
| Post 69'.c (UX overlay)     |                389  |                63 | ~168 surface |

The final state:
- **63 edges (14%)** point at a specific sub-clause. Reader sees
  narrower attribution + curator's specific rationale.
- **168 edges (37%)** carry dimension metadata surfaced in UX via
  read-time rationale parsing.
- **221 edges (49%)** are genuinely whole-to-whole. No action; Ship
  68'.b's honest reframe is the correct UX.

Two reader-side changes enabled 69'.b's granularity move without
regressing parent-article Evidence Packages:

1. `read_must_verdicts` unions descendant sub-clauses when the
   caller passes a whole-article `control_ref`
   (`target_control_ref = ANY(%s) OR target_control_ref LIKE
   ANY(%s)`).
2. `BridgeSource.target_control_ref` carries the actual retargeted
   ref so `mapping_meta` fetch queries Neo4j at the narrower node
   (rationale + confidence follow the target, not the caller).

## Codified lessons

Three new rules landed in the shared list.

### 34. Audit before refactoring; refactor before schema-changing

Ship 69'.a's 200-LOC classifier answered the scoping question in
one pass. Before the audit, the natural plan would have been
"refactor all 452 edges." After: "50 easy, 13 need micro-work, 168
need UX-only work, 221 need nothing." That's a completely
different arc — and only one sub-arc (69'.c) needed to touch a
runtime code path.

### 35. Data model changes ripple through readers designed for the OLD topology

Ship 59'.e's *self-contained sub-clause attribution* filter was
right for the topology at the time (bridges targeted whole
articles). Ship 69'.b made bridges point at sub-clauses AND the
same reader needed a parent-article union to preserve the parent-
Evidence-Package UX. Reader wasn't wrong — it was pinned to an
assumption that moved when the graph did.

Also: infrastructure that anticipates topology makes downstream
arcs cheap. Ship 59'.e's ref-parse fallback made 69'.d's 12 new
stubs Just Work — zero runtime code change.

### 36. Read-time parse before schema

Ship 69'.c surfaced dimensions from curator rationale without a
column, loader, or migration. When enrichment lives entirely
inside existing prose, the parser is faster to ship AND cheaper
to iterate on. Vocabulary changes = one-file edit; column changes
= migration + backfill + retest. Persist the extracted structure
only once a consumer needs to *filter*, not just *render*.

## What's NOT locked in but should be

Two carry-forwards to future arcs, captured here so a future
session picks them up:

- **Second-choice retarget targets.** Ship 69'.b's retargeter
  picks the FIRST narrower ref from `narrower_refs_have_nodes`.
  For rationales that name multiple (e.g. `B.8.5.7` → both
  `Art.28.2` and `Art.28.3.d`), the second-choice ref is
  unclaimed. Ship 69'.d created the stub node but no edge
  currently points at it. Future move: allow the catalog to
  author *multiple parallel edges* (one per named sub-clause)
  or use `scope_items` (Ship 68'.a) to distinguish per-MUST
  pairs.

- **Dimension vocabulary expansion.** Ship 69'.c's controlled
  vocab has ~35 tokens; the audit found dimension mentions in
  ~45% of rationales, but the extractor recognizes only what's
  in the map. Auditing the ~50% unrecognized rationales for
  common tokens (e.g. "notice", "consent", "records") would
  extend coverage. Cheap follow-up when a specific auditor
  question surfaces missing dimensions.

## What's parked

- **Task #595** — 22 tenant-facing GDPR articles (Art.11, Art.23,
  Art.27, Art.31, Art.39, Art.40-43, Art.77-82, Art.84, Art.86-91)
  currently carry NO ISO bridge edge. Ship 68'.a's dogfood surfaced
  this as a coverage gap; distinct from the Ship 69' precision work
  because these articles need *authoring*, not *retargeting*.
  Separate arc, curator triage.

- **Task #577** — leaf-detail actionable guidance rework. Parked
  from Ship 57 pre-Ship-59 arc.

## Session shape

The four-sub-arc-in-one-day cadence matches the pattern from
Ships 30/31/32 (short data-driven arcs anchored on a
measurement CSV). What made this arc even cheaper:

- The tooling from 68'.a (scope_items schema — dormant but
  intact) was ready to receive 68'.b's honest UX.
- The audit CSV from 69'.a was the single input for both 69'.b
  and 69'.d retargeters.
- The stub roll-down from Ship 59'.e absorbed 69'.d's 12 new
  stubs with no code changes.
- The dimension parser in 69'.c is 130 LOC because the
  vocabulary was already inventoried by the audit.

Composability wins over centralization. Ship 68'.a's dormant
schema, Ship 59'.e's stub roll-down, Ship 68'.b's honesty gambit,
the Ship 69'.a audit — each was a small artifact that this arc
combined into precision improvements.
