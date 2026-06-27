---
name: product-principle-evidence-stored-vs-cited
description: "PRINCIPLE 2026-06-27: ArionComply is NOT a generic evidence repository — it's a compliance program ledger that tracks where evidence lives + freshness + ownership. Two coexisting modes per (tenant, leaf): STORED (small/startup tenants — evidence authored + held in-product via templates / forms / tabular_evidence_rows) vs CITED (larger tenants — evidence lives in source systems like Odoo / Okta / ServiceNow; ArionComply tracks cite metadata + auditor gates). Both modes coexist; same leaf can be partially stored + partially cited."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## The principle

User-stated 2026-06-27:

> "Our role is to make sure the tenant keeps up-to-date compliance
> evidence — not to store the evidence."
>
> "We might and will have a mixed bag: tenants where evidence
> ends up in our registers (small, startups) and others where
> evidence lives outside (these need auditor gates)."

## What ArionComply IS / IS NOT

| IS | IS NOT |
|---|---|
| Compliance program ledger — what evidence exists, where, who owns it, when verified, when next due | Generic evidence repository |
| Shape catalog — what auditor expects per leaf | The HR system / IAM / ITAM / DPO tool |
| Freshness clock + reminder system | The data store for HR / asset / access data (data sovereignty stays with the tenant where they want it) |
| Auditor-facing provenance surface ("here's how to find this evidence + here's how we know it's current") | A bookkeeping tool tenants fill with duplicate data |
| Where policies / procedures / scope statements naturally live (those have no better home) | Where registers / records / logs / inventories live for tenants that have their own system of record |

## Two coexisting modes per (tenant, leaf)

### Stored mode (current behaviour)

The default for small / startup tenants who DON'T have an external
system of record. ArionComply IS the system of record:

- Authored via templates (md / xlsx / docx download → edit → upload)
- Authored via forms (per-MUST entry)
- Persisted in `document_findings` + `tabular_evidence_rows`
- Auto-approved when source is `templated` / `form` (tenant-authored)
- Visible via evidence-class breakdown panel

Already shipped: templates v1+v2 anchors, native-format downloads,
xlsx round-trip, tenant profile, evidence-class UI.

### Cited mode (next chunk)

For tenants whose evidence lives in source systems (Arion uses
**Odoo** for HR; many tenants use Okta / ServiceNow / OneTrust /
LogicGate / Jira). ArionComply tracks WHERE it lives + freshness
+ ownership + verification gates:

- Tenant registers source per (leaf, system): "A.5.9 → Odoo
  Inventory module → URL → owner → cadence"
- Engine treats valid + fresh cite as evidence-present
- Auditor gates: periodic samples (uploaded via xlsx round-trip),
  verification attestations, last-verified date, next-due date
- Stale cite (last_verified + cadence_days < now) → engine flips
  back to "evidence-needed" until verified

### Mixed (per-leaf)

A single leaf can have BOTH modes contributing. Example for A.5.18
Access Rights:

- **Cite**: "Identity register lives in Azure AD" (covers
  identity_link + reg_subject_asset MUSTs)
- **Stored**: A.5.18 procedure document uploaded (covers procedure
  MUSTs)
- **Form**: per-quarter access review record entered via form
  (covers review_record MUSTs)

The engine considers each MUST satisfied if EITHER mode provides
evidence. No mode is privileged.

## What this implies for design

### Schema

New `external_evidence_source` table:

    external_evidence_source (
      id, tenant_id, leaf_id,
      source_system_name,    -- "Odoo HR", "Azure AD", etc.
      source_url,            -- direct link to where the data lives
      owner_user_id,         -- responsible person (FK to users)
      cadence_days,          -- expected refresh interval
      last_verified_at,      -- when tenant last attested accuracy
      sample_upload_id,      -- optional FK to latest sample upload
      next_review_due,       -- computed from last_verified + cadence
      created_at, updated_at, created_by, updated_by,
    )

Per (tenant, leaf, source) — multiple sources allowed for a leaf.

### Engine

A leaf is satisfied if EITHER:
- enough stored findings (current behavior) OR
- ≥1 fresh `external_evidence_source` row (last_verified within cadence)

`inference_source = 'external_cite'` (new) — auto-approved at write
time, same trust model as `templated` / `form` (tenant-authored
attestation). Goes through the existing `/api/v1/stage1/auto-approved`
visibility panel.

Stale cites (past next_review_due) are dropped from satisfaction
calc and surface as "needs verification" — engine flips leaf back
to NC/OFI until verified.

### UI

Evidence-class breakdown panel gains a third lane per leaf:

```
A.5.9 Asset Inventory
  Stored:    0/6 covered     [📊 .xlsx] [📄 .md]
  Cited:     Odoo Inventory   ✓ verified 2026-06-15 (next: 2026-09-15)
                              [Update] [Upload sample]
```

For startup tenants, "Cited" is empty (they don't have external
sources). For Arion, "Cited" is the primary cell for register leaves;
"Stored" is for policy/procedure leaves.

### Catalog tagging

Per evidence_type, whether cite-acceptable:

- **Cite-acceptable**: register, record, log, inventory, matrix
  (operational data that naturally lives in source systems)
- **Cite-NOT-acceptable**: policy, procedure, scope_note,
  classification_scheme, agreement_template (authored artefacts;
  no source system holds these)

A new `cite_acceptable: bool` field on `EvidenceRequirement`, or
derived from evidence_type via a lookup like
`_TABULAR_EVIDENCE_SUFFIXES`. Probably the latter — fewer fields,
follows existing convention.

## The "auditor gate" concept

Cited evidence needs gates because the auditor can't see the data
directly. Three gates we should support:

1. **Periodic sample**: tenant exports + uploads via xlsx round-trip
   on a cadence (quarterly is common). Uses existing
   `tabular_evidence_rows` storage. Auditor sees the sample as
   point-in-time proof the source data exists and matches the
   declared shape.
2. **Verification attestation**: tenant clicks "I verified
   $source against $leaf today" → updates `last_verified_at`.
   Same trust model as form submission (tenant-attested).
3. **Process documentation**: link or attached procedure showing
   how the source data is maintained (this often satisfies the
   PROCEDURE leaf of the same control).

The combination of cite + at least one gate = audit-defensible
without ArionComply needing to hold the data.

## What's NOT in scope

- **API connectors per vendor** (Odoo / Okta / ServiceNow pulls).
  Premature — explosion of integration work for marginal value
  over manual cite + sample. Revisit only when a specific tenant
  asks AND the volume justifies it.
- **Vendor catalog** with pre-known endpoints. Same reason.
- **Automated freshness via webhooks**. Tenant-attested freshness
  is sufficient for the auditor; webhook-driven is a v2 nicety.

## Tenant-shape implications

The product onboarding journey should probably ASK the tenant about
their shape early:

- "Do you have an HR system?" → if yes, route A.6.x leaves toward
  cite mode by default
- "Do you have an asset management system?" → if yes, route A.5.9
  toward cite
- "Do you have an IAM?" → if yes, route A.5.16 / A.5.18 toward cite

Small tenants check "no" → all leaves stay stored. Large tenants
check "yes" → register-class leaves default to cite.

This intersects with the tenant journey wizard backend ([[tenant-journey-wizard]]).

## Related

- [[template-tenant-profile-2026-06-26]] — tenant identity store;
  evolves naturally to include "external system inventory" (Odoo URL,
  Okta tenant id, etc.)
- [[template-xlsx-roundtrip-phase-b-2026-06-26]] — sample-upload
  mechanism reused for the verification-gate uploads
- [[evidence-class-breakdown-backend-2026-06-26]] — the UI surface
  that gains the third "Cited" lane
- [[tabular-evidence-rows-2026-06-26]] — sample storage when
  cited evidence ALSO uploads periodic samples
- [[tenant-journey-wizard-2026-06-24]] — the onboarding flow that
  surfaces "stored vs cited" choice per tenant shape
