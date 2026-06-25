---
leaf_id: req:A.5.31:obligations_register_review
control_ref: A.5.31
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Legal/Regulatory Register Review

> Periodic verification that the register still reflects current obligations and that the compliance approach for each is still adequate. The cadence is semi-annual (freshness=180) because regulatory change is faster than annual; this matches the prior single-leaf freshness signal

<!-- TABLE-COLUMNS leaf:req:A.5.31:obligations_register_review -->
<!-- column: item:A.5.31:rev_date -->
<!-- column: item:A.5.31:rev_reviewer -->
<!-- column: item:A.5.31:rev_per_entry -->
<!-- column: item:A.5.31:rev_scope_check -->
<!-- column: item:A.5.31:rev_horizon -->
<!-- column: item:A.5.31:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.31:obligations_register_review -->
| Rev Date | Rev Reviewer | Rev Per Entry | Rev Scope Check | Rev Horizon | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.31:obligations_register_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.31:rev_date>>
_Why: 27002:5.31 — kept up to date_

> _Standard text:_ Review date within the planned interval (within 6 months of last review)

### Rev Reviewer

<<MUST item:A.5.31:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded (compliance lead with legal-counsel sign-off where material)

### Rev Per Entry

<<MUST item:A.5.31:rev_per_entry>>
_Why: 27002:5.31b_

> _Standard text:_ Per-entry outcome (verified / amended / retired / new added) with compliance-approach still-adequate confirmation

### Rev Scope Check

<<MUST item:A.5.31:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the applicable-obligations scope — any new applicability that should add entries

### Rev Horizon

<<MUST item:A.5.31:rev_horizon>>
_Why: Forward-looking compliance_

> _Standard text:_ Forward-looking section — obligations entering force in the next 12-24 months that need preparation

### Rev Register Update

<<MUST item:A.5.31:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the live register with reference to this review

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.31:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (major regulator action, court ruling, customer contract restructure)

### Rev Next Date

<<SHOULD item:A.5.31:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
