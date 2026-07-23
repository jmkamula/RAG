---
name: ship-17-prime-arc-retrospective-2026-07-23
description: "Ship 17' arc closer — fingerprint catalog regeneration; 44 gate-trigger token sets → 10 (77% reduction); extraction flat but gate now safety net not primary defense"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 17' arc retrospective — 4 sub-arcs across one day
(2026-07-23) delivering the "fingerprint catalog regeneration"
deferral from Ship 16. Root-cause fix: the auto-generator was
emitting family-templated token sets across dozens of leaves;
Ship 17 injected topic-anchor tokens from `RequirementNode.title`
so every leaf is now distinctive at generation time.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 17'.a | Regeneration strategy + generator audit memo | 2b2cad4 (opened arc) |
| 17'.b | Generator enhanced with topic-anchor injection + regenerated 27701 (98 files) | 547174a |
| 17'.c | Generator generalised via `--standard` + regenerated 27001 + GDPR (109 files) | 8196427 |
| **17'.d** | **Measurement + arc retrospective (this doc)** | pending |

## Root cause + fix

**Root cause** (from 17'.a): `scripts/generate_27701_fingerprints.py`
built keyword sets from MUST text first-phrase. Text templates
recurred verbatim across every `program_review` / `applicable_scope`
leaf — e.g. `[review, date, planned, interval]` was emitted on 48
identical leaves. The Ship 16'.b runtime gate dropped these
matches, but the catalog remained noisy.

**Fix** (17'.b): after tokenising the MUST text, inject 1-2
topic-anchor tokens extracted from parent `RequirementNode.title`.
Anchors are filtered against `_TITLE_META_NOISE` (`information`,
`security`, `management`, `data`, `iso`, `iec`, `ensure`,
`ensuring`, `processing`) — the tokens that recur across
compliance titles and would themselves collide.

Before/after on same `rev_date` MUST across three leaves:
- `A.7.2.1:rev_date` → `[review, date, planned, interval, identify]`
- `A.7.2.6:rev_date` → `[review, date, planned, interval, contracts]`
- `A.7.4.7:rev_date` → `[review, date, planned, interval, retention]`

Each leaf is now the sole match for its anchor-augmented token set.

## Metrics

### Catalog quality (audit_fingerprints.py)

| Metric | Pre-Ship-17 | Post-Ship-17 | Δ |
|---|---|---|---|
| Would-trigger Ship 16'.b gate (>5 leaves) | 44 | 10 | **-77%** |
| `multi_noise_only` class | 50 | 2 | -96% |
| `loose_pair_noise_only` class | 62 | 8 | -87% |
| Worst-case fanout | 64 leaves | 10 leaves | -84% |

Remaining 10 gate triggers are ALL register-shape templates
(`[per, row]`, `[each, row]`, `[column, containing]`,
`[each, entry]`, `[named, owner]`) from
`gen_leaf_scan_catalog.py::_EVIDENCE_TYPE_SYNONYMS` — designed
to cross-fire so the extractor recognises per-row register
content across ANY register leaf. Filtering them would defeat
their purpose; the runtime gate catches them belt-and-suspenders.

### Extraction volume (Ship 10 5-doc set)

Re-ran `scripts/measure_ship11_reextraction.py`:

| Doc | Ship 10 | Ship 11'.e (post-16) | Ship 17 (post-catalog) |
|---|---|---|---|
| Data Quality Accuracy | 9 | (n/a) | 12 (+3) |
| DPIA Procedure | 13 | (n/a) | 23 (+10) |
| Records of Processing | 17 | (n/a) | 18 (+1) |
| Consent Management | 28 | (n/a) | 63 (+35) |
| Processor Operations | 30 | (n/a) | 82 (+52) |
| **Total** | **97** | 192 (Ship 11'.e) | **198** |

Extraction volume: **192 → 198 (+3%)** — essentially flat. Ship 17
was NOT expected to reduce extraction volume (Ship 16'.b already
gated the noise at runtime); it was expected to eliminate the
NEED for the gate. Confirmed:

- `dropped_low_specificity` fires **5 total times** across 5 docs
  (Data Quality: 1, DPIA: 1, Consent Mgmt: 3, Processor Ops: 0).
- Runtime gate is now a safety net for register-shape templates,
  not the primary defense against family-templated collisions.

## Design decisions locked in

1. **Data > runtime** — catch quality problems at data generation
   time whenever possible. Runtime gates are correct but they
   process noise every extraction; catalog fixes are one-time
   and permanent.

2. **Provenance guard is mandatory** — regenerator only touches
   files whose first-6-line header contains `# Auto-generated`.
   Hand-authored files (marked "Reviewed-from-skeleton" or
   similar) stay untouched unless `--force` is passed. 65
   hand-authored files preserved across Ship 17'.b + 17'.c.

3. **Topic anchor from RequirementNode.title, not MUST id
   slugs** — the RN.title is the stable human-facing name and
   survives catalog rewrites. MUST ids are internal.

4. **Meta-noise stopword list is curator-specific** — a
   general-purpose stopword list (`the`, `a`, `of`) is not
   enough. Compliance titles need domain-specific noise
   removal (`information`, `security`, `management`, `data`).
   Manual tuning; ~9 tokens covered the 27701 + 27001 + GDPR
   corpus.

5. **Two-standard support via `--standard` flag** — one
   generator, N standards. Fetches `RequirementNode` by
   `standard_id`. No per-standard code branches.

6. **Register-shape templates are DELIBERATE cross-fire** —
   fixing them at the catalog level would defeat their purpose.
   Ship 16'.b's runtime gate is the correct place to catch
   them (matches with >5 leaves get dropped because there's
   too much ambiguity to attribute a specific leaf).

## Ship 14'.a addendum alignment

Not directly applicable (curator/tooling arc, no product
surface). Retroactive fit:

| Check | Applied |
|---|---|
| Role split? | N/A — catalog data |
| Parallel CaseFile view? | N/A — catalog data |
| Deterministic routing? | YES — deterministic transform of Neo4j titles → tokens |
| Guidance-normative discipline? | Preserved — anchors are DATA descriptors, not new MUSTs |

## Codified properties post-Ship 17

- **Fingerprint catalog is leaf-distinctive at token-set level**
  for auto-generated families across ISO 27001, ISO 27701, GDPR.
- **Runtime gates are safety nets, not primary defense** — Ship
  16'.b + 16'.c stay to catch (a) the deliberate register-shape
  templates and (b) any future auto-gen additions before they're
  regenerated.
- **Regenerator scales linearly to new standards** — future
  ISO 27002 / NIS2 / DORA / SOC 2 enrollment adds
  `--standard NEW_ID` and re-runs. No code changes needed.
- **Hand-authored catalog changes are safe** — the `_is_auto_generated`
  guard prevents accidental overwrite. Curator work is never lost.

## What did NOT ship

- **Single-token class fix** (556 fingerprints still single-token
  after prefix noise removal). These bypass the `_MIN_SET_SIZE = 2`
  guard because they have 2 non-noise tokens BEFORE the strip.
  Fixing would require broader generator rewrite. Deferred.
- **Regenerate `_review_record` / `_procedure` / other auto-gen
  families** — less collision-prone than program_review /
  applicable_scope; not in top-10 gate triggers. Audit re-runnable
  as needed.
- **Retire Ship 16'.b or 16'.c runtime gates** — belt-and-suspenders
  discipline; gates stay.
- **Backfill on live tenants** — regenerated catalog affects future
  extractions only. Prior findings not re-processed. Sample re-extract
  on Ship 10 5-doc set is representative; broad backfill deferred.
- **Deep quality audit of the 198 findings** — total flat vs Ship
  11'.e's 192 was expected. Comparing which SPECIFIC leaves those
  findings attach to (vs pre-Ship-17's set) is a Ship 18+ analysis
  question.

## Lessons

1. **Ship-11 attempted per-leaf runtime specificity checks; Ship 16
   built the two-layer gate architecture; Ship 17 fixed the data at
   source.** The right layer for each problem:
   - Ship 11'.d semantic-fit gate (post-critic) — catches semantic
     drift, still relevant, kept.
   - Ship 16'.b specificity gate (extraction) — catches token
     collisions runtime, now safety net.
   - Ship 16'.c substantiveness gate (bridge) — catches
     single-MUST source fanout, still primary.
   - Ship 17 catalog regen (generator) — eliminates the collisions
     upstream.

   Each layer catches a different class of noise. Multiple layers
   is not redundancy; it's defense in depth against different
   failure modes.

2. **Root-cause fixes upstream reduce runtime signal noise.** Post-17
   the `dropped_low_specificity` counter drops from potential-44
   catalog collisions to 5 actual runtime firings — much easier
   to reason about what the gate is doing when it fires only
   for known-intentional templates.

3. **A generalised generator is one CLI flag away.** Ship 17'.b
   built the fix for 27701. Ship 17'.c generalised via a
   parameterised `fetch_leaves(standard_id)` + `--standard` flag
   — 30 minutes of work to service two more standards.
   Cross-standard code should be data-driven from the start when
   possible.

4. **"Extraction volume flat" is the correct outcome, not a
   regression.** The gate was ALREADY catching the noise at
   runtime; Ship 17 just moved the fix upstream. If extraction
   volume had dropped, it would mean the gate was over-broad.
   Match the measurement to the intended impact — audit metrics
   (gate-trigger count) not surface metrics (extraction total).

## Ship 17 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 17'.a | Design memo + root-cause audit | Locked topic-anchor injection strategy + provenance guard |
| 17'.b | Fix generator + regenerate 27701 | Gate triggers 44 → 19 (-57%) |
| 17'.c | Generalise to any standard + regenerate 27001 + GDPR | Gate triggers 19 → 10 (-77% total) |
| **17'.d** | **Measurement + retrospective (this doc)** | **Extraction 192 → 198 (flat, expected)** |

## Related

- [[ship-17-prime-a-regeneration-design-2026-07-23]] — design memo
- [[ship-17-prime-b-regenerate-worst-families-2026-07-23]] — 27701 layer
- [[ship-17-prime-c-regenerate-remaining-2026-07-23]] — 27001 + GDPR layer
- [[ship-16-prime-arc-retrospective-2026-07-22]] — the arc whose
  "fingerprint catalog regeneration" deferral this arc delivered
- [[ship-16-prime-b-specificity-gate-2026-07-22]] — runtime gate
  now serving as safety net
- [[ship-16-prime-c-substantiveness-gate-2026-07-22]] — bridge
  substantiveness gate, still primary
- [[ship-11-prime-arc-retrospective-2026-07-21]] — arc whose
  Ship 11'.d gate stayed; Ship 11'.f fanouts now demonstrably fixed
