---
leaf_id: req:A.5.16:identity_program_review
control_ref: A.5.16
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Identity-Management Program Review

> The identity program creates value only if the lifecycle actually closes — orphan accounts, lingering contractor access, stale service credentials, missed termination SLAs all signal the program is leaking. The review captures the planned-interval check: orphan analysis, SLA-miss analysis, service-account hygiene audit, contractor expiry verification, and resulting program adjustments. Cadence tightened to 180 days — identity drift is high-volume

<!-- TABLE-COLUMNS leaf:req:A.5.16:identity_program_review -->
<!-- column: item:A.5.16:rev_date -->
<!-- column: item:A.5.16:rev_reviewer -->
<!-- column: item:A.5.16:rev_orphan_analysis -->
<!-- column: item:A.5.16:rev_termination_sla -->
<!-- column: item:A.5.16:rev_service_hygiene -->
<!-- column: item:A.5.16:rev_contractor_expiry -->
<!-- column: item:A.5.16:rev_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.16:identity_program_review -->
| Rev Date | Rev Reviewer | Rev Orphan Analysis | Rev Termination Sla | Rev Service Hygiene | Rev Contractor Expiry | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.16:identity_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.16:rev_date>>
_Why: 27002:5.16 — periodic_

> _Standard text:_ Review date within the planned 180-day interval

### Rev Reviewer

<<MUST item:A.5.16:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IT identity-lead + HR partner + InfoSec lead jointly)

### Rev Orphan Analysis

<<MUST item:A.5.16:rev_orphan_analysis>>
_Why: 27002:5.16 — drift catch_

> _Standard text:_ Orphan analysis (identities without active HR record / business reason; remediation per orphan)

### Rev Termination Sla

<<MUST item:A.5.16:rev_termination_sla>>
_Why: 27002:5.16 — timeliness_

> _Standard text:_ Termination-SLA analysis (gap between leaver effective_date and identity_revocation date; outliers investigated)

### Rev Service Hygiene

<<MUST item:A.5.16:rev_service_hygiene>>
_Why: 27002:5.16 — service-account discipline_

> _Standard text:_ Service-account hygiene audit (sample of service accounts re-validated: owner still employed, scope still appropriate, expiry not lapsed)

### Rev Contractor Expiry

<<MUST item:A.5.16:rev_contractor_expiry>>
_Why: 27002:5.16 — fixed-expiry enforcement_

> _Standard text:_ Contractor-expiry verification (audit that expired contractor identities are actually disabled, not just flagged)

### Rev Actions

<<MUST item:A.5.16:rev_actions>>
_Why: 27002:5.16 — program adjustments_

> _Standard text:_ Action items captured (e.g. tighten auto-suspend threshold, expand HR-cascade automation, retire shared accounts)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Iam Tooling

<<SHOULD item:A.5.16:rev_iam_tooling>>
_Why: Audit defensibility_

> _Standard text:_ IAM tooling check (vendor releases, new capabilities like just-in-time access; capability gaps to consider)

### Rev Next Date

<<SHOULD item:A.5.16:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated (within 180d of this review)
