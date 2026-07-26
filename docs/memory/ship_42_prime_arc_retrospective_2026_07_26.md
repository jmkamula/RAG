---
name: ship-42-prime-arc-retrospective-2026-07-26
description: "Ship 42' arc closer — evidence_group_id dedup working end-to-end. Ship 41's DPIA-opener multi-attribution poster case (20 rows across 5 controls) collapses to 5 auditor items. Engine per-MUST recognition preserved (unchanged query). Eval 231/232 baseline held. 40'.c divergence question moot: dedup applies to persistence AND surface; direct-vs-overlay tiebreak still handled by source-guard. Ship 43 direction: default-ON evaluation now safe on Arion; broader-tenant rollout candidate."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 42' arc retrospective — 2 delivery sub-arcs + closer, single
session 2026-07-25/26. Ship 41's multi-attribution regression
addressed via write-time dedup key + surface-time collapse.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 42'.a | Design memo — evidence_group_id at write, filter at surface | 5604c09 |
| 42'.b | Implementation + measurement | 723847a |
| **42'.d** | **Retro (this)** | pending |

Sub-arc 42'.c was collapsed into 42'.b (measurement happened
inline during implementation; no separate re-extract needed).

## The design's key insight

Ship 42'.a's core insight: **auditor UI and engine read the same
table with different semantics**.

- Auditor wants 1 row per unique (excerpt, control_ref)
- Engine wants 1 row per MUST for `checklist_item_id = ANY(...)`
  recognition

Naive dedup at persistence breaks engine (12 A.5.34 MUSTs → 1
row → engine sees 1/12 satisfied → verdict flips to NC).

Ship 42'.b resolution:
- Persistence keeps all N rows (engine happy)
- Stamp `evidence_group_id = sha1(document_id + control_ref +
  normalized_excerpt)[:16]` at INSERT (Ship 42 write-time work)
- Surface layers filter `DISTINCT ON (evidence_group_id)` at
  read time (auditor happy)

Same underlying data, two views.

## What ships

**schema_v90** — nullable `evidence_group_id text` column on
`document_findings` + partial index on (tenant_id,
evidence_group_id) WHERE NOT NULL.

**`rag/intake/posture_writer.py`** — 3 changes:
1. New `_normalize_excerpt(text)` — whitespace-collapse, case-fold,
   strip markdown escapes, bounded at 500 chars
2. New `_evidence_group_id(doc_id, ref, excerpt)` — 16-char sha1
   prefix; None on empty excerpt (surface layer treats NULL as
   "own group" via COALESCE fallback)
3. Both INSERT statements in `_write_document_findings` include
   `evidence_group_id` column + parameter

**`rag/posture/stage1_review_chat.py`** — 2 SELECT sites updated:
- `list_pending_for_control` uses `ROW_NUMBER() OVER (PARTITION BY
  COALESCE(evidence_group_id, id::text))` → 1 row per group
- `list_queue` uses `COUNT(DISTINCT COALESCE(evidence_group_id,
  id::text))` → dedup count per control

Legacy rows (NULL evidence_group_id) fall back to per-row counting
via COALESCE — no visibility regression for pre-Ship-42 findings.

## Measurement on 5 Ship 10 baseline docs (post-42'.b re-extract)

| Doc | raw_rows | unique_groups | collapse% |
|---|---|---|---|
| Consent | 33 | 4 | 12.1% |
| DPIA | 27 | 5 | 18.5% |
| DQA | 28 | 10 | 35.7% |
| Processor Ops | 18 | 9 | 50.0% |
| RoPA | 37 | 5 | 13.5% |
| **Total** | **143** | **33** | **23.1%** |

**Ship 41's DPIA-opener poster case** (20 rows across 5 controls,
one sentence attributed 20 times) → **5 groups** (1 per control):
- Art.35: 4 rows → 1 group
- 6.1.2: 3 rows → 1 group
- 6.1.3: 1 → 1
- 8.3: 1 → 1
- A.7.2.5: 11 rows → 1 group

**RoPA A.5.34 within-control multi-attribution** (was 26 rows on
one control) → **10 unique groups** (60% collapse); 3 unique
sentences producing 3 groups + xfw_proposer bridges kept
individually.

Stage-1 queue count per control (before → after dedup):
- Art.35: 4 → 1
- A.5.34: 26 → 10
- A.7.5.3: 3 → 1
- 6.1.2: 4 → 2

## Engine safety verified

Eval 231/232 PASS + 1 WARN + 0 FAIL. Baseline unchanged from
pre-Ship-42. Since chat pipeline reads posture (not raw findings)
and engine reads per-MUST rows unchanged, no regression.

The engine's `_fetch_recognised_items` query is untouched. It
still sees 12 rows for A.5.34's 12 MUSTs — verdict computation
proceeds identically to pre-42.

## Codified 2 lessons

### 1. Two-view semantics beat two-table refactors

Original 42'.a design considered a two-table split
(`document_findings` per-MUST + `evidence_citations` per-group).
That's a bigger schema surgery + join semantics change +
migration burden.

The `evidence_group_id` column + surface filter delivers the
same two-view semantics with a single-column addition and
zero engine code changes. **When you find yourself designing a
schema split to reconcile competing view requirements, try
adding a group-key column first.**

### 2. Backward-compat via COALESCE(nullable_column, id::text)

Legacy rows have NULL evidence_group_id. Surface filters use
`COALESCE(evidence_group_id, id::text)` — treating each legacy
row as its own group. No visibility regression; no forced
backfill.

**Rule**: whenever adding a dedup/grouping key to a live table,
use nullable + COALESCE fallback to id. Backfill becomes
optional (nice-to-have, not blocker). Prior-arc data stays
visible while new writes get the new discipline.

## What Ship 42 did NOT do

- **Backfill script for legacy rows** — deferred; not needed for
  correctness (COALESCE fallback), but useful for consistency.
  Candidate for a 15-min follow-up.
- **api_server.py auto-approved list dedup** — the
  `/api/v1/stage1/auto-approved` revert surface intentionally
  keeps per-row visibility (tenant may need to revert specific
  bindings)
- **evidence_package.py dedup** — Evidence Package is per-MUST
  view for auditor evidence rendering; naive dedup would hide
  per-MUST coverage. Left as-is.
- **UI-side "covers N MUSTs" annotation** — Ship 42 provides
  the dedup; product decision on how to surface the collapsed
  MUST count deferred to a UI arc
- **Consensus signal changes** — evidence_uniqueness signal
  keeps current thresholds; the write-time dedup is the
  hard downstream gate

## What Ship 42 accidentally did

**Discovered that xfw_proposer writes findings via a different
path** — the 69 bridge findings (48% of Ship 40'.b writes) have
NULL evidence_group_id in the fresh window. Not a problem in
practice (bridge findings are architecturally 1-per-control
already), but if we later want them in the same group scheme
(e.g. to dedup bridge findings that happen to share excerpts
across arcs), we'd need to route them through the same writer
or add a group_id computation to xfw_proposer.

## Ship 43 direction — default-ON evaluation is now safe

Ship 41 blocked default-ON on the multi-attribution regression.
Ship 42 addresses that with dedup. Ship 43 candidates:

- **Broader-tenant evaluation**: pick 2-3 tenants (staging /
  test), flip `USE_CONSENSUS_EXTRACTION=1`, re-extract their
  docs, measure recall + confirm dedup holds across doc
  variety. Ship 41-42 covered Arion's DPIA/RoPA/etc pattern;
  other tenants may have different multi-attribution shapes.
- **Retire legacy pipeline**: after broader eval clears,
  default `USE_CONSENSUS_EXTRACTION=1` + delete old code
  paths + delete flag. Bigger commit.
- **Backfill evidence_group_id + delete stale findings**:
  clean-up arc — populate the ~4225 existing document_findings
  rows on Arion + soft-delete duplicates.

Recommendation: Ship 43'.a = design memo weighing broader eval
vs. legacy retirement vs. cleanup. Order likely: broader eval →
backfill/cleanup → retirement (biggest blast radius last).

## Related

- [[ship-41-prime-arc-retrospective-2026-07-26]] — the HITL
  finding that motivates Ship 42
- [[ship-42-prime-a-dedup-design-2026-07-26]] — the design memo
- `db/schema_v90_ship42b_evidence_group_id.sql` — the schema
- `rag/intake/posture_writer.py::_evidence_group_id` — the key
  computation
- `rag/posture/stage1_review_chat.py::list_pending_for_control` —
  the primary surface filter
