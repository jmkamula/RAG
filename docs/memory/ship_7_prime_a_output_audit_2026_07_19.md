---
name: ship-7-prime-a-output-audit-2026-07-19
description: "Ship 7'.a — audit of every tenant-facing output; humanization principles; gateway architecture sketch"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 7'.a (2026-07-19) — the audit that opens Ship 7. Same shape
as Ship 5'.a and Ship 6'.a: no code changes, produces a
prioritized punch list + a design proposal for the sub-arcs that
follow.

## Motivation

Ship 6 confirmed **no LLM site is compliance-load-bearing
without a deterministic gate**. Chat prose is factual and
human — the case-file digest architecture + preservation-check +
dejargonize UX pass work together to produce natural language
that's audit-safe.

But **chat is only one output surface**. Ship 7 asks whether the
rest of the platform's outputs meet the same bar:

> "Tenants experience our outputs, they need to be full,
> factual and helpful. Let us also discuss how to make our
> outputs sound human and complete, we need to remove all code
> jargon. Now that we are using the case-file pattern, we can
> probably consolidate our output gateway and use LLM strength
> to put human touch to outputs."

## The output landscape — status by class

### CLEAN — production-quality, no changes needed

1. **Chat pipeline** (`rag/llm_answer.py`) — case-file digest +
   preservation repair + Ship 6'.d claim scan. System prompt
   forbids unexpanded acronyms; posture terminology (NC/OFI/
   Comply) defined inline on first use.
2. **Advisory panel** (`rag/posture/advisory.py`) — the
   dejargonize UX pass's canonical implementation. Humanized
   evidence types + leaf labels + standard IDs. No `req:` or
   `item:` slugs leak.
3. **Evidence Package** (`rag/posture/evidence_package.py`) —
   explicitly designed to strip system jargon. Reuses curated
   `business_description` + `EvidenceRequirement.description`
   from Neo4j (scales to arbitrary standards without re-
   authoring per-node display text).
4. **Stage-1 review chat** (`rag/posture/stage1_review_chat.py`)
   — plain verbs (approve/reject/confirm), no schema leakage.
5. **Dashboard KPI blurbs + gap summary**
   (`rag/posture/gap_writer.py`) — deterministic English
   composition, no slugs.
6. **Templates block / starter kit** (`rag/templates/answer_footer.py`)
   — leaf slugs live in URLs only; display uses humanized
   titles.
7. **Loading + empty states** (`static/arioncomply.html`) —
   plain English strings.
8. **Python SDK error hierarchy** + **External API error
   contract** — semantic codes + user-friendly messages.

### MIXED — jargon leaks partial, worth targeted fixes

1. **Stage-2 engine proposals** — `posture_loader.py::_compose_posture`
   emits `engine_reason` fields that concatenate leaf summaries
   with legacy `gap_description` prose. No structural
   humanization applied before the string lands in the queue UI
   + cascade rationale + notification bodies.
2. **Cascade event slugs** — `rag/external/endpoints/cascade.py`
   emits raw DB slugs (`policy_revised`, `access_review_required`,
   `nc_finding`) in `expected_action` / `expected_event_type`.
   External SDK consumers + SIEM/SOAR integrations see the
   internal vocabulary.
3. **Standard ID format on the wire** — External API returns
   `standard_id: "ISO27001:2022"` (internal slug). Tenants
   expect `"ISO 27001:2022"`. Client-side JS has
   `humanizeStandardId()` but the external API doesn't apply it
   at serialization.
4. **Notification implication titles** — `rag/scheduler/tick.py`
   composes titles like `"Overdue: A.5.15 requires access_review_required"`.
   Control ref humanized, action slug isn't.
5. **Posture `gap_description` scrubbing** — user-authored OR
   engine-authored prose flows through unchanged. Legacy rows
   still contain slug patterns from pre-dejargonize extraction.
   Flows downstream into advisory + chat context + external API.
6. **Cascade rationale field** — truncated to 400 chars, no
   humanization pass. Fed to SOAR playbooks as-is.
7. **Error detail UUIDs** — `HTTPException(404, "Upload not
   found: {upload_id}")` — bare UUID in tenant-facing error.
   Most other error paths use natural language; a few slipped.
8. **Evidence Package obligation text** — verbatim from Neo4j;
   may contain nested control refs or raw IDs curators embedded
   during authoring.

### INTERNAL — not tenant-visible but shape downstream outputs

- Enricher `topic_tokens` — LLM keywords used for classification
- Posture-loader raw dicts — internal bridge, humanized on the
  way out via advisory helpers
- Extractor `document_findings.excerpt` — used for audit trail
  provenance, seen in Stage-1 UI

## The problem, framed

Two humanization patterns coexist inconsistently:

**Pattern A: LLM as humanizer** — chat pipeline. LLM composes
prose over a compact, verbatim digest. Deterministic gates
(preservation-check, claim scan) verify factuality. Works
brilliantly for chat.

**Pattern B: Deterministic helpers** — dashboard/advisory/
Evidence Package. Python code applies slug→Title-Case
transforms via per-module `_humanize_*` functions. Scales but
each new site risks forgetting to call the helper.

Where Pattern B has been applied thoroughly (advisory, Evidence
Package, dashboard), outputs are clean. Where it hasn't been
applied (engine_reason, cascade slugs, external API
serialization, notification action verbs), jargon leaks.

## The consolidation tension

A monolithic gateway would consolidate all humanization but risk
constricting multi-framework growth:

**Consolidation helps** — 8 MIXED sites share the same jargon
patterns; different code paths reinventing scrubbers guarantees
drift. Framework enrolment becomes cheaper (SOC 2 lands as one
config file, not 15 code edits). Test surface shrinks to one
module.

**Consolidation hurts if done wrong** — per-framework display
conventions differ (GDPR `Art.32.1(a)`, ISO `A.5.15`, SOC 2
`CC1.1`, NIS2 numbered directives). A monolithic `humanize()`
with a switch statement grows on every enrolment. Per-surface
context differs (notification title budget vs. Evidence Package
prose). Over-cleaning breaks legitimate admin/audit-provenance
surfaces. English hardcoding blocks i18n. Coupling `polish()`
LLM latency to every serialisation is unacceptable.

## Ship 7 proposal — framework-aware output gateway

Not one function — a small composable framework under
`rag/output/` with three responsibilities:

### 1. Vocabulary as data — `rag/output/vocab/*.json`

One JSON per enrolled standard defining display conventions.
Read once at module init, cached. Adding a framework = adding
a file.

```
iso27001_2022.json:
  { "display_name":    "ISO 27001:2022",
    "annex_prefix":    "A.",                # A.5.15
    "isms_ref_bare":   true,                # 6.1.2 not "clause 6.1.2"
    "ref_display_fmt": "{display_name} {ref}" }

gdpr_2016_679.json:
  { "display_name":    "GDPR",
    "article_prefix":  "Art.",              # Art.32
    "subarticle_fmt":  "{art}.{sub}({letter})",  # Art.32.1(a)
    "ref_display_fmt": "{display_name} {ref}" }
```

Matches how `enrichment/documents/document_requirements.py`
handles per-framework catalog data. Future SOC 2 / NIS2 lands
as a config file, not a code edit.

### 2. Composable transforms — `rag/output/transforms.py`

Not one `humanize()` function but a chain of small pure
functions:

- `scrub_uuids(text, hint)` — bare UUIDs at word boundaries
- `scrub_leaf_ids(text)` — drop `req:X:Y` / `item:X:Y` slugs
- `format_standard_id(text)` — apply vocabulary
  `display_name` per framework
- `humanize_action_verbs(text)` — snake_case event/action
  slugs (`policy_revised` → `policy revised`)
- `humanize_evidence_types(text)` — snake_case type slugs

Each is unit-tested in isolation. Sites can subset:
`humanize(text, transforms=['leaf_ids', 'standard_ids'])`.

### 3. Surface context — the escape valve

`humanize(text, surface='notification_title' | 'evidence_prose' |
'external_api_json' | 'stage2_reason' | ...)`.

Surface hints tune behavior per output site. Word budgets, ref
formats, framework-name conventions differ. This escape valve
is what stops the gateway from becoming a monolith — same input
can render differently per surface without a switch statement
in the gateway itself.

### 4. `gateway_guard(text, surface) -> list[JargonEvent]`

Scans a string for known jargon patterns; reports offending
substrings + line offsets. Used in unit tests for producer
functions. **Warn-only in CI** — matches the eval baseline
pattern (tighten opportunistically, don't fail-CI on regressions).

### 5. Opt-in, never middleware

Sites call the gateway explicitly. No hidden FastAPI/psycopg2
middleware that scrubs everything — that would break admin
endpoints, audit provenance columns, external API structured
raw ref fields, and future debug/support tooling.

### 6. `polish(text, context)` — bounded LLM humanization

Deferred until Ship 7'.d, and only if deterministic gateway
output reads as stilted machine text on the MIXED sites. When
introduced, reuses the case-file preservation-check pattern
(digest → LLM polish → verify all refs + verdicts + numbers
survived, deterministically append any dropped element). Passive
per-surface opt-in. `output_polish_log` schema alongside.

Never mandatory. Never middleware.

## Decisions locked in

Discussed with user 2026-07-19:

1. **Vocabulary storage:** per-framework JSON in
   `rag/output/vocab/`. Adding SOC 2 / NIS2 later = one file.
2. **Ship 7'.b scope:** skeleton (vocab loader + composable
   transforms + surface hints + `gateway_guard`) **plus 2 pilot
   migrations** — external API `standard_id` serialisation +
   notification action verbs. Prove the shape works; Ship 7'.c
   handles the rest.
3. **`polish()` timing:** deferred to Ship 7'.d, ONE surface
   only, and only if deterministic layer proves insufficient.
   If MIXED sites look human after JUST the deterministic
   pass, skip polish() entirely and go straight to close.
4. **CI strictness:** `gateway_guard` warns only — no fail-CI
   on new hardcoded slug patterns. Tighten opportunistically.

## Sub-arc sketch for Ship 7'.b–7'.f

**7'.b** — Build framework-aware gateway skeleton
(`rag/output/vocab/*.json` + `rag/output/transforms.py` +
`rag/output/gateway.py` + `gateway_guard`). Pilot migrations:
external API standard_id serialisation + notification action
verbs. Ship unit tests for each transform + one integration
test per pilot site.

**7'.c** — Incremental migration of remaining MIXED sites:
Stage-2 engine_reason + cascade slugs + posture gap_description
scrubbing + cascade rationale + error UUIDs + Evidence Package
obligation text scrubbing. Each site under its own `surface=`
context. One PR per migration ideally.

**7'.d** — **Evaluation checkpoint**: are outputs stilted after
JUST the deterministic pass? If yes: prototype `polish()` on
ONE surface (default target: notifications — short strings,
high tenant impact, low blast radius). Ship `output_polish_log`
schema. If no: skip to 7'.f.

**7'.e** — (conditional) extend `polish()` to a second surface
based on 7'.d learnings.

**7'.f** — Arc retrospective + retire per-module
`_humanize_*` helpers in favour of the gateway.

## Baseline

No code, no schema, no eval impact. Sets up Ship 7'.b+.

## Ship 7' progress

| Sub-arc | Status |
|---|---|
| **7'.a Output audit + gateway proposal** | **✓ (this doc)** |
| 7'.b Gateway module + deterministic humanize migration | pending |
| 7'.c MIXED-site substitutions | pending |
| 7'.d polish() prototype (notifications) | pending |
| 7'.e polish() for Evidence Package | pending |
| 7'.f Arc retrospective | pending |

## Related

- [[ship-6-prime-arc-retrospective-2026-07-19]] — previous arc
- [[dejargonize-ux-pass-2026-07-01]] — the tenant-facing UX
  conventions this arc extends across ALL surfaces
- [[ship-2-prime-casefile-arc-2026-07-15]] — the pattern
  `polish()` reuses (digest + LLM + preservation-check)
