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

> Annual verification — technical bindings enforce customer purposes, no side-purpose drift, customer-verification pathways functional (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.2:program_review -->
<!-- column: item:B.8.2.2:rev_date -->
<!-- column: item:B.8.2.2:rev_reviewer -->
<!-- column: item:B.8.2.2:rev_technical_binding_audit -->
<!-- column: item:B.8.2.2:rev_side_purpose_sweep -->
<!-- column: item:B.8.2.2:rev_customer_verification_health -->
<!-- /TABLE-COLUMNS -->

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

### Rev Reviewer

<<MUST item:B.8.2.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Engineering Lead + Compliance)

### Rev Technical Binding Audit

<<MUST item:B.8.2.2:rev_technical_binding_audit>>
_Why: §8.2.2 — only processed for purposes_

> _Standard text:_ Technical binding audit — sampled tenant boundaries verified to enforce purpose limits

### Rev Side Purpose Sweep

<<MUST item:B.8.2.2:rev_side_purpose_sweep>>
_Why: §8.2.2 — no purposes other than expressed_

> _Standard text:_ Side-purpose drift sweep — cross-tenant analytics + ML training pipelines checked for unauthorised customer-PII use

### Rev Customer Verification Health

<<MUST item:B.8.2.2:rev_customer_verification_health>>
_Why: §8.2.2 — allow customer to verify_

> _Standard text:_ Customer verification health — audits requested + supported within stated SLA

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
