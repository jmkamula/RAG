---
name: task-604-docx-lockdown-2026-08-15
description: "Task #604 — closes docx dogfood friction #1 (visible <<MUST item:X>> markers) and adds document-level protection so tenants can only type inside the ▽/△ edit-zone rails. Two OOXML tricks stitched together: `w:vanish` on marker runs + `w:documentProtection` readOnly with `w:permStart`/`w:permEnd` around edit zones."
metadata:
  type: project
  ship: templates
---

# Task #604 — docx marker hiding + edit-zone lockdown

## Motivation

Dogfood friction #1 (from `template_docx_dogfood_2026_08_15.md`):

> Each of the ~7 MUSTs per template has a line like:
>   *"Do not edit — system id: `<<MUST item:A.5.15:physical_rules>>`"*
> The markers must stay for round-trip binding (the extractor uses
> them to recognize which evidence belongs to which MUST on re-upload),
> but a compliance officer opening the Word doc sees programmer-y
> `<<...>>` syntax.

Coupled with the user's ask: *"we also need to lock down what the
user should not edit."* The tenant should type only inside the edit
zones; guidance prose, headings, tables, best-practice bullets, and
`<<MUST item:X>>` binding markers stay untouchable.

Both problems have OOXML answers.

## What shipped

### Marker hiding via `w:vanish`

Any paragraph containing `<<MUST item:X:Y>>` or `<<SHOULD item:X:Y>>`
gets its runs stamped with the OOXML `w:vanish` character property.
Word treats vanish text as hidden — invisible in the normal view,
visible only when the reader toggles "Show/Hide formatting marks"
or "Hidden text." The text survives on disk unchanged, so the
upload-side extractor still recognizes the marker for round-trip
binding. Zero pipeline change.

Applied at both paragraph-emitting branches: the default
`_add_paragraph` path AND the blockquote (`> …`) path — the N/A
section renders the marker line as a `Quote` block, so both need
the hiding check.

### Document-level protection + edit-zone permission ranges

`w:documentProtection` in `word/settings.xml` with `w:edit="readOnly"`
+ `w:enforcement="1"` (no password) locks the whole document. Each
edit-zone rail pair (▽ Enter your evidence for X ▽ / △ End of X △)
gets a matching `w:permStart` + `w:permEnd` with
`w:edGrp="everyone"` stamped inline on the rail paragraphs. Word
respects these permission ranges as editable-under-protection —
the tenant can type between the rails while everything outside
stays locked.

No password enforcement means the tenant can Save/Save-As without
being prompted; the protection is a soft guard that prevents
accidental damage to scaffolding but a determined tenant can
disable via Review → Restrict Editing → Stop Protection.

## Files touched

- `rag/templates/docx_renderer.py` — imports `OxmlElement` + `qn`;
  adds `_hide_runs`, `_add_permission_range`,
  `_enable_document_protection`, `_BINDING_MARKER_RE`; threads
  `perm_id` through `_render_edit_zone_marker`; walker tracks
  `_perm_counter`; `_add_paragraph` returns the paragraph so the
  walker can post-process.

Zero changes to `renderer.py`, api_server, or the extractor
pipeline. Round-trip binding on re-upload works unchanged because
the extractor sees the same text — it's just invisible in Word's
normal view.

## Verified across 3 templates

| Leaf                  | perm ranges | protection            | visible `<<>>` |
|-----------------------|------------:|:----------------------|---------------:|
| A.5.15 access control |         6/6 | readOnly, enforced    |              0 |
| A.5.1  ISP policy     |         5/5 | readOnly, enforced    |              0 |
| A.5.24 IR procedure   |         9/9 | readOnly, enforced    |              0 |

Every edit-zone gets matched `permStart` + `permEnd` ids. Every
`<<MUST item:X>>` / `<<SHOULD item:X>>` marker is inside a hidden
run.

## Codified lesson

### 41. OOXML has answers when python-docx doesn't

python-docx has no first-class API for `w:vanish`, `w:permStart`,
`w:permEnd`, or `w:documentProtection`. Those are all one-liners
via `OxmlElement(qn("w:name"))` + attribute setters + tree
manipulation. When a rendering requirement doesn't fit the
python-docx facade, walk the OOXML directly — the schema is well-
documented and the library exposes the underlying `_p`, `_element`,
`.settings.element` accessors precisely for this.

The alternative — patch python-docx or ship a whole new render
path — would be weeks of work. The OOXML delta was ~40 LOC.

## Follow-ons from the docx dogfood

Task #604 closes friction #1. Remaining docx dogfood items:

- **#2** — prereq Why / Good_enough render as sibling bullets
  (should be indented under parent). Small `_render_prerequisites_block`
  change.
- **#3** — `Standard text:` label needs distinct visual treatment.
  The blockquote handler already special-cases `_Standard text:_`
  → `Intense Quote` — could add label prefix styling.
- **#4** — `✓ Good:` example blocks render as regular prose. Small
  new blockquote-adjacent handler.
- **#5-#7** — table widths, preamble styling, `---` horizontal rules.
  Batch when we next iterate on layout.

None block the loop. Task #604 delivered the two friction items
that matter most for compliance officer trust: they see a clean,
lock-guarded starter document instead of raw programmer syntax.
