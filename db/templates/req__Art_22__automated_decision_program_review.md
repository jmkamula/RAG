---
leaf_id: req:Art.22:automated_decision_program_review
control_ref: Art.22
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Automated Decision-Making Program Review

<<DOC_CONTROL>>

> Annual verification — every in-scope system has a current Art.22.2 basis, safeguards functioning, DPIAs current, objections handled (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.22:automated_decision_program_review -->
<!-- column: item:Art.22:rev_date -->
<!-- column: item:Art.22:rev_reviewer -->
<!-- column: item:Art.22:rev_basis_currency -->
<!-- column: item:Art.22:rev_safeguards_health -->
<!-- column: item:Art.22:rev_silent_promotion -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your automated decision-making systems, ensuring you meet GDPR Article 22 requirements and have up-to-date records of legal basis, safeguards, DPIAs, and how objections are handled.

## When to use it

Use this template whenever your organization operates systems that make automated decisions about individuals, and review it about once a year or whenever significant changes occur.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on the number of systems you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.22:automated_decision_program_review -->
| Rev Date | Rev Reviewer | Rev Basis Currency | Rev Safeguards Health | Rev Silent Promotion |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.22:automated_decision_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.22:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.22:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + ML/product lead)

<<GUIDANCE>>

### Rev Basis Currency

<<MUST item:Art.22:rev_basis_currency>>
_Why: Art.22.2_

> _Standard text:_ Basis currency check — every in-scope system still has valid Art.22.2 basis

<<GUIDANCE>>

### Rev Safeguards Health

<<MUST item:Art.22:rev_safeguards_health>>
_Why: Art.22.3_

> _Standard text:_ Safeguards health — human intervention queue actually used, contest mechanism functioning

<<GUIDANCE>>

### Rev Silent Promotion

<<MUST item:Art.22:rev_silent_promotion>>
_Why: Drift detection_

> _Standard text:_ Silent-promotion sweep — verify no flag-for-review system has been quietly promoted to solely-automated without procedure update

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.22:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
