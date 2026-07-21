---
name: ship-11-prime-arc-retrospective-2026-07-21
description: "Ship 11' arc retrospective — extractor quality; 5 sub-arcs; filters absorbed coverage growth but didn't solve the specific noise patterns"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 11' arc — extractor quality enhancement. Started from
Ship 10's HITL data (49 rejects out of 97) with a 5-pattern
taxonomy. Ended with a honest but nuanced conclusion:
structurally-correct filter infrastructure that absorbs
coverage growth, but doesn't solve the specific attribution
noise patterns Ship 10 surfaced.

**Arc window:** 2026-07-20 → 2026-07-21. 5 sub-arcs across
~1.5 days.

## Sub-arc inventory

| Sub-arc | Delivery | Impact against Ship 10 patterns |
|---|---|---|
| 11'.a | Design memo — 5-pattern taxonomy + hybrid 3-layer architecture | Framing |
| 11'.b | Bridge source-quality gate in `xfw_proposer.py` | 0-3 rejects caught structurally; future-proofs against weaker sources |
| 11'.c | MUST-aware content-shape filter in `extractor.py` | 10 of 16 Pattern-1/3 rejects (63%) |
| 11'.d | Critic prompt enhancement (business_description + MUST-prefix taxonomy) | Reduced findings but destabilized JSON |
| 11'.d/redesign (in 11'.e) | Prompt reverted + post-critic `_semantic_fit_ok()` embedding gate | Preserved case-file discipline; 2-3 drops observed empirically |
| 11'.e | Measurement checkpoint + Ship 11'.c FP-path fix | Surfaced methodology confound + real-pipeline test |

## The concrete measurement

Real re-extraction of Ship 10's 5 documents via `/api/v1/admin/uploads/{id}/reextract`:

| Doc | Ship 10 pending | Ship 11 pending | Δ |
|---|---|---|---|
| Data Quality Accuracy | 9 | 9 | 0 |
| DPIA Procedure | 13 | 6 | **-7** ↓ |
| Records of Processing Activities | 17 | 15 | -2 |
| Consent Management | 28 | 26 | -2 |
| Processor Operations | 30 | 46 | **+16** ↑ (Ship 9's new program_review mappings firing) |
| **TOTAL** | **97** | **102** | **+5** (flat) |

**Ship 11 kept the volume flat despite Ship 9 adding 189
mappings + 51 program_review leaves between Ship 10 and now.**
Without the Ship 11 filters, the raw dry-run showed 227
findings — 134% growth from coverage expansion. Filters absorbed
that growth.

## What the filters caught

Concrete drops observed:
- **`dropped_content_shape`**: 2 on DQA (both v1 and v2 dry-run
  measurements)
- **`dropped_semantic_fit`**: 2 on Consent + 3 on Processor
  (v2 dry-run)
- **Bridge count**: 22 vs Ship 10's 26 (small structural drop
  from Ship 11'.b gate + xfw_proposer scope enforcement)

## What the filters did NOT catch

The **exact same 4 bridge-fanout patterns** that Ship 10
rejected re-appeared in the Ship 11 re-extraction:

- A.7.2.6 → A.5.19 / A.5.20 / A.5.22 (subprocessor mention →
  supplier controls) — fired on DQA, Processor Ops, RoPA
- A.7.4.7 → A.5.33 (retention mention → records protection) —
  fired on DPIA, Processor Ops, RoPA
- A.7.2.8 → A.5.9 (RoPA → asset register) — fired on Consent,
  Processor Ops, RoPA
- A.7.4.8 → A.7.14 (physical disposal — Odoo tenant) — fired
  on Processor Ops

Ship 11'.b's bridge gate blocks: (a) bridge-of-bridge, (b)
low-confidence sources, (c) fragment sources (<40c + no MUST
binding). The Ship 10 rejects were medium-confidence MUST-bound
sources with 44-100 char excerpts — they pass all three gate
checks. The gate is future-proof for weaker sources but doesn't
catch these specific patterns.

## Lessons carried forward

### 1. Case-file discipline is codified for a reason

Ship 11'.d's initial prompt-bloat approach (adding
`business_description` + wrong-attribution examples + MUST-prefix
taxonomy into the system prompt) grew the critic prompt from
2100 → 4900 chars. On Consent Management the enlarged prompt
destabilized JSON output — "both attempts returned malformed
JSON" — dropping all critic findings for that doc.

The user's pointed question — "why has the prompt grown? are
we not disciplined on our case file commitment?" — surfaced
the violation. Redesign: revert prompt bloat, add post-critic
`_semantic_fit_ok()` deterministic gate. That preserves the
principle: LLM composes, deterministic gates verify.

The lesson holds beyond Ship 11: whenever the temptation is to
enrich a prompt to fix a class of noise, first ask whether a
deterministic post-LLM gate could achieve the same thing.

### 2. Measurement methodology matters

The v1 dry-run measurement showed +90% finding volume. First
instinct: Ship 11 is a regression. Actually: Ship 9's mapping
expansion between the two extractions grew the fingerprint
index 60%.

Without an A/B toggle (same index, filters ON vs OFF), the
measurement conflates coverage expansion and filter impact.
Any future filter-tuning arc should establish an A/B before
drawing conclusions.

### 3. Post-LLM gates can't fix upstream breadth

The Ship 11 filters catch the shapes they were designed for.
But when the fingerprint layer emits 71 MUST matches on
Processor Operations, no post-critic filter can rescue
signal-to-noise ratio. The right fix is UPSTREAM: tighten
fingerprint token sets per MUST.

Example: `A.7.2.6:rev_subprocessor_audit` fires on a bare
"Subprocessors" mention because its fingerprint tokens are
too permissive. A curator arc that trims that fingerprint to
require e.g. `{subprocessor, audit, review_record}` together
would eliminate the noise class at the source.

### 4. Coverage growth is a feature, not a bug

Ship 9 added 189 mappings — 51 program_review leaves plus
Batch 2/3 expansion. This is EXACTLY what we want: more
tenant-facing coverage, more auditor-testable claims. Ship 11's
job wasn't to reduce coverage; it was to reduce false-positive
per-finding noise. It didn't fully succeed on that front, but
it prevented the coverage growth from blowing up the queue.

## Deferred to a curator arc (Ship 12+ candidate)

Real Pattern 2 fix requires the following curator-side work:

1. **Fingerprint token audit** — walk the 2595 fingerprints in
   the current index, flag ones matching >N MUSTs on tenant
   documents. `A.7.2.6:rev_subprocessor_audit`,
   `A.7.4.7:rev_*`, `A.7.2.8:ropa_activity_id` etc. are
   probably too broad.

2. **Bridge condition tightening** — the `IMPLEMENTS/SUPPORTS`
   edges in Neo4j fire regardless of whether the SOURCE finding
   is substantive. Curator could add conditions like "bridge
   only when source has ≥N MUSTs satisfied" or "bridge only for
   specific source-MUST-prefix families".

3. **Per-anchor evidence-shape schema** — extend `applies_when`
   or add a new field defining what SHAPE of evidence satisfies
   the anchor's core obligation (procedure vs register vs
   review). The Ship 11'.c/d MUST-prefix taxonomy hints at this
   but was never made curator-first.

4. **Neo4j `business_description` completeness** — many anchors
   have empty or thin `business_description`. Ship 11'.d/redesign
   fail-opens when the description is missing, which means the
   semantic-fit gate silently doesn't run on those anchors.

## What ships from Ship 11

**Structural additions:**
- `_bridge_worthy_check()` + `sources_gated` telemetry in
  `xfw_proposer.py` (11'.b)
- `_looks_like_field_or_header()` + `_must_prefix()` +
  `_REGISTER_MUST_PREFIXES` + `dropped_content_shape`
  telemetry in `extractor.py`, wired into all 3 finding-
  emission paths (11'.c + 11'.e FP-path extension)
- `_semantic_fit_ok()` + `_cosine()` + `_get_embed_fn()` +
  `_ANCHOR_EMBED_CACHE` + `dropped_semantic_fit` telemetry in
  `critic_verifier.py` (11'.d/redesign)
- `business_description` on `PrimingControl` + fetched in
  `build_control_meta_from_neo4j` (11'.d + retained after
  redesign as gate-input data)

**Tests + tooling:**
- `tests/test_bridge_source_quality_gate.py` — 13 assertions
- `tests/test_content_shape_filter.py` — 30 assertions
- `scripts/measure_ship11_reextraction.py` — dry-run harness
  for future A/B filter measurements

**Documentation:**
- 5 sub-arc memos + this retrospective
- CLAUDE.md build-sequence entries (pending — this arc close)
- Ship 12+ curator-arc recommendation documented

## Baseline throughout

225/226 PASS + 1 WARN + 0 FAIL across all 5 sub-arcs. Chat-side
eval unaffected — the extractor changes don't touch the chat
pipeline.

## Ship 11' close

| Sub-arc | Status |
|---|---|
| 11'.a Extractor quality plan | ✓ |
| 11'.b Bridge source-quality gate | ✓ |
| 11'.c Content-shape filter | ✓ |
| 11'.d Critic prompt enhancement (redesigned in 11'.e) | ✓ (partial revert) |
| 11'.e Measurement checkpoint | ✓ |
| **11'.f Arc retrospective** | **✓ (this doc)** |

## Related

- Ship 10 HITL review (2026-07-20) — the source dataset
- [[ship-11-prime-a-extractor-quality-plan-2026-07-20]] —
  design memo
- [[ship-11-prime-b-bridge-source-quality-gate-2026-07-20]]
- [[ship-11-prime-c-content-shape-filter-2026-07-20]]
- [[ship-11-prime-d-critic-prompt-enhancement-2026-07-21]]
- [[ship-11-prime-e-reextraction-measurement-2026-07-21]]
- [[ship-2-prime-casefile-arc-2026-07-15]] — the discipline
  Ship 11'.d/redesign restored
- Ship 12 candidate: curator-arc for fingerprint token
  discipline + bridge condition tightening + per-anchor
  evidence-shape schema
