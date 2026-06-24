---
leaf_id: req:A.8.34:audit_testing_program_review
control_ref: A.8.34
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Audit Testing Protection Program Review

> Annual verification — register completeness, rollback-discipline compliance, evidence-preservation hygiene (freshness=365; audit-policy stable as documented in batch header)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.34:rev_date>>
_Why: 27002:8.34 — periodic_

<<TEXT>>

## 2. Reviewer identity (InfoSec lead + Internal Audit lead)

<<MUST item:A.8.34:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register-completeness check (every recent audit engagement in register)

<<MUST item:A.8.34:rev_register_completeness>>
_Why: Drift prevention_

<<TEXT>>

## 4. Rollback-discipline compliance (no untracked changes introduced during testing)

<<MUST item:A.8.34:rev_rollback_compliance>>
_Why: 27002:8.34 — protection_

<<TEXT>>

## 5. Evidence-preservation hygiene check (artefacts retained per chain-of-custody)

<<MUST item:A.8.34:rev_evidence_hygiene>>
_Why: Defensibility_

<<TEXT>>

## 6. Findings propagated to policy / scope

<<MUST item:A.8.34:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.34:rev_next_date>>
_Why: Planning_

<<TEXT>>
