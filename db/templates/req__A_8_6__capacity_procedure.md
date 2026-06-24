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

> Operational counterpart — how thresholds trigger action, escalation paths, change controls for capacity expansion

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Escalation paths when thresholds breached (engineering → procurement → executive)

<<MUST item:A.8.6:proc_escalation>>
_Why: 27002:8.6 — adjusted_

<<TEXT>>

## 2. Cross-link to A.8.32 change management for capacity expansion deployments

<<MUST item:A.8.6:proc_change_link>>
_Why: Cross-control coherence_

<<TEXT>>

## 3. Forecast review cadence (quarterly minimum; monthly for elastic / cost-sensitive workloads)

<<MUST item:A.8.6:proc_forecast_cadence>>
_Why: 27002:8.6 — expected capacity_

<<TEXT>>

## 4. Demand intake from business stakeholders (new product launches, M&A, seasonal events)

<<MUST item:A.8.6:proc_demand_intake>>
_Why: 27002:8.6 — expected capacity_

<<TEXT>>

## 5. Named procedure owner (Infrastructure lead with Finance partner for cost-tied capacity)

<<MUST item:A.8.6:proc_owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Threshold-breach runbook for common scenarios

<<SHOULD item:A.8.6:proc_runbook>>
_Why: Operational maturity_

<<TEXT>>
