---
leaf_id: req:A.5.8:project_security_closure_record
control_ref: A.5.8
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Per-Project Security Closure Record

> A.5.8 expects each project to formally close out security — not just go-live and dissolve the team. The closure record evidences the handover gate: project id, gates passed, outstanding risks transferred to operations with named owner, security artefacts archived, and final signoff. One record per closed project, traceable back to the project register and through to operational ownership

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Project identifier per record (links to project register)

<<MUST item:A.5.8:cls_project_ref>>
_Why: 27002:5.8 — traceability_

<<TEXT>>

## 2. Gates-passed summary per record (which gates closed and when; gaps explicitly noted with risk acceptance)

<<MUST item:A.5.8:cls_gates_passed>>
_Why: 27002:5.8 — lifecycle closure_

<<TEXT>>

## 3. Residual-risk register transfer per record (outstanding risks named, accepted by named operational owner with date)

<<MUST item:A.5.8:cls_residual_risks>>
_Why: 27002:5.8 — risk acceptance + transfer_

<<TEXT>>

## 4. Security artefacts archived per record (threat model, pen-test report, DPIA where applicable, exception register)

<<MUST item:A.5.8:cls_artefacts_archived>>
_Why: Audit defensibility_

<<TEXT>>

## 5. Final signoff per record (project sponsor + InfoSec gate-owner + operational owner — three-way)

<<MUST item:A.5.8:cls_signoff>>
_Why: 27002:5.8 — closure handover_

<<TEXT>>

## 6. Closure date recorded

<<MUST item:A.5.8:cls_closure_date>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Supplier-agreement handover per record where project introduced new third-party contracts (operational owner takes A.5.22 review duty)

<<SHOULD item:A.5.8:cls_supplier_handover>>
_Why: Closing loop with [[A.5.22]]_

<<TEXT>>

### 2. Lessons-learned link per record where project surfaced patterns worth feeding into A.5.27 lessons register

<<SHOULD item:A.5.8:cls_lessons_link>>
_Why: Closing loop with [[A.5.27]]_

<<TEXT>>
