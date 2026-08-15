# Template docx output dogfood — internal review notes

_2026-08-15. Post Task #603 iterations. Docs walked: `A.5.15:access_control_policy` (Comply, mix ☑/☐), `A.5.1:isp_policy` (partial), `A.5.24:incident_response_procedure` (mostly missing)._

Focus: what a compliance officer sees when they open the downloaded `.docx` in Word. First dogfood was the loop shape end-to-end. This one is on the docx artifact quality specifically after Task #603 lifted pipe-tables to native.

---

## What the docx looks like now

Sampled three narrative templates. All 3 come out with the same structural shape:

| Leaf                  | Bytes | Native tables | Paras | ☑ per-bullet | ☐ per-bullet |
|-----------------------|------:|--------------:|------:|-------------:|-------------:|
| A.5.15 access control | 45 KB |             3 |   270 |          10 |           14 |
| A.5.1  ISP policy     | 43 KB |             3 |   203 |          14 |           16 |
| A.5.24 IR procedure   | 47 KB |             3 |   323 |          11 |           46 |

Every doc has:
- **Doc-Control table** (Doc No / Rev / Rev Date / Prepared / Reviewed / Approved wet-sign slots) — native Word table, 7 rows × 2 cols, bold labels.
- **Revision History table** — native, 2 rows × 4 cols, seeded with the current version.
- **Curator-authored inline tables** (e.g. A.5.15's Authoriser matrix) — native, cell formatting preserved.

Zero literal `|` pipe rows anywhere across the sample. Task #603 iteration 2 successful.

## Walkthrough of A.5.15 docx (compliance officer view)

```
# Access Control Policy — drafted for Arion Networks

  Advisory template. A starting draft to help your compliance journey…
  Generated 2026-08-15 · A.5.15 · ISO/IEC 27001:2022
  ─────────────────────────

## How to use this template
  What this is. A starter draft…
  How to fill it in. Each section below asks one question…
  Leave the ◆ markers alone…
  When you're done. Save and upload the file back through the Documents tab…

  ┌── Table 1 (Doc-Control): 7 rows × 2 cols
  │  Field  |  Value
  │  Document No.  |  POL-A.5.15-Rev04
  │  Revision  |  Rev04
  │  Revision Date  |  15 Aug 2026
  │  Prepared By  |  _______________________
  │  Reviewed By  |  _______________________
  │  Approved By  |  _______________________

## What this template gives you
## When to use it
## Prerequisites
  Foundational
  •  ISO 27001:2022 4.3 — ISMS Scope Statement
  •  Why: …
  •  Good enough: …
  Direct upstream
  •  ISO 27001:2022 A.5.9 — Asset Register
  •  Why: …
  •  Good enough: …
  …

## Cross-references
  Implements
  •  GDPR Art.32.1.b — Security of processing — 1(b)
     Access control implements confidentiality…
  •  GDPR Art.5.1.f — Principles relating to processing of personal data — 1(f)

## 1. State physical access rules   (N/A on Arion cloud-only)
  Not applicable to your scope. Cloud-only operations…
  ◆ Required element — physical rules
  Do not edit — system id: <<MUST item:A.5.15:physical_rules>>
  Standard text: Physical access rules…
  [Not applicable to your scope — no evidence required.]

## 2. State logical access rules
  ◆ Required element — logical rules
  Do not edit — system id: <<MUST item:A.5.15:logical_rules>>
  Standard text: Logical access rules…
  ✓ Good: "Logical access rules: (a) All production system access requires SSO…"

  📎 Best practice ✓ — covered:
    ☑ Document all systems, applications, and network segments…
    ☑ State the specific rules for granting, changing, and revoking access…
    ☐ Assign responsibility for approving access requests to a named individual…
    ☐ Cross-reference the policy with supporting procedures or workflows…
    ☐ Record the latest approval of the access control policy…

  ▽ Enter your evidence for "logical rules" below ▽
    [ Click to enter your evidence here ]
  △ End of "logical rules" △

## 3. Make RBAC the default access model
  … (same shape, MUST-level ✓, 3 ☑ / 2 ☐ per-bullet)

## 4. State the least-privilege principle
## 5. State the need-to-know principle
## 6. Define authorisation rules
  ✓ Good (table):
  ┌── Table 2 (Authoriser matrix): 6 rows × 3 cols   ← lifted from body markdown
  │  Asset class            | Authoriser                | Approval cadence
  │  Public / Internal systems | Line manager           | Per provisioning request
  │  Confidential systems      | Asset owner + line mgr | Per request + annual re-attest
  │  …

## 7. Link to segregation of duties (A.5.3)
  📎 Best practice ◐ — partly covered:      ← MUST-level ◐ from SSoT
    ☐ Cross-reference the section…
    ☐ Document explicit statements…
    …

## Recommended additions

### Emergency / break-glass access
  ◆ Recommended addition — emergency access
  Do not edit — system id: <<SHOULD item:A.5.15:emergency_access>>

### Third-party / contractor access
### Periodic review cadence

## Revision history
  ┌── Table 3 (Revision History): 2 rows × 4 cols
  │  Version | Date       | Description of Change             | Author
  │  04      | 15 Aug 2026| Initial issue / current version   |
```

## Wins

1. **Native Word tables** — Doc-Control, Revision History, and curator-authored inline matrices all emerge as `doc.add_table()` structures. Compliance officer can click a cell, edit inline, add rows, format. Task #603 iteration 2 delivered.
2. **Per-bullet ☑/☐ marks** — visible in Word as unicode glyphs. Compliance officer sees at a glance which auditor cues are addressed by their evidence.
3. **MUST-level state marker** on best-practice header (✓ / ◐ / — still needed) matches per-bullet distribution.
4. **N/A sections are preserved with explanation** ("Not applicable to your scope…") rather than silently dropped — auditor sees the section + reason.
5. **Prereqs render with Why + Good enough** as bulleted callouts under category headers.
6. **Cross-references** show inbound `Implements` bridges with the curator rationale.
7. **Italic markdown** (`_text_`) parses to Word italic runs — 45 italic runs in A.5.15, zero visible underscores leaking.
8. **Edit-zone rails** (`▽ Enter your evidence for X below ▽` / `△ End of X △`) surround the `[ Click to enter your evidence here ]` placeholder — the tenant knows exactly where to type.
9. **No asterisk leaks** in any of the 3 sampled docs — the `_add_runs_with_formatting` pass reliably parses `**bold**` into bold runs.
10. **Provenance HTML comment stripped** — no `<!-- Rendered for Arion Networks… -->` leaking to page 1.

## Friction observed

### 1. `<<MUST item:X:Y>>` markers visible as plain text
Each of the ~7 MUSTs per template has a line like:

> Do not edit — system id: `<<MUST item:A.5.15:physical_rules>>`

The markers must stay for round-trip binding (the extractor uses them to recognize which evidence belongs to which MUST on re-upload), but a compliance officer opening the Word doc sees programmer-y `<<...>>` syntax. Instructions clarify "Do not edit," but it still looks like a bug to non-technical readers.

**Suggested fix**: emit the markers as tiny grey italic text (or better, as Word bookmarks / hidden text markers that survive round-trip but don't display). Phase A of the docx renderer noted this exact deferral — "Phase B (round-trip) will move these to Word-native comments/bookmarks." Now would be a good time.

### 2. Prereq Why + Good enough render as separate top-level bullets
```
Foundational
• ISO 27001:2022 4.3 — ISMS Scope Statement
• Why: You need to know…
• Good enough: A documented scope statement…
```

The `Why:` and `Good enough:` lines should be **indented sub-info** under the prereq's ref+title, not sibling bullets. Currently they visually parse as if there are three prereqs (ISMS Scope, Why, Good enough) instead of one prereq with two attributes.

**Suggested fix**: `_render_prerequisites_block` in `docx_renderer.py` — render Why/Good_enough as continuation paragraphs with an increased left indent instead of `style="List Bullet"`.

### 3. `Standard text: ...` label is inline
```
Do not edit — system id: <<MUST item:…>>
Standard text: Logical access rules (systems, applications…)
```

The "Standard text:" label is a nested cue — it's the curator-authored standard text for what this MUST requires. Reads fine but could be more distinct. Compliance officers may skim past it thinking it's boilerplate. A small distinct visual treatment (indented italic block? Small caps label?) would help.

### 4. `✓ Good: "…"` examples render as regular prose
The template body has passages like:

> ✓ Good: "Logical access rules: (a) All production system access requires SSO via Okta…"

which show up as ordinary paragraph text in Word. The `✓ Good:` prefix carries meaning (this is a curator-provided example of what to write) but there's no visual distinction from surrounding prose.

**Suggested fix**: treat `✓ Good:` (and `✗ Not good:` if any) as blockquotes with a subtle background or left-border. Small effort, meaningful auditor-facing improvement.

### 5. Table cell content wrapping / column widths
A.5.15's Authoriser matrix table has content like *"Privileged production access | Engineering Manager + Asset owner | Per request + 90-day re-attest"* — reasonable but a table `autofit` in Word may not distribute widths well by default. Compliance officers may need to hand-tune column widths after opening.

**Suggested fix** (minor): after `doc.add_table()`, set explicit column widths proportional to header/content length ratios. Not critical but a "just works" polish.

### 6. No consultant preamble in docx?
The markdown template's tenant-visible preamble ("Advisory template. NOT an authoritative evidence guideline…") lands as a regular paragraph in Word. Fine, but doesn't visually stand out. In markdown viewers this typically renders as a blockquote (`>`). The docx renderer strips leading `>` or reformats them plain.

**Suggested fix**: detect the leading blockquote block (rendered via `include_header=True`) and render it as a Word "Intense Quote" or bordered box.

### 7. Section separator `─────────────────────` renders as literal em-dash line
The markdown's horizontal-rule-ish separator (`---` or a series of em-dashes) appears in the docx as a line of literal characters. Compliance officer sees an em-dash line rather than a proper horizontal rule.

**Suggested fix**: detect `---` (or ≥3-char em-dash) lines and insert a Word `p.paragraph_format.border_bottom = ...` instead of the literal chars.

---

## Overall verdict

**The docx artifact is much better after Task #603.** The three friction items closed by the arc (empty edit zones, native tables, per-bullet marks) transformed the download from "markdown-file-opened-in-Word-with-visible-syntax" to "a genuine compliance policy starter draft."

The remaining friction is mostly cosmetic + one structural (`<<MUST>>` markers visible). Priorities for future iteration:

1. **#1 — `<<MUST>>` markers to Word bookmarks / hidden text.** Phase A deferred this explicitly; Phase B was always going to be this. Right time.
2. **#2 — prereq Why/Good_enough indented under parent bullet.** Small change to `_render_prerequisites_block`.
3. **#4 — `✓ Good:` example blocks distinct styling.** Small readability win.
4. **#5, #6, #7** — small polish; batch when we next touch docx layout.

None block the template loop. The compliance officer using this today gets a document that's professional-enough to become the actual policy artefact after their own edits.
