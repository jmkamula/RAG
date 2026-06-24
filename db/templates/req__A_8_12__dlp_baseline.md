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

> A.8.12 baseline — DLP tool stack, channel coverage, classification-driven ruleset, alert-routing. Procedure, alert log and review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Channels with DLP controls active (email / web / endpoint / cloud-storage / IM / removable-media / printing)

<<MUST item:A.8.12:bl_channels>>
_Why: 27002:8.12 — systems, networks and any other devices_

<<TEXT>>

## 2. Classification-driven ruleset configured (cross-link to A.5.12 — stronger rules for higher classifications)

<<MUST item:A.8.12:bl_classification_ruleset>>
_Why: 27002:8.12 — sensitive information_

<<TEXT>>

## 3. Sensitive categories defined (PII / payment / health / IP / source-code) with detection patterns per category

<<MUST item:A.8.12:bl_sensitive_categories>>
_Why: 27002:8.12 — sensitive information_

<<TEXT>>

## 4. Alert routing configured (severity tiering, ticketing destination, incident-team escalation)

<<MUST item:A.8.12:bl_alert_routing>>
_Why: 27002:8.12 — measures applied_

<<TEXT>>

## 5. Block-vs-alert mode per channel per category documented (block default for highest-classification leaks)

<<MUST item:A.8.12:bl_block_vs_alert>>
_Why: 27002:8.12 — measures_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cloud-native DLP (CASB / cloud storage scanning / SaaS connectors) where applicable

<<SHOULD item:A.8.12:bl_cloud_native_coverage>>
_Why: Modern environment_

<<TEXT>>
