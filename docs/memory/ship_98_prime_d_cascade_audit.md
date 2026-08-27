---
name: ship-98-prime-d-cascade-audit
description: Ship 98'.d — applied Lesson 146 systematically. Grepped every site checking `finding == 'N/A'`; migrated 6 sites (get_tenant_na_scope + 5 telemetry reads) to Ship 66'.a SSoT column `applicability_status`. CI allowlist reduced from 6 files to 3. Mid-arc regression on case #5 rooted to Ship 98'.c data cleanup (not 98'.d), reworded per state-drift rule.
metadata:
  type: project
---

# Ship 98'.d — Ship 66'.a cascade audit (2026-08-27)

## Framing

Ship 98'.c surfaced ONE writer-side miss
(`_persist_engine_proposals`) — the fix in Lesson 146: "SSoT
column promotions need a downstream-writer audit, not just a
reader audit." Ship 98'.d applies that systematically: grep
every site that reads or writes `finding == 'N/A'` and verify
each has migrated to `applicability_status`.

## Deliverable

### Sites migrated

**6 sites total** — all on Arion the data was in sync (18 rows
had both `finding='N/A'` AND `applicability_status='na'`), so
these are no-op today but future-proof:

| Site | Purpose | Kind |
|---|---|---|
| `rag/scope_filter.py::get_tenant_na_scope` | LLM system-prompt N/A list | SQL reader |
| `rag/resolver.py:718` | Resolver trace metric `posture_na` | Python-side telemetry |
| `rag/arion_graph.py:2238` | LLM prose "A.7.x N/A on your tenant" | Python-side prose |
| `rag/arion_graph.py:2258` | LLM prose "A.8.2x N/A" | Python-side prose |
| `rag/posture_loader.py:198` | Log line N/A count | Python-side log |
| `rag/posture_loader.py:215` | OTel span attribute | Python-side telemetry |

The `posture[ref]` dicts already carry `applicability_status`
(SELECT at line 116) — all 5 Python-side reads had the SSoT
column right there, just weren't using it.

### CI grep guard cleanup

`scripts/ci/check_forbidden_patterns.sh` — allowlist shrunk
from 6 files to 3 (`tests/`, `scripts/`, `snapshots/` +
`db/workbook_importer.py` + `rag/llm_answer.py` — all legitimate
exceptions: legacy workbook importer prose + LLM system-prompt
descriptive text).

### Case #5 collateral (Ship 98'.c data-drift, not 98'.d code)

The Ship 98'.c intake queue cleanup approved 1,663 findings on
Arion. That moved A.5.18 from NC to OFI (evidence coverage
expanded). Case #5's query — "what should we do to close the
access rights **NC**?" — no longer matched Arion's reality.
Classifier now prefers A.8.2 (still NC + also access-topical)
over A.5.18 as primary.

Verified via `git stash` cycle: Ship 98'.d code is innocent.
The bug is Ship 98'.c-caused eval state drift.

Reworded case #5 per [[feedback-eval-state-drift]]:

- Query: `"what should we do to improve our access rights posture?"`
  (no state qualifier)
- Dropped `"register"` from `must_contain` — too specific to a
  particular leaf-set surfacing at any given time
- Kept `access` + no-`physical` guards
- Tag `state_drift_survivor` marks the fix intent

Verified 3/3 dogfood runs: primary=A.5.18, `access` present, no
`physical` leak, expected_type=implementation.

## Eval

233 PASS + 1 WARN + 0 FAIL — baseline restored.

## What NOT flagged (kept in scope discipline)

- `db/workbook_importer.py:296` — sets `remediation_status='closed' if finding=='N/A'` at import time. The writer downstream mirrors to `applicability_status` correctly. Kept on allowlist.
- `rag/llm_answer.py:413` — LLM system-prompt text describing N/A semantics for the model. Not a code check. Kept on allowlist.
- Schema/view files (`schema.sql:635`, `baseline/schema_baseline.sql:3652`) — DB views for reporting; not runtime code paths.
- `data_fix_2026_06_23b_physical_na_and_isms_restore.sql:39` — historical data-fix. Ship 66'.a's schema_v97 migration backfilled `applicability_status` from `finding`; the data is consistent.

## Codified lessons

**Lesson 149: Cheap sites should migrate even when data is in
sync.** Every site I migrated in Ship 98'.d was a no-op today
(Arion data mirror). None had a live bug. But each is future
insurance — the moment a writer emits `applicability_status='na'`
without mirroring to `finding` (which the SSoT column allows),
these readers would silently return the old set. Rule: when a
column is promoted to SSoT, migrate cheap reader sites even if
they're not causing bugs. The migration cost is one-liner; the
regression prevention is durable.

**Lesson 150: `git stash` bisect proves innocence quickly.**
Case #5 failed on Ship 98'.d eval and my first instinct was to
suspect my code. `git stash push` on all Ship 98'.d files +
re-running the query on OLD code showed A.8.2 primary still
happened — proving the drift was pre-98'.d. Rule: when a
regression appears alongside a commit, `git stash` the commit's
changes and re-test. Two minutes of stash-bisect saves hours of
misplaced debugging.

**Lesson 151: State-drift eval fixes belong with the arc that
caused the drift, not the one that surfaced it.** Case #5 was
broken by Ship 98'.c's data cleanup but surfaced by Ship 98'.d's
eval run. The rewording lives in Ship 98'.d's commit for
proximity but the ROOT CAUSE + attribution is Ship 98'.c. The
notes field carries the cross-reference so future readers see
the causal chain.

## Related

- [[ship-98-prime-c-engine-na-guard]] — the arc that codified
  Lesson 146; this arc applies it systematically
- [[ship-66-prime-a]] — where `applicability_status` was
  promoted to SSoT
- [[feedback-na-dominance-via-applicability-column]] — the rule
  Ship 66'.a codified; this arc reduces the deferred-site count
  from 6 to 3
- [[feedback-eval-state-drift]] — the discipline applied to
  case #5 rewording
- [[feedback-verify-stability-claims]] — followed the discipline:
  case #5 had 8-of-8 PASS before Ship 98'.c cleanup; a fresh
  FAIL is a genuine regression, not a stochastic blip
