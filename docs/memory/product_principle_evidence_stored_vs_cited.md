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
2. **Verification attestation with changes_detected**: tenant
   clicks "I verified $source against $leaf today" → updates
   `last_verified_at` + records a REQUIRED `changes_detected`
   field describing what's different since last verification.
   Forces a real review, not rubber-stamp. Examples:
   - HR cite: "5 new employees onboarded since last verification;
     all completed mandatory training via Workday onboarding
     workflow. 1 contractor offboarded; access revoked per A.5.18
     leaver flow (Okta ticket #4521)."
   - IAM cite: "12 new identities added (matching HR new-hire
     list). 3 identities disabled (matching HR leavers). 2
     privileged-access additions reviewed + approved."
   - Asset cite: "47 → 53 total assets. New: 4 laptops (issued to
     new hires), 2 cloud subscriptions (S3 buckets for new
     project). Retired: nothing in this period."
   Future workflow: changes_detected can trigger follow-up actions
   (e.g. "new employee" → A.6.3 training-assignment workflow).
3. **Process documentation**: link or attached procedure showing
   how the source data is maintained (this often satisfies the
   PROCEDURE leaf of the same control).

The combination of cite + at least one gate = audit-defensible
without ArionComply needing to hold the data.

## v1 design decisions (locked 2026-06-27)

User-confirmed via design discussion:

- **Granularity: per-MUST**. Each cite row binds to one (must_id,
  source). UI groups by (source, leaf) for tenant + auditor view;
  data model stays atomic.
- **Verification**: click + named verifier (session user defaults)
  + REQUIRED `changes_detected` field (see above) + optional
  sample upload.
- **review_record evidence_type**: cite-acceptable (some tenants
  export review minutes from Jira/Confluence).
- **cadence_days**: defaults to leaf's `freshness_days` when set,
  else 365. Tenant can override per cite.
- **Stale handling**: grace = `min(cadence × 10%, 30 days)`. YELLOW
  in grace, RED after. Stale cites stay visible greyed-out with
  prominent "VERIFY NOW" CTA — never hidden.
- **Multiple cites per leaf**: allowed when different sources cover
  different subsets (Azure AD for employees + Okta for contractors).
  Unique constraint: `(tenant_id, must_id, source_system_name)`.

## v1 schema (schema_v50, planned)

Three tables:

```sql
-- 1. System registry — one row per (tenant, external system).
-- Bridge between citing the same source across many leaves.
CREATE TABLE tenant_external_system (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL,
  system_name         TEXT NOT NULL,            -- "Odoo HR" / "Azure AD" / "ServiceNow CMDB"
  system_url          TEXT,
  owner_user_id       UUID,                     -- FK to users
  default_cadence_days INTEGER NOT NULL DEFAULT 365,
  covers_evidence_types TEXT[] NOT NULL,        -- ["register", "record"] — narrows where this system is offered
  is_active           BOOLEAN NOT NULL DEFAULT TRUE,
  created_at, created_by, updated_at, updated_by,
  CONSTRAINT unique_system_per_tenant UNIQUE (tenant_id, system_name)
);

-- 2. Per-MUST cite rows. Each binds one must_id to one source.
-- Lookup-grouped by (tenant, leaf_id, system_id) for the UI/auditor view.
CREATE TABLE external_evidence_source (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            UUID NOT NULL,
  must_id              TEXT NOT NULL,
  leaf_id              TEXT NOT NULL,
  system_id            UUID NOT NULL REFERENCES tenant_external_system(id),
  cadence_days         INTEGER NOT NULL,         -- defaulted from leaf.freshness_days
  per_must_note        TEXT,                     -- optional: how this MUST is captured in source
  last_verified_at     TIMESTAMPTZ,
  next_review_due      TIMESTAMPTZ,              -- computed: last_verified_at + cadence
  is_active            BOOLEAN NOT NULL DEFAULT TRUE,
  created_at, created_by, updated_at, updated_by,
  CONSTRAINT unique_cite_per_must_system UNIQUE (tenant_id, must_id, system_id)
);

-- 3. Verification log — append-only history per (system, leaf).
-- One entry covers all MUST rows in the group simultaneously
-- (verify updates them all + appends one log row).
CREATE TABLE external_evidence_verification_log (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id           UUID NOT NULL,
  system_id           UUID NOT NULL REFERENCES tenant_external_system(id),
  leaf_id             TEXT NOT NULL,
  verified_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
  verified_by         UUID NOT NULL,             -- FK to users
  changes_detected    TEXT NOT NULL,             -- mandatory; the audit-grade payload
  sample_upload_id    UUID,                      -- optional FK to document_uploads
  note                TEXT                       -- optional free-text addition
);
```

RLS on all three tables. Append-only verification log; current state
lives on `external_evidence_source.last_verified_at` for fast read,
log retains history.

## Per-MUST entry form (the "template" for cite creation)

When tenant creates/edits a cite for a leaf, the UI is a per-MUST
checkbox form listing every MUST of the leaf. Backend writes N rows
in `external_evidence_source` (one per checked MUST). Same UI library
as the existing form lane (`POST /api/v1/dashboard/control/{ref}/template`),
adapted for cite metadata instead of free-text MUST values.

Form shape:

    Cite source for {leaf_id}

      Source:  [dropdown of tenant_external_system rows where
                covers_evidence_types includes this leaf's evidence_type]
      Cadence: [days; default from leaf.freshness_days]
      Owner:   [user dropdown; default = session user]

      Which MUSTs does this source cover?
      (renders every leaf.must_contain item as a row)

        ☑ {must.text}
          {must.id}
          [Optional per_must_note input]

        ☐ {next must, also pre-checked or unchecked based on
           current cite state if editing}
          ...

      [Cancel]    [Save — covers N of M MUSTs]

Submit posts the `covered_must_ids[]` array + cite metadata. Backend
upserts N rows (creates new, updates existing per_must_note, soft-
deletes removed).

## Three UI surfaces

| Surface | Use case | UI |
|---|---|---|
| Create cite | First time citing a source for a leaf | Per-MUST checkbox form above |
| Edit cite | Add/remove MUST coverage for an existing (source, leaf) | Same form, pre-checked from current state |
| Verify cite | Periodic refresh per cadence | Single dialog per (source, leaf): required `changes_detected` text + optional sample upload + optional note. Updates `last_verified_at` on ALL cite rows in the group + appends one row to `verification_log`. |

## v1 build plan (next session)

| Layer | Concrete change |
|---|---|
| Schema (v50) | tenant_external_system + external_evidence_source + verification_log |
| Catalog | `is_cite_acceptable(evidence_type)` predicate (tabular suffixes + review_record + extension list) |
| Engine | Per-MUST satisfaction: stored finding OR fresh cite. Stale cite dropped + warning. |
| API — system registry | GET/PUT/DELETE /api/v1/tenant/external-systems |
| API — cite | GET /api/v1/tenant/cites/leaf/{leaf_id} (grouped by source) |
| API — cite | PUT /api/v1/tenant/cites/leaf/{leaf_id}/source/{system_id} (create/edit; body has covered_must_ids[]) |
| API — verify | POST /api/v1/tenant/cites/leaf/{leaf_id}/source/{system_id}/verify (body: changes_detected required) |
| API — delete | DELETE /api/v1/tenant/cites/leaf/{leaf_id}/source/{system_id} |
| UI — leaf panel | New "Cited" sub-row per leaf grouped by source. Add/Edit/Verify/Remove. Color-coded freshness. |
| UI — profile | New "External systems" section for system registry CRUD |
| UI — onboarding | Journey wizard question: "Which systems do you use?" → creates tenant_external_system rows with sensible defaults |
| Visibility | /api/v1/dashboard/cites/needs-verification — list cites past/near due |

~2 sessions of focused work.

## Implementation scope (~1-2 sessions)

| Layer | Change |
|---|---|
| Schema (v50) | external_evidence_source + verification_log |
| Catalog | `is_cite_acceptable(evidence_type)` predicate (tabular suffixes + review_record + extension list) |
| Engine | Per-MUST satisfaction: (stored finding OR fresh cite). Stale cite dropped + surfaced. |
| API | GET/PUT/DELETE /api/v1/tenant/cites; POST /verify (with mandatory changes_detected) |
| UI | Evidence-class panel gains "Cited" sub-row per leaf, grouped by source. Add/Verify/Edit/Remove buttons. Color-coded freshness badge. |
| Visibility | `/api/v1/dashboard/cites/needs-verification` list + dashboard summary card |

## What's NOT in scope

- **API connectors per vendor** (Odoo / Okta / ServiceNow pulls).
  Premature — explosion of integration work for marginal value
  over manual cite + sample. Revisit only when a specific tenant
  asks AND the volume justifies it.
- **Vendor catalog** with pre-known endpoints. Same reason.
- **Automated freshness via webhooks**. Tenant-attested freshness
  is sufficient for the auditor; webhook-driven is a v2 nicety.
- **Auto-triggered follow-up workflows from changes_detected**
  (e.g. "new employee" → training assignment). Capture
  changes_detected in v1; build the workflow trigger in v2.

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
