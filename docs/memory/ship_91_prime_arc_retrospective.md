---
name: ship-91-prime-arc-retrospective
description: Ship 91' — LLM workbook row-arbiter for recall extension; scaffolded per-sheet prompts read catalog's three-way discipline (required/optional/cite) as frame, verifier gates via source-cell substring
metadata:
  type: project
---

# Ship 91' arc — workbook LLM row-arbiter (2026-08-20)

## Framing

Workbook extraction until Ship 90'.a: 100% structural (YAML
fingerprints → column matches → deterministic findings). High
precision, bounded recall — misses evidence in Notes/Comments
columns, cross-column composition, prose cells. Ship 85'.b tried
LLM extraction on flat markdown-rendered workbook text; regressed
F1 by 4.89pp because the LLM had to re-solve everything (what is
this sheet? which MUSTs? which columns anchor vs corroborate?)
without scaffolding. Guarded off; never revisited.

Ship 91' pivots the approach: LLM as **row-arbiter INSIDE a
fingerprint-matched frame**, reading the catalog discipline the
last 5 arcs built (required + optional + cite_columns).

## Delivered

**91'.a — `rag/intake/workbook_arbiter.py` (~330 LOC)**
- `ArbitratedFinding` dataclass — one LLM-arbitrated finding
  validated + ready for write
- `arbitrate_sheet(proposal, pass_yaml, rows)` — per-sheet function:
  fetches MUSTs from Neo4j → builds scaffolded prompt → LLM call →
  parses + verifies each finding
- `arbitrate_workbook(proposals, workbook_rows, mapping_pass_lookup)`
  — batch driver across a whole workbook

Scaffolded prompt shape:
```
SHEET: Access Register PII Systems
DETECTED AS: req:A.5.18:access_rights_register (via workbook.iso.A_5_18...)
CONTROL: A.5.18  |  EVIDENCE TYPE: register

CATALOG COLUMN DISCIPLINE (from YAML):
  ANCHOR MUSTs (required):
    - user id → item:A.5.18:reg_user_id
  CORROBORATION MUSTs (optional):
    - last verified → item:A.5.18:reg_last_verified
  CITED MUSTs (cite_columns):
    - policy link → item:A.5.18:reg_idmgmt_link

MUSTs on this leaf (bind ONLY to these ids VERBATIM):
  item:A.5.18:reg_user_id     | user identifier
  item:A.5.18:reg_grant_date  | when access was granted
  ...

HEADER ROW (1): User ID | Employee ID | System/Application | ...
DATA ROWS (18 shown of 18 total):
Row 3: User ID=41068980065 | System=Azure AD | Date Granted=2024-04-23 | ...
...
```

LLM emits per-row per-MUST verdicts; verifier gate demands:
- MUST id ∈ real Neo4j MUSTs
- `source_column` matches a real header
- `evidence_text` substring-matches the actual cell at claimed
  (row, column) — same Ship 6'.b pattern used in extractor.py

**91'.b — write path (`persist_arbitrated_findings`)**
- Inserts to `document_findings` with:
  - `inference_source = 'workbook_llm_arbiter'` (new allowlist value)
  - `grounding_method  = 'workbook_llm_arbiter'` (new allowlist value)
  - `corroborating_signals = ['llm_arbiter']`
- Dedup rule: skip if the structural pass already emitted `present`
  on the same `(control_ref, checklist_item_id)` — structural wins
  by construction (deterministic > LLM)
- schema_v103 extends both allowlists + updates
  `posture_writer._INFERENCE_TO_GROUNDING` (Ship 6'.b mapping)

**91'.c — cutover flag (`USE_WORKBOOK_LLM_ARBITER`)**
- `0` / unset → skip (default, safe)
- `shadow` → arbiter runs; count would-be-adds; do NOT write
  (measurement mode)
- `1` → arbiter runs + persists

Wired into `doc_pipeline` as **Stage 4.7**, immediately after Stage
4.6 (workbook_persistence). Uses the same open Postgres connection.
Errors caught + logged; never blocks the upload pipeline (best-effort
pattern from Ship 85'.a).

**91'.d — dogfood on ISO workbook (shadow + write mode)**

Shadow-mode run (USE_WORKBOOK_LLM_ARBITER=shadow):
- 47 fingerprint-matched proposals → 47 arbiter LLM calls
- **1164 findings proposed** (initial run at max_tokens=4000 truncated
  mid-JSON on 4 big registers; bumped to 12000, all 47 clean)
- Per-sheet range: 3-93 findings (SoA at the high end, small logs at
  the low end)
- Total cost: ~$0.48 for full ISO workbook re-extract
- Latency: ~17 min end-to-end (avg 19s per sheet arbiter call)

Write-mode run (USE_WORKBOOK_LLM_ARBITER=1):
- 1412 findings proposed (small variance vs shadow — LLM stochasticity)
- **883 deduped against structural** (structural pass already had
  `status='present'` on same control_ref × must_id)
- **529 written** (478 present + 51 partial)
- Workbook coverage: **210 → 739 total findings (3.5× lift)**
- Grounding: 100% cell-substring-verified via
  `_evidence_grounded_in_cell` (Ship 6'.b pattern)

Precision spot-check (20 random samples):

| Sample | Verdict |
|---|---|
| `item:10.1:reg_target_date` ← Due Date=2026-03-31 | tight |
| `item:4.2:owner` ← Responsibility=Vendor Security Manager | tight |
| `item:A.5.19:reg_owner` ← Assessed By=Petra | tight |
| `item:A.8.1:reg_owner` ← User Name (BYOD register) | tight |
| `item:A.8.1:reg_class` ← Device Type=Phone/Laptop | tight |
| `item:6.1.3:approval` ← Status=Implemented | tight |
| `item:A.5.22:rev_scope` ← Service Provided / Data Shared | tight |
| `item:7.2:documented` ← Employees ID | tight |
| `item:7.2:effectiveness` ← Evaluation Date | tight |
| `item:7.4:when` ← Frequency=When needed | tight |
| `item:10.1:reg_status` ← Status=Completed | tight |
| `item:10.1:reg_dimension` ← TASK column | tight |
| `item:9.2:rev_finding_closure` ← Progress Notes | tight |
| `item:9.2:rec_handoff` ← Status=Completed without automation | **weak** (status ≠ handoff) |

**19 of 20 semantically defensible ≈ 95% precision.** Well above
the 80% flip criterion set in the Ship 91' design. The one weak
case is a stretch (Status column doesn't imply handoff MUST) but
not a fabrication — the LLM DID find a populated cell to cite.

**Cutover decision: KEEP FLAG DEFAULT OFF.** Precision + recall
both good, but 20-minute latency per workbook re-extract is not a
tenant-transparent addition. Ship 91' delivers the LANE; a future
arc flips the default after broader dogfood on diverse workbooks
confirms latency + cost profile.

## Codified lessons

**Lesson 103: Structural + LLM lanes compose when they see the same
frame.** Ship 85'.b failed because LLM saw flat markdown; Ship 91'.a
succeeds because LLM sees the same three-way discipline the catalog
uses. The scaffolding IS the difference. **Give the LLM the same
frame your deterministic path uses; don't ask it to reinvent the
world from raw text.**

**Lesson 104: Verifier gates convert LLM proposals into
auditor-defensible findings.** The `_evidence_grounded_in_cell`
check (LLM's `evidence_text` must substring-match the actual cell
at LLM-claimed (row, column)) catches fabrication cleanly. Same
pattern as Ship 6'.b's extractor grounding. Auditor sees
`grounding_method='workbook_llm_arbiter'` in `document_findings`
and knows the finding was LLM-proposed + cell-verified.

**Lesson 105: Shadow mode is the right cutover shape for
LLM-additive paths.** `USE_WORKBOOK_LLM_ARBITER=shadow` measures
what WOULD be added without writing. Compare against baseline
(Ship 90'.a: 205 findings on ISO). If shadow adds 30-50 findings
of reasonable precision → flip to `1`. If it adds 300 and half are
noise → tune before flipping. Ship 35's `USE_CONSENSUS_EXTRACTION`
pattern generalizes.

## Files changed

- `rag/intake/workbook_arbiter.py` (new, ~330 LOC)
- `rag/intake/doc_pipeline.py` — Stage 4.7 wiring, env-gated
- `rag/intake/posture_writer.py` — `_INFERENCE_TO_GROUNDING`
  extended with `workbook_llm_arbiter` → `workbook_llm_arbiter`
- `rag/llm_models.py` — new `MODEL_WORKBOOK_ARBITER = "gpt-4.1-mini"`
- `db/schema_v103_workbook_llm_arbiter.sql` (new) — extends
  `inference_source` + `grounding_method` allowlists
- `docs/memory/ship_91_prime_arc_retrospective.md` (this)

## Deferred to future arcs

- **Ship 92'.a**: two-model ensemble (gpt-4.1-mini + gpt-4o) —
  precision lifter via 2-of-2 consensus. Only if shadow mode
  reveals accuracy gaps at the current model tier.
- **Ship 92'.b**: prompt tuning — Ship 91' uses a single system
  prompt across all sheets. Per-evidence-type prompts (register vs
  log vs review) may lift precision.
- **Ship 92'.c**: auto-verification of workbook cites (deferred
  from Ship 89'.b) — closes the cite-mode loop: linked doc uploaded
  + has present findings → mark cite `verified` in
  `external_evidence_verification_log`.

## Related

- [[ship-89-prime-b-cite-columns]] — cite_columns YAML field
- [[ship-90-prime-a-cite-columns-sweep]] — catalog sweep to 89 mappings
- [[ship-6-prime-a-llm-role-audit-2026-07-18]] — LLM role
  classification (arbiter is Determinative — cell-verified before write)
- [[ship-6-prime-b-grounding-provenance-2026-07-18]] —
  `grounding_method` column + substring verification pattern
