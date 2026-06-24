---
leaf_id: req:A.8.14:failover_procedure
control_ref: A.8.14
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Failover Procedure

> Operational counterpart — how failover is invoked, who has authority, failback path, cross-control wiring to A.5.30 ICT readiness

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Failover invocation authority per service (automated vs manual; on-call authority)

<<MUST item:A.8.14:proc_failover_authority>>
_Why: 27002:8.14 — sufficient_

<<TEXT>>

## 2. Per-service failover runbook (steps, validation checks, success criteria)

<<MUST item:A.8.14:proc_runbook>>
_Why: Operational maturity_

<<TEXT>>

## 3. Failback procedure — return to primary after recovery (often more risky than failover)

<<MUST item:A.8.14:proc_failback>>
_Why: Often overlooked_

<<TEXT>>

## 4. Cross-link to A.5.30 ICT readiness — coordinated with broader recovery plan

<<MUST item:A.8.14:proc_a530_link>>
_Why: Cross-control coherence_

<<TEXT>>

## 5. Stakeholder communications during failover (status page, customer notifications)

<<MUST item:A.8.14:proc_communications>>
_Why: Operational discipline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Site Reliability lead with Infrastructure partner)

<<SHOULD item:A.8.14:proc_owner>>
_Why: Accountability_

<<TEXT>>
