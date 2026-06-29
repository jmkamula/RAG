# Unified Relationship Model — Design

**Date:** 2026-06-29
**Status:** DESIGN — not yet implemented
**Companion:** [relationship_model_audit_2026_06_29.md](relationship_model_audit_2026_06_29.md)

## 1. Goals + non-goals

### Goals

- **One typed-relationship graph** covering all compliance entity relationships — intra-framework, cross-framework, composition, applicability, event-driven.
- **OSCAL-aligned naming** so the model is portable when we extend beyond ISO 27001 + GDPR (NIST 800-53, SCF, NIS2, DORA, HIPAA come later).
- **Single source-of-truth authoring file** (analogous to `document_requirements.py` for the catalog).
- **Validated against published references** — every edge type has examples in ISO 27002 / 27701 / EDPB / GDPR text / NIST OSCAL semantics. Every edge instance traces to a reference citation.
- **Backwards-compatible** — the existing 17 edge types stay; we only ADD.

### Non-goals (deferred)

- Tenant entity nodes (Personnel / Asset / Identity instances per tenant). Deferred to "after the obligation graph is unified."
- Cross-tenant relationships.
- Edge-property authoring UI. Edges are code-defined, version-controlled, reviewed.
- Auto-derivation of edges from standards text (LLM mining). The catalog is human-authored; LLM assists are a v2 enhancement.

## 2. Adopted naming convention

OSCAL `link/rel` vocabulary where applicable. Existing graph edges keep their names (no rename churn) but new edges follow OSCAL conventions.

| Concept | Existing name (keep) | OSCAL equivalent |
|---|---|---|
| "Realises the obligation of" | `IMPLEMENTS` | `incorporated-into` |
| "Helps satisfy" | `SUPPORTS` | `related` |
| "Upstream prerequisite" | `ENABLES` | `required-by` |
| "Management governance" | `GOVERNANCE` | `controlled-by` |
| "Composition" | `DERIVES_FROM` | `incorporates` |

New edges:

| New name | Definition | OSCAL/citation analog |
|---|---|---|
| `PAIRS_WITH` | Bidirectional lifecycle coupling — both controls must move together | OSCAL `related` (symmetric); also matches ISO 27002 "in conjunction with" phrasing |
| `PREREQUISITE_OF` | A must exist + be operating before B is meaningful | OSCAL `prerequisite-control` |
| `ESCALATES_TO` | Severity/scope expansion path — B is the next step when A is exceeded | No direct OSCAL; closest is custom relation tag; matches ITIL incident escalation |
| `CASCADES_FROM` | Property inheritance (review cadence, scope) from parent | OSCAL `inherits-from` (custom) |
| `FEEDS_INTO` | Output of A is input to B's operation | OSCAL `related` (directional); matches "feeds the X process" curation phrasing |
| `AUDITED_BY` | Independent-verification relationship — B audits A's operation | Custom (matches "audited under" in 27001 9.2 cross-references) |

All six are RequirementNode → RequirementNode edges and may be intra-framework or cross-framework.

## 3. Conceptual model

### 3.1 Edge classes by purpose

| Purpose | Existing edges | New edges | Coverage |
|---|---|---|---|
| **Catalog skeleton** | DERIVED_FROM, MUST_CONTAIN, SHOULD_CONTAIN, REQUIRES_EVIDENCE, HAS_TEMPLATE, SATISFIED_BY, PART_OF | — | Structural; no change |
| **Cross-framework bridges** | IMPLEMENTS, SUPPORTS, ENABLES, GOVERNANCE | — | Already 4-typed; keep |
| **Intra-framework structural** | — | **PAIRS_WITH, PREREQUISITE_OF, ESCALATES_TO, CASCADES_FROM, FEEDS_INTO, AUDITED_BY** | NEW |
| **Composition** | DERIVES_FROM (40 edges via FulfilmentSpec) | — | Keep; DerivedSpec authoring unchanged |
| **Applicability** | TRIGGERS, REQUIRES_CONTROL | — | Keep; ClientFact / ObligationRule layer unchanged |
| **Event-driven cascade** | TRIGGERS_OBLIGATION | — | Keep; **extend Event node catalog** (Section 5) |
| **Classification taxonomy** | ALLOWS, MANIFESTS_AS | — | Keep |

### 3.2 Node classes

No new node classes for the relationship graph itself.

For the cascade-implications layer (Section 6), one new Postgres table (`triggered_implication`).

For the operational-event layer (Section 5), 8 new `Event` nodes — same node class, same edge types, just more vocabulary.

## 4. New intra-framework edge types — definitions + examples

Each edge below has: **definition**, ≥3 examples from the curation corpus, and the reference citation that grounds the relationship.

### 4.1 `PAIRS_WITH`

**Definition.** Bidirectional lifecycle coupling. Both ends move together — when one fires, the other should too; when one's evidence is missing, the other's is suspect. Symmetric edge (write once; query both directions).

**Examples:**

| Source | Target | Curation citation | Reference |
|---|---|---|---|
| A.5.16 Identity Mgmt | A.5.17 Authentication Info | "rev_identity_pair MUST enforces bidirectional A.5.16↔A.5.17 lifecycle pairing" (batch 13) | ISO 27002:2022 §5.17 explicitly references §5.16 |
| A.5.16 Identity Mgmt | A.5.18 Access Rights | "bidirectional A.5.16↔A.5.18 lifecycle pairing" (batch 20) | ISO 27002:2022 §5.18 references §5.16 |
| A.5.29 Disruption | A.5.30 ICT Readiness | "natural pair with A.5.29; second HYBRID lifecycle-end" (batch 16) | ISO 27002:2022 §5.30 introduced as the ICT-specific counterpart to §5.29 |
| A.5.33 Records Protection | A.5.34 PII Protection | "natural pair with A.5.33 — A.5.33 protects records, A.5.34 protects the PII subset" (batch 18) | ISO 27002:2022 §5.34 introduced as the PII-specific extension |
| Art.13 (Information at collection) | Art.14 (Information when not from data subject) | GDPR Art.14 references Art.13 verbatim | GDPR text |
| Art.16 (Rectification) | Art.19 (Notification obligation) | GDPR Art.19 explicitly says "communicates… any rectification under Article 16" | GDPR text |

### 4.2 `PREREQUISITE_OF`

**Definition.** Directional. A must be in place + operating before B is meaningful. Asymmetric. Walking A → B answers "what does B depend on?"; walking B → A answers "what unlocks if I do A?"

**Examples:**

| Source | Target | Curation citation | Reference |
|---|---|---|---|
| A.5.9 Asset Register | A.5.12 Classification | "A.5.37 → A.5.9 asset register" (batch 19) — and you can't classify what you don't list | ISO 27002:2022 §5.12 says classification "of information…" — implies the inventory of A.5.9 |
| A.5.12 Classification Scheme | A.5.13 Labelling | "CASCADE-CADENCE pattern (review freshness inherited from A.5.12 parent)" (batch 10) | ISO 27002:2022 §5.13 references §5.12 explicitly |
| A.5.34 PII Policy | A.5.33 Records | "A.5.33 protects records, A.5.34 protects the PII subset" — A.5.34 scope-narrows A.5.33 | ISO 27002:2022 §5.34 sub-scope of §5.33 |
| A.6.5 Contractual Layer | A.5.11 Return of Assets | "A.6.5 contractual layer above operational A.5.11/A.5.16/A.5.17/A.5.18 offboarding" (batch 21) | ISO 27002:2022 §6.5 frames §5.11/§5.16-18 enforcement |
| A.6.6 Confidentiality NDA | A.6.5 Post-employment | NDA must exist before post-employment confidentiality survives | ISO 27002:2022 §6.6 + §6.5 |
| Art.30 RoPA | Art.32 Security of Processing | Art.32.1 phrase "appropriate measures…for processing" — requires Art.30 enumeration | GDPR text |
| Art.6 Lawful Basis | Art.7 Consent | Art.7 only applies if lawful basis is consent | GDPR Art.7 specialises Art.6.1.a |

### 4.3 `ESCALATES_TO`

**Definition.** Severity / scope expansion. When A's threshold is exceeded, B is the next obligation. Used for incident family, breach severity, regulatory escalation.

**Examples:**

| Source | Target | Curation citation | Reference |
|---|---|---|---|
| A.5.25 Triage | A.5.26 Incident Register | "A.5.24 sits ABOVE A.5.25-27/28 operational layer — strategic planning layer" (batch 14) | ISO 27002:2022 §5.25 → §5.26 escalation |
| A.5.26 Incident Register | A.5.27 Lessons Learned | "closes the reporting → triage → incident pipeline" | ISO 27002:2022 §5.27 follows from §5.26 |
| A.5.26 Incident (Security) | Art.33 (GDPR breach notify) | "personal_data_breach: 72h on Art.33" — when ISO incident scopes PII | GDPR Art.4(12) "personal data breach" defines escalation |
| Art.33 (Breach to SA) | Art.34 (Breach to subjects) | Art.34 escalates Art.33 when "high risk to rights" | GDPR Art.34.1 |
| A.5.7 Threat Intel | A.5.25 Triage | Threat-intel signal triggers triage | ISO 27002:2022 §5.7 deliverable feeds §5.25 |

### 4.4 `CASCADES_FROM`

**Definition.** Property inheritance. Child inherits review cadence / scope / classification from parent. Recorded so changes to parent propagate.

**Examples:**

| Child | Parent | Curation citation | Property inherited |
|---|---|---|---|
| A.5.13 Labelling | A.5.12 Classification | "CASCADE-CADENCE pattern (review freshness inherited from A.5.12 parent)" (batch 10) | Review freshness |
| A.5.18 Access Rights | A.5.16 Identity Mgmt | Identity lifecycle changes cascade scope | Lifecycle event subscription |
| A.5.34 PII Policy | A.5.33 Records | PII-specific overlay; review cadence aligned | Cadence + scope |
| Art.5.1.f | Art.32 | (DerivedSpec — already encoded as DERIVES_FROM; CASCADES_FROM is the read-back direction) | Property semantics |

CASCADES_FROM ≠ DERIVES_FROM: DERIVES_FROM is composition (A is satisfied if B is); CASCADES_FROM is property inheritance (changes to B propagate metadata to A).

### 4.5 `FEEDS_INTO`

**Definition.** Output of A is input to B's operation. Directional; processual.

**Examples:**

| Source | Target | Curation citation | Reference |
|---|---|---|---|
| A.7.4 Physical Monitoring | A.5.26 Incident Register | "A.7.4 → A.5.26 incident SIEM" (batch 22) | ISO 27002:2022 §7.4 outputs into incident detection |
| A.5.7 Threat Intel | A.5.24 IR Framework | Threat intel feeds IR planning | ISO 27002:2022 §5.7 deliverable feeds §5.24 |
| A.5.9 Asset Register | A.5.37 Operating Procedures | A.5.37 references applicable assets from A.5.9 (batch 19) | ISO 27002:2022 §5.37 cross-references |
| Art.30 RoPA | Art.35 DPIA Threshold | RoPA entries feed DPIA scoping | EDPB Guidelines on DPIA |
| A.5.36 Compliance Review | A.5.35 Independent Review | Compliance findings feed review (batch 19) | ISO 27002:2022 §5.36 outputs to §5.35 |

### 4.6 `AUDITED_BY`

**Definition.** Independent verification — B audits A. Used for management-system clauses (9.2 internal audit) auditing Annex A controls, and for A.5.36 compliance review auditing other A.5 controls.

**Examples:**

| Audited control | Auditor control | Reference |
|---|---|---|
| All A.5–A.8 controls | ISO 9.2 Internal Audit | ISO 27001:2022 9.2 scope |
| A.5.x policy controls | A.5.36 Compliance | ISO 27002:2022 §5.36 scope |
| A.5.35 Independent Review | A.5.36 Compliance | Cross-check; batch 19 ("finding registers can share infrastructure") |
| Art.32 measures | Art.5.2 Accountability | GDPR Art.5.2 demand of demonstrability over Art.32 |
| Art.40 Codes of Conduct | Art.41 Monitoring Bodies | GDPR Art.41 monitors Art.40 |

## 5. Operational event vocabulary

Extends the existing 11 Events with operational world events that PRECEDE compliance events. Source-of-truth = cite verifications (tenant attests "X happened since last verify"). Each new Event node carries `event_type`, `category`, `description`, `legal_deadline`, `severity_default` (same shape as existing Events).

| New Event | Category | Triggers (via TRIGGERS_OBLIGATION) | Source-of-truth (cite system covers_evidence_types) | Reference |
|---|---|---|---|---|
| `event:personnel_added` | hr | A.6.1, A.6.2, A.6.3, A.5.10, A.5.16, A.5.17, A.5.18 | HR system (register, record) | ITIL joiner-mover-leaver; ISO 27002:2022 §6.1/2/3 |
| `event:personnel_offboarded` | hr | A.5.11, A.5.16, A.5.17, A.5.18, A.6.5 | HR system | ITIL leaver; ISO 27002:2022 §5.11 |
| `event:role_changed` | hr | A.5.18, A.6.3, A.6.5 | HR system | ITIL mover |
| `event:asset_added` | asset | A.5.9, A.5.12, A.7.10 | Asset register | ISO 27002:2022 §5.9 |
| `event:asset_retired` | asset | A.5.9, A.7.14, A.8.10 | Asset register | ISO 27002:2022 §7.14 |
| `event:asset_reclassified` | asset | A.5.12, A.5.13 | Asset register | ISO 27002:2022 §5.12 |
| `event:privilege_granted` | iam | A.5.18, A.8.2 | IAM system (register, record) | ISO 27002:2022 §8.2 |
| `event:privilege_revoked` | iam | A.5.16, A.5.17, A.5.18 | IAM system | ISO 27002:2022 §5.16 |

Each new Event will be authored in the same source file as the existing Events (today loaded by `load_to_neo4j.py` — exact location to confirm during implementation). TRIGGERS_OBLIGATION edges follow the same property shape (`mandatory`, `deadline`, `rationale`).

Total Event nodes after extension: 19 (11 existing + 8 operational).

## 6. Implications-tracking schema

When an Event fires (a tenant verification reports `personnel_added: 5`), the cascade engine walks TRIGGERS_OBLIGATION edges → creates per-tenant `triggered_implication` rows. Tenant resolves each.

```sql
CREATE TABLE triggered_implication (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id              UUID NOT NULL,

    -- WHAT FIRED
    source_verification_id UUID NOT NULL REFERENCES
                             external_evidence_verification_log(id),
    source_event_type      TEXT NOT NULL,
    -- e.g. 'personnel_added' — references Event.event_type in Neo4j

    -- WHERE IT POINTS
    target_control_ref     TEXT NOT NULL,
    -- e.g. 'A.6.3' — Neo4j RequirementNode.id derivable

    target_leaf_id         TEXT,
    -- optional — when the implication is leaf-specific
    target_must_id         TEXT,
    -- optional — when the implication is MUST-specific

    -- LIFECYCLE
    expected_action        TEXT NOT NULL,
    -- e.g. 'new_row_required' / 'review_required' / 'attestation_required'
    fired_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    due_date               TIMESTAMPTZ,
    -- computed from Event.legal_deadline or trigger-edge deadline prop

    status                 TEXT NOT NULL DEFAULT 'pending',
    -- pending / satisfied / overdue / dismissed
    resolved_at            TIMESTAMPTZ,
    resolved_by            UUID,
    resolved_evidence_kind TEXT,
    -- 'finding' / 'cite' / 'dismissal'
    resolved_evidence_id   UUID,
    dismissed_reason       TEXT,

    -- INTEGRITY
    CONSTRAINT triggered_implication_status_chk
        CHECK (status IN ('pending', 'satisfied', 'overdue', 'dismissed')),
    CONSTRAINT triggered_implication_resolution_consistent CHECK (
        (status IN ('pending', 'overdue') AND resolved_at IS NULL)
        OR
        (status IN ('satisfied', 'dismissed') AND resolved_at IS NOT NULL)
    )
);

CREATE INDEX idx_triggered_implication_tenant_status
    ON triggered_implication(tenant_id, status, due_date);
CREATE INDEX idx_triggered_implication_source
    ON triggered_implication(source_verification_id);
```

RLS-enabled (same pattern as the cite tables in schema_v50).

### Engine pseudocode

```
on cite_verification(structured_events):
    for event in structured_events:
        targets = neo4j.query(
            "MATCH (e:Event {id: $ev})-[r:TRIGGERS_OBLIGATION]->(n) "
            "RETURN n.id AS ref, r.deadline AS deadline, "
            "       r.mandatory AS mand, r.rationale AS rationale",
            ev=event.event_type)
        for t in targets:
            for row_n in range(event.count):
                pg.insert_triggered_implication(
                    tenant_id, verification_id,
                    event.event_type, t.ref,
                    expected_action='new_row_required',
                    due_date=now() + parse(t.deadline))
```

## 7. Curation file pattern

New file: `enrichment/relationships/relationship_catalog.py`

Structure (matches `document_requirements.py` discipline):

```python
"""
Unified relationship catalog. Single source of truth for typed
edges in the obligation graph. Loaded into Neo4j by
enrichment/relationships/load_to_neo4j.py (idempotent + declarative
orphan pruning, same pattern as the catalog loader).
"""

from dataclasses import dataclass, field
from typing import Optional, List

@dataclass(frozen=True)
class RelationshipEdge:
    source_ref: str
    # e.g. 'A.5.16' or 'Art.32' — control/article ref in framework-prefixed form
    source_standard_id: str
    # e.g. 'ISO27001:2022' or 'GDPR:2016/679'

    target_ref: str
    target_standard_id: str

    edge_type: str
    # one of: PAIRS_WITH / PREREQUISITE_OF / ESCALATES_TO /
    # CASCADES_FROM / FEEDS_INTO / AUDITED_BY / IMPLEMENTS /
    # SUPPORTS / ENABLES / GOVERNANCE

    rationale: Optional[str] = None
    # 1-sentence explanation; appears in auditor-facing surfaces

    citation: Optional[str] = None
    # Reference: 'ISO27002:2022 §5.17' / 'GDPR Art.19' / 'EDPB 4/2019 §3.2'

    role: Optional[str] = None
    # Semantic role within the edge type, when there's natural sub-typing
    # (e.g. PAIRS_WITH role='lifecycle' vs role='topical')

    applies_when: Optional[str] = None
    # Optional applicability gate (matches the existing applies_when
    # DSL used elsewhere)

# Intra-framework — ISO 27001
ISO_INTRA_EDGES = [
    RelationshipEdge(
        source_ref='A.5.16', source_standard_id='ISO27001:2022',
        target_ref='A.5.17', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Identity record + credential record share a lifecycle — '
                  'disabling one without the other leaves stale auth material.',
        citation='ISO27002:2022 §5.17 references §5.16 explicitly',
        role='lifecycle',
    ),
    RelationshipEdge(
        source_ref='A.5.16', source_standard_id='ISO27001:2022',
        target_ref='A.5.18', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Identity changes drive access-rights review/revocation '
                  'in the same cycle.',
        citation='ISO27002:2022 §5.18 references §5.16',
        role='lifecycle',
    ),
    # ... 600+ entries
]

# Intra-framework — GDPR
GDPR_INTRA_EDGES = [
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='Art.34', target_standard_id='GDPR:2016/679',
        edge_type='ESCALATES_TO',
        rationale='Art.34 escalates Art.33 when breach risk is high.',
        citation='GDPR Art.34.1',
    ),
    # ... 50+ entries
]

# Cross-framework (today's IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE
# migrate here so all relationship data is in one file)
XFW_EDGES = [
    # ... 274 entries
]

ALL_EDGES = ISO_INTRA_EDGES + GDPR_INTRA_EDGES + XFW_EDGES
```

### Why this shape

- **Authoring discipline matches `document_requirements.py`** — code-defined, version-controlled, reviewable. The audit found 669 candidate pairs from curation memos; each becomes an entry, with citation.
- **One file = one queryable graph** — current relationships are split (xfw_bridge separately from DerivedSpec separately from prose-only). One file removes the "where is this encoded?" friction.
- **Citation field is non-optional in practice** — every relationship traces to ISO 27002 / 27701 / GDPR / EDPB / standards text. Reviewers verify the citation.
- **`role` field supports sub-typing** without exploding edge types — e.g. `PAIRS_WITH role='lifecycle'` vs `PAIRS_WITH role='topical'`. Keeps the edge-type list small (6 new + 4 existing = 10 RequirementNode-to-RequirementNode types).
- **`applies_when` ready** — for tenant-scope-aware edges (e.g. PAIRS_WITH that only applies if `fact:has_remote_workers`). Not used at v1 launch but the field is there.

## 8. Loader + Neo4j sync

New file: `enrichment/relationships/load_to_neo4j.py`

Same pattern as `enrichment/documents/load_to_neo4j.py`:

1. Load `ALL_EDGES` from the catalog.
2. For each edge: ensure source + target nodes exist (Cypher `MATCH`); skip with warning if not.
3. Idempotent upsert via `MERGE (a)-[r:TYPE {...}]->(b) SET r += {...}` keyed by `(source_ref, target_ref, edge_type)`.
4. Declarative orphan pruning: any existing edge of the 6 new types not in `ALL_EDGES` gets deleted (analogous to leaf MUST/SHOULD pruning at load_to_neo4j.py).
5. Final pass: existing 4 cross-framework edges (`IMPLEMENTS`/`SUPPORTS`/`ENABLES`/`GOVERNANCE`) currently come from a different source — once migrated, this loader owns all 10 edge types. **Migration is a separate task** (Section 10).

## 9. Validation harness

New script: `scripts/validate_relationship_catalog.py`

For each edge in `ALL_EDGES`:

1. **Format checks** — source_ref / target_ref match expected patterns; standard_id known; edge_type in the allowed enum.
2. **Source + target exist in the catalog** (loader-canonical-union: `ALL_EVIDENCE_REQUIREMENTS + ALL_DERIVED_SPECS.direct_evidence` — see [[feedback-validate-set-membership]]).
3. **Citation present** for new edge types — warn if empty (reviewers can override per-edge).
4. **Symmetric edges are bi-directional in the catalog** — if `A PAIRS_WITH B` is authored, the loader should infer `B PAIRS_WITH A` and they should not be authored separately (consistency check).
5. **No self-loops** unless explicitly allowed (none today).
6. **Reference-corpus coverage check** (manual + scripted):
   - For ISO 27002 — manual cite-completeness sweep (every `§X.Y` reference in 27002 has at least one edge in catalog).
   - For ISO 27701 Annex D — every mapping-table entry has a corresponding `IMPLEMENTS` edge.
   - For GDPR text — every explicit article cross-reference (Art.X "as referred to in Article Y") has an edge.
   - For EDPB Guidelines — sample one guideline per Article and check edges.

Run as part of the regular CI/test pass.

## 10. Migration sequence

Authoring + migration broken into independent, ship-able pieces:

| Step | Scope | Risk |
|---|---|---|
| **S1** | Land the catalog file + loader scaffolding (zero edges initially) + validation harness | Zero — code only |
| **S2** | Author the 8 operational Event nodes + their TRIGGERS_OBLIGATION edges + verify dialog UI accepts structured event emissions | Low — new data only |
| **S3** | Land the `triggered_implication` table + cascade engine writer + minimal UI surface | Medium — first user-visible surface |
| **S4** | Migrate the existing 274 cross-framework edges into the catalog file; switch the loader; verify Neo4j round-trip | Medium — touches running system |
| **S5** | Author the ~50 intra-GDPR edges from EDPB + GDPR cross-references (highest-quality data) | Low — additive |
| **S6** | Author the ~600 intra-ISO edges from curation memos + ISO 27002 cite-validation | Long but additive |
| **S7** | Wire the existing IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE walker (xfw_proposer) to use the unified loader | Low — same edge data, same semantics |

S1–S3 = ~3 sessions = "cascade v1 shipped" with operational events + implications. The remainder (S4–S7) extends the system but is not blocking.

## 11. What NOT in this design

- **Tenant-entity nodes** (Personnel/Asset/Identity rows per tenant). Deferred — current cite verifications encode events at the aggregate level (`personnel_added: 5`); per-instance tracking is a future layer.
- **Edge-property editing UI**. Edges are code-defined. Tenant disagreement = a curation review, not a runtime override.
- **Cross-tenant relationships**. All edges in the catalog are framework-level, not tenant-level.
- **LLM-mined edges**. The catalog is human-authored. LLM-assisted *candidate generation* (e.g., suggest PAIRS_WITH edges from ISO 27002 paragraph mining) is a v2 enhancement; the catalog reviewer remains the source of truth.
- **Time-bounded edges**. Edges don't expire. If a relationship becomes obsolete, it's deleted from the catalog (and the loader prunes it from Neo4j).

## 12. Open questions

| Q | Default | Alternatives |
|---|---|---|
| Should `PAIRS_WITH` be one symmetric edge stored once, or two directed edges? | Stored ONCE, loader creates both directions in Neo4j (one row in catalog → two graph edges) | Could store twice; doubles authoring overhead |
| Should new edge types appear in xfw_proposer's bridge walks? | Default NO at S1; YES once S4 is done and unified walker exists | Selective enabling per edge type |
| Should `applies_when` be evaluated at load time or query time? | Query time (matches existing `applies_when` semantics elsewhere) | Load-time gives faster queries but breaks dynamic applicability |
| How are duplicate authored edges detected? | Validator errors if `(source, target, edge_type)` triple appears more than once | Allow with warning |
| Should multi-target edges be allowed (one source, list of targets)? | NO — one row per edge for clarity + diffability | Convenience helpers in authoring (`pairs_with_all(A, [B, C])` → 2 edges) |

## 13. Success criteria

1. **Validation harness passes** — every edge in catalog format-validates and source+target exist.
2. **Coverage check** — at least 80% of ISO 27002 "see also" / "in conjunction with" cross-references encoded by S6 completion.
3. **xfw_proposer regression** — no behavioural change after S7 (the migrated cross-framework edges produce identical proposals).
4. **Cascade end-to-end** — by S3, a tenant verification reporting `personnel_added: 5` creates ≥5 `triggered_implication` rows targeting A.6.3 (training) + supporting controls.
5. **Eval suite** — no regression below the 197/199 floor across S1–S7.

## 14. Companion documents

- [Audit (Section A)](relationship_model_audit_2026_06_29.md)
- [[product-concept-evidence-cascade-2026-06-27]] — original cascade design memo (now superseded by this unified model)
- [[cite-mode-v1-backend-2026-06-27]] — the cite verification path that emits Events
- [[dashboard-cite-freshness-card-2026-06-27]] — sibling surface; freshness drives WHEN events are emitted

## 15. Recommended first action

Implement **S1** (catalog file + loader scaffolding + validation harness) with zero edges initially. This is a no-risk infrastructure step that unblocks every later step and proves the authoring pipeline before the data lift of S5/S6.

Estimate: 1 session.
