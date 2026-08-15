---
name: task-605-docx-signature-cells-2026-08-15
description: "Task #605 — closes docx lockdown dogfood friction #2. Wet-sign cells in the Doc-Control table (Prepared By / Reviewed By / Approved By) were locked under Task #604's readOnly protection; officers had to Stop Protection to sign. Fix: detect signature cells by content pattern (^_{3,}$) and wrap them with per-cell w:permStart/permEnd."
metadata:
  type: project
  ship: templates
---

# Task #605 — Signature cells editable inside Doc-Control table

## Motivation

Task #604 lockdown left one workflow gap surfaced by the dogfood
walk-through:

> **#2 — Doc-Control signature-line cells editable.** The
> Doc-Control table has *"Prepared By | ___________"* /
> *"Reviewed By | ___________"* / *"Approved By | ___________"*
> rows. These are meant to be signed by the officer post-approval —
> but under the current protection, they're locked. Officer would
> need to Stop Protection to fill them.

The officer's job is to review the draft, then sign. If Word blocks
the signature and the officer has to disable protection, they may
forget to re-enable it (dogfood friction #6). Better: preserve
protection AND let the signature cells stay editable.

## What shipped

`_render_pipe_table` (the pipe-table → native Word table lifter
from Task #603) grew a `perm_counter` parameter and a
signature-cell detector:

```python
_SIGNATURE_CELL_RE = re.compile(r"^_{3,}$")
```

Any cell whose stripped content matches (3+ underscores, nothing
else) gets wrapped with matching `w:permStart` + `w:permEnd`
elements inside the `<w:tc>`. Under document protection those
cells stay editable while the rest of the table stays locked.

The walker's `_perm_counter` (established Task #604) threads
through — signature-cell ranges share the same counter, so id
collisions can't happen across the doc's edit zones.

Non-signature cells (regular data rows, headers) get no
permStart/permEnd — remain locked as before.

## Verified on A.5.15

```
Doc-Control table:
     row0 col0: 'Field'
     row0 col1: 'Value'
     row1 col0: 'Document No.'
     row1 col1: 'POL-A.5.15-Rev04'
     row2 col0: 'Revision'
     row2 col1: 'Rev04'
     row3 col0: 'Revision Date'
     row3 col1: '15 Aug 2026'
     row4 col0: 'Prepared By'
  🔓 row4 col1: '___________________________'
     row5 col0: 'Reviewed By'
  🔓 row5 col1: '___________________________'
     row6 col0: 'Approved By'
  🔓 row6 col1: '___________________________'
```

Body-level perm ranges: 6 (edit zones, from Task #604).
Cell-level perm ranges: 3 (signature cells, from Task #605).
Total editable regions per template: 9. Everything else locked.

## Files touched

- `rag/templates/docx_renderer.py` — `_SIGNATURE_CELL_RE`
  constant, `perm_counter` param on `_render_pipe_table`,
  cell-level permStart/permEnd emission in the data-row loop,
  walker's sentinel dispatch threads the counter through.

Zero schema. Zero renderer.py changes. ~25 LOC net.

## Design notes

**Why `^_{3,}$` and not empty cells?** An empty cell in a
curator-authored table could be many things — an unset value, a
column header nobody filled in, an intentional blank. Underscore-
only content is unambiguous: it's a wet-sign convention. If a
curator wants an empty cell to be officer-fillable, they can
change the source markdown template to emit `___________` — no
code change needed.

**Why per-cell perm ranges and not a whole-row permission?** OOXML
supports `w:permStart`/`w:permEnd` around any block content
including whole cells, whole rows, or ranges spanning cells. The
per-cell shape is the tightest: the "Prepared By" label cell
stays locked, only the value cell is typable. If we ranged the
whole row, an officer could accidentally overwrite the "Prepared
By" label with their name. Cell-level containment prevents that.

**Why not use SDT content controls instead?** SDT rich-text
controls (dogfood friction #1) would give better UX (click-to-
select whole placeholder, hover cue). Same OOXML technique, more
code. Deferred as its own arc — signature cells alone don't
justify SDT complexity.

## Codified lesson

### 42. Protection is negotiation with the user

The Task #604 lockdown was "everything locked except the ▽/△
rails." The dogfood walk-through surfaced two workflow gaps: the
tenant needs to sign (Task #605) AND the tenant might want to
customize scaffolding (friction #6). Absolute lockdown doesn't
serve either. The right shape is: **default-locked with named
exceptions for known workflows.**

Rule: for user-facing artifacts, model the protection as a
positive list of permitted actions ("what CAN the tenant do?")
rather than a negative list ("what CAN'T the tenant do?"). The
positive list is easier to reason about — you audit it by
walking the list.

## Follow-ons

Remaining docx lockdown dogfood items:
- **#1, #4** — SDT-based placeholder (Word-native affordance).
  Own arc; higher polish but bigger change.
- **#3** — Header/footer editability (pre-render tenant name +
  confidentiality label; or open a permission range).
- **#5** — Multi-version Word testing before customer ship.
- **#6** — Extractor validates markers on re-upload (defensive).

Task #605 closes the immediate workflow gap. The remainder are
polish or defensive backstops.
