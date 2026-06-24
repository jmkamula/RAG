---
leaf_id: req:A.5.27:improvement_action_record
control_ref: A.5.27
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Per-Lesson Improvement Action Records

> A.5.27 expects lessons to actually strengthen and improve controls — not just be captured in a register. The improvement-action record evidences the actual loop-closure: which lesson, what was changed (control updated / training added / procedure amended / risk formally accepted), proof of the change, authoriser and closure date. One record per closed lesson, traceable back to the lessons register and through to the source incident

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Lesson identifier per record (links to lessons register)

<<MUST item:A.5.27:imp_lesson_ref>>
_Why: 27002:5.27 — knowledge applied_

<<TEXT>>

## 2. Action type captured (control updated / training added / procedure amended / risk accepted)

<<MUST item:A.5.27:imp_action_type>>
_Why: 27002:5.27a,c,d_

<<TEXT>>

## 3. Evidence of change (control configuration diff, training-record entry, procedure-revision link, risk-register entry)

<<MUST item:A.5.27:imp_evidence>>
_Why: 27002:5.27a — actual improvement_

<<TEXT>>

## 4. Authoriser per record (proportional to scope of the change)

<<MUST item:A.5.27:imp_authoriser>>
_Why: Accountability_

<<TEXT>>

## 5. Closure date recorded

<<MUST item:A.5.27:imp_closure_date>>
_Why: 27002:5.27a — tracking_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Effectiveness check planned or done (post-update validation that the change actually addressed the root cause)

<<SHOULD item:A.5.27:imp_effectiveness>>
_Why: Continual improvement_

<<TEXT>>

### 2. Regression-prevention check (where the change replaced a previous control, verify the prior failure mode no longer applies)

<<SHOULD item:A.5.27:imp_regression>>
_Why: Operational discipline_

<<TEXT>>
