---
name: ship-7-prime-c-mixed-site-migration-2026-07-19
description: "Ship 7'.c — migrate remaining MIXED sites through the output gateway (cascade / posture / errors / Evidence Package)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 7'.c (2026-07-19) — mechanical application of the Ship 7'.b
gateway to the remaining MIXED sites identified in the 7'.a
audit. Four migration bundles; each site under its own
`surface=` context.

## Sites migrated

### 1. Cascade endpoint (`rag/external/endpoints/cascade.py`)

Non-breaking additive: raw slug fields (`event_type`,
`expected_action`, `expected_event_type`, `standard_id`) stay
verbatim for machine keying; new `*_display` companion fields
carry human forms via `humanize(surface='cascade_rationale')`.

Both response models updated:
- `CascadeEvent` gets `event_type_display`,
  `expected_action_display`, `expected_event_type_display`,
  `standard_display`
- `ImplicationDetail` gets `source_event_type_display`,
  `expected_action_display`, `target_standard_display`

Additionally, the `rationale` field itself is now scrubbed via
the gateway before serialization (surface `cascade_rationale`).

### 2. Posture endpoint (`rag/external/endpoints/posture.py`)

`gap_summary` (bulk) and `gap_description` + `action_required`
(detail) now route through `humanize(surface='stage2_reason')`.
Legacy pre-dejargonize slug residue in DB rows is cleaned at
serialization time — the DB stays canonical.

Engine reason composition: semantic pass first
(`_humanize_reason` translates "0/4 children" → "0 of 4
evidence sources satisfied"), then gateway pass for slug
scrubbing. Both passes are idempotent, so double-application
is safe.

### 3. Error UUIDs (`api_server.py`)

Two specific offenders from the 7'.a audit fixed:
- `Upload not found: {upload_id}` → soft phrasing + UUID
  scrubbed to `…c4b191b` suffix
- `Series not found: {series_id}` → same treatment

Both route through `humanize(surface='error_detail')`, so any
future slug creep in error strings gets caught by the same
chain.

Deliberately narrow: only the audit-identified offenders
touched. Global HTTPException wrapper would be invasive; the
gateway is opt-in.

### 4. Evidence Package obligation prose (`rag/posture/evidence_package.py`)

`business_description` + leaf `.description` (both curator-
authored fields from Neo4j) now route through
`humanize(surface='evidence_prose')` before rendering into
markdown. Guards against author-embedded leaf ids / snake_case
slugs / raw standard-id references that would otherwise reach
auditors.

The gateway's `evidence_prose` surface (added this arc) chains:

    scrub_leaf_ids → humanize_snake_case → format_standard_id

## New surface registered

`evidence_prose` — auditor-facing prose in the Evidence
Package. Scrub leaf-id leakage, humanise snake_case, format
standard-id slugs. Registered in `rag/output/gateway.py::_SURFACE_DEFAULTS`.

## Non-breaking-change discipline (continued)

Every migration in 7'.c preserves the raw slug value on the
wire and adds a `*_display` companion (or scrubs at
serialisation while keeping the field name). No SDK / SIEM
consumer parsing existing fields breaks. Tenant UI can migrate
to reading display fields incrementally.

## Tests

`tests/test_output_gateway.py` extended:
- `test_evidence_prose_surface` — new surface chain
- `test_cascade_migration` — event_type + expected_action
  humanised; rationale scrubbed
- `test_error_uuid_migration` — UUID in error detail → suffix

All 51 assertions PASS (was 45 pre-7'.c).

## Baseline

Full eval running. Passes through the gateway are additive:
migrations don't remove any information from responses, just
add display companions or clean prose fields.

## Ship 7' progress

| Sub-arc | Status |
|---|---|
| 7'.a Output audit + gateway proposal | ✓ |
| 7'.b Gateway skeleton + 2 pilots | ✓ |
| **7'.c Migrate remaining MIXED sites** | **✓** |
| 7'.d polish() prototype (conditional) | evaluation checkpoint |
| 7'.e (conditional) second polish() surface | pending |
| 7'.f Arc retrospective | pending |

## Ship 7'.d evaluation checkpoint

Now that all 8 MIXED sites are behind the deterministic
gateway, the 7'.a decision was: pause and evaluate whether
outputs look stilted before building `polish()`. Recommended
sample surfaces to inspect:

- One cascade endpoint response (has 4 humanised slug fields
  + scrubbed rationale)
- One posture detail response (has scrubbed gap_description +
  semantic-then-slug engine reason)
- One Evidence Package rendering (auditor-facing prose)
- A representative notification body (from Ship 7'.b pilot)

If they read as natural + factual + complete without LLM
touch: skip `polish()` entirely, go directly to Ship 7'.f
retrospective. If any surface reads as stilted machine output:
Ship 7'.d prototypes `polish()` there.

## Related

- [[ship-7-prime-a-output-audit-2026-07-19]] — parent audit
- [[ship-7-prime-b-output-gateway-skeleton-2026-07-19]] — the
  gateway this arc consumed
