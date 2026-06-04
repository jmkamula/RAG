# Workbook Mappings

Canonical YAML mappings from tenant workbook sheets → curated `ChecklistItem`
ids. Stage I (Discovery) reads these files, fingerprints each sheet in a
tenant workbook, and emits proposals. Stage II surfaces them for tenant
confirmation. Stage III extracts rows into `document_findings`
+ optional `client_documents` pointer rows.

## Locked decisions (do not revisit without explicit ask)

1. **One YAML per canonical sheet shape.** Multiple `(control × leaf)`
   targets are expressed as separate `passes` within the same file, not
   separate files. One HITL card per sheet.
2. **`coverage: partial` is engine-conservative.** A MUST satisfied only by
   partial-coverage bindings counts as UNSATISFIED. Applies at both column
   level and `column_group` level. Partial signals do not combine into full.
3. **Tenant data only.** These mappings are tenant-data-shape artefacts.
   They live as files (and, post-confirmation, as RLS-scoped SQL rows). They
   do NOT belong in Neo4j — the shared graph carries standards and specs,
   never tenant column conventions.
4. **CamelCase is not split.** Header tokens are split on space, underscore,
   and slash. Workbook authors must use explicit separators.
5. **No tenant override layer in v1.** Fingerprint either matches or
   doesn't; tenant either fixes the Excel side or marks the sheet as skip
   in Stage II. Per-tenant synonyms are a v2 concern (re-evaluate after
   ≥3 real tenant intakes).

## Validation

Run before merging any YAML change:

```bash
python3 scripts/validate_workbook_mappings.py
```

The script loads every `*.yaml` in this directory and validates that:

- `target_evidence_requirement` resolves to an `EvidenceRequirement` in
  `ALL_EVIDENCE_REQUIREMENTS` or in any `DerivedSpec.direct_evidence`.
- `target_control` matches the requirement's `control_ref`.
- Every `binds_to` id is a `ChecklistItem.id` declared on that target
  (must_contain or should_contain).

Exits non-zero on any unknown id. Failures print the allowed-id list for
the target so typos are easy to spot.

## Schema cheat-sheet

Top-level fields:

| Field | Purpose |
|---|---|
| `schema_version` | Currently `1`. Bump when the schema changes. |
| `mapping_id` | Dotted slug (`workbook.<standard>.<control>.<shape>`). |
| `sheet_name_fingerprints` | List of `{tokens: [...]}` bags. OR-combined. |
| `header_row_hints` | Row indices to try for the header row (1-based). |
| `min_data_rows` | Below this row count, proposal confidence is capped low. |
| `passes` | List of extraction passes (see below). |
| `pointer_columns` | Columns that reference external documents → `client_documents`. |
| `cross_control_links` | Informational only. Does not write evidence. |
| `confidence_weights` | Optional per-mapping overrides for the discovery scorer. |

Per-pass fields:

| Field | Purpose |
|---|---|
| `pass_name` | Unique within file. |
| `target_control` | Control ref (e.g. `A.5.9`). Validated against requirement. |
| `target_evidence_requirement` | `req:*` id. Must exist in curation. |
| `target_evidence_type` | Mirrors the leaf's `evidence_type`. |
| `freshness` | Optional. `{column_fingerprint, alternative_fingerprints, days}`. |
| `trigger_columns` | Row included only when at least one of these is populated. |
| `required_columns` | Column fingerprints that must be present. ANY-of by default when multiple bind to same MUST. |
| `optional_columns` | Same shape; missing column does not lower confidence. |
| `column_groups` | `requires: all` or `requires: any` over a column set. Group-level `binds_to` + optional group-level `coverage`. |

## Engine semantics (Stage I/III)

- Token bags match case-insensitive after stopword removal and light
  stemming. Subset match wins (e.g. `[breach, classification]` matches
  "Breach Classification (InfoSec)").
- Multiple `required_columns` binding to the same MUST → ANY-of (first
  match satisfies).
- Multiple `column_groups` binding to the same MUST → ANY-of across groups.
  When one is satisfied fully and another partially, full wins.
- `coverage: partial` (column-level or group-level) → MUST unsatisfied.
- Missing fingerprint column → engine warns, does NOT fail-closed on the
  freshness check.

## Authoring a new mapping

1. Pick the target leaf in `enrichment/documents/document_requirements.py`.
2. Copy the closest existing YAML as a template.
3. Update `mapping_id`, sheet fingerprints, passes, and bindings.
4. Run `python3 scripts/validate_workbook_mappings.py` until clean.
5. Add a cross-reference under `cross_control_links` for any control whose
   evidence is hinted at but NOT extracted by this mapping (see
   `access_register_pii.yaml` for the A.5.34 falsification pattern).
