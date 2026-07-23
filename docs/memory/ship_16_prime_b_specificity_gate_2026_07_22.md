---
name: ship-16-prime-b-specificity-gate-2026-07-22
description: "Ship 16'.b — extraction-time specificity gate on fingerprint token sets; blocks 44 auto-generator template collisions"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 16'.b (2026-07-22) — second sub-arc of Ship 16. Delivers
the extraction-time specificity gate designed in 16'.a.
Structural fix for the 338 cross-leaf token-set collisions the
audit surfaced.

## What ships

### New in `rag/intake/extractor.py`

**`_get_token_set_specificity()`** — lazy cache that builds
`{frozenset(tokens): leaf_count}` from the fingerprint catalog
at first use. Populated from the same `_get_leaf_fingerprint_index()`
call as everything else, so no additional catalog load. Silent-
fail on error (empty dict → gate no-ops).

Load-time log line:
```
token-set specificity index: 7437 unique sets,
44 shared across >5 leaves (will trigger specificity drops)
```

**`_SPECIFICITY_THRESHOLD = 5`** — token sets defined across
more than 5 leaves are considered auto-generator template
collisions and rejected. Threshold matches 16'.a design memo:
program_review families have 3-6 leaves per control × 3-6
controls per family, so sets shared across >5 leaves are the
templated shape rather than real per-leaf specificity.

**Gate wired into `_extract_via_fingerprints`** BEFORE quote
extraction — cheap dict lookup, short-circuits rejected matches:

```python
matched_kw = m.get("matched_kw") or []
if matched_kw and specificity:
    kw_key = frozenset(str(t).lower() for t in matched_kw)
    leaf_count = specificity.get(kw_key, 1)
    if leaf_count > _SPECIFICITY_THRESHOLD:
        dropped_specificity_fp += 1
        continue
```

Gate falls through (never blocks) when:
- Specificity index is empty (load failure)
- Token set isn't in the index (edge case — e.g. hand-authored
  fingerprint added after catalog load)
- `matched_kw` is empty on the match record

**New telemetry** `dropped_low_specificity` alongside Ship
11'.c's `dropped_content_shape` + Ship 11'.d's
`dropped_semantic_fit`. Kept as a standalone counter (new class
of drop, not accumulated with any prior). Log line at
extraction close now shows:

```
fingerprint extraction for X: N findings on L leaves
(dropped_shape=X dropped_specificity=Y)
```

## Verification

Smoke test against real catalog (2595 fingerprints × 506 leaves):

**Distribution — 92% of token sets are already unique:**

| Leaf count bucket | Token set count |
|---|---|
| 1 leaf (unique) | 6,859 (92%) |
| 2-3 leaves | 472 |
| 4-5 leaves | 62 (borderline) |
| 6-10 leaves (dropped) | 29 |
| 11-30 leaves (dropped) | 13 |
| > 30 leaves (dropped) | 2 |

**Total token sets triggering drops: 44 out of 7,437 (0.6%).**
Precise, not broad-brush.

**Ship 11'.f target verification:**

| Token set | Leaves | Verdict |
|---|---|---|
| `[identity, reviewer]` | 64 | **DROP** ← worst offender |
| `[date, interval, planned, review]` | 48 | **DROP** ← program_review family |
| `[exclusions, scope]` | 17 | **DROP** ← applicable_scope family |
| `[coverage, check]` | 9 | **DROP** |
| `[subprocessor, audit]` | 2 | keep — surprise (see below) |
| `[processing, activity]` | 4 | keep |

## Surprise finding — 16'.c is still needed

`[subprocessor, audit]` only fires on 2 leaves — the very
match Ship 11'.f flagged as producing the A.7.2.6 → A.5.19/20/22
bridge fanout does NOT fail the specificity gate. That means
the fanout wasn't a token-collision problem; it was a
legitimate 2-leaf match producing OFF-target cross-family
bridges.

Same for `[processing, activity]` (4 leaves) — legitimate
RoPA-shape match that shouldn't bridge to A.5.9 asset
register.

**This confirms Ship 16'.c is necessary**: the specificity
gate catches template-collision noise (the biggest structural
class), but the bridge-fanout patterns Ship 11'.f flagged
require a separate fix at the bridge-proposal layer
(substantiveness gate — require ≥2 satisfied MUSTs on source
before proposing bridge).

Two-layer fix confirmed by the smoke test:
- **Layer A (16'.b)**: template-collision noise (44 offenders,
  ~40 program_review + applicable_scope families) — DONE
- **Layer B (16'.c)**: single-MUST bridge fanouts (Ship 11'.f's
  specific 4 patterns) — NEXT

## Ship 14'.a addendum alignment

Not directly applicable — this is a hardening arc on the
intake pipeline, not a new product surface. But the 4 checks:

**1. Role split?** N/A — the gate is standard-agnostic. Token-
set collisions span program (ISO 27001) + extension (ISO
27701) equally.

**2. Parallel CaseFile view?** N/A — extraction path, not chat.

**3. Deterministic routing?** YES — pure dict lookup on
`frozenset(tokens)`. No LLM inference in the gate.

**4. Guidance-normative discipline?** Preserved — the gate
drops OVER-attribution, keeping engine verdicts based on real
matches only. Never adds MUSTs.

## What did NOT ship

- **Per-leaf `min_specificity` override in yaml** — a curator
  might legitimately want to mark a specific hand-authored
  fingerprint as "yes I know this token set is broad, but
  it's intentional for this leaf". Deferred to a follow-up if
  the gate false-blocks anything meaningful.
- **Catalog regeneration** — not touching
  `generate_27701_fingerprints.py` in this arc per the 16'.a
  design memo. A curator arc that targets the generator (audit
  + re-emit per-family) is a Ship 17+ candidate.
- **Similar gate for the LLM path** — the LLM path uses
  `_run_critic_verifier_pass` with its own semantic-fit gate
  (Ship 11'.d). Cross-applying the token-set specificity to
  the LLM path would require different plumbing (LLM emits
  refs, not matched_kw); deferred.

## Ship 16 progress

| Sub-arc | Status |
|---|---|
| 16'.a Fingerprint audit + design memo | ✓ |
| **16'.b Extraction-time specificity gate** | **✓ (this doc)** |
| 16'.c Bridge source-substantiveness gate | next |
| 16'.d Re-extraction measurement + retro | pending |

## Related

- [[ship-16-prime-a-fingerprint-audit-2026-07-22]] — the audit
  whose 338 cross-leaf collisions this gate addresses
- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc
  whose Pattern 2 root-cause Ship 16 is delivering
- [[ship-11-prime-c-content-shape-filter-2026-07-20]] — the
  peer telemetry counter (dropped_content_shape) that
  dropped_low_specificity sits alongside
- [[ship-11-prime-d-critic-prompt-enhancement-2026-07-21]] —
  the semantic-fit gate on the LLM path (dropped_semantic_fit)
- Ship 16'.c: bridge substantiveness gate (require ≥2 satisfied
  MUSTs before proposing bridge) — closes the remaining Ship
  11'.f fanout patterns
