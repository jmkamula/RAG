---
name: ship-16-prime-c-bridge-substantiveness-2026-07-22
description: "Ship 16'.c — bridge source-substantiveness gate; requires ≥2 satisfied MUSTs on source leaf before propagating cross-framework"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 16'.c (2026-07-22) — third sub-arc of Ship 16. Closes the
gap 16'.b uncovered: Ship 11'.f's 4 bridge-fanout patterns
weren't token-collision problems (their token sets fire on
just 2-4 leaves, under the 16'.b threshold) — they were
legitimate single-MUST matches producing OFF-target
cross-framework bridges.

The substantiveness gate closes this. Layer B of the two-layer
Ship 16 fix.

## What ships

### New in `rag/intake/xfw_proposer.py`

**`_count_musts_per_leaf(findings)`** — batch pre-count of
distinct `checklist_item_id`s per `(standard_id, control_ref)`.
Used by the per-upload path (`propose_for_findings`) which
receives DocumentFinding objects.

**`_count_musts_per_leaf_from_rows(rows)`** — same shape but
tuple-indexed for the backfill path. Row shape:
`(document_id, control_ref, standard_id, status, confidence,
 excerpt, checklist_item_id, inference_source)`.

**`_SUBSTANTIVENESS_MIN_MUSTS = 2`** — a legitimate policy doc
covers a control through multiple MUST bindings; a tangential
mention typically hits exactly one. Threshold 2 catches the
Ship 11'.f pattern without over-blocking.

**New telemetry** `sources_gated_single_must` on `ProposalSummary`,
alongside `sources_gated` (Ship 11'.b). Log line updated:
```
xfw_proposer[...]: sources=N gated=X single_must_gated=Y
edges=E written=W skipped=S targets=[...]
```

### Wired into both proposer paths

**`propose_for_findings`** (per-upload) — pre-loop
`must_counts = _count_musts_per_leaf(findings)`, then per-
source check after the Ship 11'.b gate:
```python
n_musts = must_counts.get((f.standard_id, f.control_ref), 0)
if n_musts < _SUBSTANTIVENESS_MIN_MUSTS:
    summary.sources_gated_single_must += 1
    continue
```

**`propose_backfill`** (tenant-wide) — same shape, uses the
row-based count helper. Backfill's DISTINCT ON means the count
is across DIFFERENT documents feeding the same (std, ref).
That's the right coverage: even if each doc contributes only 1
MUST, multi-doc consensus on the same leaf still substantiates
the source.

## Verification (synthetic smoke test)

Simulated 4 Ship 11'.f fanout sources (single MUST per leaf)
alongside 1 legit source (2 MUSTs on A.5.15):

| Source | MUSTs | Verdict |
|---|---|---|
| `ISO27001:2022:A.5.15` (RBAC + review) | 2 | **PROPAGATE** ← legit |
| `ISO27701:2019:A.7.2.6` (subprocessor audit only) | 1 | **DROP** ← fanout |
| `ISO27701:2019:A.7.2.8` (ropa activity id only) | 1 | **DROP** ← fanout |
| `ISO27701:2019:A.7.4.7` (expiry sweep only) | 1 | **DROP** ← fanout |

Exactly the intended behavior — 3 Ship 11'.f patterns filtered
without over-blocking the legit source. Ship 16'.d re-extraction
will measure the real-doc impact.

## Interaction with Ship 11'.b + 16'.b

The three gates run in sequence with distinct failure modes:

1. **Ship 11'.b** (`_source_is_bridge_worthy`): per-source
   quality — blocks bridge-of-bridges, low-confidence, and
   fragment sources with no MUST binding.
2. **Ship 16'.b** (specificity — extraction time): blocks
   fingerprint matches whose token set fires on >5 leaves
   (auto-generator template collisions).
3. **Ship 16'.c** (substantiveness — bridge time): blocks
   bridge propagation when the source has <2 distinct MUSTs
   bound on its leaf.

The gates don't overlap. 11'.b + 16'.b filter noisy sources
BEFORE they even reach the bridge stage; 16'.c filters at the
bridge stage itself. A source can pass all three gates only
when it's high-quality (11'.b), leaf-specific (16'.b), and
substantiated by multiple MUST bindings (16'.c).

## Ship 14'.a addendum alignment

**1. Role split?**

Preserved — gate is standard-agnostic. Program (ISO 27001) and
extension (ISO 27701) sources are subject to the same
substantiveness test. The `xfw_proposer` skip rule for
`program → obligation` (Phase 5) is untouched.

**2. Parallel CaseFile view?**

Not applicable — proposer runs post-extraction, pre-chat.

**3. Deterministic routing?**

Yes — pure dict count-lookup. No LLM inference.

**4. Guidance-normative discipline?**

Preserved — the gate drops bridges that would otherwise create
inflated posture attribution. No new MUSTs added.

## What did NOT ship

- **Per-standard tunable threshold** — same threshold (2) for
  all standards. If a specific standard family produces
  legitimate single-MUST bridges routinely, a per-standard
  override in `_SUBSTANTIVENESS_MIN_MUSTS_BY_STD` could be
  added. Deferred — no evidence today that any legitimate
  bridge is single-MUST.
- **Strong-signal single-MUST override** — one alternative
  design was: allow single-MUST bridging when the excerpt is
  substantial (≥200c) OR confidence is `high`. Skipped for
  simplicity; can add if false-blocks surface in 16'.d.
- **Backfill DISTINCT ON tuning** — the backfill query's
  DISTINCT ON collapses to one row per (doc_id, control_ref,
  std_id). If a single doc has multiple MUSTs bound on the
  same leaf, the count sees only the DISTINCT ON survivor.
  Acceptable for now: the substantiveness signal is "does the
  tenant have multiple bindings SOMEWHERE for this leaf" — the
  DISTINCT ON aggregates across docs but MUSTs still count.

## Ship 16 progress

| Sub-arc | Status |
|---|---|
| 16'.a Fingerprint audit + design memo | ✓ |
| 16'.b Extraction-time specificity gate | ✓ |
| **16'.c Bridge source-substantiveness gate** | **✓ (this doc)** |
| 16'.d Re-extraction measurement + retro | next |

## Related

- [[ship-16-prime-a-fingerprint-audit-2026-07-22]] — the audit
  whose findings this arc addresses
- [[ship-16-prime-b-specificity-gate-2026-07-22]] — Layer A of
  the two-layer fix; catches template-collision noise
- [[ship-11-prime-b-bridge-source-quality-gate-2026-07-20]] —
  the peer gate `sources_gated` counter sits alongside
- [[ship-11-prime-e-reextraction-measurement-2026-07-21]] —
  the measurement checkpoint that revealed the 4 unfixed
  fanout patterns Ship 16'.c targets
- Ship 16'.d: re-extraction measurement + arc retrospective
