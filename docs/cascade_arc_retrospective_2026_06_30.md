# Cascade Arc — Retrospective

**Span:** 2026-06-27 → 2026-06-30
**Commits:** 11 (compressing ~22 logical slices)
**Status:** Cascade engine + UX complete

## The arc in one paragraph

What started as "build the evidence cascade feature" on 2026-06-27
turned into a re-grounding exercise that uncovered the system
already had ~70 % of the cascade infrastructure — 17 typed edges,
11 Events, 4 cross-framework edge classes — and that the real gap
was intra-framework structural edges (669 prose-only mentions in
curation memos). Once that frame landed, the work bifurcated:
**relationship catalog** (S1, S5, S6) authored ~210 edges over
3 sessions, then **cascade engine v1** (S2a/b/c → S3 → S3b…S3u)
shipped all 10 cascade-meditation patterns plus the UX layer
required to make them usable. The eval suite stayed at the 197/199
floor across every commit, and the engine grew from "0 lines" to
"~1900 lines + 23 API endpoints + 7 UI surfaces" without breaking
any prior path.

## Timeline

| Date | Commit | Slices | What |
|---|---|---|---|
| 2026-06-27 | (prior) | — | Product principle + cascade concept memos written |
| 2026-06-29 | 6b6aa4b | S1 + S5 | Relationship catalog scaffolding + 50 intra-GDPR edges |
| 2026-06-29 | 532ddf9 | S6 ×3 | 160 intra-ISO edges across 27 clusters |
| 2026-06-29 | a5418fa | S2a + S2b | Cascade vocabulary (40 new Events) + 6 meta-cascade edge types |
| 2026-06-29 | 363b727 | S2c+S3+S3b+S3c+S3d | Full cascade engine v1 (verify schema, triggered_implication, followup enforcement, fact + scope, applies_when) |
| 2026-06-29 | ae0fb46 | S3e | Cascade → posture overlay (observability + Stage-2 PA proposal) |
| 2026-06-29 | ccfc94c | S3f | Followup-overdue → SLA-breach implication propagation |
| 2026-06-30 | a36a037 | S3g | Effectiveness proof (P8) on closure events |
| 2026-06-30 | fa30e13 | S3h + S3i | Clock attribution + BLOCKS_WHEN suppression |
| 2026-06-30 | c27d65e | S3j | Thresholded aggregation (P5) — last unimplemented meditation pattern |
| 2026-06-30 | cae5e48 | S3k+S3l+S3m+S3n | Engine integration polish (chat context, chat surface, auto-resolve-via-cite, per-tenant overrides) |
| 2026-06-30 | 021f4e0 | S3o..S3u | UX layer (KPIs, drill-in, timeline page, override admin UI, bulk resolve, notifications, event detail) |

## The 10 meditation patterns — final disposition

The 2026-06-29 [cascade implications meditation](cascade_implications_2026_06_29.md)
surfaced 10 cross-cutting patterns. Final state:

| # | Pattern | Status | Where |
|---|---|---|---|
| P1 | Events emit events | ✓ Shipped | EMITS_EVENT edges + walk_cascade BFS (S3) |
| P2 | Missing-event detection | ✓ Shipped | EXPECTS_FOLLOWUP_EVENT + sweep + SLA-breach impl (S3b, S3f) |
| P3 | Profile-fact updates | ✓ Shipped | UPDATES_FACT + client_facts mutation + log (S3c). Recompute observational only |
| P4 | Scope expansion | ✓ Shipped | EXPANDS_SCOPE + review_required impls + scope_kind tag (S3c) |
| P5 | Thresholded aggregation | ✓ Shipped | Per-event aggregation_threshold + rolling-window count from JSONB (S3j) |
| P6 | Negative cascade | ✓ Shipped | BLOCKS_WHEN catalog edges + engine consultation + suppression log (S3i) |
| P7 | Clock attribution | ✓ Shipped | Optional occurred_at on structured_events + clock_anchor column (S3h) |
| P8 | Effectiveness proof | ✓ Shipped | requires_effectiveness_proof Event field + closure_proof_missing impls (S3g) |
| P9 | Depth cap | ✓ Shipped | MAX_DEPTH=4 in walk_cascade BFS + cycle detection via visited set (S3) |
| P10 | Implication grouping | ✓ Shipped | Group-by-source_verification_id + bulk resolve UI (S3, S3s) |

All 10 patterns are now data + engine + (where applicable) UI surfaces.

## What landed differently than designed

### 1. The cascade vocabulary doubled

The original [evidence cascade memo](memory/product_concept_evidence_cascade_2026_06_27.md)
proposed 8 operational events. The meditation surfaced a missing
fifth domain (management-system lifecycle) and bumped the count to
~40. We shipped 53 events total (11 existing + 42 new). The
extra vocabulary cost was small (each event is ~30 lines of dataclass)
but the cascade behaviour got dramatically richer — `policy_revised`
fires A.6.3 retraining + A.5.36 compliance check; `production_deployment`
gates 4 controls; `consent_withdrawn` emits `event:erasure_request`.

### 2. Engine became 23 API endpoints

Original design memo §10 envisioned 3 sessions for cascade-v1:
schema + engine + minimal UI. We shipped 22 slices across 4 days
because each behaviour surfaced a small API need: list this, patch
that, bulk-resolve here, drill into there, mark-read this. Most
slices fit under 200 lines; cumulatively they form a usable surface.

### 3. Memory's role on this arc

Five `cascade_*_2026_06_*` memory entries weren't planned at outset
but accreted naturally as the arc progressed. They preserved the
non-obvious decisions across sessions — especially the
[relationship model audit](relationship_model_audit_2026_06_29.md)
and [cascade implications meditation](cascade_implications_2026_06_29.md)
both became reference docs that subsequent slices read back from.

### 4. The UX layer was a separate commit

S3o through S3u (the UX layer) shipped as one bundle, but
internally each took ~30-60 minutes of work. Splitting into a
single commit per slice would have produced 7 small commits;
bundling them produced 1 large commit with a clean narrative.

## Lessons from the arc

### L1. Audit before designing

The relationship-model design started as "let's design cascade".
The user's question — *"what's our reference to make sure the
model is solid and exhaustive?"* — forced a 30-minute audit pass
that revealed 70 % of the cascade infrastructure already existed
(`TRIGGERS_OBLIGATION` edges, `Event` nodes, `mandatory`/`deadline`/
`rationale` properties). The design memo shrank from "build cascade
subsystem" to "extend existing graph + add implications surface."

### L2. Authoring catalog beats hard-coded rules

The intra-framework edges (S5 + S6, 214 edges) and operational
events (S2a, 40 events) were authored as **declarative Python
data**. Each entry is a 5-15 line `RelationshipEdge` or `Event`
constructor with citation, applies_when, role, etc. Reviewable in
PRs, version-controlled, validated by the harness, loaded into
Neo4j idempotently. Compare against the original `xfw_bridge` /
`DerivedSpec` / curation-memo-prose / cascade-trigger-catalog
fragmentation: one source of truth, four loaders, zero rules
written inline in engine code.

### L3. Engine extension via uniform pattern

Every cascade engine slice followed the same shape:
- Schema migration for any new state
- Engine function added or extended in `rag/cascade/engine.py`
- API endpoint(s) surfacing the new output
- Optional UI consumer
- Smoke test
- Eval (always ≥197/199)
- Commit

Six slices reused this shape across 4 days. The repetitiveness
was a feature, not a bug.

### L4. Auto-resolve > auto-deletion

Multiple write paths (`status='satisfied'` via cite verify,
`status='dismissed'` via PATCH, `status='overdue'` via due_date)
preserve audit-grade history. No row is ever deleted from
`triggered_implication`; closure is a state transition. Same for
`tenant_notification` (read/dismissed_at columns) and
`tenant_cascade_override` (is_active soft-delete). Auditor sees
the full lifecycle without needing change-tracking infrastructure.

### L5. Bug fix during the arc

S3l surfaced a latent `get_logger()` bug — the existing
`polish_short_circuit_answer` was calling `.warning()` on a
possibly-None return. We added a `_NullLogger` fallback. The bug
had probably existed for months but only fired when bullet-drop
detection ran on long short-circuit answers. Arcs that build new
short-circuit paths flush out these.

## What's deferred (and why)

| Deferred | Why |
|---|---|
| Recompute semantics for UPDATES_FACT | Needs source-of-truth query layer per fact (HR row count for headcount, etc.). Today: observational only — change logged but column unchanged for `recompute`. |
| Email/Slack notification provider | In-app notifications work; outbound delivery needs SMTP/webhook config + per-tenant subscription model. Not blocking adoption. |
| Periodic sweep scheduler | `sweep_overdue_followups` is on-demand. Production would want a cron/background-worker invocation. Can be added when first real tenant comes onboard. |
| Verification trends sparklines | KPI tiles cover the now; trends-over-time is a v2 feature. |
| Cross-tenancy cascade | The 2026-06-29 meditation explicitly deferred this. All current logic is single-tenant scoped. |

## Carry-forward insights for the next big arc

1. **Always audit existing infrastructure before designing the next thing.**
   The cascade arc would have been 3× larger if we'd built it from
   scratch instead of recognizing the existing 17-edge typed graph.
2. **Author catalogs declaratively. Author no engine rules inline.**
   The relationship_catalog.py + event_nodes.py patterns make
   curation reviewable. Engine code stays small.
3. **Bundle slices in commits when they're additive output handling.**
   The single commit `021f4e0` covers 7 slices = ~1700 lines of
   read-side polish. Single-slice commits would have made the same
   work 7× as much git history without proportional information
   gain.
4. **Eval-stable forward motion is faster than batching.**
   22 small slices, each smoke-tested + eval'd individually,
   shipped faster than three "big bang" releases would have.
   Every commit was deployable. No rollbacks.
5. **The meditation pattern translates well to other domains.**
   The 10-pattern format (P1...P10 with cross-cutting concerns)
   could be reused for any next big design. Recommended.

## Pointer to the corpus

- [Relationship model audit](relationship_model_audit_2026_06_29.md) — what existed before we started
- [Relationship model design](relationship_model_design_2026_06_29.md) — what we proposed
- [Cascade implications meditation](cascade_implications_2026_06_29.md) — the 10 patterns + 5 domains
- 11 commit messages on git log, each with detailed before/after
- ~10 memory entries under `docs/memory/` keyed `cascade_*`

The cascade engine is now ready for tenant use.
