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

> A.8.6 baseline — what resources are monitored, what the current and expected demand is, what alert thresholds apply. The procedure, monitoring log and review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Resources monitored (CPU / memory / storage / network / DB connections / licences)

<<MUST item:A.8.6:bl_monitored_resources>>
_Why: 27002:8.6 — use of resources monitored_

<<TEXT>>

## 2. Current vs expected capacity baseline documented per resource

<<MUST item:A.8.6:bl_current_vs_expected>>
_Why: 27002:8.6 — current and expected capacity_

<<TEXT>>

## 3. Alert thresholds defined (warning / critical) per resource class

<<MUST item:A.8.6:bl_thresholds>>
_Why: 27002:8.6 — adjusted in line_

<<TEXT>>

## 4. Forecasting approach documented (historical trend / business-driven / leading-indicator)

<<MUST item:A.8.6:bl_forecasting>>
_Why: 27002:8.6 — expected capacity_

<<TEXT>>

## 5. Auto-scaling automation configured for elastic workloads (modern baseline)

<<MUST item:A.8.6:bl_automation>>
_Why: Modern cloud-native baseline_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Capacity baseline integrated with A.5.30 ICT readiness (DR target sizing)

<<SHOULD item:A.8.6:bl_dr_integration>>
_Why: Resilience_

<<TEXT>>
