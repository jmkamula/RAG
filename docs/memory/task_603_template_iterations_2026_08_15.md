---
name: task-603-template-iterations-2026-08-15
description: "Two template iterations after the arc closer + dogfood: (1) default to empty edit zones — don't echo prior evidence inside the template since the client can see it on the dashboard; (2) lift markdown pipe-tables into native Word tables in the docx renderer."
metadata:
  type: project
  ship: templates
---

# Task #603 iterations — post-dogfood templates polish

Two direct-response iterations after the dogfood report (2026-08-15):

## Iteration 1 — Empty edit zones by default

The A.5.15 dogfood surfaced that every edit zone echoed the tenant's
prior extracted evidence:

```
▽ Enter your evidence for "logical rules" below ▽
From Information Security and Data Management Process.docx (uploaded document, 2026-06-24):
  Implement role-based access control (RBAC) to restrict access…
From Access Control Policy.docx (uploaded document, 2026-06-24):
  Access to information systems must be granted based on the principle of least privilege.
  …
△ End of "logical rules" △
```

The tenant already has those documents visible on the Dashboard.
Echoing extracted excerpts inside the template is redundant
clutter — the tenant scans past them to find the empty space to
write in.

**Fix**: flip the `empty` parameter default from `False` → `True`
on both template endpoints (`GET /api/v1/templates/{leaf_id}` and
`GET /api/v1/templates/{leaf_id}/download`). Prefill is now opt-in
via `?empty=false` — the escape hatch is preserved for internal
tooling or curator debug, but the default tenant experience is a
blank edit zone.

Verified on Arion A.5.15: default download 20,109 chars with 0
`uploaded document` echoes; `?empty=false` restores the 23,447-char
prefill-on behavior with 14 echoes.

Both prose edit zones and record-shape TABLE-COLUMNS zones drop
the tenant's prior content — the `prefill=False` path already
suppresses both `_apply_prefills_and_wrap_edit_zones` prose
substitution AND `_prefill_table_zones` per-row replay.

## Iteration 2 — Pipe-tables render as native Word tables

The doc-control block at the top of every template:
```
| Field | Value |
|---|---|
| Document No. | POL-A.5.15-Rev04 |
| Revision | Rev04 |
| …
```

Rendered as literal `|` characters in the docx output. Compliance
officers open the Word doc and see pipe syntax instead of a table.

Root cause: `render_template` (in `renderer.py`) substitutes
`<<DOC_CONTROL>>` markers into markdown pipe-tables. That body_md
gets passed to `render_template_docx`, which walks line-by-line
and has no markdown-pipe-table parser. The dead code path at
`docx_renderer.py:524` for `<<DOC_CONTROL>>` never fires because
the marker was already consumed upstream.

**Fix**: add a pre-pass to `render_template_docx` that finds every
GFM pipe-table (header row + separator row + data rows), replaces
it with a `<<TABLE::N>>` sentinel, and stashes the parsed spec.
The main walker dispatches on the sentinel via `_render_pipe_table`,
which calls `doc.add_table()` and populates cells via
`_add_runs_with_formatting` (so cell-level `**bold**` / `_italic_`
markdown gets parsed instead of showing as literal asterisks).

Verified on A.5.15 docx: 3 native Word tables emerge (Doc-Control
7×2, Authoriser matrix 6×3, Revision History 2×4), zero literal
pipe rows leftover, bold-formatted cell content renders as native
Word bold runs.

The pre-pass approach also handles any curator-authored inline
tables (like the A.5.15 Authoriser matrix) without needing per-
marker plumbing. General fix, single site.

## Files touched

- `api_server.py` — 2 endpoint signatures + docstrings (default flip).
- `rag/templates/docx_renderer.py` — ~90 LOC for pipe-table
  detector + parser + native emitter + walker dispatch.

Zero schema. Zero renderer.py changes for iteration 2 (the
markdown pipe-tables are the correct output; docx just needed to
recognize them).

## Codified lesson

### 40. Dead-code paths in a pipeline are load-bearing bugs

The docx renderer had a `<<DOC_CONTROL>>` handler at line 524 that
looked correct in isolation — but it never fired, because
renderer.py had already substituted the marker for a markdown
pipe-table one layer up. Neither layer was wrong; the composition
was. The docx output silently degraded to literal `|` characters
until a compliance officer opened the Word file and saw it.

Rule: when two layers of a pipeline both handle the same marker,
one of them is dead. If the dead one is downstream, the "fix" that
was already there does nothing. Regularly audit which markers
survive to which layer — the ones the code claims to handle should
be the ones that actually reach it.

## Follow-ons

- docx renderer per-bullet parity — still open from Task #577
  retro; when a docx tweak lands next, port the ☑/☐ per-bullet
  marks + MUST-level tick indicator too.
- xlsx renderer for tabular templates has its own tenant profile /
  guidance path — unaffected by this arc.
