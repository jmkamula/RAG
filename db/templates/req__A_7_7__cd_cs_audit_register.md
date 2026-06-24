---
leaf_id: req:A.7.7:cd_cs_audit_register
control_ref: A.7.7
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Clear Desk / Clear Screen Audit Register

> The catalogue of spot-check audits with findings. Each audit row: date, scope, findings, sanctions applied

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-audit unique identifier

<<MUST item:A.7.7:reg_audit_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-audit date

<<MUST item:A.7.7:reg_date>>
_Why: Operational discipline_

<<TEXT>>

## 3. Per-audit scope (which floors / areas covered)

<<MUST item:A.7.7:reg_scope>>
_Why: 27002:7.7 — appropriately enforced_

<<TEXT>>

## 4. Per-audit findings (count of violations, types observed)

<<MUST item:A.7.7:reg_findings>>
_Why: Operational discipline_

<<TEXT>>

## 5. Per-audit remediation log (awareness email sent, repeat-violator escalation)

<<MUST item:A.7.7:reg_remediation>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-audit trend analysis (vs previous audit — improvement / worsening / steady)

<<SHOULD item:A.7.7:reg_trend>>
_Why: Continual improvement_

<<TEXT>>
