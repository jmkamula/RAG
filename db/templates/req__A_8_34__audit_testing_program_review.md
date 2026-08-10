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
table_shape: true
---

# Periodic Audit Testing Protection Program Review

<<DOC_CONTROL>>

> Annual verification — register completeness, rollback-discipline compliance, evidence-preservation hygiene (freshness=365; audit-policy stable as documented in batch header)

<!-- TABLE-COLUMNS leaf:req:A.8.34:audit_testing_program_review -->
<!-- column: item:A.8.34:rev_date -->
<!-- column: item:A.8.34:rev_reviewer -->
<!-- column: item:A.8.34:rev_register_completeness -->
<!-- column: item:A.8.34:rev_rollback_compliance -->
<!-- column: item:A.8.34:rev_evidence_hygiene -->
<!-- column: item:A.8.34:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of audit testing protection, ensuring your register is complete and your evidence is up to date and well maintained.

## When to use it

Use this template once a year to record your periodic audit testing protection program review, as it applies to all environments and supports ISO 27001 compliance.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of required elements and the amount of information you need to gather.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.34:audit_testing_program_review -->
| Rev Date | Rev Reviewer | Rev Register Completeness | Rev Rollback Compliance | Rev Evidence Hygiene | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.34:audit_testing_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.34:rev_date>>
_Why: 27002:8.34 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.34:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (InfoSec lead + Internal Audit lead)

<<GUIDANCE>>

### Rev Register Completeness

<<MUST item:A.8.34:rev_register_completeness>>
_Why: Drift prevention_

> _Standard text:_ Register-completeness check (every recent audit engagement in register)

<<GUIDANCE>>

### Rev Rollback Compliance

<<MUST item:A.8.34:rev_rollback_compliance>>
_Why: 27002:8.34 — protection_

> _Standard text:_ Rollback-discipline compliance (no untracked changes introduced during testing)

<<GUIDANCE>>

### Rev Evidence Hygiene

<<MUST item:A.8.34:rev_evidence_hygiene>>
_Why: Defensibility_

> _Standard text:_ Evidence-preservation hygiene check (artefacts retained per chain-of-custody)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.34:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to policy / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.34:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
