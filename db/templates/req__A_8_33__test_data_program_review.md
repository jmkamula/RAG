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
---

# Periodic Test Information Program Review

> Annual verification — register currency, no-live-PII spot-check, retention compliance, masking effectiveness (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.33:rev_date>>
_Why: 27002:8.33 — periodic_

<<TEXT>>

## 2. Reviewer identity (Data Engineering + DPO + InfoSec)

<<MUST item:A.8.33:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register-currency check (active datasets all registered; retired datasets archived/deleted)

<<MUST item:A.8.33:rev_register_currency>>
_Why: Drift prevention_

<<TEXT>>

## 4. No-live-PII spot-check in non-production environments (auditor-critical for GDPR)

<<MUST item:A.8.33:rev_no_live_pii_check>>
_Why: GDPR alignment_

<<TEXT>>

## 5. Retention compliance (no datasets surviving past end-of-need)

<<MUST item:A.8.33:rev_retention_compliance>>
_Why: 27002:8.33 — managed_

<<TEXT>>

## 6. Findings propagated to procedure / scope

<<MUST item:A.8.33:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.33:rev_next_date>>
_Why: Planning_

<<TEXT>>
