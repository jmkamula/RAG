---
leaf_id: req:Art.43:cert_body_program_review
control_ref: Art.43
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Cert Body Program Review

<<DOC_CONTROL>>

> Annual verification — accreditation current, issuances criteria-aligned, complaints handled (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.43:cert_body_program_review -->
<!-- column: item:Art.43:rev_date -->
<!-- column: item:Art.43:rev_reviewer -->
<!-- column: item:Art.43:rev_accreditation_currency -->
<!-- column: item:Art.43:rev_issuance_audit -->
<!-- column: item:Art.43:rev_complaint_handling -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record showing your accreditation is up to date, your certification decisions follow the right criteria, and any complaints are handled properly.

## When to use it

Use this review record once a year, or whenever your certification body profile changes in a way that requires a fresh compliance check under GDPR Article 43.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on how many entries you need to add to the register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.43:cert_body_program_review -->
| Rev Date | Rev Reviewer | Rev Accreditation Currency | Rev Issuance Audit | Rev Complaint Handling |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.43:cert_body_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.43:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.43:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (executive sponsor + independent counsel)

<<GUIDANCE>>

### Rev Accreditation Currency

<<MUST item:Art.43:rev_accreditation_currency>>
_Why: Art.43.1_

> _Standard text:_ Accreditation currency — SA / NAB accreditation still in force

<<GUIDANCE>>

### Rev Issuance Audit

<<MUST item:Art.43:rev_issuance_audit>>
_Why: Art.43.5_

> _Standard text:_ Issuance audit — sampled decisions reviewed against published criteria (Art.43.5)

<<GUIDANCE>>

### Rev Complaint Handling

<<MUST item:Art.43:rev_complaint_handling>>
_Why: Art.43.2.d_

> _Standard text:_ Complaint handling audit — complaints processed within fair procedural standards

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.43:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
