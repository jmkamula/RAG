---
leaf_id: req:A.6.7:remote_working_review
control_ref: A.6.7
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Remote Working Programme Review

<<DOC_CONTROL>>

> Periodic verification that the policy is current, the register has no orphan rows (each row's personnel still in scope and approved), conditions are being honoured, and any incidents stemming from remote-work context have been triaged into lessons. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.7:remote_working_review -->
<!-- column: item:A.6.7:rev_date -->
<!-- column: item:A.6.7:rev_reviewer -->
<!-- column: item:A.6.7:rev_register_currency -->
<!-- column: item:A.6.7:rev_orphan_check -->
<!-- column: item:A.6.7:rev_incident_review -->
<!-- column: item:A.6.7:rev_policy_currency -->
<!-- column: item:A.6.7:rev_next_date -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep your remote working programme up to date by checking that your policy is current, your register is accurate, and any incidents have been reviewed for lessons learned.

## When to use it

Use this template if your organisation manages remote workers and needs to regularly review its remote working programme. Plan to complete this review about once a year, or when your situation changes significantly.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend around 1.5 to 2 hours to fill out the required sections from scratch, plus additional time for each person listed in your register.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.7:remote_working_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Orphan Check | Rev Incident Review | Rev Policy Currency | Rev Next Date |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.7:remote_working_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.7:rev_date>>
_Why: 27002:6.7 — periodic_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.6.7:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Head of IT / InfoSec lead + HR partner; reviewer must not be the sole approver of any reviewed row)

<<GUIDANCE>>

### Rev Register Currency

<<MUST item:A.6.7:rev_register_currency>>
_Why: 27002:6.7 — currency_

> _Standard text:_ Register-currency check (every row's personnel_id is still in A.5.16 active register; expired-approval rows surfaced and revoked or re-approved)

<<GUIDANCE>>

### Rev Orphan Check

<<MUST item:A.6.7:rev_orphan_check>>
_Why: 27002:6.7 + A.5.18 coherence_

> _Standard text:_ Orphan-row check (any row whose personnel_id is no longer in A.5.16 active identity register) — surfaces missed leaver-flow revocations; cross-link to A.5.18 access review

<<GUIDANCE>>

### Rev Incident Review

<<MUST item:A.6.7:rev_incident_review>>
_Why: 27002:6.7 + A.5.27 link_

> _Standard text:_ Remote-context incident review (any A.5.26 incident-register entries flagged as remote-work-related in the period; lessons fed back into policy / procedure)

<<GUIDANCE>>

### Rev Policy Currency

<<MUST item:A.6.7:rev_policy_currency>>
_Why: Cross-control coherence_

> _Standard text:_ Policy-currency check (referenced policies still aligned — A.5.10 acceptable use, A.5.12 classification, A.5.15 access, A.5.18 access review, A.7.4 physical, A.7.7 desk policy, A.8.1 user endpoint, A.8.24 cryptography)

<<GUIDANCE>>

### Rev Next Date

<<MUST item:A.6.7:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.7:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (major incident exposing remote-work gap, policy change affecting remote workers, regulatory change for cross-border data, geographic-risk shift)

<<GUIDANCE>>

### Rev Metrics

<<SHOULD item:A.6.7:rev_metrics>>
_Why: Continual improvement_

> _Standard text:_ Metrics noted (count of active remote workers, distribution by location category, count of expired-pending-revocation rows, count of remote-context incidents in period)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
