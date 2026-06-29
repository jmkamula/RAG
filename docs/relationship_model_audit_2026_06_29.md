# Relationship Model Audit — ISO 27001 + GDPR

**Date:** 2026-06-29
**Scope:** Inventory the current relationship apparatus across Neo4j, the Python catalog, and the curation memo corpus. Foundation for the unified relationship-model design.

## TL;DR

The product already has a substantial typed-relationship model in Neo4j — 17 edge types, 11 Event nodes, 22 ClientFacts, 18 ObligationRules, 4 distinct cross-framework edge classes. The "cascade" concept is partly built at the schema level.

**What's missing:**

1. **Intra-framework typed relationships** — 669 cross-control mentions across 30 curation memos describe pairings, escalations, prerequisites, dependencies *within* ISO 27001 and *within* GDPR. None of these are encoded as typed edges in Neo4j; they live in prose.
2. **Operational world events** — current Events are compliance-lifecycle (DSAR, breach, audit, new processing). Missing: HR joiner-mover-leaver, asset lifecycle, IAM grants/revocations, role changes.
3. **Tenant-side event emission** — cite verifications (`external_evidence_verification_log.changes_detected`) don't yet emit structured Events into the graph.
4. **Implications tracking** — no `triggered_implication` table or surface for "this event fired → these obligations need attention now".

## A. Neo4j relationship inventory

### Edge types (17 total, 11,793 edges)

**Structural (catalog skeleton — load_to_neo4j.py owns):**

| Edge | Count | Shape |
|---|---:|---|
| `DERIVED_FROM` | 4305 | ChecklistItem → EvidenceRequirement |
| `MUST_CONTAIN` | 3409 | EvidenceRequirement → ChecklistItem (mandatory) |
| `SHOULD_CONTAIN` | 897 | EvidenceRequirement → ChecklistItem (recommended) |
| `REQUIRES_EVIDENCE` | 651 | RequirementNode → EvidenceRequirement |
| `HAS_TEMPLATE` | 648 | EvidenceRequirement → Template |
| `SATISFIED_BY` | 429 | RequirementNode → FulfilmentSpec |
| `PART_OF` | 26 | RequirementNode → RequirementNode (clause hierarchy, e.g. 7.2 → 7) |

**Cross-framework (the model's "bridges"):**

| Edge | Count | Semantics | Direction |
|---|---:|---|---|
| `IMPLEMENTS` | 168 | "Realises the obligation of" | ISO→GDPR 90 / GDPR→ISO 78 |
| `SUPPORTS` | 76 | "Helps satisfy, but doesn't alone implement" | ISO→GDPR 41 / GDPR→ISO 35 |
| `ENABLES` | 22 | "Upstream prerequisite" | ISO→GDPR 11 / GDPR→ISO 11 |
| `GOVERNANCE` | 8 | "ISO management clause governs the GDPR practice" | ISO→GDPR 7 / GDPR→ISO 1 |

**Composition (the DerivedSpec layer):**

| Edge | Count | Shape |
|---|---:|---|
| `DERIVES_FROM` | 40 | FulfilmentSpec → RequirementNode, with `role` / `title` / `scope_items` properties |

**Applicability + event-driven cascade (existing infrastructure):**

| Edge | Count | Shape |
|---|---:|---|
| `TRIGGERS` | 27 | ClientFact → ObligationRule (e.g., `fact:processes_personal_data` triggers `gdpr_universal`) |
| `REQUIRES_CONTROL` | 63 | ObligationRule → RequirementNode (with `mandatory` / `trigger_type` / `rationale` props) |
| `TRIGGERS_OBLIGATION` | 44 | Event → RequirementNode (with `deadline` / `mandatory` / `rationale` props) |

**Classification (incident taxonomy):**

| Edge | Count | Shape |
|---|---:|---|
| `ALLOWS` | 11 | ClassificationDimension → ClassificationValue |
| `MANIFESTS_AS` | 11 | ClassificationValue → Event |

### Node classes (10 total)

| Label | Count | Role |
|---|---:|---|
| `ChecklistItem` | 4305 | The MUST/SHOULD atomic assertions |
| `EvidenceRequirement` | 648 | The leaf-level evidence artifacts |
| `RequirementNode` | 429 | Standards-level controls / articles / clauses |
| `FulfilmentSpec` | 429 | Per-control fulfilment spec (1:1 with RequirementNode) |
| `Template` | 648 | Template artifacts (1:1 with EvidenceRequirement) |
| `ObligationRule` | 18 | Applicability gating rules |
| `ClientFact` | 22 | Per-client applicability facts |
| `Event` | 11 | World events that trigger obligations |
| `ClassificationDimension` | 2 | Incident taxonomy axes |
| `ClassificationValue` | 11 | Incident taxonomy values |

### Existing Events (11)

Compliance-lifecycle only — no operational world events:

| Event | Targets | Deadline pattern |
|---|---|---|
| `personal_data_breach` | Art.32/33/34 + ISO 6.1.2/A.5.26/A.5.27 | 72h on Art.33 |
| `dsar` | Art.12, Art.15 | 1 month |
| `erasure_request` | Art.12, Art.17, Art.19 | 1 month |
| `restriction_request` | Art.12, Art.18 | 1 month |
| `new_processing_activity` | Art.6/13/30/35 + ISO 6.1.2 | "before" / "at collection" |
| `new_processor_engaged` | Art.28/28.3 + ISO A.5.19/20/21 | "before" |
| `significant_system_change` | Art.30/35 + ISO 6.1.2/A.8.25/A.8.29 | "before" |
| `information_security_incident` | ISO 6.1.2/A.5.26/A.5.27 | (no deadline) |
| `audit_nonconformity` | ISO 9.2/10.1/10.2 | (no deadline) |
| `certification_audit` | ISO 5.2/6.1.2/6.1.3/9.2/9.3 | (no deadline) |
| `supervisory_authority_inquiry` | Art.5/24/31 + ISO 6.1.2/9.2 | (no deadline) |

### Existing ClientFacts (22)

Applicability triggers covering data-protection scope (PII / EU / UK / children / criminal / special category / large-scale / public-authority / automated / profiling), role (controller / joint-controller / processor), supply-chain (cloud / processors), workforce (250+ / remote / physical premises), tech (software-dev / transfers).

### Existing ObligationRules (18)

`gdpr_universal`, `iso_universal`, plus 16 conditional rules (DPIA / DPO / records-of-processing / international transfers / processors / joint-controllers / special-category / children / criminal / automated-decision / privacy-notices / remote / physical / cloud / software / processor-role).

## B. DerivedSpec composition catalog

15 specs in `enrichment/documents/document_requirements.py`:

| Spec | Op | Deps | Direct evidence | Notes |
|---|---|---|---:|---|
| `Art.32` | ALL | A.8.24 (crypto), A.5.18 (access), A.5.24 (IR), A.5.30 (BCP), A.8.13 (backup) | 4 | Security of processing |
| `Art.25` | ALL | A.5.8, A.8.27, A.8.25, A.8.11, A.5.34, A.8.10 | 4 | DPbD |
| `Art.24` | ALL | 5.1, 5.3, 9.3, A.5.1, A.5.34, A.5.36 | 4 | Controller responsibility (FIRST DerivedSpec 0→4 direct, 2026-06-02 batch 29a) |
| `Art.6` | ALL | A.5.34, A.5.31 | 4 | Lawfulness |
| `Art.16` | ALL | A.5.34 | 4 | Rectification |
| `Art.17` | ALL | A.5.34, A.8.10 | 4 | Erasure |
| `Art.5.1.a` | ALL | Art.6, Art.13 | 0 | Lawfulness/fairness/transparency |
| `Art.5.1.b` | ALL | Art.6, Art.30 | 0 | Purpose limitation |
| `Art.5.1.c` | ALL | Art.25 | 0 | Minimisation |
| `Art.5.1.d` | ALL | Art.16 | 0 | Accuracy |
| `Art.5.1.e` | ALL | A.5.33, Art.25 | 0 | Storage limitation |
| `Art.5.1.f` | ALL | Art.32 | 0 | Integrity/confidentiality |
| `Art.5.1` | ALL | Art.5.1.a-f | 0 | Composes the 6 principles |
| `Art.5.2` | ALL | Art.24 | 0 | Accountability |
| `Art.5` | ALL | Art.5.1, Art.5.2 | 0 | Top-level Art.5 |

Notable: each DerivedFrom edge carries a `role` tag (cryptography / access_rights / incident_response / etc.) — already two-level typing (edge type + semantic role).

A.5.34 (privacy policy / governance) appears in 5 GDPR specs — the most-reused ISO control in GDPR derivation.

## C. Curation-memo cross-references

30 curation memos analysed (`curation_phase_b_batch_*.md`). Each memo names a "focal" control + cross-references several others.

**669 unique focal↔other ref pairs** across all memos, of which the strongest neighbourhoods are intra-ISO clusters:

- **Identity-lifecycle quartet**: A.5.16 ↔ A.5.17 ↔ A.5.18 (+ A.5.11 leaver) — paired bidirectionally in 4+ memos as "lifecycle pairing" / "bidirectional A.5.16↔A.5.17 / A.5.16↔A.5.18". Encodes `PAIRS_WITH` semantics.
- **Incident family chain**: A.5.24 → A.5.25 → A.5.26 → A.5.27 (+ A.5.28 evidence-handling, A.5.7 threat-intel). Memos describe "A.5.24 sits ABOVE A.5.25-27 operational layer" — encodes `ESCALATES_TO` / `PREREQUISITE_OF`.
- **BCP pair**: A.5.29 ↔ A.5.30. Memos: "natural pair with A.5.29; second HYBRID lifecycle-end". `PAIRS_WITH`.
- **Records protection chain**: A.5.33 → A.5.34 (PII subset) ↔ A.5.35/A.5.36 (review/compliance). Memos describe A.5.34 as "natural pair with A.5.33 — A.5.33 protects records, A.5.34 protects the PII subset". `PAIRS_WITH` + `DERIVES_FROM`/`SCOPES`.
- **Information-handling cascade**: A.5.12 (classification scheme) → A.5.13 (labelling) → A.7.10 (media handling) → A.5.28 (disposal). "CASCADE-CADENCE pattern (review freshness inherited from A.5.12 parent)". `PREREQUISITE_OF` + `CASCADES_FROM`.
- **People controls (A.6.x)** to **operational counterparts**: A.6.5 contractual layer above A.5.11/A.5.16/A.5.17/A.5.18 offboarding. `GOVERNS_OPERATIONALLY` / `ESCALATES_TO`.
- **Physical-to-cyber bridges**: A.7.4 → A.5.26 (physical entry detection feeds SIEM incident). `FEEDS_INTO` / `TRIGGERS`.
- **GDPR principle composition**: Art.5.1.a-f → six principles, already captured in DerivedSpec. The curation memos for batch 27 also describe Art.6 → Art.7 (consent specialises lawful-basis) — currently DerivedSpec composition.

**Cross-validation against Neo4j:** intra-framework cross-control mentions in memos do **not** appear as typed edges in Neo4j. The 4 cross-framework edge classes (`IMPLEMENTS`/`SUPPORTS`/`ENABLES`/`GOVERNANCE`) only link RequirementNodes of *different* standards.

## D. Gaps the unified model must close

### D.1 Intra-framework relationships are prose-only

Curation memos describe ~600 intra-ISO + ~70 intra-GDPR relationships, but none are queryable. A.5.16 ↔ A.5.17 lifecycle pairing is repeatedly asserted across batches 12, 13, 20 but the engine can't walk it.

**Needed edge types** (candidate, to validate against references):

| Candidate | Examples in memos | OSCAL analog |
|---|---|---|
| `PAIRS_WITH` | A.5.16↔A.5.17; A.5.29↔A.5.30; A.5.33↔A.5.34 | `related` (bidirectional) |
| `PREREQUISITE_OF` | A.5.9 → A.5.12; A.5.12 → A.5.13; A.5.34 → A.5.33 | `prerequisite-control` |
| `ESCALATES_TO` | A.5.25 → A.5.26 → A.5.27; A.5.24 governs A.5.25-30 | `incorporates-by-reference` (loose) |
| `CASCADES_FROM` | A.5.13 inherits review-cadence from A.5.12 | `inherits-from` |
| `FEEDS_INTO` | A.7.4 physical detection → A.5.26 SIEM | `related` |
| `AUDITED_BY` | A.5.35 ← A.5.36; ISMS 9.2 ← A.5.36 | `audited-by` (custom) |

### D.2 Operational world events absent

The 11 existing Events are compliance-lifecycle. The cascade concept needs operational events that PRECEDE the compliance events:

| Missing event type | Compliance events it would precede | Source-of-truth |
|---|---|---|
| `personnel_added` | (would feed A.6.1/2/3 + A.5.16/17/18 obligations) | HR system |
| `personnel_offboarded` | (would feed A.5.11/16/17/18 + A.6.5) | HR system |
| `role_changed` | (would feed A.5.18 + A.6.3) | HR system |
| `asset_added` | (would feed A.5.9/12 + A.7.x classification) | Asset register |
| `asset_retired` | A.7.14 + A.8.10 (linked to existing `significant_system_change`) | Asset register |
| `identity_added` | A.5.16/17 + A.8.2 (admin grants) | IAM |
| `privilege_granted` | A.8.2 + A.5.18 | IAM |
| `privilege_revoked` | A.5.16/17/18 (linked to `personnel_offboarded`) | IAM |

These would emit from cite verifications when the tenant attests "5 new employees onboarded" — turning free-text `changes_detected` into structured Events. The cascade engine then walks the existing `TRIGGERS_OBLIGATION` edge primitive.

### D.3 Tenant-side event emission missing

`external_evidence_verification_log` has the `changes_detected` text payload. The cascade design memo proposed a `structured_events JSONB` column alongside. With operational event types in the graph (D.2), the verify dialog could capture structured emissions that match Event ids.

### D.4 Implications tracking surface missing

No `triggered_implication` table. When an Event fires, walking `TRIGGERS_OBLIGATION` reveals the controls to act on, but there's no per-tenant state ("this implication is pending / satisfied / dismissed").

## E. Cross-validation against references

Per the agreed reference base for ISO 27001 + GDPR:

| Reference | Used to validate |
|---|---|
| **ISO 27002:2022 implementation guidance** | Each intra-ISO `PAIRS_WITH` / `PREREQUISITE_OF` / `ESCALATES_TO` candidate must trace to a "see also" / "in conjunction with" / "supports" sentence in 27002 |
| **ISO/IEC 27701 Annex D** | The cross-framework ISO↔GDPR `IMPLEMENTS` / `SUPPORTS` edges already encoded — sanity-check completeness against Annex D's mapping table |
| **GDPR text** | Each intra-GDPR edge must trace to an explicit article cross-reference (e.g., Art.32 → Arts. 5, 6, 25) or a recital |
| **EDPB Guidelines** | Interpretive cross-references between articles (e.g., the Art.25 DPbD guideline lists Arts. 5, 24, 32, 35 — confirms `PREREQUISITE_OF`-style edges) |
| **Curation memo corpus** | The 669 mentioned pairs are the empirical bottom-up corpus |

OSCAL `link/rel` vocabulary provides naming conventions: `related`, `incorporated-into`, `incorporates`, `required-by`, `replaces`, etc. We adopt these names where applicable.

ITIL joiner-mover-leaver + NIST 800-61 incident phases provide the event-vocabulary references for the operational events in D.2.

## F. Conclusions

1. **We're not starting from scratch.** The relationship apparatus has 17 typed edges, an Event/ObligationRule/ClientFact applicability layer, a DerivedSpec composition layer, and 4 distinct cross-framework edge classes. The naming is partly OSCAL-compatible (`IMPLEMENTS`, `SUPPORTS`, `ENABLES`).

2. **The dominant gap is intra-framework structural edges.** 669 mentioned cross-control pairs encoded as prose, not data. This is the single biggest blocker to a unified model.

3. **The cascade design is a small extension, not a new subsystem.** `TRIGGERS_OBLIGATION` already exists; the gap is (a) operational world events as Event nodes, (b) tenant-side event emission, (c) the implications-tracking surface.

4. **OSCAL provides the naming reference; ISO 27002 + 27701 + GDPR text + EDPB guidelines provide the inventory references; curation memos provide the empirical corpus.**

## G. Proposed next step

Author a **unified relationship-model design memo** that:

- Adopts the existing 17 edge types as the baseline (no rename churn)
- Proposes ~6 NEW intra-framework edge types (`PAIRS_WITH`, `PREREQUISITE_OF`, `ESCALATES_TO`, `CASCADES_FROM`, `FEEDS_INTO`, `AUDITED_BY`) with OSCAL-aligned naming
- Specifies the curation file pattern (`enrichment/relationships/relationship_catalog.py`) that becomes the single source of truth for new edges
- Proposes the operational-event vocabulary (8 event types) to extend the existing 11
- Defines the implications-tracking schema (`triggered_implication` table)
- Specifies the validation script that cross-references the catalog against ISO 27002 / 27701 / EDPB

Implementation can then be staged independently per edge type.
