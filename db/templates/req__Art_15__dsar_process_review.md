---
leaf_id: req:Art.15:dsar_process_review
control_ref: Art.15
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 3
table_shape: true
---

# Periodic DSAR Process Review

<<DOC_CONTROL>>

> Periodic management review of DSAR handling effectiveness. Confirms the procedure produced timely, lawful responses across the year, identifies systemic defects (late responses, refusals, complaints to supervisory authority) and feeds corrective actions back into the procedure

<!-- TABLE-COLUMNS leaf:req:Art.15:dsar_process_review -->
<!-- column: item:Art.15:rev_date -->
<!-- column: item:Art.15:rev_reviewer -->
<!-- column: item:Art.15:rev_volume -->
<!-- column: item:Art.15:rev_timing -->
<!-- column: item:Art.15:rev_defects -->
<!-- column: item:Art.15:rev_corrective -->
<!-- column: item:Art.15:rev_identity_pair_30 -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of how well your organization handles Data Subject Access Requests (DSARs) over the year, highlighting any recurring issues and supporting improvements to your process.

## When to use it

Use this review record once a year to assess your DSAR response process, ensuring you consistently meet GDPR requirements and address any problems that have come up.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this from scratch, depending on the number of DSAR cases you need to review and the detail you provide for each required element.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.15:dsar_process_review -->
| Rev Date | Rev Reviewer | Rev Volume | Rev Timing | Rev Defects | Rev Corrective | Rev Identity Pair 30 |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.15:dsar_process_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.15:rev_date>>
_Why: Periodic accuracy_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:Art.15:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role (DPO, privacy lead, or delegated equivalent)

<<GUIDANCE>>

### Rev Volume

<<MUST item:Art.15:rev_volume>>
_Why: Effectiveness measurement_

> _Standard text:_ Volume metric — number of DSARs received in the review period

<<GUIDANCE>>

### Rev Timing

<<MUST item:Art.15:rev_timing>>
_Why: Art.12.3 evidence_

> _Standard text:_ Timing metric — percentage within one month, count of extensions used, count of late responses

<<GUIDANCE>>

### Rev Defects

<<MUST item:Art.15:rev_defects>>
_Why: Defect tracking_

> _Standard text:_ Defects identified (late responses, refusals, supervisory-authority complaints) referenced

<<GUIDANCE>>

### Rev Corrective

<<MUST item:Art.15:rev_corrective>>
_Why: Closes the loop_

> _Standard text:_ Corrective actions to the procedure with owner and target date

<<GUIDANCE>>

### Rev Identity Pair 30

<<MUST item:Art.15:rev_identity_pair_30>>
_Why: Art.30 cross-leaf coherence — drops rev_inventory_align SHOULD into MUST shape_

> _Standard text:_ Bidirectional Art.15 ↔ Art.30 RoPA pair check — every system the review period's DSARs actually queried is captured in the data flow inventory; every system the inventory lists was reachable when DSARs landed on it (closes the silent inventory-drift gap)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.15:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

### Rev Training Impl

<<SHOULD item:Art.15:rev_training_impl>>
_Why: EDPB 01/2022 — operational realism_

> _Standard text:_ Training implications captured where defects trace to staff awareness

<<GUIDANCE>>

### Rev Inventory Align

<<SHOULD item:Art.15:rev_inventory_align>>
_Why: Art.30 cross-leaf coherence (the rev_identity_pair_30 MUST carries the formal check)_

> _Standard text:_ Soft cross-check supplementary to rev_identity_pair_30 — narrative observations on inventory drift between formal pair checks

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
