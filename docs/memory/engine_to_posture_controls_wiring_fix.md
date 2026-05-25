---
name: engine-to-posture-controls-wiring-fix
description: "2026-05-25: end-to-end engine→posture_controls→chat wiring shipped. Three changes that together close the gap [[posture-engine-alignment-plan-2026-05-22]] called out: [DRAFT] label fix, leaves<=1 filter fix, GDPR inventory backfill (schema_v27)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 05fd0622-fbff-4999-9132-e4622a40b0f2
---

The "engine produces verdicts but they never reach chat" symptom turned out to be three independent gaps stacked on top of each other. Fixing only one of them would have looked broken from the chat side.

**1. `[DRAFT]` label tuple was incomplete.** `rag/llm_answer.py:879,928` and `rag/resolver.py:676` treated only `{confirmed, overridden}` as non-draft. The CHECK constraint allows two more states the Stage-1 / Stage-2 paths actually write: `document_confirmed` and `engine_confirmed`. So 76 Stage-1-confirmed rows were getting tagged `[DRAFT]` in the LLM prompt, triggering the CONFIRMATION RULE in SYSTEM_PROMPT to hedge with "Our records suggest…" / "A preliminary assessment indicates…" — making confirmed findings sound provisional.

Fixed by expanding the tuple at all 3 sites to `{confirmed, overridden, document_confirmed, engine_confirmed}`. EvalCase 39 ("what is our posture on A.5.1?") locks the contract via must_not_contain on those two phrases.

**2. `_persist_engine_proposals` filter missed derives_from.** `posture_loader.py` had `if len(verdict.leaves) <= 1: continue` at lines 184 (overlay) and 283 (persistence). Predates derives_from composition. GDPR umbrella verdicts have ≤1 direct leaf but compose 2-6 dependencies via `ControlRef` → `derived_from`. So all 20 GDPR engine verdicts were skipped (e.g. Art.32 has 1 leaf + 5 derived; Art.5 has 0 leaves + 2 derived). Only ISO A.5.1 (4 direct leaves) made it through.

Fixed at both sites: `if len(verdict.leaves) <= 1 and not verdict.derived_from: continue`. Skips only when the verdict adds zero composition value. **Why:** without derived_from check, every umbrella article in GDPR is silently dropped from persistence.

**3. GDPR posture_controls inventory was nearly empty.** Even after the filter fix, `_persist_engine_proposals` writes via UPDATE — it requires a posture_controls row to attach to. The DB had exactly 1 GDPR row (Art.28) vs 303 curated GDPR controls in Neo4j. So the SELECT at posture_loader.py:308 found nothing for `(GDPR:2016/679, Art.32)` etc.

Fixed by `schema_v27_posture_source_engine_backfill.sql` + a one-shot backfill that inserts 302 missing GDPR rows for Arion Networks (`finding='Not assessed'`, `confirmation_status='draft'`, `source='engine_backfill'`). The schema migration was needed to extend the `posture_controls.source` CHECK constraint to allow the new audit token `engine_backfill` alongside `chat, questionnaire, document, assessor, self_reported, workbook, Not assessed, engine`.

After all three: 15/20 GDPR verdicts persist as Stage-2 proposals (status='proposed'). The other 5 (Art.13, Art.15, Art.28, Art.30, Art.33) are single-leaf-no-derived — correctly skipped because they add no composition value beyond what `posture_controls.finding` already represents.

**End-to-end flow now:**
1. `load_posture` → engine overlay → `_persist_engine_proposals` writes 15 GDPR proposals
2. Stage-2 review chat surface (`what engine verdicts need review?`) lists them
3. User approves via `approve engine verdict for Art.32` → finding flips Not assessed→OFI, confirmation_status→engine_confirmed
4. Next `load_posture` includes the row (filter passes) → overlay applies (status=approved) → chat answer cites OFI with engine_reason + engine_gap_list

**How to apply:** Phase D (Stage-1 contract change) shipped same session via [[stage1-contract-change-path-a-2026-05-25]] — Stage-1 no longer mutates `posture_controls.finding`, Arion's 27 Stage-1 flips were reverted. Phase B (bulk GDPR curation) still pending. This wiring fix remains infrastructure Phase B will rely on — its curated specs will start producing engine verdicts that this filter + backfill now accept.

**Tenant scope:** Backfill only ran on Arion Networks (`00000000-0000-0000-0000-000000000001`). New tenants will need the same backfill — consider rolling it into the tenant-onboarding path or running it lazily when the engine first encounters a missing row.

Related: [[posture-engine-alignment-plan-2026-05-22]], [[hitl-two-stage-approval-design]], [[engine-verdict-verification-snippet]].
