---
leaf_id: req:A.7.2.4:program_review
control_ref: A.7.2.4
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Consent Capture Program Review

<<DOC_CONTROL>>

> Annual verification — consent records complete + retrievable within SLA, per-event demonstration works, withdrawal flags propagate to processing (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.2.4:program_review -->
<!-- column: item:A.7.2.4:rev_date -->
<!-- column: item:A.7.2.4:rev_reviewer -->
<!-- column: item:A.7.2.4:rev_retrievability -->
<!-- column: item:A.7.2.4:rev_completeness_audit -->
<!-- column: item:A.7.2.4:rev_withdrawal_propagation -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your consent records, making sure they are complete, easy to find, and up to date. It also checks that consent withdrawals are handled correctly across your systems.

## When to use it

Use this template once a year, or whenever your organization meets certain privacy-related criteria, to review and confirm your consent management processes are working as required.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours to fill out this review from scratch, depending on how many consent records you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.4:program_review -->
| Rev Date | Rev Reviewer | Rev Retrievability | Rev Completeness Audit | Rev Withdrawal Propagation |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.4:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.2.4:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.2.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Engineering)

<<GUIDANCE>>

### Rev Retrievability

<<MUST item:A.7.2.4:rev_retrievability>>
_Why: §7.2.4 — provide on request_

> _Standard text:_ Retrievability test — sampled consent events retrieved within stated SLA

<<GUIDANCE>>

### Rev Completeness Audit

<<MUST item:A.7.2.4:rev_completeness_audit>>
_Why: §7.2.4 — record consent_

> _Standard text:_ Completeness audit — sampled consented users have retrievable records

<<GUIDANCE>>

### Rev Withdrawal Propagation

<<MUST item:A.7.2.4:rev_withdrawal_propagation>>
_Why: §7.3.4 — modify or withdraw_

> _Standard text:_ Withdrawal propagation — sampled withdrawals verified to have stopped downstream processing

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.2.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
