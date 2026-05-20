---
name: hitl-two-stage-rollout-gotchas
description: "Non-obvious scars from the HITL two-stage rollout — confirmation-guard CHECK/trigger drift, Stage-1/Stage-2 grammar disjointness, eval ordering, engine overlay gate, chat-user placeholder"
metadata: 
  node_type: memory
  type: project
  originSessionId: e02ef53a-6116-4dde-a064-7c0a9bab0a34
---

Things that bit during the HITL two-stage rollout (commits `0a0eb01..58401ee`, shipped 2026-05-20) that won't be obvious from reading the current code. See [[hitl-two-stage-approval-design]] for the design.

**1. CHECK-vs-trigger drift on `posture_controls.confirmation_status` / `confirmation_log.action`.**
The v24 migration added `document_confirmed` and `engine_confirmed` to the CHECK constraints but did **not** update `fn_posture_confirmation_guard`. The v7 trigger still raised on every write involving the new states, so every Stage-1 approval silently fell into the idempotent `no_pending` branch — appearing to succeed while writing nothing. v25 (`db/schema_v25_hitl_confirmation_guard.sql`) added the `any → document_confirmed` and `any → engine_confirmed` transitions. **Why:** symptoms looked like a writer bug, not a trigger bug — wasted hours chasing the wrong layer. **How to apply:** any time a CHECK constraint gains new values for a column that has a trigger validating transitions, audit the trigger in the same migration. Grep for trigger functions referencing the column before shipping.

**2. SECURITY DEFINER required on rebound functions.**
The v24 rebuild of `fn_posture_confirmation_guard` dropped `SECURITY DEFINER` (the v7 version had it). RLS on `confirmation_log` then blocked inserts from the trigger context. v25 restored it. **How to apply:** when `CREATE OR REPLACE FUNCTION`-ing a trigger function that touches RLS-guarded tables, verify the SECURITY DEFINER clause survives the rewrite.

**3. Stage-1 vs Stage-2 intent grammar disjointness.**
The two surfaces share the verbs `approve`/`reject`/`list`. Disjointness is enforced by required object words:
- Stage-1 (`rag/posture/stage1_approval_chat.py`): `findings|extractions` + control ref
- Stage-2 (`rag/posture/stage2_approval_chat.py`): `engine verdict|proposal` + control ref

Both surfaces also live behind their own CLEAR_INTENT_PHRASES entries in `rag/classifier.py`. **How to apply:** when adding new intents that share verbs with these surfaces, require an object word; do not rely on classifier ordering alone. The classifier is regex-first-match so collisions silently route to the wrong handler.

**4. Engine overlay gate now blocks unapproved proposals.**
`posture_loader._apply_engine_overlay` skips rows whose `engine_proposal_status != 'approved'`. This changed the meaning of "engine verdict" in headlines: pre-rollout, the engine's Comply→OFI flip showed up immediately in the answer; post-rollout it only shows up after Stage-2 approval. Proposals stay visible through the Stage-2 list surface but do not pre-empt the user's decision in the headline. **How to apply:** if a future feature wants to "preview" engine verdicts in answers without approval, it must bypass the overlay gate explicitly — not paper over it by writing `engine_proposal_status='approved'`.

**5. `confirmation_log.performed_by NOT NULL` needs a fallback.**
Chat-driven approvals don't yet have session-bound user ids. v25 seeds a per-tenant `chat-user` placeholder and the trigger falls back `NEW.confirmed_by → app.user_id → chat-user lookup`. **How to apply:** when session→user wiring lands, remove the chat-user fallback last (after writers start setting `confirmed_by`), and consider a constraint that bans the placeholder for non-chat sources.

**6. Eval case 38 is position-critical.**
`tests/eval_suite.py` case 38 approves A.5.1's engine proposal. It must run **before** case 33 ("are we ISO 27001 A.5.1 compliant?"). Once approved, the overlay gate lets the engine's OFI verdict reach the headline; without that approval first, case 33 sees the raw `posture_controls.finding` and the assertion drifts. **How to apply:** if reordering or removing case 38, audit every later case that depends on A.5.1 posture state. The dependency is implicit — the eval suite has no fixture-reset between cases.

**7. Stage-2 answer phrasings are eval-locked.**
`"Engine verdict for X is already approved."` (idempotent re-approve) and the list-queue phrasing both satisfy substring assertions in cases 37/38. Don't reword without checking the eval.
