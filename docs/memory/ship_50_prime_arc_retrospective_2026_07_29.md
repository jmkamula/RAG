---
name: ship-50-prime-arc-retrospective-2026-07-29
description: "Ship 50' arc retrospective — template round-trip repair + Q&A restructure. 4 sub-arcs one session. Diagnosis: customers who downloaded .docx templates + filled them in + re-uploaded were losing their evidence to fingerprint noise because docx_renderer converts `<<MUST>>` markers to human-friendly `◆ Required element — <slug>` labels that no code path detects on re-read. Fix: L2 reader-side reconstruction (marker + edit-zone rebuild), L1 defensive scaffold filter, How-to-use preamble, Q&A template exemplar for A.5.1. Curator followup: propagate Q&A shape to 643 remaining narrative templates."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 50' arc retrospective — template round-trip repair.

## What shipped

4 sub-arcs across one session (2026-07-29). Triggered by pre-POC
dry-run inspection of the Arion demo tenant's Stage-1 queue: customer
had uploaded three template-based artefacts today (A_5_1_management_approval.docx,
A_5_1_communication_record.xlsx, A_5_1_annual_review.xlsx). The two
xlsx uploads bound cleanly via the `_arion_meta` sheet; the docx
upload produced 15 findings on WRONG controls (5.2 / A.5.12) with
excerpts that were literally OUR OWN template scaffolding.

| Sub-arc | Delivery | Commit |
|---|---|---|
| 50'.a | Extractor: L1 scaffold filter + L2 ◆ marker detection | 0b67e25 |
| 50'.b | Renderer: How-to-use preamble | 37a7621 |
| 50'.c | Reference template rewrite (A.5.1 management_approval) | 37a7621 |
| 50'.d | E2E verify on customer's actual docx | 37a7621 |
| **50'.e** | **This retro** | pending |

## Root cause + fix summary

**The problem**: `rag/templates/docx_renderer.py::_render_marker_line`
transforms `<<MUST item:A.5.1:approval_signatory>>` → visible-but-
unrecognizable `◆ Required element — approval signatory` labels in
the downloaded .docx. Beautiful for humans, but on re-upload:

- The machine-readable `<<MUST>>` marker is **gone from the docx text**
- No code path in `rag/intake/readers.py` recognized the ◆ shape
- The templated fast-path (`_extract_templated` in extractor.py)
  found zero markers, returned None, fell through
- Consensus extraction then matched **template scaffolding** (title
  heading, "◆ Required element — X" labels, "Why: 27002..." citations,
  advisory disclaimer prose) against random control fingerprints
- Result: high-confidence noise on wrong controls; customer's real
  evidence (CEO name, date, version) invisible to the system

**The fix** (Ship 50'.a):

- **L2 (reader-side reconstruction)**: In `_read_docx`, after mammoth
  produces markdown, detect ArionComply-rendered docx via the
  attribution line ("Generated <date> · <ref> · <std>") + ≥1 ◆ label.
  When detected, rewrite the markdown to emit `<<MUST item:CTRL:slug>>`
  markers + `<!-- EDIT-ZONE-START/END -->` brackets so the templated
  fast-path fires unchanged. Filename fallback for the ref when the
  attribution line is missing. Strips Why-citations + Click-placeholders
  as they carry no tenant evidence.

- **L1 (extractor-side defensive filter)**: In `_looks_like_field_or_header`,
  added an `arion_scaffold` shape. Catches ◆ marker labels + "Advisory
  template" disclaimer + attribution line + "Why:" citations + "Click
  to enter" placeholders + "▽ Enter your evidence" / "△ End of" rails.
  Fires when L2 partially degrades (customer renamed file AND deleted
  attribution) so scaffold lines still can't become consensus evidence.

## The Q&A restructure (Ship 50'.b + 50'.c)

Once round-trip worked, the fill-in UX was worth investing in. The
old template shape asked customers to fill in imperative-headed
sections like "1. Signatory at top-management level (CEO...)" — a
descriptor, not a prompt. Customers weren't sure what to type.

New shape (v2 template) — reference implementation on A.5.1
management_approval:

```
## How to use this template
[4 paragraphs — what this is, how to fill in, why ◆ matters, next steps]

## Question 1: Who is the top-management signatory approving this policy?
**Enter:** the signatory's name and title.
**Examples:** `Jane Doe — CEO` · `Board of Directors (as delegated...)` · ...

<<MUST item:A.5.1:approval_signatory>>
<<TEXT>>

> **Why we ask:** 27002 §5.1 requires approval by management...
```

Key structural shifts:

- **Section heading = the question** (`Question N: <question>`)
- **Bold-prefix hints** (`**Enter:**` / `**Examples:**`) — cleaner in
  Word than multi-line `_..._` italics which the docx_renderer
  doesn't collapse across line breaks
- **`<<MUST>>` marker preserved verbatim** — Ship 50'.a L2 depends on
  the ◆ label surviving so the marker can be reconstructed
- **"Why we ask" as blockquote below the answer** — reads as context,
  not as part of the question. Was above the marker in v1; auditor
  citation belongs after evidence, not before

## Delivery velocity

- Session length: ~2h
- 4 sub-arcs, one commit per phase
- Zero mid-arc rollbacks
- Every change verified end-to-end on the customer's actual docx
- Customer's Stage-1 queue went from **15 wrong-control noise findings**
  to **4 correct-control auto-approved findings** on the same file

## Codified 4 lessons

### 1. Human-friendly rendering breaks machine-readable round-trip
Docx_renderer transforming `<<MUST>>` → `◆ Required element — <slug>`
was pure UX improvement — until customers started uploading filled
templates. The pretty label was one-way. Load-bearing rule: **if
downstream code needs to parse a marker on re-read, either preserve
it verbatim OR detect the visible transformed shape on read**. The
50'.a L2 reconstruction shows how to do the latter cheaply.

### 2. Scaffolding-as-evidence is a broader failure mode than heading-only
Ship 49'.a fixed one shape of scaffolding-as-evidence (bare markdown
headings). Ship 50'.a's L1 filter generalizes: any line that's
recognizably OUR template chrome should never become tenant
evidence. The `_ARION_SCAFFOLD_RE` combined regex is small (six
alternatives) but blocks a large class of false positives.

### 3. Q&A structure > imperative structure for fill-in accuracy
The v1 template heading "1. Signatory at top-management level (CEO,
board chair, or delegated equivalent)" is a DESCRIPTION of what
goes in the section. The v2 heading "Question 1: Who is the
top-management signatory approving this policy?" is an INSTRUCTION
to the reader. Descriptive headings pass through peripheral vision;
question headings command attention. Also: bold-prefix hints
(`**Enter:** ...`) render more reliably in docx than italics
across multiple lines.

### 4. Diagnose downstream from real data, not from the code
The customer's Stage-1 queue was the ground truth. Reading it
revealed the failure mode — three uploads, all template-based, one
bound cleanly (xlsx via `_arion_meta`), one bound noise (docx via
consensus scaffolding). The pattern was invisible from the extractor
code alone. **Rule: when a dev-loop question is "does this work?",
check what actually shipped for a real customer BEFORE reading the
code path**.

## What Ship 50' did NOT do

- **Propagate v2 Q&A shape to the other 643 narrative templates** —
  A.5.1 is the reference implementation; curator picks the pattern
  up opportunistically when touching other templates. v1 shape
  still works end-to-end via 50'.a (marker + round-trip); v2 is
  UX-only.
- **Word bookmark preservation** — L2 handles the current visible-
  label detection well; hidden bookmarks would be more robust but
  bigger change. Deferred.
- **Xlsx template Q&A restructure** — xlsx round-trip already works
  via `_arion_meta` sheet; the register format is inherently Q&A
  (column headers = questions, rows = answers). No structural
  restructure needed.
- **Multi-line italic support in docx_renderer** — worked around by
  moving to bold-prefix hints in the v2 template. If a future
  template author writes multi-line italic hints anyway, they'll
  render with leading `_`. Fixable later if it matters.
- **Rate-limit or feature-gate the new templates** — v2 shape is
  the default going forward; no rollback path needed since v1 and
  v2 both work with L2 detection.

## Deferred / follow-on candidates

### Ship 51 candidates
- **Curator arc: migrate the other 643 narrative templates to Q&A
  shape**. Volume work; break into batches per framework (ISO 27001
  clauses first, then GDPR, then ISO 27701). ~5 min per template
  once the pattern is established.
- **Word bookmark preservation** — as a belt-and-braces addition to
  50'.a L2. Emit `<<MUST>>` as a hidden field code alongside the ◆
  label. Robust even if customer removes attribution + renames file.
- **Multi-line italic support in docx_renderer** — allow `_...\n..._`
  spanning multiple markdown lines. Requires accumulating italic
  state across line boundaries.
- **Tabular template Q&A audit** — xlsx templates already work but
  the Register/Guidance/_arion_meta sheet trio might benefit from
  a "How to use" text block on the Guidance sheet.
- **Prefill collapse indicator** — when a MUST is prefilled from
  prior evidence between ▽/△ rails, render a small "(prefilled
  from your Jan 2026 approval)" hint so the customer knows why the
  answer is already there.

### Longer-term
- **Template versioning UX** — surface template_version to the
  customer. When a customer downloads a template today, they get
  the current version; when they later re-download after a v3 lands
  they should know something improved.
- **Fill-in-then-preview loop** — customer fills in the docx,
  uploads a preview version, sees which MUSTs bound cleanly BEFORE
  submitting for Stage-1 approval. Would let them iterate without
  polluting the Stage-1 queue.
- **Q&A shape validator in `enrichment/templates/load_to_postgres.py`**
  — warn during template loading when a template doesn't follow the
  v2 shape. Enforce the pattern for new/edited templates.

## Related

- Ship 49'.a — extraction shape gate + Word TOC anchor scrub (this
  arc's immediate predecessor; same root cause class — scaffold
  content becoming evidence)
- Ship 48 — deployment diagnostics (the arc that caught the customer
  seeing garbled Stage-1 output during the demo prep pass)
- Ship 42 — evidence_group_id dedup (why the 3 upload attempts of
  the same file coalesced onto one client_documents row)
- Ship 33+ — consensus extraction (the fallback path that Ship 50'.a
  L2 now prevents from firing on template docs)
- `rag/intake/readers.py::_reconstruct_arion_markers` — the L2
  reconstruction
- `rag/intake/extractor.py::_ARION_SCAFFOLD_RE` — the L1 filter
- `db/templates/req__A_5_1__management_approval.md` — v2 Q&A
  reference template
