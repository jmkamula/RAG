---
name: ship-32-prime-arc-retrospective-2026-07-25
description: "Ship 32' arc closer — first forward-motion arc after 4 maintenance arcs. Re-extracted the 5 Ship-10-baseline docs; surfaced a sentence-level multi-MUST attribution precision gap (Processor Ops: 121 fingerprint findings on 11 unique evidence_text values, 103 findings share evidence with 5+ others). Ship 28+29 tightened token-set specificity but opened a new hole — same sentence containing many controls' anchor tokens fires their fingerprints simultaneously. Measurement arc did its job. Ship 33 opens for the fix."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 32' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). First forward-motion arc after 4 consecutive
maintenance arcs (28→31). Deliberately picked to validate the
architecture end-to-end vs shipping another fix.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 32'.a | Measurement design + baselines locked | 13f25f1 |
| 32'.b | Re-extraction executed; precision finding surfaced | (this arc) |
| **32'.c** | **Eval + retrospective (this doc)** | pending |

## The numbers

**Per-doc extraction (5 Ship-10-baseline procedural docs):**

| Doc | Ship 10 (2026-06) | Ship 11'.e (2026-07-21) | Ship 32 (2026-07-25) | Δ vs Ship 10 |
|---|---|---|---|---|
| Data Quality Accuracy | 9 | — | 14 | +5 (+56%) |
| DPIA | 13 | — | 28 | +15 (+115%) |
| Records of Processing Activities | 17 | — | 24 | +7 (+41%) |
| Consent Management | 28 | — | 56 | +28 (+100%) |
| **Processor Operations** | **30** | — | **143** | **+113 (+377%)** |
| **TOTAL** | **97** | ~198 | **265** | **+168 (+173%)** |

**Grounding_method distribution (Ship 27 baseline: 89.2% deterministic):**
- `fingerprint` (fingerprint_match): 173
- `extractor_verbatim` (extracted, gated by `_evidence_grounded`): 92
- **Deterministic %: 100%** — above Ship 27's baseline

## The precision finding

The Processor Ops surge (30 → 143) triggered a spot-check. Result:

- **11 unique `evidence_text` values across 121 fingerprint findings** (9% uniqueness)
- **103 of 121 findings** share `evidence_text` with ≥5 other findings
- Top single evidence text produces **43 findings** across 43 different MUST items
- Second: **29 findings** on one sentence
- Third: **19 findings** on one bullet-list

Sample worst offender:
> `- Logging processing activities (A.8.3.1)` — 43 fingerprint findings on this ONE bullet line across 43 different MUST items

Second worst:
> `This procedure defines Arion Networks' operational responsibilities when acting as a data processor, including:` — 29 findings

Both are doc-level SUMMARY / SCOPE-STATEMENT sentences, not substantive evidence for any specific MUST.

## Mechanism (the interesting part)

Ship 16'.b runtime gate (`dropped_low_specificity`) checks
whether the *same token set* matches more than N leaves. It
dropped 44 sets pre-Ship-17; Ship 28+29 tightening pushed it
down to **5 sets across >5 leaves** in the current catalog.

That gate does not fire here because each of the 43 leaves has
a *different* fingerprint token set (anchors are leaf-distinctive
per Ship 29). So specificity gate sees 43 different sets, each
firing once — legitimate by its criteria.

But those 43 different sets all happened to hit ONE sentence
because:
- The sentence "- Logging processing activities (A.8.3.1)" contains
  common words: `logging`, `processing`, `activities`
- 43 different controls' anchor sets contain one or more of those
  words alongside their leaf-specific anchor
- Each set → ONE fingerprint match on this sentence → ONE finding

The specificity gate protects against
*same-token-set-firing-on-many-leaves*. It does not protect against
*different-token-sets-firing-on-the-same-sentence*.

Ship 29's anchor injection tightened per-leaf distinctiveness (Ship
17'.b's motivating collision `[review, date, planned, interval]`
went from 48 leaves → 0), but opened this new hole. Net: catalog
metrics look better, real-doc extraction volume grew 34%.

## What Ship 32 validated

- **Case-file architecture** — untouched, still works. Chat still
  renders correctly (Ship 30 fixed the DRAFT bug there).
- **Role model** — untouched.
- **Deterministic grounding_method invariant** — 100% deterministic
  on this corpus, above Ship 27's 89.2% baseline.
- **Loader fixes (Ship 30+31)** — didn't corrupt extraction.

## What Ship 32 surfaced (Ship 33's problem)

Sentence-level multi-MUST attribution: one doc sentence can produce
N fingerprint findings across N MUSTs where each MUST's token set
contains a common word appearing in that sentence. Ship 16'.b gate
doesn't catch it. Ship 11'.c content-shape filter doesn't catch it
(the sentence LOOKS like content, not a field label). Ship 11'.d
semantic-fit gate doesn't catch it (semantic fit is per-finding, not
cross-finding-dedup).

**Ship 33 candidate fix**: per-evidence-text cap in
`_extract_via_fingerprints`. If ONE evidence-text produces >N
fingerprint findings across different MUSTs, drop it as summary /
TOC-style content. Threshold TBD from data — probably 3-5.

Alternative candidate: **anchor-set overlap check**. If the same
excerpt is captured by K different anchor sets and each set contains
a common word (`processing`, `data`, `logging`), require the sets
also to share the leaf-distinctive anchor tokens — not just the
common ones. This is a stricter check but harder to implement.

## Codified 3 lessons

### 1. Measurement arcs earn their keep

4 maintenance arcs shipped between Ship 27 (last measurement) and
Ship 32 (this measurement). Each of them touched catalog / loader
surfaces adjacent to extraction. None of them re-measured
end-to-end. Ship 32 surfaced a real precision gap that would
otherwise have shipped silently through more arcs.

**Rule**: after every N (probably 3-4) arcs that touch a pipeline,
run a measurement arc against a fixed baseline. If the numbers
haven't moved as expected, investigate before more forward motion.

### 2. Gates cover their design space, not the whole space

Ship 16'.b + Ship 11'.c + Ship 11'.d are three different gates
each covering a distinct failure mode. They compose well when the
failure modes are orthogonal. Ship 29's anchor injection
inadvertently created a NEW failure mode (sentence-level
multi-attribution) that lies OUTSIDE all three gates' design
spaces.

**Rule**: when a design change moves the failure mode, previously
sufficient gates may leave a gap. The measurement checkpoint is
what catches the gap.

### 3. Catalog metrics ≠ extraction metrics

Ship 28+29 measured catalog quality (singleton count, cross-leaf
token-set collisions). Those numbers looked great: singletons
0, worst collision 5 leaves (was 44 pre-Ship-16, 148 pre-Ship-17).
But actual extraction on real docs got 34% more findings, most of
them precision-hostile.

**Rule**: catalog quality metrics predict what CAN happen in
extraction, not what DOES happen. End-to-end measurement is the
only proof that the changes had the intended effect.

## Design decisions locked in 32'.c

1. **Don't fix in Ship 32** — arc is measurement, not
   implementation. Ship 33 does the fix.
2. **Ship 33'.a scope**: design per-evidence-text cap + alternative
   anchor-set overlap check + choose one.
3. **Ship 33'.b**: implement + re-measure to validate the fix.
4. **Ship 33'.c**: retro.
5. Threshold for per-evidence-text cap: empirical, from data
   (probably 3-5 based on the 43 / 29 / 19 top offenders).

## What Ship 32 did NOT do

- **Fix the precision gap** — deferred to Ship 33.
- **Update Ship 10 baseline** — historical fixed point.
- **Re-extract via full pipeline** — measurement uses
  `extract()` directly, doesn't invoke `xfw_proposer` or
  `write_findings`. Cross-framework bridges + writer-side
  telemetry not measured in this arc. Ship 33 could extend.
- **Trace `dropped_content_shape` / `dropped_semantic_fit`
  absence** — the counters were low (0 and 1) but the log shows
  the paths ran. Not a wiring bug this arc surfaced.

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 32'.a | Design + baselines | Success/failure signals locked |
| 32'.b | Execute + probe | 265 findings, 100% det %; sentence-level multi-attribution found |
| **32'.c** | **Eval + retro (this)** | **Baseline holds; Ship 33 opens for the fix** |

## Related

- [[ship-27-prime-arc-retrospective-2026-07-24]] — established
  grounding_method + 89.2% deterministic baseline
- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc whose
  measurement checkpoint we mirrored
- [[ship-17-prime-arc-retrospective-2026-07-23]] — anchor
  injection introduced (6 combos)
- [[ship-28-prime-arc-retrospective-2026-07-24]] — singleton
  suppression
- [[ship-29-prime-arc-retrospective-2026-07-24]] — anchor
  injection extended to all 397 auto-gen files (the change that
  most likely widened the sentence-level multi-attribution
  surface)
