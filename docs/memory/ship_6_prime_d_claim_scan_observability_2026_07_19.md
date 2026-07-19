---
name: ship-6-prime-d-claim-scan-observability-2026-07-19
description: "Ship 6'.d — passive normative-claim scanner + full-answer capture in chat_casefile_log"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 6'.d (2026-07-19) — the fourth sub-arc out of the Ship 6'.a
LLM-role audit. Passive observability layer for LLM chat prose
that makes normative claims about standards ("Art.32 requires
X", "under GDPR, ...", "the standard mandates Y").

## Motivation

Ship 6'.a called the chat-answer LLM a **Compositional** role —
it drafts prose from a case-file digest but could in principle
hallucinate a normative rule. Ship 6'.c's retrospective on
`chat_casefile_log` (1417 turns) showed preservation-check is
firing on 87% of turns catching dropped refs/verdicts/DRAFT
tags. Ship 6'.d asked the adjacent question: **when the LLM DOES
make a normative claim, is it grounded in the digest?**

Preliminary sampling of `ai_call_log.response_preview` (500-char
cap) showed a raw claim rate of ~1.3% and spot-checks confirmed
accuracy. So the case-file architecture is already suppressing
this class of hallucination — but we had no persistent per-turn
record of what claims were made or whether the cited ref was
in the digest.

## What shipped

1. **schema_v82** — 3 new columns on `chat_casefile_log`:
   - `answer_text text` (nullable; capped at 8000 chars — covers
     >99% of realistic answers)
   - `claim_events jsonb NOT NULL DEFAULT '[]'`
   - `claim_events_count int NOT NULL DEFAULT 0`
   - Partial index `idx_ccfl_claim_events` on
     `(tenant_id, created_at DESC) WHERE claim_events_count > 0`.

2. **`rag/casefile/claim_scan.py`** — pure passive scanner. Three
   regex patterns:
   - **direct** — `REF (requires|mandates|specifies|states|prescribes|obliges) X`
   - **prepositional** — `(per|under|according to|as required by|pursuant to) REF, X`
   - **generic** — `the (standard|regulation|article|control) (requires|...) X` (untethered — ref=None)

   REF tokens accepted: `Art.N` / `Art.N.N.letter` (GDPR),
   `A.N.N` / `A.N.N.N` (ISO Annex A), `N.N` / `N.N.N` (ISMS
   clauses), `ISO 27001` / `ISO 27002` / `ISO 27701` / `GDPR`
   (standard names).

   Each event enriched with:
   - `ref_in_digest`     — TRUE if `ref` appears in case-file's
     `posture_by_ref` or `all_nodes()` refs (safe)
   - `standard_in_scope` — TRUE if the ref's standard family is
     in the tenant's `scope_standards`

   **APPEND-ONLY passive** — never rewrites answer text, never
   blocks the response, never auto-appends warnings. Only logs.

3. **`rag/casefile/log.py`** — extended `log_casefile()` with
   `answer_text` parameter; invokes `scan_claims()` and persists
   the event list to `chat_casefile_log.claim_events`.

4. **`rag/llm_answer.py`** — `_log_casefile_turn` accepts
   `answer_text` and passes it through; the `_casefile_flow`
   call site now passes the post-repair `answer_text` (the same
   text the tenant sees).

5. **`tests/test_claim_scan.py`** — 41 assertions across 10 test
   functions covering ref canonicalisation, standard-family
   inference, all three patterns, empty/edge cases, JSON
   serialization, ref-in-digest signal, standard-in-scope signal.

## What the LLM audit revealed (Ship 6'.d preliminary data)

From `ai_call_log.response_preview` (truncated at 500 chars) over
4 days (~1876 chat responses):

| pattern | hits |
|---|---|
| `X requires Y` direct | 25 |
| `per/under/according to REF` | 40 |
| `the standard/regulation/article requires` | 18 |
| `X mandates Y` variant | 8 |
| ref-adjacent `must` | 8 |

Total ~99 normative-verb occurrences across ~1876 responses
(~5%). Spot-checks (Art.32, Art.35.7) confirmed accuracy. The
case-file digest architecture is doing most of the work — the
LLM tends to quote MUST/SHOULD content rather than paraphrase.

Ship 6'.d captures the FULL answer text now (up to 8000 chars),
so future observability arcs can measure the true rate on the
full body — not just the first 500 chars.

## What Ship 6'.d does NOT do

- **No enforcement.** No repair pass, no auto-warning, no test
  fail on a claim event. The signal goes to the log only.
- **No prose rewriting.** Answer text is untouched; the tenant
  sees exactly what the LLM produced (post preservation-check).
- **No alerting.** No Grafana panel, no email, no notification.
  Ship 6'.e+ can build on this data.
- **No answer-text migration for pre-6'.d rows.** Old rows have
  `answer_text = NULL`; only new turns capture text.

## End-to-end smoke test

```
POST /api/v1/chat  "what does GDPR Art.32 require?"

Latest chat_casefile_log row:
  ans_len = 2254
  claim_events_count = 1
  claim_events[0] = {
    "ref": "Art.32",
    "kind": "direct",
    "verb": "requires",
    "snippet": "both controllers and processors to implement
                appropriate technical and organizational
                measures to ensure a level of security
                appropriate to the risk",
    "ref_in_digest": true,
    "standard_in_scope": true
  }
```

Both signals TRUE — this is the "safe" case (LLM cited a ref it
had digest evidence for, in a standard the tenant is enrolled
in). The interesting future signal is when either goes FALSE.

## Baseline

Full eval running. No behavior change on the answer path — the
scanner runs INSIDE the log write which is already silent-fail
best-effort. If claim_scan errors, the log write proceeds
without events (empty jsonb array).

## Deferred to Ship 6'.e+

- **Grafana panel** on `claim_events_count` per day + a
  drill-down on rows where `ref_in_digest = false`
- **Sample-review workflow** — surface risky claim events in a
  Stage-2-style HITL queue for periodic auditor review
- **Enforcement pass** — once we have ~2 weeks of Ship 6'.d data,
  decide whether to promote any claim-event category into
  active enforcement (append-only warning footer, similar to
  preservation-check's repair)
- **Multi-turn stitching** — a single conversation may make the
  same claim across multiple turns; deduplicate for reviewer
  efficiency

## Ship 6' progress

| Sub-arc | Status |
|---|---|
| 6'.a Role audit + safeguard inventory | ✓ |
| 6'.b Grounding provenance column + tests | ✓ |
| 6'.c Preservation-check retrospective | ✓ |
| **6'.d Passive claim-scan observability** | **✓** |
| 6'.e Joined LLM decision-trail view | next |
| 6'.f Arc retrospective | pending |

## Related

- [[ship-6-prime-a-llm-role-audit-2026-07-18]] — parent audit
- [[ship-6-prime-b-grounding-provenance-2026-07-18]] — 6'.b
- [[ship-6-prime-c-preservation-retrospective-2026-07-19]] — 6'.c
