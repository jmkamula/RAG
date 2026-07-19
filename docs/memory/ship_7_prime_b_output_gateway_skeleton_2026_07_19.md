---
name: ship-7-prime-b-output-gateway-skeleton-2026-07-19
description: "Ship 7'.b — framework-aware output gateway skeleton + 2 pilot migrations (external API standard_display, notification action verbs)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 7'.b (2026-07-19) — the first concrete implementation of
the output-gateway design proposed in Ship 7'.a. Locks the shape
(vocabulary as data + composable transforms + surface hints +
warn-only guard) via 2 low-risk pilot migrations.

## What shipped

### 1. Per-framework vocabulary — `rag/output/vocab/*.json`

Three JSON files, one per enrolled standard:

- `iso27001_2022.json` — `display_name: "ISO 27001:2022"`, `short_name: "ISO 27001"`, Annex A + ISMS-clause ref conventions
- `iso27701_2019.json` — Annex A + Annex B (controller/processor) refs
- `gdpr_2016_679.json` — `display_name: "GDPR (EU 2016/679)"`, `short_name: "GDPR"`, article ref conventions

Loader in `rag/output/vocab/__init__.py`: reads every `*.json` at
first access, cached in a module-level dict. Adding SOC 2 / NIS2
= drop a file, no code edit.

Public API: `vocab.get(internal_id)`, `vocab.all_ids()`,
`vocab.display_name(id, fallback=None)`,
`vocab.short_name(id, fallback=None)`.

### 2. Composable transforms — `rag/output/transforms.py`

Five pure functions, each idempotent:

- `format_standard_id(text)` — replaces embedded slugs
  (`ISO27001:2022` → `ISO 27001:2022`) in prose
- `format_standard_id_exact(std_id, *, short=False)` — the
  single-slug case (e.g. serialising a Pydantic field)
- `humanize_snake_case(text)` — 2+-word snake identifiers
  become space-separated (single-word tokens left alone —
  indistinguishable from ordinary lowercase words)
- `scrub_leaf_ids(text)` — drops `req:X:Y:Z` + `item:X:Y` slugs
- `scrub_uuids(text, keep_suffix=8)` — bare UUIDs → `…c4b191b`

`TRANSFORMS` dict maps names → functions for the gateway to
compose. New transforms added there.

### 3. Gateway — `rag/output/gateway.py`

Two public entry points:

- `humanize(text, *, surface, transforms=None)` — apply the
  default chain for the surface (or an explicit subset).
  Unknown surface without explicit transforms raises
  `UnknownSurface` (fail loud — a typo in the surface name
  would silently ship jargon otherwise).
- `gateway_guard(text, *, surface=None)` — warn-only linter.
  Returns a list of `{kind, snippet, start, end, surface}`
  events for known jargon patterns (raw_standard_id, leaf_id,
  item_id, bare_uuid, snake_case_slug).

Six default surface chains registered:

    external_api_json     [format_standard_id]
    notification_title    [humanize_snake_case, format_standard_id]
    notification_body     [humanize_snake_case, format_standard_id, scrub_uuids]
    stage2_reason         [scrub_leaf_ids, humanize_snake_case, format_standard_id]
    error_detail          [scrub_uuids, humanize_snake_case, format_standard_id]
    cascade_rationale     [humanize_snake_case, format_standard_id]

Callers may bypass with `transforms=['scrub_uuids', ...]`
explicitly.

### 4. Pilot 1 — external API `standard_display`

`rag/external/endpoints/posture.py`:

- Added `standard_display: Optional[str]` field to
  `PostureControl` + `PostureControlDetail` (non-breaking
  additive change; `standard_id` still carries the canonical
  DB slug for machine keying).
- `_standard_display()` helper now imports
  `format_standard_id_exact` from the gateway — the local
  hardcoded dict is retired.
- Both `PostureControl` construction sites populate the new
  field.

### 5. Pilot 2 — notification action verbs

`rag/scheduler/tick.py`:

- Two producer sites (`followup_overdue`,
  `implication_overdue`) now build titles + bodies through
  `humanize(text, surface='notification_title'|'notification_body')`.
- Inline `.replace('_', ' ')` calls removed.
- Downstream benefit: any future notification producer using
  the same surface hint gets consistent humanisation for free.

### 6. Tests — `tests/test_output_gateway.py`

45 assertions across 10 test functions covering:

- Vocab loader (3 frameworks + fallback + unknown pass-through)
- Each transform (positive cases + idempotence)
- Surface routing (all 3 pilot surfaces + custom subset + fail-loud on unknown)
- `gateway_guard` (detection + post-humanize clean round-trip)
- Both pilot integrations end-to-end

All 45 PASS.

## Design invariants proven by the pilots

1. **Adding a framework is a file, not a code change.** Dropping
   `soc2_2017.json` would extend `vocab.all_ids()` + all
   `format_standard_id*` transforms would recognise the new slug
   automatically. Same holds for NIS2 / DORA / HIPAA.

2. **Per-surface behaviour without switch statements.** The
   gateway's `_SURFACE_DEFAULTS` dict is a lookup, not a
   dispatch chain. New surfaces (e.g. `email_subject`,
   `pdf_export_prose`) register by adding a key.

3. **Idempotent transforms compose safely.** Every transform
   is idempotent, so double-applying (e.g. by two callers in
   the same request path) doesn't corrupt output.

4. **Opt-in, never middleware.** Sites call the gateway
   explicitly. No FastAPI/psycopg2 middleware that scrubs
   everything — admin endpoints, audit provenance, external API
   `standard_id` structured field all remain untouched.

## Non-breaking-change discipline

Pilot 1 chose ADD-a-field over CHANGE-the-value for the external
API surface — SDK consumers keying on `standard_id: "ISO27001:2022"`
continue to work. Tenant UI can migrate to reading
`standard_display` incrementally. The old field stays.

Same principle will apply to Ship 7'.c's migrations of the
remaining MIXED sites.

## Baseline

Full eval running. Gateway is passive (only called at sites
that opted in via pilot migrations); other paths unchanged.

## Ship 7' progress

| Sub-arc | Status |
|---|---|
| 7'.a Output audit + gateway proposal | ✓ |
| **7'.b Gateway skeleton + 2 pilots** | **✓** |
| 7'.c Migrate remaining MIXED sites | next |
| 7'.d polish() prototype (conditional) | pending |
| 7'.e (conditional) second polish() surface | pending |
| 7'.f Arc retrospective | pending |

## Related

- [[ship-7-prime-a-output-audit-2026-07-19]] — parent audit
  memo that proposed this architecture
- [[dejargonize-ux-pass-2026-07-01]] — the tenant-facing
  vocabulary conventions this gateway extends and consolidates
