---
leaf_id: req:A.7.3.8:program_review
control_ref: A.7.3.8
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Copy Provision Program Review

<<DOC_CONTROL>>

> Annual verification — copy formats current, scope-restriction enforced, direct-transfer capability tested, SLAs met (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.8:program_review -->
<!-- column: item:A.7.3.8:rev_date -->
<!-- column: item:A.7.3.8:rev_reviewer -->
<!-- column: item:A.7.3.8:rev_scope_leakage_test -->
<!-- column: item:A.7.3.8:rev_format_currency -->
<!-- column: item:A.7.3.8:rev_direct_transfer_test -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review how your copy provision processes meet privacy requirements, including format checks, scope restrictions, transfer capabilities, and service level agreements.

## When to use it

Use this template when your organization’s profile matches certain privacy triggers and you need to complete an annual review, typically once every 12 months.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes filling this out from scratch, as each required section takes around 10-15 minutes to complete.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.8:program_review -->
| Rev Date | Rev Reviewer | Rev Scope Leakage Test | Rev Format Currency | Rev Direct Transfer Test |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.8:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.8:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.8:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Engineering)

<<GUIDANCE>>

### Rev Scope Leakage Test

<<MUST item:A.7.3.8:rev_scope_leakage_test>>
_Why: §7.3.8 — relate specifically_

> _Standard text:_ Scope-leakage test — sampled copies verified to contain only the requesting subject's PII

<<GUIDANCE>>

### Rev Format Currency

<<MUST item:A.7.3.8:rev_format_currency>>
_Why: §7.3.8 — commonly used format_

> _Standard text:_ Format currency — output format aligns with commonly-used industry standards

<<GUIDANCE>>

### Rev Direct Transfer Test

<<MUST item:A.7.3.8:rev_direct_transfer_test>>
_Why: Art.20.2_

> _Standard text:_ Direct-transfer capability tested end-to-end

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.8:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
