# Document Mappings

Canonical YAML mappings from uploaded document shapes → curated
`EvidenceRequirement` leaves. The doc analog of `db/workbook_mappings/`.

## What problem this solves

The LLM doc-extractor's default scoping (`DOC_TYPE_CLAUSE_MAP` in
`rag/intake/ref_normalizer.py`) is coarse: `policy → [A.5, A.6, A.7,
A.8]` essentially exposes every Annex A control as a candidate per
chunk. The LLM then over-attributes — Arion's Supplier Vendor Security
Policy got bound to 42 distinct controls, Access Control Policy to 29.

Doc mappings replace that broad pre-filter with a per-doc-shape
declaration: "a doc whose filename tokens match `[cloud, service,
policy]` covers leaf `req:A.5.23:cloud_services_policy` and its
cross-links — and ONLY those leaves go to the LLM extractor."

## Locked decisions

1. **One YAML per canonical document shape.** Multiple leaves a single
   doc shape covers (e.g. an Access Control Policy doc commonly
   addresses A.5.15 + A.5.16 + A.5.17 + A.5.18) live as multiple
   `target_leaves` entries within ONE YAML.
2. **Filename fingerprints are the primary signal.** Body fingerprints
   are a tie-breaker for ambiguous filenames.
3. **`cross_control_links` is informational only.** Listed for the
   Stage-2 HITL card; does NOT scope the LLM call. Use a `target_leaves`
   entry if you want the LLM to assess a control.
4. **No tenant override layer in v1.** Same as workbook mappings: the
   fingerprint matches or it doesn't. Per-tenant filename synonyms are
   a v2 concern.
5. **Soft fallback.** If no mapping matches an upload, the extractor
   falls back to the legacy `DOC_TYPE_CLAUSE_MAP` path so older docs
   continue to work.

## Validation

```
python3 scripts/validate_doc_mappings.py
```

Checks every `leaf_id` in `target_leaves` resolves to an
`EvidenceRequirement` (top-level or `DerivedSpec.direct_evidence`)
and that `control_ref` matches.

## Schema cheat-sheet

| Field | Purpose |
|---|---|
| `schema_version` | Currently `1`. |
| `mapping_id` | Dotted slug (`doc.<standard>.<control>.<shape>`). |
| `filename_fingerprints` | List of `{tokens: [...]}` bags matched against filename. OR-combined. |
| `body_fingerprints` | Optional. Token bags matched against first N lines of doc body. |
| `min_body_chars` | Optional. Below this, confidence cap applies. |
| `target_leaves` | List of `{leaf_id, control_ref, role}` — leaves this doc shape covers. |
| `cross_control_links` | Informational. Does NOT scope the LLM call. |
| `confidence_weights` | Optional per-mapping overrides for the discovery scorer. |

## Authoring a new mapping

1. Find the curated leaves the doc should satisfy (search
   `enrichment/documents/document_requirements.py` by title or
   evidence_type).
2. Copy the closest existing YAML as a template.
3. Update `mapping_id`, filename fingerprints, target_leaves.
4. Run `python3 scripts/validate_doc_mappings.py` until clean.
5. Verify against a real upload via the discovery driver (TBD).
