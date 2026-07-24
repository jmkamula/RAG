---
name: ship-28-prime-a-singleton-fix-design-2026-07-24
description: "Ship 28'.a — design memo for the single-token fingerprint fix; generator emits redundant singletons alongside multi-token alternatives, causing 976 low-specificity keyword sets across the catalog"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 28'.a — opens Ship 28 arc (single-token fingerprint
fix). Deferred from Ship 17. Direct follow-on to Ship 27's
finding that `grounding_method` is the quality signal —
Ship 28 improves the fingerprint layer to shift more findings
into the deterministic `fingerprint` bucket.

## The problem — concrete counts

Ship 16'.a's audit + Ship 27's grounding-method audit both
surfaced the single-token fingerprint noise class:

- **472 single-token groups** (per `scripts/audit_
  fingerprints.py`, "single_token" class = a `tokens` list
  with exactly 1 element).
- **976 single-token `excerpt_keywords` entries** across all
  YAML files (a MUST item can have multiple single-token
  keyword sets — the audit classifies by group; the raw
  YAML count is nearly 2x).

Sample from `req_6_1_2_risk_assessment.yaml`, item
`item:6.1.2:consistency`:
```yaml
- must_id: "item:6.1.2:consistency"
  description: "Consistent and comparable results produced"
  excerpt_keywords:
    - [consistency]                          ← id-token singleton
    - [consistent]                           ← description singleton
    - [consistent, comparable]               ← bigram (OK)
    - [consistent, comparable, results]      ← trigram (OK)
    - [comparable]                           ← description singleton
    - [comparable, results]                  ← bigram (OK)
    - [comparable, results, produced]        ← trigram (OK)
    - [results]                              ← description singleton
```

Four multi-token keyword sets for this item, plus four
single-token variants. The singletons `[consistent]`,
`[comparable]`, `[results]` are covered by the bigrams
+ trigrams — they just create false-positive matches for
any document containing those common words.

## Root cause — `scripts/gen_leaf_scan_catalog.py`

Two functions produce singletons unconditionally:

1. **`_starter_excerpt_keywords()`** — step 2 iterates
   `id_tokens` (parsed from the MUST item id, minus role
   prefix). For `item:6.1.2:consistency` → `id_tokens =
   ['consistency']`. Then:
   ```python
   for t in id_tokens:
       if t not in _NEVER_EMIT_SINGLETON:
           _add([t])
   ```
   `consistency` isn't in the block-list → emits `[consistency]`.

2. **`_phrases_from_description()`** — for each token in the
   description (after stopword removal):
   ```python
   if t not in _NEVER_EMIT_SINGLETON:
       out.append([t])
   ```
   Emits `[consistent]`, `[comparable]`, `[results]` etc.

`_NEVER_EMIT_SINGLETON` (60+ tokens) catches the worst
offenders (`user`, `account`, `date`, `password`, `owner`,
etc.) but leaves 400+ "medium-generic" tokens that shouldn't
be singletons either.

## The fix — last-resort singleton emission

**Rule**: emit singletons ONLY when the item's total keyword
set list contains no 2+ token alternatives.

For `item:6.1.2:consistency` (description "Consistent and
comparable results produced"):
- Bigrams available: `[consistent, comparable]`,
  `[comparable, results]`, `[results, produced]`
- Trigrams available: `[consistent, comparable, results]`,
  `[comparable, results, produced]`
- → **drop all singletons** (bigrams+trigrams cover the
  same content with better specificity)

For a hypothetical item with description "Owner":
- Bigrams available: none
- Trigrams available: none
- → keep `[owner]` singleton as last-resort safety net
- (In practice, `owner` is in `_NEVER_EMIT_SINGLETON` so
  even this fallback is suppressed. Edge case is only
  triggered for items with a single non-blocked token.)

## Fix in code

Modify `_starter_excerpt_keywords`:
1. Build the list normally (as today).
2. Before returning, compute `has_multi = any(len(s) >= 2
   for s in suggestions)`.
3. If `has_multi is True` → filter out all `len(s) == 1`
   entries.
4. Else → keep singletons (last-resort safety net).

This is a **surgical 5-line change** in one function. No
signature changes, no other-file impact.

## Regenerate scope

`_is_auto_generated(path)` helper from Ship 17'.b checks
first 6 lines for `# Auto-generated` marker. Ship 28'.b
runs the generator across all leaves, updating only
auto-generated files. Hand-authored files (Ship 16'.a's
inventory: 246 files) stay untouched.

Expected outcome:
- **472 single-token groups → near-zero** (only items with
  truly no multi-token alternatives keep them)
- **~976 single-token YAML entries → ~50-100** (last-resort
  safety net items)
- **Catalog gate triggers** (Ship 16'.b runtime specificity
  gate `>5 leaves`) → further reduced, since the removed
  singletons are the biggest cross-leaf offenders

## Ship 27 audit re-run — expected impact

Ship 27's `audit_finding_quality.py` reports grounding_method
distribution. Post-Ship-28 expectations on Ship 10 5-doc corpus:

- **fingerprint** count: possibly SLIGHTLY LOWER (fewer weak
  singletons will fire during extraction; the strict matches
  stay).
- **extractor_verbatim**: possibly slightly higher (some
  content that used to be caught by weak singletons now falls
  through to LLM path).
- **Overall determinism**: expected to STAY ≥89% since Ship 16'.b's
  runtime gate was already dropping >5-leaf matches. Ship 28
  moves the fix upstream to the catalog rather than
  filtering at runtime.

The measurement matters: if extraction volume drops
significantly, Ship 28 was too aggressive. If it stays flat
or grows, Ship 28 improved catalog signal without losing
recall.

## Design decisions locked in 28'.a

1. **Suppress redundant singletons only** — never
   unconditionally. Items with only a single distinctive
   token (rare edge case) keep their singleton as last-
   resort safety net.

2. **Fix in generator, not curator files** — regenerate the
   catalog rather than hand-edit ~250 YAML files. Ship 17'.b
   established this pattern; Ship 28 extends it.

3. **Respect `_is_auto_generated` guard** — hand-authored
   files (246 out of 598 per Ship 16'.a inventory) stay
   untouched.

4. **No changes to `_NEVER_EMIT_SINGLETON`** — that block-
   list is a targeted list of always-bad tokens (like
   `owner`, `date`). Ship 28's algorithmic fix handles the
   redundant-singleton case; the block-list keeps its
   role for always-bad tokens.

5. **Measurement via Ship 27's tool** — reuse
   `audit_finding_quality.py` to verify grounding_method
   distribution stays healthy. Cross-run before/after.

## Sub-arc plan

### 28'.b — Implement + regenerate

- `scripts/gen_leaf_scan_catalog.py::_starter_excerpt_
  keywords` — 5-line change to filter singletons when
  multi-token alternatives exist.
- Run the generator across all auto-generated leaves.
  Expected diff: many YAML files change (drop singleton
  entries).
- Re-run `audit_fingerprints.py`. Expect single_token
  class 472 → near-zero.
- Re-run `audit_cross_role_edges.py` (should be
  unaffected — Ship 28 doesn't touch relationship_catalog).
- Re-run `audit_finding_quality.py` for Ship 10 5-doc
  corpus. Compare fingerprint / extractor_verbatim / total
  counts to Ship 27 baseline.

### 28'.c — Eval + retro

- Full eval regression check.
- Interpret grounding_method delta.
- Retrospective codifying the "redundant emission is worse
  than absent emission" pattern for generator design.

## What Ship 28 does NOT do

- **Fix multi_noise_only / loose_pair_noise_only** — the
  6 + 9 findings in those classes require semantic surgery,
  not algorithmic.
- **Fix `loose_pair_one_signal`** — the 136 findings in
  this class have 2 tokens of which 1 is noise. Filtering
  by "at least one signal per set" is a separate discipline
  decision (could suppress valid short items).
- **Extend `_NEVER_EMIT_SINGLETON`** — the algorithmic fix
  handles the problem class more broadly.
- **Hand-edit any YAML file** — regenerator only touches
  auto-generated files.
- **Change the runtime `_CROSS_ROLE_SECTION_CAP` or
  Ship 16'.b's specificity gate** — those are downstream
  belts-and-suspenders. Ship 28 improves upstream signal.

## Ship 28 progress

| Sub-arc | Status |
|---|---|
| **28'.a Design memo (this)** | **✓** |
| 28'.b Generator fix + regenerate + verify | next |
| 28'.c Eval + retrospective | pending |

## Related

- Ship 16'.a — the fingerprint audit that first surfaced
  the 556 (now 472) single-token class
- Ship 17'.b — the auto-gen provenance guard
  (`_is_auto_generated`) Ship 28 reuses
- [[ship-27-prime-arc-retrospective-2026-07-24]] — the
  quality-audit arc that established `grounding_method`
  as the quality signal Ship 28 measures against
