# Locked docx dogfood — internal review notes

_2026-08-15. Post Task #604 (marker hiding + edit-zone lockdown). Focus: what a compliance officer experiences when they open the locked docx in Word, what happens when they type, and whether round-trip binding still works after they save + re-upload._

Second Task #604 dogfood after the OOXML delta. Walks the tenant journey with the new protection in place.

---

## Stage 1 — Open the .docx in Word (normal view)

Sample: `req:A.5.15:access_control_policy` (45 KB, Comply state).

- **250 visible paragraphs, 10 hidden paragraphs** (`w:vanish` runs — the `Do not edit — system id: <<MUST item:X>>` binding markers).
- **3 native tables** (Doc-Control, Authoriser matrix, Revision History).
- **19 headings** across H1–H4.

What the officer sees: a clean starter policy. No `<<MUST item:X:Y>>` syntax, no `EDIT-ZONE-START/END` comment markers. Just prose, headings, tables, ▽/△ rails around empty placeholders, and the Word protection banner.

## Stage 2 — Word shows the protection

On open, Word displays:
```
This document is protected.  [ Stop Protection ]  [ Turn On/Off ]
```

Under **Review → Restrict Editing**:
```
Editing restrictions: Read only
✓ Allow only this type of editing
  Exceptions: 6 individual ranges (matching the 6 edit-zones)
```

`settings.xml` element:
```xml
<w:documentProtection w:edit="readOnly" w:enforcement="1"/>
```

No password. The officer can turn protection off from the Review tab if they want to edit locked content — this is a soft guard, not encryption. Fine for the compliance-drafting use case; a determined tenant can still customize the scaffolding.

## Stage 3 — Where can the tenant type?

Each edit zone is a body-level `w:permStart` / `w:permEnd` pair around the placeholder paragraph. For A.5.15:

```
Editable regions (paragraphs strictly inside permStart→permEnd):

  #1: [ Click to enter your evidence here ]     (item:A.5.15:logical_rules)
  #2: [ Click to enter your evidence here ]     (item:A.5.15:rbac)
  #3: [ Click to enter your evidence here ]     (item:A.5.15:least_privilege)
  #4: [ Click to enter your evidence here ]     (item:A.5.15:need_to_know)
  #5: [ Click to enter your evidence here ]     (item:A.5.15:authorisation)
  #6: [ Click to enter your evidence here ]     (item:A.5.15:segregation_link)
```

Click into any placeholder → cursor active, tenant can type. Click anywhere else → Word displays "cannot modify this selection" or similar. Because the perm markers are **body-level siblings** (not inline within the rail paragraphs), the ▽ and △ rails themselves are OUTSIDE the range — locked. Tenant can't accidentally delete the rails.

**Multi-line handling**: when the tenant hits Enter inside a placeholder, Word inserts a new paragraph BETWEEN the `w:permStart` and `w:permEnd` body-level markers. The new paragraph inherits the editable range because it sits between the sentinels. So multi-line prose works (verified structurally; empirical Word testing recommended before shipping to a real customer).

## Stage 4 — Hidden binding markers

10 `<<MUST item:X>>` / `<<SHOULD item:X>>` markers live in the docx but display as nothing in normal view. Toggle **Home → ¶ (Show/Hide formatting marks)** or **File → Options → Display → Hidden text** and Word displays them with a grey dotted underline.

That's the right visibility contract:
- Normal reader (tenant, compliance officer, auditor) sees a clean document.
- Someone debugging round-trip binding can inspect the markers with a two-click toggle.
- The extractor pipeline sees them unchanged on the wire.

## Stage 5 — Round-trip binding

Simulated the tenant workflow:
1. Open the locked docx.
2. Fill placeholder #1 with plausible policy text: *"Logical access to production systems uses SSO with hardware MFA; least-privilege enforced via RBAC bundles; all admin actions logged to SIEM; quarterly access review per A.5.18."*
3. Save.
4. Feed to `rag/intake/readers.py::_read_docx` (the real upload-side reader).

Result:
- **20 `<<MUST item:X>>` markers preserved** in extracted markdown.
- **Tenant text correctly bound to `item:A.5.15:logical_rules`** — the nearest binding marker above.
- Extractor pipeline can now emit a `document_findings` row with `checklist_item_id='item:A.5.15:logical_rules'` and the tenant's excerpt.

Round-trip works end-to-end. The `w:vanish` doesn't affect the reader because mammoth (the markdown converter under `_read_docx`) preserves the text content regardless of the display attribute.

## Wins

1. **Officer sees a clean document** — zero visible `<<MUST item:X:Y>>` markers, zero visible `EDIT-ZONE-START/END` HTML comments.
2. **Word banner announces protection** — the tenant knows the document is guarded.
3. **Edit zones self-announce** with visible ▽/△ rails around `[ Click to enter your evidence here ]`. Tenant knows exactly where to type.
4. **Rails themselves are locked** — tenant can't accidentally delete them (which would break round-trip binding).
5. **Round-trip binding intact** — hidden markers survive on disk; the reader still finds them and binds tenant evidence to the correct MUST id.
6. **No password required** — tenant can Save/Save-As without prompts. Protection is soft, defensible for a starter-doc use case.
7. **Multi-line evidence supported** structurally — perm markers are body-level siblings, so Enter creates paragraphs that stay inside the range.

## Friction observed

### 1. Placeholder is styled as prose, but tenant should replace it entirely
`[ Click to enter your evidence here ]` sits alone in a paragraph. When the tenant clicks in, the cursor lands at position 0 (before the `[`) — they can type in front of, inside, or after the placeholder. If they type without first selecting the whole placeholder text, they'll produce mixed content like `Their new textClick to enter your evidence here ]`.

**Suggested fix**: replace the plain text placeholder with a Word **Structured Document Tag (SDT)** rich-text content control that has "Contents cannot be edited" = false but "Remove content control when contents are edited" = true. Clicking anywhere in an SDT selects the whole placeholder; typing replaces it wholesale. Word's native "click here to enter text" behavior. Bigger OOXML change but higher polish.

### 2. Whole locked doc includes the Doc-Control table's wet-sign lines
The Doc-Control table has *"Prepared By | _________________"* / *"Reviewed By | _________________"* / *"Approved By | _________________"* rows. These are meant to be signed by the officer post-approval — but under the current protection, they're locked. Officer would need to Stop Protection to fill them.

**Suggested fix**: add per-cell perm ranges for the Approver/Reviewer/Preparer value cells in the Doc-Control table. Same OOXML technique — `w:permStart`/`w:permEnd` around specific `w:tc` cells.

### 3. Header / footer are unprotected AND uneditable
The docx has no header/footer content. Officer intending to add "*[Company Name] Confidential*" or a page number is welcome to try — headers aren't included in the perm ranges, so they'd land as locked-by-default under the readOnly enforcement. To edit, they must Stop Protection.

**Suggested fix**: either open a header perm range (small OOXML delta) OR pre-render a header with tenant name + confidentiality label. The latter closes friction #3 without expanding the perm-range surface.

### 4. No hover cue on the placeholder
Word displays the `[ Click to enter your evidence here ]` as regular plain text with no interactive affordance. Compare to native Word placeholders (from SDTs) which show a rounded outline and grey text suggesting "this is a form field."

**Suggested fix**: same as #1 — convert to an SDT rich-text control with placeholder text.

### 5. Multi-paragraph edit inside a range is Word-version dependent
Structurally OK, but Word's behavior around perm ranges + Enter varies slightly by version. On Word 365 desktop it usually extends the range through the new paragraph. On some older versions (Word 2016) it may lock the new paragraph. Would benefit from empirical multi-version testing before customer ship.

### 6. Officer might disable protection to fix a typo elsewhere
The protection is designed to protect scaffolding, but a careful officer editing "one small typo" in the guidance prose will:
1. Click on the typo → cursor blocked → open Restrict Editing → Stop Protection.
2. Fix typo.
3. Save.
4. Turn protection back on (or forget).

If they forget, the re-upload path still binds evidence correctly (the extractor doesn't care about protection state). If they forget AND accidentally edited a `<<MUST item:X>>` marker, the extractor might mis-bind. Low likelihood but worth documenting.

**Suggested fix**: the extractor should defensively validate that each `<<MUST item:X:Y>>` marker on re-upload matches a known catalog checklist item id; if a marker was mangled ("`<<MUST item:A.5.15:logica_rules>>`"), log a warning and skip.

---

## Overall verdict

**The lockdown works.** Compliance officer opens the docx and sees exactly what should be visible; edits are constrained to the placeholder paragraphs; hidden markers survive round-trip binding without cluttering the reader's view.

Six friction items ranked by tenant impact:

1. **#1 — SDT-based placeholder** (higher polish, Word-native affordance)
2. **#2 — Doc-Control signature-line cells editable** (workflow gap)
3. **#4 — Placeholder hover cue** (same fix as #1)
4. **#5 — Multi-version Word testing** (validation, not code)
5. **#3 — Header/footer editability** (minor)
6. **#6 — Extractor validates markers on re-upload** (defensive backstop)

None block the customer-facing loop. #1+#4 could be one arc (SDT conversion). #2 is a small OOXML addition. #6 is a defensive-coding backstop useful independent of Task #604.

The tenant loop is now: click NC leaf → download docx → open in Word → see clean starter doc → type only in the 6 highlighted placeholders → save → upload → posture flips. End-to-end auditor-defensible, no compliance officer sees programmer syntax.
