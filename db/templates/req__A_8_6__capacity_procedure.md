---
leaf_id: req:A.8.6:capacity_procedure
control_ref: A.8.6
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Capacity Management Procedure

<<DOC_CONTROL>>

> Operational counterpart — how thresholds trigger action, escalation paths, change controls for capacity expansion

## What this template gives you

This template helps you document how your organization manages capacity, including when to take action, who to escalate to, and how to handle changes when expanding resources.

## When to use it

Use this whenever you need to outline your process for monitoring and responding to capacity thresholds in your environment, and update it whenever your procedures or escalation paths change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this from scratch, as you'll need to cover several key steps and details in your procedure.

## 1. Escalation paths when thresholds breached (engineering → procurement → executive)

<<MUST item:A.8.6:proc_escalation>>
_Why: 27002:8.6 — adjusted_

<<GUIDANCE>>

<<TEXT>>

## 2. Cross-link to A.8.32 change management for capacity expansion deployments

<<MUST item:A.8.6:proc_change_link>>
_Why: Cross-control coherence_

<<GUIDANCE>>

<<TEXT>>

## 3. Forecast review cadence (quarterly minimum; monthly for elastic / cost-sensitive workloads)

<<MUST item:A.8.6:proc_forecast_cadence>>
_Why: 27002:8.6 — expected capacity_

<<GUIDANCE>>

<<TEXT>>

## 4. Demand intake from business stakeholders (new product launches, M&A, seasonal events)

<<MUST item:A.8.6:proc_demand_intake>>
_Why: 27002:8.6 — expected capacity_

<<GUIDANCE>>

<<TEXT>>

## 5. Named procedure owner (Infrastructure lead with Finance partner for cost-tied capacity)

<<MUST item:A.8.6:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Threshold-breach runbook for common scenarios

<<SHOULD item:A.8.6:proc_runbook>>
_Why: Operational maturity_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
