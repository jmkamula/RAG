---
name: ship-28-prime-arc-retrospective-2026-07-24
description: "Ship 28' arc closer — singleton fingerprint fix; 976 → 0 auto-generated singleton entries via surgical generator fix + 352-file bulk regen; codifies redundant-emission-is-worse-than-absent lesson"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 28' arc retrospective — 3 sub-arcs across one day
(2026-07-24) delivering the single-token fingerprint fix
deferred from Ship 17 (~11 arcs ago). Follow-on to Ship 27's
finding that `grounding_method` is the quality signal —
Ship 28 improves the deterministic fingerprint layer at
its source.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 28'.a | Design memo + root-cause + fix strategy | 4643636 |
| 28'.b | Generator fix (5 lines) + 352-file regen + Ship 17 restoration | 298383b |
| **28'.c** | **Eval + retrospective (this doc)** | pending |

## The fix in one paragraph

`scripts/gen_leaf_scan_catalog.py::_starter_excerpt_keywords`
was unconditionally emitting id-token and description-token
singletons alongside their multi-token variants. Result: item
`item:6.1.2:consistency` (description "Consistent and
comparable results produced") got `[consistency]`,
`[consistent]`, `[comparable]`, `[results]` as separate
match-alternatives PLUS the bigrams and trigrams that already
covered the same content with better specificity. Fix:
`has_multi = any(len(s) >= 2 for s in suggestions); if
has_multi: suggestions = [s for s in suggestions if len(s)
>= 2]`. Preserved as last-resort safety net when NO multi-
token alternative exists.

## Numbers

**Auto-generated fingerprint files** (352 files):
| Metric | Pre-Ship-28 | Post-Ship-28 |
|---|---|---|
| Single-token `excerpt_keywords` entries | 976 | **0** |
| Total keyword-set entries | ~2100 | ~2600 (multi-token replaces singletons) |

**Whole catalog** (598 files including 246 hand-authored):
| Metric | Pre-Ship-28 | Post-Ship-28 |
|---|---|---|
| single_token groups (audit_fingerprints.py) | 472 | **195** (58.7% drop) |
| All remaining single_token groups | 292 in hand-auth + 180 in auto-gen | 195 in hand-auth ONLY |

Ship 17'.b discipline respected — hand-authored files
(246 total) stay untouched. The 195 remaining singletons are
all curator decisions.

## Restoration + subtle regression

**Mid-arc regression + fix**: my first bulk regen used
`gen_leaf_scan_catalog.py` for ALL auto-generated files,
including 27701 program_review + applicable_scope. That
reverted Ship 17'.b/c's topic-anchor injection (which lives
in the specialized `generate_27701_fingerprints.py`).
Restored by re-running the specialized generator for 6 family
× standard combos:
- ISO27001:2022 program_review + applicable_scope
- ISO27701:2019 program_review + applicable_scope
- GDPR:2016/679 program_review + applicable_scope

Net effect: 192 files ultimately modified.

## Ship 16'.b runtime gate still load-bearing

Cross-leaf collision count in the audit went UP:
- Pre-Ship-28: `[per, row]` fired on 10 leaves
- Post-Ship-28: `[per, row]` fires on 60 leaves

Root cause: the `[:8]` cap now has room for
`_ROLE_PREFIX_HINTS` scaffolds where previously singletons
crowded the slots. These scaffolds are DELIBERATELY cross-
register — that's their design purpose. Ship 16'.b's runtime
specificity gate (`>5-leaf drop`) handles this at extraction
time.

**Net runtime behavior is correct**: the matches ARE
dropped by Ship 16'.b's gate before they can propagate to
findings. The audit output looks louder but the
compliance-load-bearing pipeline is unchanged.

## Eval outcome

**231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to all
prior baselines. Ship 28 changed only the fingerprint catalog
data (not code); extraction changes would only materialize on
re-extraction of documents, not on eval-suite chat runs.
Baseline held.

## Codified 3 lessons

### 1. Redundant emission is worse than absent emission

The pre-Ship-28 generator emitted `[consistency]`,
`[consistent]`, `[comparable]`, `[results]` as singletons
"just in case" — even though the same MUST already had 3
multi-token variants covering the same content. The
singletons couldn't add ANY signal the multi-tokens didn't
already carry; they only ADDED false-positive matches.

The general principle: **when a generator has both a
high-specificity and a low-specificity variant of the same
pattern, drop the low-specificity variant.** Adding both
doesn't help; adding both hurts. This is a discipline that
generalises beyond fingerprints — any "match-alternatives"
list benefits from the same filter.

### 2. Multi-generator drift is a real risk

Two generators produce fingerprints:
- `gen_leaf_scan_catalog.py` (general, no topic anchors)
- `generate_27701_fingerprints.py` (Ship 17'.b/c —
  topic-anchor injection for program_review + applicable_scope)

My first regen pass used the general one for ALL auto-generated
files, silently reverting Ship 17'.b/c's work on the
specialized files. Caught by the audit (Art.32-adjacent
program_review leaves collided at 148+ leaves post-first-regen).
Restored by re-running the specialized generator.

**Rule**: when two generators cover overlapping surfaces,
document which owns which files. A bulk-regen tool must
route each file to its correct generator, or run them in
sequence. Follow-on candidate: consolidate topic-anchor
injection into `gen_leaf_scan_catalog.py` itself so the
specialized generator becomes redundant.

### 3. Runtime gates + catalog quality are complementary not redundant

Ship 16'.b's `>5-leaf drop` runtime specificity gate could
have absorbed 100% of the singleton noise. But Ship 28
still made sense because:
- Catalog quality is auditable (Ship 27's discipline —
  first-class DB signals over in-flight labeling)
- Runtime gates are silent (a `dropped_low_specificity`
  counter but no audit-facing detail)
- Upstream fixes reduce the runtime cost of the gate
  (fewer matches to evaluate)

The pattern: **runtime gates are the safety net; catalog
quality is the correctness floor.** Both matter. Ship 28
raised the floor by 976 entries; the safety net still works
for the ~500 legitimate cross-register templates that
remain.

## What Ship 28 did NOT do

- **Consolidate two generators** — deferred; the
  restoration hack (running specialized generator after
  general) works but is fragile
- **Hand-edit any curator-authored file** — the 195
  hand-authored singletons stay
- **Extend `_NEVER_EMIT_SINGLETON`** — algorithmic fix
  handles the redundancy class; block-list keeps role for
  always-bad tokens
- **Re-extract documents** to measure grounding_method
  delta — Ship 27's audit tool remains ready; future arcs
  can measure

## Deferred / follow-on candidates from Ship 28

- **Consolidate topic-anchor injection into
  `gen_leaf_scan_catalog.py`** — retire the specialized
  27701 generator, eliminate multi-generator drift risk
- **Re-extract Ship 10 5-doc corpus** to measure post-
  Ship-28 grounding_method distribution shift
- **Curator arc for the 195 hand-authored singletons** —
  either replace with multi-token alternatives OR add to
  `_NEVER_EMIT_SINGLETON`

## Ship 28 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 28'.a | Root-cause + fix strategy + expected outcome | Locked 5-line surgical fix; regen scope; measurement plan |
| 28'.b | Fix generator + regen 352 auto-gen files + restore Ship 17'.b/c | 976 → 0 auto-gen singletons; hand-auth 195 preserved; API restart clean |
| **28'.c** | **Eval + retro (this)** | **231/232 PASS baseline held; arc closed** |

## Related

- Ship 16'.a (2026-07-22) — audit that first surfaced the
  singleton class (556 groups pre-Ship-17)
- Ship 17'.b (2026-07-23) — the auto-generated header guard
  Ship 28 respected
- Ship 17'.c (2026-07-23) — the specialized 27701 generator
  Ship 28'.b restored after unintended overwrite
- [[ship-27-prime-arc-retrospective-2026-07-24]] — the
  grounding_method quality-signal audit Ship 28 improves
