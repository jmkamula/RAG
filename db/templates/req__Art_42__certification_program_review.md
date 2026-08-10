---
leaf_id: req:Art.42:certification_program_review
control_ref: Art.42
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Certification Program Review

<<DOC_CONTROL>>

> Annual verification — certifications current, surveillance audits passing, renewal on track (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.42:certification_program_review -->
<!-- column: item:Art.42:rev_date -->
<!-- column: item:Art.42:rev_reviewer -->
<!-- column: item:Art.42:rev_validity_audit -->
<!-- column: item:Art.42:rev_surveillance_status -->
<!-- column: item:Art.42:rev_business_case_recheck -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your GDPR certification status, ensuring your certifications are current, audits are successful, and renewals are on schedule.

## When to use it

Use this review record once a year, or whenever your organization meets certain criteria that require a certification program check, to confirm ongoing compliance with GDPR Article 42.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, as each required section takes some time to fill out thoroughly.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.42:certification_program_review -->
| Rev Date | Rev Reviewer | Rev Validity Audit | Rev Surveillance Status | Rev Business Case Recheck |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.42:certification_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.42:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.42:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + executive sponsor)

<<GUIDANCE>>

### Rev Validity Audit

<<MUST item:Art.42:rev_validity_audit>>
_Why: Art.42.7_

> _Standard text:_ Validity audit — every active certification still in validity period; renewal in flight where approaching expiry

<<GUIDANCE>>

### Rev Surveillance Status

<<MUST item:Art.42:rev_surveillance_status>>
_Why: Lifecycle_

> _Standard text:_ Surveillance status — most-recent surveillance audit outcome reviewed

<<GUIDANCE>>

### Rev Business Case Recheck

<<MUST item:Art.42:rev_business_case_recheck>>
_Why: Defensibility_

> _Standard text:_ Business case recheck — certification still providing value (transfer enablement / customer requirement / market position)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.42:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
