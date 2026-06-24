---
leaf_id: req:A.5.22:change_response_log
control_ref: A.5.22
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Supplier Service Change Response Log

> A.5.22 requires the org to manage changes in supplier service delivery — network/tech changes, new dev tools, location changes, change of sub-contractors, re-tendering. Each change is evidenced by a log entry: change type captured, impact assessed, treatment decided, with escalation to termination where findings warrant

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Change type captured (network / technology / dev tools / location / sub-contractor / re-tendering)

<<MUST item:A.5.22:chg_type>>
_Why: 27002:5.22k_

<<TEXT>>

## 2. Impact assessment on InfoSec arrangements (which controls affected, which threats opened or closed)

<<MUST item:A.5.22:chg_impact>>
_Why: 27002:5.22k_

<<TEXT>>

## 3. Treatment decided (accept / mitigate / re-paper agreement / terminate relationship)

<<MUST item:A.5.22:chg_treatment>>
_Why: 27002:5.22k_

<<TEXT>>

## 4. Escalation criteria for findings — when a finding terminates the relationship

<<MUST item:A.5.22:chg_escalation>>
_Why: 27002:5.22j,k_

<<TEXT>>

## 5. Authoriser of the treatment decision (proportional to residual risk)

<<MUST item:A.5.22:chg_authoriser>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Regulatory-notification check (where the change triggers a regulator-notify obligation)

<<SHOULD item:A.5.22:chg_regulatory>>
_Why: 27002:5.22 — compliance_

<<TEXT>>

### 2. Lessons-learned feeding back to the procedure or template (link to A.5.19 / A.5.20)

<<SHOULD item:A.5.22:chg_lessons>>
_Why: Continual improvement_

<<TEXT>>
