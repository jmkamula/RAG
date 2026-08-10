---
leaf_id: req:4.2:parties_program_review
control_ref: 4.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Interested Parties Program Review

<<DOC_CONTROL>>

> Annual verification that the parties register reflects current reality, the framework is being followed, and the scope still bounds the right categories (freshness=365)

<!-- TABLE-COLUMNS leaf:req:4.2:parties_program_review -->
<!-- column: item:4.2:rev_date -->
<!-- column: item:4.2:rev_reviewer -->
<!-- column: item:4.2:rev_register_currency -->
<!-- column: item:4.2:rev_requirements_currency -->
<!-- column: item:4.2:rev_scope_check -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep an up-to-date record of all interested parties relevant to your information security program, ensuring your register reflects current relationships and responsibilities.

## When to use it

Use this review record once a year to confirm your list of interested parties is accurate and that your program’s scope and framework still fit your organization’s needs.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many parties you need to review and update.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:4.2:parties_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Requirements Currency | Rev Scope Check |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:4.2:parties_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:4.2:rev_date>>
_Why: Clause 4.2 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:4.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + executive sponsor)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:4.2:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every party row reviewed for continued relevance, new parties added

<<GUIDANCE>>

### Rev Requirements Currency

<<MUST item:4.2:rev_requirements_currency>>
_Why: Critical for compliance currency_

> _Standard text:_ Requirements currency check — regulator updates, contract amendments swept in

<<GUIDANCE>>

### Rev Scope Check

<<MUST item:4.2:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-domains scope — any new category that should be covered

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:4.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
