---
leaf_id: req:Art.85:program_review
control_ref: Art.85
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.85 Derogation Program Review

<<DOC_CONTROL>>

> Annual verification that the national-law register is current per Member State, no in-scope activity is operating without a documented derogation basis, and any GDPR-Chapter changes have been reflected (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.85:program_review -->
<!-- column: item:Art.85:rev_date -->
<!-- column: item:Art.85:rev_reviewer -->
<!-- column: item:Art.85:rev_law_currency -->
<!-- column: item:Art.85:rev_scope_coverage -->
<!-- column: item:Art.85:rev_subject_rights_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your national-law register, ensuring all activities that need a derogation under GDPR Article 85 are properly documented and up to date.

## When to use it

Use this template if your organization’s activities might require a derogation under GDPR Article 85, especially when your profile matches certain criteria. Plan to review and update it about once a year.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of activities and updates needed for each required section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.85:program_review -->
| Rev Date | Rev Reviewer | Rev Law Currency | Rev Scope Coverage | Rev Subject Rights Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.85:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.85:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.85:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel + editorial/academic lead)

<<GUIDANCE>>

### Rev Law Currency

<<MUST item:Art.85:rev_law_currency>>
_Why: Art.85.2 — currency_

> _Standard text:_ Member State law currency check — every cited national-law provision still in force; new MS implementations swept in

<<GUIDANCE>>

### Rev Scope Coverage

<<MUST item:Art.85:rev_scope_coverage>>
_Why: Defensibility_

> _Standard text:_ Scope coverage — every in-scope activity has a derogation basis (or explicit decision to NOT invoke Art.85 for it)

<<GUIDANCE>>

### Rev Subject Rights Audit

<<MUST item:Art.85:rev_subject_rights_audit>>
_Why: Recital 153_

> _Standard text:_ Subject-rights audit — confirm derogations are not over-applied (residual rights still honoured where not legitimately derogated)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.85:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
