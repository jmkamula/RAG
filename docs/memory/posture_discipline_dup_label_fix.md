---
name: posture-discipline-dup-label-fix
description: "SHIPPED 2026-05-26: fixed the dup-label bug (control listed under both Comply and OFI) via context_assembler relabel + system_prompt POSTURE FINDING DISCIPLINE block. Residual NC↔OFI drift on multi-control answers is a separate LLM-side issue."
metadata: 
  node_type: memory
  type: project
  originSessionId: 23cb7b33-d854-4985-9f9a-c02de86209a1
---

**Status: SHIPPED 2026-05-26.**

User reported (2026-05-26 chat session) that the LLM was listing the same control under both "Opportunities for Improvement (OFI)" and "Compliance (Comply)" headings in a single posture answer — e.g. A.5.30 (ICT readiness for BC) appearing in both sections with contradictory narrative. They asked "is the LLM saying the control is done but ongoing monitoring is missing?" — which clarified the LLM's real reasoning and what to keep vs suppress.

**Root cause (context-side):** `_render_posture_summary` in `rag/context_assembler.py` labelled `gap_description` as `Gap:` regardless of finding. For Comply rows, `gap_description` actually carries the **evidence narrative** (e.g. "ICT readiness maintained through Microsoft Azure and 365 redundancy"), so the LLM saw `✓ Comply A.5.30 / Gap: …` and naturally treated that text as OFI input. The column is overloaded by the upstream writer; the fix is to relabel at render time based on finding: `Evidence:` for Comply, `Gap:` for OFI/NC.

**Root cause (prompt-side):** the system prompt's "POSTURE FINDINGS" section said "the tag IS the finding" but didn't explicitly forbid dup-label or describe what to do with best-practice advisory commentary. Added a STRICT block with worked WRONG/CORRECT examples plus an ADVISORY COMMENTARY — QUARANTINED block that routes "ongoing monitoring would help" style commentary to a separate `Recommendations` section.

**Product decision** (asked the user via AskUserQuestion): allow advisory commentary but quarantine it under `Recommendations` rather than suppressing it entirely or letting it borrow the OFI heading. Reasoning: the advisory is often genuinely useful domain knowledge (e.g. A.5.30 typically needs ongoing testing per ISO 27001 intent), just shouldn't be confused with a formal posture verdict.

**Verified post-fix:**
- `is A.5.30 compliant?` → "A.5.30 is marked as Comply [DRAFT]" (no OFI taint).
- Multi-control `what is our business continuity compliance status?` → A.5.30 and A.5.29 in Comply only, no longer duplicated.

**Residual issue to track separately:** in the same multi-control answer the LLM moved A.5.18 from NC to OFI. The relabel fix doesn't help here — A.5.18's gap_description is correctly labelled `Gap:` and the tag is `NC` in the context. The LLM is ignoring the tag and re-categorizing based on its own judgment. Probing A.5.18 directly (`is A.5.18 a non-conformity?`) returns NC correctly — so it's a multi-control narrative-drift issue, not a single-control parsing issue. Likely needs a verification-pass tightening or a more imperative "tag is the verdict — copy it exactly" instruction. Not in scope for this fix.

**Eval coverage:** case 41 (`is A.5.30 compliant?`, must_contain=["A.5.30","Comply"], must_not_contain=["A.5.30 [OFI]", "A.5.30 is OFI", "A.5.30 is an opportunity for improvement", …]). Single-control probe — robust against the substring assertion limits. Multi-control dup-label not directly tested because substring matching can't express "control X must not appear in BOTH OFI and Comply sections."

Related: [[engine-nc-at-zero-satisfied]], [[hitl-two-stage-approval-design]].
