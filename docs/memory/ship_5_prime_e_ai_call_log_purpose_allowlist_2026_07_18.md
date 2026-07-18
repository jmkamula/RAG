---
name: ship-5-prime-e-ai-call-log-purpose-allowlist-2026-07-18
description: "Ship 5'.e — add missing purpose values to ai_call_log CHECK constraint (Ship 5'.a INFORMATIONAL finding 9)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 5'.e (2026-07-18) — closes the last Ship 5'.a finding.

## The bug

`ai_call_log_purpose_check` CHECK constraint had been throwing
constraint-violation warnings during evals for months. Root
cause: two purpose values used in production code weren't in
the allowlist:

- `consensus_gatekeeper` (Ship 1 consensus arc — bounded LLM
  arbiter in `rag/consensus/gatekeeper.py:283`)
- `enrichment_tier2` (Ship 5'.c — tier2_generator's migration
  off direct OpenAI to `llm_client.call`)

Both writes silently failed via `ai_trace`'s error-swallow. We'd
been missing ~5-15% of LLM-call telemetry:
- All chat gatekeeper calls (fires on ~5-15% of chat turns per
  Ship 1 arc's design)
- All tier2 enrichment runs (offline, but still worth logging
  for cost + latency)

## Fix — schema_v80

Extended the allowlist from 16 to 18 values. Existing rows with
legacy purposes are unaffected — CHECK only applies to future
INSERTs. Smoke-tested both new values via manual INSERTs.

## Discipline note

Added a `COMMENT ON COLUMN ai_call_log.purpose` pointer to this
memory entry so the next time someone adds a purpose, they know
to bump the allowlist in the same migration.

Also: adding an ai_trace WARN-level log for constraint-violation
errors is arguably worth doing (currently DEBUG or swallowed).
That's the kind of thing that would've caught this earlier.
Noted as follow-up, not shipped in this arc.

## Baseline

Eval running. Ship 5'.e is a pure DB constraint change — no
Python behavior change, no RAG-path change. Regression guard
only.

## Ship 5 progress

| Sub-arc | Status |
|---|---|
| 5'.a Audit | ✓ |
| 5'.b Embedding consolidation | ✓ |
| 5'.c Temperature + tier2 migration | ✓ |
| 5'.d Dead code + llm_models module | ✓ |
| **5'.e ai_call_log purpose allowlist** | **✓** |
| 5'.f Arc retrospective | next / close |

## Related

- [[ship-5-prime-a-llm-audit-2026-07-18]] — audit finding 9
- [[ship-5-prime-c-temperature-tier2-2026-07-18]] — where the
  enrichment_tier2 purpose was introduced
