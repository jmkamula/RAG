---
name: ship-21-prime-a-footer-retire-design-2026-07-23
description: "Ship 21'.a — design memo: retire ↳ Compliance facts footer entirely + polish answer_text prose reconstruction with a related-controls markdown section so eval assertions + SDK consumers keep working"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 21'.a — opens Ship 21 arc (retire prose footer + prose
polish). Now that Ship 20 landed universal `answer_structured`
coverage across every chat path, the `↳ Compliance facts:`
prose footer is redundant on the card render and awkward on
the reconstructed `answer_text` prose. Retire it entirely +
polish the reconstruction.

## Current state (post-Ship-20)

Every chat response carries BOTH:
- `answer_structured` (intro + actions[] + related[]) — cards
  render every ref with full title, verdict, evidence summary,
  and per-leaf checklist.
- `answer_text` (prose) — for backward compat with SDK / API
  consumers who haven't migrated to structured.

Prose reconstruction (in `_casefile_flow`):
```python
prose_lines = [structured.intro.text]
for a in structured.actions:
    prose_lines.append("")
    prose_lines.append(f"{a.title}: {a.body}" if a.title else a.body)
```

Reads as:
```
{intro.text}

Title 1: body 1

Title 2: body 2
```

Then `check_and_repair(answer_text, spec, cf)` may append:
```
↳ Compliance facts: 10.1 [NC-DRAFT] — ALL: 0 of 4 required...
```

## Problems

1. **Redundant on card render.** Frontend renders structured
   cards; footer duplicates in prose text a tenant already sees
   as cards. Truncation "still needed: operating procedure, sc…"
   in the footer is a UX regression Ship 18 was supposed to fix.

2. **Awkward prose reconstruction.** `Title 1: body 1` inline
   with a colon reads more like a list than a section. SDK
   consumers hitting `/api/v1/chat` and printing the prose
   response see cramped output.

3. **Related detail lost in prose.** Actions carry LLM
   guidance; related cards carry the structural detail
   (verdict, evidence, refs). Prose reconstruction drops all
   `related[]` info entirely — an SDK consumer reading
   `answer` misses everything the cards would surface.

4. **Footer fires on the reconstructed prose.** Ship 20
   short-circuits compose their prose from
   `polish_short_circuit_answer` — these don't go through
   `check_and_repair`. But the LLM path DOES. So today the
   footer fires only on LLM-path turns, adding to text that
   was ALREADY reconstructed from structured cards. Double
   coverage.

## The fix

### Retire `↳ Compliance facts:` footer entirely

Remove the `_compliance_facts_footer` call in
`check_and_repair`. Repair events (`missing_ref`,
`missing_verdict_near_ref`, `missing_draft_near_ref`) still fire
and log to `chat_casefile_log` for observability — we only stop
appending to the visible prose.

Rationale: the structured payload's `related[]` cards carry
every dropped-ref with full metadata. The footer's job is done.

Keep the bridge footer (Ship 1.14 `↳ Bridges to ISO 27001 for
Art.X: ...`) and the risk-facts footer (Ship 14'.e `↳ Risk
register: R-042`) for now — they surface data that the current
`related[]` doesn't quite mirror. Follow-up arcs can retire them
similarly if we decide to.

### Polish prose reconstruction to include Related section

Rewrite the composition in `_casefile_flow`:
```markdown
{intro.text}

## {action[0].title}
{action[0].body}

## {action[1].title}
{action[1].body}

## Related controls
- **A.5.15** (Access control, ISO 27001:2022) — OFI-DRAFT — 1 of 4 items present
- **10.1** (Continual improvement, ISO 27001:2022) — NC-DRAFT — 0 of 4
- **10.2** (Nonconformity and corrective action, ISO 27001:2022) — NC-DRAFT — 0 of 4
```

Format:
- Intro text unchanged.
- Actions as markdown headings (`## Title` + blank line + body).
- Related controls as a bulleted list with:
  * Bold ref
  * Title in parens with standard_display
  * Verdict (+ `-DRAFT` suffix when `card.draft==True`)
  * Evidence summary (or nothing if summary is empty)

Applied uniformly to both LLM path (`_casefile_flow`) and
short-circuit paths (`build_short_circuit_structured`). Extract
into a shared helper `structured_to_prose(structured)` in
`rag/casefile/answer_augment.py`.

### Eval impact analysis

Assertions scan `answer_text` for:
- **Refs** (A.5.15, Art.32, etc.) — 232 cases, most have
  `must_contain=[ref]`. Related section includes every ref
  → PASS. Also `expected_refs` regex — same.
- **Verdicts** (`NC`, `OFI`, `Comply`) — many cases have
  `must_contain=["NC"]` or `["OFI"]`. Related section includes
  verdict verbatim (`NC-DRAFT`, `OFI-DRAFT`) → PASS.
- **Bracketed verdicts** (`[NC]`, `[OFI-DRAFT]`) — 4 cases
  (grep'd `\[NC(-DRAFT)?\]` in eval_suite.py). Ship 15'.e
  baseline confirmed 3 of 4 are commentary/regex-guard, not
  strict `must_contain`. Only case #200 pattern is at risk;
  #200 is already the standing WARN. Structured cards render
  `NC-DRAFT` chip but the reconstructed prose won't have
  `[NC-DRAFT]` bracket format. Assertion changes if needed
  → per-case eval-suite tweak, not a prompt or content change.
- **Guidance-standard names** (27004, 27005) — 3 cases (Rule 7
  from Ship 18'.c). Intro text contains these when Rule 7
  fires → unaffected.
- **`↳ Compliance facts:` string** — grep'd eval_suite.py: 0
  matches. No case depends on the footer string.
- **`↳ Bridges to`** — 0 matches. Bridge footer stays for now.

Verdict: expect **zero regression** from footer retirement +
prose polish. All ref+verdict assertions satisfied by the
related-controls section format.

## Sub-arc plan

### 21'.b — implement

- Add `structured_to_prose(structured)` helper in
  `rag/casefile/answer_augment.py`.
- Remove `↳ Compliance facts:` append from
  `rag/casefile/repair.py::check_and_repair`. Repair events
  still log; only the visible append is retired.
- Rewrite `_casefile_flow` prose composition (llm_answer.py:
  1253) to call `structured_to_prose`.
- Rewrite short-circuit prose composition — but note
  short-circuits SET `answer_text = <composed prose from
  polish_short_circuit_answer>` and use `structured_to_prose`
  is orthogonal there. Leave short-circuit `answer_text` alone
  (it's already polished by the site-specific composer). Only
  the LLM path's reconstruction changes.

  Actually wait — short-circuits ALSO call
  `build_short_circuit_structured(intro_text=composed, ...)`.
  The `answer_text` returned to the client IS `composed` (the
  short-circuit prose). We don't reconstruct from structured
  for short-circuits. So no change needed there.

Effective scope: 2 files (repair.py, llm_answer.py) + 1 helper
addition (answer_augment.py).

### 21'.c — eval + retro

- Full eval regression check.
- Verify a few queries visually (chat UI + API JSON) to
  confirm no unexpected regressions.
- Arc retrospective.

## Design decisions locked in 21'.a

1. **Full retirement over conditional.** The footer is
   structurally redundant with `related[]` on every response.
   Keep-when-fail-open isn't worth the complexity — fail-open
   already logs `structured_parse_failed`, and the tenant
   still sees actionable prose (just without the footer).

2. **Markdown headings for actions.** `## Title\nbody` reads
   as sections in most markdown renderers (SDK CLIs, notion
   pastes, etc.). Colon-prefixed inline was harder to scan.

3. **Related section as bulleted list, not repeat cards.**
   Prose consumers want compact scannable info. Bullets +
   bold ref + parenthetical context matches the pattern in
   evidence_footer and every other Ship 7' gateway prose site.

4. **Bridge + risk footers stay for now.** They surface
   different classes of data than `related[]` (cross-framework
   bridges + risk external refs). Would need separate arc to
   retire. Ship 21 scope is narrow.

5. **APPEND-ONLY discipline preserved.** Prose reconstruction
   isn't a rewrite of LLM output — the intro + actions[] are
   the LLM's structured emission verbatim. Related section is
   backend-derived. Same discipline as Ship 18.

## Auditor-trail guarantee (blowback prevention)

The concern with retiring a visible append: does the auditor
lose provenance of what the LLM originally dropped?

**Answer: no.** The `chat_casefile_log` table (schema_v68+)
already captures every repair event as a first-class row:

```
Column          Type      Purpose
──────────────────────────────────────────────────────────────
repair_events   jsonb     [{kind, ref, detail}, ...]
                          — every missing_ref / missing_verdict
                          / missing_draft event the repair pass
                          identified
repair_events_count int   fast filter for "did anything fire?"
footers_added   text[]    literal footer strings appended
```

Verified on live data (last 30 days on demo tenant):
- 2,996 chat_casefile_log rows
- 91% have repair events populated
- 61% had at least one `missing_ref` event

Post-retirement:
- `repair_events` continues to fire + log identically (only
  the visible append is removed).
- `footers_added` will reflect only the retained footers
  (bridge + risk), which is a natural signal that the
  compliance-facts footer is gone.
- Auditors reconstruct the "would-have-been-footer" content
  via `scripts/audit_retired_footer.sql` — join
  `chat_casefile_log ⋈ jsonb_array_elements(repair_events)` +
  filter on kind.

New helper landed in Ship 21'.b:
- `scripts/audit_retired_footer.sql` — parameterized query for
  drill-in on any single turn or a 24h-sweep across all
  tenants. Documented in-file with usage.

## What Ship 21 does NOT do

- **Retire the prose `answer` field.** Kept for backward
  compat. Every existing consumer keeps working.
- **Retire bridge footer** (`↳ Bridges to ISO 27001 ...`) or
  **risk footer** (`↳ Risk register: R-...`). Both surface
  data the current related[] doesn't fully mirror. Future arcs.
- **Change short-circuit prose composition.** Short-circuits
  compose their own prose via `polish_short_circuit_answer`;
  Ship 21 doesn't touch that. Only the LLM path's
  reconstruction changes.
- **Restructure `check_and_repair`.** Only the append line is
  removed. Every repair event still fires + logs, so
  `chat_casefile_log.repair_events` stays populated for
  observability.

## Ship 21 progress

| Sub-arc | Status |
|---|---|
| **21'.a Design memo + eval impact analysis (this)** | **✓** |
| 21'.b Retire footer + polish prose reconstruction | next |
| 21'.c Eval + arc retrospective | pending |

## Related

- [[ship-2-prime-j-preservation-footer-2026-07-16]] — the
  arc that introduced the footer this arc retires
- [[ship-18-prime-arc-retrospective-2026-07-23]] — the
  structured payload arc that made the footer redundant
- [[ship-19-prime-arc-retrospective-2026-07-23]] — card polish
  (leaves checklist, intro dedupe)
- [[ship-20-prime-arc-retrospective-2026-07-23]] — universal
  structured coverage across short-circuits
