---
leaf_id: req:Art.16:program_review
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.16 Rectification Program Review

> Annual verification — SLAs met, systems coverage complete, Art.19 notifications fired (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.16:program_review -->
<!-- column: item:Art.16:rev_date -->
<!-- column: item:Art.16:rev_reviewer -->
<!-- column: item:Art.16:rev_sla_compliance -->
<!-- column: item:Art.16:rev_systems_completeness -->
<!-- column: item:Art.16:rev_art19_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.16:program_review -->
| Rev Date | Rev Reviewer | Rev Sla Compliance | Rev Systems Completeness | Rev Art19 Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.16:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.16:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.16:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO)

### Rev Sla Compliance

<<MUST item:Art.16:rev_sla_compliance>>
_Why: Art.12.3_

> _Standard text:_ SLA compliance (Art.12.3 one-month)

### Rev Systems Completeness

<<MUST item:Art.16:rev_systems_completeness>>
_Why: Art.16 — all instances_

> _Standard text:_ Systems-completeness check — sampled requests reached every system in scope

### Rev Art19 Audit

<<MUST item:Art.16:rev_art19_audit>>
_Why: Art.19_

> _Standard text:_ Art.19 audit — recipient notifications fired (or exceptions documented)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.16:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
