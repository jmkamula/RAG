---
name: ship-122-prime-arc-retrospective-2026-09-05
description: Ship 122' arc — consolidate audit-grant guards into CI script + verify Neo4j ClientFact write path has no drift risk
metadata:
  type: project
---

# Ship 122' — audit-grant guard consolidation + Neo4j write-path verification

**Date:** 2026-09-05
**Sub-arcs:** 122'.a extract guards → 122'.b verify Neo4j path → 122'.c eval + retro
**Trigger:** Ship 121' retro deferred items 2 + 4 (item 3 explicitly deferred for trigger-driven day). Same session as Ship 121'.

## Motivation

Ship 121' added two pre-commit guards for the audit-grant drift class. They lived inline in `scripts/git-hooks/pre-commit`, which meant the source-of-truth for "forbidden shapes" was split across two files (`pre-commit` had the audit-grant patterns; `scripts/ci/check_forbidden_patterns.sh` had the Ship 60/61/66 patterns). Consolidating into the CI script gives one place to add new patterns as they emerge — and lets the same script run under an actual CI runner if/when one gets set up.

Ship 121' also deferred a Neo4j audit for "does any writer to ClientFact bypass Postgres logging?" The concern was that tenant-mutable data in Neo4j could get modified in-place without provenance. Ship 122'.b closed that loop.

## Delivery summary

### 122'.a — extract Ship 121 guards into `scripts/ci/check_forbidden_patterns.sh`

Two new `report` calls added:

1. **Blanket `GRANT ... (DELETE|ALL) ... ON ALL TABLES ... TO arioncomply_app`** outside `deploy/baseline_grants.sql`. Also excludes `scripts/ci/**` so the script doesn't self-match its own docstring.
2. **schema_v* GRANT UPDATE/DELETE/ALL on `_log|_audit` tables**. Uses the `-- APPEND-ONLY-EXEMPT` escape hatch pattern from Ship 121'.d.

Running the extended CI script against the full tree surfaced 8 pre-existing lines matching pattern 2. Splits into two intent classes:

- **7 legitimate** (all pre-Ship-121 diagnostic-table grants — v65 sweep_log UPDATE, v79 x5 diagnostic DELETEs, v89 intake_consensus_log DELETE) — annotated inline with `-- APPEND-ONLY-EXEMPT: <reason>`.
- **1 superseded** (v63:103 GRANT UPDATE on `ai_call_log` — later revoked by v79). Annotated as `-- APPEND-ONLY-EXEMPT: superseded by schema_v79`.

Rather than mutating historical migration files aggressively, we chose the inline-marker approach: the historical line stands, but future readers see explicit "this is intentional / this was corrected later" context on the same line.

Pre-commit hook reduced from 66 lines of inline pattern-matching to a 12-line delegation:

```bash
if [[ -x "$REPO/scripts/ci/check_forbidden_patterns.sh" ]]; then
    if ! "$REPO/scripts/ci/check_forbidden_patterns.sh" > /tmp/forbidden-check.log 2>&1; then
        ... show hits + escape-hatch instructions
        exit 1
    fi
fi
```

Scope difference intentional: the CI script uses `git grep` (full tracked tree, ~1s). The pre-commit hook previously used `git diff --cached | while read` (staged-only, faster). We chose full-tree scope in the hook because it catches drift anywhere — not just what's being committed right now — and 1s is acceptable per-commit latency at this repo size. If the tree grows enough that this becomes painful, add a `--staged-only` mode to the CI script.

### 122'.b — audit ClientFact write path in Neo4j

**Result: no gap.** Grepping for every `MERGE (:ClientFact ...)` / `CREATE (:ClientFact ...)` / `SET ... ClientFact` writer in `rag/`, `api_server.py`, `scripts/`, `enrichment/` surfaced exactly **one file**: `enrichment/obligations/load_to_neo4j.py`. That's the offline curator loader, not a runtime writer.

The loader writes schema-only fields (`id`, `fact` name, `description`, `updated_at`). Never tenant values. From `enrichment/obligations/client_facts.py` docstring:

> Facts are:
> - Boolean (true/false about the client's situation)
> - Collected once at onboarding via questionnaire
> - Stored in Postgres per tenant
> - Loaded at session start into TenantProfile

The 22 ClientFact nodes in Neo4j are the 22 possible facts a tenant *can* declare (an ontology of scoping questions), not any tenant's actual values. Tenant-specific fact state lives only in Postgres:

- `client_facts` — current value per tenant per fact
- `client_facts_log` (Ship 118'.b) — user-driven changes (Profile PUT, quickstart, explicit derivation)
- `client_fact_change_log` (Ship 121') — cascade-event-driven changes

All three are classified as append-only compliance in the Ship 121' audit-grant regression. So the architecture already has the right separation — Ship 121' item 3 was scoping for a risk that doesn't exist in the current design.

### 122'.c — eval baseline

237/238 PASS + 1 known WARN + 0 FAIL — baseline held identically to Ship 120' and Ship 121'. No regressions from the CI-script extraction or the annotation edits to historical schema files.

## Lessons codified

### Lesson 231 — Consolidate before adding another guard

Ship 121' added two guards inline in the pre-commit hook because the immediate need was "make sure my Ship 120 fix doesn't regress." That was the right call for the moment. But the moment a third guard came along, the pattern would fragment — some in the hook, some in the CI script. Ship 122'.a caught the seam before that third guard existed. Rule of thumb: after adding N=2 checks of the same class to a fast-feedback surface, look for where they SHOULD live long-term and move them before adding N=3.

### Lesson 232 — Historical migration files deserve inline exemption markers, not edits

The 8 pre-existing schema_v* lines the extended CI script flagged were mostly intent-correct (diagnostic-table DELETEs) or intent-corrected-later (ai_call_log's superseded UPDATE grant). Editing historical migrations to remove the grants would be dishonest — the line WAS the truth at that point in history. The `-- APPEND-ONLY-EXEMPT: <reason>` inline marker preserves the historical line + tells future readers "yes, we saw this, here's why it's fine." Migration files are immutable historical records; annotations on them are additive commentary.

### Lesson 233 — Absence of a gap is a delivery outcome, not a non-arc

Ship 122'.b's finding was "no gap exists." That's still a valuable arc close — it documents WHY the concern is unfounded (Neo4j ClientFact is schema not data; tenant state lives in Postgres; the architecture already enforces the separation). Without the arc, the concern lives on as an ambient TODO forever. Better: verify, document, close. The retro entry ("verified: no gap, here's the evidence") is the deliverable.

### Lesson 234 — Docstrings that describe data ownership are load-bearing documentation

The 8-line docstring on `ClientFacts` explicitly says "Stored in Postgres per tenant." That single line answered the Ship 121 deferred question in 30 seconds — without it, verifying the write path would have required tracing every reader/writer through the codebase. Docstrings that state where data lives + who owns it are a compounding investment; the class was authored years ago and its docstring is still the fastest source of truth today.

## Related arcs

- [[ship-121-prime-arc-retrospective-2026-09-05]] — parent arc; Ship 122' closed 2 of its 3 deferred items
- [[ship-120-prime-arc-retrospective-2026-09-05]] — the original drift class this guard chain protects against
- [[ship-63-prime-arc]] — the CI script we extended (Ship 63' added the first 3 patterns)
- [[ship-118-prime-arc-retrospective-2026-09-05]] — added client_facts_log
- [[ship-54-prime-arc]] — added client_fact_change_log

## Deferred to future arcs

1. **Actual automated CI runner** — the extended `check_forbidden_patterns.sh` is ready to be invoked by GitHub Actions / GitLab CI / any hosted runner. Not yet configured because the project's dev model is "solo developer + operator, verify locally, deploy per-ship." An automated runner is an arc-sized decision (secret management, cost, merge-review flow change).
2. **Erasure workflow on existing `deletion_log` plumbing** — Ship 120 item 3 / Ship 121 deferred item 1. Infrastructure exists; workflow doesn't. Wait for real customer-offboarding trigger.
3. **--staged-only mode for `check_forbidden_patterns.sh`** — if tree growth makes the full-repo grep painful in pre-commit. Not needed yet at this repo size.

## PoC deployment plan

**No PoC deploy needed.** Ship 122' is entirely dev-side:
- `scripts/ci/check_forbidden_patterns.sh` — dev script, never runs on PoC
- `scripts/git-hooks/pre-commit` — dev-side git hook, never runs on PoC
- `db/schema_v63/v65/v79/v89` inline comment annotations — cosmetic; SQL parsers ignore comments

The PoC's Ship 120' + 121' state is fully current. Ship 122' just tightens the developer feedback loop that protects those wins.
