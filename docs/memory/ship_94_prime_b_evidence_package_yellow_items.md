---
name: ship-94-prime-b-evidence-package-yellow-items
description: Ship 94'.b — Evidence Package export renders partial + missing + cite + closure-trail so the auditor sees the same actionable narrative the tenant sees inside the product.
metadata:
  type: project
---

# Ship 94'.b — Evidence Package reflects yellow-item picture (2026-08-24)

## Framing

Ships 92-93 made yellow items actionable **inside the product**:

- Ship 92'.b — MUST-overlap cite attestation prompts
- Ship 92'.d — server-side humanization + auditor-details toggle
- Ship 93'.a — `explain_partial()` close-path prose
- Ship 93'.b — upload affordance ("Upload evidence for X" button)
- Ship 93'.f — `explain_missing()` for MUSTs with zero coverage
- Ship 93'.z.iii — closure trail via `resolved_by_upload_id`
- Ship 94'.a — LLM arbiter default ON

But the **auditor-facing Evidence Package export** (the
tenant-downloads-a-.md-and-emails-it-to-their-auditor deliverable)
still fell through to generic "not covered" lines for any MUST
that wasn't fully evidenced. The auditor saw:

    ✗ Per-row target completion date
      No evidence yet. Add or upload a source that addresses this element.

...while the tenant, opening the same leaf in-product, saw:

    ✗ Per-row target completion date
      No evidence yet for Target date. To add it: (1) Add a
      column named like Due Date, Target Date, Completion
      Date to a register in your workbook. (2) Or upload a
      document that explicitly demonstrates Target date.

**Ship 94'.b closes that asymmetry.** Auditor now sees the same
narrative. Every yellow item on the export carries the specific
close path, not a generic prompt.

## What changed

Single file: `rag/posture/evidence_package.py`.

### 1. `_must_state()` gains a 'partial' branch

`MustVerdict.partial` was already in the SSoT (Ship 61'.a); the
package renderer just wasn't reading it. Now branches:
`direct` / `bridged` / `partial` / `missing`.

### 2. Coverage summary counts partial + missing explicitly

Old header:
```
**Coverage:** 3 of 7 required elements have evidence on file.
```

New header:
```
**Coverage:** 3 of 7 required elements have evidence on file.
**Partial evidence on file:** 1 of 7 required elements have partial
  evidence — see per-element detail below for what's missing to
  move each to full coverage.
**No evidence yet:** 3 of 7 required elements have no evidence
  on file. Each has an inline note showing how to add it.
```

### 3. Per-MUST 'partial' rendering

New ◐ branch:
```
- ◐ **Per-row status** (partial evidence)
  Excerpt: "PROPOSED, APPROVED, IN-PROGRESS, CLOSED"
  Source: workbook — Improvement Actions sheet
  _To move to full coverage: This is corroboration-only evidence
   by design. Your workbook shows STATUS, which supports but
   doesn't fully evidence Status. To move it to present:
   (1) Upload a document that explicitly demonstrates Status._
```

Prose comes from `explain_partial()` — HTML tags stripped for
markdown-clean surface.

### 4. Per-MUST 'missing' rendering enriched

Every missing MUST now gets `explain_missing()` prose inline:
```
- ✗ **Per-row action owner**
  _No evidence yet for Owner. To add it: (1) Add a column named
   like Owner, Assigned To, Responsible to a register in your
   workbook. (2) Or upload a document that explicitly
   demonstrates Owner._
```

### 5. New "External evidence cites" section

Compact block between required elements + recommended additions:
```
## External evidence cites

- **Reg Trigger Type** — cite in Internal Documents: Audit Log
  (last attested 2026-08-21; next review due 2027-08-21).
- **Owner** — cite in Legal SharePoint: DPA v3
  (not yet attested).
```

Silent when zero cites. Queries `external_evidence_source` scoped
to the leaf's control ref + standard.

### 6. Closure trail linkage inline

Direct findings that closed a prior partial get:
```
_Closes an earlier partial finding — linked to upload on 2026-08-24._
```

`findings_by_element` query extended with a LEFT JOIN to
`document_uploads` + `client_documents` on
`resolved_by_upload_id` to pull resolver filename + `resolved_at`
+ `resolution_reason` from Ship 93'.z.iii schema (`schema_v109`).

## Dogfood

**On ISO Arion 10.1 (improvement_action_register)**, all 7
elements missing (this workbook has zero improvement actions
yet):

- Coverage summary: `0 of 7 required elements have evidence` +
  new `No evidence yet: 7 of 7` line
- Each MUST gets its `explain_missing()` prose with specific
  column-add suggestions (e.g. "Add a column named like Due Date,
  Target Date, Completion Date to a register")
- External evidence cites section: fires with `reg_trigger_type` →
  Audit Log SharePoint cite

**Synthetic partial test** (approved partial on `reg_status`):
- ◐ branch fires
- Excerpt from workbook cell shown
- Sheet + column source shown
- "corroboration-only" prose from `explain_partial()` shown

Reverted the synthetic approve so demo state stays clean.

## What doesn't change

- Chat pipeline untouched
- No new schemas (uses existing `schema_v109` closure trail cols +
  existing `external_evidence_source` from Ship 92 arc)
- No new endpoints — same `/api/v1/dashboard/leaf/{ref}/evidence-package`
- Recommended additions (SHOULD items) still list-only; the yellow-item
  narrative is scoped to required elements (MUSTs) intentionally

## Eval

232 PASS + 1 WARN + 0 FAIL (baseline preserved).

## Codified lessons

**Lesson 116: Internal-surface parity is the auditor experience.**
Every arc that improves the tenant's in-product view of a state
(yellow items in this case) creates a parity gap with the
auditor-facing export unless the export catches up. The gap
widens silently — the tenant never sees the export they hand
off, so they don't feel the regression. Auditor-facing surfaces
need their own tracking. Ship 94'.b's cost was small (one file,
~200 net LOC) because the underlying explain functions
(`explain_partial`, `explain_missing`) were already surface-clean
— but only if the retrospective explicitly checks for auditor
parity does the arc get scheduled.

**Lesson 117: Reuse the explain function; don't fork the prose.**
`explain_partial()` and `explain_missing()` were built for the
in-product Stage-1 detail panel. Ship 94'.b calls them
unchanged, strips HTML for markdown, done. If we'd hand-authored
"auditor-tone" prose in the package renderer, we'd have two
copies of the close-path narrative that would drift the first
time we changed either. Single source of truth for close-path
prose across every surface.

## Related

- [[ship-93-prime-a-partial-explainability]] — where
  `explain_partial()` was built
- [[ship-93-prime-f-missing-musts]] — where `explain_missing()`
  was built
- [[ship-93-prime-z-housekeeping]] — closure trail schema
  (`schema_v109` `resolved_by_upload_id`)
- [[ship-92-prime-b-cite-attestation]] — where
  `external_evidence_source` + attestation flow was built
- [[dejargonize-ux-pass-2026-07-01]] — the natural-language
  conventions the reused explain-functions already comply with
