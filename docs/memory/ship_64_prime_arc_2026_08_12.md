---
name: ship-64-prime-arc-2026-08-12
description: "Ship 64' — codebase-wide dead code audit + surgical deletions + one live bug caught. AST-driven sweep of 2438 defs surfaced 30 candidates; 7 deleted (chains included), one missed exception-handler registration wired."
metadata:
  type: project
  ship: "64'"
---

# Ship 64' — Dead code audit + surgical deletions

## The arc in one sentence

Ship 64' ran an AST-driven codebase-wide dead-code audit, verified
each candidate manually, deleted 7 truly-dead functions/classes
(including one call-chain), and fixed one real bug the audit
surfaced: a defined-but-never-registered FastAPI exception handler
on the external API surface.

## Audit method

`/tmp/dead_code_audit.py` — a self-contained Python-AST walk that:
1. Collects every top-level `def` and `class` across the tree
   (excludes `__pycache__`, `*.old.py`, `*.last.py`, `docs/`,
   `results/`).
2. For each unique name, runs `git grep -w -c` across `*.py` files
   and categorizes usage:
   - **A**: public defs (no leading `_`) with 0 external + 0
     same-file references. Leading deletion candidates.
   - **B**: module-private defs (`_`-prefixed) with 0 references
     anywhere. Definitely dead.
3. Filters out entrypoint-shaped names (`main`, `__init__`,
   dunders), framework-decorator-kept-live defs (`@app.get`,
   `@app.exception_handler`, `@validator`, etc.), and
   `__init__.py` re-exports.

Results: **26 public + 4 private candidates** across 2438 defs
scanned. Each was verified manually before deletion — several
"dead" candidates turned out to be public API surface (`read_
bridge_contributions`) or framework-registered handlers I hadn't
decorated correctly.

## Deletions

**Ship 60'.h call-chain**:
- `build_per_must_advisory` (advisory.py) — legacy chat markdown
  wrapper. Zero callers. Ship 60'.h had plumbed a bridge nudge into
  this dead function (spending 30 min of a prior arc on a no-op).
- `_render_advisory_markdown` — only called by the above.
- `_bridge_nudge_line` — the Ship 60'.h plumb itself. Only called
  by `_render_advisory_markdown`.
- `_HUMAN_STD` — dict constant only used by `_bridge_nudge_line`.

**Other confirmed-dead**:
- `get_conn` (api_server.py:322) — Postgres pool helper, never
  actually referenced as a `Depends()`. The `Depends`-based API
  paths use pool access differently.
- `build_template_footer` (answer_footer.py) — legacy
  `↳ Templates available:` chat footer. Superseded by
  `build_templates_block` (the structured card). Its private
  helpers `_fetch_primary_templates` + `_title_from_source_file` +
  `_RELEVANT_QUESTION_TYPES` remain because `build_templates_block`
  still uses them.
- `_format_ref` (llm_answer.py:705) — private ref-formatter, zero
  callers. Its dependency `_standard_label` remains live via other
  callers.
- `_truncate` (telemetry.py:82) — private truncation helper, zero
  callers.
- `_FakeConn` (tests/test_notification_producers.py:55) — test
  fixture class, zero callers.

## Bug caught + fixed

`external_unhandled_exception_handler` (rag/external/errors.py:120)
was defined but never registered on the FastAPI app. The
audit tagged it as "zero external refs"; investigation showed
api_server.py:8407-8409 registered the sibling `http` and
`validation` handlers but omitted `unhandled` from the import +
`app.add_exception_handler()` calls.

Consequence: top-level exceptions on external API paths (any
non-HTTP / non-validation error — e.g. a DB timeout, an
uncaught `KeyError`) returned FastAPI's default HTML 500 page
instead of the module's structured `error_type=internal` JSON
body that external SDKs are supposed to parse.

Fix: extend the import + add the `app.add_exception_handler(
Exception, _external_unhandled_exception_handler)` registration.
See Ship 64' comment in api_server.py.

## Candidates NOT deleted (require domain review)

The audit surfaced 18 additional candidates I left alone —
they're either public API surface with deferred consumers, private
helpers whose deletion would cascade through verification-shaped
code, or enrichment-scripting entrypoints:

- `read_bridge_contributions` (must_verdicts.py) — Ship 59'.c
  public API for future SDK / auditor UI. Deferred consumer, not
  dead.
- `_verify_posture_status_claims` (llm_answer.py:598) — deleting
  would cascade to 4 verification helpers (`_classify_section_
  header`, `_renumber_numbered_lists`, `_VERIFIER_REF_RE`,
  `_VERIFIER_STATUS_RE`). Verification-shaped code warrants a
  separate review — might be re-enabled by a future arc.
- Various `get_by_id` / `list_types` / `get_dimension` etc. on
  taxonomy + classification nodes — public API surface for
  enrichment scripting, deferred consumers.
- `cache_clear` on `leaf_structure.py` — Ship 60'.a wrote it for
  tests (Ship 63's suite uses `_open_pg()` not this). Keep as
  test-helper API even though tests don't call it right now.
- FastAPI exception handlers on `rag/external/errors.py` — the
  audit missed the framework-registration path; that's why one
  slipped through (see bug caught + fixed above).

Full list preserved in the audit tool output; ready for a
follow-up arc to sweep the remaining.

## Verification

- API server restarts cleanly (Uvicorn Ready + tenant context
  loaded).
- Chat smoke: `is Art.32 compliant?` → HTTP 200 in 30s.
- Ship 63 snapshot tests: 5 of 5 PASS.
- Ship 63 grep guards: OK — no forbidden patterns.
- Comment breadcrumbs in the deleted-name sites (kept as short
  "Ship 64' — Deleted X" markers so a future reader searching for
  the old name finds context, not a mysterious absence).

## Codified lessons

### 25. Dead code lives until you look for it

Ship 60'.h plumbed a bridge nudge into `build_per_must_advisory` —
a function with ZERO callers. The plumb worked (unit-tested during
Ship 60'.h). It just never reached a user. Nobody noticed for 4
arcs. AST-based codebase-wide audits are cheap and catch this
class of drift; grepping `def X(` in 2438 files takes minutes.

Rule: after every 3-5 substantial arcs, run a dead-code audit.
The compounding cost is small; the compound rot is real.

### 26. Zero-reference is the audit signal — verification is the arc

The audit flagged 30 candidates. Manual verification:
- 7 truly dead → deleted.
- 1 was a real bug (registration gap) → fixed.
- 22 were public API surface, framework-registered handlers, or
  deferred-consumer code → kept.

The audit output is a *hypothesis*, not a decision. A blind
"delete everything flagged" would have removed `read_bridge_
contributions` (a Ship 59'.c public API) and broken
`external_unhandled_exception_handler` even further (deletion vs
registration are opposite fixes for the same signal).

Rule: dead-code audit output is a starting point for
investigation, not a punchlist. Every deletion needs a manual
"this really has no purpose" verification. Framework-registered
handlers, public SDK surface, and cascade helpers all look "dead"
to a plain grep.

## Follow-ons deferred

- Sweep the remaining 22 audit candidates one at a time in a
  future arc (`_verify_posture_status_claims` + its 4-helper
  cascade is the biggest single opportunity if we decide the
  verification-shaped code is truly retired).
- Extend the audit tool to detect framework decorators the current
  regex misses (`@app.exception_handler`, custom decorators the
  codebase authors) — false-positive rate would drop further.
- Ship 60'.g still points at `_bridge_nudge_line` in the SPA
  render comment; kept as documentation of the shared idiom
  (`renderBridgeChip` is the surviving reference implementation).

## What Ship 64' costs to reproduce

- Schema migrations: 0
- Wall clock: ~90 min (audit tool + verification + surgical
  deletes + smoke test + retro)
- Files touched: 8 (advisory.py, api_server.py, answer_footer.py,
  llm_answer.py, telemetry.py, test_notification_producers.py,
  answer_augment.py comment cleanup, retro doc)
- Lines removed: ~180 (deletions + stale-comment cleanup)
- Lines added: ~20 (Ship 64' breadcrumb comments + exception
  handler registration + retro)
- Eval regression: baseline preserved (Ship 63 tests + guards all
  green post-delete).
