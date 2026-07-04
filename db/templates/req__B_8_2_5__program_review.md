---
leaf_id: req:B.8.2.5:program_review
control_ref: B.8.2.5
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Customer Support Program Review

> Annual verification — support pathways functional, SLAs met, certifications current, audit rights honoured (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.2.5:program_review -->
<!-- column: item:B.8.2.5:rev_date -->
<!-- column: item:B.8.2.5:rev_reviewer -->
<!-- column: item:B.8.2.5:rev_sla_audit -->
<!-- column: item:B.8.2.5:rev_certification_health -->
<!-- column: item:B.8.2.5:rev_audit_rights_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.2.5:program_review -->
| Rev Date | Rev Reviewer | Rev Sla Audit | Rev Certification Health | Rev Audit Rights Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.2.5:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.2.5:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:B.8.2.5:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Trust + Compliance + Sales Ops)

### Rev Sla Audit

<<MUST item:B.8.2.5:rev_sla_audit>>
_Why: §8.2.5 — appropriate information_

> _Standard text:_ SLA audit — sampled requests measured against response SLA

### Rev Certification Health

<<MUST item:B.8.2.5:rev_certification_health>>
_Why: Currency_

> _Standard text:_ Certification health — currency + scope of shared certifications reviewed

### Rev Audit Rights Audit

<<MUST item:B.8.2.5:rev_audit_rights_audit>>
_Why: §8.2.5 — audits conducted by customer_

> _Standard text:_ Audit rights audit — customer audits requested + granted per contract tier

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.2.5:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
