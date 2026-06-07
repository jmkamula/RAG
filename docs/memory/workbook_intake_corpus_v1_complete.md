---
name: workbook-intake-corpus-v1-complete
description: "SHIPPED 2026-06-06: workbook intake YAML corpus complete for v1 — 182 mappings across all 5 tiers, covers full curated sheet-shaped leaf surface; Arion discovery matches 25 of 38 sheets after vocabulary tuning"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The workbook-intake YAML corpus is complete for v1 as of 2026-06-06.

## State

**182 YAMLs in `db/workbook_mappings/`** covering all 5 tiers from the taxonomy (`docs/workbook_intake_canonical_shapes.md`):

- Tier 1 (review_record): 12 hand-written YAMLs covering ISMS clauses 9.2 / 9.3 / 10.1 / 10.2 / 6.2 + Annex A control-family reviews (audit, supplier, change, SIG, training, pentest, legal, BCP, NC tracker)
- Tier 1 (revocation_log): 14 hand-written per-leaf YAMLs (identity / credential / access / leaver / triage / lessons / evidence-disposal / equipment-disposal / cloud-exit / EOL / supplier-offboarding / supplier-deviation / BCP-activation / ICT-recovery)
- Tier 2 (small clusters): 13 per-leaf YAMLs (monitoring_record × 6, change_record × 3, responsibility_matrix × 2, contact_register × 2)
- Tier 3 (registers): 124 bulk-generated via `scripts/generate_register_yamls.py` (24 A.5 + 7 A.6 + 13 A.7 + 28 A.8 + 14 ISMS clauses + 38 GDPR)
- Tier 4 (one-offs): 15 sheet-shaped (SoA, RTP, classification scheme, lawful_basis_register, RoPA, DFI, audit_execution_log, segregation_of_duties, publication, controller_processor_decision, asset_discovery, resilience_test, default_settings, operational risk assessment / treatment)

Doc-shaped Tier 4 leaves (audit programme charter, risk_assessment procedure, isp_approval_record) intentionally NOT YAML-targeted — they take file upload + LLM doc-extraction path.

## Why per-leaf, not "163-in-one"

Tier 1 review_record was initially scoped as ONE canonical YAML covering 163 leaves via multi-pass. V1 schema's `trigger_columns` only checks if a column EXISTS in the sheet header — it cannot filter rows by cell content. A multi-pass YAML against a master review-log sheet would attribute every row's review_date to every leaf's pass, polluting freshness. Per-leaf YAMLs with distinct sheet-name fingerprints sidestep this entirely. Row-level filtering is a v2 schema concern.

## How to apply

- **Adding a new YAML**: copy the closest existing template, edit fingerprints + binds_to. Validate with `scripts/validate_workbook_mappings.py` (catches typos in target_evidence_requirement / target_control / item:* ids).
- **Regenerating Tier 3**: `python3 scripts/generate_register_yamls.py` is idempotent — won't overwrite existing files. Drop a generated file first if you want it re-derived. Hand-edits survive future regens.
- **Tenant vocabulary mismatches**: discovery emits `unmatched sheets` for sheets whose tokenised name doesn't subset any fingerprint. Extend the relevant YAML's `sheet_name_fingerprints` with the tenant's abbreviation (e.g. `[bia]` added to asset_register; `[spec, int]` added to A.5.6).
- **Workbook tokenizer** (`rag/intake/workbook_discovery.py:_SPLIT_RE`): splits on `[\s_/\-&+,]+`. Stems trailing `s/es/ed/ing/ies`. Does NOT auto-stem abbreviations (reg ≠ register, doc ≠ document) — the generator emits BOTH forms in the fingerprint.

## Discovery state on Arion (2026-06-06)

- 38 sheets read → 31 matched via 37 proposals (after hand-tuning 6 vocabulary gaps)
- 7 unmatched are legitimate: 5 admin/utility (TOC/Documentation/Mapping/Instructions/Formulas), 1 task tracker (ISMS Schedule), 1 row-level review (Quarterly Security Review — defer to v2 row-routing)
- Effectively 100% of actionable Arion sheets covered

## Persistence run

Run `1f6ec172-52d5-4540-89d0-177f25c9166c` (2026-06-06) persisted 37 proposals + 143 `document_findings` rows on Arion at `review_status='pending'`. 21 controls now in the Stage-1 queue. The original 29 approved findings from run `af6ea615` (2026-06-04) continue feeding the engine; new findings stay gated at pending until per-control Stage-1 approval.

CLI invocation:
```
scripts/discover_workbook.py <workbook.xlsm> --persist \
  --tenant-id <uuid> --client-document-id <uuid>
```

## Post-Stage-1-approval state (2026-06-07)

User drained the Stage-1 queue on Arion (all 143 new findings + 29 prior = 172 approved). Engine sweep re-ran (16 active PA rows refreshed with new structured reasons). **Stage-2 queue stayed at 2 entries** (A.5.23 + A.5.34) — and that's intentional, not a bug.

Why no new Stage-2 proposals: under the strict `_compose_posture` rule the user chose 2026-06-05, OFI requires ≥1 fully-fulfilled child leaf. The workbook columns include `coverage: partial` qualifiers on interpretive bindings (Findings → rec_findings is partial because column hints at the MUST without proving it). The leaf evaluator counts only `status='present'`, never `status='partial'`. Every workbook-fed control ends up 0/4 sat + 1-2 partial → engine NC → matches live NC → concurrence, no Stage-2 proposal.

Tenant chose to accept this on 2026-06-07. Partial evidence still surfaces in the engine reason text ("(N with partial evidence)") so progress is visible per-control, just doesn't earn an OFI promotion. To move a control off NC, the tenant needs to fully complete a leaf (all MUSTs at status='present'), not just partial-cover several.

The hybrid "surface partial as Stage-2 for HITL acknowledgement" surface was discussed and shelved.

## Related

- [[workbook-intake-phase-2-design-2026-06-04]] — design + early state (4 seed YAMLs)
- [[compose-posture-any-progress-ofi]] — verdict rule that decides how partial workbook signals roll up
- [[engine-agreement-suppression]] — concurrence write path that surfaces engine reasoning for NC/OFI
