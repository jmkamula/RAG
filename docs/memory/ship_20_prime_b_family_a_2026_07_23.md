---
name: ship-20-prime-b-family-a-2026-07-23
description: "Ship 20'.b — Family A intro-only structured payload wired to 7 no-refs short-circuit sites; new build_intro_only_structured + CaseFileShim helpers in answer_augment.py"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 20'.b — first delivery sub-arc of Ship 20. 7 no-refs
short-circuit sites now emit intro-only structured payload.
Commit `96031b8`.

## New helpers in `rag/casefile/answer_augment.py`

### CaseFileShim
Duck-typed stand-in for CaseFile. Duck-types the 5 methods
`build_related_cards` needs (`all_nodes`, `posture_for`,
`needs_draft_tag`, `role_of`, `demonstrated_by`). Reserved for
Family B/C in 20'.c/d.

### build_intro_only_structured(text, primary_ref=None)
Family A helper. Returns `StructuredAnswer(intro=IntroCard(...),
actions=[], related=[])`. Frontend renders as single bubble;
consistent envelope with LLM path so clients don't branch on
structured absence.

## Sites migrated

All 7 pass `answer_structured=build_intro_only_structured(...)`
into `build_answer_envelope`:

- deictic_clarify (line 2147, no refs)
- scope_na (line 2402, cloud-only physical/dev)
- cascade_followups (line 2432, overdue triage report)
- risk (line 2454, risk register summary)
- cascade_suppressions (line 2470, suppression state)
- upload_status (line 2555, doc inventory)
- resolver_short_circuit (line 2605, resolver's own SC)

Every site preserves `attach_templates=False`, `attach_advisory=
False` (existing behaviour). `answer_text` still composed from
existing `polish_short_circuit_answer` prose (backward compat).

## Verified end-to-end

- Sync: `what are our physical security gaps?` → scope_na →
  intro carrying composed prose, actions=[], related=[].
- Sync: `what are our top risks?` → risk → same shape.
- Streaming: SSE `type: "answer_structured"` event fires between
  token chunks and `done` for Family A paths.
- Frontend: no changes needed — Ship 18/19 renderer handles
  intro-only fine.

## Ship 20 progress

| Sub-arc | Status |
|---|---|
| 20'.a Design memo | ✓ (9846eb6) |
| **20'.b Family A (this)** | **✓ (96031b8)** |
| 20'.c Family B | next |
| 20'.d Family C | pending |
| 20'.e Eval + retro | pending |

## Related

- [[ship-20-prime-a-short-circuit-design-2026-07-23]] — design
- [[ship-18-prime-arc-retrospective-2026-07-23]] — LLM-path
  structured payload arc this extends
