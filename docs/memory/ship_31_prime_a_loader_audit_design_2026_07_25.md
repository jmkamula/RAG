---
name: ship-31-prime-a-loader-audit-design-2026-07-25
description: "Ship 31'.a — audit of every posture_controls SELECT in rag/ for the Ship 30 loader-blindness pattern (SELECT omits semantic field, downstream .get(field) silently reads None). Found one real bug: _fetch_not_assessed_obligation_rows at posture_loader.py:466 is a near-twin of the Ship 30 case, missing confirmation_status. Feeds the DEMONSTRATES overlay materialization path."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 31'.a — opens Ship 31 arc (loader SELECT audit). Direct
follow-on to Ship 30's discovery that `posture_loader.load_posture`
was silently making every assessed posture emit `[NC-DRAFT]` in
chat because the SELECT never fetched `confirmation_status`.

## The bug pattern

A "loader" function:
1. Runs `cur.execute("SELECT c1, c2, ... FROM some_table")`
2. Returns `dict[node_id, record]` to downstream code
3. Downstream code does `record.get("some_semantic_field")` and
   treats the result as significant (e.g. `not in _ALLOWED_STATES`)

If the SELECT never fetched `some_semantic_field` but the schema
HAS that column, `.get()` returns `None`, which typically defaults
to the "wrong" branch in the downstream check.

Silent, cross-tenant, load-bearing. Grows worse over time as
downstream code accumulates more `.get()` consumers of that field.

## Audit approach

Explore agent + manual verification. Scope was `rag/` — 15 SELECTs
against `posture_controls` inventoried; scored against these
criteria:

- Returns records as **dicts** (loader shape) vs tuples/scalars
  (targeted lookup) → only loader shape is at risk
- Records **fed downstream** to consumers doing `.get()`  → the
  bug requires this pathway
- Column list **matches or misses** semantically-checked fields
  from the schema

## Findings

### FINDING 1 — CONFIRMED BUG

**`rag/posture_loader.py::_fetch_not_assessed_obligation_rows` (line 450)**

SELECT columns (line 468-473):
```
node_id, control_ref, standard_id, finding, confidence,
gap_description, action_required, source, source_authority,
platform_ref, external_ref, soa_notes, remediation_status,
linked_policies, last_updated, engine_proposal_status
```

Missing: **`confirmation_status`** (schema has it — `\d
posture_controls` confirms `confirmation_status text`).

Downstream:
- `_apply_demonstrates_overlay` line 588: `posture[tgt_id] =
  tgt_rec` — the record is merged into the main posture dict.
- Same downstream consumers as the Ship 30 fix:
  - `rag/casefile/types.py:373` — `rec.get("confirmation_status")
    not in _CONFIRMED_STATES` → `None not in {...}` → True
  - `rag/resolver.py:685,689,690` — draft/confirmed counting

Impact: any obligation posture materialized via DEMONSTRATES
propagation (Phase 2c — Not-assessed → Comply/OFI via
PROGRAM/EXTENSION contributions) emits `[DRAFT]` in chat despite
propagation being deterministic engine output.

On Arion this affects GDPR articles that are satisfied by ISO
27001 postures (dozens of controls in the demonstrated_by /
propagated_finding pathway).

### FINDING 2 — SAFE

`rag/posture_loader.py::load_posture` line 84 — Ship 30 already
added `confirmation_status`. Verified.

### FINDING 3 — SAFE (targeted lookups)

- `posture_loader.py:648` — SELECT `finding, engine_proposal_status` —
  2-column tuple, not loader shape
- `posture_loader.py:767` — SELECT `id::text` — scalar, not loader
- `stage1_review_chat.py:406` — SELECT includes `confirmation_status`
  — safe
- `stage2_approval_chat.py:206,305,453` — targeted joins, not
  loader-shape returns
- `scheduler/tick.py:501` — sweep query, not consumed by DRAFT-checkers
- `templates/answer_footer.py:241`, `intake/posture_writer.py:751`,
  `scope_filter.py:91`, `facts/recompute.py:139` — targeted lookups

## Ship 31'.b fix plan

**One-line fix**: add `confirmation_status` to the SELECT at
`posture_loader.py:473`. Same shape as the Ship 30 fix.

**Belt-and-suspenders**: add a CI grep guard so future edits to
either loader remain aligned.

## Grep guard design

The bug pattern is detectable by grep: any SELECT from
`posture_controls` that returns records to a loader-shape dict
must include `confirmation_status`. Grep guard shape:

```bash
# scripts/dev/audit_loader_selects.sh
# Warn if any SELECT ... FROM posture_controls in rag/ misses
# confirmation_status in the column list.
grep -rn "FROM posture_controls" rag/ --include="*.py" |
  while read hit; do
    # walk backwards from the FROM line to the containing SELECT,
    # extract the column list, verify confirmation_status is present
    ...
  done
```

Simpler: use a Python one-shot in `tests/` that parses each
`rag/**/*.py` file, finds every psycopg2 `cur.execute()` call with
`FROM posture_controls`, and asserts the SQL literal includes
`confirmation_status` when the caller returns records as dicts.

## What Ship 31 does NOT do

- **Audit other tables** — this arc is focused on the
  `posture_controls`-shaped bug. `document_findings`, `client_facts`,
  etc. might have their own missing-field bugs but each table's
  audit is a separate exercise.
- **Audit Neo4j Cypher queries** — Cypher has different failure
  modes (missing property → `null` in Cypher, not equivalent to
  Python None-defaulting-to-wrong-branch).
- **Backfill posture data** — the DEMONSTRATES overlay
  materialization happens fresh on every `load_posture` call.
  Nothing to backfill; the next call after the fix has the
  correct behavior.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **31'.a** (this) | Audit + write-up | 1 bug found in `_fetch_not_assessed_obligation_rows` |
| 31'.b | Fix + grep guard | One-line SELECT fix + CI check preventing recurrence |
| 31'.c | Eval + retro | Baseline holds; loader-audit pattern codified |

## Related

- [[ship-30-prime-arc-retrospective-2026-07-25]] — the arc that
  surfaced the pattern
- [[ship-27-prime-arc-retrospective-2026-07-24]] —
  `grounding_method` audit; similar shape (schema-driven audit
  tool)
