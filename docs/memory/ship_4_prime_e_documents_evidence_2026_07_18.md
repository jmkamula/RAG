---
name: ship-4-prime-e-documents-evidence-2026-07-18
description: "Ship 4'.e — /evidence + /documents (upload + status) on external API"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 4'.e (2026-07-18) — write-side + evidence-read surface.
External systems can now push documents into the intake pipeline
and read back the findings bound to specific controls.

## What shipped

`rag/external/endpoints/documents.py` — 3 endpoints:

### POST /api/external/v1/documents
Multipart/form-data upload. Same dedup + series/version handling
as the internal `/api/v1/documents/upload`. Runs the intake
pipeline (`rag/intake/doc_pipeline.py::DocumentPipeline`) in a
background task. Returns `upload_id` immediately with
`extraction_status='pending'` (or `'duplicate'` + canonical id).

Scope: `external:evidence:write`.

### GET /api/external/v1/documents/{upload_id}
Poll for extraction status + findings count + metadata. External
clients poll until `extraction_status='completed'` (or `'failed'`).
Malformed UUID → 400 rather than 500.

Scope: `external:evidence:read`.

### GET /api/external/v1/evidence
Returns all `document_findings` for a (control_ref, standard_id).
Joins BOTH `document_uploads` AND `client_documents` (findings
can reference either — intake-pipeline uploads vs. manually
declared / workbook-imported documents) and COALESCEs the
filename so external clients get a human label either way.

Query params (both required):
- `control_ref` — e.g. `A.5.18`
- `standard_id` — e.g. `ISO27001:2022`

Scope: `external:evidence:read`.

## Design decisions worth remembering

- **document_findings.document_id is bimodal** — it references
  either `document_uploads` (from the intake pipeline) or
  `client_documents` (from manual declaration / workbook
  import). The JOIN pattern must LEFT-JOIN both + COALESCE.
  Missed this on first pass; got 136 rows with `filename=null`
  and had to fix.
- **Pipeline signature is `declared_standard_ids` (plural list),
  not `declared_standard_id`** (singular). Also `original_filename`
  is critical — API uploads store the file with a UUID name, so
  without this the DOC-prefix / title matchers can never link
  to the pre-registered `client_documents` row.
- **Background processing** — the FastAPI `BackgroundTasks`
  handles the pipeline invocation. Errors are logged; the
  upload_id + pending status are returned immediately.

## Tests

`tests/test_external_api.py` — **42/42 pass** (33 from
Ships 4'.a-d + 9 new for /documents + /evidence). Test suite
now uses a new `_post_multipart()` helper for form uploads.

New fixture `_test_state_evidence()` seeds:
- Read + write api_keys (distinct scopes)
- A `client_documents` row
- A `document_findings` row referencing that client_document,
  bound to `(A.5.18, ISO27001:2022)`

Test coverage:
1. Evidence happy path — seeded finding visible
2. Evidence scope check
3. Evidence missing query params → 422
4. Document status unknown id → 404
5. Document status malformed id → 400
6. Document upload happy path — pending returned
7. Document upload scope check — read alone ≠ write
8. Document upload bad extension → 400
9. Document upload dedup — 2nd identical content → duplicate + canonical_upload_id

## Verified end-to-end via curl

- Evidence for A.5.18 in Arion — 136 findings across ~10 named
  files (workbook + policies + registers)
- Upload of a 49-byte markdown → pending → 20s later →
  completed, `processed_at` populated, `findings_count=0`
  (tiny doc, no extractable evidence, expected)

## Baseline

Eval running (PID 111140). No RAG path change; new endpoints
query `document_findings` + `document_uploads` + `client_documents`
directly and reuse the internal intake pipeline.

## Ship 4 progress

| Sub-arc | Status |
|---|---|
| 4'.a Foundation | ✓ shipped |
| 4'.b /query | ✓ shipped |
| 4'.c /posture family | ✓ shipped |
| 4'.d /notifications | ✓ shipped |
| **4'.e /documents + /evidence** | **✓ shipped** |
| 4'.f /cascade + /bridges | next |
| 4'.g Python SDK + docs + key UI | future |

## Related

- [[ship-4-prime-a-external-api-foundation-2026-07-17]] — auth
  + rate limit + error contract
- [[ship-4-prime-d-notifications-endpoints-2026-07-18]] —
  previous sub-arc
