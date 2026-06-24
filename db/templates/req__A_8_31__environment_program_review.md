---
leaf_id: req:A.8.31:environment_program_review
control_ref: A.8.31
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Environment Separation Program Review

> Annual verification — environment-register currency, no-production-data-in-non-prod sample check, per-env access review (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.31:rev_date>>
_Why: 27002:8.31 — periodic_

<<TEXT>>

## 2. Reviewer identity (Infrastructure + InfoSec + Engineering leads)

<<MUST item:A.8.31:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Environment-register currency check

<<MUST item:A.8.31:rev_register_currency>>
_Why: Drift prevention_

<<TEXT>>

## 4. Sample-based check — no raw production data found in lower environments (auditor-critical for GDPR)

<<MUST item:A.8.31:rev_no_prod_data_sample>>
_Why: 27002:8.31 — secured + GDPR alignment_

<<TEXT>>

## 5. Per-env access review (cross-link to A.8.3 + A.5.18 outcomes)

<<MUST item:A.8.31:rev_per_env_access>>
_Why: Cross-control coherence_

<<TEXT>>

## 6. Findings propagated to procedure / register

<<MUST item:A.8.31:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.31:rev_next_date>>
_Why: Planning_

<<TEXT>>
