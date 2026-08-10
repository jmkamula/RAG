---
leaf_id: req:B.8.2.2:program_review
control_ref: B.8.2.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Purpose Adherence Program Review

<<DOC_CONTROL>>

> Annual verification — technical bindings enforce customer purposes, no side-purpose drift, customer-verification pathways functional (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.2:program_review -->
<!-- column: item:B.8.2.2:rev_date -->
<!-- column: item:B.8.2.2:rev_reviewer -->
<!-- column: item:B.8.2.2:rev_technical_binding_audit -->
<!-- column: item:B.8.2.2:rev_side_purpose_sweep -->
<!-- column: item:B.8.2.2:rev_customer_verification_health -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of how your technical controls ensure customer data is used only for its intended purpose, with clear checks against unintended use and working customer verification options.

## When to use it

Use this review record if your operations require annual confirmation that your systems enforce customer data purposes, especially when your profile matches certain risk or compliance triggers.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of required elements and the amount of detail needed for each section.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.2:program_review -->
| Rev Date | Rev Reviewer | Rev Technical Binding Audit | Rev Side Purpose Sweep | Rev Customer Verification Health |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.2.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.2.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Engineering Lead + Compliance)

<<GUIDANCE>>

### Rev Technical Binding Audit

<<MUST item:B.8.2.2:rev_technical_binding_audit>>
_Why: §8.2.2 — only processed for purposes_

> _Standard text:_ Technical binding audit — sampled tenant boundaries verified to enforce purpose limits

<<GUIDANCE>>

### Rev Side Purpose Sweep

<<MUST item:B.8.2.2:rev_side_purpose_sweep>>
_Why: §8.2.2 — no purposes other than expressed_

> _Standard text:_ Side-purpose drift sweep — cross-tenant analytics + ML training pipelines checked for unauthorised customer-PII use

<<GUIDANCE>>

### Rev Customer Verification Health

<<MUST item:B.8.2.2:rev_customer_verification_health>>
_Why: §8.2.2 — allow customer to verify_

> _Standard text:_ Customer verification health — audits requested + supported within stated SLA

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
