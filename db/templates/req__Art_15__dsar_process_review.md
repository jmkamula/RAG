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
---

# Periodic DSAR Process Review

> Periodic management review of DSAR handling effectiveness. Confirms the procedure produced timely, lawful responses across the year, identifies systemic defects (late responses, refusals, complaints to supervisory authority) and feeds corrective actions back into the procedure

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval (typically within 12 months of last review)

<<MUST item:Art.15:rev_date>>
_Why: Periodic accuracy_

<<TEXT>>

## 2. Reviewer identity and role (DPO, privacy lead, or delegated equivalent)

<<MUST item:Art.15:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Volume metric — number of DSARs received in the review period

<<MUST item:Art.15:rev_volume>>
_Why: Effectiveness measurement_

<<TEXT>>

## 4. Timing metric — percentage within one month, count of extensions used, count of late responses

<<MUST item:Art.15:rev_timing>>
_Why: Art.12.3 evidence_

<<TEXT>>

## 5. Defects identified (late responses, refusals, supervisory-authority complaints) referenced

<<MUST item:Art.15:rev_defects>>
_Why: Defect tracking_

<<TEXT>>

## 6. Corrective actions to the procedure with owner and target date

<<MUST item:Art.15:rev_corrective>>
_Why: Closes the loop_

<<TEXT>>

## 7. Bidirectional Art.15 ↔ Art.30 RoPA pair check — every system the review period's DSARs actually queried is captured in the data flow inventory; every system the inventory lists was reachable when DSARs landed on it (closes the silent inventory-drift gap)

<<MUST item:Art.15:rev_identity_pair_30>>
_Why: Art.30 cross-leaf coherence — drops rev_inventory_align SHOULD into MUST shape_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.15:rev_next_date>>
_Why: Planning_

<<TEXT>>

### 2. Training implications captured where defects trace to staff awareness

<<SHOULD item:Art.15:rev_training_impl>>
_Why: EDPB 01/2022 — operational realism_

<<TEXT>>

### 3. Soft cross-check supplementary to rev_identity_pair_30 — narrative observations on inventory drift between formal pair checks

<<SHOULD item:Art.15:rev_inventory_align>>
_Why: Art.30 cross-leaf coherence (the rev_identity_pair_30 MUST carries the formal check)_

<<TEXT>>
