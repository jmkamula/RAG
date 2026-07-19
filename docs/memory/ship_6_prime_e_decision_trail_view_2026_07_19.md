---
name: ship-6-prime-e-decision-trail-view-2026-07-19
description: "Ship 6'.e — joined LLM decision-trail view + admin endpoint; wires session_id/request_id through all chat log writers"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 6'.e (2026-07-19) — the fifth sub-arc of the Ship 6 LLM-role
audit. Produces a single joined lens across the three chat log
tables so an auditor or engineer can trace one turn end-to-end
without hand-JOINing four tables.

## Motivation

Prior sub-arcs each added a dedicated log:

- Ship 1 → `chat_consensus_log`   (classifier signals + verdict)
- Ship 2' → `chat_casefile_log`   (digest tokens + repair events)
- Ship 6'.d → `chat_casefile_log.{answer_text, claim_events}`
- `ai_call_log` → every LLM call with cost + latency

Investigating a single chat turn required manually correlating
rows across all three. Worse: the correlation was broken —
`chat_casefile_log.request_id` and `chat_consensus_log.request_id`
were 0% populated over 2 days of chat traffic (the columns
existed but nothing wrote them). Only `ai_call_log.request_id`
had 3.2% coverage (the API endpoint chat path).

## What shipped

### 1. Wire session_id + request_id through all writers

`api_server.py::chat` already calls `set_trace_context()` at
request entry (Wave 4c), stamping tenant_id + session_id +
request_id into ai_trace ContextVars. `log_llm_call` reads
these from context if the caller doesn't pass them explicitly.

Ship 6'.e extends the same pattern to the chat-side log writers:

- **`rag/ai_trace.py`** — new getters `current_session_id()`,
  `current_request_id()`, `current_tenant_id()`.
- **`rag/casefile/log.py::log_casefile()`** — pulls from
  ContextVars when the caller passes `None`.
- **`rag/consensus/log.py::log_consensus()`** — same pattern.

No signature changes needed at the call sites; the ContextVars
are populated at request entry and inherited by every internal
async task and thread.

### 2. schema_v83 — `chat_llm_decision_trail` view

Non-materialized SQL view joining the three tables on
`request_id` + `tenant_id`. One row per chat turn with:

- Consensus columns (verdict, top_refs, confidence,
  corroborators, framework, llm_fallback_used)
- Case-file columns (prompt tokens, repair events, footers,
  latency breakdown)
- Ship 6'.d claim scan (claim_events, claim_events_count,
  answer_len from `LENGTH(answer_text)`)
- LLM aggregate (n_calls, tokens_in/out, cost_usd, purposes[],
  models[]) via `LEFT JOIN LATERAL` over `ai_call_log`

`WHERE cf.request_id IS NOT NULL` filters out pre-6'.e rows +
eval-harness runs that don't stamp a request_id.

Granted `SELECT` to `arioncomply_app`.

### 3. `/api/v1/admin/chat/decision-trail` endpoint

Read-only tenant-scoped, respects RLS. Query params:

- `request_id`    — pin to a specific turn
- `session_id`    — all turns in a session
- `hours`         — time window (default 24, max 90 days)
- `limit`         — default 50, max 500
- `only_repaired` — preservation-check fired ≥1 repair event
- `only_ungrounded` — case-file emitted a claim event with
                    `ref_in_digest = false` (via jsonb `@>` gate)

Returns `{count, turns[]}` with every field the view exposes,
timestamps ISO-formatted, `Decimal` cost cast to float.

## End-to-end smoke test

Fired one chat turn ("what does Art.32 require?") and pulled the
trail:

```
POST /api/v1/chat  "what does Art.32 require?"
GET  /api/v1/admin/chat/decision-trail?hours=1

{
  "request_id": "eb95c520-b18e-4d81-bccd-582df65e9cbf",
  "session_id": "api_6e1a85ba",
  "consensus_verdict": "confident",
  "consensus_top_conf": 1.56,
  "consensus_corroborators": 3,
  "consensus_framework": "GDPR:2016/679",
  "consensus_llm_fallback": false,
  "prompt_tokens_total": 1749,
  "repair_events_count": 5,
  "footers_added": ["↳ Bridges to ISO 27001 for Art.32 ...",
                    "↳ Compliance facts: 10.1 ..."],
  "claim_events_count": 0,
  "answer_len": 1512,
  "llm_n_calls": 2,
  "llm_tokens_in": 3860,
  "llm_tokens_out": 260,
  "llm_cost_usd": 0.000735,
  "llm_purposes": ["consensus_gatekeeper", "rank_answer"]
}
```

All three previously-empty ID fields populated. All filters
(`only_repaired`, `only_ungrounded`, `request_id`) verified.

## Design notes

- **Non-materialized view.** Source tables are already indexed
  by `(tenant_id, created_at)`; queries are always time- +
  tenant-scoped. If the view gets expensive later, a materialized
  version with `REFRESH MATERIALIZED VIEW CONCURRENTLY` on a
  sweep tick is the natural upgrade.
- **`LATERAL` join for aggregation.** Avoids a `GROUP BY` +
  `ARRAY_AGG` explosion on the outer query when there are 0
  matching `ai_call_log` rows.
- **NULL request_id excluded.** Eval-harness paths don't stamp a
  request_id (they use the classifier + resolver directly, not
  the API endpoint). Excluding them keeps the view focused on
  real chat traffic that can be traced end-to-end.

## Deferred / follow-up

- **Chat UI drill-in.** Currently only the admin API can view
  the trail. A tenant-facing "why this answer?" panel could
  render per-turn signals + LLM calls; Ship 6'.f or a later arc.
- **Materialised variant.** If audit teams query historical
  traffic frequently, materialise with a nightly refresh.
- **Materialised claim-event dedup.** Ship 6'.d captures per-
  turn claims but doesn't dedupe across a session. If a claim
  repeats 5 times in one conversation, we'd want 1 review item
  not 5. A session-scoped rollup view is the natural next step.
- **Backfill.** Pre-6'.e rows can't be linked — the request_id
  wasn't in the wire. Not worth backfilling; they age out via
  the retention sweep.

## Baseline

Full eval running. Wire-up is passive (only reads ContextVars
that the API server already populates); no behaviour change on
the answer path.

## Ship 6' progress

| Sub-arc | Status |
|---|---|
| 6'.a Role audit + safeguard inventory | ✓ |
| 6'.b Grounding provenance column + tests | ✓ |
| 6'.c Preservation-check retrospective | ✓ |
| 6'.d Passive claim-scan observability | ✓ |
| **6'.e Joined LLM decision-trail view** | **✓** |
| 6'.f Arc retrospective | next |

## Related

- [[ship-6-prime-a-llm-role-audit-2026-07-18]] — parent audit
- [[ship-6-prime-d-claim-scan-observability-2026-07-19]] — 6'.d
