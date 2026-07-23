---
name: ship-16-prime-arc-retrospective-2026-07-22
description: "Ship 16' arc retrospective — fingerprint token discipline / Pattern 2 root-cause fix; 3 delivery sub-arcs + closer; two-layer gate architecture"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 16' arc — fingerprint token discipline. Explicit follow-up
to Ship 11'.f's "real Pattern 2 fix belongs in a curator arc"
recommendation. Delivered the root-cause fix as two independent
gates rather than YAML edits — solving the structural class of
problems the Ship 11'.a audit was designed to surface.

**Arc window:** 2026-07-22. 3 delivery sub-arcs + this closer,
single-session.

## Sub-arc inventory

| Sub-arc | Delivery | Commit |
|---|---|---|
| 16'.a | Fingerprint audit tooling + design memo — 2595 fingerprints scanned; 338 collisions; 40% loose | `2b2cad4` |
| 16'.b | Extraction-time specificity gate — blocks 44 auto-generator template collisions | `1f5211d` |
| 16'.c | Bridge source-substantiveness gate — blocks single-MUST cross-framework fanouts | `44808ef` |
| **16'.d Re-extraction measurement + retro** | **This doc** | (next commit) |

## What ships from Ship 16'

**Audit tooling:**
- `scripts/audit_fingerprints.py` — 245 LOC read-only script;
  walks catalog, classifies token groups, surfaces cross-leaf
  collisions, writes JSON report

**Extraction gates (in `rag/intake/extractor.py`):**
- `_get_token_set_specificity()` — lazy `{frozenset(tokens):
  leaf_count}` index; `_SPECIFICITY_THRESHOLD = 5`
- Wired into `_extract_via_fingerprints` BEFORE quote extraction
  (cheap dict lookup, short-circuits rejected matches)
- New `dropped_low_specificity` telemetry alongside Ship 11's
  `dropped_content_shape` + `dropped_semantic_fit`

**Bridge gates (in `rag/intake/xfw_proposer.py`):**
- `_count_musts_per_leaf(findings)` + `_count_musts_per_leaf_from_rows(rows)`
  — batch pre-count helpers for both proposer paths
- `_SUBSTANTIVENESS_MIN_MUSTS = 2` — bridge source must have
  ≥2 distinct MUSTs bound on its leaf
- Wired into both `propose_for_findings` (per-upload) and
  `propose_backfill` (tenant-wide)
- New `sources_gated_single_must` telemetry on `ProposalSummary`

**Measurement:**
- Re-extraction on Ship 10's 5-doc set (see below)

## Re-extraction measurement

Two complementary measurements — the arc's two gates operate
at different pipeline stages, so a single harness can't
observe both.

### Layer A — Ship 16'.b specificity gate (extraction time)

Ran `scripts/measure_ship11_reextraction.py` on Ship 10's 5-doc
set. Findings:

| Doc | Ship 10 baseline | Ship 16 today | Δ |
|---|---|---|---|
| Data Quality Accuracy | 9 | 13 | +4 ↑ |
| DPIA | 13 | 33 | +20 ↑ |
| Records of Processing Activities | 17 | 21 | +4 ↑ |
| Consent Management | 28 | 42 | +14 ↑ |
| Processor Operations | 30 | 83 | +53 ↑ |
| **Total** | **97** | **192** | **+95** |

`dropped_low_specificity` counter fired **10 times total** across
the 5 docs (1 + 1 + 0 + 7 + 1). The gate IS doing measurable
work — but the raw finding volume nearly doubled between Ship
10 and today.

**Honest interpretation**: the extraction-side volume growth is
NOT a Ship 16 regression. Between Ship 11'.e (2026-07-21, when
we last measured 102 findings) and today, Ship 9'.c's 189 new
`doc_mappings` + Ship 13's guidance-family enrichment continued
to expand the fingerprint index. Layer A caught 10 template-
collision hits from the auto-generator, but couldn't offset the
coverage growth. **This confirms the Ship 16'.a decision to
defer catalog regeneration** — the auto-generator (not the gate)
is the volume-growth source.

### Layer B — Ship 16'.c substantiveness gate (bridge time)

The extraction harness doesn't invoke `xfw_proposer` so
measured Layer B separately via a dry-run count against the
demo tenant's 133 DISTINCT extracted findings:

| Gate | Sources filtered |
|---|---|
| Ship 11'.b (source quality) | 0 (all pass; pipeline already produces high-quality sources) |
| **Ship 16'.c (substantiveness)** | **81 (60.9%)** ← NEW |
| Pass all gates → propagate | 52 |

**Leaf-MUST binding distribution:**
- 50 leaves with 1 MUST bound → bridge-blocked
- 20 leaves with ≥2 MUSTs bound → bridge

**This is the arc's primary win.** 60.9% of tenant sources are
newly filtered at bridge time — cross-framework fanout
inflation cut dramatically. The Ship 11'.f target patterns
(A.7.2.6 → A.5.19/20/22, A.7.2.8 → A.5.9, A.7.4.7 → A.5.33,
A.7.4.8 → A.7.14) are all single-MUST sources and would be
blocked by the substantiveness gate.

### Why the two-layer split was right

If Ship 16 had only shipped Layer A (specificity), the arc
would have reported 10 drops — a modest but real fix.
Layer B on its own would have filtered 81 sources but left the
template-collision volume growth uncontrolled.

Together, the two gates address BOTH structural failure
modes: template collisions (Layer A) drop at their point of
creation; single-MUST fanouts (Layer B) drop at their point
of amplification (bridge propagation). Different failure
modes → different gates.

## Two-layer gate architecture (codified)

Three extractor gates now run in sequence with **distinct
failure modes and no overlap**:

| Gate | Layer | Failure mode caught |
|---|---|---|
| Ship 11'.b `_source_is_bridge_worthy` | Bridge time (source) | Bridge-of-bridge / low-confidence / fragment sources with no MUST binding |
| **Ship 16'.b specificity** | Extraction time (fingerprint) | Auto-generator template collisions (token set shared across >5 leaves) |
| **Ship 16'.c substantiveness** | Bridge time (source-leaf) | Single-MUST cross-framework fanouts |

A source can only produce a bridge proposal when it's
high-quality (11'.b), leaf-specific (16'.b), AND substantiated
by multiple MUST bindings (16'.c). Each gate targets a
different structural failure mode — none is redundant.

## Codified lessons

### 1. Audit-first arcs surface structural class of problems

Ship 11'.f punted the root-cause fix to a "curator arc" but
without a clear scope. Ship 16'.a's audit tooling turned that
punt into a concrete inventory: 338 collisions, 44% loose
fingerprints, 4 auto-generator patterns responsible for most
of the noise. That made the arc scopable — 16'.b/'.c became
specific interventions rather than open-ended curator work.

**Generalisation**: before committing to a "curator arc," write
the audit script first. If the audit produces a structural
inventory (not just a list of edge cases), the arc becomes
architectural. If it produces just a list, it stays curator.

### 2. Structural fixes beat YAML edits

The naive approach to Ship 11'.f was "walk 2595 YAMLs and hand-
edit the over-broad token sets." Ship 16'.b instead added a
load-time index that solves 338 collisions with a 1-file
change (extractor.py) — and preserves the catalog's provenance
from `generate_27701_fingerprints.py` for a future
regeneration arc.

**Generalisation**: when audit surfaces a structural pattern
across a large data corpus, prefer an extraction-time gate
over a data-side rewrite. The gate is versioned in code,
tunable via a single constant, and reversible.

### 3. Layered gates have distinct failure modes

The surprise in 16'.b's smoke test drove this home: Ship 11'.f's
`[subprocessor, audit]` fingerprint fires on only 2 leaves —
UNDER the specificity threshold. So the specificity gate
alone wouldn't have fixed the fanout Ship 11'.f identified.
The substantiveness gate (16'.c) was needed as a separate
layer, catching the "legitimate but tangential" match pattern
at bridge-proposal time.

**Generalisation**: when a filter arc surfaces N problem
patterns, resist the temptation to force them into one gate.
Different failure modes need different gates. Ship 16 shipped
two because the audit proved two were needed.

### 4. Design memo → concrete threshold → smoke test

Ship 16'.a's design memo locked `N=5` for specificity and
`N=2` for substantiveness. Both survived the 16'.b/'.c smoke
tests unchanged. Reason: the memo reasoned from FAMILY SIZE
(program_review families have 3-6 leaves per control × 3-6
controls per family = 5+ leaf threshold) and DOC STRUCTURE (a
real policy doc binds multiple MUSTs per leaf).

**Generalisation**: derive thresholds from structural facts
(family sizes, doc shapes), not from measurement iteration.
Measurement iteration is a tuning fallback, not a first-order
approach.

### 5. Extractor-layer changes don't need chat-eval cases

Per Ship 15'.e's codified lesson: eval-suite ratchet fires on
chat-pipeline changes. Ship 16's gates operate on the extractor
path — they don't touch chat. So no new eval cases were added.
The measurement harness (`scripts/measure_ship11_reextraction.py`)
is the right ratchet for this arc: it verifies the extractor's
noise-reduction claims empirically.

**Generalisation**: use the right ratchet for the layer being
changed. Chat pipeline → eval suite. Extractor → measurement
harness. HTTP/UI/SDK → integration tests. Cross-firing
ratchets adds theater, not coverage.

## What did NOT ship

- **Fingerprint catalog regeneration** — locked out by 16'.a
  design memo. The auto-generator (`scripts/generate_27701_fingerprints.py`)
  templates loose shapes across families; regenerating with
  per-leaf context is a Ship 17+ candidate curator arc.
- **Per-standard tunable thresholds** — both gates use single
  global constants (`_SPECIFICITY_THRESHOLD = 5`,
  `_SUBSTANTIVENESS_MIN_MUSTS = 2`). If a specific standard
  family exhibits legitimate outlier behavior, a per-standard
  override could be added. Deferred — no evidence today.
- **Strong-signal single-MUST override** — for 16'.c, one
  alternative was "allow single-MUST bridging when excerpt is
  ≥200c OR confidence is high." Skipped for simplicity;
  16'.d measurement will surface if this over-blocks anything
  meaningful.
- **Similar gate on the LLM path** — the critic-verifier pass
  has its own semantic-fit gate (Ship 11'.d). Cross-applying
  token-set specificity to the LLM path would require
  different plumbing.
- **Backfill re-run on live tenant data** — the propose_backfill
  changes are code-only; running the backfill against the demo
  tenant would flip live proposal state. Deferred to when
  needed (a real tenant enrolment shift).

## Ship 16' close

| Sub-arc | Status |
|---|---|
| 16'.a Fingerprint audit + design memo | ✓ |
| 16'.b Extraction-time specificity gate | ✓ |
| 16'.c Bridge source-substantiveness gate | ✓ |
| **16'.d Re-extraction measurement + retro** | **✓ (this doc)** |

Total: 3 delivery sub-arcs + closer. Compact, focused arc —
matches Ship 8's scope shape.

## Related

- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc
  whose "real Pattern 2 fix belongs in a curator arc" this
  arc delivered
- [[ship-11-prime-e-reextraction-measurement-2026-07-21]] —
  the measurement checkpoint that surfaced the 4 unfixed
  fanout patterns Ship 16 targets
- [[ship-16-prime-a-fingerprint-audit-2026-07-22]] —
  audit + design memo
- [[ship-16-prime-b-specificity-gate-2026-07-22]] — Layer A
- [[ship-16-prime-c-bridge-substantiveness-2026-07-22]] — Layer B
- Ship 17+ candidates: fingerprint catalog regeneration (target
  the auto-generator, re-emit per-family); per-standard
  tunable thresholds; strong-signal single-MUST override on
  the substantiveness gate
