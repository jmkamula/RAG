---
name: cite-mode-v1-frontend-2026-06-27
description: "SHIPPED 2026-06-27: cite-mode v1 frontend. Profile page gains External Evidence Systems registry (register/edit/delete inline). Evidence-class panel gains Cited lane on cite-acceptable leaves only (per-system groups with fresh/stale/unverified badges + Verify/Edit/+ Cite buttons). Three modals: Create cite (system pick → per-MUST checkbox form), Edit cite (jumps to MUST form), Verify cite (mandatory changes_detected textarea). Backend extension: evidence-class endpoint eagerly returns cite_acceptable + cites per leaf (single round-trip). Partial unique indexes fixed soft-delete-collision bug surfaced during smoke."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

### Frontend (`static/arioncomply.html`)

**Profile page** — new "External Evidence Systems" section below
the placeholder fields:

- Inline `Register system` form: system_name (required) + URL +
  default_cadence_days + multi-select for covers_evidence_types
  (grouped Registers / Records / Other so the tenant doesn't have
  to know our taxonomy)
- Per-row Edit (in-place form swap) and Delete (confirm dialog;
  soft-deletes the system AND its dependent cites)
- "No systems registered yet" empty state with educational copy

**Evidence-class panel** — new Cited lane per leaf (only on
`leaf.cite_acceptable`):

- Per-cite-group row: `↗ <system_name> · N MUSTs · verified
  YYYY-MM-DD · <badge>`
- Badge states:
  - **unverified** (grey) — cite exists but no verification yet
  - **✓ fresh** (green) — within (cadence + grace)
  - **stale — verify now** (red) — past grace
- Buttons per group: Verify, Edit
- "+ Cite external source" button on each cite-acceptable leaf

**Three modals**:

- `openCiteCreate(leafId, evidenceType)` — step 1: pick system
  from a dropdown filtered to those whose covers_evidence_types
  includes this evidence_type (empty list = applies to any). If no
  applicable system, prompts "register one in Profile?"
- `_citeAdvanceToMustForm(leafId, systemId)` — step 2: per-MUST
  checkbox form. Re-fetches current cite state to pre-check
  existing covered MUSTs (so Edit flow shows the current
  selection). Cadence override input defaults from the cite
  state or system default.
- `openCiteEdit(leafId, systemId, systemName)` — skips step 1
  (system already chosen); jumps straight to the MUST form
- `openCiteVerify(leafId, systemId, systemName)` — required
  `changes_detected` textarea with realistic placeholder text
  ("5 new employees onboarded; all completed training..."). Will
  block submit if empty.

All modals use a shared `_renderCiteModal(title, body, footer)`
helper — overlay-click-to-close, escape-on-X button. After any
write, the dashboard panel is refreshed via `selectHeatCell` so
the cite group surface updates immediately.

### Backend extension (`rag/posture/advisory.py`)

- New `_fetch_cites_per_leaf(pg_conn, tenant_id, leaf_ids)` —
  eager-loads all cite groups for the panel's leaves in one
  query (joined to `tenant_external_system` for the human-grade
  system name). Per-MUST freshness flag computed via
  `cite_mode.is_cite_fresh()`.
- `build_evidence_class_breakdown` now returns `cite_acceptable`
  (bool) + `cites` (list of per-system groups) per leaf in the
  same response. Single round-trip; the frontend doesn't have to
  handle async per-leaf loading.

### Schema fix (mid-smoke)

Unique constraint `(tenant_id, system_name)` was non-partial,
which fired even on rows where `is_active = FALSE`. Tenants who
deleted a system then tried to re-register the same name hit a
500. Fix: dropped both unique constraints (`tenant_external_system_unique_name`
and `external_evidence_source_unique`) + created partial unique
indexes filtered on `WHERE is_active = TRUE`. New rows after a
soft-delete get fresh ids; old rows preserved for audit.

Schema v50 file updated to encode the partial-unique pattern.

## Non-obvious decisions

### Cite groups eager-loaded, not lazy

A leaf might have 0 or 5 cite groups. Lazy-loading per-leaf
would cascade async UI re-renders; eager-loading puts everything
in the single `/evidence-classes` response that already drives
the panel. Cost: one extra small SQL query per panel open;
saves N round-trips and avoids async UI flicker.

### Per-MUST checkbox form re-fetches current cite state

On Edit, the form needs to know which MUSTs are currently
covered (to pre-check). On Create with a system already cited
on the same leaf, same need (so the form acts as an
add-to-existing rather than wipe-and-replace). Single endpoint
`GET /api/v1/tenant/cites/leaf/{leaf_id}` returns grouped state;
form filters to the chosen system_id.

### Modal close on overlay-click

UX convention. Avoids users feeling "trapped" in a modal.
Submit buttons require explicit click (don't auto-close on
overlay) to prevent accidental dismissal mid-typing.

### `_citeAdvanceToMustForm` accepts optional pre-filled system

The `_` prefix marks it as an internal helper called by both
`openCiteCreate` (after system pick) and `openCiteEdit` (no
pick needed). Avoids duplicating the per-MUST form rendering.

### Smart filter on "no applicable system"

If tenant clicks "+ Cite external source" but they haven't
registered any system that covers this evidence_type, we ask
"register one in Profile?" with a confirm dialog that routes to
the Profile page via `setMode('profile')`. Removes the dead-end
state — tenant always has a path forward.

### Verify modal forces real review

The `changes_detected` textarea is the audit-grade payload. UI
placeholder text shows a realistic example
("5 new employees onboarded since last verification; all
completed mandatory training via onboarding workflow. 1
contractor offboarded; access revoked per A.5.18 leaver flow.")
to demonstrate the expected detail level — not "verified ✓".
JS validation blocks empty submission. Backend also enforces.

## End-to-end verified

Smoke sequence through the API surface the frontend hits:

1. Register Odoo HR (90-day cadence, covers [register, review_record])
2. Cite 3 A.6.1 register MUSTs (reg_checks_performed,
   reg_outcome, reg_decision_date)
3. Verify with realistic `changes_detected` text
4. A.6.1 register leaf flips 0/6 → 3/6; overall 17% → 30%
5. evidence-class endpoint returns the cite group inline with
   `is_fresh: true` per MUST

The frontend code reads this same response and renders the
"↗ Odoo HR · 3 MUSTs · verified 2026-06-27 · ✓ fresh" row.

## Hardening worth adding (deferred to v2)

- **Catalog validation on cite PUT** (already flagged in
  [[cite-mode-v1-backend-2026-06-27]]) — backend doesn't yet
  reject invalid must_ids. The frontend can't submit invalid ids
  because the form only checkboxes catalog must_items, but the
  API still accepts anything matching the format regex.
- **Verification log viewer** in UI — backend
  `/log` endpoint exists but no UI surface yet. Audit/compliance
  officer wanting to see "show me the last 4 verifications of
  this cite" must use the API directly.
- **Dashboard freshness card** — `/api/v1/dashboard/cites/needs-verification`
  endpoint not yet built; would surface cites past/near due in a
  summary card on the dashboard for at-a-glance visibility.
- **Onboarding question** — journey wizard would ask "which
  systems do you use?" at first sign-in to pre-seed
  `tenant_external_system` rows. Skipped for v1.
- **Stale-cite filter in JS** — `isCiteAcceptable()` predicate
  mirror in JS so the +Cite button could be conditionally
  rendered without the backend's `cite_acceptable` flag. Today
  the backend tells the frontend per leaf — works but couples
  the surfaces. v2 can mirror the predicate for resilience.

## Files touched

- `static/arioncomply.html` — Profile page extension +
  evidence-class panel cited lane + three modal helpers +
  shared modal infrastructure (~270 lines added)
- `rag/posture/advisory.py` — `_fetch_cites_per_leaf` helper +
  `build_evidence_class_breakdown` returns cite_acceptable +
  cites per leaf
- `db/schema_v50_external_evidence.sql` — partial unique indexes
  replace blocking constraints

## Related

- [[cite-mode-v1-backend-2026-06-27]] — sibling backend memo;
  this entry is the UI layer on top
- [[product-principle-evidence-stored-vs-cited]] — the design
  this implements
- [[product-concept-evidence-cascade-2026-06-27]] — strategic
  successor; needs the verification UI as substrate
- [[evidence-class-breakdown-backend-2026-06-26]] — sibling UI
  surface; this entry extends it with the cited lane
- [[template-tenant-profile-2026-06-26]] +
  [[template-tenant-profile-ui-2026-06-26]] — Profile page
  shares structural code with the external-systems registry
