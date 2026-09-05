---
name: ship-120-prime-arc-retrospective-2026-09-05
description: Ship 120' arc — audit-table DELETE-drift diagnostic + fix + regression test
metadata:
  type: project
---

# Ship 120' — audit-table DELETE-drift diagnostic + fix

**Date:** 2026-09-05
**Sub-arcs:** 120'.a diagnostic → 120'.b root-cause → 120'.c fix → 120'.d regression test → 120'.e deploy → 120'.f eval → 120'.g this doc
**Trigger:** Ship 119' PoC deployment step 5 output showed `audit_ledger_download_token` had `DELETE` granted to `arioncomply_app`, contradicting `schema_v116`'s explicit `REVOKE DELETE`. Flagged mid-conversation; opened as its own arc because the drift shape suggested a systemic issue larger than one table.

## Motivation

The auditor-defensibility discipline of compliance-load-bearing tables (Ship 4'.b addendum, Ship 118'.b, Ship 119'.c) rests on the app role NOT having `DELETE` (or in some cases `UPDATE`) on those tables. If the app role can silently delete a `posture_status_log` row or a `audit_ledger_download_token`, the "we never erased the audit trail" claim in front of an auditor becomes unverifiable — the tenant is telling the auditor they didn't do a thing they had permission to do.

Ship 119'.c ended with 25/25 PII tests green and the token endpoint 401'ing correctly, but the deploy verification revealed DELETE was granted anyway. Left unfixed, every fresh customer install would silently ship with the wrong permissions on every audit table.

## Diagnostic — 120'.a

Enumerated the 9 tables that have codified append-only or diagnostic-log semantics. Result on the dev VM:

```
                             actual                       intended
posture_status_log         DELETE,INSERT,SELECT,UPDATE    INSERT,SELECT
applicability_status_log   INSERT,SELECT                  INSERT,SELECT
client_facts_log           INSERT,SELECT                  INSERT,SELECT
audit_ledger_download_token INSERT,SELECT,UPDATE          INSERT,SELECT,UPDATE
ai_call_log                DELETE,INSERT,SELECT,UPDATE    DELETE,INSERT,SELECT
chat_casefile_log          DELETE,INSERT,SELECT,UPDATE    DELETE,INSERT,SELECT
chat_consensus_log         DELETE,INSERT,SELECT,UPDATE    DELETE,INSERT,SELECT
fact_recompute_log         DELETE,INSERT,SELECT,UPDATE    DELETE,INSERT,SELECT
intake_trace_log           DELETE,INSERT,SELECT,UPDATE    DELETE,INSERT,SELECT
```

7 of the 9 tables had drift. On the fresh Ship 119' PoC install, `audit_ledger_download_token` had drifted too (extra `DELETE`) — the dev VM shape was slightly better because its baseline_grants.sql hadn't been re-run since schema_v116, so the REVOKE from the migration was still in place.

## Root cause — 120'.b

`deploy/baseline_grants.sql` (loaded by `install.sh` at step 4.9) contains:

```sql
GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA public TO arioncomply_app;
```

This runs **after** all `schema_v*.sql` migrations complete. The blanket `GRANT ALL` silently overwrites the per-table `REVOKE` clauses in:

- `schema_v21_posture_status_log.sql` — REVOKE UPDATE, DELETE on posture_status_log
- `schema_v79_ship4b_audit_log_grant_correction.sql` — REVOKE UPDATE on ai_call_log/chat_casefile_log/chat_consensus_log/fact_recompute_log/intake_trace_log + REVOKE UPDATE, DELETE on posture_status_log (double-defensive)
- `schema_v115_applicability_and_scoping_history.sql` — REVOKE DELETE on applicability_status_log + client_facts_log
- `schema_v116_audit_ledger_download_tokens.sql` — REVOKE DELETE on audit_ledger_download_token

Every one of these gets clobbered on every fresh install. The comment in baseline_grants.sql even documents the ordering intent ("Run AFTER migrations so any migrations that create new tables get their ownership + grants set too") — the auditor-defensibility contract collided with the "new tables get default grants" convenience.

## Fix — 120'.c

Added a post-blanket-GRANT `DO $$` block to `deploy/baseline_grants.sql` that explicitly re-REVOKEs the intended shape for the 9 audit tables. Uses `to_regclass()` guard so the block is safe on customer boxes that haven't yet applied every schema (silently no-ops for missing tables).

Design choice: the fix lives in **one file** (`baseline_grants.sql`) rather than being reasserted in every future `schema_v*.sql`. This means adding a new compliance-load-bearing audit table requires two edits — the migration file AND `baseline_grants.sql` — but keeps the intended shape in one place instead of scattered across dozens of migration files that could each get outrun by another blanket grant later.

Verified locally: after applying the updated `baseline_grants.sql`, all 9 tables report the intended shape (see 120'.a table above with "actual" column matching "intended").

## Regression test — 120'.d

`tests/test_audit_table_grants.py` — 4 assertions:

1. **`test_append_only_audit_tables_have_no_update_or_delete`** — `posture_status_log`, `applicability_status_log`, `client_facts_log` must be exactly `{SELECT, INSERT}`.
2. **`test_counter_audit_tables_shape`** — `audit_ledger_download_token` must be exactly `{SELECT, INSERT, UPDATE}`.
3. **`test_diagnostic_logs_have_no_update`** — 5 diagnostic tables must be exactly `{SELECT, INSERT, DELETE}`.
4. **`test_no_new_audit_table_slipped_in_unclassified`** — soft-warn if any new `%_log` / `%_audit` table appears in the schema without being classified in either the append-only or diagnostic set.

Passes 4/4 on the dev VM post-fix. The soft-warn test surfaced 8 additional `_log` tables (`audit_log`, `cascade_suppression_log`, `client_fact_change_log`, `confirmation_log`, `deletion_log`, `external_evidence_verification_log`, `intake_consensus_log`, `request_trace_log`) that deserve future classification — captured as deferred.

Uses `ARION_OWNER_PW` via `python-dotenv` (Ship 111' canonical env-var scheme) — the test connects as `arioncomply` (owner) so `information_schema.role_table_grants` returns full visibility regardless of RLS.

## Lessons codified

### Lesson 221 — Blanket GRANTs eat per-table REVOKEs when they run last

`GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public` is a convenience-first tool, and every migration's per-table `REVOKE` before it runs becomes theatre. Two options for compliance-load-bearing schemas: either drop the blanket grant and enumerate per-table (many hundreds of grants), or add a post-blanket restore block for the specific tables that need tighter constraints. Ship 120' picked option 2 — enumeration only for the compliance-relevant subset (~9 tables), everything else keeps convenience defaults.

The corollary: if a schema migration ships a REVOKE and a downstream install-time hook re-GRANTS, the REVOKE was never real. The grant matrix in `information_schema.role_table_grants` is the ground truth, not the migration file. Test what actually runs, not what you meant.

### Lesson 222 — "Ordering intent documented in a comment" is not "ordering intent enforced"

The comment in `baseline_grants.sql` explicitly noted "Run AFTER migrations so any migrations that create new tables get their ownership + grants set too." The reasoning was correct for one class of table (new features that need default grants) and wrong for another (compliance-load-bearing audit trails). No test caught the contradiction because no test existed. Comments describe intent, not behaviour. When behaviour matters for compliance, encode it in a test that runs against the actual live shape.

### Lesson 223 — Deploy verification steps that show grants are worth the 5 lines of SQL

Ship 119'.c PoC update step 5 was `SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'audit_ledger_download_token'`. Without that visible output in the deploy log, the drift would have been silent until someone hit `pytest` in the right place or an auditor asked. Every future ship-N-poc-update.sh that touches an audit table should print the actual live grants — the 5-line SELECT costs almost nothing and turns a silent regression into a visible one.

### Lesson 224 — Diagnostic-log drift is easier to accept but should be caught by the same test

Ship 120' also fixed the 5 diagnostic-log tables (`ai_call_log` etc.) that had errant `UPDATE` grants. `UPDATE` on a diagnostic log is arguably less scary than `DELETE` on an audit log (retention sweeps use DELETE; UPDATE is just a footgun for silently rewriting entries), but the drift shape is the same and the fix location is the same. Regression tests should treat both classes uniformly — the test doesn't need a "severity" axis when the mechanism (baseline_grants.sql clobber) is identical.

### Lesson 225 — Soft-warn assertions catch scope creep without blocking

The 4th test (`test_no_new_audit_table_slipped_in_unclassified`) surfaces new `_log` tables that haven't been classified into either set. It doesn't hard-fail because that would block unrelated work every time someone adds a diagnostic table; it prints a warning that lands in CI output for future review. This is the "collaborative regression" shape — the test's job is to make drift visible, not to weld every future migration to a Ship 120' TODO. The 8 unclassified tables it surfaced are captured as deferred, not blockers.

## Related arcs

- [[ship-4-prime-b-addendum-audit-log-correction-2026-07-17]] — established the compliance-load-bearing vs diagnostic-log distinction that Ship 120' enforces
- [[ship-118-prime-arc-retrospective-2026-09-05]] — added `applicability_status_log` + `client_facts_log` to the append-only set; Ship 120' fixes their grant drift
- [[ship-119-prime-arc-retrospective-2026-09-05]] — added `audit_ledger_download_token`; Ship 119' PoC deploy is what surfaced the drift
- [[ship-104-prime-arc-retrospective-2026-09-02]] — first arc to consume `baseline_grants.sql` via install.sh at scale

## Deferred to Ship 121'+

1. **Classify the 8 unclassified `_log` tables** — the soft-warn found `audit_log`, `cascade_suppression_log`, `client_fact_change_log`, `confirmation_log`, `deletion_log`, `external_evidence_verification_log`, `intake_consensus_log`, `request_trace_log`. Each needs a call on append-only vs diagnostic + an entry in the regression test.
2. **CI grep guard against `GRANT ... ON ALL TABLES ... TO arioncomply_app`** — the next arc that adds a new "grant all" convenience block could re-open this bug on a table not yet in the audit list. Static check prevents.
3. **Superuser-only "erasure with provenance" flow** — the tenant-delete-when-audit-history-exists question is still open (Ship 4'.b addendum FK RESTRICT deferred). GDPR Art.17 needs a real answer eventually.
4. **`schema_v_check` migration audit** — schema_v* files that GRANT UPDATE to arioncomply_app on tables the migration created are the mirror-image bug: a schema file granting more than it should. Would need a static check on schema_v* GRANT statements.

## PoC deployment plan

`scripts/ops/ship-120-poc-update.sh` follows Ship 118'.d / 119'.d convention. From operator's Mac:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-120-poc-update.sh
'
```

Expected result: install.sh re-applies `baseline_grants.sql` (new REVOKE block idempotent-fires), API restarted, grant-shape SELECT output shows the intended matrix on all 9 tables, `tests/test_audit_table_grants.py` passes 4/4.

No schema_v117 needed — this is a pure `baseline_grants.sql` fix. No new tables, no data mutations, zero migration risk on existing customer installs.
