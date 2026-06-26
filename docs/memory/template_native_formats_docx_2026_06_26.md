---
name: template-native-formats-docx-2026-06-26
description: "SHIPPED 2026-06-26: Phase A .docx download for narrative templates. GET /api/v1/templates/{leaf_id}/download?format=docx produces a python-docx generated Word document with proper Heading 1/2/3, Quote / Intense Quote blocks, List Bullet, ☐/☒ checkboxes, inline bold/italic/code. python-docx chosen over pandoc — no system dependency. 400 with helpful message for tabular templates. Narrative leaves now downloadable in Word, tabular in Excel — compliance officers no longer need a markdown editor."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

`rag/templates/docx_renderer.py` + `?format=docx` on the existing
download endpoint + frontend split into native-format buttons.

The renderer walks the rendered markdown body line-by-line and maps
idioms to Word styles:

- `# Title` → Heading 1
- `## N. Section` → Heading 2
- `### Subsection` → Heading 3
- `> _Standard text:_ ...` → Intense Quote
- `> other quote` → Quote
- `- text` / `* text` → List Bullet (with indent for nested)
- `- [ ] text` / `- [x] text` → Normal with ☐/☒ prefix (real Unicode
  ballot box, not [ ])
- `**bold**` / `_italic_` / `` `code` `` → inline runs with proper
  formatting

Structural markers preserved as visible plain-text cues:
- `<<MUST item:X>>` → small Consolas line `[ MUST · item:X ]`
- `EDIT-ZONE-START / END` → tiny gray `⇣ EDIT START ⇣ (item:X)`
- `<<TEXT>>` → italic "[ Click to enter your evidence here ]"

Frontend (`static/arioncomply.html`): each leaf in the
evidence-class panel now shows the native-fit button:
- Tabular evidence_type → `📊 .xlsx`
- Narrative evidence_type → `📝 .docx`
- `.md` always available as the power-user / round-trip option

## Non-obvious decisions

### python-docx, not pandoc

pandoc is the obvious choice for md → docx, but it's a system binary
(Haskell) not on this VM and not pip-installable. python-docx is
already installed (1.2.0) and gives us full control over Word styles.
Cost: more code (~200 lines of line-by-line walker vs one subprocess
call). Benefit: no system dependency + we own the rendering quality.

### Markers stay visible, not as Word comments/bookmarks

Phase A goal is download-only. Word-native comments + bookmarks are
the right Phase B move (survive edits cleanly, addressable by API),
but they require comment-XML construction which adds complexity.
For Phase A, plain-text markers in Consolas at small size are
adequate — visible enough that tenants see them and (hopefully) edit
around them rather than through them.

### .docx for narrative only — 400 for tabular

Word handles narrative beautifully and tables clumsily. Tabular
templates (registers, matrices) are explicitly rejected with a
pointer at .xlsx. The check is `"TABLE-COLUMNS" in rendered.body_md`
— simple and survives the include_header strip.

### Checkbox regex order matters

`- [ ] Foo` is ALSO matched by the generic unordered-list regex
`^[-*]\s+(.*)$` — generic match wins if it runs first, leaking
"[ ] Foo" into the bullet text. Checklist regex MUST be tested
before the generic list rule. Caught and fixed during smoke (line
17 of the test doc was rendering as `[ ] Clause 5.2...` instead of
`☐ Clause 5.2...`).

## How hybrid templates render today

5.3 RACI / 6.1.3 SoA / Art.30 RoPA have TABLE-COLUMNS metadata + per-MUST
edit zones. They currently:
- `?format=xlsx` → renders the table portion ONLY (doc-level MUSTs
  excluded)
- `?format=docx` → 400 (because `TABLE-COLUMNS` is present)
- `?format=md` → full template with both portions

So the doc-level narrative MUSTs on hybrid templates are not yet
reachable via native-format download. Open as a follow-on chunk:
either extend the xlsx with a "Document Fields" sheet for the
narrative MUSTs, or ship a paired .docx alongside, or zip both.

## Roadmap

Phase A (this session):
- ✓ xlsx for tabular templates
- ✓ docx for narrative templates
- Next: hybrid templates' doc-level MUSTs in native format

Phase B (future):
- Round-trip uploads (.docx + .xlsx → marker extraction)
- Word-native comments/bookmarks for markers (vs plain text)

## Related

- [[template-native-formats-xlsx-2026-06-26]] — sibling work for
  tabular templates. Same endpoint, same frontend pattern.
- [[templates-v2-anchors-complete-2026-06-25]] — the 14 narrative
  v2 anchors this serves; their standard-text blockquotes become
  Intense Quote blocks in Word.
- [[evidence-class-breakdown-backend-2026-06-26]] — the panel the
  format buttons live on.
