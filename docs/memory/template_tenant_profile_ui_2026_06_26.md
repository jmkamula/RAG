---
name: template-tenant-profile-ui-2026-06-26
description: "SHIPPED 2026-06-26: 'Profile' admin UI in static/arioncomply.html — fifth topbar mode alongside Dashboard / Queue / Chat / Documents. Form rendered from the enriched GET /api/v1/tenant/profile response (now includes group/label/description/reference_count per key). Empty fields visually flagged; per-row footer shows the <<UPPER_SNAKE>> placeholder convention. Closes the 'type once, see everywhere' loop — compliance officers no longer need curl to populate their profile."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

Backend extension to `GET /api/v1/tenant/profile` — response now
carries per-key metadata for the UI:

- `group` — People / Organisation / Business / Dates / Other
- `label` — human-grade name ("CEO name", not `<<CEO_NAME>>`)
- `description` — one-sentence explanation
- `reference_count` — distinct templates that reference this
  placeholder (computed at request time by scanning the
  `templates` table for `<<UPPER_SNAKE>>` occurrences)

A new module-level `_TENANT_PROFILE_KEYS` catalog drives both the
GET response shape and the future admin UI form. Adding a new
known placeholder = add a row here.

Frontend (`static/arioncomply.html`):

- New `Profile` topbar entry, extends the existing `setMode`
  pattern (`['dashboard','queue','chat','docs','profile']`)
- `loadProfile()` calls the enriched GET, `renderProfile(rows)`
  groups by `group` and emits a form per group
- Each row: label + description + reference-count badge
  ("Used in 7 templates") + text input + convention footer
  ("↳ replaces `<<ISMS_MANAGER_NAME>>` in templates")
- Empty fields outlined in soft red (`#E8B5B5`) with an "empty"
  tag — visible gap before download
- Top progress card: "N of M fields filled" + explainer
- `saveTenantProfile()` collects all inputs, batches into PUT,
  shows `{upserted, deleted}` counts in the Save button, reloads
  on success

## Non-obvious decisions

### Backend computes reference_count, not frontend

Frontend doesn't have access to the `templates` table content
(returning 4133 MUST item ids + ~645 template bodies per page load
would be wasteful). Backend scans once per request and returns
counts. ~10ms on Arion's catalog; not worth caching yet.

### Per-request scan, no cache

645 templates × short regex scan = a few milliseconds. Invalidation
complexity (templates table can change on load_to_postgres runs,
profile keys catalog can change in code) isn't worth solving until
we see latency. Add a cache when load justifies it.

### Empty-state styling is soft, not blocking

Red border + small "empty" tag, NOT a red banner or modal. The
profile is "fill when you have time", not "BLOCKING ERROR". Tenant
should feel like the system surfaces the gap, not gates them on it.
Downloads still work with empty profile values — the placeholder
just renders literally.

### Convention footer per row

Each row shows `↳ replaces <<ISMS_MANAGER_NAME>>` in monospace. Two
reasons:
1. Transparency: the tenant understands what the field controls.
2. Debuggability: if a tenant sees `<<CEO_NAME>>` literal in a
   downloaded doc, they can grep the Profile UI for that exact
   string to find which field to fill.

### Grouping (People / Org / Business / Dates) over flat list

13 fields would be a wall of text. Grouping gives structure that
matches mental categories — and surfaces gaps in specific areas
("you have 5 People fields filled but 0 Date fields").

## Real-data observation (Arion)

After the SQL seed for Arion's 13 keys, the reference counts paint
the leverage picture:

- `isms_manager_name` → 7 templates (highest leverage)
- `dpo_name` → 4
- `approval_date` → 4
- `ceo_name` → 3
- `ciso_name`, `isms_owner_name`, `next_review_date` → 2 each
- Others → 1

This is auditable signal: filling `isms_manager_name` once flows
into 7 distinct compliance documents. The UI surfaces this
explicitly so the tenant sees the leverage.

## Roadmap

Built on:
- [[template-tenant-profile-2026-06-26]] — schema + renderer +
  PUT/GET. This entry is the UI layer on top.

Open follow-ups (not yet scoped):
- **"Preview in template" action per field** — show a snippet of
  a real template with the value substituted (gives tighter
  feedback loop than abstract "used in 7 templates").
- **Tenant journey integration** — surface "complete your
  profile" as an early step in the onboarding journey, so new
  tenants don't discover the profile only after first download.
- **Inferred defaults** — seed some keys from tenants table
  (e.g. `tenant_domain` from `tenants.slug + '.com'`).
- **Custom-key entry** — today the "Other" group renders
  tenant-added keys but there's no UI to ADD one. Add a "+ Add
  custom field" button.

## Related

- [[template-tenant-profile-2026-06-26]] — the backend this UI
  consumes.
- [[evidence-class-breakdown-backend-2026-06-26]] — the dashboard
  surface that drives downloads (which then use Profile values).
- [[template-native-formats-xlsx-2026-06-26]] +
  [[template-native-formats-docx-2026-06-26]] +
  [[template-native-formats-hybrid-2026-06-26]] — the download
  formats that all benefit from Profile substitution.
- [[templates-v2-anchors-complete-2026-06-25]] — the 20 anchor
  templates whose placeholders Profile fills.
