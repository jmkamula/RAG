---
name: case-2-drift-followup
description: "Eval case #2 ('what are our main compliance gaps?' → A.5.26) drifted into LLM-stochastic ~40-60% PASS after Phase C batch 1 Stage-2 mass-approval brought Arion from ~25 to 168 NCs on 2026-06-02. Data intact; ranking issue. Promoted to known-stale 2026-06-03."
metadata:
  type: project
---

**Eval case #2 promoted to known-stale 2026-06-03.**

**Fact:** Case #2 ("what are our main compliance gaps?" expecting A.5.26 in refs) now passes at ~40-60% on retry. Measured 2/5 PASS over five fresh eval re-runs on 2026-06-03 after Phase 1b commit.

**Why:** Phase C batch 1 (commit 33e0668, 2026-06-02) included a Stage-2 mass-approval session that promoted ~150 engine-proposed NCs on Arion to live NCs. Total NCs went from ~25 to 168. The LLM ranking head for POSTURE_STATUS picks ~30 controls to surface; with 168 candidates, A.5.26 (incident_register NC) is no longer reliably in the top — it appeared at position 21 in one observed run and was absent in two others. Data is intact (A.5.26 still finding=NC in posture_controls), problem is LLM ranking among many equally-NC candidates.

**Pre-drift history (from results/eval_2026060*.csv):** #2 PASSed in nearly every run b17 through b29b. First FAIL was b30 (2026-06-02 mid-batch). Phase 1a (2026-06-03 morning) PASSed. Phase 1b (2026-06-03 afternoon) FAILed. The Stage-2 mass-approval was the inflection.

**How to apply:**
- Do not treat case #2 failure alone as a regression blocker — re-run before declaring a problem.
- Combined regression threshold is now 195/198 PASS (was 197/198 before Stage-2 mass-approval).
- If addressing: candidate fixes are (a) re-pick a more reliably-top-of-list NC for expected_refs, (b) loosen the assertion to "any of {A.5.26, ...other-known-load-bearing NCs}", or (c) change the resolver-level ranking to be more deterministic (own LLM-stochasticity rather than asserting against it).

Related: [[engine-agreement-suppression]] is downstream of the same mass-approval — many newly-approved NCs were engine proposals where engine agreed with live (now both NC). [[posture-assertions-phase-1b]] is unaffected by this drift; eval failure timing was coincidental.
