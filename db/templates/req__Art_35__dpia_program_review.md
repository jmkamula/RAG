---
leaf_id: req:Art.35:dpia_program_review
control_ref: Art.35
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
table_shape: true
---

# DPIA Program Review

> Annual verification — every in-scope activity has a current DPIA, DPO advice was sought, Art.36 consultations escalated where residual risk warranted (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.35:dpia_program_review -->
<!-- column: item:Art.35:rev_date -->
<!-- column: item:Art.35:rev_reviewer -->
<!-- column: item:Art.35:rev_coverage -->
<!-- column: item:Art.35:rev_advice_quality -->
<!-- column: item:Art.35:rev_art36_audit -->
<!-- column: item:Art.35:rev_review_cadence -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.35:dpia_program_review -->
| Rev Date | Rev Reviewer | Rev Coverage | Rev Advice Quality | Rev Art36 Audit | Rev Review Cadence |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.35:dpia_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.35:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.35:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + executive sponsor + lead privacy engineer)

### Rev Coverage

<<MUST item:Art.35:rev_coverage>>
_Why: Art.35.1_

> _Standard text:_ Coverage check — every in-scope activity has a current DPIA OR documented Art.35.5 white-list justification

### Rev Advice Quality

<<MUST item:Art.35:rev_advice_quality>>
_Why: Art.35.2_

> _Standard text:_ DPO-advice quality sample — advice substantive, not rubber-stamp

### Rev Art36 Audit

<<MUST item:Art.35:rev_art36_audit>>
_Why: Art.36_

> _Standard text:_ Art.36 escalation audit — residual-high-risk DPIAs escalated to SA where required

### Rev Review Cadence

<<MUST item:Art.35:rev_review_cadence>>
_Why: Art.35.11_

> _Standard text:_ Review-cadence audit — DPIAs refreshed per Art.35.11 when processing changed

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.35:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
