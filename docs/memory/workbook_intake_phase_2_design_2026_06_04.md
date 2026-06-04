---
name: workbook-intake-phase-2-design-2026-06-04
description: "ACTIVE plan — Phase 2 workbook intake design state as of 2026-06-04. 4 seed YAML mappings authored, Stage I engine pending. Schema decisions, engine requirements, predicted Arion outcomes all locked."
metadata: 
  node_type: memory
  type: project
  originSessionId: 26c1ec2d-8e36-436c-af44-a16367a2126d
---

ACTIVE design as of 2026-06-04. Goal: ingest tenant workbooks (Arion Networks as messy-shape reference, but design for arbitrary tenant intake) and write `document_findings` rows bound to MUST ids so the engine can verdict against real workbook evidence. Closes the wiring gap where `document_findings.checklist_item_id` is null everywhere despite 10 sheets already importing to domain tables.

## Pipeline shape (REVISED 2026-06-04 — merged into posture Stage 1)

The original 3-stage design (Discovery → Confirmation → Extraction with its own HITL surface) collided terminologically with the already-shipped posture Stage 1 / Stage 2 HITL pipeline AND duplicated the same conceptual layer ("is this a correct evidence claim?"). User flagged this directly: "i want to merge these to stage 1 stage 2." Acted on it.

The revised shape:

1. **Discovery** — fingerprint pass that produces `workbook_intake_proposal` (sheet-level breadcrumb, jsonb summary) AND writes `document_findings` rows inline — one per `(pass, satisfied-or-partial MUST)` with `inference_source='workbook'`, `checklist_item_id` populated, `workbook_proposal_id` linking back, `review_status='pending'`. No separate Confirmation or Extraction stages. Missing MUSTs do NOT get a finding row (gaps surface via curated MUST list vs satisfied set, the engine's job).
2. **Posture Stage 1** (existing — `rag/posture/stage1_review_chat.py`) reviews workbook findings IN THE SAME QUEUE as LLM-doc-extracted findings. Source-agnostic — Stage 1 queries `document_findings WHERE review_status='pending'`. Zero code changes to Stage 1 to make this work.
3. **Posture Stage 2** (existing — `rag/posture/stage2_approval_chat.py`) approves engine verdict deltas, unchanged.

What this collapsed:
- No `workbook_evidence_mappings` table. The YAML IS the binding rule; a confirmed `document_findings` row IS the confirmation.
- No separate Stage III extraction. Discovery writes findings inline.
- No new HITL surface. The existing Stage 1 chat picks them up for free.
- The wiring gap CLAUDE.md flagged (`document_findings.checklist_item_id` null everywhere) closes naturally — workbook is the first extraction path that populates it.

## Core decisions

**Why:** see retrospective on 2026-06-04 design session. Six decisions accumulated:

1. **Canonical YAML mappings live in `db/workbook_mappings/*.yaml`** — version-controlled curation artefact, NOT SQL-table-driven. SQL is for tenant-confirmed bindings + tenant-specific overrides only.
2. **`coverage: partial` semantics = engine-conservative** (MUST treated as unsatisfied when binding is partial). Locked by user 2026-06-04.
3. **Multi-target via passes (revised rule)** — ONE YAML per canonical sheet shape; passes can target any `(control × leaf)`. NOT separate YAMLs per control. One HITL card per sheet, one canonical file per sheet shape.
4. **Tenant override layer deferred to v2** (after ≥3 real tenant intakes). v1 = fingerprint-matches-or-doesn't; tenant fixes Excel-side or marks sheet as skip.
5. **Seed scope: 4 high-confidence mappings** (incident_log, asset_register, risk_register, access_register_pii). Defer the other 8 of original 12 until v1 engine validated.
6. **A.5.34 falsification** — Access Register PII Systems does NOT feed A.5.34; that's a RoPA-shaped target (categories/lawful_basis/retention/transfers), not access-shaped. Current YAML is A.5.18-only. A future RoPA-sheet YAML will fingerprint-match A.5.34 directly.
7. **Intake YAMLs are NOT a Neo4j candidate** (re-asked + locked 2026-06-04). The column→MUST bindings, sheet fingerprints, column_groups, and coverage qualifiers are tenant-data-shape concerns. Neo4j is the shared standards/specs graph and must not carry tenant-data-shape artefacts. Overlap with curation is minimal (`freshness.days` ≡ `freshness_days`; MUST list shape implied by `must_contain`) — kept as files, validated against `ALL_EVIDENCE_REQUIREMENTS` at load time. Decision NOT to revisit even though Neo4j-resident `typical_column_tokens` would help the LLM-answer layer explain gaps; if that need emerges, generate a derived property at curation-load time rather than moving the YAMLs.

**How to apply:** when continuing this work, treat the above as locked unless explicitly revisited. New YAMLs follow the same schema; engine implementation must enforce conservative `coverage: partial` semantics.

## Seed mappings authored (2026-06-04)

| File | Target(s) | New schema features it introduced |
|---|---|---|
| `db/workbook_mappings/incident_log.yaml` | A.5.26 (2 passes: register + closure) | multiple passes, `trigger_columns`, `pointer_columns` with `surfaces_gap_when_missing` |
| `db/workbook_mappings/asset_register.yaml` | A.5.9 (1 pass) | `column_groups` with `requires: all` (CIA-triad) + `requires: any` fallback, `alternative_fingerprints` on freshness |
| `db/workbook_mappings/risk_register.yaml` | 6.1.2 (1 pass) | `coverage: partial` at group level; cross-sheet MUST acknowledged unsatisfied |
| `db/workbook_mappings/access_register_pii.yaml` | A.5.18 only (1 pass) | nested `alternative_fingerprints` inside column_group entries; A.5.34 cross-link rationale documenting NOT-a-pass-target decision |

## Schema fields (decided, all 4 YAMLs use them consistently)

`mapping_id` · `schema_version` · `sheet_name_fingerprints` (token bags) · `header_row_hints` · `min_data_rows` · `passes` (with `pass_name`, `target_control`, `target_evidence_requirement`, `target_evidence_type`, `freshness` with `column_fingerprint` + `alternative_fingerprints` + `days`, `required_columns`, `optional_columns`, `column_groups` with `requires: all|any` + optional group-level `coverage`, `trigger_columns`) · `pointer_columns` with `surfaces_gap_when_missing` · `cross_control_links` (informational, not extractive) · `confidence_weights`

## Engine requirements surfaced by review pass (Stage I must do these)

| Requirement | Failing example without it |
|---|---|
| Stopword removal (of, by, in, to, for, the, and, ...) | `[chain, custody]` won't match "Chain of Custody" → `[chain, of, custody]` |
| Light stemming (granted→grant, subjects→subject) | `[grant, date]` won't match "Date Granted" → `[date, granted]` |
| Token splitter handles space + underscore + slash | "Asset_Owner", "System/Application" |
| Token bag SUBSET matching (not exact equality) | `[breach, classification]` matches "Breach Classification (InfoSec)" → `[breach, classification, infosec]` |
| `binds_to` validation at YAML-load time against `document_requirements.py` ALL_EVIDENCE_REQUIREMENTS | Typo `item:A.5.9:clasification` would silently produce zero satisfaction |
| Inner confidence math (Jaccard for sheet-name overlap? satisfied/required for column rate?) | Currently undefined; weights are 0.5/0.4/0.1 but functions unspecified |

CamelCase splitting is an OPEN call. Recommendation: require column headers use explicit separators; engine does NOT split CamelCase. Document this constraint in a README when authoring it.

## Engine semantics needing implementation

- `coverage: partial` at column-level AND group-level → both treat MUST as unsatisfied (conservative, locked).
- Multiple `column_groups` binding to same MUST → ANY-of. When one is satisfied full and another partial, **full wins**.
- Multiple `required_columns` with same `binds_to` → ANY-of (first matched column satisfies).
- Partial+partial+partial ≠ full (don't combine partial signals; conservative rule applies).

## Predicted Arion outcomes (under conservative rule)

| Sheet | Pass | Sat | Partial-but-unsat | Missing | Verdict |
|---|---|---|---|---|---|
| Incident Log | register | 1/5 (incident_id) | reg_severity, reg_lifecycle_dates | reg_status, reg_owner | NC |
| Incident Log | closure | 3/8 (incident_ref, authoriser, gdpr_triggered) | cls_root_cause | cls_containment, cls_recovery, cls_lessons, cls_sla_met | NC |
| Asset Register | register | 5/6 (records×2, owner, location, asset_type, classification via triad) | — | last_updated | NC |
| Risk Register | register | 4/6 (risk_id, description via group, owner, scoring via group) | — | treatment_status, last_assessed | NC |
| Access Register PII | register | 4/7 (idmgmt_link, grant_date, subject_asset via group, authoriser via group) | reg_status, reg_last_verified | reg_review_due | NC |

5 engine NC verdicts will be proposed once Stage III lands. 17 MUSTs satisfied, 5 partial-unsat, 9 missing across the 4 sheets. That delta is the engine-delta proof for v1.

## Next steps when resuming

1. ~~Optional cleanups before Stage I~~ **DONE 2026-06-04**: `db/workbook_mappings/README.md` authored with locked decisions + schema cheat-sheet; `scripts/validate_workbook_mappings.py` validates every `target_evidence_requirement` (against `ALL_EVIDENCE_REQUIREMENTS` + all `DerivedSpec.direct_evidence`), `target_control` (matches requirement's `control_ref`), and `binds_to` id (must be ChecklistItem on the declared target). All 4 seed YAMLs clean. Exits 1 with allowed-id list on error.
2. ~~Stage I engine~~ **DONE 2026-06-04** (in-memory v1): `rag/intake/workbook_discovery.py` (load YAMLs → tokenize → fingerprint sheets → emit `SheetProposal` / `PassProposal` dataclasses). Hand-rolled tokenizer (lowercase + split on `[\s_/-]+` + strip non-alnum + ~15 stopwords + trailing-s/es/ed/ing/ies stem with `_STEM_KEEP` exceptions). Subset-match for token bags. Conservative `coverage: partial`. CLI driver at `scripts/discover_workbook.py`. Verified against Arion `.xlsm`: 5 sheets matched 4 mappings; 33 sheets unmatched (expected — 8 of 12 originally-scoped mappings not yet authored). **Two real workbook gaps surfaced beyond the predicted-outcomes table**: Asset Register has no `Last Updated` column AT ALL; Risk Register has no `Last Assessed` column. These are real product gaps, not YAML calibration misses — feed back to Arion in Stage II.
3. ~~Persistence (v1b)~~ **DONE 2026-06-04**: schema_v31 + writer; superseded by v32 in same session.
4. ~~Stage II / III separate stages~~ **OBSOLETE 2026-06-04 — merged into posture Stage 1**. See "Pipeline shape REVISED" above. Concrete delivery:
   - `db/schema_v32_workbook_intake_into_stage1.sql`: extends `document_findings.inference_source` CHECK to include `'workbook'`; simplifies `workbook_intake_proposal.status` CHECK to `pending|superseded` only (per-row review_status owns approve/reject); replaces misnamed `document_upload_id` with `client_document_id` FK; adds `document_findings.workbook_proposal_id` FK + index.
   - `rag/intake/workbook_persistence.py`: in one transaction, inserts the proposal row + N `document_findings` rows (one per satisfied/partial MUST). FK note: `document_findings.document_id` references `client_documents`, NOT `document_uploads`. Two-step CLI lookup `storage_path → document_uploads.filename → client_documents.id`.
   - Verified end-to-end against Arion `.xlsm`: 5 proposals + 29 findings persisted (run `af6ea615-e265-4363-b449-b106b9e400e8`, client_document_id `64f10b73-d6e1-4b54-9197-4640b8220eef`). Stage 1's `list_queue()` surfaces all 4 workbook-touched controls (A.5.9 / 6.1.2 / A.5.18 / A.5.26) with correct pending counts. Zero changes to Stage 1 code.
5. Re-ingest Arion workbook end-to-end → measure NC delta (168 NCs → ?). That delta is the merge's proof. Requires tenant to actually approve the 29 pending findings via Stage 1 first, then engine to recompute.

## Engine vs predicted-outcomes deltas (2026-06-04 verification)

Predicted table was MUST-only; engine reports every MUST/SHOULD that any binding declares. Predicted author also eyeballed Arion's columns and missed two (Incident Log has "Owner" and "Evidence Collected" columns; predictions had them missing). Engine output is the truth-finder; predictions retained for historical reference but **do not treat as a contract**. The two genuine gaps in (2) above are valuable real findings the engine surfaced beyond what was predicted.

## v2 extensions noted but not designed

- **Tenant override layer** — per-tenant column-name synonyms for fingerprint failures.
- **Cross-sheet MUST satisfaction** — real-world pattern where tenants split logical registers across multiple sheets (Arion's Risk Register + Risk Treatment Plan is canonical; reg_treatment_status MUST sits on 6.1.2 register but lives in the 6.1.3 sheet). v1 schema doesn't join.
- **CamelCase column splitting** — open call; deferred.

## Related memories

- [[curation-program-full-multi-leaf]] — the curation arc that produced the multi-leaf specs this intake will satisfy
- [[engine-proposes-for-all-curated-specs]] — the engine surface this intake will feed
