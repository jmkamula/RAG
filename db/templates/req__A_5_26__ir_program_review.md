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
---

# Periodic Incident Response Program Review

> IR readiness erodes between exercises and between incidents. The review records the planned-interval check of the program: MTTC/MTTR trends, exercise outcomes, procedure currency against threat landscape, and the resulting calibration of roles, runbooks and contact lists

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.26:rev_date>>
_Why: 27002:5.26 — periodic_

<<TEXT>>

## 2. Reviewer identity (Incident Manager + InfoSec lead jointly)

<<MUST item:A.5.26:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. MTTC / MTTR / containment-success metrics analysed across the period

<<MUST item:A.5.26:rev_metrics>>
_Why: 27002:5.26 — improvement_

<<TEXT>>

## 4. Tabletop / simulation outcomes reviewed (or scheduled-but-not-yet-run noted)

<<MUST item:A.5.26:rev_exercise>>
_Why: 27002:5.26 — exercises_

<<TEXT>>

## 5. Procedure currency assessed against threat landscape + new control changes

<<MUST item:A.5.26:rev_procedure_currency>>
_Why: 27002:5.26 — keep current_

<<TEXT>>

## 6. Action items captured (e.g. revise containment runbook, refresh contact list, schedule exercise)

<<MUST item:A.5.26:rev_actions>>
_Why: 27002:5.26_

<<TEXT>>

## 7. Art.33 72h feasibility audited empirically across the period — count of personal-data incidents, count notified within 72h, root cause of any late notifications (parity with A.5.24:rev_gdpr_72h_feasibility)

<<MUST item:A.5.26:rev_72h_feasibility>>
_Why: GDPR Art.33.1 — A.5.24 is planning, A.5.26 is the real-incident proof_

<<TEXT>>

## 8. Bidirectional A.5.25 ↔ A.5.26 lifecycle pair check — every register row traces back to an A.5.25 triage decision (no orphan incidents) and every escalated triage decision opened an incident (no lost escalations)

<<MUST item:A.5.26:rev_identity_pair_25>>
_Why: Closes the silent A.5.25→A.5.26 handoff gap that 0/1-day reviews can't catch_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External benchmarking input considered (industry IR-metrics references)

<<SHOULD item:A.5.26:rev_benchmark>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.26:rev_next_date>>
_Why: Planning_

<<TEXT>>
