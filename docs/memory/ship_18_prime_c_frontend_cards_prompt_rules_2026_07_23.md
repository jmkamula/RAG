---
name: ship-18-prime-c-frontend-cards-prompt-rules-2026-07-23
description: "Ship 18'.c — frontend card renderer for structured answer payload + two JSON-mode prompt rules (guidance-standard names + newline-bullet listing) that closed all 3 Ship 18'.b regressions"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 18'.c — frontend card render + JSON-mode prompt rule
additions closing the 3 eval regressions surfaced by Ship 18'.b.
Commit `68a36af`.

## Frontend (static/arioncomply.html)

New helper `renderStructuredAnswer(s)` returns HTML for:

- **Intro card** (`.sa-intro`) — 1-2 sentence LLM framing text
  + primary_ref chip. Uses `renderMd` for the text so bullets/
  bold survive.
- **Action cards** (`.sa-actions` container of `.sa-action-card`)
  — one per remediation step; each has:
  * `.sa-card-title` — imperative header
  * `.sa-card-body` — LLM-authored guidance (renderMd'd)
  * `.sa-card-refs` — ref chip row (backend-scanned refs)
- **Related-control cards** (`.sa-related` container of
  `.sa-related-card`) — one per cited/derived ref:
  * `.sa-related-head` — ref chip + standard_display + verdict
    badge + optional DRAFT chip
  * `.sa-related-title` — control title from Neo4j
  * `.sa-related-rel` — relation_display label (small, muted)
  * `.sa-related-ev` — evidence_summary line
  * `.sa-still-needed` — inline `.sa-still-item` chips for
    each unnamed leaf
  * `.sa-related-drill` — `Open in dashboard →` link via
    `/#dashboard?control=X` hash + `setMode('dashboard')`

Cards ordered: intro → actions → related. Templates block
(Tier-4 starter kit) renders below related when present.

### Wiring changes

- `appendMsg(role, text, refs, ms, templatesBlock, structured)`
  gains new `structured` param. Prefers card render when
  `structured && structured.intro` present; falls back to prose
  bubble otherwise.
- Streaming path (`sendChat`): captures `answer_structured` SSE
  event into `finalStructured`; passed to `appendMsg` on stream
  completion.
- Backend `_dashboard_url` in `answer_augment.py` corrected from
  the design-doc's `/#dashboard/control/X` guess to the
  frontend's actual hash pattern `/#dashboard?control=X`.

### CSS additions

- `.sa-intro` — bubble matching `.msg-bubble` styling
- `.sa-actions` + `.sa-related` — flex-column containers
- `.sa-card` + `.sa-action-card` (purple left border) +
  `.sa-related-card` (gray left border)
- `.sa-badge` variants: `.sa-badge-nc` (red #D9534F, matches
  heatmap), `.sa-badge-ofi` (amber #EF9F27), `.sa-badge-comply`
  (green #7FB36F), `.sa-badge-na` (gray), `.sa-badge-unknown`
  (light gray)
- `.sa-draft-chip` — off-white background, small pill
- `.sa-still-item` — inline pill for each still-needed leaf
- `.sa-related-drill` — action-purple link

## Prompt rule additions

Ship 18'.b's initial eval regressed 3 cases; all closed by two
new rules in `LLM_OUTPUT_RULES` (`rag/casefile/answer_schema.py`):

### Rule 7 — GUIDANCE citations MUST name the ISO standard verbatim

```
7. GUIDANCE citations MUST appear by full ISO standard name in
   `intro.text`. When the OBLIGATIONS / GUIDANCE section mentions
   a specific ISO family standard (ISO 27002, ISO 27003, ISO
   27004, ISO 27005, ISO 27701, ISO 27017, ISO 27018, ISO 27552,
   ISO 27799), name it verbatim in the intro — "ISO 27005"
   (not just "the risk-management standard"). Auditors trace the
   guidance path by standard number.
```

Closes #222 (`what does ISO 27005 recommend...`) + #224
(`what does ISO 27004 say...`). In prose mode the LLM naturally
cited "ISO 27005" / "ISO 27004"; in JSON mode it compressed to
"the risk-management standard" / "the monitoring standard".

### Rule 8 — LISTING queries MUST bullet every item on its own line

```
8. LISTING queries — when the user asks "what must X contain",
   "what are the required items", "list the required elements",
   "what should X include": enumerate EVERY item from the
   OBLIGATIONS section (or ≥5 if the section carries more) as a
   NEWLINE-SEPARATED BULLETED LIST inside `intro.text` or a
   single `action.body`. Each item MUST be on its own line
   prefixed with "- " (hyphen space). Do NOT emit them inline as
   a comma-separated sentence — auditors read the bulleted list
   verbatim. The enumeration IS the answer for these queries.
   Example format for `intro.text`:
     "The ISMS scope statement must contain:\n- item one\n- item
      two\n- item three\n- item four\n- item five"
```

Closes #31 (`what must our ISMS scope statement contain?` —
`musts_listing` shape check requires ≥5 enumerated items on
their own lines). In prose mode the LLM naturally bulleted
each of 18 items; JSON mode compressed them into a single
comma-separated inline list. The explicit example in the rule
solved it — 18 bullets now emitted.

## Verified

Manual retest of the 3 failing queries after prompt-rule +
API restart:

| Case | Query | Before | After |
|---|---|---|---|
| #31 | "what must our ISMS scope statement contain?" | 0 bullets (inline commas) | 18 bullets |
| #222 | "what does ISO 27005 recommend for risk assessment methodology?" | no "27005" | contains "27005" |
| #224 | "what does ISO 27004 say about monitoring and measurement?" | no "27004" | contains "27004" |

Full re-eval: **231/232 PASS + 1 WARN (#200) + 0 FAIL** —
identical to Ship 15'.e baseline.

## Ship 14'.a addendum alignment

1. **Role split?** YES — verdict badge + relation label carry
   the role model into the UI. Program/extension controls
   render with their own verdict; obligation controls show
   `relation: demonstrated_by` when applicable.
2. **Parallel CaseFile view?** YES — UI reflects what the
   digest surfaced.
3. **Deterministic routing?** N/A — UI layer.
4. **Guidance-normative discipline?** YES — related cards
   carry `role` (guidance controls render distinguishably from
   program/extension).

## Lessons

1. **JSON-mode compresses; codify exceptions in prompt rules.**
   The 3 regressions all had the same root cause: what the LLM
   did naturally in prose mode got compressed in JSON mode.
   Fix was explicit rules with examples. Any output-mode swap
   should be followed by an eval re-run + prompt calibration
   round.

2. **Example format inline beats abstract prescription.** Rule 8
   works because it shows a literal
   `"...:\n- item one\n- item two\n..."` example. Rule 7 works
   because it enumerates all 9 relevant ISO standard IDs.
   Pattern: when JSON mode drops a prose behavior, give the LLM
   a copy-paste template.

3. **Frontend card render fell out of the same helpers as
   templates block.** Reusing existing chip/badge/drill-in
   idioms (`ref-tag`, `_applyNotifFocus`, `setMode('dashboard')`,
   `_POSTURE_BADGE` color palette) kept the diff small.

## Ship 18 progress

| Sub-arc | Status |
|---|---|
| 18'.a Design memo | ✓ (477ca39) |
| 18'.b Backend schema + LLM structured output | ✓ (c05e669) |
| **18'.c Frontend card renderer + prompt rules** | **✓ (68a36af, this doc)** |
| 18'.d Eval + arc retrospective | next |

## Related

- [[ship-18-prime-a-structured-answer-design-2026-07-23]] — design
- [[ship-18-prime-b-structured-backend-2026-07-23]] — backend
- [[ship-2-prime-j-preservation-footer-2026-07-16]] — prose
  footer this arc supersedes (card render carries same
  auditor-visible info)
- [[dejargonize-ux-pass-2026-07-01]] — the natural-language UX
  pattern Ship 18 extends to card structure
- [[tier4-starter-kit-arc-2026-07-02]] — precedent for a
  structured card block in the chat UI
- Ship 18'.d: eval + arc retrospective (final sub-arc)
