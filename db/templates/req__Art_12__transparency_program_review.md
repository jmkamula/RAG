---
leaf_id: req:Art.12:transparency_program_review
control_ref: Art.12
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Transparency Program Review

> Annual verification that SLAs are being met, the register reflects all requests, refusal grounds are being applied consistently (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.12:transparency_program_review -->
<!-- column: item:Art.12:rev_date -->
<!-- column: item:Art.12:rev_reviewer -->
<!-- column: item:Art.12:rev_sla_compliance -->
<!-- column: item:Art.12:rev_refusal_audit -->
<!-- column: item:Art.12:rev_channel_coverage -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.12:transparency_program_review -->
| Rev Date | Rev Reviewer | Rev Sla Compliance | Rev Refusal Audit | Rev Channel Coverage |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.12:transparency_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.12:rev_date>>
_Why: Periodic accountability_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.12:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + ops lead)

### Rev Sla Compliance

<<MUST item:Art.12:rev_sla_compliance>>
_Why: Art.12.3_

> _Standard text:_ SLA compliance check — one-month response rate against in-scope requests

### Rev Refusal Audit

<<MUST item:Art.12:rev_refusal_audit>>
_Why: Art.12.5 — defensibility_

> _Standard text:_ Refusal-grounds audit — refused requests sampled for legitimate Art.12.5 grounds

### Rev Channel Coverage

<<MUST item:Art.12:rev_channel_coverage>>
_Why: Drift detection_

> _Standard text:_ Channel coverage check — every in-scope channel is reaching the procedure (no orphan requests)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.12:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
