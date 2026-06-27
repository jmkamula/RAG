---
name: cite-mode-v1-backend-2026-06-27
description: "SHIPPED 2026-06-27: cite-mode v1 backend. schema_v50 (3 tables: tenant_external_system + external_evidence_source + external_evidence_verification_log) + rag/posture/cite_mode.py (is_cite_acceptable predicate + freshness helpers) + leaf_evaluators._fetch_recognised_cites (engine union: stored OR fresh cite) + 6 API endpoints (system registry CRUD + cite CRUD + verify + log). Closed-loop verified end-to-end: register system → cite 3 MUSTs → verify → engine flips leaf 0/6 → 2/6 immediately. Frontend (Cited lane + system registry UI + checkbox form + verify dialog) deferred to next chunk."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

### Schema (v50)

`db/schema_v50_external_evidence.sql` — three tables:

- **`tenant_external_system`** — per (tenant, system) registry.
  Columns: system_name, system_url, owner_user_id,
  default_cadence_days, covers_evidence_types[], is_active.
  Unique (tenant_id, system_name). RLS-enabled.

- **`external_evidence_source`** — per-MUST cite rows.
  Columns: must_id, leaf_id, system_id (FK), cadence_days,
  per_must_note, last_verified_at, next_review_due (app-maintained),
  is_active. Unique (tenant_id, must_id, system_id).
  CHECK constraints enforce must_id / leaf_id format. RLS-enabled.

- **`external_evidence_verification_log`** — append-only audit
  history. Columns: system_id (FK), leaf_id, verified_at,
  verified_by, changes_detected (REQUIRED, non-empty), note,
  sample_upload_id, musts_covered_count. Grants only SELECT +
  INSERT (audit integrity). RLS-enabled.

### Catalog tag

`rag/posture/cite_mode.py`:

- `is_cite_acceptable(evidence_type) -> bool` — explicit
  operational allowlist (register / record / log / inventory /
  matrix / baseline / approval / DPO-software types) + suffix
  fallback (`_register`, `_record`, etc.). Authored-artefact
  types (policy / procedure / scope_note / agreement_template /
  charter / classification_scheme) return False.
- `is_cite_fresh(last_verified_at, cadence_days)` — grace =
  `min(cadence_days * 10%, 30 days)`. Fresh iff `now <=
  last_verified_at + (cadence + grace) days`.
- `next_review_due(last_verified_at, cadence_days)` — last +
  cadence days (the YELLOW threshold; past this is grace, then
  RED/stale).

### Engine integration

`rag/posture/leaf_evaluators.GenericLeafEvaluator`:

- New `_fetch_recognised_cites(must_item_ids)` method. SQL filter
  expresses the grace formula directly: `now() <= last_verified_at
  + make_interval(days => cadence_days + LEAST(GREATEST(cadence_days
  / 10, 1), 30))`. Returns (set of recognised must_ids,
  latest verified_at).
- Existing `_fetch_recognised_items` UNIONs in the cite set:
  `recognised.update(cite_recognised)`.
- **Bug found + fixed** mid-smoke: original code had
  `if not per_item_rows: return set(), None` early-return after
  the stored-findings query. That killed the cite path for leaves
  with zero stored findings (which is exactly the cite-only case).
  Removed; cite query always runs.

### API endpoints

- `GET /api/v1/tenant/external-systems` — list registered systems
- `PUT /api/v1/tenant/external-systems` — create/update one
  (`id: null` = create)
- `DELETE /api/v1/tenant/external-systems/{id}` — soft-delete;
  cascades to soft-delete dependent cites
- `GET /api/v1/tenant/cites/leaf/{leaf_id:path}` — grouped by
  source system with per-MUST freshness flags
- `PUT /api/v1/tenant/cites/leaf/{leaf_id:path}/source/{system_id}`
  — per-MUST checkbox form upsert. Body: `covered_must_ids[]` +
  optional `cadence_days` (defaults from system) + optional
  `per_must_notes{}`. Inserts new, updates existing, soft-deletes
  removed. Returns `{inserted, updated, removed}` counts.
- `POST /api/v1/tenant/cites/.../source/{system_id}/verify` —
  verify. Body REQUIRES `changes_detected` (400 if empty).
  Updates last_verified_at + next_review_due on all cites in
  group; appends verification_log row.
- `GET /api/v1/tenant/cites/.../source/{system_id}/log` — audit
  history newest-first

`:path` converter on the `leaf_id` route parameter — the leaf_id
format (`req:A.6.1:screening_record_register`) contains colons
that FastAPI's default UUID-shaped path matcher rejects.

## Smoke-test result (end-to-end closed loop)

Verified on Arion 2026-06-27:

1. Registered "Odoo HR" system (90-day cadence,
   covers_evidence_types = `[register, review_record, approval]`)
2. Created cite for `req:A.6.1:screening_record_register`
   covering 3 MUSTs (2 valid catalog ids + 1 wrong id that the
   schema accepted but the engine ignored)
3. Verified with realistic `changes_detected` text
4. Engine breakdown: A.6.1 register leaf went 0/6 → **2/6**.
   Two valid cites recognised; wrong id ignored. Overall A.6.1
   17% → 26%.

The wrong id was due to my test data error, not a system bug. But
it surfaces a hardening opportunity (below).

## Non-obvious decisions

### Unverified cites don't count

A cite with `last_verified_at IS NULL` is NOT considered fresh
by the engine. Tenants must explicitly verify at least once before
a cite counts toward satisfaction. Reason: "I added the cite"
isn't an attestation — verification IS the attestation. Caught
during smoke: cites were correctly excluded from satisfaction
until I called the verify endpoint.

### Grace formula in SQL, not Python

Computed in the WHERE clause via `make_interval(days =>
cadence_days + LEAST(GREATEST(cadence_days / 10, 1), 30))`.
Lets the DB do filtering server-side; no Python-side
stale-check loop. The 30-day cap prevents grace inflating on
ultra-long cadences; the floor of 1 day prevents zero-grace on
very short cadences.

### Append-only verification log

Grants only `SELECT, INSERT` on the log table (no UPDATE/DELETE).
Once a verification is recorded, it can't be edited or removed
through the app — only via direct DB admin. Audit-integrity is
non-negotiable for cite mode (the log IS the auditor evidence).

### Tenant-table-wins-collision in profile substitution doesn't
### apply here

`tenant_profile` (schema_v49) had a "tenants table wins on
collision" rule. `tenant_external_system` doesn't have that
problem because the system_name space is open and tenant-owned —
there's no "core" set we need to protect. Tenant freedom is fine.

## Hardening worth adding (deferred)

- **Catalog validation on cite write**: today, PUT
  `/cites/leaf/{leaf_id}/source/{system_id}` accepts any
  `covered_must_ids[]` as long as format-regex passes. Should
  validate each id is actually in the catalog (via the canonical
  `ALL_EVIDENCE_REQUIREMENTS + DerivedSpec.direct_evidence` union)
  before insert. Same pattern as the catalog-membership predicate
  documented in [[feedback-validate-set-membership]].
- **leaf_id ↔ must_id consistency**: validate that each must_id's
  parent leaf matches the URL's `leaf_id`. Today caller can claim
  to cite for `req:A.6.1:screening_record_register` with MUSTs
  that belong to a different leaf — the engine still recognises
  them (because it queries by must_id), but the audit trail
  becomes misleading. Detect + 400.

## What's NOT in scope (frontend coming next)

- **Frontend** — Cited lane on evidence-class panel + system
  registry section on Profile page + per-MUST checkbox form
  modal + verify dialog with mandatory changes_detected text +
  JS `isCiteAcceptable()` mirror predicate
- **Visibility endpoint** — `/api/v1/dashboard/cites/needs-verification`
  listing cites past or near due
- **Dashboard freshness card** — summary count of due/overdue cites
- **Onboarding integration** — journey wizard question seeding
  `tenant_external_system` rows at first sign-in

## Related

- [[product-principle-evidence-stored-vs-cited]] — the design that
  drove this implementation (locked v1 design)
- [[product-concept-evidence-cascade-2026-06-27]] — strategic
  successor; cascade fires when verifications report
  structured changes
- [[feedback-validate-set-membership]] — canonical catalog union
  pattern; hardening opportunity above
- [[evidence-class-breakdown-backend-2026-06-26]] — the dashboard
  surface the cited lane plugs into
- [[template-tenant-profile-2026-06-26]] — sibling tenant-attested
  data store (Profile substitution values); cite-mode UI may
  borrow form patterns from the Profile UI
