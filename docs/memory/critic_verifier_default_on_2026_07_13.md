---
name: critic-verifier-default-on-2026-07-13
description: SHIPPED 2026-07-13 — critic-verifier is now the default LLM extraction pass; USE_CRITIC_VERIFIER_PASS=0 disables for rollback; old pipeline slated for removal in ~2 weeks.
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The critic-verifier LLM extraction pass is now the default in
`rag/intake/extractor.py`. Env flag inverted:

- **Default (env unset)** → critic-verifier fires (confirm/reject
  fingerprint findings + extend via top-N semantic pool)
- `USE_CRITIC_VERIFIER_PASS=0` (or `false`/`no`/`off`) → fall back
  to legacy `_extract_full` / `_extract_sections` pipeline

**Why:** Phase 6 A/B (6 docs on Arion) showed +40.2% discovery,
+39.1% auto-approve, 3.18× cost at $0.24/doc absolute. Wave 4a's
precision feedback loop is the safety net — bad critic findings
get rejected in Stage-1, precision drops, gate tightens
automatically. Old pipeline has no distinct architectural purpose.

**How to apply:** The env flag stays for ~2 weeks as a rollback
escape hatch. If a real-world doc regresses (extract 0 findings /
mass over-extraction / cost spike), set `USE_CRITIC_VERIFIER_PASS=0`
in `.env` and restart API. A follow-up commit (target: 2026-07-27+)
will remove:

- `_extract_full` (rag/intake/extractor.py) — old candidate-list pass-1
- `_extract_sections` — section-based variant
- `_llm_extract` / `_llm_extract_pass2` — inner callsites
- Pass-2 backfill mechanism (the one that never fired on DPIA)
- Old prompt templates + response parsers
- The env flag itself

~600-800 lines of code become deletable at that point.

Related: [[critic-verifier-arc-2026-07-12]] (if written),
[[llm-client-refactor-2026-07-11]] (raw HTTP, provider-neutral).
