---
name: compose-posture-any-progress-ofi
description: "REVERTED 2026-06-05: any-partial-→OFI rule (shipped 2026-06-04) reverted because OFI was too generous; new rule requires ≥1 fully satisfied child to earn OFI. Partial evidence still surfaced in reason and per-leaf serializer."
metadata: 
  node_type: memory
  type: project
  originSessionId: b7702385-93e8-4fb5-8bcc-881816acb712
---

## Status

REVERTED 2026-06-05. The "any partial → OFI" rule shipped 2026-06-04 (commit 53fbad7) was too generous — promoted controls to OFI even when no child was fully fulfilled. User flagged this directly on Art.16 case ("0 of 5 satisfied · 1 with partial evidence" → NC→OFI proposal): partial work alone doesn't merit an OFI promotion; the verdict should stay NC until at least one child is fully fulfilled.

## Current rule (2026-06-05)

In `rag/posture/fulfilment_engine.py:_compose_posture` for ALL / AT_LEAST_N ops:

- All outcomes True → **Comply** (unchanged)
- Zero outcomes True → **NC** (regardless of partial — stricter than 2026-06-04 rule)
- ≥1 outcomes True (not all) → **OFI**

ANY op unchanged.

`progress` argument is retained but no longer lifts NC → OFI. It still feeds `_build_reason` so the reason string surfaces `"(N with partial evidence)"` — partial work stays visible in the verdict surface, just doesn't promote the verdict.

## Why the original rule was wrong

OFI as a verdict means "in progress toward compliance" — implies real, fulfilled progress. Partial-only evidence (e.g. A.5.18 register with 4/7 MUSTs recognised, no other leaves) is not meaningful progress toward control compliance — it's pre-completion work on a single artefact. Promoting to OFI inflated the OFI count and de-emphasised genuine OFI controls (those with ≥1 fully done leaf).

User wording: "keep it NC until 1 child is fully fulfilled".

## How to apply

When recomputing posture: NC means no child fully done yet. Partial-evidence counts surface in the reason string, not in the verdict. OFI implies a real demonstrable starting point (≥1 fully satisfied leaf).

If looking at a control reported as NC with partial evidence in chat: the engine is saying "you've started but no single artefact is complete yet". Worth surfacing in posture exports.

## Partial-evidence visibility (2026-06-05 surface enhancements)

Three coordinated surface changes ship alongside the rule reversal:

1. **Chat (`stage2_approval_chat.list_one`):** when an active engine PA exists and PC.engine_proposal_status='none' (concurrence), chat now responds "engine concurs with live at 'X'. Reason: ..." — previously this was a terse "no current proposal". Partial-evidence count surfaces in the reason text.

2. **Verdict serializer (`api_server._serialize_verdict`):** each leaf child carries `items_recognised: list[str]`, `items_unrecognised: list[str]`, and a derived `partial: bool` flag (True if not satisfied but ≥1 item recognised). UI consumers can distinguish three states.

3. **UI renderer (`static/arioncomply.html:renderRow`):** three-state marker for verdict tree children — ✓ satisfied · ◐ partial (with `(N/M recognised)` inline detail) · ✗ no evidence. Currently dormant on Arion because no Stage-2 proposal has a partial leaf (queue is down to A.5.23 + A.5.34, both with 1 fully + 3 empty); fires once any control reaches OFI with mixed partial+empty leaves.

## Writer supersession (also 2026-06-05)

`_persist_engine_proposals` now supersedes any stale pending engine PA when the engine's view shifts to NC/OFI concurrence with live. Without this, the rule reversal would have left 18 stale pending OFI proposals from the 2026-06-04 sweep — the Stage-2 queue would still show them despite the engine no longer holding the view. The supersede also resets PC.engine_proposal_status to 'none'.

## Impact on Arion (2026-06-05 sweep, post-revert)

- Engine NC: 150 → 168 (the 18 controls that flipped to OFI under the prior rule are back to NC).
- Stage-2 pending queue: 2 entries (A.5.23 + A.5.34, both engine-OFI-vs-live-Comply at 1/4). Down from ~20 pending under the prior rule.
- 8 eval cases (Art.6 / Art.16 / Art.17 / Art.24 / Art.25 / Art.32 / 6.1.2 / A.5.9) updated to expect "engine concurs with live at 'NC'" + (where applicable) "partial evidence". Art.32 omits the "partial evidence" assertion because pure DerivedSpec cascade loses the partial signal under the new rule (deps roll up to NC, child_progress=False at the parent).
- 196/198 PASS (baseline; #2 + #25 known-stale).

## 2026-06-09 follow-up: user re-confirmed the strict rule

After uploading "Information Security and Data Management Process.docx"
and approving all 18 findings (7 ISO + 11 GDPR xfw), user observed
that NO Stage-2 entries appeared. Diagnosis: engine recomputed all 18
controls, every verdict matched live (NC=NC or OFI=OFI), so engine-
agreement suppression skipped writing Stage-2 entries. The compose
rule was working as designed — the doc's high-level claims ("Implement
RBAC", "incidents trigger response") count as PARTIAL evidence on
their leaves but don't fully satisfy any leaf, so the strict rule
keeps NC at NC and OFI at OFI.

User direction: **"leave it as-is"** — strict rule reconfirmed. Doc-
upload approvals that yield only partial-leaf evidence are a known,
acceptable outcome under the rule. Stage-2 movement requires evidence
that fills ALL MUSTs on at least one leaf.

This is the cost side of the rule's benefit: it keeps the OFI
population honest (no inflation from sprinkled partials) at the cost
of needing more substantive evidence per upload to move the verdict.

## Related

- [[engine-nc-at-zero-satisfied]] — the NC-at-zero rule this works alongside.
- [[engine-agreement-suppression]] — concurrence path; the chat surface enhancement here builds on the writer's 'active' PA write from that fix.
- [[leaf-evaluators-phase2-evidence-type-drop]] — the prerequisite that lets workbook findings reach the leaf evaluator and provide `items_recognised`.
- [[stage1-engine-kick-after-batch]] — the auto-sweep that fires after
  Stage-1 approval; surfaces engine concurrence (and thus the
  "no Stage-2 movement" outcome) immediately rather than on next manual sweep.
