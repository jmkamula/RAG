---
leaf_id: req:7.3:awareness_completion_register
control_ref: 7.3
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# ISMS Awareness Completion Register

> Per-person completion record — who completed which module, on what date, with what acknowledgement. The proof that awareness was actually delivered, not just designed. Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Subject identifier per row (employee or contractor)

<<MUST item:7.3:reg_subject_id>>
_Why: Accountability_

<<TEXT>>

## 2. Module identifier per row (policy module, contribution module, consequences module)

<<MUST item:7.3:reg_module>>
_Why: Coverage_

<<TEXT>>

## 3. Completion date per row

<<MUST item:7.3:reg_completion_date>>
_Why: Currency_

<<TEXT>>

## 4. Acknowledgement per row (signed receipt, LMS attestation, quiz pass)

<<MUST item:7.3:reg_acknowledgement>>
_Why: Evidence preservation_

<<TEXT>>

## 5. Expiry / next-due date per row (drives refresher trigger)

<<MUST item:7.3:reg_expiry>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row assessment score where the module included a knowledge check

<<SHOULD item:7.3:reg_assessment_score>>
_Why: Effectiveness signal_

<<TEXT>>
