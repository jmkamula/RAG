---
name: rls-tenant-context-for-app-user
description: "Postgres reads from tenant-scoped tables silently return 0 rows unless `app.tenant_id` is set via `set_config`. The `arioncomply_app` role has no BYPASSRLS — only `arioncomply` (superuser) does."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7c33fad-b32e-4557-9944-b406bcbbd8ee
---

**Rule:** Any Postgres code that queries tenant-scoped tables (incidents, incident_classifications, incident_obligations, incident_documents, client_documents, posture_*, etc.) MUST set `app.tenant_id` at the start of each transaction via:

```python
cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (str(tenant_id),))
```

The `TRUE` flag = transaction-local; auto-clears on commit/rollback. This pattern is established in `rag/posture_loader.py`, `api_server.py:231`.

**Why:** burned this 2026-05-14 while building `rag/incident_fulfillment.py`. RLS policies on these tables are `(tenant_id = current_setting('app.tenant_id')::uuid AND is_active = TRUE)`. When `app.tenant_id` is not set, the comparison evaluates to NULL, which RLS treats as a non-match — all rows are filtered out **silently**. No error, no warning, just empty result sets.

The trap: it appears to work in CLI testing because CLI scripts often default to connecting as the `arioncomply` superuser role (`POSTGRES_USER` env var default), which has implicit BYPASSRLS via superuser status. But the API pool uses `DATABASE_URL` which connects as `arioncomply_app` — this role has no BYPASSRLS:

```
psql=> SELECT rolname, rolsuper, rolbypassrls FROM pg_roles
        WHERE rolname IN ('arioncomply', 'arioncomply_app');
     rolname      | rolsuper | rolbypassrls
  ---------------+----------+--------------
   arioncomply     |    t     |    f       ← superuser bypasses RLS
   arioncomply_app |    f     |    f       ← strictly enforced
```

So a module that "works" in `python3 module.py` testing can silently fail in production with no error trail.

**How to apply:**
- At the start of every public method that touches tenant data, set the context:
  ```python
  with self._pg.cursor() as cur:
      cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                  (str(tenant_id),))
  ```
- For loops over incidents/tenants, set it both at the outer level and inside each iteration's commit boundary, because commit clears the local config.
- After read-only operations on a pooled connection, call `conn.commit()` explicitly so the set_config is cleared and the connection returns to the pool clean. Don't leave an open transaction lingering.
- When you write a new tenant-scoped read/write method, treat `set_config('app.tenant_id', ..., TRUE)` as a precondition — not optional polish.
- Don't rely on POSTGRES_USER defaults during testing. If the CLI runs as superuser and the API pool uses the app user, the behavior diverges silently. Test both code paths or always set the context defensively.

**Affected modules (fixed 2026-05-14):**
- `rag/incident_materializer.py` — set_config added in `materialize_for_incident`, `materialize_for_tenant`, `_verify`
- `rag/incident_fulfillment.py` — set_config added in `check_for_incident`, `check_for_tenant`, `_verify`
- `rag/graph_expander.py:get_incident_obligations` — set_config + explicit commit added; was silently broken in chat path before the fix

Related: [[incident-obligations-model]]
