---
leaf_id: req:A.7.3.6:program_review
control_ref: A.7.3.6
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# ACR Program Review

> Annual verification — request handling reliable, SLAs met, refusals defensible, propagation working, no ACR gaps in systems (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.6:program_review -->
<!-- column: item:A.7.3.6:rev_date -->
<!-- column: item:A.7.3.6:rev_reviewer -->
<!-- column: item:A.7.3.6:rev_sla_audit -->
<!-- column: item:A.7.3.6:rev_refusal_audit -->
<!-- column: item:A.7.3.6:rev_propagation_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.6:program_review -->
| Rev Date | Rev Reviewer | Rev Sla Audit | Rev Refusal Audit | Rev Propagation Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.6:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.6:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.3.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal + Engineering)

### Rev Sla Audit

<<MUST item:A.7.3.6:rev_sla_audit>>
_Why: §7.3.6 — undue delay + Art.12.3_

> _Standard text:_ SLA audit — sampled requests measured against undue-delay standard

### Rev Refusal Audit

<<MUST item:A.7.3.6:rev_refusal_audit>>
_Why: §7.3.6 + Art.12.4_

> _Standard text:_ Refusal audit — sampled refusals reviewed for defensibility + subject-notification of reason

### Rev Propagation Audit

<<MUST item:A.7.3.6:rev_propagation_audit>>
_Why: §7.3.6 — pass to third parties_

> _Standard text:_ Propagation audit — sampled corrections/erasures verified downstream

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
