---
leaf_id: req:A.8.32:change_management_procedure
control_ref: A.8.32
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 1
---

# Change Management Procedure

> A.8.32 requires changes to information processing facilities + systems subject to CM procedures. Procedure documents scope, approval workflow, risk-assessment-per-change, rollback, emergency-change path, post-implementation review. Per-change register (lifecycle-end), applicable scope, program review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope — which change classes require formal CM (production / customer-facing / security-relevant / cross-system)

<<MUST item:A.8.32:scope>>
_Why: 27002:8.32 — changes subject to change management_

<<TEXT>>

## 2. Change approval workflow (CAB / lightweight async approval / automated approval per risk tier)

<<MUST item:A.8.32:approval>>
_Why: 27002:8.32 — change management procedures_

<<TEXT>>

## 3. Per-change risk assessment (impact / blast radius / rollback complexity)

<<MUST item:A.8.32:risk_assessment>>
_Why: 27002:8.32 — change management_

<<TEXT>>

## 4. Rollback plan required per change (no-rollback changes treated as exceptions)

<<MUST item:A.8.32:rollback>>
_Why: 27002:8.32 — change management_

<<TEXT>>

## 5. Emergency-change provisions with mandatory post-hoc review (no untracked emergencies)

<<MUST item:A.8.32:emergency>>
_Why: Operational reality_

<<TEXT>>

## 6. Post-implementation review for significant changes (learning loop into procedure)

<<MUST item:A.8.32:pir>>
_Why: Continuous improvement_

<<TEXT>>

## 7. CI/CD pipeline integration for low-risk automated changes (modern baseline; CAB-everything bottleneck not acceptable)

<<MUST item:A.8.32:ci_integration>>
_Why: Modern velocity (Style v2 promotion)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Defined change windows for non-emergency changes

<<SHOULD item:A.8.32:change_windows>>
_Why: Predictability_

<<TEXT>>
