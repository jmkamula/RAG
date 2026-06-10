---
name: conversational-context-routing-followup
description: "SHIPPED 2026-06-10: state['last_entity'] + LLM status-preservation + deictic-only retrieve short-circuit + 5 short-circuits populate last_entity + Pattern 3 expand-directive nudge. Smoke test 5/5 PASS. Only Option B (history-aware classifier re-routing), scope_na last_entity, and retrieval-side Pattern 3 depth fetch remain deferred."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The chat pipeline drops conversational context across turns when
the prior turn was answered via a short-circuit (deterministic
answerer that bypasses LLM+retrieval). Surfaced 2026-06-10 when
a tenant asked:

  Q1: "have we uploaded our business continuity policy?"
  A1: [deterministic answer naming DOC028 Plan — pre-shape-word fix]
  Q2: "this is the plan, what about the policy document?"
  A2: "The query does not provide any primary compliance nodes to
       assess the policy document. Please provide the relevant
       compliance nodes for further evaluation."

The title-matcher shape-word fix (commit f693954) addresses Q1
but leaves Q2's follow-up failure intact.

## Three failure layers (in order of evaluation)

1. **Short-circuit doesn't write semantic state.** The
   `_answer_upload_status` path in `arion_graph.py` returns a
   formatted string assembled from `tenant.uploaded_documents`.
   PostgresSaver records the chat turn (text in/out) but nothing
   records *what entity was being discussed* — no "topic =
   business_continuity_policy" or "entity = DOC028" lands in
   LangGraph state. Same applies to other short-circuit paths:
   `acknowledge`, Stage-1/Stage-2 lists, `find documents missing`,
   `scope N/A` answers.

2. **Classifier is per-query, no history.** `make_classify_node`
   in `arion_graph.py` reads only `state["query"]` plus a fixed
   set of `CLEAR_INTENT_PHRASES` regexes. A follow-up like
   "what about the policy?" with no shared keywords with the
   prior intent falls into the default route (often `gap_analysis`)
   and the retriever runs with no focus_refs.

3. **Empty-retrieval LLM template is unhelpful.** When the
   retriever returns no primary nodes, the LLM answers with a
   scripted fallback ("The query does not provide any primary
   compliance nodes..."). Designed for the case where a user
   types a vague compliance question — wrong for a conversational
   follow-up.

## Fixes ranked by cost

| Fix | What it does | Cost | Coverage |
|---|---|---|---|
| **A: Persist short-circuit entities** | When `_answer_upload_status` or other short-circuits match a specific doc/control, write `state["last_entity"] = {"type": "document", "id": DOC028, "title": "BC Plan"}`. Resolver/classifier can read this on the next turn. | Low (~30 LOC per short-circuit path) | Catches "this doc", "that one", "it" follow-ups |
| **B: History-aware classifier** | Classifier reads prior turn's `intent_type` + `last_entity` from state. If the new query is short and contains a generic noun ("what about the policy?"), re-route to the prior intent with the new noun as focus. | Medium (~100 LOC + thread_id plumbing) | Catches re-framing follow-ups |
| **C: Better empty-retrieval message** | When the resolver returns no primary nodes AND state has `last_entity`, the LLM template says "I don't see a 'policy document' in the current scope. Did you mean DOC028 (Plan) from your earlier question, or a different doc?" | Low (~20 LOC in LLMAnswer.compose) | Mitigation; doesn't fix routing but makes the failure honest |

**A + C together** are probably the right minimum — A captures the
entity, C uses it gracefully when classification falls through.
B is more principled but touches the classifier's prompt design.

## How to identify this bug

- Chat answer contains the literal phrase `"does not provide any
  primary compliance nodes"` or `"please provide the relevant
  compliance nodes"` — that's the empty-retrieval LLM template.
- AND the user's question was a short conversational follow-up
  with deictic references ("this", "that", "the X", "what about").
- AND the prior turn was a short-circuit answer (check
  `intake_trace_log` or simply: was the prior answer
  deterministic / template-shaped?).

## 2026-06-10 — MVP shipped (a3150ca)

Options A + lightweight C landed as one commit:

- **arion_state.py** — new `last_entity: dict` field on ArionState.
  Defaults to empty. Populated by short-circuit returns.
- **arion_graph.py** — new helper `_resolve_upload_entity()` mirrors
  `_answer_upload_status` shape but returns just the matched doc
  dict (or `{}`). Called in the upload-status short-circuit return
  path; matched entity written to `state["last_entity"]` so it
  carries to the next turn via PostgresSaver. `make_retrieve_node`
  reads state["last_entity"] and passes it to `rank_and_answer`.
- **llm_answer.py** — `rank_and_answer()` accepts a new
  `last_entity` parameter and, when present, injects a `PRIOR-TURN
  CONTEXT:` block into the user message. The LLM is told to use
  it for deictic resolution ("this", "that", "the X document")
  NOT as new compliance evidence to cite.

Smoke test on Arion (two-turn conversation sharing session_id):
  Q1: "have we uploaded our business continuity policy?"
      → Yes, DOC007 (Policy), uploaded 2026-04-28.
  Q2: "this is the plan, what about the policy document?"
      → Pre-fix: "The query does not provide any primary compliance
        nodes..." (generic empty-retrieval template)
      → Post-fix: contextual response about the BC Policy DOC007
        from the prior turn.

**What's still missing (Option B):** classifier-side re-routing
of deictic queries. When a short follow-up has no clear intent
match AND a `last_entity` exists, the classifier should
re-route to the prior intent rather than falling into the
gap-analysis default. Deferred — wait for production signal on
whether the MVP is sufficient.

## Smoke test + LLM-answer-quality gap (2026-06-10, 2097d01)

`scripts/test_conversational_context.py` exercises 5 follow-up
patterns. **5/5 PASS on the "no generic empty-retrieval template"
bar.** Routing works.

But the test deliberately uses a low bar. Examining the actual
answers exposes a SECOND failure mode the MVP doesn't address —
LLM-answer-quality on follow-ups:

  - **Pattern 1 (named-doc + deictic)**: A1 correctly says "uploaded
    2026-04-28"; A2 then says "registered but NOT uploaded yet"
    about the SAME doc. The LLM uses the prior-turn entity but
    contradicts the upload status it just gave. Hallucinated
    inversion.
  - **Pattern 5 (inventory + deictic)**: Q2 asks "what about the
    policy?" with no `last_entity` (inventory queries don't pick a
    single entity). The LLM doesn't admit it doesn't know what
    "the policy" refers to — it dumps random NCs on ISO clauses
    10.1/10.2. Lost the deictic thread entirely.

These are LLM-prompt-engineering failures, NOT state-flow
failures. The fixes live in `rank_and_answer`'s system prompt /
user message structure, not in ArionState plumbing:

  - For Pattern 1: when `last_entity` already carries a definitive
    status ("status": "uploaded"), the LLM should preserve that
    fact, not contradict it. Could add explicit constraint to the
    PRIOR-TURN CONTEXT block.
  - For Pattern 5: when there's no `last_entity` AND the query has
    deictic words, the LLM should ASK for clarification, not
    invent a referent. Could add a "if you can't resolve the
    deictic, ask which doc" instruction.

Both deferred. The smoke test is the regression baseline — future
prompt tweaks should net more PASSes (with tighter per-pattern
heuristics) without regressing the existing 5.

## 2026-06-10 — both quality gaps closed (3cef7e4 + f76b389)

**Pattern 1 fix (3cef7e4 — prompt-level):** the PRIOR-TURN
CONTEXT block now includes an explicit status-preservation
constraint when `last_entity.status` is set. Pre-fix the LLM
would invert "uploaded 2026-04-28" → "registered but NOT
uploaded yet" because it confused doc-level upload status with
control-level engine_proposal_status='draft'. Post-fix A2
reads: "the doc IS UPLOADED on 2026-04-28 — confirmed fact from
the previous turn. Do NOT say it is 'registered but not
uploaded'." Pattern 1 in smoke test 2097d01 now produces a
faithful answer.

**Pattern 5 fix (f76b389 — retrieve-stage short-circuit):**
new `_is_deictic_only_query()` heuristic in arion_graph.py:
- query ≤10 words
- contains deictic phrase (this/that/it/what about/tell me more/
  is it/the X) where X ∈ {policy/plan/procedure/register/
  document/doc}
- no explicit refs (A.x.y / Art.x / DOC### / CD-ARN-####)

When true AND state["last_entity"] is empty, the retrieve node
returns a deterministic clarification asking the user to name
the specific doc/control. No retriever call, no LLM call.
answer_source = "deictic_clarify". Eliminates the
NC-dump-on-random-control failure mode.

Eval verification: 194/198 PASS post-fix (same baseline as
pre-fix). The short-circuit did NOT trip any of the 198 eval
cases — the heuristic's 10-word ceiling + explicit-ref
disqualifier guard against false positives.

## What still doesn't perfectly work

Pattern 3 ("tell me more about it") still just echoes Q1's
upload-status response rather than probing deeper. The LLM has
the entity in context but doesn't volunteer additional detail.
Not a routing or correctness issue — depth-of-answer issue.
Fix would be a prompt nudge: when query is "tell me more" /
"what else" and last_entity is set, prompt the LLM to surface
the doc's curated checklist items or related controls. Low
priority; the answer isn't wrong, just thin.

**What other short-circuits don't yet populate `last_entity`:**

- `_answer_acknowledge` — acknowledge-gap short-circuit
- Stage-1 / Stage-2 list/approve chat surfaces
- `_answer_scope_na` — physical/dev controls N/A short-circuit
- Posture timeline queries ("how did A.5.18 evolve?")

Each takes ~10-15 LOC: resolve the matched entity → return it in
state["last_entity"] on the short-circuit return. Wait for a
real user need (a follow-up after any of these short-circuits
falls into the bad template) before generalising.

## Why we deferred today

The title-matcher fix (f693954) resolves the *immediate* user
complaint (Q1 returns the right doc). Q2's bad fallback is a
related-but-separate routing issue that requires LangGraph state
threading work. Not in scope when the urgent fix was the
matcher.

## 2026-06-10 — 4 more short-circuits + Pattern 3 nudge (bb88640)

New `_control_entity()` helper in `arion_graph.py` builds a
control-shape last_entity (`{type: "control", ref, standard_id,
title}`; standard_id inferred from `Art.` prefix). Plumbed into
four additional short-circuit return paths:

  - `acknowledge-gap`         → `_ack_intent.control_ref`
  - `Stage-1 review`          → `_s1_intent.control_ref`
  - `Stage-2 approval`        → `_s2_intent.control_ref`
  - `Posture timeline`        → `_ref` from query

Now follow-ups after any of these short-circuits carry the
matched control across turns. The list of short-circuits that
populate last_entity:

  - upload-status (shipped a3150ca, 2026-06-10 AM)
  - acknowledge-gap (bb88640)
  - Stage-1 list/approve (bb88640)
  - Stage-2 list/approve (bb88640)
  - posture timeline (bb88640)

Still missing: `_answer_scope_na` — that short-circuit is
category-level ("physical security N/A for cloud-only tenant"),
not control-level, so the entity shape doesn't map cleanly. Wait
for a real user need before forcing the fit.

**Pattern 3 expand-directive (bb88640).** When query matches
`tell me more / what else / expand / elaborate / dig deeper / go
deeper` AND last_entity is set, the PRIOR-TURN CONTEXT block
adds an explicit instruction to surface concrete additional
detail rather than repeat Q1's summary.

Limitation: the directive lands in the prompt but the LLM is
still working off the existing COMPLIANCE NODES retrieval. For a
doc-shape entity, those nodes don't carry doc-specific detail
(checklist items, leaf MUSTs). True depth needs a retrieval-side
change: when query is expand-style AND last_entity.type ==
"document", fetch the doc's checklist items / leaf evidence and
inject as additional context. Not in scope for this iteration.

## Related

- [[doc-curation-engine-v1]] — the short-circuit answerers depend
  on `tenant.uploaded_documents`.
- [[classifier-posture-short-circuit]] — same family of
  short-circuits; same blind spot.
- [[stage1-detail-show-inference-chain-idea]] — Stage-1 detail
  panel also a short-circuit; check for the same symptom there.
