---
leaf_id: req:A.5.27:improvement_action_record
control_ref: A.5.27
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Per-Lesson Improvement Action Records

> A.5.27 expects lessons to actually strengthen and improve controls — not just be captured in a register. The improvement-action record evidences the actual loop-closure: which lesson, what was changed (control updated / training added / procedure amended / risk formally accepted), proof of the change, authoriser and closure date. One record per closed lesson, traceable back to the lessons register and through to the source incident

<!-- TABLE-COLUMNS leaf:req:A.5.27:improvement_action_record -->
<!-- column: item:A.5.27:imp_lesson_ref -->
<!-- column: item:A.5.27:imp_action_type -->
<!-- column: item:A.5.27:imp_evidence -->
<!-- column: item:A.5.27:imp_authoriser -->
<!-- column: item:A.5.27:imp_closure_date -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.27:improvement_action_record -->
| Imp Lesson Ref | Imp Action Type | Imp Evidence | Imp Authoriser | Imp Closure Date |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.27:improvement_action_record -->

## Column guidance — what to fill in

### Imp Lesson Ref

<<MUST item:A.5.27:imp_lesson_ref>>
_Why: 27002:5.27 — knowledge applied_

> _Standard text:_ Lesson identifier per record (links to lessons register)

### Imp Action Type

<<MUST item:A.5.27:imp_action_type>>
_Why: 27002:5.27a,c,d_

> _Standard text:_ Action type captured (control updated / training added / procedure amended / risk accepted)

### Imp Evidence

<<MUST item:A.5.27:imp_evidence>>
_Why: 27002:5.27a — actual improvement_

> _Standard text:_ Evidence of change (control configuration diff, training-record entry, procedure-revision link, risk-register entry)

### Imp Authoriser

<<MUST item:A.5.27:imp_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser per record (proportional to scope of the change)

### Imp Closure Date

<<MUST item:A.5.27:imp_closure_date>>
_Why: 27002:5.27a — tracking_

> _Standard text:_ Closure date recorded

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Imp Effectiveness

<<SHOULD item:A.5.27:imp_effectiveness>>
_Why: Continual improvement_

> _Standard text:_ Effectiveness check planned or done (post-update validation that the change actually addressed the root cause)

### Imp Regression

<<SHOULD item:A.5.27:imp_regression>>
_Why: Operational discipline_

> _Standard text:_ Regression-prevention check (where the change replaced a previous control, verify the prior failure mode no longer applies)
