---
name: ship-66-prime-arc-2026-08-12
description: "Ship 66' arc — N/A dominance via schema split. Splits scoping (applicability_status) from evidence assessment (finding). Multi-ship arc: 66'.a schema + data + loader wire, 66'.b engine/SSoT/bridge honor applicability, 66'.c downstream readers, 66'.d Stage-2 write-side + retire finding='N/A', 66'.e codified rule + CI guard."
metadata:
  type: project
  ship: "66'"
---

# Ship 66' — N/A dominance via schema split

## The problem (dogfood-surfaced)

Ship 65's Art.32 dogfood walk surfaced a CRITICAL-severity
regression: 17 controls on Arion were tenant-declared N/A but
being surfaced as NC downstream — LLM prose recommending
remediation on physical controls (A.7.7–A.7.13) for a cloud-only
tenant. Root-cause: `_apply_engine_overlay` at
`rag/posture_loader.py:334` clobbers `finding='N/A'` when
`engine_proposal_status='approved'` (past Phase B mass-approval
sticky).

Codified rule [[feedback-engine-should-not-clobber-tenant-na]]
existed but was documented, not enforced. Every consumer had to
remember N/A was special.

## The categorical error

`posture_controls.finding` mixed two semantically different
signals in one column:
- **NC / OFI / Comply / Not assessed** — evidence assessment
- **N/A** — scoping decision (control doesn't apply)

Scoping precedes evidence. If a control is out of scope, there
is no "how well is my evidence?" question to ask. The engine's
*"I don't see any evidence, so NC"* is irrelevant on an N/A row.

By keeping both in one column, the schema let any consumer treat
N/A as just another finding value that could be overridden,
filtered, mass-approved, etc. The guard had to be re-invented at
every consumer site — and any missed site is a bug like the one
Ship 65 surfaced.

## The structural fix (arc plan)

Split into two columns; make N/A dominant by construction, not
convention. Sub-arc plan:

| Sub-arc | Deliverable |
|---|---|
| 66'.a | Schema `applicability_status ∈ {applicable, na}` (default `applicable`) added to `posture_controls`. Migration: rows where `finding='N/A'` → `applicability_status='na'`. `load_posture` SELECT includes the new column so downstream can read it. `finding='N/A'` remains a legal value for backward compat until 66'.d. **Zero behavior change** — data + shape only. |
| 66'.b | Engine overlay + SSoT writer + bridge writer honor applicability. `_apply_engine_overlay` early-continues on `applicability='na'`. `_persist_must_verdicts` skips N/A. `_persist_bridge_coverage` filters. Visible bug resolves here — Arion's 17 clobbered controls stop surfacing as NC. |
| 66'.c | Downstream readers: digest excludes N/A from POSTURE / XFW BRIDGES / OBLIGATIONS. Advisory + Evidence Package + Dashboard treat N/A as scope info, not finding. |
| 66'.d | Stage-2 write-side: approve endpoint refuses engine proposal when `applicability='na'`. Migration: retire `finding='N/A'` as legal value (use `finding='Not assessed'` + `applicability='na'`). |
| 66'.e | Retro + codified rule (supersedes [[feedback-engine-should-not-clobber-tenant-na]]) + CI grep guard against new consumers treating N/A as a finding value. |

## 66'.a delivered this commit

- `db/schema_v97_applicability_status.sql` — new column with
  CHECK constraint + partial index on `(tenant_id,
  applicability_status)` where status='na' (Ship 66'.b's
  overlay guard will filter on this).
- `rag/posture_loader.py::load_posture` SELECT includes
  `applicability_status`. Consumers now see it in returned rows.

Migration on Arion demo:
- 18 rows populated (17 ISO 27001 + 1 ISO 27701).
- Cross-check: `applicability='na'` matches `finding='N/A'`
  exactly (no data loss / drift).
- `load_posture()`: 208 applicable, 18 na — matches DB row
  counts.

Chat smoke: HTTP 200. `A.7.7` still shows `finding='NC'`
downstream (overlay still clobbers) — expected for 66'.a
(behavior unchanged until 66'.b's guard lands).

## What Ship 66'.a costs

- Schema migrations: 1 (schema_v97)
- Wall clock: ~30 min (design + migration + loader wire + smoke)
- Files touched: 2 (schema + posture_loader.py SELECT)
- Lines: ~50 (mostly schema documentation)
- Eval regression: n/a — data + shape only
- Downstream impact: none until 66'.b
