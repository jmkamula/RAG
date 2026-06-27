---
name: product-concept-evidence-cascade-2026-06-27
description: "STRATEGIC 2026-06-27: 'evidence cascade' layer — when a cite verification or tenant entry detects a CHANGE (new employee, offboarding, new asset, incident, new processing activity), the system fires DERIVED IMPLICATIONS across related leaves (training assignment, access creation, NDA signature, etc.). Generalises xfw_bridge from STATIC + PASSIVE to EVENT-DRIVEN + ACTIVE. Builds on cite-mode v1's changes_detected substrate. NOT a near-term build — captured here as strategic direction; build sequence after cite-mode v1."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## The concept

Compliance isn't static. A change in one place (new hire, new asset,
new incident, new processing activity) creates **downstream evidence
expectations** across many related controls. ArionComply should
detect these chains and surface them as actionable implications.

Example flows (the canonical starter set):

| Triggering change | Cascaded implications |
|---|---|
| HR cite reports "new employee onboarded" | A.6.3 training completion · A.6.2 NDA signature · A.5.16 identity register · A.5.18 access rights · A.5.10 AUP acknowledgement |
| HR cite reports "employee offboarded" | A.5.11 return of assets · A.5.16 identity revocation · A.5.18 access revocation · A.6.5 post-employment briefing · NDA survival check |
| HR cite reports "role changed" | A.5.18 access rights modification · A.6.3 role-specific training · A.6.5 confidentiality scope check |
| IAM cite reports "new admin granted" | A.8.2 privileged access record · A.5.18 register row · A.8.16 monitoring activation |
| Asset cite reports "new asset acquired" | A.5.9 classification + ownership · A.8.10 lifecycle entry · A.5.12 classification assignment |
| Incident cite reports "new incident logged" | A.5.27 lessons learned · A.5.30 BCP review trigger · GDPR Art.33/34 notification check |
| GDPR Art.30 cite reports "new processing activity" | A.5.20 supplier review · A.5.34 PII analysis · A.5.23 cloud risk · Art.35 DPIA threshold check |
| GDPR Art.30 cite reports "new cross-border transfer" | Art.44-49 transfer mechanism · Art.46 SCC update · Art.35 DPIA |

## Relationship to xfw_bridge

xfw_bridge today is **passive + static**: when finding F1 is
approved, xfw_proposer walks Neo4j IMPLEMENTS edges and proposes
related findings. Says "if you have F1, you probably have F2 too".

The cascade layer is **active + event-driven**: when EVENT happens,
it fires triggers saying "now you NEED these new artifacts". The
two share infrastructure (Neo4j relationships, trigger predicates,
the per-MUST data model) but answer different questions.

Both can coexist. xfw_bridge keeps doing what it does for static
cross-framework discovery. Cascade adds the event-driven dimension.

## Architectural shape (post-cite-mode-v1)

Three new layers:

### 1. Structured change events (extends cite verification)

Cite-mode v1 has `changes_detected` as required free-text on each
verification ([[product-principle-evidence-stored-vs-cited]]). The
cascade layer adds OPTIONAL structured events alongside:

    verification_log gains:
      structured_events: [
        {event_type: "personnel_added",     count: 5, subject_refs: [...]},
        {event_type: "personnel_offboarded", count: 1, subject_refs: [...]},
        {event_type: "role_changed",         count: 2, subject_refs: [...]},
      ]

Event types are catalogued per evidence_type:
- HR register → `personnel_added` / `personnel_offboarded` / `role_changed` / `org_change`
- Asset register → `asset_added` / `asset_retired` / `asset_reclassified`
- IAM register → `identity_added` / `identity_disabled` / `privilege_granted` / `privilege_revoked`
- Incident register → `incident_logged` / `incident_escalated` / `incident_closed`
- RoPA → `processing_added` / `purpose_changed` / `transfer_added`

Hybrid free-text + structured: tenant must write `changes_detected`
(forces real review); structured events optional but unlock cascade.

### 2. Declarative trigger catalog

A curation file (alongside `document_requirements.py`):

    enrichment/documents/trigger_definitions.py

Shape per trigger:

    TRIG_HR_PERSONNEL_ADDED = TriggerDefinition(
        id              = "trigger:hr:personnel_added",
        event_type      = "personnel_added",
        source_evidence_types = ["register", "record"],
        applicable_controls = ["A.6.1"],
        implications    = [
            ImpliedAction(
                target_leaf_id = "req:A.6.3:training_completion_register",
                target_must_id = "item:A.6.3:reg_personnel_id",
                expected_action = "new_row_required",
                description = "Each new employee triggers an expected training completion row",
                due_offset_days = 30,
            ),
            ImpliedAction(
                target_leaf_id = "req:A.6.2:signed_terms_register",
                target_must_id = "item:A.6.2:reg_personnel_id",
                expected_action = "new_row_required",
                due_offset_days = 7,
            ),
            ImpliedAction(
                target_leaf_id = "req:A.5.16:identity_register",
                ...
            ),
            ...
        ],
    )

Same authorship discipline as the catalog: code-defined, version-
controlled, reviewable. The trigger definitions become a curation
artifact.

### 3. Implications tracking + surface

When a verification fires structured events, the cascade engine
matches against trigger catalog → creates `triggered_implication`
rows:

    triggered_implication (
      id, tenant_id, fired_at,
      source_verification_log_id (FK),
      source_event_type,
      trigger_id (which trigger_definition matched),
      target_leaf_id,
      target_must_id,
      expected_action,
      due_date (computed from due_offset_days),
      status: 'pending' / 'satisfied' / 'overdue' / 'dismissed',
      resolved_at, resolved_by, resolved_evidence_id (FK to a finding or cite),
      dismissed_reason (when dismissed)
    )

New product surface ("Triggered actions") shows pending implications.
Tenant resolves each by:
- Uploading evidence (link to finding)
- Citing a source (link to external_evidence_source)
- Dismissing with reason (audit-traceable; "the new employee is a
  contractor; no NDA required per A.6.2 scope")

Implications past due_date flip to 'overdue' and surface red.

## How this fits the journey

Existing tenant-journey wizard ([[tenant-journey-wizard-2026-06-24]])
computes "next anchor to fill". With cascade:

- Pending implications get high priority in next-action recommendations
- "5 new employees onboarded → 5 training completions needed by Aug 5"
  becomes a concrete, actionable card

The journey backend evolves from "fill the next anchor template" to
"resolve the next pending implication". More operationally useful.

## When to build

NOT a near-term build. Sequence:

1. **Cite-mode v1** (next ~2 sessions) — provides changes_detected
   substrate. Without it, no triggers to fire from.
2. **Structured change events** (~1 session) — extends verification
   with event-type vocabulary; updates the verify dialog UI.
3. **Trigger catalog curation** (~1-2 sessions) — populate the
   declarative rules from the 7-8 example flows above. Same
   review discipline as document_requirements.py.
4. **Cascade engine + implications surface** (~2 sessions) —
   backend fires + tracks implications; UI surfaces them as
   "Triggered actions" panel; journey wizard integration.

Total ~5-6 sessions of work AFTER cite-mode v1. Each layer ships
independently and provides value on its own.

## Open design questions (defer to build-time)

- **Tenant customisation of triggers** — should a tenant be able to
  add/disable specific implications? (e.g. "we use contractors not
  employees; new personnel doesn't trigger A.6.2 NDA — they sign a
  different agreement"). Probably YES but it's a future flex.
- **Implication dependency chains** — can one implication trigger
  another? (e.g. completing the A.6.3 training row triggers an
  awareness-effectiveness review check). Probably DEFER — keep
  v1 flat.
- **Bulk implications** — "5 new employees" → 5 training rows
  needed. Surfaced as a single card "5 training rows" or 5 separate?
  Probably grouped by trigger event for UI clarity.
- **Tenant who SKIPS structured events** — they only write free-text
  changes_detected. No cascade fires. That's fine — they get the
  audit trail but not the proactive nudges. Adoption is gradual.

## What's NOT in scope (even at full build)

- **Automated remediation** — system fires implication but doesn't
  auto-create the artifact. Tenant must take the action.
- **Cross-tenant triggers** — implications are scoped per tenant.
- **External system pushes** — system doesn't push to Workday "this
  employee needs training assignment". External systems are sources,
  not sinks (in v1).

## Related

- [[product-principle-evidence-stored-vs-cited]] — cite-mode v1
  provides the changes_detected substrate
- [[cross-framework-bridge-footer-2026-06-14]] — xfw_bridge is the
  static cousin of this active cascade mechanism
- [[xfw-proposer]] (related — same Neo4j IMPLEMENTS infrastructure)
- [[tenant-journey-wizard-2026-06-24]] — implications enrich the
  journey backend's next-action recommendations
- [[per-must-advisory-2026-06-14]] — implications surface in the
  advisory panel as "this MUST is implicated by recent change X"
