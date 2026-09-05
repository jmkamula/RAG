---
name: ship-121-prime-arc-retrospective-2026-09-05
description: Ship 121' arc — audit-table classification completion + pre-commit drift guards
metadata:
  type: project
---

# Ship 121' — audit-table classification completion + drift guards

**Date:** 2026-09-05
**Sub-arcs:** 121'.a classify → 121'.b extend → 121'.c blanket-grant guard → 121'.d schema-v over-grant guard → 121'.e deploy → 121'.f this doc
**Trigger:** Ship 120' retro deferred items 1 + 2 + 4 as "small effort, close soon." Same session as Ship 120'.

## Motivation

Ship 120' fixed the DELETE-drift on 9 audit tables but its regression test soft-warned on 8 more `_log` tables that hadn't been classified yet. That soft-warn is a smell — it means we know there's a problem but we're not yet asserting the fix. Closing it while the context is fresh is cheaper than re-diagnosing in six weeks. The two pre-commit guards prevent Ship 120's fix from regressing: item 2 catches a new blanket `GRANT ... ON ALL TABLES`, item 4 catches a new migration that grants too much on a new audit-shape table.

## Delivery summary

### 121'.a — classify the 8 unclassified `_log` tables

`\d public.<table>` + `\d+ ... COMMENT` + grep of writers/readers in `rag/` gave enough to decide each. Results:

**Append-only compliance (revoke UPDATE + DELETE):**
- `audit_log` — system-wide who/what/table/record/old_values/new_values/ip/user-agent. Partitioned by `created_at`. This is *the* general-purpose audit trail; if the app role can rewrite or delete rows, all the other REVOKEs are theatre.
- `confirmation_log` — tenant posture-change confirmations (previous_status/new_status/previous_finding/new_finding/performed_by/ip/source). Auditor evidence for "who confirmed this change."
- `deletion_log` — deletion provenance (deletion_type/reason/requested_by/executed_by/record_snapshot/purge_scheduled/purge_verified_at). Written by `rag/deletion_service.py` — plumbing exists, 0 rows on dev because no workflow calls it yet. Ship 120' item 3 (erasure-with-provenance flow) partially exists as infrastructure but has no UI/workflow.
- `cascade_suppression_log` — per `COMMENT`: "Append-only log of EMITS_EVENT edges whose applies_when evaluated false. Captures the path that was considered and consciously skipped, for auditor explanation."
- `client_fact_change_log` — per `COMMENT`: "Append-only audit of ClientFact mutations from cascade UPDATES_FACT edges." Written by `rag/cascade/engine.py`. Not redundant with `client_facts_log` from Ship 118'.b — that one captures user-driven changes (PUT /facts + quickstart + explicit derivation); this one captures cascade-event-driven changes. Complementary.
- `external_evidence_verification_log` — per `COMMENT`: "Append-only audit history of cite verifications... changes_detected REQUIRED — forces real review."

**Diagnostic (revoke UPDATE only, keep DELETE for retention):**
- `intake_consensus_log` — per `COMMENT`: "Diagnostic log for Ship 33 extraction consensus module. Retention-eligible; arioncomply_app has INSERT/SELECT/DELETE." The comment already documented the intended shape; Ship 120' just hadn't enforced it.
- `request_trace_log` — per-chat-request routing metadata (classifier_type/taxonomy_type/handler_name/strategy/node_ids_built/nodes_primary). Chat pipeline observability. Written by `rag/arion_graph.py` + `api_server.py`.

### 121'.b — extend baseline_grants.sql + regression test

`deploy/baseline_grants.sql` post-blanket `DO $$` block extended:
- Append-only compliance array grew from 3 to 9 tables.
- Diagnostic array grew from 5 to 7 tables.
- Comment table listing all 17 tables + their intended shape + source-of-truth schema_v* file (or Ship 121' for the new ones).

`tests/test_audit_table_grants.py` `APPEND_ONLY_AUDIT_TABLES` + `DIAGNOSTIC_LOG_TABLES` extended with the same 8 tables. Also updated the soft-warn's `known_non_audit` handling to filter out `audit_log_YYYY_MM` partitions from the "unclassified" set — those inherit grants from the parent, so surfacing them per-partition would just add noise.

Verified locally: applied updated `baseline_grants.sql`, ran test — 4/4 pass, all 17 tables show intended shape.

### 121'.c — pre-commit blanket-grant guard

Added to `scripts/git-hooks/pre-commit`. Scans the staged diff of `*.sql / deploy/ / scripts/` for the exact dangerous shape:

```
GRANT ... (DELETE|ALL PRIVILEGES|ALL) ... ON ALL TABLES ... TO arioncomply_app
```

Whitelists `deploy/baseline_grants.sql` by name (the one legitimate site). Fails the commit with a message explaining what silently regresses and how to add the shape correctly (enumerate per-table + register in the regression test).

### 121'.d — pre-commit schema_v* over-grant guard

Mirror of 121'.c for schema_v files: scans staged `db/schema_v*.sql` for:

```
GRANT ... (UPDATE|DELETE|ALL) ... ON <table ending in _log or _audit> ... TO arioncomply_app
```

Escape hatch: `-- APPEND-ONLY-EXEMPT` comment on the same line silences it (for the rare case a `_log`-suffixed table is legitimately mutable).

Smoke-tested both patterns with 4 hand-crafted inputs — all 4 assertions matched (offender caught, benign line not flagged, offender caught, exempt marker suppresses).

## Lessons codified

### Lesson 226 — Soft-warn assertions expire; close them while context is fresh

Ship 120's soft-warn on 8 unclassified tables was correct discipline (don't hard-fail unrelated work) but that discipline has a shelf life. Every week that passes, the context for "what does `confirmation_log` even do" fades and the fix costs more. Ship 121' closed the soft-warn same-day the parent arc did. Rule of thumb: if a soft-warn surfaces on the first CI run after a fix, treat it as a follow-on TODO with a max age of one session — not a permanent "someday" note.

### Lesson 227 — Comments already declare the classification; use them

Of the 8 tables, 5 had `COMMENT ON TABLE` clauses that literally said "Append-only audit..." or "Diagnostic log... arioncomply_app has INSERT/SELECT/DELETE." The classification was documented in the schema for years — Ship 120' just hadn't enforced it. The 3 uncommented ones (`audit_log`, `confirmation_log`, `deletion_log`) got classified from field inspection + writer greps in a few minutes. Corollary: when adding a new `_log` / `_audit` table, always write `COMMENT ON TABLE` declaring its class + grant shape. The comment is future-you's documentation and the classifier's input, all in one line.

### Lesson 228 — Two guards, one drift class

The blanket-grant guard (121'.c) catches the mechanism Ship 120' fixed. The schema_v over-grant guard (121'.d) catches the mirror mechanism — a new migration that grants too much on the table it creates. Both are the same class of drift ("wrong grants at commit time") but the origin sites are different (`baseline_grants.sql` vs `schema_v*.sql`), so they need different regex signatures. The lesson isn't "add one guard per file type" — it's "when you close a drift with a fix at one site, imagine every OTHER site that could re-open the same drift and add a guard there too." The mental exercise takes a minute; the guards are cheap; the alternative is Ship 120 having to happen again in some form.

### Lesson 229 — Escape hatches keep discipline collaborative

The 121'.d guard has an `-- APPEND-ONLY-EXEMPT` escape marker. Without it, the guard would hard-block legitimate cases (a `_log`-suffixed table that's genuinely mutable) and either (a) get commented out under pressure, or (b) drive people to `--no-verify` every commit that involves audit files. Explicit escape hatches with a self-documenting name mean "yes, this looks like the drift class but here's why it isn't" — future readers can grep for the marker and audit the exemptions. Discipline that people can work with survives; discipline that fights the workflow gets bypassed.

### Lesson 230 — Deletion provenance infrastructure existed; workflow didn't

`deletion_log` + `rag/deletion_service.py` were already built (schema_v6 and earlier). Zero rows on dev because no code path calls it. This partly-answers Ship 120' item 3 ("superuser erasure-with-provenance flow") — the plumbing is there, the workflow isn't. Adding a superuser-scoped erasure endpoint + UI + reason-capture is now a "wire up existing infrastructure" arc, not a "design from scratch" arc. Lesson: before scoping a feature as a full arc, grep for tables + services with the shape you'd need — sometimes past-you already built the foundation.

## Related arcs

- [[ship-120-prime-arc-retrospective-2026-09-05]] — parent arc; Ship 121' closed 3 of its 4 deferred items
- [[ship-4-prime-b-addendum-audit-log-correction-2026-07-17]] — the classification pattern this arc extended
- [[ship-118-prime-arc-retrospective-2026-09-05]] — added applicability_status_log + client_facts_log
- [[ship-119-prime-arc-retrospective-2026-09-05]] — added audit_ledger_download_token

## Deferred to Ship 122'+

1. **Erasure workflow on existing deletion_log plumbing** — Ship 120' item 3. Infrastructure exists (deletion_log table + deletion_service.py); need superuser endpoint + UI + reason capture + tenant-erasure two-person rule. Non-trivial arc; wait for a real customer-offboarding trigger.
2. **Ship 121' guards to CI (not just pre-commit)** — the pre-commit hook fires only when `git config core.hooksPath scripts/git-hooks` is set on the developer's clone. A CI job that runs the same greps would catch drift even when the hook is bypassed or not installed.
3. **Extend guards to Neo4j/Cypher and Chroma layer** — currently the drift-class guards only cover Postgres. Cross-store audit tables might exist in Neo4j (e.g. RequirementNode change history?) that need the same treatment.

## PoC deployment plan

`scripts/ops/ship-121-poc-update.sh` follows Ship 118'.d / 119'.d / 120' convention. From operator's Mac:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-121-poc-update.sh
'
```

Expected: install.sh re-applies extended `baseline_grants.sql`, prints all 17 tables' live grants (matching intended shape), regression test 4/4 pass. Pre-commit guards are dev-side (repo hooks) — they don't deploy to the PoC but they protect every future commit against Ship 120 / Ship 121 drift regression.
