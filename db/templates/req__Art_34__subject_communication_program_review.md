---
leaf_id: req:Art.34:subject_communication_program_review
control_ref: Art.34
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.34 Subject Communication Program Review

<<DOC_CONTROL>>

> Annual verification — high-risk decisions defensible, exceptions applied appropriately, communication content meets Art.34.2 (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.34:subject_communication_program_review -->
<!-- column: item:Art.34:rev_date -->
<!-- column: item:Art.34:rev_reviewer -->
<!-- column: item:Art.34:rev_decision_defensibility -->
<!-- column: item:Art.34:rev_exception_audit -->
<!-- column: item:Art.34:rev_content_quality -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review how you communicate with individuals about high-risk decisions, ensuring your process meets GDPR Article 34 requirements and that any exceptions are properly justified.

## When to use it

Use this template whenever your organization makes high-risk decisions that require communication under GDPR Article 34, and review or update it about once a year to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, depending on the number of cases you need to document and the detail required for each element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.34:subject_communication_program_review -->
| Rev Date | Rev Reviewer | Rev Decision Defensibility | Rev Exception Audit | Rev Content Quality |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.34:subject_communication_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.34:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.34:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal + incident-response lead)

<<GUIDANCE>>

### Rev Decision Defensibility

<<MUST item:Art.34:rev_decision_defensibility>>
_Why: Art.34.1_

> _Standard text:_ High-risk decision defensibility — sampled decisions reviewed against criteria

<<GUIDANCE>>

### Rev Exception Audit

<<MUST item:Art.34:rev_exception_audit>>
_Why: Art.34.3_

> _Standard text:_ Exception-claim audit — Art.34.3 exception claims reviewed for legitimacy (especially encryption-deemed-appropriate where keys may also have been compromised)

<<GUIDANCE>>

### Rev Content Quality

<<MUST item:Art.34:rev_content_quality>>
_Why: Art.34.2_

> _Standard text:_ Content-quality audit — communications used plain language, included DPO contact, described concrete measures

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.34:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
