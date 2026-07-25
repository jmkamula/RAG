---
name: ship-31-prime-arc-retrospective-2026-07-25
description: "Ship 31' arc closer — loader SELECT audit. Extended the Ship 30 bug pattern from posture_controls to a cross-table sweep; found 2 more loader-blindness bugs (_fetch_not_assessed_obligation_rows on posture_controls, load_client_facts on 8 client_facts columns). Added tests/test_loader_select_columns.py as a static grep-shape regression guard. Codifies: schema evolves; loader whitelists don't. Every semantic column added to a table needs a paired loader edit or it's silently invisible downstream."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 31' arc retrospective — 3 sub-arcs delivered in one session
(2026-07-25). Started as a targeted audit motivated by Ship 30's
discovery ("posture_loader missed `confirmation_status`"); grew when
the user asked "audit the other tables too" and a second-round scan
found a bigger loader-blindness gap in `load_client_facts`.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 31'.a | Design memo + first audit (posture_controls only) | 7033d98 |
| 31'.b | Expanded audit + 2 loader fixes + regression guard test | 8d5fed4 |
| **31'.c** | **Eval + retrospective (this doc)** | pending |

## What was fixed

**Bug #1 — `posture_loader._fetch_not_assessed_obligation_rows`
(line 466-479)** — same shape as the Ship 30 case. Missing
`confirmation_status` in the SELECT column list. Downstream:
`_apply_demonstrates_overlay` line 588 merges the record into the
main posture dict; `casefile.needs_draft_tag()` reads
`.get("confirmation_status")` and treats None as "not confirmed" →
DEMONSTRATES-materialized obligations wrongly emit `[DRAFT]` in
chat despite being deterministic engine output.

One-line fix: added `confirmation_status` to the SELECT.

**Bug #2 — `posture_loader.load_client_facts` (line 882-903)** — the
loader's SELECT column list drifted from schema. Every field the
loader whitelist was missing:

| Missing column | Downstream trigger |
|---|---|
| `uk_data_subjects` | UK GDPR territorial scope |
| `role_joint_controller` | Art.26 |
| `criminal_conviction_data` | Art.10 |
| `automated_decision_making` | Art.22 |
| `profiling` | Art.22 |
| `systematic_monitoring` | Art.37 DPO trigger |
| `employee_count_250_plus` | Art.30 records mandatory |
| `public_authority` | Art.37 DPO mandatory |

Each is referenced in `rag/posture/applies_when.py` or
`rag/cascade/engine.py` as a scope decision. Silent `False`
bypassed obligation activation for any tenant with those fact
values.

**Arion impact right now**: `uk_data_subjects=True` in DB → loader
returned False → UK-scoped obligations wrongly skipped. Verified
post-fix: loader now returns True. Other 7 missing fields were
False on Arion but the same bug would trip for any tenant with
different fact values.

Also added the 8 fields to the `defaults` dict so the DB → dataclass
merge picks them up.

**Regression guard — `tests/test_loader_select_columns.py`**

Static grep-shape test. For each entry in `_ASSERTIONS`, verifies
the named loader function's body contains the required
semantically-load-bearing column identifiers. Fails fast if a
future edit drops a whitelist entry. Doesn't hit the DB;
standalone-runnable.

Extension pattern: when new semantic columns are added to
`posture_controls` or `client_facts`, extend `_ASSERTIONS` to
lock the loader alignment.

## Tables the audit spot-checked clean

- `client_documents` — `load_uploaded_documents` includes
  `document_status`
- `posture_assertions` — targeted lookups, not loader-shape
  (`get_all_active_by_control` has no external callers today)
- `document_findings` — targeted lookups + tuple unpacking, not
  dict-loader shape
- `document_uploads` — writes only; targeted lookups on read

## Codified 3 lessons

### 1. Loader whitelist ≠ schema truth

The bug pattern is: schema evolves, `ALTER TABLE ADD COLUMN`
lands, downstream code starts reading the new column, but the
loader SELECT — which is a static column-list — never got
updated. Every record silently gets `None` (or the dataclass
default), which typically defaults to the "wrong" branch in
downstream Boolean/enum checks.

**Rule**: when adding a semantic column (something a downstream
check will read), the same PR must extend any loader
`SELECT ... FROM` for that table. If you can't do it in the same
PR, add the column identifier to
`tests/test_loader_select_columns.py::_ASSERTIONS` so the drift
is CI-visible.

### 2. Whitelist SELECTs are load-bearing, `SELECT *` is defensive

`rag/posture/engine_runner.py:150` does `SELECT * FROM client_facts
WHERE ...`. That's defensive — never drops a column. `SELECT column-
list` is more explicit + slightly cheaper but forces manual
alignment discipline. Choose the shape per site: `SELECT *` for
short-lived reader queries where the record is briefly used;
whitelist for loaders that build long-lived cached objects (where
you want the column contract explicit in code).

The client_facts loader is a whitelist because it maps to a
dataclass with a fixed field set — that's correct. But the
whitelist grew stale. Ship 31 fixed the alignment + added the
guard.

### 3. User pushback expands audit scope productively

The 31'.a audit as originally scoped covered only `posture_controls`.
User asked "audit the other tables too" — and the second-round
scan found a bigger bug (client_facts, 8 missing fields including
a live regression on Arion via `uk_data_subjects`).

**Rule**: when a user asks to broaden a targeted audit, take it
literally. Structural bugs like whitelist-vs-schema drift tend to
recur across every whitelist SELECT in the codebase; narrow scope
misses the ones that matter.

## Diagnosis notes

- The Explore agent's first pass reported "NO BUGS" on the broader
  tables. Spot-checking `load_client_facts` directly against the
  schema surfaced 8 missing columns the agent's regex-based
  approach missed. **Rule**: for shape-drift audits, cross-check
  against the schema itself, not just the caller-side `.get()`
  greps. Downstream code that reads a MISSING field defaults
  silently — you can't grep for what's absent.
- Both bugs are the same shape as Ship 30's: static column-list
  SELECT drifted from schema evolution. Confirms the pattern
  isn't a one-off.

## What Ship 31 did NOT do

- **Retrofit `SELECT *` everywhere** — that would be defensive
  but drops the explicit column contract at loader sites. Chose
  whitelist + guard instead.
- **Audit Neo4j Cypher queries** — different failure mode (missing
  property → Cypher `null`, not equivalent to Python `None`-
  defaulting-to-wrong-branch). Cypher whitelist queries have their
  own drift risk but out of scope for this arc.
- **Audit every table** — audit covered the load-bearing chat/
  posture pipeline tables. Ancillary tables (notification, cascade,
  external API, audit log) not covered.
- **Auto-populate `_ASSERTIONS`** from schema introspection — the
  test would be more resilient but tighter coupling to CI +
  Postgres. Kept the static list for simplicity.

## Deferred / follow-on candidates from Ship 31

- **Audit Neo4j Cypher SELECT-shape queries** — same drift risk
  in a different substrate
- **Audit ancillary tables** — `tenant_notification`,
  `cascade_events`, `chat_casefile_log`, `ai_call_log`, external
  API endpoint readers — each is a small audit
- **Extend `_ASSERTIONS` to more loaders** — currently 3 entries;
  loaders in `resolver.py`, `stage1_review_chat.py`, etc. could
  be added if a future arc finds a drift there
- **Schema-driven auto-audit** — a script that walks
  `information_schema.columns` for a table, greps for `.get("col")`
  in `rag/`, and reports "column X exists in schema, is referenced
  in rag/, but not in load_X's SELECT" — more powerful than the
  static guard, higher setup cost

## Sub-arc sequence

| Sub-arc | Focus | Outcome |
|---|---|---|
| 31'.a | Design + first audit | 1 bug found in `_fetch_not_assessed_obligation_rows` |
| 31'.b | Expanded audit + 2 fixes + guard | client_facts bug (8 missing fields) uncovered; regression test locks alignment |
| **31'.c** | **Eval + retro (this)** | **Baseline holds; loader-audit pattern codified** |

## Related

- [[ship-30-prime-arc-retrospective-2026-07-25]] — the arc that
  surfaced the bug pattern
- [[ship-31-prime-a-loader-audit-design-2026-07-25]] — the 31'.a
  audit design memo (before the client_facts scope expansion)
