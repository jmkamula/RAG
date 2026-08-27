---
name: ship-98-prime-a-diagnostic
description: Ship 98'.a — chat-scope diagnostic matrix. Dogfooded 16 (question_type × shape) cells to isolate where broad-context-as-default causes bloat. 15 of 16 cells >3 related cards. Pattern by shape (SCOPED/TOPIC/PROGRAM) is consistent across question_type — pointed at Ship 98'.b shape-enum direction over Ship 97'.b/c-style per-intent gates.
metadata:
  type: project
---

# Ship 98'.a — Chat-scope diagnostic (2026-08-27)

## Framing

Ship 97'.b/c fixed one specific bloat cell (IMPLEMENTATION +
cited_refs). The wider question: does the same top-N-NC leakage
affect other `question_type` values? Where should Ship 98'.b
intervene — enumerate per-intent gates or introduce a new
abstraction?

Rather than guess, dogfood.

## What was done

New `scripts/ship98a_scope_diag.py` — 16 realistic tenant
queries × 5 `question_type` shapes × 3 scoping intents (SCOPED
with typed ref / TOPIC with topic phrase / PROGRAM with no ref).
Per query: hit `/api/v1/chat`, capture:

- classified `question_type`
- `answer_structured.related` card count + refs
- `templates.leaves` (starter) count

Threshold: >3 cards = bloat candidate.

## Result

| Shape | Cells | Avg cards | Range |
|---|---|---|---|
| SCOPED | 6 | 9 | 2-13 (Ship 97'.b/c fix visible: 2 on IMPLEMENTATION) |
| TOPIC | 5 | 13 | 5-19 |
| PROGRAM | 4 | 22 | 17-25 |

**15 of 16 cells exceed the >3 threshold.** Ship 97'.b/c fixed
exactly one cell.

Secondary finding: **classification drift on 4 cells** —
"what does A.5.18 say?" → document_content (should be
definition); "am I compliant?" → cross_framework (broken);
FREE_ASSESSMENT → gap_analysis (arguable). Not the arc's
target; noted for follow-up.

## Interpretation

- PROGRAM queries LEGITIMATELY want breadth. 24 cards on "what
  are our main compliance gaps?" reflects tenant state.
- SCOPED queries EVERYWHERE exhibit the same top-N-NC leak
  pattern regardless of `question_type`. The bloat isn't
  intent-specific; it's shape-specific.
- TOPIC queries want adjacent-area context (case #1 lesson —
  going too tight on gap_analysis TOPIC caused the "physical"
  leak).

The shape distinction (SCOPED / TOPIC / PROGRAM) is orthogonal
to `question_type` and applies uniformly. Points at Ship 98'.b
= introduce a `QuestionShape` enum rather than enumerate ~9
per-intent gates.

## Signal-based shape inference is trivial

The consensus layer already computes the signals that
distinguish shape:
- Signal B (`explicit_refs`) fires with refs → SCOPED
- Signal C (`curated_lexicon` on DOCUMENT_TOPIC_MAP) fires with
  refs (Signal B didn't) → TOPIC
- Neither → PROGRAM

Simpler yet: check whether any cited ref appears literally in
the query text — no consensus-internal access needed. Verified
on the 16 diagnostic queries in Ship 98'.b.

## Deliverable

- `scripts/ship98a_scope_diag.py` — the diagnostic script
  (kept in-repo for regression re-runs)
- Findings above — the input to Ship 98'.b design

## Related

- [[ship-97-prime-b-chat-scoping-remediation]] — the arc that
  fixed cell 1; this diagnostic quantifies what's left
- [[ship-98-prime-b-question-shape]] — the arc that implements
  the shape-enum direction this diagnostic pointed at
