---
name: conversational-context-routing-followup
description: "FOLLOW-UP: short-circuit answers don't write semantic state, so conversational references in the next turn ('this', 'that doc', 'the X') fall through to a generic 'no primary compliance nodes' LLM template. Three layers, three fixes ranked by cost."
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

## Why we deferred today

The title-matcher fix (f693954) resolves the *immediate* user
complaint (Q1 returns the right doc). Q2's bad fallback is a
related-but-separate routing issue that requires LangGraph state
threading work. Not in scope when the urgent fix was the
matcher.

## Related

- [[doc-curation-engine-v1]] — the short-circuit answerers depend
  on `tenant.uploaded_documents`.
- [[classifier-posture-short-circuit]] — same family of
  short-circuits; same blind spot.
- [[stage1-detail-show-inference-chain-idea]] — Stage-1 detail
  panel also a short-circuit; check for the same symptom there.
