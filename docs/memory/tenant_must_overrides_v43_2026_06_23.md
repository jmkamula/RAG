---
name: tenant-must-overrides-v43-2026-06-23
description: "SHIPPED 2026-06-23 (f7fdfc9, schema_v43): per-tenant MUST applicability overrides. Cloud-only tenants can mark physical-scope MUSTs (e.g. item:A.5.15:physical_rules) as N/A; engine filters them from leaf denominators; advisory hides them from missing-list. Audit trail via reason + set_by + set_at columns. Pre-populated Arion seed: A.5.15:physical_rules N/A. Effect: leaf 5/7 → 5/6; eval case #1 'physical' forbid stopped tripping."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Direction C's pass-2 closed the LLM recall ceiling but surfaced a
different ceiling: some MUSTs are *inapplicable by tenant scope*,
not missing from extraction. Counting them in the leaf denominator
permanently blocks satisfaction, and surfacing them in the advisory
("your policy doesn't yet include: Physical access rules") leaks
scope-irrelevant content into chat answers.

Concrete: Arion is cloud-only. A.5.15's `access_control_policy` leaf
has 7 MUSTs including `physical_rules` ("Physical access rules —
premises, server rooms, restricted areas"). The leaf can never reach
7/7 because Arion has no physical infrastructure to evidence.

Eval signal: case #1 ("what are our access rights gaps?") had
`must_not_contain=["physical"]` and started failing post-Direction-C
because A.5.15's per-MUST advisory now legitimately listed "Physical
access rules" as a missing item.

## Schema (schema_v43)

```sql
CREATE TABLE tenant_must_overrides (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   uuid NOT NULL,
    must_id     text NOT NULL,            -- e.g. item:A.5.15:physical_rules
    applies     boolean NOT NULL DEFAULT FALSE,
    reason      text,
    set_by      uuid,
    set_at      timestamp with time zone NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, must_id)
);
```

RLS-enabled. `arioncomply_app` grants. Pattern matches
`posture_controls` / `document_findings`.

## Engine wiring (rag/posture/leaf_evaluators.py)

```python
def _fetch_na_must_ids(self, must_item_ids: list[str]) -> set[str]:
    """Return the subset of supplied must_ids that this tenant has
    marked as N/A. Empty set when no overrides exist. Silent on
    missing table — degrades gracefully if schema_v43 hasn't been
    applied."""
```

Called immediately after Neo4j MUST fetch, before the recognised/
unrecognised math. The N/A subset is removed from `must_item_ids`
in-place, so:
- `items_unrecognised` no longer includes N/A MUSTs
- `n_total` shrinks (5/6 instead of 5/7 on Arion's A.5.15 policy leaf)
- `satisfied` becomes reachable when remaining MUSTs are met

Advisory inherits the filter via `LeafVerdict` — no separate
advisory-side filter needed.

## Architectural classification

Different from existing concepts in three subtle ways:

| Mechanism | What it represents |
|---|---|
| `document_findings.inference_source` | Where the evidence came from (extracted / workbook / form / leaf_scan) |
| `posture_controls.finding='N/A'` | Whole-control scope exclusion |
| `tenant_must_overrides.applies=FALSE` | **Per-MUST scope exclusion within an applicable control** |

The third case wasn't representable pre-v43. Workbook intake had a
`profile_fact` mechanism that's analogous but spec-level — this is
per-tenant runtime override of curated MUSTs.

## Arion pre-population

```sql
INSERT INTO tenant_must_overrides (tenant_id, must_id, applies, reason)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'item:A.5.15:physical_rules',
  FALSE,
  'Cloud-only operations: no premises, server rooms or restricted physical areas in ISMS scope. A.7.x family controls also N/A.'
);
```

Effect (verified via /api/v1/dashboard/control/A.5.15/advisory):
- access_control_policy leaf: 5/7 → **5/6** (1 MUST left: segregation_link)
- A.5.15 posture: OFI (the management_approval leaf is fully satisfied
  thanks to Direction C; access_control_policy leaf one MUST away)
- Eval case #1: ✓ PASS (was failing on "physical" forbid)

## What still needs follow-up

1. **Bulk N/A application**: Arion's physical-scope exclusion should
   apply to A.7.1-A.7.14 controls too (not just A.5.15:physical_rules).
   Today's seed covers only the eval-triggering MUST.
2. **Tenant UI to manage overrides**: currently admin-only via SQL.
   Should surface a "mark N/A with reason" action on each MUST in the
   advisory card.
3. **Curation-driven applies_when**: long-term, MUSTs should carry
   their own scope conditions (e.g. `applies_when: tenant.physical_scope`)
   in Neo4j. Per-tenant overrides remain for exceptions. The Phase-1
   `applies_when` DSL infrastructure exists for FulfilmentSpecs —
   would need extension to MUSTs.

## Eval result post-v43

| Case | Before v43 | After v43 |
|---|---|---|
| #1 "physical" forbid | ✗ FAIL | **✓ PASS** |
| #5 "physical" forbid | ✗ FAIL | ✗ FAIL (LLM-stochastic, A.5.18 has no physical MUSTs) |
| #16 A.5.18 missing | ✗ FAIL | ✗ FAIL (known LLM-stochastic) |

**197/199** with #5 + #16 LLM-stochastic, no architectural regressions.

## Related

- [[per-must-recall-direction-c-2026-06-23]] — same-day shipment;
  v43 addresses the new advisory-content leak that Direction C
  introduced
- [[feedback-eval-state-drift]] — the rule that frames why the eval
  needed an architectural fix vs an assertion update
- [[applies-when-phase1-regression-tests]] — sibling pattern at the
  FulfilmentSpec layer; future direction is to extend this to MUSTs
- [[engine-agreement-suppression]] — sibling concept of "engine
  agrees with live; don't surface" — same principle, different layer
