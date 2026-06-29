---
name: relationship-model-audit-design-2026_06_29
description: "DESIGN 2026-06-29 (no code): two-doc pair sets the unified relationship-model foundation. AUDIT (docs/relationship_model_audit_2026_06_29.md) inventories what's already in Neo4j — 17 typed edges, 11 Events, 22 ClientFacts, 18 ObligationRules, 4 cross-framework edge classes (IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE) with 274 edges, 15 DerivedSpecs, 669 intra-framework cross-control pairs mentioned in curation memos as prose-only. DESIGN (docs/relationship_model_design_2026_06_29.md) proposes 6 NEW intra-framework edge types (PAIRS_WITH/PREREQUISITE_OF/ESCALATES_TO/CASCADES_FROM/FEEDS_INTO/AUDITED_BY) + 8 new operational Events (HR/asset/IAM) + triggered_implication table + relationship_catalog.py authoring file + load_to_neo4j sync + validation harness + 7-step migration sequence (S1-S7). Cascade is now framed as a small extension to a 70%-built model, not a new subsystem."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What this captures

A re-grounding moment. The "evidence cascade" feature concept
([[product-concept-evidence-cascade-2026-06-27]]) was about to be
built as a new subsystem with new event vocabulary + trigger
catalog + implications surface. User asked first-principles:
generalize across intra-framework AND cross-framework AND
multi-standard — and pin against published references.

The audit revealed Neo4j ALREADY has substantial relationship
infrastructure. Cascade is a small extension, not a new layer.

## The two documents

### Audit (audit doc)

Inventories what's there now:

- **17 typed edges in Neo4j** — DERIVED_FROM (4305), MUST_CONTAIN
  (3409), SHOULD_CONTAIN (897), REQUIRES_EVIDENCE (651),
  HAS_TEMPLATE (648), SATISFIED_BY (429), IMPLEMENTS (168),
  REQUIRES_EVIDENCE, SUPPORTS (76), REQUIRES_CONTROL (63),
  TRIGGERS_OBLIGATION (44), DERIVES_FROM (40), TRIGGERS (27),
  PART_OF (26), ENABLES (22), ALLOWS (11), MANIFESTS_AS (11),
  GOVERNANCE (8).
- **4 typed cross-framework edge classes** with 274 edges total
  (IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE) covering ISO↔GDPR
  bidirectionally.
- **15 DerivedSpecs** in `document_requirements.py` (composition
  layer; 40 DERIVES_FROM edges in graph; each carries `role` tag).
- **11 Event nodes** covering compliance-lifecycle (DSAR, breach,
  audit, new processing, supervisory inquiry). NO operational
  events.
- **22 ClientFacts + 18 ObligationRules + ALLOWS/MANIFESTS_AS
  classification taxonomy** — applicability + incident taxonomy
  layers already complete.

The gap is THREE specific things:

1. **Intra-framework relationships are prose-only.** 669 unique
   focal-other ref pairs across the 30 curation memos
   (`curation_phase_b_batch_*.md`). None are typed edges in
   Neo4j. The 4 cross-framework edge classes only link nodes from
   different standards.
2. **No operational world events.** All 11 Events are
   compliance-lifecycle; missing HR/asset/IAM lifecycle events
   that PRECEDE compliance events.
3. **No tenant-side event emission** from cite verifications +
   no implications-tracking surface.

### Design (design doc)

Proposes the unified model in 15 sections:

- **6 NEW intra-framework edge types** (RequirementNode →
  RequirementNode), OSCAL-aligned naming:
  - `PAIRS_WITH` (symmetric lifecycle pairing — e.g. A.5.16↔A.5.17)
  - `PREREQUISITE_OF` (asymmetric — e.g. A.5.9 → A.5.12)
  - `ESCALATES_TO` (e.g. A.5.25 → A.5.26 → A.5.27)
  - `CASCADES_FROM` (property inheritance — e.g. A.5.13 cadence
    from A.5.12)
  - `FEEDS_INTO` (processual — e.g. A.7.4 → A.5.26 SIEM)
  - `AUDITED_BY` (e.g. all A.5-8 by 9.2 internal audit)
- **8 NEW operational Events** (personnel_added / offboarded /
  role_changed / asset_added / retired / reclassified /
  privilege_granted / revoked).
- **`triggered_implication` Postgres table** — per-tenant
  cascade-implication rows with status (pending/satisfied/overdue/
  dismissed) + due_date computed from event-edge deadline.
- **`enrichment/relationships/relationship_catalog.py`** as the
  single authoring file. RelationshipEdge dataclass with
  source_ref, target_ref, edge_type, rationale, citation
  (non-optional in practice), role, applies_when.
- **`enrichment/relationships/load_to_neo4j.py`** with idempotent
  MERGE + declarative orphan pruning (same pattern as
  load_to_neo4j.py for the catalog).
- **`scripts/validate_relationship_catalog.py`** validation
  harness — format / catalog-membership / citation / symmetry /
  no-self-loops / reference-corpus coverage checks.
- **7-step migration sequence (S1-S7)** with S1-S3 = ~3 sessions
  to ship cascade-v1, S4-S7 extending to full migration of
  existing 274 cross-framework edges + ~600 intra-framework
  edges from curation memos.

## Critical non-obvious takeaways

### The cascade is NOT new infrastructure

`TRIGGERS_OBLIGATION` edges + `Event` nodes + `mandatory`/
`deadline`/`rationale` edge properties ALREADY EXIST in the
graph. Personal data breach + DSAR + erasure + audit all wire
up correctly. Cascade as a feature is: (a) add 8 more Event
nodes, (b) connect them via TRIGGERS_OBLIGATION, (c) add tenant-
side emission from cite verifications, (d) add the implications
table. No new edge type needed for cascade itself.

### Cross-framework relationships are MORE typed than I assumed

There are FOUR distinct cross-framework edge types in graph
(IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE), not one
xfw_bridge. They differ semantically:

- IMPLEMENTS (168 edges) — "realises the obligation of"
- SUPPORTS (76 edges) — "helps satisfy"
- ENABLES (22 edges) — "upstream prerequisite"
- GOVERNANCE (8 edges) — "management clause governs"

This validates the typed-edge approach EMPIRICALLY — the
curation team already needed four types of cross-framework
relationships. The 6 new intra-framework types are
extrapolation from this empirical baseline, not invention.

### `role` field on DerivedFrom edges already exists

`DerivedSpec.derives_from` entries carry `role` tag
(cryptography / access_rights / incident_response / etc.). This
is a precedent for the `role` field on the new
RelationshipEdge dataclass — sub-typing without exploding the
edge-type count.

### Reference corpus for validation

The design ties each edge type to specific references:

- ISO 27002:2022 "see also" / "in conjunction with" phrases
- ISO/IEC 27701 Annex D (ISO↔GDPR mapping table)
- GDPR text explicit cross-references between Articles
- EDPB Guidelines (per-Article interpretive cross-refs)
- OSCAL `link/rel` vocabulary (naming conventions)
- ITIL joiner-mover-leaver (operational event semantics)
- NIST 800-61 incident phases (incident-event semantics)

Validation harness scripts this as a coverage check.

## Why the user's question reframed everything

User asked: "what is our reference to make sure that our
relationship model is solid and exhaustive?". That question
forced moving from "design a feature" to "design an
authoring + validation pipeline against external references".
The audit then revealed that 70% of the data plane is already
there. The deliverable shrank from "build cascade subsystem"
to "extend the existing graph + add the implications surface".

## What ships next

Section 15 of design doc: implement S1 (catalog file + loader
scaffolding + validation harness, zero edges). Zero risk; proves
the authoring pipeline. Then S2 (operational events) + S3
(implications table + cascade engine + minimal UI) = cascade-v1
in ~3 sessions.

S4 (migrate existing 274 cross-framework edges into the catalog)
+ S5 (~50 intra-GDPR edges) + S6 (~600 intra-ISO edges from
memos+27002) + S7 (wire xfw_proposer to unified loader) are
additive expansions over months, not blocking.

## Files touched

- `/data/arioncomply/docs/relationship_model_audit_2026_06_29.md`
  (created)
- `/data/arioncomply/docs/relationship_model_design_2026_06_29.md`
  (created)

## Related memory

- [[product-concept-evidence-cascade-2026-06-27]] — original
  cascade memo; superseded by this unified design
- [[cite-mode-v1-backend-2026-06-27]] — cite verification
  emits Events (per design)
- [[dashboard-cite-freshness-card-2026-06-27]] — freshness
  drives WHEN events are emitted
- [[feedback-validate-set-membership]] — catalog-membership
  predicate the validation harness uses
- [[product-principle-evidence-stored-vs-cited]] — the
  product-level frame this all sits inside
