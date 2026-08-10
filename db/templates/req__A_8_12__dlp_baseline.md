---
leaf_id: req:A.8.12:dlp_baseline
control_ref: A.8.12
standard_id: ISO27001:2022
evidence_type: configuration_baseline
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# DLP Baseline

<<DOC_CONTROL>>

> A.8.12 baseline — DLP tool stack, channel coverage, classification-driven ruleset, alert-routing. Procedure, alert log and review are sibling leaves

## What this template gives you

This template helps you document your data loss prevention (DLP) tool setup, including which channels are covered, how rules are set based on data classification, and how alerts are routed and reviewed.

## When to use it

Use this whenever you need to describe or update your DLP configuration, as it should always reflect your current environment and be refreshed whenever changes are made.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this from scratch, as each required section takes around 10 to 15 minutes to fill in.

## 1. Channels with DLP controls active (email / web / endpoint / cloud-storage / IM / removable-media / printing)

<<MUST item:A.8.12:bl_channels>>
_Why: 27002:8.12 — systems, networks and any other devices_

<<GUIDANCE>>

<<TEXT>>

## 2. Classification-driven ruleset configured (cross-link to A.5.12 — stronger rules for higher classifications)

<<MUST item:A.8.12:bl_classification_ruleset>>
_Why: 27002:8.12 — sensitive information_

<<GUIDANCE>>

<<TEXT>>

## 3. Sensitive categories defined (PII / payment / health / IP / source-code) with detection patterns per category

<<MUST item:A.8.12:bl_sensitive_categories>>
_Why: 27002:8.12 — sensitive information_

<<GUIDANCE>>

<<TEXT>>

## 4. Alert routing configured (severity tiering, ticketing destination, incident-team escalation)

<<MUST item:A.8.12:bl_alert_routing>>
_Why: 27002:8.12 — measures applied_

<<GUIDANCE>>

<<TEXT>>

## 5. Block-vs-alert mode per channel per category documented (block default for highest-classification leaks)

<<MUST item:A.8.12:bl_block_vs_alert>>
_Why: 27002:8.12 — measures_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cloud-native DLP (CASB / cloud storage scanning / SaaS connectors) where applicable

<<SHOULD item:A.8.12:bl_cloud_native_coverage>>
_Why: Modern environment_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
