---
name: templates-hybrid-2026-06-15
description: "SHIPPED 2026-06-15 (5da8aa8 + 289c5d7): hybrid form+doc template loop. Phase A: POST /api/v1/dashboard/control/{ref}/template writes per-MUST document_findings rows with checklist_item_id + inference_source='form'. Phase B: dashboard UI textareas per missing MUST + Save button + live re-render of advisory counts. Phase C: GET .../template/document?leaf=&format=md downloads markdown with MUST descriptions as section headings + tenant text as bodies + (not yet filled in) placeholders. Auditor sees what's covered + what's pending in the same artefact. schema_v40 added 'form' to inference_source enum."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The synthesis of "form for binding, doc for artefact".

## The strategic choice

Two competing pressures shaped this:

1. **Compliance teams want documents.** Auditors read PDFs and
   .docx files; they expect the artefact form. A pure web form
   feels alien.

2. **The engine needs structured per-MUST bindings.**
   `document_findings.checklist_item_id` is the only signal the
   engine counts after Phase-1 retirement. Documents alone don't
   set it deterministically — extractor binding is probabilistic
   (see all of week of 2026-06-09 fighting this).

The hybrid resolves both: tenant fills a **per-MUST web form**
(deterministic binding), system **generates a markdown document**
on demand from the form data (auditor artefact). Same source of
truth, different shape per consumer.

## Three-phase ship

### Phase A (5da8aa8) — backend save

`POST /api/v1/dashboard/control/{ref}/template` accepts:
```
{items: [{checklist_item_id, leaf_id, evidence_type, text}, ...]}
```

For each item:
- Resolves / creates one synthetic `client_documents` row per
  `(control, leaf)` pair — filename `template_<ctrl>_<leaf>.md`,
  `is_metadata_only=TRUE`, `document_status='registered'`
- INSERT/UPDATE one `document_findings` row with
  `checklist_item_id` set, `status='present'`,
  `review_status='approved'` (tenant-authored is pre-approved),
  `inference_source='form'`
- Empty text + existing row → soft-delete (tenant cleared field)
- Engine-kick (load_posture) runs post-commit so the next
  advisory fetch sees the new bindings

schema_v40 adds 'form' to the
`document_findings.inference_source` CHECK enum.

### Phase B (5da8aa8) — dashboard UI

`renderAdvisoryPanel` extended:
- Per-MUST `<textarea>` rendered for each unsatisfied MUST,
  with `data-must=<checklist_item_id>` attribute
- "Save evidence" button — collects all textareas, POSTs to
  template endpoint, refetches advisory, replaces panel
  in-place with updated counts
- "Download .md" button — fetches Phase-C endpoint, browser
  blob download with server's Content-Disposition filename

Live UX: tenant fills a field, clicks Save, sees "2/7 → 3/7"
update without page reload.

### Phase C (289c5d7) — downloadable doc

`GET /api/v1/dashboard/control/{ref}/template/document
  ?leaf=<id>&standard_id=<std>&format=md`

Per-leaf or whole-control markdown document:
```
# Template: A.5.15
_Generated 2026-06-15 from per-MUST tenant input._

## access control policy (policy)
### 1. Principle of need-to-know stated
<tenant's filled text>

### 2. Authorisation rules — who can authorise access...
<tenant's filled text>

### 3. Cross-link to A.5.3 segregation of duties
> _(not yet filled in)_

...
---
Source: ISO/IEC 27002:2022 §5.15 implementation guidance.
```

`rag/posture/template_document.py:build_template_document` is
the data path:
- MUST descriptions + IDs from Neo4j ChecklistItem nodes
  (preserves the order in the leaf)
- Tenant text from `document_findings` filtered to
  `inference_source='form'` + `is_active=TRUE` for this control
- Missing MUSTs render as visible "(not yet filled in)"
  placeholders — auditor sees the gap inline, not silently

## Auditor visibility of unfilled MUSTs

Important design choice: the doc INCLUDES placeholders for
unfilled MUSTs rather than only showing filled ones. The auditor
reading the document sees both the structure (per ISO/IEC 27002
§5.15) AND the gap. Hiding unfilled MUSTs would let the tenant
"look complete" by producing a partial document. The placeholder
forces honesty.

## Why form-only content (no auto-merge of extracted findings)

The doc generator only pulls form-authored text, NOT extracted
findings on the same MUSTs. Trade-off:

- **Form-only (chosen):** clean auditable provenance — every
  word in the doc was authored by the tenant on a specific date
  via a specific form input. Auditor knows what they're reading.
- **Auto-merge:** richer doc, but extractor snippets can be
  noisy / partial / mis-attributed. Document quality becomes
  hostage to extractor quality.

Tenant can copy extracted text into the form if they want it
in the doc. The form save then records it as their own
authored statement (with a date and audit trail).

## Data path summary

```
tenant fills form (UI textarea)
  → POST /template (per-MUST → document_findings rows)
  → engine_kick (load_posture re-runs)
  → advisory refetch (counts update)
  → tenant sees "n/M" change live

tenant clicks Download .md
  → GET /template/document
  → template_document.py joins MUSTs (Neo4j) ⊕ form text (Postgres)
  → renders markdown with placeholders
  → browser blob download
```

Both directions of the loop read/write the same
`document_findings` rows with `inference_source='form'`. There's
no separate "drafts" table — the binding IS the storage.

## Future moves on the backlog

- `?format=docx` — Word document via python-docx. Single section
  per MUST with consistent styling. Easier audit hand-off.
- Per-evidence_type form variants — register-shape MUSTs need a
  table editor (rows of entries); record-shape MUSTs need a
  "per-event" template (one per incident / disposal / etc.).
  Today: every MUST gets a textarea. Works but coarse.
- Attachments per MUST — file upload that creates a normal
  `client_documents` row, linked to the form-authored finding.
  Lets the tenant cite "see attached screenshot" alongside the
  text.
- Versioning — `document_status='superseded'` chain so the
  tenant can keep history of policy revisions.

## Related

- [[per-must-advisory-2026-06-14]] — the chat / endpoint / UI
  surfaces that this hybrid extends. The data builder
  `build_per_must_advisory_data()` produces the per-MUST list
  that the form consumes.
- [[curation-document-templates-idea]] — the original backlog
  item this implements (was deferred during Phase B catalog
  authoring).
- [[feedback-phase-1-fallback-masks-gaps]] — the architectural
  rule that drove "deterministic per-MUST binding only". The
  form save respects it: every saved field IS a
  `checklist_item_id`-bound finding.
- [[leaf-scan-catalog-campaign-2026-06-14]] — the fulfilment
  criteria the form surfaces. Every textarea label is a MUST
  description authored during Phase B catalog work.
