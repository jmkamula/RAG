---
leaf_id: req:Art.26:joint_controller_program_review
control_ref: Art.26
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Joint Controller Program Review

> Annual verification — every active joint-controller relationship has current arrangement, essence is published, contact point still functioning (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.26:joint_controller_program_review -->
<!-- column: item:Art.26:rev_date -->
<!-- column: item:Art.26:rev_reviewer -->
<!-- column: item:Art.26:rev_currency -->
<!-- column: item:Art.26:rev_essence_published -->
<!-- column: item:Art.26:rev_contact_point -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.26:joint_controller_program_review -->
| Rev Date | Rev Reviewer | Rev Currency | Rev Essence Published | Rev Contact Point |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.26:joint_controller_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.26:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.26:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + legal counsel)

### Rev Currency

<<MUST item:Art.26:rev_currency>>
_Why: Art.26.1_

> _Standard text:_ Arrangement currency — every active relationship has current signed arrangement

### Rev Essence Published

<<MUST item:Art.26:rev_essence_published>>
_Why: Art.26.2_

> _Standard text:_ Essence-published audit — privacy notice / equivalent surface reflects each arrangement

### Rev Contact Point

<<MUST item:Art.26:rev_contact_point>>
_Why: Art.26.1_

> _Standard text:_ Contact-point health check — point still reachable, requests being routed correctly

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.26:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
