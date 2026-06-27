---
name: curation-a67-remote-working-promotion-2026-06-27
description: "SHIPPED 2026-06-27: A.6.7 Remote Working promoted from 1-leaf (policy only, 6 MUSTs) to 4-leaf (policy + procedure + register + review_record, 27 MUSTs + 8 SHOULDs total). Closes the LAST single-leaf hole in the catalog — every control is now multi-leaf. trigger_type=profile_fact preserved (gated by ClientFacts.has_remote_workers). Existing policy leaf MUSTs all preserved (item-id stability). Arion's A.6.7 flipped Comply → NC; tenant can fill new leaves via xlsx round-trip."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

A.6.7 single-leaf → 4-leaf promotion, matching the A.6 family pattern
established in batch 21 (2026-06-01). Surfaced by the user
2026-06-27 who noticed A.6.7 displayed "Composition · 1 of 1
satisfied" while every sibling shows 4-of-4.

Pre-promotion: 1 leaf (`req:A.6.7:remote_working_policy`, 6 MUSTs + 2
SHOULDs). Post-promotion: 4 leaves:

| leaf | evidence_type | role |
|---|---|---|
| `req:A.6.7:remote_working_policy` (existing, untouched) | policy | Umbrella rules: equipment, physical, network, access, PII, incident reporting |
| `req:A.6.7:remote_working_procedure` (new, 7+2) | procedure | Per-worker approval/modification/revocation workflow; equipment provisioning; cross-link to A.5.11 / A.5.18 / A.5.24 |
| `req:A.6.7:remote_workers_register` (new, 7+2) | register | Per-worker rows: identity, location, equipment, approval date, review-due, status |
| `req:A.6.7:remote_working_review` (new, 7+2) | review_record | Annual review: register currency, orphan check vs A.5.16, incident review, policy currency |

Total: 6+7+7+7 = **27 MUSTs**, 2+2+2+2 = **8 SHOULDs**.

`trigger_type=profile_fact` preserved across all 4 leaves — A.6.7
remains gated by the remote-work profile fact (only fires when the
tenant has remote workers).

## Catalog mechanics

- New ER variables: `REQ_A67_REMOTE_WORKING_PROCEDURE`,
  `REQ_A67_REMOTE_WORKERS_REGISTER`, `REQ_A67_PROGRAMME_REVIEW`
- Added to `ALL_EVIDENCE_REQUIREMENTS` immediately after
  `REQ_REMOTE_WORKING` with a header comment marking the batch
- Existing `REQ_REMOTE_WORKING` left unchanged — all 6 MUST + 2
  SHOULD item-ids preserved (item-id stability discipline from
  Phase B; see [[curation-phase-b-batch-18-2026-06-01]])
- `description` extended with "umbrella policy leaf; the per-worker
  procedure, the registered-workers register, and the periodic
  programme review are sibling leaves" — same language as the
  A.6.3 family

## Load chain (the Phase B sequence)

1. **`load_to_neo4j.py`** — sync Neo4j to current catalog. Loader
   reports: 648 EvidenceRequirement nodes (was 645, +3 new),
   4306 ChecklistItem nodes (was 4278, +28), pruned 0 stale (clean).
2. **`generate_template_scaffolds.py`** — auto-generate template
   markdown for the 3 new leaves. Writes
   `db/templates/req__A_6_7__remote_working_procedure.md` +
   `_remote_workers_register.md` + `_remote_working_review.md`.
3. **`load_to_postgres.py`** — sync templates table. Reports:
   inserted=3 updated=1 unchanged=644 total=648.
4. **`load_posture(tenant)`** — recompute Arion's verdicts.

## Arion impact

A.6.7 verdict: **Comply → NC** (1 of 4 leaves satisfied — the
existing Remote Working Policy doc covers the policy leaf; the
new procedure + register + review have no evidence yet).

This is the correct + expected behaviour: prior single-leaf shape
was under-specified, gave a too-easy Comply rating. The new shape
surfaces the real evidence gap. Tenant can fill the three new
leaves via:

- xlsx round-trip on the new register leaf
  ([[template-xlsx-roundtrip-phase-b-2026-06-26]])
- docx download + edit for the procedure + review leaves
- form lane for any specific MUSTs

## Significance

A.6.7 was the **LAST single-leaf control in the entire catalog**
(per a survey: 1 of 162 controls). With this promotion, every
ISO 27001 Annex A control, every ISMS clause, and every GDPR
article is multi-leaf at modern Style v2 conventions. The Phase B
arc that began 2026-05-26 is fully closed.

## Cross-control links surfaced in new MUSTs

The new leaves' MUSTs reference:
- A.5.9 asset register (equipment tracking on the register leaf)
- A.5.11 return of assets (revocation path → leaver flow)
- A.5.12 classification (data-class restrictions per remote worker)
- A.5.16 identity register (orphan-row check)
- A.5.18 access review (review pair-check)
- A.5.24 incident response (remote-context incident routing)
- A.5.26 incident register (remote-context incidents for review)
- A.5.27 lessons learned (feedback loop)
- A.7.4/7.7/8.1/8.24 (policy currency check covers these)

## Related

- [[curation-phase-b-batch-21-2026-06-01]] — the A.6 7-pack that
  deferred A.6.7 ("A.6.7 was already curated"). This entry closes
  the loose end.
- [[curation-phase-b-retrospective]] — the arc retrospective. Now
  honestly complete: 1-leaf hole closed.
- [[stage1-queue-sweep-2026-06-27]] — sister memo from earlier
  today: the queue clean-up surfaced the A.6.7 anomaly via the
  user noticing "1 of 1 satisfied".
- [[template-xlsx-roundtrip-phase-b-2026-06-26]] — how the tenant
  will fill the new register leaf.
