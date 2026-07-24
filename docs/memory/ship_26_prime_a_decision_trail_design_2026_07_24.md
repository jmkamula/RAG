---
name: ship-26-prime-a-decision-trail-design-2026-07-24
description: "Ship 26'.a — design memo for Chat decisions UI section in existing Trace mode; delivers Ship 6'.f deferred item"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 26'.a — opens Ship 26 arc. Extends the existing Trace
mode with a `## Chat decisions` section wired to the Ship 6'.e
`/api/v1/admin/chat/decision-trail` endpoint. Delivers the
Ship 6'.f deferred item — routine surfacing of the auditor
observability signals the 8-arc Ship 18→25 chat UX programme
built up (repair_events, claim_events, prompt-token breakdown,
LLM cost, consensus verdicts).

## What exists

**Backend endpoint** — `/api/v1/admin/chat/decision-trail`
(api_server.py:3379, shipped in Ship 6'.e, 2026-07-19). Reads
the `chat_llm_decision_trail` view (schema_v83) joining
`chat_casefile_log ⋈ chat_consensus_log ⋈ ai_call_log` on
`request_id`. Returns 25+ fields per turn:

- Identity: `casefile_log_id, request_id, session_id, turn_at, query, question_type`
- Consensus: `consensus_verdict, consensus_top_refs, consensus_top_conf, consensus_corroborators, consensus_framework, consensus_llm_fallback`
- Prompt breakdown: `prompt_tokens_system, prompt_tokens_digest, prompt_tokens_total`
- Repair signals: `repair_events_count, footers_added`
- Latency: `digest_latency_ms, repair_latency_ms, total_latency_ms`
- Claim scan: `claim_events_count, claim_events, answer_len`
- LLM aggregate: `llm_n_calls, llm_tokens_in, llm_tokens_out, llm_cost_usd, llm_purposes, llm_models`

Filters: `request_id, session_id, hours (default 24),
only_repaired, only_ungrounded, limit (default 50)`.

**Existing UI** — `#trace` mode (arioncomply.html:1480+).
Already shows AI-calls/intake/requests summaries with a
window selector + refresh. Well-established pattern to
extend.

## Design

### Section placement

Add `## Chat decisions` **between the KPI row and the existing
Chat requests card** in the Trace mode. Reuses:
- Existing hours-window selector (no new filter)
- Existing card/table CSS
- Existing modal pattern for drill-in

### Table shape

One row per turn (most recent first, limit 50):

| Column | Source field | Notes |
|---|---|---|
| Time | `turn_at` | Short "HH:MM" or "N min ago" |
| Query preview | `query` (first 80 chars) | Truncate with `…` |
| Type | `question_type` | Small chip |
| Consensus | `consensus_verdict` + `consensus_llm_fallback` | Chip: "signals" / "LLM" |
| Repair | `repair_events_count` | Chip highlighted red when > 0 |
| Claims | `claim_events_count` + ungrounded flag | Chip highlighted amber when ungrounded |
| Tokens | `prompt_tokens_total` / `llm_tokens_out` | e.g. "1.8k / 210" |
| Cost | `llm_cost_usd` | e.g. "$0.0042" |
| Drill-in | button | Opens modal |

**Filter chips above table**: `[ Only repaired ]` /
`[ Only ungrounded ]` toggles that re-query the endpoint.
Uses existing filter buttons style.

### Drill-in modal

Click any row → modal opens showing the full trail:

```
── Query ────────────────────────────────────────────────
  "how do I remediate A.5.15?"
  Type: implementation  ·  Time: 12:34  ·  Session: ui_abc123

── Consensus routing ────────────────────────────────────
  Verdict: confident  ·  Fallback: none
  Top refs: A.5.15 (score 0.87)
  Framework: ISO27001:2022  ·  Corroborators: 3

── Prompt breakdown ─────────────────────────────────────
  System: 1104 tok  ·  Digest: 736 tok  ·  Total: 1840 tok
  Digest latency: 42ms  ·  Repair: 3ms  ·  Total: 6.2s

── Repair events (3) ────────────────────────────────────
  · missing_ref_structured   A.5.15   "required ref absent from intro/actions"
  · missing_verdict_near_ref 10.1     "ref present but verdict not adjacent"
  · missing_bridge_footer    —        "bridge footer absent + refs [A.5.15]"

── Claim scan (2 events, 0 ungrounded) ──────────────────
  · A.5.15 requires ...  ref_in_digest=✓  standard_in_scope=✓
  · Art.32 covers ...    ref_in_digest=✓  standard_in_scope=✓

── LLM calls (3) ────────────────────────────────────────
  gpt-4o-mini  purpose=chat        tok=1840/210  cost=$0.0018
  gpt-4o-mini  purpose=consensus_g tok=340/45    cost=$0.0004
  ...

  Total: 3 calls  ·  2180/255 tokens  ·  $0.0042
```

Each section uses the existing modal-body pattern from Stage-2
drill-in or notification detail.

### API integration

New JS function `loadDecisionTrail(filters)` — pulls
`/api/v1/admin/chat/decision-trail?hours={h}&limit=50&
only_repaired={b}&only_ungrounded={b}`. Called from
`loadTrace()` alongside existing summary/AI/intake/requests
fetches. Rendered by extending `renderTrace()` with a new
section.

Filter chip clicks toggle the flag + re-call
`loadDecisionTrail`. Debounce not needed (server-side limit).

Modal open: click on row → `showDecisionTrail(request_id)`
fetches single-turn detail via
`?request_id=<id>&hours=720` (wide window since request_id
is unique).

### What Ship 26 does NOT do

- **New nav item** — surface lives in existing Trace mode.
- **Session-thread view** — showing all turns in a session
  in chronological chat-thread order. Deferred; the current
  design shows independent turns for now.
- **Wire decision-trail into every tenant-facing chat bubble**
  — tenant-facing transparency is out of scope (user chose
  admin surface option).
- **Add server-side pagination beyond `limit=50`** —
  window-based filtering handles this for now.
- **Change the endpoint** — pure frontend consumption.

## Sub-arc plan

### 26'.b — Implement

- `static/arioncomply.html`:
  * `loadDecisionTrail(hours, only_repaired, only_ungrounded)` helper
  * `renderDecisionTrail(turns)` — table under the existing KPI row
  * `showDecisionTrail(request_id)` — modal opener
  * `renderDecisionTrailDetail(turn)` — modal body
  * Extend `loadTrace()` to include decision-trail fetch
  * Small CSS additions: chip variants for repair/claim/fallback

Backend unchanged.

### 26'.c — Eval + retro

Full eval regression check (should be zero-risk — no
backend changes). Arc retrospective codifying the
observability-surface pattern (integrate into existing
modes, don't sprawl nav).

## Design decisions locked in 26'.a

1. **Extend existing Trace mode.** No new nav item; the
   observability surface stays cohesive. Matches the
   pattern established by Trace mode itself (multiple data
   sources rendered as sections within one mode).

2. **Row-plus-drill-in.** Table shows the triage signals
   (query preview, verdict, repair count, cost); modal
   shows the full trail. Same pattern as Stage-2 dashboard
   drill-in, notification inbox, etc.

3. **Reuse existing filters.** Hours window comes from the
   Trace mode's existing selector. New filter chips added
   for the two admin-toggles (only_repaired,
   only_ungrounded).

4. **Cost display in dollars.** `llm_cost_usd` already
   pre-computed in the view. Frontend renders "$0.0042"
   format matching existing Trace KPI style.

5. **No new schema.** Consumes existing view. Ship 6'.e
   already built the plumbing; Ship 26 just surfaces it.

## Ship 26 progress

| Sub-arc | Status |
|---|---|
| **26'.a Design memo (this)** | **✓** |
| 26'.b Implement Chat decisions section | next |
| 26'.c Eval + retro | pending |

## Related

- Ship 6'.e (2026-07-19) — the endpoint + view Ship 26 surfaces
- [[ship-25-prime-arc-retrospective-2026-07-24]] — the arc
  whose retire-visible + keep-observability discipline made
  routine surfacing of this data valuable
- [[ship-22-prime-arc-retrospective-2026-07-24]] — retirement
  arc that built up the events log this UI reads
