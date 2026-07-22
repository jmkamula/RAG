---
name: ship-16-prime-a-fingerprint-audit-2026-07-22
description: "Ship 16'.a — fingerprint audit tooling + design memo; 2595 MUST-fingerprints across 506 leaves scanned; 556 single-token + 338 cross-leaf collisions surfaced"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 16'.a (2026-07-22) — opens Ship 16 arc (fingerprint token
discipline / Pattern 2 root-cause fix). This sub-arc delivers
the audit tooling and the design memo; 16'.b applies the fixes.

## Audit findings

Ran `scripts/audit_fingerprints.py` against
`db/must_fingerprints/`. Numbers match Ship 11'.f's
inventory: **2,595 MUST-fingerprints across 506 leaves**.

### Per-class MUST-fingerprint counts (worst-group classification)

| Class | Count | % of total | Description |
|---|---|---|---|
| `single_token` | 556 | 21% | Fires on any doc containing the token |
| `multi_noise_only` | 50 | 2% | 3+ tokens but all in the noise set |
| `loose_pair_noise_only` | 62 | 2% | 2 tokens, both noise (e.g. `[review, date]`) |
| `loose_pair_one_signal` | 204 | 8% | 2 tokens, only 1 non-noise word |
| `one_signal_padded` | 92 | 4% | 3+ tokens but only 1 non-noise word |
| `loose_pair_ok` | 536 | 21% | 2 non-noise tokens (borderline) |

**Bottom line: ~40% of fingerprints (964 of 2,595) have loose
or over-broad token sets.** The auto-generator
(`scripts/generate_27701_fingerprints.py`) produced these
without per-leaf specificity.

### Cross-leaf token-set collisions

**338 token-sets are defined on 2+ leaves.** Worst offenders:

| Token set | Leaves affected |
|---|---|
| `[identity, reviewer]` | 64 leaves — any doc mentioning a reviewer identity |
| `[date, interval, planned, review]` | 48 leaves — every program_review's rev_date |
| `[date, review]` | 20 leaves |
| `[exclusions, scope]` | 17 leaves — every applicable_scope leaf |
| `[date, planned, within]` | 16 leaves |
| `[per, row]` | 10 leaves |

**Root cause identified**: the fingerprint auto-generator
templated the same shape across every `program_review` and
`applicable_scope` leaf, so tokenised review-cadence phrasing
attributes to 48+ leaves simultaneously.

### Ship 11'.f target confirmation

The 4 patterns Ship 11'.f identified surface in the audit:

- `item:A.7.2.6:reg_annex_b_coverage` → `[annex, coverage]`
  (loose_pair_noise_only)
- `item:A.7.2.6:rev_subprocessor_audit` → `[subprocessor, audit]`
  (loose_pair_one_signal — subprocessor is the signal; audit
  is noise)
- `item:A.7.2.8:ropa_activity_id` → `[processing, activity]`
  (loose_pair_one_signal — fires on any RoPA-shaped mention
  in tenant docs)
- `item:A.7.4.7:rev_expiry_sweep` → `[expiry, sweep]`
  (loose_pair_ok — but shared with 5+ other leaves)

Audit confirms these are structural not one-off.

## Strategy for the fix (16'.b + 16'.c)

Given the scale (~1,000 problematic fingerprints), touching
each YAML by hand is intractable. Two-layer approach:

### 16'.b — extraction-time specificity gate

At `_extract_via_fingerprints` load time, build an index:
`token_set → set(leaf_ids)`. At extraction time, when a
fingerprint matches, check the index — if the same token set is
defined on more than N leaves (default `N=5`), reject the
match with a new telemetry counter `dropped_low_specificity`.

**Why this over YAML edits**: the audit surfaced structural
patterns (all program_reviews share `[review, date, planned,
interval]`) that would require regenerating catalog files, not
hand-editing them. A load-time index fix touches 1 file and
solves the 338 collisions in one edit.

**Retained for hand-authored fingerprints**: legitimate
per-leaf hand-authored fingerprints (rare — most catalog files
are auto-generated) may share tokens with the auto-generated
ones. The load-time index is agnostic; if a hand-authored
`[coverage, check]` collides with the auto-generated ones, it
fires the same drop. Curator can raise the threshold per-leaf
via a new `min_specificity` field in the yaml if needed —
deferred to a follow-up.

### 16'.c — bridge source-substantiveness

Ship 11'.f's bridge gate blocked bridge-of-bridge + low-
confidence + fragment sources but let medium-confidence
MUST-bound sources through. Add a NEW gate: only propose a
bridge when the source has >=2 satisfied MUSTs on the same
leaf. Single-MUST matches don't bridge — matches Ship 10's
observed pattern (single loose-pair match → wrong bridge fired).

## Design decisions locked in 16'.a

1. **Load-time index over YAML edits.** Solves 338 collisions
   with a single-file change; preserves the catalog's provenance
   from `generate_27701_fingerprints.py`.

2. **Threshold `N=5`.** Any token set defined on >5 leaves is
   almost certainly over-broad (program_review family has 5+
   leaves for each control × 3-6 controls per family). Start
   conservative; tune via re-extraction on Ship 10 5-doc set
   (16'.d).

3. **New telemetry counter** `dropped_low_specificity` alongside
   Ship 11'.c's `dropped_content_shape` and Ship 11'.d's
   `dropped_semantic_fit`. Confirms whether the specificity gate
   is doing measurable work.

4. **Bridge substantiveness gate = ≥2 satisfied MUSTs** on the
   source. Matches the Ship 10 evidence that single-MUST bridges
   were the false positives.

5. **NO catalog regeneration in this arc.** Regenerating
   fingerprints is a broader curator arc (target the generator,
   audit + re-emit per-family). Deferred to Ship 17+ candidate.

## What ships from 16'.a

- `scripts/audit_fingerprints.py` — walks catalog, classifies
  per-group tokens, surfaces cross-leaf collisions, writes JSON
  report. 245 LOC. Idempotent read-only script.
- This design memo.
- Task list for 16'.b/'.c/'.d.

## Ship 16 progress

| Sub-arc | Status |
|---|---|
| **16'.a Fingerprint audit + design memo** | **✓ (this doc)** |
| 16'.b Extraction-time specificity gate | next |
| 16'.c Bridge source-substantiveness gate | pending |
| 16'.d Re-extraction measurement + eval + retro | pending |

## Related

- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc
  whose Pattern 2 root-cause fix this arc delivers
- [[ship-11-prime-e-reextraction-measurement-2026-07-21]] —
  the measurement checkpoint that flagged the same 4 patterns
  reappearing
- [[ship-11-prime-b-bridge-source-quality-gate-2026-07-20]] —
  the bridge gate this arc extends
- Ship 16'.b: extraction-time specificity gate at
  `_extract_via_fingerprints`
