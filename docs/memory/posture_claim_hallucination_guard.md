---
name: posture-claim-hallucination-guard
description: "SHIPPED L1+L3 2026-06-10/11. L1 (14633c1+5b98a42) is post-compose guard in rank_and_answer that drops lines contradicting posture truth. L3 (adc1a8f) bypasses LLM entirely for enumeration-shape POSTURE_CHECK queries — deterministic markdown from posture_by_ref. Same query → byte-identical output. L2 (pre-compose dedup) still deferred."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

L1 of a three-tier strategy for chat-compose hallucination. Surfaced
2026-06-10 by a tenant query `what is our access control compliance
status?` where the LLM listed 4 controls as NC + duplicated 2 of them
under OFI, fabricating "NC - All children unassessed" reason text for
3 controls whose actual posture was OFI.

## What it does

`rag/llm_answer.py:_verify_posture_status_claims(answer_text,
posture_by_ref)` — runs just before the final `return
ComplianceAnswer(...)` in `rank_and_answer`. For each line:

  - Find all refs (`A.X.Y[.Z]` / `Art.X[.Y]` / `X.Y[.Z]`).
  - For each ref, look at the window from this ref to the next ref
    (or end of line) for the first `NC|OFI|Comply` token.
  - If the claim contradicts `posture_by_ref[ref].finding`, mark line
    as bad and drop it.

Per-ref windowing matters — `"Addressed via A.X [NC], A.Y [OFI]"`
needs each pair validated independently, which a single-status-per-line
heuristic would miss.

`posture_by_ref` is built at line ~909 in rank_and_answer from the
same posture dict the LLM sees, so truth and LLM input are
guaranteed consistent.

## Why "drop the line, not rewrite it"

Drop is simpler and provably safe. Rewriting `NC` → `OFI` in-place
risks corrupting surrounding prose (the LLM's narrative was built
around the wrong status). A gap in a numbered list (1. 3.) is
acceptable — markdown renderers auto-renumber, and the omission
is preferable to a false claim.

## What's logged

Each violation logged via the existing `logger.log_call` with
`step="posture_claim_guard"`. This makes the guard observable in
the same trace stream as the LLM calls themselves.

## Sanity test

```python
answer = '''
1. A.5.18 — Access rights: NC [DRAFT] - All children unassessed
2. A.5.15 — Access control: NC [DRAFT] - All children unassessed
- GDPR Art.17: Addressed via A.5.18 [OFI], A.5.9 [NC]
'''
truth = {'A.5.18': {'finding': 'OFI'}, 'A.5.15': {'finding': 'OFI'},
         'A.5.9': {'finding': 'NC'}}
```

Expected: lines 1+2 dropped (NC fabricated, truth=OFI). xfw line
preserved — A.5.18 [OFI] matches truth, A.5.9 [NC] matches truth.

## The two unfixed layers

- **L2 — pre-compose dedup + strict context binding.** Today each
  control can appear multiple times in the COMPLIANCE NODES block
  (primary + xfw lines). Deduping by control_ref before sending
  the prompt would reduce the *opportunity* for compose-time
  duplication. Touches `context_assembler.py`. Not shipped.
- **L3 — deterministic compose for enumeration intents.** For
  POSTURE_STATUS / list-gaps queries the truth IS the structured
  data; the LLM adds no signal, only risk. Replace `rank_and_answer`
  with a deterministic markdown formatter for these intents. Big
  refactor; biggest payoff. Not shipped.

## Pattern lineage

Same shape as [[polish-short-circuit-data-loss-guard]] —
post-LLM parity check + drop bad output rather than trust prompts.
The general principle: **the truth is in the data; the LLM output
is the suspect. Add a verifier that detects when LLM output
contradicts the source data.**

## 2026-06-10 — v2 (5b98a42)

The v1 guard only caught **explicit** status tokens (`[NC]`, `OFI`,
etc). On the next reproduction the LLM swapped to PROSE — "Access
control is not effectively implemented" under a `**Non-Conformities
(NC):**` section header — and the guard saw no claim to validate, so
the fabricated NC bullets passed through untouched.

Three extensions:

**Section-aware claim inference.** A new `_classify_section_header()`
recognises `**Non-Conformities (NC):**` / `**Opportunities for
Improvement (OFI):**` / `**Comply:**` headers (and `RESET` markers
like `**Cross-Framework:**` / `**Not yet assessed:**`). The line
walker tracks `current_section` and, when a bullet has a ref but no
inline status token, treats the section as the claim. Heuristics:
header lines have `**` or `#`, length < 120, and don't start with a
bullet marker.

**Standard-logger fallback.** `logging.getLogger("rag.llm_answer")
.warning(...)` runs unconditionally on violation, so a line like
`WARNING rag.llm_answer: posture_claim_guard: dropped 2 line(s):
A.5.15: claimed=NC actual=OFI; A.5.18: claimed=NC actual=OFI`
lands in `/tmp/api.log` — the chain logger isn't enabled in
production, so without this the guard was invisible.

**Renumber after drops.** Contiguous `^N. ` bullet blocks are
rewritten to monotonic 1, 2, 3 after dropping. Eliminates the
`1. 3. 5.` numbering gap that reads as a rendering bug. Only fires
when at least one violation was detected, so clean answers are
untouched.

Eval 195/198 with v2 — known-stale #2/#25/#26 only.

## 2026-06-11 — L3 shipped (adc1a8f)

L1 fixed individual hallucinated bullets but didn't address
*selection stochasticity*: same query → different controls listed
each run, because rank_and_answer picks 5-7 nodes from ~30
candidates and the choice drifts run-to-run. Tenant complaint:
"I'm not getting consistent answers here. I also want the
control number and name. Markdown bold doesn't seem to work."

The structural fix: for enumeration-shape POSTURE_CHECK queries
("what is our X compliance status", "what are our NCs", "where
do we stand", "list our gaps"), the truth IS the structured
posture data. The LLM rank step adds no signal, only risk.
Bypass rank_and_answer entirely and compose markdown directly.

`rag/arion_graph.py` additions:

  - `_POSTURE_ENUMERATION_RE` — regex matching enumeration query
    shapes. Single-control questions ("is Art.5 a NC?", "what
    does A.5.18 mean?") still route through the LLM.
  - `_is_posture_enumeration_query(q)` — bool gate.
  - `_compose_posture_enumeration_answer(...)` — buckets
    `expanded_nodes` by posture finding (NC/OFI/Comply), sorts
    by ref, formats `**STD REF — Title**: reason` per row;
    cross-framework section inherits per-linked-ref finding
    via `xfw_edges` + posture_by_ref, dedupes duplicate
    rel_type edges.

The composer is called in the retrieve node just before
`llm.rank_and_answer(...)`; when it returns text, the function
short-circuits with `answer_source="posture_enumeration_
deterministic"`.

What this delivered (vs prior LLM-compose):

  - **Determinism**: byte-identical answer for the same posture
    state on every run.
  - **Control names always present**: format always
    `**ISO 27001 A.X.Y — Title**`, regardless of LLM mood.
  - **Markdown stable**: flat bullet list, no nested `1.` + `-`,
    bold renders cleanly across renderers.
  - **Latency**: 35s → 3-6s on the user's reference query.

What this didn't break:

  - rank_and_answer (and the L1 guard inside it) still runs for
    free-form posture queries, definition queries, gap queries
    where the user wants narrative not enumeration.
  - Eval 194/198 — known-stochastic only.

## Three-tier strategy now stands

  - **L1 (shipped)** — post-compose verifier on LLM output;
    catches per-line hallucinations.
  - **L2 (deferred)** — pre-compose dedup of context blocks; not
    needed once L3 covers the highest-risk intent.
  - **L3 (shipped)** — deterministic compose for enumerations;
    bypass LLM entirely where truth is structured.

The general principle stays the same as the polish guard / extractor
grounding rules: **the truth is in the data. The LLM is the suspect.**
For enumerations, the simplest guard is to skip the suspect.

## Related

- [[polish-short-circuit-data-loss-guard]] — sibling pattern for
  short-circuit polish.
- [[extractor-grounding-rules]] — analogous pattern at the intake
  pipeline (LLM claims must substring-match source).
