---
leaf_id: req:A.7.2.5:program_review
control_ref: A.7.2.5
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# PIA Program Review

<<DOC_CONTROL>>

> Annual verification — every triggered activity has a completed PIA, PIAs remain current, SA-consultation obligations honoured (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.5:program_review -->
<!-- column: item:A.7.2.5:rev_date -->
<!-- column: item:A.7.2.5:rev_reviewer -->
<!-- column: item:A.7.2.5:rev_coverage_check -->
<!-- column: item:A.7.2.5:rev_currency_audit -->
<!-- column: item:A.7.2.5:rev_sa_consultation_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your Privacy Impact Assessments (PIAs), making sure each required activity is reviewed and up to date, and that any necessary consultations have been completed.

## When to use it

Use this template whenever your activities meet the criteria for a PIA, and review it about once a year to ensure all information is current and obligations are met.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing the required sections from scratch, with additional time needed if you have multiple activities to register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.5:program_review -->
| Rev Date | Rev Reviewer | Rev Coverage Check | Rev Currency Audit | Rev Sa Consultation Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.5:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.5:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + risk owner)

<<GUIDANCE>>

### Rev Coverage Check

<<MUST item:A.7.2.5:rev_coverage_check>>
_Why: §7.2.5 — every new/changed processing_

> _Standard text:_ Coverage check — every triggered activity has a completed PIA on file

<<GUIDANCE>>

### Rev Currency Audit

<<MUST item:A.7.2.5:rev_currency_audit>>
_Why: §7.2.5 — changes to existing processing_

> _Standard text:_ Currency audit — PIAs older than currency threshold reviewed for material change

<<GUIDANCE>>

### Rev Sa Consultation Audit

<<MUST item:A.7.2.5:rev_sa_consultation_audit>>
_Why: Art.36.1_

> _Standard text:_ SA-consultation audit — high-residual-risk PIAs verified to have escalated where required

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
