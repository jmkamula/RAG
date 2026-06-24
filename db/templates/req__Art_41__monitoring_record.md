---
leaf_id: req:Art.41:monitoring_record
control_ref: Art.41
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Code Monitoring Activity Record

> Per-monitoring activity record — assessments, complaint handlings, infringement actions (Art.41.4). Annual refresh (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row adherent monitored

<<MUST item:Art.41:reg_adherent>>
_Why: Audit_

<<TEXT>>

## 2. Per-row activity (eligibility check / periodic monitoring / complaint / infringement action)

<<MUST item:Art.41:reg_activity_type>>
_Why: Art.41.2-4_

<<TEXT>>

## 3. Per-row outcome (compliant / non-compliant — corrective / suspension / exclusion per Art.41.4)

<<MUST item:Art.41:reg_outcome>>
_Why: Art.41.4_

<<TEXT>>

## 4. Per-row SA notification where Art.41.4 actions taken

<<MUST item:Art.41:reg_sa_notification>>
_Why: Art.41.4_

<<TEXT>>

## 5. Per-row activity date

<<MUST item:Art.41:reg_date>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row appeal handling where adherent contests the outcome

<<SHOULD item:Art.41:reg_appeal>>
_Why: Procedural fairness_

<<TEXT>>
