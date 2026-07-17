---
name: feedback-posture-test-state-cleanup
description: "Manual posture_controls edits for smoke tests must restore confirmation_status + finding through the guard trigger, not just finding"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ad-hoc UPDATEs on `posture_controls` for smoke tests (e.g. Ship 3'.b
freshness_expiry manual seed) MUST restore BOTH `finding` AND
`confirmation_status`. Restoring only `finding` while leaving
`confirmation_status='document_confirmed'` from an earlier real upload
suppresses engine proposal overlay and silently regresses stage2
eval cases (#48 A.5.9 arc).

**Why:** `fn_posture_confirmation_guard` blocks most explicit
transitions back to `draft`/`unconfirmed` from `document_confirmed`,
so once you flip live away from what the doc supported, the
confirmation_status is stuck lying about a doc that no longer
justifies it. Stage-2 reader treats `document_confirmed` as "human
already agreed" and hides the engine's proposal.

**How to apply:**

- When manually editing posture_controls for a test:
  1. Snapshot the ROW before touching it (SELECT * WHERE ...).
  2. If you change `finding`, ALSO restore `confirmation_status` to
     its snapshot value in the same restore statement.
  3. If the guard rejects the restore (document_confirmed →
     draft/unconfirmed is invalid), use the trigger-bypass pattern:
     ```sql
     ALTER TABLE posture_controls DISABLE TRIGGER trg_posture_confirmation;
     UPDATE posture_controls SET ... WHERE ...;
     ALTER TABLE posture_controls ENABLE TRIGGER trg_posture_confirmation;
     ```
     (trigger name is `trg_posture_confirmation`, not
     `fn_posture_confirmation_guard` — that's the function it calls.)
  4. Call `load_posture(pg, tenant)` post-restore so engine overlay
     re-materializes.
- Prefer designing smoke tests against a throwaway tenant seed rather
  than the eval-covered `00000000-0000-0000-0000-000000000001` Arion
  tenant when possible.

Related: [[feedback-eval-state-drift]] — same class of hazard;
this one is the mechanism.
