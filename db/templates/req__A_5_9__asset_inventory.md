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
---

# Inventory of Information and Associated Assets

## What this template gives you

The **register of everything you protect**. Without it, every other
control is operating in the dark — you can't apply access controls,
classification, retention, or risk treatment to assets you don't
know about. Auditors sample the register against reality (do these
exist? what's not on it?). A stale or aspirational register is a
common nonconformity.

## When to use it

Standing artefact required by **ISO/IEC 27001:2022 A.5.9**. The
register is **continuously maintained** — at least every 90 days
freshness, plus event-driven updates (new asset onboarded, retired,
ownership transferred).

## Before you start

- [ ] **4.3 ISMS Scope** clear — only in-scope assets in this register
- [ ] **A.5.12 Classification Scheme** in place — needed for MUST 3
- [ ] **5.3 Roles** clear — owners are named individuals/roles

## Cross-references

- **A.5.12 Classification** — every record gets a class
- **A.5.10 Acceptable Use** — references this register
- **A.5.11 Return of Assets** — closes register rows on leaver
- **A.5.16 Identity Management** — identities are also assets
- **A.5.21 ICT Supply Chain** — supplier-managed assets flagged
- **A.5.33 Records Protection** — records are a subset
- **A.8.10 Information Deletion** — disposal feeds back into the
  register

## Estimated effort

**1-3 days** for v1 (discovery + classification effort); **ongoing
operational cost** for maintenance.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Create per-asset records covering all in-scope categories

<<MUST item:A.5.9:asset_records>>
_Asset coverage — the register must include all asset types in
ISMS scope: information, software, hardware, services, cloud
resources, facilities (if in scope)._

State the categories you cover and how each category gets onto the
register. Categories typically: information assets (datasets,
documents), software (apps, libraries), hardware (devices, network
infra), services (SaaS, APIs), cloud resources (storage, compute,
identity stores), facilities (if you have premises in scope).

**✓ Good**: "Register covers (a) information assets — customer
datasets, employee records, IP, ISMS records; (b) software —
production services, internal tools, third-party licences; (c)
hardware — endpoints, network appliances (if any in scope), MFA
tokens; (d) services — SaaS subscriptions, managed APIs, paid
data feeds; (e) cloud resources — AWS accounts, S3 buckets,
databases, IAM roles, KMS keys; (f) facilities — N/A
(cloud-only per scope statement)."

<<TEXT>>

## 2. Name a per-asset owner

<<MUST item:A.5.9:owner_per_asset>>
_Accountability — every asset has a named owner with authority to
decide on its protection and risk treatment._

The owner is a **role or named individual** — not "IT" or "everyone".
For multi-stakeholder assets, a single accountable owner with
documented stakeholders.

**✓ Good**: "Ownership rules: (a) product engineering assets →
VP Engineering or delegated team lead. (b) customer data assets →
DPO is accountable + relevant product owner is the operational
owner. (c) Corporate IT assets → IT Manager. (d) Specific
inventory entries record the named role + current incumbent.
Re-assignment recorded in row history."

**✗ Avoid**: "Owner: IT team" (un-actionable).

<<TEXT>>

## 3. Classify every asset

<<MUST item:A.5.9:classification>>
_A.5.12 classification scheme applied to every row — the
classification drives downstream control intensity._

Each asset gets a class from the A.5.12 scheme. Without
classification, you can't apply the right protection. Multi-class
assets get the highest applicable class (the data inside an asset
wins over the asset itself).

**✓ Good**: "Each row carries the A.5.12 classification (Public /
Internal / Confidential / Restricted). PII flag set independently
on the same row (cross-cuts the class). Class is re-evaluated on
significant change to asset content or use."

<<TEXT>>

## 4. Record location / hosting per asset

<<MUST item:A.5.9:location>>
_Where the asset physically or logically resides — drives
jurisdictional, access, and physical-controls applicability._

For cloud resources: region (eu-west-1) + account. For SaaS: vendor
+ region. For data: storage system + (where relevant) physical
location. For hardware: site or assigned-to user.

**✓ Good**: "Location column captures: (a) cloud assets — provider
+ region + account ID + service. (b) SaaS — vendor + tenancy
region. (c) data sets — primary storage system + replication
locations (driven by GDPR transfer analysis). (d) endpoints —
assigned-user country (no fixed site for cloud-only)."

<<TEXT>>

## 5. Update timestamp per record

<<MUST item:A.5.9:last_updated>>
_Freshness signal — proves the register is alive, not snapshotted._

Each row carries a last-updated date. Stale rows surface in the
A.5.9 review (sibling leaf). Freshness target: every row touched
within 90 days OR has explicit "no-change-confirmed" attestation
within 90 days.

**✓ Good**: "Each row has 'last_updated' + 'last_attested'
columns. 'last_updated' = real change; 'last_attested' = owner
re-confirmed unchanged. Either resets the 90-day clock.
Quarterly review surfaces rows beyond 90 days for attestation
push."

<<TEXT>>

## 6. Tag asset type

<<MUST item:A.5.9:asset_type>>
_Type-specific controls — different asset types have different
applicable controls (e.g. A.8.x technological controls apply
differently to data vs hardware vs services)._

A typed register lets you pivot to "all software" or "all
services" for control-applicability sweeps.

**✓ Good**: Discrete column with values {information, software,
hardware, service, cloud_resource, facility}. Asset-type
distribution reviewed at the A.5.9 program review (sibling leaf).

<<TEXT>>

---

## Recommended additions

### Lifecycle status

<<SHOULD item:A.5.9:lifecycle_status>>
_Asset lifecycle awareness — onboarded / active / sunsetting /
retired._

Track lifecycle so retired assets don't carry stale controls and
sunset assets get the right compensating controls.

<<TEXT>>

### Dependencies

<<SHOULD item:A.5.9:dependencies>>
_Cross-asset coupling — useful for impact analysis (R-CIA chain)._

For each asset, list immediate dependencies (this DB → that
service; this service → that API key). Enables blast-radius
analysis at incident time + drives BCP scope.

<<TEXT>>

### Data Flow Inventory cross-link

<<SHOULD item:A.5.9:dfi_link>>
_PII-bearing assets → Art.30 RoPA data-flow inventory._

For any asset holding personal data, cross-link to the Art.30 RoPA
data-flow inventory row. Closes the ISO ↔ GDPR loop.

<<TEXT>>
