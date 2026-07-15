---
name: ship-2-prime-casefile-arc-2026-07-15
description: Full Ship 2' arc (2026-07-15) — case-file pattern replacing ~22k-token rank_answer prompts with ~2k-token digest + deterministic preservation-check repair. Behind CASEFILE_ENABLED flag during rollout.
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 2' arc — SHIPPED 2026-07-15 across commits f246df3 → 93fb034.
Rewrite of `rank_and_answer`'s prompt-assembly + post-processing.

**Why:** `rank_answer` prompts averaged 21,731 tokens per call over
a 14-day window (from `ai_call_log`), peaking at 61,827. The LLM
generated ~550-token answers from 22k-token contexts — a 40× ratio
that diluted attention on the actual evidence. Case #14/#33
residuals (LLM stochastically dropping OFI acronym / A.5.1 ref
from prose) were the visible symptom of that dilution.

**Pivot from Ship 2:** Original Ship 2 (2026-07-15 morning) built
`AnswerPayload` dataclasses per taxonomy — 2,000 LOC of type
scaffolding that RESHAPED ResolvedContext without adding new
information. User caught the duplication ("btw are we sure we
are not building something that already exists?"). Ship 2.0 + 2.1
were reverted in commit f246df3. Ship 2' rebuilt lean.

**How to apply:** Every future prompt-assembly change should respect:

1. **The CaseFile is the ground truth.** Any new signal (session,
   incidents, doc contexts) enters the CaseFile once; digest +
   preservation both read from it. Never build a parallel view.

2. **Digest is fixed-slots, empty-omitting.** No per-taxonomy
   branching. Section budgets are soft — items truncate, not lines
   clip mid-string. Test the token budget explicitly (< 2000).

3. **Preservation is APPEND-ONLY.** The repair pass never rewrites
   LLM prose. Missing elements go into a `↳ Compliance facts: ...`
   footer, matching Ship 1.14's bridge-footer pattern. Auditor
   provenance survives; LLM's narrative stays intact.

4. **Feature-flag rollout.** New pipeline paths hide behind an env
   flag; any exception in the new path falls back to the legacy
   route. The case-file flow can NEVER block a response.

**Arc phases** (all landed 2026-07-15):
- 2'.a audit — 14-day ai_call_log baseline: 21,731 avg / 61,827 peak
- 2'.b CaseFile dataclass — 17 unit tests
- 2'.c build_prompt_digest — 37 tests; realistic case = 658 tokens
- 2'.d extract_preservation_spec — 16 tests
- 2'.e check_and_repair — 23 tests
- 2'.f wire into rank_and_answer (CASEFILE_ENABLED flag)
- 2'.g schema_v68 chat_casefile_log — observability
- 2'.h eval + docs + default flip

**Component map:**
- `rag/casefile/types.py` — CaseFile (wraps ResolvedContext + intent +
  session + tenant + last_entity + incidents)
- `rag/casefile/digest.py` — build_prompt_pair, section renderers,
  approx_tokens helper, _rank_posture_refs (cited > session > NC >
  OFI > Comply)
- `rag/casefile/preservation.py` — PreservationSpec dataclass +
  extract_preservation_spec (required_refs, draft_refs,
  verdict_by_ref, bridge_footer)
- `rag/casefile/repair.py` — check_and_repair, RepairEvent, four
  event kinds (missing_ref / missing_draft_near_ref /
  missing_verdict_near_ref / missing_bridge_footer)
- `rag/casefile/log.py` — log_casefile (silent-fail like consensus)
- `db/schema_v68_chat_casefile_log.sql`
- `rag/llm_answer.py::LLMAnswer._casefile_flow` — the new path
- `rag/llm_answer.py::_is_uuid_shape` — detects UUID-shaped
  tenant_name (which is how arion_graph passes it today)

**Token-budget target: ~2,000 tokens** (10× reduction from 21,731
baseline). Smoke test on realistic Arion case: 442 sys + 216 user
= 658 total.

**Escape hatches:**
- `CASEFILE_ENABLED=0` (default) — legacy path, unchanged
- Exception in `_casefile_flow` — logged, falls back to legacy
- `USE_LEGACY_CLASSIFIER=1` (Ship 1) still applies to intent layer

**Observability targets** (chat_casefile_log):
- Confirm token distribution shifts (measure user_digest_tokens vs
  legacy baseline of 21,731)
- Track repair_events_count per kind — high missing_ref rates
  indicate the digest needs to surface that element more
  prominently OR the required_refs computation is too aggressive
- casefile_enabled + shadow_mode fields enable per-slice analysis

**Related memories:**
- `[[ship-1-consensus-arc-2026-07-15]]` — Ship 1 was the intent
  layer; Ship 2' is the answer-assembly layer. Together they form
  a coherent chat pipeline: consensus-classified intent →
  case-file digest → preservation-checked answer.
- `[[feedback-eval-with-each-feature]]` — rule to add eval cases
  per change. Ship 2'.h adds cases 216+ (locking preservation)
  when the flag is flipped.
- `[[feedback-eval-state-drift]]` — Ship 2''s preservation footers
  produce deterministic content, making case assertions more
  robust against LLM phrasing variance.

**Reversal path:** if the flag flip regresses eval, roll back by
setting CASEFILE_ENABLED=0. The revert plan does NOT require code
changes — the legacy path is intact behind the flag branch.
