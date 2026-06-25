---
leaf_id: req:6.3:change_program_review
control_ref: 6.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# ISMS Change Program Review

> Annual verification that change identification triggers are firing, the register reflects all actual changes, the A.8.32 boundary holds (freshness=365)

<!-- TABLE-COLUMNS leaf:req:6.3:change_program_review -->
<!-- column: item:6.3:rev_date -->
<!-- column: item:6.3:rev_reviewer -->
<!-- column: item:6.3:rev_register_currency -->
<!-- column: item:6.3:rev_silent_changes -->
<!-- column: item:6.3:rev_boundary_check -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:6.3:change_program_review -->
| Rev Date | Rev Reviewer | Rev Register Currency | Rev Silent Changes | Rev Boundary Check |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:6.3:change_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:6.3:rev_date>>
_Why: Clause 6.3 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:6.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + change-management lead)

### Rev Register Currency

<<MUST item:6.3:rev_register_currency>>
_Why: Cross-leaf coherence_

> _Standard text:_ Register currency check — every approved change reached implementation OR was withdrawn

### Rev Silent Changes

<<MUST item:6.3:rev_silent_changes>>
_Why: Drift detection_

> _Standard text:_ Silent-change sweep — verify no scope / policy / roles changes happened without a register entry

### Rev Boundary Check

<<MUST item:6.3:rev_boundary_check>>
_Why: Cross-control coherence_

> _Standard text:_ A.8.32 boundary check — no technical changes mis-routed to 6.3, no ISMS changes mis-routed to A.8.32

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:6.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
