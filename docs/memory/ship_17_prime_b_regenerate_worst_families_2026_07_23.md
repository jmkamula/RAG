---
name: ship-17-prime-b-regenerate-worst-families-2026-07-23
description: "Ship 17'.b — generator enhanced with topic-anchor injection; regenerated ISO 27701 program_review + applicable_scope families; 27701 collisions triggering Ship 16'.b gate dropped 25→0"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 17'.b — implementation of the topic-anchor injection
designed in 17'.a. Regenerated the 2 worst-offender ISO 27701
families (program_review + applicable_scope), verified against
`audit_fingerprints.py`.

## What ships

### Generator enhancements (`scripts/generate_27701_fingerprints.py`)

- **`_topic_anchor_tokens(title)`** — extracts 1-2 distinctive
  tokens from `RequirementNode.title`. Strips meta-tokens that
  recur across compliance titles (`information`, `security`,
  `management`, `data`, `iso`, `iec`, `ensure`, `ensuring`,
  `processing`) via new `_TITLE_META_NOISE` set.
- **`_augment_with_anchor(kw_set, anchors)`** — appends one
  anchor token per keyword set. No-op when the set already
  contains an anchor. Preserves set narrowness by adding just
  ONE token, not the full anchor list.
- **`_build_keyword_sets()`** — extended with a `topic_anchors`
  parameter that flows through to `_augment_with_anchor`.
- **`fetch_27701_leaves()`** — extended to fetch parent
  `RequirementNode.title` alongside the ChecklistItem rows.
- **`_is_auto_generated(path)`** — safety guard checks the
  file's first 6 lines for the `# Auto-generated` marker.
  Hand-authored files (marked "Reviewed-from-skeleton" or
  similar prose) stay untouched unless `--force` is passed.
- **CLI flags**: `--family SUBSTR` (regenerate only leaves
  whose slug contains substring); `--force` (override the
  hand-authored guard, with warning).

### Regenerated files

- **49 program_review YAMLs** (ISO 27701 A.7.x + B.8.x)
- **49 applicable_scope YAMLs** (ISO 27701 A.7.x + B.8.x)
- Total: **98 files regenerated**, 0 hand-authored files
  overwritten.

## Verification (pre / post audit comparison)

Re-ran `scripts/audit_fingerprints.py`:

| Metric | Pre-17'.b | Post-17'.b | Delta |
|---|---|---|---|
| `multi_noise_only` (3+ tokens, all noise) | 50 | 2 | **-48 (96%)** |
| `loose_pair_noise_only` (2 tokens, all noise) | 62 | 8 | **-54 (87%)** |
| `loose_pair_one_signal` (2 tokens, 1 signal) | 204 | 135 | -69 (34%) |
| `one_signal_padded` (3+ tokens, 1 signal) | 92 | 193 | +101 (by design*) |
| Cross-leaf collisions (≥2 tokens, >1 leaf) | 338 | 336 | -2 |
| **Would trigger Ship 16'.b gate (>5 leaves)** | **44** | **19** | **-25 (57%)** |

*The `one_signal_padded` increase is BY DESIGN: sets that were
`[review, date]` (2 noise tokens) become `[review, date,
contracts]` (2 noise + 1 anchor) — the anchor moves the set
from the "loose_pair_noise_only" class into the "padded" class,
which is FAR MORE SPECIFIC per-leaf.

**Key headline**: 25 of the 44 gate-triggering token sets were
27701 leaves (program_review + applicable_scope families). All
25 are now fully leaf-distinctive. The remaining 19 gate-
triggering sets are ALL ISO 27001 program_reviews (Ship 17'.c
target).

**Worst-case fanout dropped 3×**: pre-17'.b's `[identity,
reviewer]` fired on 64 leaves; post-17'.b's top offender
`[date, review]` fires on 20 leaves (all ISO 27001).

## Sample regenerated fingerprints

Same MUST id (`rev_date`) across three leaves — before all
shared `[review, date, planned, interval]`; now leaf-distinctive:

- `A.7.2.1:rev_date` → `[review, date, planned, interval, identify]`
  (title: "Identify and document purpose")
- `A.7.2.6:rev_date` → `[review, date, planned, interval, contracts]`
  (title: "Contracts with PII processors")
- `A.7.4.7:rev_date` → `[review, date, planned, interval, retention]`
  (title: "Retention")

Every 27701 leaf now has a distinct anchor. The 48-leaf
collision on `[review, date, planned, interval]` is entirely
broken up.

## Ship 14'.a addendum alignment

Not directly applicable (curator arc, no product surface). But
the 4 checks:

1. **Role split?** N/A — regenerator operates on ISO 27701
   catalog data; program-parallel ISO 27001 handled by Ship 17'.c.
2. **Parallel CaseFile view?** N/A — catalog data.
3. **Deterministic routing?** YES — regenerator is pure
   deterministic transform of Neo4j titles → anchor tokens.
4. **Guidance-normative discipline?** Preserved — anchor tokens
   are DATA descriptors of leaf topic, not new MUSTs.

## What did NOT ship

- **ISO 27001 program_review + applicable_scope regeneration**
  — Ship 17'.c scope. The remaining 19 gate-triggering
  collisions are all ISO 27001; the regenerator needs its
  Neo4j fetch extended to include `standard_id='ISO27001:2022'`
  or a new generator per-standard.
- **`single_token` class fix (556 remains)** — single-token
  fingerprints come from MUST id slugs that strip to 1
  meaningful token after prefix noise removal. These bypass
  the auto-generator's `_MIN_SET_SIZE = 2` because they
  ALREADY have 2 non-noise tokens BEFORE the strip. Fixing
  this would require a broader generator rewrite; deferred.
- **Backfill on live tenant** — the regenerated catalog affects
  future extractions only. Ship 17'.d will re-run
  `scripts/measure_ship11_reextraction.py` to observe the
  impact.

## Ship 17 progress

| Sub-arc | Status |
|---|---|
| 17'.a Regeneration strategy + generator audit | ✓ |
| **17'.b Fix generator + regenerate worst-offender families** | **✓ (this doc)** |
| 17'.c Regenerate remaining families + verify against gates | next |
| 17'.d Measurement + arc retrospective | pending |

## Related

- [[ship-17-prime-a-regeneration-design-2026-07-23]] — design
  memo whose plan this arc executes
- [[ship-16-prime-a-fingerprint-audit-2026-07-22]] — the audit
  tooling used for verification
- [[ship-16-prime-b-specificity-gate-2026-07-22]] — the runtime
  gate whose drop count 17'.b is reducing
- Ship 17'.c: extend regenerator to ISO 27001 auto-generated
  families
