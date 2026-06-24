---
leaf_id: req:A.6.3:training_completion_register
control_ref: A.6.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Training Completion Register

> The operational catalogue of who has completed which training, when. Each row: personnel identifier, training module, completion date, quiz score (where applicable), next-due date. Drives the audit-defensibility 'show me every active employee completed mandatory training this year' query

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row personnel identifier (links to identity register A.5.16)

<<MUST item:A.6.3:reg_personnel_id>>
_Why: Accountability_

<<TEXT>>

## 2. Per-row training module identifier (links to the curriculum catalogue)

<<MUST item:A.6.3:reg_module_id>>
_Why: 27002:6.3 — curriculum_

<<TEXT>>

## 3. Per-row completion date

<<MUST item:A.6.3:reg_completion_date>>
_Why: Audit defensibility_

<<TEXT>>

## 4. Per-row next-due date (drives reminder/escalation workflow)

<<MUST item:A.6.3:reg_next_due>>
_Why: 27002:6.3 — regular updates_

<<TEXT>>

## 5. Per-row status (current / overdue / waived-with-reason / N/A — for role change exemptions)

<<MUST item:A.6.3:reg_status>>
_Why: Operational discipline_

<<TEXT>>

## 6. Per-row score where the module includes assessment (drives effectiveness metrics)

<<MUST item:A.6.3:reg_score>>
_Why: 27002:6.3 — effectiveness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row phishing simulation participation log (separate from formal training — drives awareness metrics)

<<SHOULD item:A.6.3:reg_phishing_sim_log>>
_Why: Continuous improvement_

<<TEXT>>

### 2. Overdue-status alerting (notification to line manager when training crosses next-due date)

<<SHOULD item:A.6.3:reg_overdue_alerts>>
_Why: Operational discipline_

<<TEXT>>
