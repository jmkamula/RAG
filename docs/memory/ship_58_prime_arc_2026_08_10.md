---
name: ship-58-prime-arc-2026-08-10
description: "Ship 58' arc retrospective — two coordinated tracks landed
  together over 2026-08-08→10. Track A (Templates rendering polish): 5
  mechanical passes bulk-normalised 844 templates to a canonical section
  skeleton, wired the Ship 56' guidance / Ship 57' prereqs / Ship 1.7
  xfw-bridges data into every template download, then 8+ readability
  iterations informed by tenant review (label duplication, section
  renames, blockquote-wrap N/A, humanised markers, hand-auth strip,
  boilerplate strip, multi-line bold fix, prefill removal). Track B
  (Single source of truth): closed the each-consumer-runs-the-engine
  pattern via 4 steps (engine per-MUST stale + partial fields → 18-MUST
  data audit → posture_must_verdicts persistence → template tick
  indicator). Codified lessons: additive over replacement for tenant-
  facing UX, portable markdown ≠ HTML-strippable markdown, absence-of-
  row is a valid N/A encoding, data-sample audit before persist,
  on-the-fly beats grounded store when underlying data is already
  curator-authored."
metadata:
  type: project
  ship: "58'"
---

# Ship 58' — Templates rendering polish + single source of truth for per-MUST verdict

## The arc in one sentence

Two coordinated tracks landed as one commit: (A) a 5-pass mechanical
normalization + 8-iteration polish that made every downloaded template
surface the full compliance context living in the Ship 56' / 57' / 1.7
data model; (B) a 4-step single-source-of-truth arc that closed the
"each consumer runs the engine independently" pattern by persisting
per-MUST engine verdicts to a new `posture_must_verdicts` table and
wiring the template renderer's Best-practice tick indicator to it.

## Motivation

Ship 57' shipped per-leaf prerequisites; Ship 56' shipped per-MUST
guidance; Ship 1.7 shipped cross-framework bridges. All three had rich
data + working renderers + working SPA surfaces. **But downloaded
templates surfaced almost none of it** — only 2 of 844 templates
carried `<<GUIDANCE>>` markers, 3 carried `<<PREREQUISITES>>`, zero
carried a cross-references block. A tenant downloading a template
saw a bare MUST checklist and none of the "before you start" /
"here's what best practice looks like" / "here's how this maps to
other frameworks" content that other UX surfaces already delivered.

Data-vs-deployment gap. Deployment side was a mechanical text-processing
job across 844 template files.

Then during template review, the tick-indicator ask surfaced a deeper
architectural gap: **there was no single canonical source of truth
for per-MUST fulfillment state**. Four overlapping stores each spoke
partial truth (`document_findings` raw, `posture_controls` per-control,
`posture_assertions` per-control audit log, engine-as-function computed
on demand). Every consumer that wanted per-MUST truth ran the engine
themselves — including the template renderer we were about to build.
Track B closes that.

## Sub-arc breakdown

### Track A — Templates rendering polish

| Sub-arc | Deliverable |
|---|---|
| 58'.a | Pass 1: `scripts/dev/templates_pass1_architecture.py` — canonical section skeleton (What this template gives you / When to use it / Prerequisites / Cross-references / Estimated effort / Revision history) inserted additively across 844 templates via gpt-4.1 for LLM prose. Zero LLM failures. Cost ~$2.53. |
| 58'.b | Pass 1b: `templates_pass1b_doc_control_reposition.py` — `<<DOC_CONTROL>>` moved from footer-with-heading to top-inline after user preference. 842 files touched. |
| 58'.c | Pass 2: `templates_pass2_guidance_markers.py` — `<<GUIDANCE>>` inserted after every MUST/SHOULD marker (5,367 insertions). Deterministic text op, sub-second execution. Ship 56' data now surfaces in every template download (was 2/844). |
| 58'.d | Pass 3: `templates_pass3_marker_gap_fix.py` — 18 tier-A anchors with pre-existing hand-authored Prerequisites/Cross-references sections got `<<PREREQUISITES>>` + `<<CROSS_REFERENCES>>` markers appended at section end. Hand-auth content preserved. |
| 58'.e | Pass 4: `rag/templates/cross_references_lookup.py` — after a Neo4j diagnostic confirmed edge titles carry rich curator rationale prose, chose **on-the-fly resolution over grounded YAML store**. Reader queries the graph (IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE edges — 452 total) grouped by relationship type. Saved an entire arc of curation. |
| 58'.f | Pass 5: `rag/templates/renderer.py` markdown equivalents of Ship 54'.d docx blocks — `<<DOC_CONTROL>>` renders as a 2-column compact table, `<<REVISION_HISTORY>>` as a 4-column table seeded with current template_version + today. Same content the docx renderer emits. |
| 58'.g | Iteration wave 1 — hand-auth stripping. `templates_strip_hand_auth.py` removed curator-authored intra-framework bullets from 20 tier-A anchors' Prerequisites + Cross-references sections. Generated content owns the sections cleanly. |
| 58'.h | Iteration wave 2 — label / naming polish. Dropped redundant `**Prerequisites:**` / `**Cross-references:**` bold labels (H2 already names the section); replaced with italic intros. Renamed `## Before you start` → `## Prerequisites` in all 844 templates. Added `**Foundational** / **Direct upstream** / **Cross-framework**` bold category sub-headers (previously invisible — category ordering was hidden behind flat bullet list). |
| 58'.i | Iteration wave 3 — 393-template boilerplate strip. `"Replace the placeholders below with your content. Leave the MUST/SHOULD heading markers untouched"` blockquote removed — redundant with the top-of-doc "How to use this template" intro AND referred to stale marker convention (MUST/SHOULD instead of ◆). |
| 58'.j | Iteration wave 4 — multi-line bold repair. 19 tier-A anchors had `**word\nnext-line**` bold spanning newlines (hard-wrap broke strict markdown parsers → literal `**` rendered). Joined across newlines to single-line format. |
| 58'.k | Iteration wave 5 — N/A section handling. Instead of `_strip_na_sections` dropping the entire section, `_mark_na_sections` retains it: H2 heading stays at normal weight; body is wrapped in `> ` blockquote prefix (portable visual distinction); italic-callout at top with tenant-facing `reason` from `tenant_must_overrides.reason`; `<<GUIDANCE>>` marker dropped for N/A section (no best-practice callout); `<<TEXT>>` replaced with `_[Not applicable — no evidence required.]_`. Section numbering (1, 2, 3, ...) preserved. |
| 58'.l | Iteration wave 6 — humanised system markers. `<<MUST/SHOULD item:X>>` marker lines transformed at final render pass to `**◆ Required element — {humanised slug}**` visible bold + `_Do not edit — system id_: \`<<MUST item:X>>\`` explanatory line below. Round-trip preserved (intake regex matches inside backticks). |
| 58'.m | Iteration wave 7 — prefill elimination. Download endpoint flipped from `prefill=not empty` → `prefill=False`. Ship-55'-era `_compose_prefill_block` no longer runs; tenant edit-zones show just `[ Click to enter your evidence here ]`. Evidence lives in Dashboard, no template-level duplication. |

### Track B — Single source of truth for per-MUST verdict

| Sub-arc | Deliverable |
|---|---|
| 58'.n | Phase 1 audit: code walk of `fulfilment_engine.py`, `leaf_evaluators.py`, `engine_runner.py`. Coverage matrix produced (12 dimensions). Three real gaps identified: (1) freshness at leaf level not per-MUST; (2) `partial`-status findings treated as absent; (3) cross-framework bridges don't propagate satisfaction. |
| 58'.o | Step 1: `LeafVerdict` extended with `item_ids_stale` + `item_ids_partial` fields. `GenericLeafEvaluator._fetch_recognised_items` now returns per-MUST latest_uploaded_at + partial status. `_check_freshness` stays leaf-wide (backward compat); new per-MUST staleness computed inline in `__call__`. Additive change — zero downstream impact. Eval regression: identical 231/232 baseline. |
| 58'.p | Step 2: Phase 2 audit — `scripts/dev/audit_engine_per_must.py` runs the engine on 18 diverse MUST ids across ISO 27001 / ISO 27701 / GDPR + shapes + edge cases (partial-only, both-present-and-partial, N/A override). 18/18 match after fixing 2 catalog-typo audit-list entries. Zero engine bugs surfaced. |
| 58'.q | Step 3: `db/schema_v94_posture_must_verdicts.sql` + `posture_loader._persist_must_verdicts()` writer hook. RLS-scoped table with `(tenant_id, must_id) UNIQUE`, columns `(satisfied, stale, partial, reason, computed_at)`. Best-verdict-wins dedup for shared MUSTs (rare Ship 12'.a `rev_identity_pair` case). Populated on Arion: 4,291 rows (704 satisfied + 80 partial + 0 stale + 3,507 unrecognised). N/A signaled by absence-of-row. |
| 58'.r | Step 4: `_fetch_must_verdicts_for_ids()` + `_apply_guidance_blocks(body, verdicts)` — renderer extracts MUST ids from body, queries the persisted table, threads results through applier. Best-practice callout header carries a three-state tick: `**Best practice ✓ — covered:**` / `**Best practice ◐ — partly covered:**` / `**Best practice — still needed:**` / `**Best practice:**` (neutral fallback). Verified end-to-end on A.5.15 download: 5 ✓ + 1 ◐ + 3 blank. |

## Key architectural decisions

**1. Additive over replacement for tenant-facing UX.**
Every template-touching operation across all 13+ sub-arcs preserved
existing curator-authored content by default. Pass 1 skipped sections
already present. Pass 3 appended markers to existing sections. Wave 1
strip was a deliberate later step, once the generated content was
proven visible-enough to replace hand-auth.

Rule: preserve curator judgment on first pass; audit-and-replace only
after generated content has been reviewed.

**2. Deterministic scripts beat LLM for mechanical text ops.**
Only Pass 1's 3 prose sections used the LLM (~$2.53 in gpt-4.1
tokens). Passes 2, 3, 1b, hand-auth-strip, boilerplate-strip,
multi-line-bold-fix are all pure Python regex passes — deterministic,
idempotent, sub-second execution, zero cost.

Rule: reach for the LLM only when the transformation requires
generation, not when it requires transformation.

**3. On-the-fly beats grounded YAML when underlying data is already
curator-authored.**
The Ship 1.7 xfw bridge edges carry rationale prose that reads
tenant-facing after a Neo4j diagnostic sample confirmed 100% coverage.
Building a grounded YAML store like Ship 56' guidance / Ship 57'
prereqs would have been an entire arc of authoring cost for zero
signal gain. Chose on-the-fly resolution + runtime cache.

Rule: diagnose the underlying data quality before deciding whether a
grounded authoring layer is needed. Deferred authoring debt is
enemy #1 for curator time.

**4. Blockquote-wrap for portable N/A visual distinction.**
Considered HTML `<div style="opacity">` (unreliable across viewers),
italic wrapping (breaks around existing formatting), strikethrough
(inconsistent). Blockquote `> ` prefix works everywhere — plain md
viewers, Word, some previewers all render an indented / muted block.
Nested `>>` for existing per-MUST blockquotes rendered fine.

Rule: default to portable markdown constructs; escape hatches into
HTML only when data-tested against actual tenant viewers.

**5. Visible-but-de-emphasized system markers, not hidden HTML
comments.**
First tried `<!-- <<MUST item:X>> -->` HTML comment wrapping. Tenant
review showed the comment renders as literal text in their viewer.
HTML comment invisibility is markdown-parser-dependent and unreliable
across the tenant viewer diaspora. Replaced with visible-but-explained
tag: `**◆ Required element — humanised slug**` + `_Do not edit —
system id_: \`<<MUST item:X>>\`` on next line. Tenant knows what the
tag is, why it's there, and to leave it alone.

Rule: don't rely on "invisibility" in markdown — assume the tenant
sees everything and design what they see for comprehensibility.

**6. Engine-as-function → per-MUST truth table.**
Multiple consumers (template renderer, SPA leaf-detail, chat,
dashboard) all had the same need: "for MUST X, is it satisfied?"
Each independently ran `build_per_must_advisory_data()` (which
internally runs `compute_engine_verdicts()`). Duplication of both
compute cost and staleness semantics.

Solved by persisting engine output to `posture_must_verdicts` on
every `posture_loader.load_posture()` refresh — same cadence as the
existing `posture_controls`. Consumers query one table, get one truth.

Rule: when N consumers each compute the same truth, persist once and
read many times. The consumer surface simplifies + refresh semantics
consolidate to one job.

**7. Absence-of-row as valid N/A encoding.**
`posture_must_verdicts` doesn't have an `n_a` column. When a MUST is
N/A-excluded via `tenant_must_overrides.applies=FALSE`, the
`GenericLeafEvaluator` drops it from `must_item_ids` before the
recognition scan — so it never appears in `item_ids_{recognised,
unrecognised, partial, stale}`. Persistence follows: no row is
written. Consumers reading `WHERE must_id = X` get an empty result
set = correct signal ("not tracked → not applicable").

Rule: absence-of-row is a legitimate design encoding when the truth
condition is truly binary "in scope vs excluded." Don't force a
nullable/tri-state column for what's semantically a set-membership
check.

**8. Best-verdict-wins dedup for MUSTs shared across leaves.**
Ship 12'.a's `item:A.5.18:rev_identity_pair` appears under two
leaves (identity + auth). Same evidence applies to both. Persistence
writer aggregates per `must_id` and keeps the most positive verdict:
recognised > stale-recognised > partial > unrecognised.

Rule: when the persistence grain is coarser than the compute grain,
choose an aggregation rule that reflects the underlying reality.
Here: shared MUST id = shared evidence = shared truth.

## Coverage — before vs after

**Template surface:**

| Marker / section | Before Ship 58' | After Ship 58' |
|---|---:|---:|
| `<<GUIDANCE>>` | 2 / 844 (0.2%) | 844 / 844 (100%) — 5,386 total insertions |
| `<<PREREQUISITES>>` | 3 / 844 (0.4%) | 844 / 844 (100%) |
| `<<CROSS_REFERENCES>>` | 0 / 844 | 844 / 844 (100%) |
| `<<DOC_CONTROL>>` | 2 / 844 | 844 / 844 (top-inline convention) |
| `<<REVISION_HISTORY>>` | 2 / 844 | 844 / 844 |
| `## Prerequisites` section | 21 / 844 | 844 / 844 (renamed from "Before you start") |
| N/A section handling | dropped entirely | preserved + blockquote-wrapped + callout with reason |

**Per-MUST verdict store (`posture_must_verdicts` for Arion demo):**

| Category | Rows |
|---|---:|
| satisfied (recognised + fresh) | 704 |
| partial | 80 |
| stale | 0 (Arion's data all recent) |
| unrecognised | 3,507 |
| **total** | **4,291** |
| N/A-excluded (absence-of-row) | ~1,000+ (not persisted) |

## Codified lessons

### 1. Portable markdown ≠ HTML-strippable markdown

HTML comments (`<!-- ... -->`) SHOULD be invisible in rendered markdown.
In practice, many viewers (Word imports, some previewers, plain-text
displays) show them as literal text. This isn't a bug in any specific
viewer — it's a spec-vs-implementation gap in the markdown ecosystem.

Design corollary: assume every character in the source md renders.
"System" content the tenant might see needs to be either legitimately
invisible (via structural constructs like backticks/code blocks that
signal "technical") or visibly labeled and self-explaining.

### 2. Absence-of-row is a valid encoding for N/A

`posture_must_verdicts` handles N/A-excluded MUSTs by not writing a
row. Consumers reading `WHERE must_id = X` get an empty result set,
which correctly means "not tracked for this tenant → not applicable."

The alternative — a nullable `n_a` column or a tri-state
`status` enum — pushes complexity into every reader without adding
information. When a set-membership check is the semantic truth,
absence-of-row is honest.

### 3. Data-sample audit before persist

Two-phase audit (code walk + 18-MUST data sample) surfaced 0 engine
bugs, 2 audit-list typos, and 1 useful design decision (cross-framework
bridge propagation is intentionally scoped out — documented). Total
cost: ~1 hour of investigation.

Would have shipped a 4,291-row lie-machine if we'd skipped straight
from "design SSoT table" to "write it." The audit shape (raw findings
+ N/A logic → expected truth; engine output → actual truth; compare)
is reusable for any truth-computing function you're about to persist.

### 4. On-the-fly beats grounded YAML store when underlying data is
already curator-authored

Ship 56' guidance + Ship 57' prereqs needed grounded YAML stores
because the underlying data (Neo4j edges' short labels) was too terse
to render tenant-facing. Ship 58' cross-references was different:
Ship 1.7's xfw bridge `rationale` field carries curator-quality prose
already. Building a grounded store would have been an entire arc of
authoring cost for zero user-visible signal gain.

Diagnostic step: sample the underlying data before deciding whether
to build a grounded layer. If the data is already curator-authored
at the right depth, wire the reader. If it's terse/machine-generated,
build the grounded layer.

### 5. Iteration cycle for tenant-facing UX pays off

The templates rendering had 8+ iterations post-Pass-1 based on user
review of specific downloaded templates. Each iteration surfaced a
real readability issue that the "canonical shape" alone didn't cover
(label duplication, section naming, multi-line bold, HTML comment
visibility, prefill clutter).

Ship the canonical shape → have a real tenant look at a real render
→ fix what's ugly → repeat. The iterations were cheap (~10-15 minutes
each) and each one made the shape closer to what the tenant would
actually want. If we'd waited to "get it right" before the first
review, we'd have delayed forever.

### 6. Engine as function → per-MUST truth table pattern

When N ≥ 3 consumers all need the same computed truth, persist the
function's output once and let consumers read the persisted table.
Trade-off: minor staleness window (bounded by refresh cadence) in
exchange for cheaper reads, consistent truth across consumers, and
one clear place to inspect/debug.

Applied to per-MUST fulfillment via `posture_must_verdicts`. Same
pattern would apply to (a) per-leaf posture, (b) per-control gap
reasons — anywhere multiple consumers currently each run the engine.

### 7. Additive engine changes ship cleanly

Adding `item_ids_stale` + `item_ids_partial` to `LeafVerdict` had
zero downstream impact — existing consumers (advisory.py, dashboard,
chat) just don't read the new fields. Same for adding columns to
`posture_must_verdicts` (satisfied / stale / partial — all
independently set).

Additive shape lets you extend engine semantics without a big-bang
migration of consumer code. Combined with backwards-compat query
patterns (e.g. leaf-level `fresh: bool` still emitted alongside
per-MUST `item_ids_stale`), the new dimensions become opt-in.

## What's now different in the product

**Every downloaded template — for every tenant, every leaf, every
framework — now surfaces:**
- Prerequisites (Ship 57' data): category-grouped list of upstream
  artefacts with rationale + good-enough thresholds
- Cross-references (Ship 1.7 data): grouped by IMPLEMENTS / SUPPORTS
  / ENABLES / GOVERNANCE bridges with per-edge curator rationale
- Doc control (top-inline): 6-row table with doc number, revision,
  wet-sign lines
- Revision history (footer): 4-column table seeded with current version
- Best practice per MUST (Ship 56' data): 3-5 imperative steps with a
  three-state tick indicator (✓ satisfied / ◐ partial-or-stale /
  still-needed) driven by the new `posture_must_verdicts` table
- N/A sections retained + visually distinct + reason surfaced from
  `tenant_must_overrides.reason` (no more silently-vanishing sections
  with numbering gaps)
- System markers transformed to human-friendly labels with round-trip
  binding preserved

**Every consumer of "is this MUST satisfied?"** now has a canonical
answer to query: `posture_must_verdicts`. Template renderer already
uses it. SPA leaf-detail + chat + dashboard can migrate off their
own engine calls to read from the table in follow-on arcs (see #577
already pending).

## Follow-ons deferred

- **SPA leaf-detail migration**: the leaf-detail endpoint's fallback
  path (added in Ship 57' when advisory returned None for Comply
  leaves) can be simplified — read `posture_must_verdicts` directly.
- **Chat pipeline consumption**: queries like "which A.5.15 MUSTs are
  covered?" can hit the table instead of re-running the engine per
  turn.
- **Dashboard drill-in migration**: same.
- **Bridge-coverage secondary signal** (Gap 1 from audit): if tenant
  demand surfaces, add a `bridge_covered: bool` column to
  `posture_must_verdicts` populated by walking IMPLEMENTS/SUPPORTS
  edges. Currently intentionally scoped out — auditors expect
  per-framework dossiers.
- **Per-step tick accuracy**: rejected as too expensive for MVP
  (per-step LLM matching = ~$0.02 per template render + ~2-5s latency).
  Can be an opt-in "premium accuracy" mode later.
- **Docx tick indicator**: the markdown renderer emits ✓/◐ ticks but
  the docx renderer still emits the neutral "Best practice:" label.
  Small mirror change for tenants who download .docx.
- **Read-only enforcement** (deferred per user's "let's finish tuning
  the documents and then we can apply the hardening" call): docx +
  xlsx cell/section protection so tenants can edit only the edit-zones,
  not the system content.
- **Retro on Gap 1 decision**: if any tenant asks why their GDPR
  Art.32 evidence doesn't automatically satisfy ISO A.5.15,
  documented answer is "per-framework dossier discipline; upload
  A.5.15-bound evidence for A.5.15." Signal for revisiting.
- **Chat prose gateway migration** (Ship 7' follow-on that's still
  pending): the same "output gateway" pattern that governs API
  responses could clean up any last raw slugs surfaced in template
  render prose.

## What Ship 58' costs to reproduce

- **LLM cost**: ~$2.53 for Pass 1's 3 prose blocks × 844 templates.
  All other passes are deterministic Python.
- **Wall clock**: ~25 min Pass 1 bulk gen + sub-second on every other
  pass + ~1 min per iteration cycle (edit + restart API + curl-verify)
  × ~8 iterations = ~10 min iteration time.
- **Human time**: ~5-6 hours across the arc — most in the iteration
  cycle (reviewing rendered output + deciding on next tweak) and
  ~1.5 hours on Track B (audit + persist + tick).
- **Schema migrations**: 1 (schema_v94 posture_must_verdicts).
- **Files touched**: 857 (mostly the 844 templates + 13 code/schema
  files); 33,244 lines inserted.

Cheaper than any equivalent template rewrite from scratch would have
been. And the per-MUST truth table is a compounding investment — every
future consumer that needs per-MUST state now costs zero engine walks
to satisfy.
