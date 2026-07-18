---
name: feedback-test-fixture-audit-log-fks
description: "Integration-test fixtures can't delete a test tenant if the code under test writes to append-only audit-log tables — leave the tenant + user idempotent instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Integration tests that invoke the RAG pipeline CAN delete their
test tenant's rows in most tables, but `posture_status_log`
(compliance-load-bearing audit trail) will block tenant DELETE
if any posture change was written for that tenant.

**Historical note:** Ship 4'.b originally documented this rule
against 6 tables (`ai_call_log`, `chat_casefile_log`,
`chat_consensus_log`, `intake_trace_log`, `fact_recompute_log`,
`posture_status_log`) as "append-only audit logs by design".
schema_v79 (Ship 4'.b addendum, 2026-07-17) corrected the
misclassification — 5 of those are diagnostic logs (LLM cost
tuning, digest observability, pipeline QA) and are now
retention-eligible with DELETE granted. Only `posture_status_log`
remains genuinely load-bearing (INSERT/SELECT only + tenant FK
hardened from CASCADE to NO ACTION).

**Why the fixture pattern still stands:** even though the 5
diagnostic logs no longer block, using an idempotent tenant +
surgical-delete-of-what-you-created pattern remains the
lowest-friction cleanup. It doesn't accumulate DB drift and it
doesn't require enumerating every table with an FK to
`tenants(id)` (there are 39). See
[[ship-4-prime-b-audit-log-correction-2026-07-17]].

**How to apply:**

- Design the fixture so the tenant + user rows are IDEMPOTENT
  (create with `ON CONFLICT (id) DO NOTHING`). They persist
  across runs — that's fine, they're test fixtures, not real
  data.
- Cleanup does SURGICAL deletes only of the resources each test
  run creates: api_keys (by tenant_id), api_rate_limit_bucket
  (by key_id via api_keys), notifications (by tenant_id +
  title LIKE 'TEST %'), etc. Anything the test doesn't own,
  leave alone.
- Use a FIXED test tenant UUID (not random) so idempotent seed
  works. Example UUIDs already used:
  * `77777777-7777-7777-7777-777777777777` — external API tests
  * `88888888-8888-8888-8888-888888888888` — notification retention
  * `99999999-9999-9999-9999-999999999999` — notification delivery
- Keep test-tenant slugs / names distinct so accidents are
  visible in the DB (e.g. "ArionComply Delivery-Test Tenant").
- Audit-log rows for the test tenant will accumulate. Not a
  problem unless the tables grow unbounded — a retention sweep
  will age them out, and volumes are trivial for tests anyway.

**Anti-pattern** (learned in Ship 4'.b):

- Trying to enumerate every FK'd table and DELETE from it. 39
  tables reference `tenants(id)`; not all have DELETE grants;
  savepoints don't help because rollback resets the whole
  transaction on the append-only tables.
- Trying to open a superuser connection for cleanup. Adds
  another DSN + credential surface just for tests — not worth it.

Related: [[ship-4-prime-b-query-endpoint-2026-07-17]] (where this
surfaced), [[feedback-rls-grant-parity]] (the parent principle).
