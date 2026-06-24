---
leaf_id: req:A.6.4:disciplinary_case_register
control_ref: A.6.4
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Disciplinary Case Register

> The operational catalogue of disciplinary cases (anonymised at the audit-trail layer to comply with privacy requirements). Each case: violation type, investigation outcome, action taken, decision authority, closure date. Drives the 'show me how the disciplinary process actually operates' audit question

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-case unique identifier (anonymised externally; internal traceability to personnel record preserved)

<<MUST item:A.6.4:reg_case_id>>
_Why: Audit defensibility_

<<TEXT>>

## 2. Per-case violation type (matches the procedure's violation_scope categories)

<<MUST item:A.6.4:reg_violation_type>>
_Why: 27002:6.4 — categorisation_

<<TEXT>>

## 3. Per-case investigation outcome (substantiated / not-substantiated / partially-substantiated)

<<MUST item:A.6.4:reg_investigation_outcome>>
_Why: 27002:6.4 — investigation_

<<TEXT>>

## 4. Per-case action taken (matches the action_range categories; 'no action' is a valid outcome where investigation didn't substantiate)

<<MUST item:A.6.4:reg_action_taken>>
_Why: 27002:6.4 — actions_

<<TEXT>>

## 5. Per-case decision authority (named role)

<<MUST item:A.6.4:reg_decision_authority>>
_Why: Accountability_

<<TEXT>>

## 6. Per-case closure date

<<MUST item:A.6.4:reg_closure_date>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-case appeals log (where appeal was lodged; status tracked)

<<SHOULD item:A.6.4:reg_appeals_log>>
_Why: Fair process_

<<TEXT>>

### 2. Per-case lessons feed (where the violation surfaced a control gap, feeds back to relevant control owner / awareness curriculum)

<<SHOULD item:A.6.4:reg_lessons_feed>>
_Why: Continual improvement_

<<TEXT>>
