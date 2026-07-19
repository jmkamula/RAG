---
name: ship-7-prime-arc-retrospective-2026-07-19
description: "Ship 7' arc retrospective — 4 sub-arcs delivered + 1 skipped; framework-aware output gateway consolidates every tenant-facing string transform"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 7' arc — the framework-aware output gateway. Entry-point
for future work on anything under `rag/output/`, adding
frameworks (SOC 2 / NIS2 / DORA), or migrating a new output
surface to consolidated humanization.

**Arc window:** 2026-07-19. 4 sub-arcs + 1 skipped + closer, all
in one day. Shortest arc since Ship 5'.

## Motivation

User's ask after Ship 6' closed:

> "Tenants experience our outputs. They need to be full,
> factual, and helpful. Let us look at every place we produce
> tenant-facing text, remove the code jargon, and consolidate.
> Now that we're using the case-file pattern, we can probably
> consolidate our output gateway and use LLM strength for the
> human touch."

Ship 6' had confirmed the chat pipeline was clean. Ship 7'
turned the same lens on every other output surface.

## Sub-arc inventory

| Sub-arc | Kind | Key win |
|---|---|---|
| 7'.a | Audit memo | Cataloged every tenant-facing output: 8 CLEAN + 8 MIXED. Proposed **framework-aware** gateway (not monolithic) — per-framework JSON vocabulary + composable transforms + surface hints. Locked 4 design decisions with the user before touching code. |
| 7'.b | Code + tests | Built the skeleton: 3 vocab JSONs (ISO 27001 / ISO 27701 / GDPR), 5 idempotent transforms, `humanize()` + `gateway_guard()`, 6 surface chains. Pilot 1: external API PostureControl `standard_display` non-breaking additive field. Pilot 2: notification producers in tick.py. |
| 7'.c | Migrations | Migrated remaining 4 MIXED site groups: cascade endpoint (4 `*_display` fields + rationale scrub), posture endpoint (gap_description + engine reason composed with `_humanize_reason`), api_server error UUIDs (2 offenders), Evidence Package prose (new `evidence_prose` surface). |
| 7'.d | Evaluation + fix | Sampled real outputs from all 4 surfaces. Evidence Package + posture + notification bodies read naturally after the deterministic pass. Found a NEW jargon pattern the 7'.a audit missed — markdown-escape artifacts (`\-`, `\(`, `\.`) from mammoth-processed DOCX. Added `strip_markdown_escapes` transform. **Decided polish() unnecessary**; validated against real API responses. |
| **7'.e** | **Skipped** | Conditional second polish() surface — 7'.d evaluation showed the deterministic layer met the natural-language bar. Ship 7'.a's decision tree explicitly branched here. |
| **7'.f** | **Retrospective** | This document. |

**Delivered:** 3 schema-less JSON vocab files + 3 Python modules
(`gateway.py`, `transforms.py`, `vocab/__init__.py`) + 6 pure
idempotent transforms + 6 surface chains + 57 test assertions +
5 memos, all in 4 git commits.

## Architectural properties that emerged

1. **Vocabulary as data, not code.** Adding a framework is a JSON
   file drop. When SOC 2 / NIS2 / DORA / HIPAA land, no gateway
   code change is required. This was the single most important
   design constraint from the "how do we not constrict xframework
   growth?" conversation with the user.

2. **Composable transforms, not one function.** `humanize()` is a
   chain-runner over `TRANSFORMS[name]` lookups. Each transform
   is a pure ~20-line function that unit-tests in isolation. Adding
   a new one is: write the function, add it to `TRANSFORMS`, register
   it in the relevant surface chains.

3. **Surface hints as the escape valve.** Different surfaces get
   different chains without a switch statement. `notification_title`
   skips `scrub_uuids` (short strings, ellipsis reads worse than
   truncation); `external_api_json` skips `humanize_snake_case`
   (structured fields intentionally carry raw slugs); `evidence_prose`
   is the full pass. New surfaces register by adding a key.

4. **Opt-in, never middleware.** Sites call the gateway explicitly.
   No FastAPI/psycopg2 middleware that scrubs everything —
   admin endpoints, audit provenance columns, external API's
   structured raw ref fields all remain untouched. This preserves
   dual use (auditor sees raw slugs when they need them, tenants
   see clean output).

5. **Non-breaking additive migration.** Every 7'.c wire-format
   change adds a `*_display` companion instead of changing the
   existing field. SDK consumers keying on `standard_id: "ISO27001:2022"`
   or `expected_event_type: "policy_revised"` still work; UI
   migrates to reading display fields incrementally.

6. **Idempotent transforms compose safely.** Every transform is
   idempotent, so double-application (e.g. two callers in the
   same request path) doesn't corrupt output. This lets us
   compose `_humanize_reason` (semantic) with the gateway (slug
   scrub) without worrying about ordering.

7. **The evaluation checkpoint was load-bearing.** The 7'.a
   decision tree said: build deterministic first, prototype
   polish() only if deterministic proves insufficient. 7'.d ran
   the experiment on real data. Deterministic won. We saved
   building unnecessary LLM latency + cost + failure paths + a
   `output_polish_log` schema for a class of surfaces that
   didn't need it.

## The one gap the audit missed

Ship 7'.a's audit identified 8 MIXED sites. What it missed:
**backslash-escaped markdown punctuation** (`\-`, `\(`, `\.`,
`\+`, etc.) in extractor-produced `gap_description` prose.

The 7'.a audit sampled response_preview (500 chars) which
apparently didn't catch this. 7'.d's evaluation on real API
responses did.

Lesson: audit + evaluation both matter. An audit alone can miss
patterns that only show up in real data volume. Ship 6'.c's
retrospective (data-driven look at chat_casefile_log) taught
this lesson once already; Ship 7 relearnt it.

## What we didn't build (and why)

- **polish() LLM humanization** — 7'.d evaluation showed the
  deterministic gateway is sufficient for the surfaces we care
  about. If a specific surface (e.g. auditor-facing PDF export
  in a future arc) proves stilted, revisit then. The
  `output_polish_log` schema stays in the design memo, not in
  the codebase.

- **Fail-CI gateway_guard** — 7'.a locked "warn-only" to match
  the eval baseline pattern. Tightening opportunistically.

- **Per-tenant display customization** — the 7'.a option to
  store vocabulary per-tenant in Postgres was rejected: no
  customer has asked for it, and JSON files are simpler.

- **Legacy gap_description backfill migration** — read-time
  scrubbing via the gateway makes backfill unnecessary. The DB
  stays canonical; the wire is clean. If we ever need to
  materialize humanized versions, `strip_markdown_escapes`
  + friends are pure functions we can pipeline through a
  one-shot SQL migration script.

## What this changes about future work

- **Adding a new framework** is now:
  1. Drop `<framework>_<year>.json` in `rag/output/vocab/`.
  2. Confirm curator content follows CLAUDE.md tenant-language
     conventions.
  3. Any endpoint that already routes through `humanize()`
     serialises the new framework's slugs cleanly for free.

- **Adding a new output surface** is:
  1. Pick / register a surface in `_SURFACE_DEFAULTS` if the
     existing ones don't fit.
  2. Wrap the serialization boundary in
     `humanize(text, surface='...')`.
  3. Add a unit test asserting `gateway_guard(result, ...) == []`.
  4. Ship.

- **Adding a new jargon pattern** (like the markdown-escape
  discovery in 7'.d):
  1. Write a small pure transform in `rag/output/transforms.py`.
  2. Add to `TRANSFORMS` + re-export.
  3. Register in relevant surface chains.
  4. Unit test.
  Total: ~30 lines of code + a test.

## Test suite impact

| Sub-arc | Assertions added |
|---|---|
| 7'.b | 45 (initial coverage of vocab, 5 transforms, surface routing, gateway_guard, 2 pilots) |
| 7'.c | +6 (evidence_prose surface, cascade migration, error UUID migration) |
| 7'.d | +6 (strip_markdown_escapes: positive + preserved whitespace + idempotence + 2 gateway integration) |
| **Total** | **57 assertions** in `tests/test_output_gateway.py` |

Eval baseline held at 207/208 PASS + 1 WARN + 0 FAIL across
every sub-arc.

## Deferred / follow-up

- **Chat prose migration** — currently the chat pipeline uses
  its own humanization (system prompt discipline, case-file
  digest). Overlaps with gateway concerns. Not urgent since
  chat is CLEAN, but eventual consolidation would kill the
  last "two vocabularies" ambiguity.

- **CI grep guards** — from Ship 5'.f and Ship 6'.f. Still
  deferred. Could tighten in a Ship 8 hygiene pass.

- **Full external API SDK response coverage** — Python SDK
  models don't yet expose the new `*_display` fields as typed
  attributes. Non-breaking (JSON `.dict()` still works), but
  typed access would be nicer.

- **UI drill-in from Ship 6'.e decision-trail** — carried over
  from Ship 6'; still valuable.

- **Model-tier divergence investigation** (Ship 6'.f
  follow-up) — still open.

## Lessons carried forward

- **Anchor with the user before locking design.** Ship 7'.a's
  AskUserQuestion round on consolidation-helps-vs-hurts +
  framework-aware architecture surfaced the "don't constrict
  xframework growth" constraint BEFORE any code was written.
  That single conversation shaped the whole arc.
- **Empirical evaluation catches what audits miss.** The
  markdown-escape leak in extractor output only appeared when
  we sampled real API responses. Building the evaluation
  checkpoint into the arc (7'.a → 7'.d) forced this discipline.
- **Skipping a planned sub-arc is a win.** Ship 7'.e was
  designed to be optional; making it explicitly conditional
  in the 7'.a plan meant the "skip" was a first-class outcome,
  not a shortcut.
- **Non-breaking-additive works.** Every 7'.c wire-format
  change is `*_display` additions — SDK consumers key on the
  raw slug and stay unaffected. Same principle should apply to
  future output-model evolution.

## Ship 7' close

| Sub-arc | Status |
|---|---|
| 7'.a Output audit + gateway proposal | ✓ |
| 7'.b Gateway skeleton + 2 pilots | ✓ |
| 7'.c Migrate remaining MIXED sites | ✓ |
| 7'.d Evaluation checkpoint + markdown-escape fix | ✓ |
| 7'.e (conditional) second polish() surface | SKIPPED |
| **7'.f Arc retrospective** | **✓ (this doc)** |

## Related

- [[ship-6-prime-arc-retrospective-2026-07-19]] — previous arc
- [[ship-7-prime-a-output-audit-2026-07-19]] — the audit that
  opened this arc + captured the design decisions
- [[dejargonize-ux-pass-2026-07-01]] — the tenant-language
  conventions this arc extends and consolidates
- [[ship-7-prime-b-output-gateway-skeleton-2026-07-19]] — 7'.b
- [[ship-7-prime-c-mixed-site-migration-2026-07-19]] — 7'.c
- [[ship-7-prime-d-evaluation-checkpoint-2026-07-19]] — 7'.d
