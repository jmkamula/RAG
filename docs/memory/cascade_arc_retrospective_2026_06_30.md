---
name: cascade-arc-retrospective-2026-06-30
description: "SHIPPED 2026-06-27→2026-06-30 (13 commits / 24 slices including S4+S7 closure): cascade arc + relationship catalog migration sequence both complete. All 10 cascade-meditation patterns implemented + 505 typed edges in relationship_catalog across 11 edge types (286 cross-framework migrated via S4 + 214 intra-framework authored S5/S6 + 5 BLOCKS_WHEN) + cascade vocabulary with 53 events + cascade engine + 23 API endpoints + 7 UI surfaces. xfw_proposer (S7) now uses catalog rationale in bridge excerpts. Engine grew from 0 to ~1900 lines; eval stayed at 197/199 floor across every commit. KEY LESSON: audit before design — relationship-model audit revealed 70% of cascade was already built; the actual gap was intra-framework structural edges + operational events + tenant-side implications surface. Full retrospective in docs/cascade_arc_retrospective_2026_06_30.md. SECONDARY DELIVERABLE: load_graph_relationships.py cross-framework section deprecated; relationship_catalog is now the single source of truth for typed edges. Data-quality follow-up filed: 12 source-JSON edges target ISO 27001:2013 refs (A.9.x, A.4.1) that need 2022 renumbering."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What this is

Retrospective + index for the cascade arc that ran 2026-06-27 to
2026-06-30. Covers what shipped, what landed differently than
designed, lessons, deferrals, carry-forward insights.

## Arc summary

- **S1**: relationship_catalog.py scaffolding + loader + validator (zero edges)
- **S5**: 50 intra-GDPR edges (Art.6 → Art.7, Art.33 → Art.34, etc.) authored from GDPR text + EDPB guidelines
- **S6 ×3**: 160 intra-ISO edges across 27 clusters (identity lifecycle, incident family, BCP pair, records protection, classification cascade, etc.) cited against ISO 27002:2022 §X.Y
- **S2a**: 40 new operational Events (personnel/IAM/asset/supplier/ISMS lifecycle) with 5 meta-cascade fields on Event dataclass
- **S2b**: events loader extended for 5 new edge types (EMITS_EVENT, EXPECTS_FOLLOWUP_EVENT, UPDATES_FACT, EXPANDS_SCOPE, CASCADES_REVIEW); BLOCKS_WHEN added to relationship_catalog managed types
- **S2c**: structured_events JSONB on verification log + verify endpoint validation + UI categorised picker
- **S3**: triggered_implication table + cascade engine + walk_cascade BFS + GET/PATCH endpoints + dashboard panel
- **S3b**: expected_followup_event table + CASCADES_REVIEW handling + sweep
- **S3c**: UPDATES_FACT writes client_facts + EXPANDS_SCOPE emits review_required impls
- **S3d**: applies_when evaluator (== / != / truthy) for EMITS_EVENT
- **S3e**: cascade → posture overlay (compute_cascade_pressure + propose_from_cascade)
- **S3f**: followup-overdue → SLA-breach implication propagation
- **S3g**: requires_effectiveness_proof on closure events
- **S3h**: optional occurred_at on structured_events + clock_anchor column
- **S3i**: 5 BLOCKS_WHEN edges + engine consultation + suppression_kind='blocks_when'
- **S3j**: per-event aggregation_threshold + rolling-window count from JSONB → synthetic threshold event
- **S3k**: per-control implications in LLM context (load_per_control_implications + context_assembler integration)
- **S3l**: cascade chat surface — 3 short-circuit predicates (impl/followup/suppression queries) + CLEAR_INTENT_PHRASES
- **S3m**: auto-resolve-via-cite (effectiveness_evidence in metadata resolves prior open impls on TRIGGERS_OBLIGATION targets)
- **S3n**: per-tenant cascade overrides (mute_event / mute_event_target)
- **S3o**: dashboard cascade KPIs (5 tiles)
- **S3p**: implications drill-in on heatmap cell detail
- **S3q**: cascade timeline page (verifications ∪ implications ∪ followups ∪ suppressions)
- **S3r**: cascade-override admin UI on Profile page
- **S3s**: bulk resolve UI + bulk endpoint
- **S3t**: in-app notifications (schema_v59 + 4 write sites + bell + inbox page)
- **S3u**: cascade event detail modal (focal + related chains)

## All 10 cascade-meditation patterns implemented

P1 EMITS_EVENT · P2 EXPECTS_FOLLOWUP · P3 UPDATES_FACT · P4 EXPANDS_SCOPE
P5 aggregation · P6 BLOCKS_WHEN · P7 clock attribution · P8 effectiveness proof
P9 depth cap · P10 implication grouping

## Key non-obvious takeaways

### The audit insight

Before this arc started, Arion already had 17 typed edges in
Neo4j (DERIVED_FROM/MUST_CONTAIN/...) including 4 cross-framework
edge classes (IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE with
274 edges) + 11 Event nodes + 22 ClientFacts + 18 ObligationRules
+ existing TRIGGERS_OBLIGATION mechanism (44 edges). The 30-min
[audit](docs/relationship_model_audit_2026_06_29.md) revealed the
cascade was 70% built. We extended rather than rebuilt.

### Catalog discipline

Two declarative files run the cascade:
- `enrichment/relationships/relationship_catalog.py` — 219 edges
  total (54 GDPR + 160 ISO + 5 BLOCKS_WHEN). Each carries citation
  + applies_when + role.
- `enrichment/events/event_nodes.py` — 53 events with
  triggers + emits_events + expects_followups + updates_facts +
  expands_scope + cascades_review + requires_effectiveness_proof
  + aggregation_threshold/period/emits.

Engine code reads these, never embeds rules.

### The 10-pattern meditation

The 2026-06-29 domain-by-domain walk (personnel → IAM → asset →
supplier → management-system lifecycle) surfaced 10 patterns no
single domain reveals alone. P1 (events emit events) + P3
(profile-fact updates) + P5 (aggregation) wouldn't have been
captured by listing 8 HR events. This **5-domain × 10-pattern**
deliberation method is reusable for next big design.

### Eval-stable forward motion

22 logical slices, each individually smoke-tested + eval'd, every
commit at or above the 197/199 floor. No rollbacks. The
discipline of "commit when eval passes" forced each slice to be
genuinely additive (no engine regression possible).

### Auto-resolve closures > deletes

triggered_implication / expected_followup_event / cascade_
suppression_log / client_fact_change_log / tenant_notification
are all **append + state-transition only**. No row is ever
deleted. Auditor sees full lifecycle. Same applies to
tenant_cascade_override (is_active soft-delete).

### Latent bug found mid-arc

S3l surfaced `get_logger()` returning None when chain logging
wasn't enabled, with bullet-drop guard calling `.warning()` on
it. Fixed with `_NullLogger` fallback. Bug had probably existed
unnoticed for months — short-circuit-heavy paths flushed it out.

## What's deferred (intentional)

- Recompute semantics for UPDATES_FACT (needs per-fact source-of-
  truth queries; today: observational only)
- Email/Slack notification provider (in-app works; outbound is v2)
- Periodic sweep scheduler (on-demand only; cron/worker invocation
  is v2)
- Verification trends sparklines (KPI tiles cover the now)
- Cross-tenancy cascade (single-tenant only; the meditation
  deferred this explicitly)

## Update (2026-06-30 evening) — S4 + S7 closed

Retrospective above was written between S3u and S4. Both
remaining migration-sequence steps shipped that same evening:

- **S4** — 286 cross-framework edges migrated from source JSONs
  into XFW_EDGES; all 274 Neo4j-resident edges tagged
  managed_by='relationship_catalog'; `load_graph_relationships.py`
  cross-framework section marked deprecated. 12 dropped edges
  reference ISO 27001:2013 numbering (filed as data-quality
  follow-up).
- **S7** — `_walk_implements` returns rationale; new
  `_compose_bridge_excerpt` produces `[Bridge: <rationale>] <src>`
  on xfw_bridge proposals so auditor sees WHY the cross-framework
  link applies.

**Migration sequence COMPLETE.** Catalog owns 505 typed edges
(286 xfw + 54 GDPR + 160 ISO + 5 BLOCKS_WHEN) across 11 edge
types. relationship_catalog is the single source of truth.

### Data-quality follow-up filed

12 dropped source-JSON edges target stale ISO 27001:**2013** refs
(A.9.1/A.9.3 renumbered to A.5.15/17/18 in 2022; A.4.1 doesn't
exist in 2022; one A.6.1.2 typo). Fix in
`iso_nodes_phase1.json` + `gdpr_nodes_phase2.json` then re-run
`scripts/extract_xfw_to_catalog.py` to regenerate. Not blocking.

## Carry-forward insights

1. **Always audit existing infrastructure before designing the next thing.**
2. **Author catalogs declaratively; keep engine rules out of code.**
3. **Bundle slices in commits when they're additive output handling.**
4. **Eval-stable forward motion beats batching.**
5. **The meditation pattern (5 domains × 10 patterns) translates to other domains.**

## Files

- `docs/cascade_arc_retrospective_2026_06_30.md` — full retrospective
- `docs/relationship_model_audit_2026_06_29.md` — what existed
- `docs/relationship_model_design_2026_06_29.md` — what we proposed
- `docs/cascade_implications_2026_06_29.md` — the 10 patterns
- 11 commits on `main` since 6b6aa4b

## Related memory

- [[product-concept-evidence-cascade-2026-06-27]] — original idea
- [[relationship-model-audit-design-2026-06-29]] — the framing reset
- [[cite-mode-v1-backend-2026-06-27]] — verification substrate
- [[dashboard-cite-freshness-card-2026-06-27]] — sibling surface

The cascade engine is feature-complete relative to the 2026-06-29
meditation. Next big arcs can build ON top — recompute semantics,
outbound notifications, scheduler, anomaly detection — without
reshaping the foundation.
