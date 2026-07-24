---
name: ship-26-prime-arc-retrospective-2026-07-24
description: "Ship 26' arc closer — Chat decisions UI section in Trace mode delivers Ship 6'.f deferred item; frontend-only arc, baseline held"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 26' arc retrospective — 3 sub-arcs across one day
(2026-07-24) delivering the Ship 6'.f deferred item (chat UI
drill-in for LLM decision-trail). Extends existing `#trace`
mode with a Chat decisions section reading Ship 6'.e's
endpoint. Frontend-only arc; zero backend changes.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 26'.a | Design memo — extend Trace mode, row + inline-detail pattern | bc53bed |
| 26'.b | 230-line frontend delivery in `renderTrace` + drill-in helpers | 205fbec |
| **26'.c** | **Eval + retrospective (this doc)** | pending |

## What the surface delivers

Chat decisions section renders between the Trace KPI row and
the existing AI-calls section. One table row per chat turn
(limit 50) with 8 columns:

| Column | Signal |
|---|---|
| Time | Relative — "5m ago" |
| Query | First 80 chars |
| Type | question_type chip |
| Consensus | verdict + LLM-fallback flag; green confident, amber fallback |
| Repair | red chip if `repair_events_count > 0`, green "clean" if 0 |
| Claims | amber chip if any `ref_in_digest=false` (ungrounded) |
| Tokens | Prompt in / LLM out |
| Cost | `$0.XXXX` |

**Row click → inline detail row** with 6 sub-sections in a
2-column grid + 2 full-width:
1. Query framing (query text + type + session_id + request_id + turn timestamp)
2. Consensus routing (verdict + fallback + framework + corroborators + top-6 refs + top_conf 3-decimal)
3. Prompt + latency (system/digest/total tokens + answer_len + digest/repair/total latencies)
4. LLM calls (n_calls + tokens in/out + cost + purposes list + models list)
5. Repair events (count + collapsible raw JSON of footers_added)
6. Claim scan (count + ungrounded count + per-event ref + ref_in_digest ✓/✗ + standard_in_scope ✓/✗)

**Filters**: hours window reuses the existing Trace selector;
new chip toggles for `Only repaired` + `Only ungrounded`.

## Eval outcome

**231/232 PASS + 1 WARN (#200) + 0 FAIL** — identical to
Ship 15'.e / 18'.c / 19'.d / 20'.e / 21'.c / 22'.d / 23'.c /
24'.c / 25'.c baselines. Zero risk from a pure frontend
observability surface.

## What made this arc trivially clean

Ship 26 is the shortest observability arc possible because
**Ship 6'.e already built the plumbing 5 days ago** (endpoint
+ view + schema_v83). The decision-trail data has been
accumulating in `chat_casefile_log` on every chat turn since
Ship 2'.g (2026-07-15) — 9 days of history at the point of
this arc.

The user's Ship 26 pick was framed as "deliver Ship 6'.f
deferred item" and it truly was — no design surprise, no
data gap, no schema change. Just wire the existing endpoint
to a UI section using the existing patterns.

## Codified 3 lessons

### 1. Deferred UI can be pure consumption when plumbing exists

Ship 6'.e (endpoint) → 5 days later Ship 26 (UI) → zero new
schema, zero new API, zero new logic. The backend built the
data path anticipating the UI would follow. Ship 26 just
consumed it. Pattern: when deferring UI, prioritise landing
the data path first + describing what the UI *would* consume;
the UI itself becomes rate-limited only by frontend authoring
time.

### 2. Observability data density earns its surface

`chat_casefile_log.repair_events` accumulated for 9 days
before Ship 26 shipped a routine surface for it. Ad-hoc
inspection worked but was expensive. The 8 arcs of
retire-visible + keep-observability discipline (Ship 18→25)
made this UI worth the frontend effort:
- Ship 21 retired the compliance-facts footer + logged repair
  events for auditor drill
- Ship 22 retired bridge + risk footers + logged their
  missing_bridge_footer / missing_risk_ref events
- Ship 25 caps + overflow_counts contribute to the same
  visibility surface

Every one of those arcs' hidden signals now has a routine
routes-to-UI. The observability paid off exactly when we
built the UI, not before.

### 3. Trace mode is the observability home

We considered a new nav item ("Chat trail") vs extending
Trace. Extension won: cohesive surface, reuses filters,
matches the sections-within-one-mode pattern Trace already
established (AI-calls + Intake + Chat requests). Adding a
fourth section (Chat decisions) fits naturally without
sprawl. Rule: when adding an observability surface, ask
first whether an existing mode has the right shape — most
new signals don't need new nav.

## What Ship 26 did NOT do

- **New nav item** — surface lives in Trace mode
- **Session-thread view** (chronological chat-thread render
  of all turns in a session) — deferred; the current design
  shows independent turns
- **Wire decision-trail into tenant-facing chat bubbles** —
  admin surface only per user choice
- **Modal drill-in** — used inline row expansion instead,
  matching Trace's aesthetic
- **Change the endpoint or view** — pure frontend consumption
- **Pagination beyond limit=50** — window-based filtering
  handles this for now

## Ship 26 sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 26'.a | Design + placement decision (extend Trace mode) | Row + inline-detail pattern locked; 6 sub-sections in drill-in specified |
| 26'.b | 230-line frontend delivery — table + filters + inline detail + helpers | Verified live: Art.32 turn showed 6 repair events, 2 LLM calls, $0.00092 cost |
| **26'.c** | **Eval + retro (this)** | **231/232 PASS + 1 WARN + 0 FAIL; arc closed** |

## Related

- Ship 6'.e (2026-07-19) — endpoint + view Ship 26 consumed
- Ship 2'.g (2026-07-15) — chat_casefile_log schema
- Ship 1 (2026-07-14) — chat_consensus_log schema
- [[ship-25-prime-arc-retrospective-2026-07-24]] — the arc
  whose retire-visible + keep-observability discipline made
  routine surfacing of this data valuable
- [[ship-22-prime-arc-retrospective-2026-07-24]] — the arc
  whose missing_bridge_footer / missing_risk_ref events
  Ship 26 now surfaces routinely
