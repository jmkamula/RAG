---
leaf_id: req:A.5.9:asset_discovery_upstream
control_ref: A.5.9
standard_id: ISO27001:2022
evidence_type: discovery_record
trigger_type: universal
template_version: 1
must_count: 4
should_count: 2
table_shape: true
---

# Asset Discovery and Onboarding Upstream

<<DOC_CONTROL>>

> The upstream that feeds the register. Where the lifecycle procedure covers intake of known new assets, the discovery upstream documents how the org finds assets it didn't already know about — network scans, cloud-tenant inventory APIs, procurement export, endpoint-management exports — and how those feeds reconcile into the register

<!-- TABLE-COLUMNS leaf:req:A.5.9:asset_discovery_upstream -->
<!-- column: item:A.5.9:disc_sources -->
<!-- column: item:A.5.9:disc_cadence -->
<!-- column: item:A.5.9:disc_reconciliation -->
<!-- column: item:A.5.9:disc_scope_coverage -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document how your organization discovers previously unknown assets, such as through network scans or inventory exports, and tracks how these assets are added to your official register.

## When to use it

Use this template whenever you need to record or update the ways your environment identifies and onboards new assets, especially when new discovery methods or sources are introduced. Update it as needed to keep your records current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing the required sections for the first time, plus additional time for each asset source or discovery method you need to document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.9:asset_discovery_upstream -->
| Disc Sources | Disc Cadence | Disc Reconciliation | Disc Scope Coverage |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.9:asset_discovery_upstream -->

## Column guidance — what to fill in

### Disc Sources

<<MUST item:A.5.9:disc_sources>>
_Why: 27002:5.9 — develop_

> _Standard text:_ Discovery sources enumerated (network scan tool, CSPM tool, EDR/MDM inventory, procurement system, license database)

<<GUIDANCE>>

### Disc Cadence

<<MUST item:A.5.9:disc_cadence>>
_Why: 27002:5.9 — maintained_

> _Standard text:_ Discovery cadence per source (continuous / daily / weekly)

<<GUIDANCE>>

### Disc Reconciliation

<<MUST item:A.5.9:disc_reconciliation>>
_Why: Closes the discovery loop_

> _Standard text:_ Reconciliation rule — discovered-but-not-in-register entries are flagged for owner assignment and classification

<<GUIDANCE>>

### Disc Scope Coverage

<<MUST item:A.5.9:disc_scope_coverage>>
_Why: 27002:5.9 — completeness_

> _Standard text:_ Coverage statement — what categories of assets each source covers and where gaps exist (e.g., personal devices, OT)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Disc A812 Link

<<SHOULD item:A.5.9:disc_a812_link>>
_Why: Cross-control coherence_

> _Standard text:_ Cross-link to A.8.12 (data leakage prevention) or A.8.20 (network mapping) where those scans double as discovery

<<GUIDANCE>>

### Disc Gap Remediation

<<SHOULD item:A.5.9:disc_gap_remediation>>
_Why: Continuous improvement_

> _Standard text:_ Process for closing coverage gaps (procuring new tools, mandating registration in ungovernable zones)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
