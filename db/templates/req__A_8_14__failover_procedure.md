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

<<DOC_CONTROL>>

> Operational counterpart — how failover is invoked, who has authority, failback path, cross-control wiring to A.5.30 ICT readiness

## What this template gives you

This template helps you document your organization's process for handling system failovers, including who is responsible, how to switch over and back, and how it connects to ICT readiness requirements.

## When to use it

Use this whenever your environment requires a clear, up-to-date procedure for managing failover events. Review and update the document whenever your processes or systems change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes to complete this from scratch, as each required section takes around 10 to 15 minutes to write.

## 1. Failover invocation authority per service (automated vs manual; on-call authority)

<<MUST item:A.8.14:proc_failover_authority>>
_Why: 27002:8.14 — sufficient_

<<GUIDANCE>>

<<TEXT>>

## 2. Per-service failover runbook (steps, validation checks, success criteria)

<<MUST item:A.8.14:proc_runbook>>
_Why: Operational maturity_

<<GUIDANCE>>

<<TEXT>>

## 3. Failback procedure — return to primary after recovery (often more risky than failover)

<<MUST item:A.8.14:proc_failback>>
_Why: Often overlooked_

<<GUIDANCE>>

<<TEXT>>

## 4. Cross-link to A.5.30 ICT readiness — coordinated with broader recovery plan

<<MUST item:A.8.14:proc_a530_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 5. Stakeholder communications during failover (status page, customer notifications)

<<MUST item:A.8.14:proc_communications>>
_Why: Operational discipline_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named procedure owner (Site Reliability lead with Infrastructure partner)

<<SHOULD item:A.8.14:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
