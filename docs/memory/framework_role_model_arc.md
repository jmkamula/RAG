---
name: framework-role-model-arc
description: Design + Phase 1 shipped for the framework role model (PROGRAM/EXTENSION/OBLIGATION); replaces peer-bridges as the multi-framework architecture
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Multi-framework architecture refactor kicked off 2026-07-05 after
observing that the LLM extracts under a "27001 gravity well" bias
(Privacy Policy Arion produced 30 findings all on 27001 + 28 xfw
proposals to GDPR/27701 despite being privacy-primary content).

## Design (2026-07-05 conversation)

The three in-scope standards do NOT stand as peers. Their real
relationship is hierarchical:

    GDPR (law — what regulators enforce)
      ▲
      │ demonstrated-by
      │
    ISO 27701 (PIMS overlay — privacy extension)
      ▲
      │ extends (per ISO 27701 §4.1)
      │
    ISO 27001 (ISMS spine — baseline security)

Model generalises to 20+ frameworks with three role values:

- **program** — standalone management-system / attestation framework
  (ISO 27001, SOC 2, HITRUST, TISAX, NIST CSF)
- **extension** — extends a PROGRAM for a specific subject; requires
  ≥1 PROGRAM (ISO 27701, 27017, 27018)
- **obligation** — legal/regulatory/contractual mandate; not a
  management system itself; demonstrated-by PROGRAM + EXTENSION
  (GDPR, CCPA, NIS2, DORA, EU AI Act, HIPAA Privacy Rule, PCI DSS)

Plus **guidance** for code-of-practice companions (ISO 27002).

Two orthogonal axes on each standard:

- **subject** (list) — what content domain: `information_security`,
  `privacy`, `cloud`, `payment`, `health`, `financial`, `automotive`,
  `ai_governance`, `resilience`, `financial_reporting`
- **scope_type** — `org_wide` / `data_type_scoped` / `sector_scoped` /
  `system_scoped`
- **mandate_source** — `voluntary` / `attestation` / `legal` /
  `contractual`

Handles stress-test frameworks cleanly: SOC 2 (parallel PROGRAM to
27001), NIS2 (prescriptive OBLIGATION with own leaves), PCI DSS
(PROGRAM with scope filter), HITRUST (PROGRAM with inherits_from),
EU AI Act (OBLIGATION, new subject).

## Why (design conversation)

Bridges are the wrong primitive when the relationship is
hierarchical. A Privacy Policy isn't "27001 with GDPR/27701 bridges"
— it's fundamentally a 27701 §A.7.3.2 artifact that happens to also
demonstrate GDPR Art.13 (by design) and touches 27001 A.5.34 as a
side effect. The LLM's 27001 gravity well is the natural output of
treating co-equal standards. Role model turns propagation from LLM
inference into deterministic routing.

## Phase 4b shipped 2026-07-05 (role-band dashboard headers)

- **api_server.py** `/api/v1/dashboard/posture` — response
  frameworks now carry `role` + `subject` fields (looked up from
  the standards table in a single batch query with silent fallback).
  Frameworks re-ordered by role rank (program → extension →
  obligation → guidance) then by legacy standard rank as tiebreak.
- **static/arioncomply.html** — `renderDashboard` emits a
  role-band header (indigo left-bar chip) each time the role
  transitions in the framework iteration. Copy is tenant-friendly:
  "Programs — your ISMS spine…", "Extensions — overlays on top of
  a program…", "Obligations — legal / regulatory requirements
  demonstrated by your programs + extensions". Backfill-missing
  role → header suppressed (no visible degradation).
- Deliberately kept the linear scrollable layout instead of
  role-tabs — tenants want to see the whole compliance stack
  at once; the band headers make the hierarchy visible without
  hiding rows behind clicks.

## Phase 5 shipped 2026-07-05 (xfw_proposer fallback-only)

- **rag/intake/xfw_proposer.py** — `_walk_bridges` now also returns
  `src_role` and `tgt_role` (populated by Phase 1's role_owner
  backfill). Both call sites — `propose_for_findings` (per-upload)
  and `propose_backfill` — skip target proposals where source is
  PROGRAM/EXTENSION and target is OBLIGATION. That direction is
  now handled deterministically by DEMONSTRATES propagation in
  posture_loader (Phase 2b/2c); double-writing produces a
  redundant Stage-1 xfw_bridge finding for a relationship that's
  already surfaced as an in-memory posture overlay + drill-in
  provenance (Phase 4a).
- Kept directions:
    - OBLIGATION → PROGRAM (reverse navigation surface, useful for
      "which ISO controls implement this GDPR article")
    - PROGRAM ↔ PROGRAM (future SOC 2 ↔ ISO 27001 peer bridges)
    - PROGRAM ↔ EXTENSION (extension curation coverage)
- Existing pending xfw_bridge findings in Stage-1 stay valid; the
  filter applies only to newly-proposed rows from Phase 5 onward.
- Safety note: Phase 5's filter assumes 1:1 correspondence between
  IMPLEMENTS/SUPPORTS PROGRAM→OBLIGATION edges and DEMONSTRATES
  edges — established by Phase 2a's seed. Any new IMPLEMENTS
  edges added AFTER seed_demonstrates_edges.py runs need a
  re-seed (idempotent) to maintain coverage.

## Phase 4a shipped 2026-07-05 (demonstrated-by drill-in provenance)

- **api_server.py** — new endpoint
  `GET /api/v1/dashboard/control/{control_ref}/demonstrated-by`
  returns the list of PROGRAM/EXTENSION sources contributing to an
  obligation, with each source's current finding + rationale, plus
  `propagated_finding`, `current_finding`, and `materialised` flag.
  Reads from tenant_context.posture (already populated by Phase 2b/2c).
- **static/arioncomply.html** — `selectHeatCell` now fetches the
  new endpoint after the advisory panel and renders a
  "Demonstrated by" section via `renderDemonstratedByPanel()`.
  Section shows per-source ref, humanized standard label, current
  finding pill, and "→" drill-into-source link. Materialised
  obligations get an "auto-inferred" tag so the tenant can
  distinguish propagated postures from their own assessments.
- Silent fallback: if the endpoint returns `demonstrated_by: null`
  (non-obligation control, cache unavailable, etc.), the panel is
  simply not rendered — no visible degradation.

Deferred to Phase 4b (three-lens dashboard restructure): grouping
the heatmap by role (Programs / Extensions / Obligations) or by
subject. The drill-in surface delivers the auditor value that
Phase 2b/2c metadata was blocked on; the dashboard grid restructure
is a bigger UX change worth its own eval baseline.

## Phase 3 shipped 2026-07-05 (role-aware extraction)

- **rag/intake/doc_pipeline.py** — `_get_controls` gained a
  `_filter_demonstrated_obligations` post-load step. Any OBLIGATION
  RequirementNode whose DEMONSTRATES source is in the tenant's
  PROGRAM/EXTENSION scope is excluded from the LLM candidate list.
  Those get propagated deterministically at posture-load time via
  Phase 2b/2c overlays.
- OBLIGATIONs WITHOUT a demonstrator remain in the LLM candidate
  set. Direct extraction still works for pure-legal content
  (Art.1-4 definitions/scope, Art.7 consent mechanics, Art.11.x,
  Art.13.1.a-d sub-obligations that don't have curated
  DEMONSTRATES coverage yet).
- Silent fallback: any Neo4j failure returns the unfiltered list;
  Phase 3 is an overlay, not a hard dependency.
- **On Arion:** 51 GDPR obligations excluded (matches the 51
  RequirementNodes with DEMONSTRATES sources). LLM candidate set
  478 → 427 controls. The A-strategy multi-framework prompt
  (2026-07-05, commit ae37566) is preserved — it still helps the
  LLM correctly bind PROGRAM/EXTENSION overlaps (e.g. A.5.15 +
  B.8.5.1 for identity-management privacy overlay).

## Phase 2c shipped 2026-07-05 (finding-level materialisation for gaps)

- **rag/posture_loader.py** — `_apply_demonstrates_overlay` upgraded
  to also materialise obligation postures that are 'Not assessed'
  in `posture_controls` but have positive DEMONSTRATES sources. A
  new SQL helper `_fetch_not_assessed_obligation_rows` pulls those
  rows on demand (the main `load_posture` query still filters
  Not-assessed out, keeping the fast path fast).
- Materialised rows carry `source='demonstrates_propagation'` +
  `finding` = propagated aggregate + a `gap_description` explaining
  the propagation. Distinguishable from tenant-authored postures.
- **Rule preserved:** propagation only fills gaps. Tenant-asserted
  postures (any finding other than 'Not assessed') keep their
  finding untouched; the demonstrated_by metadata attaches for the
  UI to surface as auditor context.
- **On Arion:** 4 materialisations (Art.32.1.b, Art.32.1.d,
  Art.32.2, Art.32.4 — all Security-of-processing sub-articles),
  all OFI from partial ISO 27001 demonstration. GDPR obligation
  count grew 53→57; total posture rows 226→230. 33 tenant-asserted
  NC obligations left untouched despite having positive
  demonstrators (correct per rule).

## Phase 2b shipped 2026-07-05 (additive metadata overlay)

- **scripts/seed_demonstrates_edges.py** — creates DEMONSTRATES
  edges from every PROGRAM/EXTENSION → OBLIGATION relationship in
  the existing cross-framework catalog. 235 edges seeded:
  - ISO27001 → GDPR: IMPLEMENTS(90) + SUPPORTS(41) + ENABLES(11)
    + GOVERNANCE(7) = 149
  - ISO27701 → GDPR: IMPLEMENTS(86) = 86
  Idempotent via MERGE on (source, target, via_edge). Direction
  enforced: source.role_owner ∈ {program, extension} AND
  target.role_owner = obligation.
- **rag/posture_loader.py** — `_apply_demonstrates_overlay()`
  reads the DEMONSTRATES map from Neo4j and attaches
  `demonstrated_by` (list of contributing sources with their
  findings) + `propagated_finding` to obligation posture records.
  Aggregation: all sources Comply → Comply; any Comply/OFI → OFI;
  else no propagation. Top-level `finding` is NOT modified (Phase
  2c will flip it for Not-assessed obligations); this is a pure
  metadata overlay so downstream consumers (Phase 3 extractor +
  Phase 4 UI) can read the provenance without any user-visible
  behavior change.
- On Arion: 44 GDPR articles enriched — 33 propagate to OFI (27701
  overlay partially demonstrates), 11 have only-NC demonstrators.

Reverse GDPR→ISO edges (125 total) stay untouched — they are the
auditor navigation direction, not demonstration. ISO27701 →
ISO27001 SUPPORTS edges (26) stay untouched — those are the
`extends` relationship at the control level.

## Phase 1 shipped 2026-07-05 (no behavior change)

- **schema_v60_standards_role_model.sql** — adds `role`, `subject`
  (text[]), `scope_type`, `mandate_source` columns to `standards`.
  Backfills all 6 rows in the existing registry
  (ISO27001/27002/27701/27018, GDPR, NIST-CSF).
- **rag/scope_loader.py** — `StandardInfo` dataclass gets role /
  subject / scope_type / mandate_source fields. `TenantScope` gets
  `programs` / `extensions` / `obligations` role-grouped accessors
  and `subjects_in_scope()`.
- **scripts/backfill_neo4j_subject_role.py** — one-shot pass that
  writes `role_owner`, `subject`, `scope_type`, `mandate_source`
  properties onto every RequirementNode + EvidenceRequirement based
  on `standard_id`. 1322 nodes tagged across the 3 in-scope
  standards (ISO27001: 598, ISO27701: 245, GDPR: 479).

Existing registry infrastructure already had `standards`,
`standard_relationships`, `tenant_standards`, `applicable_standards`,
`tenant_evaluation_scope` view — much of the plumbing existed and
just needed role metadata layered on. `standard_type` (existing:
management_system / regulation / framework / code_of_practice) is
ORTHOGONAL to `role` — 27701 is `standard_type=management_system`
AND `role=extension` because it's an ISMS extension that only exists
on top of another ISMS. Both columns coexist.

## Operator note

Until Phase 3 folds subject/role_owner into the Python catalog, the
Neo4j backfill script must be re-run after every
`load_to_neo4j.py` execution (idempotent; safe to re-run).

Related memory:
- [[framework-role-taxonomy-2026-07-05]] — vocabulary + subject list
- [[framework-role-api-compatibility-decision]] — API contract
  deferred as a "fight for another day" per user
- Phase 2+ will add DEMONSTRATES edges + retire xfw for obligation
  propagation; Phase 3 role-aware extraction + Phase 4 UI three-lens
  + Phase 5 xfw retire
