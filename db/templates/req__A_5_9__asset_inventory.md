---
leaf_id: req:A.5.9:asset_inventory
control_ref: A.5.9
standard_id: ISO27001:2022
evidence_type: asset_register
trigger_type: universal
freshness_days: 90
template_version: 2
must_count: 6
should_count: 3
table_shape: true
---

# Inventory of Information and Associated Assets

<<DOC_CONTROL>>

## What this template gives you

The **register of everything you protect**. Without it, every other
control is operating in the dark — you can't apply access controls,
classification, retention, or risk treatment to assets you don't
know about. Auditors sample the register against reality (do these
exist? what's not on it?). A stale or aspirational register is a
common nonconformity.

## When to use it

Standing artefact required by **ISO/IEC 27001:2022 A.5.9**. The register is **continuously maintained** — at least every 90 days
freshness, plus event-driven updates (new asset onboarded, retired,
ownership transferred).

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**1-3 days** for v1 (discovery + classification effort); **ongoing operational cost** for maintenance.

---

<!-- TABLE-COLUMNS leaf:req:A.5.9:asset_inventory -->
<!-- column: item:A.5.9:asset_records -->
<!-- column: item:A.5.9:owner_per_asset -->
<!-- column: item:A.5.9:classification -->
<!-- column: item:A.5.9:location -->
<!-- column: item:A.5.9:last_updated -->
<!-- column: item:A.5.9:asset_type -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per asset. Each column maps to a MUST item the auditor
will check — empty columns count as unsatisfied. Add as many rows as
you need.

<!-- EDIT-ZONE-START leaf:req:A.5.9:asset_inventory -->
| Asset ID | Owner | Classification | Location | Last Updated | Asset Type |
|---|---|---|---|---|---|
|          |       |                |          |              |            |
|          |       |                |          |              |            |
|          |       |                |          |              |            |
<!-- EDIT-ZONE-END leaf:req:A.5.9:asset_inventory -->

## Column guidance — what to fill in

### Asset ID

<<MUST item:A.5.9:asset_records>>

> _Standard text:_ Asset records exist (information assets, software,
> hardware, services, cloud resources)

Stable unique identifier per asset. Use a convention that scales: a
prefix per asset type + a sequence (e.g. `AST-DATA-001`,
`AST-SVC-014`). Don't recycle IDs after disposal — keep them in the
historical view.

**✓ Good**: `ARION-SVC-001`, `ARION-DATA-CUST-PROD`, `ARION-IAM-OKTA`

**✗ Avoid**: free-text names that get edited ("Customer DB" → "Customer
Database" → "Cust DB") — the auditor can't trace the same asset across
quarters.

<<GUIDANCE>>

### Owner

<<MUST item:A.5.9:owner_per_asset>>

> _Standard text:_ Owner named per asset (individual or role
> accountable for protection and risk decisions)

A **role or named individual** with authority to decide on the asset's
protection. Not "IT" or "everyone". For multi-stakeholder assets, a
single accountable owner with documented stakeholders.

**✓ Good**: `VP Engineering (currently <<ISMS_MANAGER_NAME>>)`,
`DPO + Customer Success Director` (joint), `IT Manager`

**✗ Avoid**: "Owner: IT team" — un-actionable for the auditor.

<<GUIDANCE>>

### Classification

<<MUST item:A.5.9:classification>>

> _Standard text:_ Classification per asset (links to the A.5.12
> classification scheme)

A.5.12 scheme value: Public / Internal / Confidential / Restricted.
Plus a PII flag (independent of class — cross-cuts). Re-evaluate on
significant change to asset content or use.

**✓ Good**: `Restricted (+ PII)`, `Confidential`, `Internal`

**✗ Avoid**: "High / Medium / Low" if your scheme uses different terms
— the value must match A.5.12 exactly.

<<GUIDANCE>>

### Location

<<MUST item:A.5.9:location>>

> _Standard text:_ Location or hosting system where the asset resides
> (data centre, cloud region, endpoint pool)

Where the asset physically or logically resides. Drives jurisdictional,
access, and physical-controls applicability.

**✓ Good**:
- Cloud: `AWS eu-west-1 / account 123-prod / S3`
- SaaS: `Okta (EU pod, Frankfurt)`
- Data: `RDS prod-customers / replicated to eu-west-2`
- Endpoint: `assigned-user: <<TENANT_COUNTRY>> remote pool`

**✗ Avoid**: "Cloud" alone — auditor can't sample without region +
account.

<<GUIDANCE>>

### Last Updated

<<MUST item:A.5.9:last_updated>>

> _Standard text:_ Last-updated date per record (proves the register
> is actively maintained, not snapshotted)

Each row's last-updated date. Two columns help in practice:
`last_updated` (real change) vs `last_attested` (owner confirmed
unchanged). Either resets the 90-day freshness clock.

**✓ Good**: `2026-05-12` (updated) / `2026-06-22` (attested unchanged)

**✗ Avoid**: An entire register dated to the same day — auditor
sees that as a one-time snapshot, not active maintenance.

<<GUIDANCE>>

### Asset Type

<<MUST item:A.5.9:asset_type>>

> _Standard text:_ Asset type tag (information / software / hardware /
> service / facility) so type-specific controls can be applied

Discrete category from: `information`, `software`, `hardware`,
`service`, `cloud_resource`, `facility`. Lets you pivot to "all
software" or "all services" for control-applicability sweeps.

**✓ Good**: `information`, `cloud_resource`, `service`

**✗ Avoid**: Free-text variations ("software" / "Software" / "SW")
that break grouping queries.

---

<<GUIDANCE>>

## Recommended additional columns

_These strengthen the register but aren't strictly required for the
MUST checks. Add them as extra columns in the table if they apply._

### Lifecycle Status

<<SHOULD item:A.5.9:lifecycle_status>>

> _Standard text:_ Asset lifecycle awareness — onboarded / active /
> sunsetting / retired

Track lifecycle so retired assets don't carry stale controls and
sunset assets get the right compensating controls.

<<GUIDANCE>>

### Dependencies

<<SHOULD item:A.5.9:dependencies>>

> _Standard text:_ Cross-asset coupling — useful for impact analysis
> (R-CIA chain)

For each asset, list immediate dependencies (this DB → that service;
this service → that API key). Enables blast-radius analysis at
incident time + drives BCP scope.

<<GUIDANCE>>

### Data Flow Inventory cross-link (PII-bearing assets)

<<SHOULD item:A.5.9:dfi_link>>

> _Standard text:_ PII-bearing assets → Art.30 RoPA data-flow inventory

For any asset holding personal data, cross-link to the Art.30 RoPA
data-flow inventory row. Closes the ISO ↔ GDPR loop.

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
