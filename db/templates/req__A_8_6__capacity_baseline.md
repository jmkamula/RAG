---
leaf_id: req:A.8.6:capacity_baseline
control_ref: A.8.6
standard_id: ISO27001:2022
evidence_type: configuration_baseline
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Capacity Monitoring Baseline

<<DOC_CONTROL>>

> A.8.6 baseline — what resources are monitored, what the current and expected demand is, what alert thresholds apply. The procedure, monitoring log and review are sibling leaves

## What this template gives you

This template helps you clearly document which resources are being monitored, how much capacity is currently used, what future demand is expected, and when alerts should be triggered. It's useful for keeping track of your environment's capacity and ensuring you meet compliance requirements.

## When to use it

Use this template whenever you need to establish or update a baseline for monitoring your environment's capacity. Refresh the document as needed to reflect changes in resources, demand, or alert thresholds.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this template from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Resources monitored (CPU / memory / storage / network / DB connections / licences)

<<MUST item:A.8.6:bl_monitored_resources>>
_Why: 27002:8.6 — use of resources monitored_

<<GUIDANCE>>

<<TEXT>>

## 2. Current vs expected capacity baseline documented per resource

<<MUST item:A.8.6:bl_current_vs_expected>>
_Why: 27002:8.6 — current and expected capacity_

<<GUIDANCE>>

<<TEXT>>

## 3. Alert thresholds defined (warning / critical) per resource class

<<MUST item:A.8.6:bl_thresholds>>
_Why: 27002:8.6 — adjusted in line_

<<GUIDANCE>>

<<TEXT>>

## 4. Forecasting approach documented (historical trend / business-driven / leading-indicator)

<<MUST item:A.8.6:bl_forecasting>>
_Why: 27002:8.6 — expected capacity_

<<GUIDANCE>>

<<TEXT>>

## 5. Auto-scaling automation configured for elastic workloads (modern baseline)

<<MUST item:A.8.6:bl_automation>>
_Why: Modern cloud-native baseline_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Capacity baseline integrated with A.5.30 ICT readiness (DR target sizing)

<<SHOULD item:A.8.6:bl_dr_integration>>
_Why: Resilience_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
