# Intake Pipeline Architecture (as of 2026-06-15)

One-page reference for the three paths that produce `document_findings`,
their stages, and the failure modes each path has accumulated guards
against. Read this before adding a new filter, signal, or path.

## The three paths

```
                      ┌─────────────────────────┐
   policy/process/    │  PATH 1: doc extraction │   → checklist_item_id
   evidence DOC ─────▶│  (LLM-based)            │     OPTIONAL (set when
                      └─────────────────────────┘     doc_mapping matched)
                      ┌─────────────────────────┐
   posture XLSX ─────▶│  PATH 2: workbook       │   → checklist_item_id
   workbook           │  (structured, YAML map) │     NATIVE (from YAML)
                      └─────────────────────────┘
                      ┌─────────────────────────┐
   existing approved  │  PATH 3: leaf-scan      │   → checklist_item_id
   findings ─────────▶│  back-bind (CLI,        │     RETROFIT
   (any source)       │  lexical fingerprint)   │     (one-shot scan)
                      └─────────────────────────┘
              │
              ▼
   ┌──────────────────────────────────────────────┐
   │   document_findings  (review_status=pending) │
   └──────────────────────────────────────────────┘
              │
              ▼  HITL Stage-1 review (approve/reject)
   ┌──────────────────────────────────────────────┐
   │   document_findings  (review_status=approved)│
   └──────────────────────────────────────────────┘
              │
              ▼  engine sweep (only checklist_item_id-bound findings)
   ┌──────────────────────────────────────────────┐
   │   posture_controls  (Comply / OFI / NC / N/A) │
   └──────────────────────────────────────────────┘
```

A finding without `checklist_item_id` is **inert** for the engine —
visible in audit trails, not visible to verdict logic. Post Phase-1
retirement (2026-06-13).

## Path 1: doc extraction

```
upload → reader → enricher → [TOC filter] → [doc-mapping discovery]
       → [scope controls] → [fetch leaf MUSTs] → LLM extract
       → [filters: grounding | referential-demote | questionnaire | low-conf]
       → DocumentFinding → posture_writer → document_findings
       → xfw_proposer (cross-framework GDPR proposals)
       → intake_trace_log
```

### Failure modes & guards

| Failure mode | Guard | Shipped |
|---|---|---|
| Hallucinated evidence quote | `_evidence_grounded` substring check vs full_text + markdown | 2026-06-09 |
| Register-shape "X mentions Y" → false Comply | referential-mention demote to OFI | 2026-06-10 |
| Vendor questionnaire templates → spurious findings | `_looks_like_questionnaire` (Y/N, Proof Point, interrogatives) | 2026-06-12 |
| TOC/index docs → spurious findings | `_looks_like_toc` (filename + N.N Title — Purpose: density) | 2026-06-15 |
| Over-attribution (one doc → 30+ controls) | `doc_mappings` narrows the LLM candidate list | 2026-06-06 |
| LLM rephrases ref (A5.18 → A.5.18) | `normalize_ref` post-LLM | 2026-05 |
| Annex A vs ISMS clause confusion (5.x → A.5.x) | strict valid_refs match + 3-dot ISMS-only rule | 2026-06-09 |
| Findings landed unbound to MUSTs | per-MUST candidate list to LLM + checklist_item_id validation | **2026-06-15 (B)** |
| LLM picks legitimate MUST id but evidence doesn't match it semantically | catalog crosscheck — evidence vs `must_fingerprints` keyword sets, soft signal counted in `crosscheck_disagreements` | **2026-06-15** |

### Telemetry surfaces

- `intake_trace_log` rows per stage (schema_v35–v41)
- `/api/v1/admin/uploads/quality` red/yellow/green dashboard
- `/api/v1/admin/intake/unmatched-patterns` filename gaps for new doc_mappings

### Known open gaps

- Legacy fallback (`doc_mappings_match_count=0`) → no per-MUST binding; ~10 yellow uploads on Arion
- Section-based extraction dedup is `(control_ref, checklist_item_id)` — multi-MUST split works but section→section conflict resolution still uses Comply > OFI > NC priority

## Path 2: workbook intake

```
upload (.xlsm) → workbook_discovery → match db/workbook_mappings/*.yaml
   → workbook_persistence → finding rows with checklist_item_id NATIVE
   → intake_trace_log
```

### Why this path is simpler

- Structured input (XLSX columns) — no LLM at extraction time
- YAML mapping declares each MUST's source column / sheet / row filter
- 182 mapping YAMLs cover most posture-workbook shapes; 31/38 Arion sheets matched at last count

### Failure modes & guards

| Failure mode | Guard | Shipped |
|---|---|---|
| Filename vocabulary gap | `_SHAPE_SYNONYMS` + always-on topic_tokens enricher | 2026-06-08 |
| One workbook → many leaves of different evidence_types | per-leaf YAML, not per-workbook | 2026-06-06 |
| Sheet-row over-filter dropping evidence | v1 row-filter limitation accepted; per-leaf YAMLs compensate | 2026-06-06 |

## Path 3: leaf-scan back-bind

```
CLI: run_leaf_scan.py [--cap-fanout N] [--leaf X]
   → load db/must_fingerprints/*.yaml (310 catalogs)
   → for each leaf: find unmet MUSTs on this tenant
                  ↓ for each: pull approved findings on same control
                  ↓ regex match excerpt vs fingerprint keyword sets
                  ↓ propose new finding (status=pending, inference_source=leaf_scan)
   → cap-fanout filter (drop sources binding to >N MUSTs)
   → persist as pending findings
```

### Failure modes & guards

| Failure mode | Guard | Shipped |
|---|---|---|
| Loose autogen catalogs (one excerpt → many MUSTs) | `--cap-fanout 1` per-source filter | 2026-06-15 |
| Cross-doc fanout (same MUST attracting many unrelated excerpts) | **NOT GUARDED** — manual catalog refinement needed | open |
| Catalog keyword too generic | manual review per leaf (campaign 2026-06-14) | partial |

### Status

- 310 catalogs total (246 from 2026-06-14 campaign + 64 autogen on 2026-06-15)
- The autogen catalogs are skeleton-quality; the campaign manually reviewed
- Yield on Arion: 4 proposals from 241 unbound findings (1.7%) on first run;
  17 from expanded catalogs at `--cap-fanout=1` (out of 210 unfiltered).
  ~30% noise rate even at cap=1 (target-side fanout not yet filtered).

## Cross-cutting concerns

### Telemetry coordination
Every `extraction_metrics` key MUST also appear in:
1. `IntakeTracer.write` allowed-list (`doc_pipeline.py:107`)
2. `intake_trace_log` schema (current: v41)
3. `_extraction_quality_flag` if it affects red/yellow/green

Pair rule with [[feedback-eval-with-each-feature]]: new metric →
trace columns in same commit, no exceptions. Surfaced 2026-06-15:
the questionnaire + TOC filters had ridden 3 days with metrics
silently dropped at trace write because nobody added the columns.

### Finding state machine
```
   pending ──approve──▶ approved ──engine sees──▶ feeds verdict (if bound)
      │                    │
      ├──reject──▶ rejected (is_active=false)
      │                    
      └──expire (TTL)──▶ expired (is_active=false)
```
- `approved + checklist_item_id IS NULL` = inert (Phase-1 retired)
- `rejected/expired` MUST also be `is_active=false` (CHECK constraint)
- Reverting an approval = `approved` → `rejected` with rationale, soft-delete only

### Schema migration discipline
- 43 migrations as of v41
- All additive (ALTER TABLE ADD COLUMN, CREATE INDEX) — no destructive changes
- Squash-to-baseline opportunity flagged for next consolidation pass

## What's "right" today vs "next thread"

**Right today** (architecturally clean):
- Three paths with clear ownership
- HITL gate before engine
- Telemetry for each path with dashboard surface
- Filter family in extractor (4 filters, consistent shape)

**Next thread** (accreted, worth a look):
- Filter family lacks a shared abstraction (4 inline blocks in `_parse_llm_response`)
- Leaf-scan is now a recovery layer — should it stay first-class or move behind a "is the source extractor producing bound findings?" gate?
- 4 unmatched filename patterns in `/admin/intake/unmatched-patterns` — write doc_mappings YAMLs
- Catalog quality lint to flag autogen catalogs at risk of false-positive

## Related

- `[[per-must-binding-in-extractor-2026-06-15]]` — today's B+A fix
- `[[intake-quality-signals-v41-2026-06-15]]` — today's telemetry fix
- `[[leaf-scan-catalog-campaign-2026-06-14]]` — Path 3 catalogs
- `[[feedback-phase-1-fallback-masks-gaps]]` — why per-MUST binding matters
- `[[curation-phase-b-retrospective]]` — Neo4j schema arc
