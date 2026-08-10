---
leaf_id: req:4.1:context_program_review
control_ref: 4.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Context Program Review

<<DOC_CONTROL>>

> Annual verification that the issues register reflects current reality, the identification framework is being followed, and the scope still bounds the right domains (freshness=365)

<!-- TABLE-COLUMNS leaf:req:4.1:context_program_review -->
<!-- column: item:4.1:rev_date -->
<!-- column: item:4.1:rev_reviewer -->
<!-- column: item:4.1:rev_register_currency -->
<!-- column: item:4.1:rev_risk_handoff -->
<!-- column: item:4.1:rev_scope_check -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your issues register is up to date, your identification process is being followed, and your program scope is still accurate. It’s designed to support annual reviews for ISO 27001 compliance.

## When to use it

Use this template once a year to review your program context, ensuring your register and scope are current and correct. It applies to every environment and should be refreshed annually.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this from scratch, depending on the number of required elements and the amount of information in your register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.1:context_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Risk Handoff | Rev Scope Check |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.1:context_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:4.1:rev_date>>
_Why: Clause 4.1 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:4.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + executive sponsor)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:4.1:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every row reviewed for continued relevance, new issues added

<<GUIDANCE>>

### Rev Risk Handoff

<<MUST item:4.1:rev_risk_handoff>>
_Why: Closes the loop_

> _Standard text:_ Confirmation that handoff to 6.1.2 risk assessment occurred for material issues

<<GUIDANCE>>

### Rev Scope Check

<<MUST item:4.1:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-domains scope — any new domain that should be covered

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:4.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
