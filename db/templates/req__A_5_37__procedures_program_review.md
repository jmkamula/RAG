---
leaf_id: req:A.5.37:procedures_program_review
control_ref: A.5.37
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Operating Procedures Program Review

> Periodic verification that the register reflects the facility scope, procedures are still accurate (not just 'documented' but matching reality), availability mechanisms still work (operators can actually find them), and the maintenance procedure is being followed. Annual cadence (freshness=365) matches the records-family default — operational procedure methodology is stable, individual procedures get updated continuously via maintenance

<!-- TABLE-COLUMNS leaf:req:A.5.37:procedures_program_review -->
<!-- column: item:A.5.37:rev_date -->
<!-- column: item:A.5.37:rev_reviewer -->
<!-- column: item:A.5.37:rev_register_check -->
<!-- column: item:A.5.37:rev_scope_check -->
<!-- column: item:A.5.37:rev_accuracy_sample -->
<!-- column: item:A.5.37:rev_emergency_review -->
<!-- column: item:A.5.37:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.37:procedures_program_review -->
| Rev Date | Rev Reviewer | Rev Register Check | Rev Scope Check | Rev Accuracy Sample | Rev Emergency Review | Rev Register Update |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.37:procedures_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.37:rev_date>>
_Why: 27002:5.37 — documented + current_

> _Standard text:_ Review date within the planned interval (typically within 12 months of last review)

### Rev Reviewer

<<MUST item:A.5.37:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded (operations lead + InfoSec lead jointly)

### Rev Register Check

<<MUST item:A.5.37:rev_register_check>>
_Why: 27002:5.37 — documented + available_

> _Standard text:_ Per-procedure outcome (verified / amended / retired / new added) with availability-mechanism-still-works confirmation

### Rev Scope Check

<<MUST item:A.5.37:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-facilities scope — any new system / SaaS environment / facility class that should add procedures

### Rev Accuracy Sample

<<MUST item:A.5.37:rev_accuracy_sample>>
_Why: 27002:5.37 — operations_

> _Standard text:_ Accuracy sampling — operator walked through a sample procedure end-to-end? procedure matches current system reality (UI screenshots current, commands work, dependencies still valid)

### Rev Emergency Review

<<MUST item:A.5.37:rev_emergency_review>>
_Why: Operational realism_

> _Standard text:_ Emergency-use procedure review — confirmed available and accurate for DR/incident scenarios (these are the procedures where stale = catastrophic)

### Rev Register Update

<<MUST item:A.5.37:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the live register with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.37:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (major incident exposing procedure gap, M&A, major system migration)

### Rev Next Date

<<SHOULD item:A.5.37:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
