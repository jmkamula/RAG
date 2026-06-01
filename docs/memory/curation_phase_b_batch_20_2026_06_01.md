---
name: curation-phase-b-batch-20-2026-06-01
description: Phase B batch 20 — A.5.18 Style v2 alignment (NOT a promotion). Closes the A.5 Organisational Controls arc. Pattern for legacy multi-leaf alignment locked in.
metadata: 
  node_type: memory
  type: project
  originSessionId: cc746afe-8680-4e51-a963-96eb379653f8
---

Phase B batch 20 — A.5.18 (Access rights) Style v2 alignment. NOT a
promotion: A.5.18 was the FIRST control promoted to multi-leaf back on
2026-05-26 (the OG NC from case #1 — the gap that started the whole
curation arc). This batch brings it up to A.5.16/A.5.17 identity-family
modern conventions.

**Why:** User asked to "close the A.5 arc" after batch 19 closed A.5.3x.
A.5.18 was already 4-leaf but with pre-Phase-B conventions (shorter
descriptions, fewer MUSTs, looser freshness, no SLA-met flag). Aligning
brings the A.5 block to consistent Style v2 across all controls.

**How to apply:** Pattern for any "legacy multi-leaf" alignment. Analogous
to [[curation-phase-b-batch-7-2026-05-31]] (A.5.1 alignment). Compare to
the most recent batch in the spine family + add modern MUSTs (rubber-
stamping checks, paired-family integration, SLA proof, residual cleanup),
tighten freshness where the domain volatility warrants it, preserve ALL
existing item-ids to avoid breaking DerivedSpecs or eval cases.

**Shipped (commit pending — current session 2026-06-01):**
- All 4 leaves expanded: procedure 5→8 MUST + 2→3 SHOULD; register 4→7
  MUST + 2→3 SHOULD; review 4→8 MUST + 2→3 SHOULD; revocation_record
  4→8 MUST + 2→3 SHOULD
- 6 new MUSTs + 4 new SHOULDs total
- Review freshness 365 → 180d (matches A.5.16/A.5.17/A.5.25/A.5.26
  high-volume drift family)
- All 17 existing item-ids preserved
- No new eval case (engine NC == live NC → Stage-2 suppression; A.5.26
  precedent)
- Eval 76/78 → 77/78 (CLEAN UPPER BOUND — cases #1 + #2 PASS, only #25
  known-stale fails). Sixth consecutive PR with no non-stochastic
  regression.

**Item-id preservation:**
No DerivedSpecs reference A.5.18 items. Only the 4 leaf-ids matter
(`req:A.5.18:access_rights_procedure`, `:access_rights_register`,
`:access_rights_review`, `:access_revocation_record`) — all 4 preserved.
17 existing checklist-item ids also preserved despite ~50% expansion
in MUST count — new ids added alongside, none replaced.

**Modern MUSTs added (A.5.16/A.5.17 family parity):**

On `access_rights_procedure`:
- `sla_targets` — SLA targets per operation (grant/modify/revoke); drives
  the rev_sla_met flag
- `service_account_handling` — explicit non-human identity handling
  (weakest spot in most access programs)
- `identity_link` — explicit linkage to A.5.16 identity register (no
  orphan access)

On `access_rights_register`:
- `reg_idmgmt_link` — promoted SHOULD → MUST. Bidirectional pairing
  with A.5.16 identity register; closes "access points to disabled
  identity" gap
- `reg_last_verified` — per-row last-verified date (drives staleness
  detection between formal reviews)
- `reg_review_due` — per-row next review-due date (drives the review
  leaf's schedule)

On `access_rights_review`:
- `rev_coverage` — full vs. sampled coverage stated explicitly
- `rev_orphan_check` — orphan-access check (every register row
  reconciled against A.5.16 identity register; orphans surfaced and
  revoked)
- `rev_privileged_check` — privileged subset reviewed with extra
  scrutiny (cross-link to A.8.2)
- `rev_identity_pair` — identity-family pair check (A.5.16 reviewed
  in parallel)

On `access_revocation_record`:
- `rev_sla_met` — SLA-met flag (the famous "within 24h of role-change"
  timeliness proof, mirrors A.5.16:rev_sla_met)
- `rev_identity_pair` — bidirectional A.5.16 ↔ A.5.18 lifecycle
  pairing (closes "identity disabled but access lingers" gap)
- `rev_residual_cleanup` — mailbox/file-share/group/OAuth/API key
  cleanup (mirrors A.5.16:rev_residual_cleanup)
- `rev_completeness` — all access rights for the subject accounted
  for, not just primary RBAC

**Why no new eval case (engine-agreement suppression):**
A.5.18 live posture is NC (per case #1). After alignment, engine
returns NC at 0/4. Engine NC == live NC → [[engine-agreement-
suppression]] kicks in at posture_loader.py:343 — Stage-2 doesn't
propose anything, so the "engine proposes NC at 0/4" pattern doesn't
surface. Same precedent as A.5.26 ([[curation-phase-b-batch-4-2026-
05-31]]).

Cases #1 + #2 still lock A.5.18 NC via the gap_analysis path
(unchanged behavior — live posture is still NC).

**A.5 arc complete:**
The A.5 Organisational Controls block is now fully multi-leaf at
Style v2 conventions:
- A.5.1 (InfoSec policy) — Style v2 aligned batch 7
- A.5.2 (Roles + responsibilities) — calibration #3
- A.5.3 (Segregation of duties) — Phase B batch 2
- A.5.4 (Management responsibilities) — Phase B batch 2
- A.5.5 (Authority contacts) — Phase B batch 1
- A.5.6 (SIG contacts) — Phase B batch 1
- A.5.7 (Threat intel) — Phase B batch 5
- A.5.8 (Project security) — Phase B batch 8
- A.5.9 (Asset inventory) — Phase B batch 1
- A.5.10 (Acceptable use) — Phase B batch 2
- A.5.11 (Return of assets) — Phase B batch 9
- A.5.12 (Classification) — Phase B batch 2
- A.5.13 (Labelling) — Phase B batch 10
- A.5.14 (Information transfer) — Phase B batch 11
- A.5.15 (Access control policy) — Phase B batch 2
- A.5.16 (Identity management) — Phase B batch 12
- A.5.17 (Authentication info) — Phase B batch 13
- A.5.18 (Access rights) — promoted 2026-05-26, aligned Phase B batch 20
- A.5.19-23 (Supplier+cloud 5-pack) — Phase B batch 3
- A.5.24 (Incident planning) — Phase B batch 14
- A.5.25-27 (Incident triage 3-pack) — Phase B batch 4
- A.5.28 (Evidence handling) — Phase B batch 6
- A.5.29 (Disruption security) — Phase B batch 15
- A.5.30 (ICT readiness) — Phase B batch 16
- A.5.31-32 (Legal register + IPR) — Phase B batch 1
- A.5.33 (Records protection) — Phase B batch 17
- A.5.34 (PII protection) — Phase B batch 18
- A.5.35-37 (Review + procedures 3-pack) — Phase B batch 19

37 of 37 A.5 controls multi-leaf at Style v2. The A.5 block is the
benchmark for what "fully curated" looks like.

**Next:**
A.6 People Controls (7 controls) or A.7 Physical Controls (14 controls)
are the natural next bulk batches. Multi-control batching pattern proven
across batches 1, 3, 4, 19. Could even attempt the full A.6 block as a
single batch given the pattern is so well-locked in.

Style v2 alignment pattern is also now established — applies to any
control that was multi-leaf-promoted before the modern conventions
landed (e.g., A.8.2/A.8.11/A.8.24/A.8.25/A.8.26/A.8.27 are
calibration-era multi-leaf, may benefit from similar alignment).
