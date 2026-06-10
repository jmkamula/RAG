---
name: posture-claim-hallucination-guard
description: "SHIPPED 2026-06-10 (14633c1 + 5b98a42): L1 post-compose guard in rank_and_answer drops lines whose (control_ref, claimed_status) pair contradicts posture_by_ref truth. v2 is section-aware (claim inferred from **Non-Conformities (NC):** style headers when bullet has no inline [STATUS]), logs violations via std logger, and renumbers bullets after drops."
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

## Related

- [[polish-short-circuit-data-loss-guard]] — sibling pattern for
  short-circuit polish.
- [[extractor-grounding-rules]] — analogous pattern at the intake
  pipeline (LLM claims must substring-match source).
