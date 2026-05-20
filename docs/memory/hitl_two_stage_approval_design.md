---
name: hitl-two-stage-approval-design
description: Two-stage HITL approval model — extraction findings then engine verdicts. SHIPPED 2026-05-20 across commits 0a0eb01..58401ee; see [[hitl-two-stage-rollout-gotchas]] for operational scars
metadata: 
  node_type: memory
  type: project
  originSessionId: ab2912f3-a587-4819-891f-14d62eba574c
---

Two-stage HITL model for posture approval, designed 2026-05-20.

**Status: SHIPPED 2026-05-20** across five sequential commits on `main`:
- `0a0eb01` — schema additions (review_status, engine_proposed_*, change_kind, v24 confirmation guard)
- `cd91c2a` — writer to `system_finding`, intake enumeration
- `9774039` — Stage-1 batch approval chat surface
- `abe1f6a` — engine filter on review_status='approved' + verdict persistence to engine_proposed_finding
- `58401ee` — Stage-2 approval surface + v25 trigger fix-up

Operational gotchas discovered during rollout are captured in [[hitl-two-stage-rollout-gotchas]] — read before touching the confirmation trigger, the Stage-1/Stage-2 intent grammars, or the engine overlay gate.

**Why:** Today the engine's Comply→OFI overlay flip lives only in `posture_loader`'s in-memory dict — never persisted, never approved. The user wants explicit HITL gating: approve extraction findings first, then approve engine verdicts before they mutate `posture_controls.finding`. Direct application of [[human-in-the-loop-positioning]] — client owns posture, the platform proposes.

**How to apply:** When touching `posture_writer`, `posture_loader`, `engine_runner`, or designing any new intake-related chat surface, treat this as the target architecture. Today's behaviour (writer flips `finding` directly to draft extraction verdict; engine overlay in-memory only) is provisional and should not be extended.

**Model — two sequential approval gates:**

```
upload → extract → document_findings (review_status=pending)
                       │
                       ▼
            user batch-approves per control
                       │
                       ▼
            posture_controls.confirmation_status = 'document_confirmed'
                       │
                       ▼
            engine runs on confirmed findings → engine_proposed_finding
                       │
                       ▼
            user approves engine verdict → posture_controls.finding overwritten
            confirmation_status = 'engine_confirmed'
```

**Locked decisions:**

1. **Batch approval per control.** User reviews all findings for a control together; approves/rejects the bundle. No per-finding auto-promotion of the parent posture row.
2. **7-day TTL on pending findings.** Auto-expire to `is_active=false`, `review_status='expired'`, reason="expired without review". Engine ignores them via the existing `is_active=true` filter. Distinct from explicit rejection — expiry is a UX failure, not an extraction-quality signal.
3. **Digest-based re-upload semantics.** `client_documents.checksum_sha256` drives idempotency. Same digest = no-op. New digest = update; affected controls drop back to pending review, prior `engine_confirmed` invalidated.
4. **Any engine-input change retriggers a fresh proposal cycle.** Uploads, finding revocation, FulfilmentSpec re-curation, acknowledgement withdrawal, time-based leaf staleness. Nothing silently re-overlays. Each transition produces a new proposal carrying its own snapshotted reason. Audit trail lives in `posture_status_log`.
5. **Engine reasons snapshot at proposal time.** Never recomputed on read. Falls out of #4 — every meaningful change spawns a new proposal, so the persisted reason matches what the user actually saw and approved.
6. **Rejection ≠ deletion.** Rejected findings: `is_active=false` + `rejection_reason` + `reviewed_by` / `reviewed_at`. Audit-trail preserving. Future hook: `rejection_reason IS NOT NULL` emits an `extraction_rejected` event in the [[incident-obligations-model]] system. **Expired findings do not trigger this incident.**

**Schema additions (additive only — no rewrites):**

- `document_findings`: `review_status` ('pending'/'approved'/'rejected'/'expired'), `rejection_reason`, `reviewed_by`, `reviewed_at`. CHECK: rejected/expired ⇒ `is_active=false`.
- `posture_controls`: `engine_proposed_finding`, `engine_proposed_at`, `engine_proposal_status` ('none'/'proposed'/'approved'/'rejected'), `engine_approved_by`, `engine_approved_at`, `engine_proposal_reason` (snapshotted).
- `posture_status_log`: add `change_kind` ('extraction'/'engine'/'assessor'/'acknowledgement') for transition explainability.
- Optional new: `document_findings_review_event` for fan-out audit of per-finding decisions.

**Code touch points (orientation, no diffs):**

- `posture_writer._write_posture_controls` — writes to `system_finding` only, not `finding`. Extend source guard (currently `posture_writer.py:483`) to include all `*_confirmed` states.
- `engine_runner.compute_engine_verdicts` — filter source set to `review_status='approved' AND is_active=true`.
- `posture_loader._apply_engine_overlay` — persist verdict to `engine_proposed_finding` instead of overlaying in-memory only. Overlay reads the persisted proposal.
- Intake response (chat surface after upload) — enumerate findings (control_ref + status + excerpt + confidence), not just counts. Today returns `posture_updated: N, skipped: M`; needs the per-finding list.
- New chat surface — per-control engine-proposal review queue (distinct from existing acknowledge-gap surface, which acknowledges *gaps*, not engine verdicts).

**Open considerations to resolve at build time:**

- **Fan-out throttling.** Curation changes (Neo4j FulfilmentSpec edits) and staleness sweeps can invalidate many controls at once across many tenants — proposal flood risk. Throttle or batch.
- **Stalled controls.** Some findings approved, others pending. Either UX nudge ("3 findings pending review on A.5.1") or rely entirely on the 7-day TTL.
- **Migration.** Existing `posture_controls.finding` values stay as-is; new HITL gates apply only to extractions arriving after deploy. No back-confirmation pass.
- **Today's filename-mangling bug** (Access Control Policy.docx → DOC006_Access_Control_Policy.pdf) is separate from this design but will distort the per-finding review surface — auditors will see a fake `.pdf` name attached to docx-extracted findings. Fix before launching the review queue UX.

**Eval suite obligation** ([[feedback-eval-with-each-feature]]): when this lands, add EvalCases for: (a) pending finding does not promote posture, (b) batch-approve flow promotes correctly, (c) engine waits for `document_confirmed`, (d) digest-change resets prior approvals.
