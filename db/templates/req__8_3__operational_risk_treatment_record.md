---
leaf_id: req:8.3:operational_risk_treatment_record
control_ref: 8.3
standard_id: ISO27001:2022
evidence_type: risk_treatment_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 1
---

# Operational Risk Treatment Records

> Clause 8.3 requires the organisation to implement the 6.1.3 treatment plan and retain documented information of results. Per-treatment-item records are the canonical artefact. Sibling leaves: execution procedure, applicable plan-items scope, program review. Operational freshness (180d)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Treatment plan from 6.1.3 being implemented (status per item)

<<MUST item:8.3:plan_implemented>>
_Why: Clause 8.3 — implement the information security risk treatment plan_

<<TEXT>>

## 2. Implementation status per treatment item (planned, in-progress, complete, deferred)

<<MUST item:8.3:implementation_status>>
_Why: Clause 8.3 — implementation_

<<TEXT>>

## 3. Residual risk recorded after treatment

<<MUST item:8.3:residual_risk>>
_Why: Clause 8.3 — results_

<<TEXT>>

## 4. Documented information of results retained

<<MUST item:8.3:retention>>
_Why: Clause 8.3 — retain documented information of the results_

<<TEXT>>

## 5. Per-treatment-item owner identified

<<MUST item:8.3:per_item_owner>>
_Why: Accountability_

<<TEXT>>

## 6. Per-treatment-item target completion date

<<MUST item:8.3:per_item_target_date>>
_Why: Tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Link to Statement of Applicability for control selection rationale

<<SHOULD item:8.3:soa_link>>
_Why: Audit traceability_

<<TEXT>>
