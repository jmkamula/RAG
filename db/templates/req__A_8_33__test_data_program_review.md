---
leaf_id: req:A.8.33:test_data_program_review
control_ref: A.8.33
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# Periodic Test Information Program Review

<<DOC_CONTROL>>

> Annual verification — register currency, no-live-PII spot-check, retention compliance, masking effectiveness (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.8.33:test_data_program_review -->
<!-- column: item:A.8.33:rev_date -->
<!-- column: item:A.8.33:rev_reviewer -->
<!-- column: item:A.8.33:rev_register_currency -->
<!-- column: item:A.8.33:rev_no_live_pii_check -->
<!-- column: item:A.8.33:rev_retention_compliance -->
<!-- column: item:A.8.33:rev_findings_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your periodic testing information, ensuring your records are up-to-date, no live personal data is present, and your data retention and masking practices are effective.

## When to use it

Use this template once a year or whenever your profile matches certain review triggers, to confirm your information program is current and compliant with ISO 27001 requirements.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, depending on the number of records you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.33:test_data_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev No Live Pii Check | Rev Retention Compliance | Rev Findings Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.33:test_data_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.8.33:rev_date>>
_Why: 27002:8.33 — periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.8.33:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Data Engineering + DPO + InfoSec)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:A.8.33:rev_register_currency>>
_Why: Drift prevention_

> _Standard text:_ Register-currency check (active datasets all registered; retired datasets archived/deleted)

<<GUIDANCE>>

### Rev No Live Pii Check

<<MUST item:A.8.33:rev_no_live_pii_check>>
_Why: GDPR alignment_

> _Standard text:_ No-live-PII spot-check in non-production environments (auditor-critical for GDPR)

<<GUIDANCE>>

### Rev Retention Compliance

<<MUST item:A.8.33:rev_retention_compliance>>
_Why: 27002:8.33 — managed_

> _Standard text:_ Retention compliance (no datasets surviving past end-of-need)

<<GUIDANCE>>

### Rev Findings Update

<<MUST item:A.8.33:rev_findings_update>>
_Why: Closes the loop_

> _Standard text:_ Findings propagated to procedure / scope

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.8.33:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
