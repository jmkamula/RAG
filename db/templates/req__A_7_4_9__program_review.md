---
leaf_id: req:A.7.4.9:program_review
control_ref: A.7.4.9
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Transmission Program Review

<<DOC_CONTROL>>

> Annual verification — encryption standards current, audit logs retained, no plaintext transmission paths, endpoints authenticated (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.9:program_review -->
<!-- column: item:A.7.4.9:rev_date -->
<!-- column: item:A.7.4.9:rev_reviewer -->
<!-- column: item:A.7.4.9:rev_encryption_currency -->
<!-- column: item:A.7.4.9:rev_audit_log_retention_check -->
<!-- column: item:A.7.4.9:rev_shadow_channel_sweep -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your data transmission methods meet current encryption standards, keep audit logs, avoid sending data in plain text, and ensure all endpoints are properly authenticated.

## When to use it

Use this review each year, or whenever your organization’s profile changes in a way that affects how you transmit data, to make sure your practices stay up to date with privacy requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours completing this from scratch, depending on how many transmission methods you need to document and review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.9:program_review -->
| Rev Date | Rev Reviewer | Rev Encryption Currency | Rev Audit Log Retention Check | Rev Shadow Channel Sweep |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.9:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.9:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.4.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure + Security Engineering + DPO)

<<GUIDANCE>>

### Rev Encryption Currency

<<MUST item:A.7.4.9:rev_encryption_currency>>
_Why: Modern baseline_

> _Standard text:_ Encryption currency — TLS / cipher-suite standards current (deprecated protocols flagged)

<<GUIDANCE>>

### Rev Audit Log Retention Check

<<MUST item:A.7.4.9:rev_audit_log_retention_check>>
_Why: §7.4.9 — retention of audit logs_

> _Standard text:_ Audit-log retention check — retention meets policy

<<GUIDANCE>>

### Rev Shadow Channel Sweep

<<MUST item:A.7.4.9:rev_shadow_channel_sweep>>
_Why: Drift detection_

> _Standard text:_ Shadow-channel sweep — unauthorised transmission paths flagged (e.g. developers using consumer file-sharing)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
