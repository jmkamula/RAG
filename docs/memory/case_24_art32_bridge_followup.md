---
name: case-24-art32-bridge-followup
description: Eval case
metadata: 
  node_type: memory
  type: project
  originSessionId: 99048f90-bd73-4ace-9570-e5eec76ba3e0
---

Eval case #24 ("what is our GDPR Art.32 status?") is flagged known-stale alongside #25 as of 2026-05-31. Test asserts `must_contain=["Art.32", "A.5"]` — i.e. the answer should mention at least one ISO 27001 A.5.x bridge control because Art.32 derives via xfw inheritance from ISO controls.

**When it broke:** Between 2026-05-28 (calib commit — case #24 PASS) and 2026-05-30 (batch 2 commit — case #24 already FAIL in `eval_20260530_0806_phase_b_batch_2.csv` and `eval_20260530_0902_phase_b_batch_2_v2.csv`). The batch 2 commit message reported "54/55 PASS" but the CSV evidence shows actual was **53/55** — #24 had already regressed and was not caught at commit time. Batch 3 inherits the regression, not the cause.

**Pass rate now:** ~20% (manual reruns: 1/3 passed in batch 3 session; 0/2 in eval runs). The answer is fundamentally Art.32-centric without bridging to A.5 controls most of the time. When the bridge does appear it is from xfw_targets retrieval surfacing the A.5.30 / A.5.7 / A.5.x related controls.

**Why:** The LLM context for Art.32 status questions is being built primarily from POSTURE_STATUS (live finding tag) + STANDARD_KNOWLEDGE (Art.32 text), without consistently injecting xfw_targets (the linked ISO 27001 bridge controls). Likely root cause is a change in `rag/graph_expander.py` or `rag/context_assembler.py` around 2026-05-30 (batch 2 timeframe) that altered how xfw expansion is fed to the LLM, but git archaeology has not been done.

**How to apply:**
1. Treat as known-stale alongside #25 until investigated. Batch 3 ships at 58/60 PASS with both flagged.
2. **Do not** attribute new FAILs on #24 to whatever current change is in flight — it has been failing since 2026-05-30.
3. When investigating, start with: `git log --oneline 2026-05-28..2026-05-30 -- rag/graph_expander.py rag/context_assembler.py rag/llm_answer.py` to find candidate commits, then trace a single Art.32 query end-to-end through graph_expander → context_assembler → llm_answer to see when xfw_targets get dropped from the context.
4. Two viable fixes once cause is located: (a) restore reliable xfw_targets injection into LLM context for Layer-2 nodes, or (b) relax the assertion to require *either* `["A.5"]` *or* explicit "derives from ISO 27001" / "Art.32 inherits posture" phrasing — but option (a) is the right one since the test is asserting a real user-value behaviour, not a phrasing artefact.

**Why the rule matters:** The CLAUDE.md "no regressions below the case count" rule has now been violated for two batches in a row (batch 2 silently, batch 3 acknowledged). Future curation batches should explicitly diff the eval CSV against the prior baseline as part of pre-commit verification, not just rely on the PASS-count summary which can be misread.

Related memory: [[curation-phase-b-batch-3-2026-05-31]] flagged this at ship time.
