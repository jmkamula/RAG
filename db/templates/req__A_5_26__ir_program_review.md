---
leaf_id: req:A.5.26:ir_program_review
control_ref: A.5.26
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 8
should_count: 2
table_shape: true
---

# Periodic Incident Response Program Review

> IR readiness erodes between exercises and between incidents. The review records the planned-interval check of the program: MTTC/MTTR trends, exercise outcomes, procedure currency against threat landscape, and the resulting calibration of roles, runbooks and contact lists

<!-- TABLE-COLUMNS leaf:req:A.5.26:ir_program_review -->
<!-- column: item:A.5.26:rev_date -->
<!-- column: item:A.5.26:rev_reviewer -->
<!-- column: item:A.5.26:rev_metrics -->
<!-- column: item:A.5.26:rev_exercise -->
<!-- column: item:A.5.26:rev_procedure_currency -->
<!-- column: item:A.5.26:rev_actions -->
<!-- column: item:A.5.26:rev_72h_feasibility -->
<!-- column: item:A.5.26:rev_identity_pair_25 -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.26:ir_program_review -->
| Rev Date | Rev Reviewer | Rev Metrics | Rev Exercise | Rev Procedure Currency | Rev Actions | Rev 72H Feasibility | Rev Identity Pair 25 |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.26:ir_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.26:rev_date>>
_Why: 27002:5.26 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.5.26:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Incident Manager + InfoSec lead jointly)

### Rev Metrics

<<MUST item:A.5.26:rev_metrics>>
_Why: 27002:5.26 — improvement_

> _Standard text:_ MTTC / MTTR / containment-success metrics analysed across the period

### Rev Exercise

<<MUST item:A.5.26:rev_exercise>>
_Why: 27002:5.26 — exercises_

> _Standard text:_ Tabletop / simulation outcomes reviewed (or scheduled-but-not-yet-run noted)

### Rev Procedure Currency

<<MUST item:A.5.26:rev_procedure_currency>>
_Why: 27002:5.26 — keep current_

> _Standard text:_ Procedure currency assessed against threat landscape + new control changes

### Rev Actions

<<MUST item:A.5.26:rev_actions>>
_Why: 27002:5.26_

> _Standard text:_ Action items captured (e.g. revise containment runbook, refresh contact list, schedule exercise)

### Rev 72H Feasibility

<<MUST item:A.5.26:rev_72h_feasibility>>
_Why: GDPR Art.33.1 — A.5.24 is planning, A.5.26 is the real-incident proof_

> _Standard text:_ Art.33 72h feasibility audited empirically across the period — count of personal-data incidents, count notified within 72h, root cause of any late notifications (parity with A.5.24:rev_gdpr_72h_feasibility)

### Rev Identity Pair 25

<<MUST item:A.5.26:rev_identity_pair_25>>
_Why: Closes the silent A.5.25→A.5.26 handoff gap that 0/1-day reviews can't catch_

> _Standard text:_ Bidirectional A.5.25 ↔ A.5.26 lifecycle pair check — every register row traces back to an A.5.25 triage decision (no orphan incidents) and every escalated triage decision opened an incident (no lost escalations)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Benchmark

<<SHOULD item:A.5.26:rev_benchmark>>
_Why: Audit defensibility_

> _Standard text:_ External benchmarking input considered (industry IR-metrics references)

### Rev Next Date

<<SHOULD item:A.5.26:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
