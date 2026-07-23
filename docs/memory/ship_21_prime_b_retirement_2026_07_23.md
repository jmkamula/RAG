---
name: ship-21-prime-b-retirement-2026-07-23
description: "Ship 21'.b — retired ↳ Compliance facts prose footer + new structured_to_prose helper emits markdown reconstruction with a Related controls section"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 21'.b — implementation of the Ship 21 arc.
Commit `66247f4`.

## Three surgical changes

### 1. rag/casefile/repair.py — RETIRED footer append

Removed the `_compliance_facts_footer(...)` call from
`check_and_repair`. Repair events (`missing_ref` /
`missing_draft_near_ref` / `missing_verdict_near_ref`) still
fire above the retirement block and land in
`chat_casefile_log.repair_events` for auditor drill-in via
`scripts/audit_retired_footer.sql`.

`_compliance_facts_footer` helper kept in the file (removed the
call, not the function) — any future caller wanting to
reconstruct the string can import it.

Bridge footer + risk footer stay (surface different data
classes; future arcs may retire similarly).

### 2. rag/casefile/answer_augment.py — new structured_to_prose

Emits clean markdown from a `StructuredAnswer`:

```markdown
{intro.text}

## {action.title}
{action.body}

## Related controls
- **A.5.15** (Access control, ISO 27001:2022) — OFI-DRAFT —
  1 of 4 items present
- **10.1** (Continual improvement, ISO 27001:2022) —
  NC-DRAFT — 0 of 4
```

Related section included ONLY when `structured.related` is
non-empty (intro-only payloads stay clean). Bold ref + context
(title + standard_display) + verdict-with-DRAFT-suffix +
evidence_summary. Every related-card field surfaces in prose so
SDK/CLI consumers get complete detail.

### 3. rag/llm_answer.py::_casefile_flow — wired helper

Swapped the old `Title: body\n\n...` inline reconstruction for
`structured_to_prose(structured)`. Prose consumers now see
markdown-formatted output identical in content to the frontend
cards.

Short-circuit paths UNCHANGED — they compose their own
answer_text via `polish_short_circuit_answer`; Ship 21'.b only
touches the LLM-path reconstruction.

## Verified end-to-end

Live test on `how do I remediate A.5.15?`:
- Zero `↳ Compliance facts:` in answer prose ✓
- `## Related controls` section with 3 refs (A.5.15 primary
  OFI-DRAFT + 10.1 + 10.2 both NC-DRAFT) ✓
- Timeline short-circuit answer prose unchanged (no
  `## Related` — short-circuits compose their own prose) ✓
- `answer_structured` payload unchanged ✓

APPEND-ONLY discipline preserved (intro + actions[] verbatim
from LLM; related section derived from CaseFile; same
discipline as Ship 18/19/20).

## Ship 21 progress

| Sub-arc | Status |
|---|---|
| 21'.a Design memo + audit trail | ✓ (d1aceb6) |
| **21'.b Retirement + prose polish** | **✓ (66247f4, this doc)** |
| 21'.c Eval + retro | next |

## Related

- [[ship-21-prime-a-footer-retire-design-2026-07-23]] — design
- [[ship-20-prime-arc-retrospective-2026-07-23]] — the arc
  that made the footer structurally redundant
