---
name: ship-42-prime-a-dedup-design-2026-07-26
description: "Ship 42'.a design memo — per-doc excerpt dedup at write time. Key tension: auditor wants 1 finding per unique (excerpt, control_ref); engine reads checklist_item_id per-MUST and needs all N rows visible. Resolution: write all rows (engine visibility) but stamp evidence_group_id at INSERT. Surface layers (Stage-1, advisory, evidence package, chat) filter to 1 row per group. Preserves engine semantics; auditor experience matches Option B intent."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 42'.a — design memo for per-doc excerpt dedup at write time.

## Motivation

Ship 41 HITL surfaced multi-attribution regression: DPIA opener
sentence → 20 findings across 5 controls (Ship 32-shape in
miniature); ~38% of Ship 40'.b's fresh findings share excerpts
within-doc. Ship 42 direction locked as Option B: per-doc
excerpt dedup at write time.

## The tension: auditor UI vs engine

**Auditor wants**: 1 finding per unique (excerpt, control_ref).
DPIA opener → 5 findings (one per control), not 20 (one per MUST).

**Engine wants**: 1 finding per MUST. `leaf_evaluators.
_fetch_recognised_items` queries `checklist_item_id = ANY(%s)` —
each MUST must appear on its own row (or the engine sees the MUST
as unrecognised → verdict drops).

**Naive dedup breaks engine.** Collapsing 12 A.5.34 rows to 1 with
`checklist_item_id=A.5.34:owner` loses the other 11 MUSTs; engine
verdict flips from potentially-covered to 1/12 satisfied → NC.

## Resolution — write all rows, stamp group_id, filter at surface

Two-layer semantics:

1. **Persistence** — keep all N rows in `document_findings`
   (engine visibility preserved). Each row has its own
   `checklist_item_id`.
2. **Surface** — stamp `evidence_group_id` on each row at INSERT
   (hash of `document_id + control_ref + normalized_excerpt`).
   Auditor-facing SELECTs (Stage-1 queue, advisory, evidence
   package, chat digest) filter `DISTINCT ON (evidence_group_id)`
   to display 1 row per group. Engine SELECTs (leaf_evaluators)
   keep the per-row scan unchanged.

This IS "dedup at write time" — the dedup key (group_id) is
determined + stamped at write. Surface layers just group by it.

## Schema change

`schema_v90_document_findings_evidence_group_id.sql`:

```sql
ALTER TABLE document_findings
  ADD COLUMN evidence_group_id text;

CREATE INDEX idx_document_findings_evidence_group
  ON document_findings (tenant_id, evidence_group_id)
  WHERE evidence_group_id IS NOT NULL;

COMMENT ON COLUMN document_findings.evidence_group_id IS
  'Ship 42 dedup key: sha1(document_id || control_ref || normalized_excerpt). '
  'Rows sharing the same evidence_group_id are UI-collapsed to a single '
  'auditor-facing citation but preserved individually for engine per-MUST '
  'recognition.';
```

NOT-NULL constraint NOT added — legacy rows have NULL; only fresh
Ship 42+ writes stamp the column.

Optional backfill script: `scripts/backfill_evidence_group_id.py`
computes group_id for existing document_findings rows. Safe to run
anytime; idempotent.

## Group ID computation

```python
import hashlib

def evidence_group_id(document_id: str, control_ref: str,
                      excerpt: str) -> str:
    normalized = _normalize_excerpt(excerpt)
    key = f"{document_id}|{control_ref}|{normalized}"
    return hashlib.sha1(key.encode()).hexdigest()[:16]

def _normalize_excerpt(text: str) -> str:
    # Collapse whitespace; strip; case-insensitive; strip common
    # markdown escapes. Same excerpt with different whitespace
    # should collapse.
    import re
    text = re.sub(r"\\([\\\-\(\)\.])", r"\1", text or "")  # unescape
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text[:500]  # cap for safety
```

Note: 16-char sha1 prefix gives 2^64 space — plenty for
per-tenant. Not cryptographic use — collision resistance not
critical.

## Writer changes — one function

`rag/intake/posture_writer.py::write_findings` — compute
`evidence_group_id` for each finding before the INSERT loop.
Column added to both INSERT statements (line 489 + line 531).

~10 LOC net addition. Zero changes to engine, chat, or advisory
query logic in this sub-arc. Surface filtering ships in 42'.b
when the writer + backfill are proven.

## Surface filter — Stage-1 queue example

Current Stage-1 SELECT (`stage1_review_chat.py:254`):

```sql
SELECT df.checklist_item_id, ...
  FROM document_findings df
 WHERE ...
```

Adds `DISTINCT ON (evidence_group_id) ...` OR uses a subquery
picking the highest-confidence row per group:

```sql
WITH ranked AS (
  SELECT df.*,
         ROW_NUMBER() OVER (
           PARTITION BY evidence_group_id
           ORDER BY confidence DESC, extracted_at DESC
         ) AS rn
    FROM document_findings df
   WHERE ... /* existing filters */
)
SELECT * FROM ranked WHERE rn = 1 OR evidence_group_id IS NULL;
```

`OR evidence_group_id IS NULL` preserves legacy row visibility
until backfill runs.

Surfaces to touch (5 files, ~4 queries each):
- `stage1_review_chat.py` (multiple SELECT sites)
- `advisory.py` (line 348)
- `evidence_package.py` (line 137)
- `api_server.py` (5 SELECT sites listing findings)
- Frontend: no changes if backend does the filter

## Ship 42'.b implementation plan

1. Write `db/schema_v90_document_findings_evidence_group_id.sql`
2. Apply schema
3. Add `evidence_group_id()` helper in
   `rag/intake/posture_writer.py`
4. Modify `write_findings()` to compute + insert
5. Add regression test: DPIA opener re-extract → verify
   evidence_group_id populates + Stage-1 SELECT collapses to
   5 rows (not 20)
6. Backfill script `scripts/backfill_evidence_group_id.py` +
   run once on Arion demo

## Ship 42'.c re-measurement

Trigger re-extract via API. Measure:
- Ship 41 fresh finding counts (baseline): DPIA 27, RoPA 37,
  Consent 33, DQA 28, Processor Ops 18 = 143 total rows in
  document_findings
- Ship 42'.b: **row count unchanged** — dedup is at surface, not
  persistence. Engine still sees N rows.
- **Distinct evidence_group_id counts**: DPIA should collapse
  to ~10 (was 20 opener + 7 unique); RoPA ~15; Consent ~18;
  DQA ~22; Processor Ops ~10. Total ~75 distinct groups (down
  from 143 rows).
- Auditor-facing Stage-1 queue: shows ~75 items (was 143).

Verify eval baseline holds (chat pipeline reads
`_render_obligations` which reads posture, not directly findings
— should be unaffected).

## Ship 42'.d retro topics

- Did dedup solve the DPIA opener case? (verify distinct
  group_ids per doc)
- Engine verdict for demonstrated obligations — did per-MUST
  recognition survive dedup? (verify posture_controls stability)
- Is default-ON now safe? (Ship 43 gate)
- Surface filter completeness — any query site missed?

## Framework role + case-file alignment

**Role model**: Direct extraction still respects the role model.
Consensus extracts on all standards under bypass; Phase 2c
DEMONSTRATES overlay coexists. Dedup doesn't affect role
propagation — it's a within-doc citation-collapse concern.

**Case-file model**: Chat digest renders posture, not raw
findings. Dedup at document_findings surface layer doesn't reach
chat digest. Preservation-check unaffected.

## What Ship 42 does NOT do

- **Change engine verdict computation** — engine reads N rows
  same as today
- **Change consensus signal weights** — evidence_uniqueness signal
  keeps current thresholds
- **UI/frontend changes** — backend query changes suffice for
  the surfaces enumerated; chat digest natively renders posture
- **Retire evidence_uniqueness signal** — keeps functioning as
  upstream soft filter; Ship 42 is downstream hard filter
- **Retire USE_CONSENSUS_EXTRACTION flag** — default-OFF
  preserved; dedup applies whether flag on or off

## Ship 43 preview

If Ship 42'.c confirms dedup + engine verdict stability:
Ship 43 = broader-tenant default-ON evaluation (per Ship 40's
deferred candidate). If not — iterate to Ship 42'.e with
Option A signal tuning as belt-and-suspenders.

## Related

- [[ship-41-prime-arc-retrospective-2026-07-26]] — the HITL
  finding that motivates Ship 42
- [[ship-33-prime-arc-retrospective-2026-07-25]] — where
  evidence_uniqueness signal was designed
- [[framework-role-model-arc]] — the framework role model
  dedup preserves
- `rag/intake/posture_writer.py::write_findings` — the writer
  Ship 42'.b modifies
- `rag/posture/leaf_evaluators.py::_fetch_recognised_items` —
  the engine query dedup MUST NOT break
- `rag/posture/stage1_review_chat.py:254` — first surface
  filter site
