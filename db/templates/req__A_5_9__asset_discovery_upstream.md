---
leaf_id: req:A.5.9:asset_discovery_upstream
control_ref: A.5.9
standard_id: ISO27001:2022
evidence_type: discovery_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
---

# Asset Discovery and Onboarding Upstream

> The upstream that feeds the register. Where the lifecycle procedure covers intake of known new assets, the discovery upstream documents how the org finds assets it didn't already know about — network scans, cloud-tenant inventory APIs, procurement export, endpoint-management exports — and how those feeds reconcile into the register

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Discovery sources enumerated (network scan tool, CSPM tool, EDR/MDM inventory, procurement system, license database)

<<MUST item:A.5.9:disc_sources>>
_Why: 27002:5.9 — develop_

<<TEXT>>

## 2. Discovery cadence per source (continuous / daily / weekly)

<<MUST item:A.5.9:disc_cadence>>
_Why: 27002:5.9 — maintained_

<<TEXT>>

## 3. Reconciliation rule — discovered-but-not-in-register entries are flagged for owner assignment and classification

<<MUST item:A.5.9:disc_reconciliation>>
_Why: Closes the discovery loop_

<<TEXT>>

## 4. Coverage statement — what categories of assets each source covers and where gaps exist (e.g., personal devices, OT)

<<MUST item:A.5.9:disc_scope_coverage>>
_Why: 27002:5.9 — completeness_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to A.8.12 (data leakage prevention) or A.8.20 (network mapping) where those scans double as discovery

<<SHOULD item:A.5.9:disc_a812_link>>
_Why: Cross-control coherence_

<<TEXT>>

### 2. Process for closing coverage gaps (procuring new tools, mandating registration in ungovernable zones)

<<SHOULD item:A.5.9:disc_gap_remediation>>
_Why: Continuous improvement_

<<TEXT>>
