---
name: ship-17-prime-a-regeneration-design-2026-07-23
description: "Ship 17'.a — fingerprint catalog regeneration design memo; enrich auto-generator with topic-anchor tokens from RequirementNode.title"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 17'.a — opens Ship 17 arc (fingerprint catalog
regeneration). Direct follow-up to Ship 16's gate architecture:
Ship 16 caught noise at the pipeline; Ship 17 fixes the data
at its source.

## Root-cause analysis

Ship 16'.a's audit surfaced 338 cross-leaf token collisions
across 2595 fingerprints. Ship 16'.b's specificity gate caught
44 of them at extraction time (matches shared >5 leaves →
drop). But the underlying catalog remains noisy — the gate is
belt-and-suspenders, not the fix.

Root cause is in `scripts/generate_27701_fingerprints.py`:

- **Set 1** builds tokens from the MUST id slug
  (`item:A.7.2.1:rev_date` → strip `rev` prefix noise → `[date]`
  — single token, gets dropped by `_MIN_SET_SIZE = 2`)
- **Set 2** builds tokens from the MUST text first-phrase
  (`"Review date within the planned interval"` → tokens
  `[review, date, planned, interval]`)

The MUST TEXT is templated identically across every
`program_review` and `applicable_scope` leaf. So `[review,
date, planned, interval]` gets emitted for A.7.2.1, A.7.2.2,
A.7.2.3, ... A.7.5.4 — 48 leaves with the identical token
set. That's the template-collision Ship 16'.b catches at
runtime.

## The fix: topic-anchor tokens

Every leaf has a distinctive `RequirementNode.title` that
identifies its content domain:

| Leaf | Title | Anchor tokens |
|---|---|---|
| A.7.2.6 | Contracts with PII processors | `[contracts, pii, processors]` |
| A.7.2.1 | Identify and document purpose | `[identify, document, purpose]` |
| A.7.2.8 | Records related to processing PII | `[records, processing, pii]` |
| A.7.4.7 | Retention | `[retention]` |
| A.7.4.8 | Disposal | `[disposal]` |
| A.5.19 | Information security in supplier relationships | `[supplier, relationships]` |

Injecting 1-2 topic-anchor tokens into every keyword set for
a leaf turns family-templated sets into leaf-distinctive ones:

- Before: `A.7.2.6:rev_date` = `[review, date, planned, interval]`
  — same set on 48 leaves
- After:  `A.7.2.6:rev_date` = `[review, date, planned, interval, processor]`
  — distinctive to A.7.2.6

Zero token-set collisions across the program_review family
because each control has a different anchor token.

## Generator enhancements

### 1. Add topic-anchor extraction (from Neo4j)

Fetch `RequirementNode.title` alongside the existing MUST rows.
Tokenize the title with the same `_tokenize()` helper. Keep 1-2
distinctive tokens (non-stopword, ≥4 chars, non-generic — skip
`information`, `security`, `management` which are meta-terms).

### 2. Inject anchor tokens into every keyword set

For a leaf with anchor tokens `[processor, contracts]` and a
generated set `[review, date, planned, interval]`, emit
`[review, date, planned, interval, processor]`. Only one
anchor per set (avoid making sets too narrow).

### 3. Cross-collision guard at build time

After candidate sets are generated for a leaf, check against a
running index of already-generated sets. If a candidate
collides with >N leaves that have DIFFERENT control refs, add
a second anchor token or fall back to a leaf-slug tail token.

### 4. Preserve auto-generator provenance

Regenerated YAMLs still carry the `# Auto-generated` marker
line so future audits distinguish them from hand-authored
files (Ship 16'.a survey found 260/506 auto-generated;
246 hand-reviewed).

**Discipline**: the regenerator only touches files whose
first-6-line header contains "Auto-generated". Hand-authored
work is off-limits. `gen_leaf_scan_catalog.py` (the
single-leaf interactive generator) already respects this via
"never overwrites existing files"; the bulk generator gains
the same guard.

## Sub-arc plan

### 17'.b — Fix generator + regenerate worst-offender families

- Enhance `generate_27701_fingerprints.py`:
  * Neo4j fetch expanded to include `RequirementNode.title`
  * `_topic_anchor_tokens(title)` extractor
  * Anchor injection in `_build_keyword_sets`
- Regenerate ONLY the program_review + applicable_scope
  families first — biggest ROI (48 + 17 leaves = 65 files with
  the worst collisions)
- Verify via re-run of `audit_fingerprints.py`:
  * `[review, date, planned, interval]` should no longer be a
    single collision across 48 leaves
  * Expect substantial drop in cross-leaf collisions count
    (338 → estimate <100)

### 17'.c — Regenerate remaining auto-generated families + verify

- Extend to all remaining auto-generated families
  (`processor_contract_register`, `program_review` for A.5.x,
  `applicable_scope` overlaps, etc.)
- Full audit re-run: measure collision reduction + specificity-
  gate drop-count on the same 5-doc Ship 10 set
- Expected: Ship 16'.b `dropped_low_specificity` counter falls
  to near-zero (the gate becomes a genuine safety net rather
  than the primary defense)

### 17'.d — Measurement + arc retrospective

- Compare pre/post audit metrics (338 collisions → N)
- Re-run `scripts/measure_ship11_reextraction.py` for
  extraction-volume comparison
- Optional: re-run Ship 16'.c bridge-substantiveness dry-run
  on demo tenant to confirm the improvement compounds
- Arc retrospective codifying lessons

## Design decisions locked in 17'.a

1. **Topic-anchor injection is the fix** — cheap, deterministic,
   preserves the auto-generator's provenance. No hand-authoring
   of individual leaves.

2. **Only touch files with "Auto-generated" header** —
   hand-authored/reviewed files stay untouched. Ship 16'.a's
   inventory confirmed this is safe (246 hand-authored files
   distinguished by header prose like "Reviewed-from-skeleton").

3. **Anchor from RequirementNode.title, not from EvidenceRequirement
   slug or MUST id.** The RN.title is the canonical
   human-facing name and is stable across catalog rewrites.

4. **Skip generic meta-tokens as anchors** — `information`,
   `security`, `management`, `data`, `iso` (which appear in
   most titles). Curator-specific stopword list.

5. **Ship 16'.b gate stays** — belt and suspenders. Post-Ship-17
   the gate's drop counter should decrease dramatically but not
   necessarily to zero (some hand-authored fingerprints
   collide too).

6. **Keep the generator's --dry-run flag** — allows preview
   before overwriting. Add a per-family filter flag so 17'.b
   can regenerate program_review only.

## What Ship 17 does NOT do

- **Regenerate hand-authored files** — those 246 files remain
  authoritative. Any collision they introduce stays as a
  known-good curator decision.
- **Rewrite `gen_leaf_scan_catalog.py`** — that's the
  interactive single-leaf tool. Not the source of the family
  collision problem.
- **Retire Ship 16'.b gate** — the gate becomes a safety net
  post-Ship-17 but isn't removed. Belt-and-suspenders discipline.
- **Retire Ship 16'.c substantiveness gate** — orthogonal to
  the token specificity problem. Still catches single-MUST
  bridge fanouts.
- **Regenerate for ISO 27001** — the auto-generator only
  currently supports 27701. Extending it to 27001 is a Ship
  17'.c (or later) scope decision.

## Ship 17 progress

| Sub-arc | Status |
|---|---|
| **17'.a Regeneration strategy + generator audit** | **✓ (this doc)** |
| 17'.b Fix generator + regenerate worst-offender families | next |
| 17'.c Regenerate remaining families + verify against gates | pending |
| 17'.d Measurement + arc retrospective | pending |

## Related

- [[ship-16-prime-arc-retrospective-2026-07-22]] — the arc
  whose "fingerprint catalog regeneration" deferral this arc
  delivers
- [[ship-16-prime-a-fingerprint-audit-2026-07-22]] — the audit
  tooling this arc will re-run to measure improvement
- [[ship-16-prime-b-specificity-gate-2026-07-22]] — the runtime
  gate that becomes belt-and-suspenders post-Ship-17
- Ship 17'.b: implementation of the topic-anchor injection
