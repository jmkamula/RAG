---
leaf_id: req:Art.46:safeguards_program_review
control_ref: Art.46
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Safeguards Program Review

> Annual verification — SCCs on current version, TIAs current, supplementary measures effective, vendor compliance attested (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.46:safeguards_program_review -->
<!-- column: item:Art.46:rev_date -->
<!-- column: item:Art.46:rev_reviewer -->
<!-- column: item:Art.46:rev_sccs_version -->
<!-- column: item:Art.46:rev_tia_currency -->
<!-- column: item:Art.46:rev_supplementary_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.46:safeguards_program_review -->
| Rev Date | Rev Reviewer | Rev Sccs Version | Rev Tia Currency | Rev Supplementary Audit |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.46:safeguards_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.46:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.46:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

### Rev Sccs Version

<<MUST item:Art.46:rev_sccs_version>>
_Why: Commission Decision 2021/914_

> _Standard text:_ SCCs version audit — any old-version SCCs identified for migration

### Rev Tia Currency

<<MUST item:Art.46:rev_tia_currency>>
_Why: Schrems II — ongoing duty_

> _Standard text:_ TIA currency — TIAs refreshed where third-country law has changed materially

### Rev Supplementary Audit

<<MUST item:Art.46:rev_supplementary_audit>>
_Why: EDPB 01/2020_

> _Standard text:_ Supplementary measures audit — applied measures (encryption keys, pseudonymisation, etc.) actually in place at vendor

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.46:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
