---
name: template-tenant-profile-2026-06-26
description: "SHIPPED 2026-06-26: schema_v49 tenant_profile (k/v) + renderer extension + GET/PUT /api/v1/tenant/profile. Tenants now type CEO/CISO/DPO/ISMS-Manager/etc. names + registered address + company number + domain ONCE, see them substituted everywhere templates render. 22 placeholder occurrences across templates that previously stayed as literal `<<CEO_NAME>>` text now fill from tenant_profile. No new admin UI yet — API-only. xlsx/docx renderers unaffected since substitution happens upstream in render_template."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

`tenant_profile` table (`schema_v49`) — key/value store for
template-substitution placeholders that aren't core tenant identity:

    tenant_profile (tenant_id, profile_key, profile_value,
                    updated_at, updated_by)

Renderer (`rag/templates/renderer.py`) loads the rows alongside
`tenants`, extends `_substitute_placeholders` to apply
`profile_key='ceo_name'` → `<<CEO_NAME>>` substitution.

API:

- `GET /api/v1/tenant/profile` — full set of 13 known keys + any
  extras, current value + updated_at + `known` flag per row
- `PUT /api/v1/tenant/profile` — upsert/delete; body shape
  `{"profile": [{"key": "ceo_name", "value": "Jane Doe"}, ...]}`

Known keys (drive future admin UI form):

| Group | Keys |
|---|---|
| People | ceo_name, ciso_name, dpo_name, isms_manager_name, isms_owner_name, hr_partner_name, awareness_lead_name |
| Org metadata | registered_address, company_number, tenant_domain |
| Business context | product_or_service |
| Dates | approval_date, next_review_date |

Templates accept ANY placeholder following the convention — unknown
keys just stay as literal `<<NAME>>` text in the rendered output, so
the renderer is forgiving. The "known" set is an API/UI convenience,
not a substitution constraint.

## Convention

`<<UPPER_SNAKE_NAME>>` ↔ `profile_key = 'upper_snake_name'.lower()`.

Schema CHECK constrains keys to `^[a-z][a-z0-9_]*$` to keep the
mapping deterministic. PUT endpoint applies the same regex
defensively — invalid keys are silently dropped (no 400; we accept
mixed batches).

## Non-obvious decisions

### Key/value, not fixed columns on `tenants`

Templates may introduce new placeholders without schema migrations.
Today we use ~13 placeholders; tomorrow a new template might want
`<<AUDIT_FIRM_NAME>>` or `<<SUPERVISORY_AUTHORITY>>`. Adding a
column per placeholder doesn't scale; key/value does.

### `tenants` table wins on collision

If a stray profile row sets `profile_key='tenant_name'`, the
renderer must NOT use it to override the real tenant name. Achieved
by populating `fills` from `tenants` FIRST, then `fills.setdefault(...)`
from profile — `tenants` keys are already there and won't be
overwritten.

### Unknown placeholders stay literal

Forgiving by design. If a template uses `<<UNUSUAL_KEY>>` and the
tenant hasn't added a corresponding profile row, the rendered
output keeps `<<UNUSUAL_KEY>>` — visible to the tenant, who can
edit it by hand OR add the profile row later. Better than silently
substituting an empty string or crashing.

### GET returns the full known-key set with empty strings

So a future admin UI can render a complete form without merging
known-keys client-side. Each row carries `known: true|false`. Rows
beyond the known set (tenant added custom keys) appear after the
known ones — they get `known: false` for the UI to handle
separately (or surface as "Other custom values").

### Empty value = delete

PUT with `value: ""` deletes the row. Clean semantics for a future
form: an admin UI's "clear this field" action sends the same
payload shape as "set to empty". The renderer treats missing rows
identically to empty-string values (placeholder stays literal in
either case), so this collapses well.

### xlsx + docx renderers unaffected

Both operate on the body returned by `render_template()`, which has
already had substitutions applied. No changes needed in either
format-specific renderer — tenant identity flows through
transparently.

## Verified on Arion

13 keys upserted. A.5.1 ISP Policy rendered:
- `.md` → only `<<TEXT>>` placeholders remain (tenant-edit zones)
- `.docx` → zero placeholders; "ISMS Manager (Mutua John) operates
  the ISMS day-to-day..." renders with names baked in

## Roadmap

Builds on:
- [[templates-v1-foundation-2026-06-24]] — render_template +
  `_substitute_placeholders` foundation
- [[template-native-formats-xlsx-2026-06-26]] +
  [[template-native-formats-docx-2026-06-26]] — both formats
  inherit the substitution for free

Unblocks (deferred):
- Admin UI: a "Tenant Profile" page with the 13 known-key form
  + the placeholder annotated where it's used
- Inferred defaults in xlsx Document Fields "Your content"
  (e.g. seed `item:5.3:owner` with `isms_manager_name`)
- Tenant-aware ✓ Good examples ("For a SaaS company in
  `<<TENANT_COUNTRY>>` like yours, the typical retention is...")

## Related

- [[templates-v2-anchors-complete-2026-06-25]] — the 20 v2 anchors
  whose placeholders this fills.
- [[client-facts]] — sibling data store but yes/no flags about
  GDPR processing. Different shape, different audience —
  tenant_profile is human-facing identity; client_facts is
  engine-facing fact set.
