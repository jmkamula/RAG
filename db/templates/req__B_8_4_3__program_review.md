---
leaf_id: req:B.8.4.3:program_review
control_ref: B.8.4.3
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Processor Transmission Program Review

<<DOC_CONTROL>>

> Annual verification — encryption current, contract alignment intact, no unauthorised channels, customer consultation invoked when needed (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.4.3:program_review -->
<!-- column: item:B.8.4.3:rev_date -->
<!-- column: item:B.8.4.3:rev_reviewer -->
<!-- column: item:B.8.4.3:rev_contract_alignment_audit -->
<!-- column: item:B.8.4.3:rev_shadow_channel_sweep -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document your annual review of how data is transmitted to processors, ensuring encryption is up to date, contracts are aligned, and no unauthorized channels are used.

## When to use it

Use this review record if your organization transmits data to external processors and needs to verify compliance with privacy standards, typically once a year or when your data handling profile changes.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 45 to 60 minutes completing this from scratch, as each required element takes 10-15 minutes and the register format may require additional detail for each processor.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.4.3:program_review -->
| Rev Date | Rev Reviewer | Rev Contract Alignment Audit | Rev Shadow Channel Sweep |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.4.3:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.4.3:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:B.8.4.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Platform Ops + Security Engineering + DPO)

<<GUIDANCE>>

### Rev Contract Alignment Audit

<<MUST item:B.8.4.3:rev_contract_alignment_audit>>
_Why: §8.4.3 — contract requirements_

> _Standard text:_ Contract-alignment audit — sampled channels reviewed against customer B.8.2.1 agreements

<<GUIDANCE>>

### Rev Shadow Channel Sweep

<<MUST item:B.8.4.3:rev_shadow_channel_sweep>>
_Why: Drift detection_

> _Standard text:_ Shadow-channel sweep — unauthorised channels flagged

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.4.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
