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

> Annual verification — encryption standards current, audit logs retained, no plaintext transmission paths, endpoints authenticated (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.9:program_review -->
<!-- column: item:A.7.4.9:rev_date -->
<!-- column: item:A.7.4.9:rev_reviewer -->
<!-- column: item:A.7.4.9:rev_encryption_currency -->
<!-- column: item:A.7.4.9:rev_audit_log_retention_check -->
<!-- column: item:A.7.4.9:rev_shadow_channel_sweep -->
<!-- /TABLE-COLUMNS -->

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

### Rev Reviewer

<<MUST item:A.7.4.9:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure + Security Engineering + DPO)

### Rev Encryption Currency

<<MUST item:A.7.4.9:rev_encryption_currency>>
_Why: Modern baseline_

> _Standard text:_ Encryption currency — TLS / cipher-suite standards current (deprecated protocols flagged)

### Rev Audit Log Retention Check

<<MUST item:A.7.4.9:rev_audit_log_retention_check>>
_Why: §7.4.9 — retention of audit logs_

> _Standard text:_ Audit-log retention check — retention meets policy

### Rev Shadow Channel Sweep

<<MUST item:A.7.4.9:rev_shadow_channel_sweep>>
_Why: Drift detection_

> _Standard text:_ Shadow-channel sweep — unauthorised transmission paths flagged (e.g. developers using consumer file-sharing)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.9:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
