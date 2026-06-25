---
leaf_id: req:Art.48:foreign_authority_program_review
control_ref: Art.48
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Foreign Authority Program Review

> Annual verification — procedure tested via tabletop where no real requests occurred, agreements catalogue current, any actual disclosures defensible (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.48:foreign_authority_program_review -->
<!-- column: item:Art.48:rev_date -->
<!-- column: item:Art.48:rev_reviewer -->
<!-- column: item:Art.48:rev_register_currency -->
<!-- column: item:Art.48:rev_tabletop -->
<!-- column: item:Art.48:rev_agreements_currency -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.48:foreign_authority_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Tabletop | Rev Agreements Currency |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.48:foreign_authority_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.48:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.48:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel + executive sponsor)

### Rev Register Currency

<<MUST item:Art.48:rev_register_currency>>
_Why: Cross-leaf_

> _Standard text:_ Register currency — every actual request handled per procedure

### Rev Tabletop

<<MUST item:Art.48:rev_tabletop>>
_Why: Effectiveness_

> _Standard text:_ Tabletop exercise — procedure tested at least annually against a hypothetical foreign authority request (mirrors A.5.24 IR exercises)

### Rev Agreements Currency

<<MUST item:Art.48:rev_agreements_currency>>
_Why: Currency_

> _Standard text:_ Agreements currency — international agreements catalogue refreshed

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.48:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
