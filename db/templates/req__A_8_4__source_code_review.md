---
leaf_id: req:A.8.4:source_code_review
control_ref: A.8.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 180
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Source Code Access Review

> Periodic verification that repository access is current, dependency allowlist is current, and the monitoring log shows expected hygiene (freshness=180; dev landscape changes fast)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (≤180 days)

<<MUST item:A.8.4:rev_date>>
_Why: 27002:8.4 — periodic_

<<TEXT>>

## 2. Reviewer identity (Engineering + InfoSec)

<<MUST item:A.8.4:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Sample-based repo access verification (per-repo admin and write list re-confirmed)

<<MUST item:A.8.4:rev_access_sample>>
_Why: Drift prevention_

<<TEXT>>

## 4. Dependency-allowlist currency check (no abandoned libraries; vulnerable versions retired)

<<MUST item:A.8.4:rev_dep_currency>>
_Why: Supply chain hygiene_

<<TEXT>>

## 5. Outstanding scanner findings reviewed (closed / accepted / extended)

<<MUST item:A.8.4:rev_findings_closed>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.4:rev_next_date>>
_Why: Planning_

<<TEXT>>
