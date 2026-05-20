---
name: sql-dry-run-nested-transaction
description: Wrapping a SQL file in outer BEGIN/ROLLBACK does NOT roll back when the file has its own BEGIN/COMMIT — the inner COMMIT commits the outer transaction.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7c33fad-b32e-4557-9944-b406bcbbd8ee
---

**Rule:** Do not "dry-run" a SQL migration by piping it inside an outer `BEGIN; ... ROLLBACK;` if the file itself contains `BEGIN; ... COMMIT;`. Postgres does not nest transactions — when it hits the inner `COMMIT`, it commits the *outer* transaction. The trailing `ROLLBACK` then has no transaction to undo and is a no-op. Changes apply for real.

**Why:** burned this 2026-05-14 while validating `db/schema_v8.sql`. The file legitimately wrapped its DDL in `BEGIN; ... COMMIT;` for atomicity. I added an outer `BEGIN; <file> ROLLBACK;` thinking it was a dry-run; the inner `COMMIT` fired and applied the migration to the live DB before the outer `ROLLBACK` got the chance. Got lucky — the schema state was the intended end state anyway — but the user had explicitly asked me to dry-run first and ask before applying. I bypassed that guardrail.

**How to apply:**
- Before "dry-running" a SQL file, scan it for `BEGIN`/`COMMIT`/`COMMIT;` literals. If present, the outer-wrap approach does not work.
- Safer dry-run patterns:
  - **Strip the file's own transaction markers first**: `grep -vE '^(BEGIN|COMMIT);$' file.sql` then wrap in outer `BEGIN;…ROLLBACK;`.
  - **Savepoint**: outer `BEGIN; SAVEPOINT s; <file>; ROLLBACK TO SAVEPOINT s; ROLLBACK;` (but inner `COMMIT` still releases the savepoint — limited help).
  - **Syntax-only check**: feed the file to a fresh DB clone or an EXPLAIN-only path; don't rely on rollback.
  - **Best**: when the user says "dry-run, then ask before applying," treat that as a permission gate. Do the syntax check via a different mechanism (parse it, run it against a throwaway DB, or just inspect it), then *literally stop* and ask. Don't chain the dry-run and the real run via subtle transaction tricks.
- Also: a SQL file authored for a migration step usually does want internal `BEGIN/COMMIT` for atomicity — don't strip those from the canonical file just to enable wrap-dry-runs.
