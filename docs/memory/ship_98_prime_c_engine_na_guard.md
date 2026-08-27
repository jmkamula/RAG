---
name: ship-98-prime-c-engine-na-guard
description: Ship 98'.c — surfaced by dev-queue audit. Ship 66'.a promoted N/A to applicability_status SSoT but `_persist_engine_proposals` never got the memo — 14 A.7 physicals on cloud-only Arion had pending NC engine proposals despite applicability_status='na'. Fixed the write path + superseded 18 stale N/A proposals + cleaned up 1811 pending Stage-1 dev residue with per-source discipline. Adds 2 regression guards.
metadata:
  type: project
---

# Ship 98'.c — Engine N/A guard + intake queue cleanup (2026-08-27)

## Framing

Operator: "our intake queues were filled while developing and
testing arion workbook, can we audit + return them to their
normal status."

Two problems surfaced:

1. **Stage-1 residue**: 1,811 pending items on Arion from Ships
   89-94 workbook + arbiter dogfood cycles.
2. **Stage-2 anomaly**: 28 pending engine proposals — 18 of them
   on controls the tenant had already scoped OUT
   (applicability_status='na'). This shouldn't happen. Ship
   66'.a codified N/A dominance via the applicability_status
   SSoT column.

The Stage-1 was straightforward dev-cleanup. The Stage-2
finding was a real code bug.

## Root cause

`rag/posture_loader.py::_persist_engine_proposals` (Phase 1c) —
where the engine writes Stage-2 proposals from computed
verdicts. It fetches `finding + engine_proposal_status` from
`posture_controls` to decide whether the proposal is a no-op
repeat. It DOES NOT fetch `applicability_status`.

Ship 66'.a (2026-08-12) promoted N/A from `finding='N/A'` to
`applicability_status='na'` — the SSoT for scoping. Load-path
readers were migrated ([[feedback-na-dominance-via-applicability-column]])
but this specific WRITE path was missed in the cascade. Result:
engine ran per usual on all controls, computed verdicts on
scoped-out ones, wrote them as pending proposals. Tenant sees a
Stage-2 queue full of items they've already decided don't apply.

On Arion (cloud-only, 14 A.7 physicals + A.7.2.7 27701 physical
+ A.8.21/22/26 tech-physical all applicability_status='na'):
**18 stale proposals** at time of audit.

## Delivered

### 1. Guard in `_persist_engine_proposals`

`rag/posture_loader.py` — added `applicability_status` to the
SELECT + skip-guard:

```python
cur.execute(
    """
    SELECT finding, engine_proposal_status, applicability_status
      FROM posture_controls
     WHERE tenant_id = %s AND standard_id = %s
       AND control_ref = %s AND is_active = TRUE
     LIMIT 1
    """,
    (tenant_id, standard_id_full, control_ref),
)
...
live_finding, cur_status, applicability_status = cur_row

# Ship 98'.c — Ship 66'.a SSoT enforcement
if applicability_status == 'na':
    continue
```

Engine may still COMPUTE a verdict for N/A controls (internal
math is unchanged); it just doesn't emit them as tenant-facing
Stage-2 proposals.

### 2. Data cleanup

**Stage-1 (Option C, per-source discipline):**

| Source | Pending | Action | Rationale |
|---|---|---|---|
| `structural_pattern` | 630 | approve | Ship 54'.e provenance-anchored |
| `workbook_llm_arbiter` | 608 | approve | Ship 91'.d HITL 95% precision |
| `xfw_bridge` | 215 | approve | Curator-authored Neo4j edges |
| `workbook` | 210 | approve | Ship 89'.a/b catalog-fixed auditor-grade |
| `fingerprint_match` | 95 | soft-delete | Variable-quality keyword match |
| `extracted` | 53 | soft-delete | Variable-quality LLM extraction |

**Stage-1**: 1,811 pending → **0** (1,663 approved + 148 soft-deleted).

**Stage-2**: superseded 18 stale N/A proposals with
`superseded_at=NOW()` — 14 A.7 physicals + A.7.2.7 27701 +
A.8.21/22/26 tech-physical. **28 → 10 pending** (all remaining
are genuine engine proposals on in-scope controls).

### 3. Regression guards

`tests/test_notification_producers.py` (40 → 42, all pass):

- `test_persist_engine_proposals_selects_applicability_status`
  — asserts the SELECT includes applicability_status
- `test_persist_engine_proposals_skips_na_applicability`
  — asserts the guard's continue branches on `== 'na'`

Verified both fail on the pre-fix state via `git stash` cycle.
Cheap durable insurance for a Ship-66'.a-cascade class of bug.

## Eval

233 PASS + 1 WARN + 0 FAIL — baseline preserved.

## Codified lessons

**Lesson 146: SSoT column promotions need a downstream-writer
audit, not just a reader audit.** Ship 66'.a migrated the READ
paths from `finding='N/A'` to `applicability_status='na'` and
codified [[feedback-na-dominance-via-applicability-column]].
Reader consumers were audited + fixed. The engine WRITE path
was missed — it wrote proposals against controls the tenant had
already scoped out. Rule: when a semantic column is promoted to
SSoT, grep for every SITE that used the old signal — not just
readers. Writers matter too.

**Lesson 147: Dev-queue-fill audits surface real bugs, not just
housekeeping.** The user opened this as "clean up dev residue."
The Stage-1 side was pure cleanup. The Stage-2 side surfaced a
Ship-66'.a-cascade-miss that had been silently writing bad data
for ~2 weeks on every tenant with any N/A controls. Rule: when
auditing state on a dev/demo tenant, look at each pending item
and ask "should this exist at all?" — not just "does this need
approval." Anomalies in the queue are diagnostic signals.

**Lesson 148: Per-source cleanup discipline beats bulk actions
on demo tenants.** Bulk-approve makes the dashboard look clean
but promotes low-precision items to posture. Bulk-delete
throws out real coverage. Per-source triage (approve trusted
lanes; soft-delete variable-quality lanes) matches the
underlying quality gradient. Rule: for demo/staging state
cleanup, tag actions by source-quality tier rather than by
bulk queue status.

## Related

- [[ship-66-prime-a]] — where applicability_status was promoted
  to SSoT; this arc closes a missed writer-side cascade
- [[feedback-na-dominance-via-applicability-column]] — the rule
  Ship 66'.a codified; this arc extends its coverage to writers
- Ship 89-91 — workbook dogfood arcs that filled Arion Stage-1
- Ship 54'.e — structural_pattern lane; its outputs approved
  wholesale
- Ship 91'.d — arbiter HITL 95% precision; its outputs approved
  wholesale
