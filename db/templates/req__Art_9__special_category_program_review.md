---
leaf_id: req:Art.9:special_category_program_review
control_ref: Art.9
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Special Category Program Review

<<DOC_CONTROL>>

> Annual verification that every Art.9 processing activity has a current Art.9.2 condition justification, safeguards are in place, no quiet onboarding happened (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.9:special_category_program_review -->
<!-- column: item:Art.9:rev_date -->
<!-- column: item:Art.9:rev_reviewer -->
<!-- column: item:Art.9:rev_register_currency -->
<!-- column: item:Art.9:rev_safeguards_audit -->
<!-- column: item:Art.9:rev_silent_onboarding -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of all your processing activities involving special category data, making sure each one has a valid legal basis and the right safeguards in place.

## When to use it

Use this template once a year if your organization handles special category data under GDPR, especially when your activities match certain risk or profile triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours completing this from scratch, depending on the number of activities you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.9:special_category_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Safeguards Audit | Rev Silent Onboarding |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.9:special_category_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.9:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + executive sponsor)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:Art.9:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every active activity has its Art.9.2 condition still appropriate

<<GUIDANCE>>

### Rev Safeguards Audit

<<MUST item:Art.9:rev_safeguards_audit>>
_Why: Art.9.3_

> _Standard text:_ Safeguards audit — Art.9.3 secrecy obligations being enforced (where Art.9.2.h-i applies)

<<GUIDANCE>>

### Rev Silent Onboarding

<<MUST item:Art.9:rev_silent_onboarding>>
_Why: Art.9.1 — prohibition default_

> _Standard text:_ Silent-onboarding sweep — verify no new special-category data ingested without the procedure being invoked

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
