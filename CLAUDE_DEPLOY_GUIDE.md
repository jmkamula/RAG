# CLAUDE_DEPLOY_GUIDE.md

**Operations playbook for ArionComply deployments — Claude Code edition.**

This file is intentionally structured for AI consumption. Paste it into a
Claude Code session alongside a diagnostic bundle (`arion-diag-*.tar.gz`
from `scripts/ops/diagnose.sh`) and Claude has everything it needs to
reason about a broken or degraded install.

Human-first documentation lives in:
- `docs/poc_install_guide.html` — install runbook
- `docs/demo_walkthrough.html` — demo flow
- `docs/architecture_brief.html` — architecture overview
- `docs/error_catalog.html` — error code catalog (companion to this file)

---

## 1. Environment

| Thing | Location |
|---|---|
| Install root | `/data/arioncomply` |
| Config file | `/data/arioncomply/.env` (chmod 640, owner `arioncomply`) |
| Systemd units | `arioncomply-api.service`, `arioncomply-chroma.service`, `arioncomply-jaeger.service`, `arioncomply-phoenix.service`, `arioncomply-sweep.timer` |
| Journal | `journalctl -u arioncomply-<service> -n 500 --no-pager` |
| Legacy tmp logs | `/tmp/arioncomply-api.log`, `/tmp/arioncomply-chroma.log` (only if service started via nohup, not systemd) |
| DB — compliance | Postgres `arioncomply_compliance` |
| DB — sessions | Postgres `arioncomply_sessions` (LangGraph checkpointer) |
| Graph | Neo4j `bolt://127.0.0.1:7687` |
| Vector store | Chroma `http://127.0.0.1:8000` |
| SPA | `http://127.0.0.1:8080/ui/arioncomply.html` |
| API | `http://127.0.0.1:8080/api/v1/*` |
| Jaeger | `http://127.0.0.1:16686` (if `OTEL_ENABLED=1`) |
| Phoenix | `http://127.0.0.1:6006` (if `OTEL_ENABLED=1`) |

**Two Postgres roles**:
- `arioncomply` — schema owner, bypasses RLS. Used by install.sh, migrations, `create_tenant.py`.
- `arioncomply_app` — RLS-scoped, used by the API pool. Requires `SET LOCAL app.tenant_id = '<uuid>'` for tenant-scoped reads.

## 2. Diagnostic surfaces

### 2.1 Diagnostic bundle (offline)

Run on the customer VM:

```bash
bash /data/arioncomply/scripts/ops/diagnose.sh
# → writes /tmp/arion-diag-<host>-<timestamp>.tar.gz
```

Contents (15 files):

| File | What it holds | When to read it |
|---|---|---|
| `README.txt` | metadata: host, timestamp, bundle name | orientation |
| `deploy_state.md` | systemd unit states + port bindings + "look here first" list | ALWAYS read first |
| `system.txt` | uname, os-release, disk, memory, uptime, whoami | resource / permissions issues |
| `services.txt` | `systemctl status` + `list-timers` + port bindings | any systemd service issue |
| `journal-api.txt` | last 500 lines of `arioncomply-api` journal | API crashes, boot errors |
| `journal-chroma.txt` | last 500 lines of `arioncomply-chroma` journal | vector store issues |
| `api-log.txt` | tail of `/tmp/arioncomply-api.log` if legacy path | non-systemd installs |
| `chroma-log.txt` | tail of `/tmp/arioncomply-chroma.log` if legacy path | non-systemd installs |
| `postgres.txt` | version, DB sizes, active queries, RLS tables, extensions | any Postgres-related error |
| `neo4j.txt` | node counts by label + edge counts by type + constraints | missing bridges, missing curated leaves |
| `chroma.txt` | collection list + document counts + server version | vector search issues |
| `tenants.txt` | tenants, framework enrolment, posture counts, api_keys metadata | provisioning + auth issues |
| `env.redacted.txt` | `.env` with secrets masked; variable names visible | config verification |
| `versions.txt` | git SHA, Python, Postgres, Neo4j, Chroma, key pip deps | version-drift bugs |

**Privacy**: bundle NEVER contains evidence text, chat prose, LLM
prompts/completions, user emails, or raw API keys.

### 2.2 Live status endpoint

```bash
curl -sf -H "X-API-Key: <admin-scoped-key>" \
  http://127.0.0.1:8080/api/v1/admin/deployment/status | jq .
```

Returns non-sensitive live metadata: version, git SHA, uptime,
per-service health, aggregate DB/graph/vector counts, tenant + framework
proxy, feature flags. Requires `admin:status` scope on the API key.

Grant that scope:

```sql
UPDATE api_keys
SET scopes = array_append(scopes, 'admin:status')
WHERE id = '<uuid>' AND NOT ('admin:status' = ANY(scopes));
```

### 2.3 Systemd inspection

```bash
systemctl status  arioncomply-api arioncomply-chroma
systemctl is-active arioncomply-api                       # active / activating / failed
systemctl show arioncomply-api | grep -E 'Restart|Exec|Environment'
journalctl -u arioncomply-api -n 200 --no-pager
journalctl -u arioncomply-api --since "10 min ago" --no-pager
```

### 2.4 Direct DB reach

```bash
source /data/arioncomply/.env
psql "$DATABASE_URL" -c "SELECT count(*) FROM posture_controls;"
psql "$SESSIONS_DATABASE_URL" -c "SELECT count(*) FROM checkpoints;"
```

### 2.5 Neo4j reach

```bash
python3 -c "
from neo4j import GraphDatabase
import os
d = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))
with d.session() as s:
    print('ER:', s.run('MATCH (n:EvidenceRequirement) RETURN count(n) AS c').single()['c'])
    print('ChecklistItem:', s.run('MATCH (n:ChecklistItem) RETURN count(n) AS c').single()['c'])
"
```

## 3. Symptom → verify → fix

For every ARION-* error code in `docs/error_catalog.html`, this is the
same info as three-line lookup format.

Full table lives in the HTML catalog. Quick-reference below for the
most common:

### ARION-INSTALL-005 — Neo4j graph load fails
- **SYMPTOM**: `install.sh` fails at Neo4j load with `ClientError` / connection refused
- **VERIFY**: `curl -sf http://localhost:7474` should return HTTP 200
- **FIX**: wait 30s then `PYTHONPATH=/data/arioncomply python3 enrichment/documents/load_to_neo4j.py`

### ARION-BOOT-002 — Chroma not listening
- **SYMPTOM**: API 500 on first chat with `RAG pipeline failed`
- **VERIFY**: `ss -tlnp | grep :8000` (or `lsof -i :8000`)
- **FIX**: `sudo systemctl start arioncomply-chroma && sudo systemctl enable arioncomply-chroma`

### ARION-BOOT-005 — PYTHONPATH missing from unit
- **SYMPTOM**: `journal-api.txt` shows `ModuleNotFoundError: rag.intake`
- **VERIFY**: `systemctl cat arioncomply-api | grep PYTHONPATH`
- **FIX**: `sudo systemctl edit arioncomply-api` → add `Environment=PYTHONPATH=/data/arioncomply` → `systemctl daemon-reload` + restart

### ARION-RUNTIME-002 — Fresh tenant "not assessed" everywhere
- **SYMPTOM**: dashboard shows all controls Not assessed
- **VERIFY**: `psql "$DATABASE_URL" -c "SELECT count(*) FROM posture_controls WHERE tenant_id='<uuid>';"` = 0
- **FIX**: upload documents via SPA OR seed posture rows via `create_tenant.py`

### ARION-RUNTIME-004 — Every posture shows [DRAFT]
- **SYMPTOM**: chat prose has `[DRAFT]` on every ref, even confirmed ones
- **VERIFY**: `psql "$DATABASE_URL" -c "SELECT ref, finding, confirmation_status FROM posture_controls WHERE tenant_id='<uuid>' LIMIT 5;"` — confirmation_status column populated?
- **FIX**: check `rag/posture_loader.py::load_posture` SELECT includes `confirmation_status` (Ship 30'.b regression class)

### ARION-RUNTIME-005 — Cold-cache 30s latency on first chat turn
- **SYMPTOM**: first turn takes 30+ seconds; subsequent turns <5s
- **VERIFY**: `journalctl -u arioncomply-api --since "5 min ago" | grep posture_cache`
- **FIX**: expected on cold cache. Warm with a throwaway query before demo. Ship 45 candidate.

### ARION-TENANT-001 — RLS violation on tenant INSERT
- **SYMPTOM**: `create_tenant.py` fails with "new row violates row-level security policy"
- **VERIFY**: script must use `_admin_dsn()` (owner role) not the default arioncomply_app pool
- **FIX**: check `scripts/dev/create_tenant.py` imports `_admin_dsn` and uses it for the tenants INSERT specifically

Full catalog: `docs/error_catalog.html` — 26 codes in the initial release.

## 4. Common ops queries

### 4.1 Recent chat traffic

```sql
SELECT session_id, created_at, question_type, latency_ms
FROM chat_casefile_log
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC
LIMIT 20;
```

### 4.2 Recent LLM cost

```sql
SELECT purpose, model, count(*), sum(cost_usd) AS usd
FROM ai_call_log
WHERE created_at > NOW() - INTERVAL '1 day'
GROUP BY 1, 2
ORDER BY 4 DESC;
```

### 4.3 Extraction quality flags (red/yellow/green)

```bash
curl -s -H "X-API-Key: <key>" \
  "http://127.0.0.1:8080/api/v1/admin/uploads/quality?days=7" | jq .
```

### 4.4 Sweep timer health

```sql
SELECT tick_id, work_type, status, items_scanned, items_acted_on, items_error,
       (extract(epoch from (completed_at - started_at)) * 1000)::int AS ms
FROM sweep_log
WHERE started_at > NOW() - INTERVAL '2 hours'
ORDER BY started_at DESC LIMIT 20;
```

### 4.5 Cross-framework bridge count (per direction)

```cypher
MATCH ()-[e]->()
WHERE type(e) IN ['IMPLEMENTS','SUPPORTS','DEMONSTRATES','GOVERNANCE','ENABLES']
RETURN type(e) AS bridge, count(e) AS n
ORDER BY n DESC;
```

### 4.6 Notification delivery pipeline

```sql
SELECT kind, severity, count(*), sum(CASE WHEN read_at IS NULL THEN 1 ELSE 0 END) AS unread
FROM tenant_notification
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY 1, 2 ORDER BY 3 DESC;
```

## 5. Codebase orientation

### 5.1 Where to look for X

| Symptom / concern | Read this |
|---|---|
| Chat pipeline shape | `rag/arion_graph.py`, `rag/llm_answer.py`, `rag/casefile/*` |
| Intent classification | `rag/classifier.py`, `rag/consensus/aggregator.py`, `rag/consensus/gatekeeper.py` |
| Retrieval | `vector/retriever.py`, `rag/graph_expander.py`, `rag/resolver.py` |
| Case-file digest / preservation | `rag/casefile/{types,digest,preservation,repair,log}.py` |
| Uploads → findings pipeline | `rag/intake/{readers,extractor,doc_pipeline,posture_writer}.py` |
| Consensus extraction | `rag/intake/consensus_extraction/` (Ship 33-43 arc) |
| Templates | `rag/templates/{renderer,xlsx_renderer,docx_renderer}.py` + `db/templates/req__*.md` |
| Posture engine | `rag/posture/{fulfilment_engine,engine_runner,advisory}.py` |
| Cascade | `rag/cascade/{engine,notify}.py` |
| Notifications | `rag/notifications/{deliver,produce}.py` + `rag/scheduler/tick.py` |
| Deployment status | `rag/admin/deployment_status.py` (Ship 48'.c) |
| Output humanization | `rag/output/{gateway,transforms}.py` + `rag/output/vocab/*.json` |
| External API | `rag/external/` + api_server.py `/api/external/v1/*` |
| SPA | `static/arioncomply.html` (single file) |
| Systemd units | `ops/systemd/arioncomply-{api,chroma,jaeger,phoenix,sweep}.service{,.timer}` |
| Install path | `deploy/install.sh` + `deploy/postgres_preamble.sql` + `deploy/.env.example` |
| Tenant provisioning | `scripts/dev/create_tenant.py` |
| Diagnostic bundle | `scripts/ops/diagnose.sh` |

### 5.2 Where to look for schema changes

- `db/baseline/schema_baseline.sql` — install target (pg_dump --schema-only)
- `db/baseline/seed_curator_data.sql` — 54 rows of portable reference data
- `db/schema_v<N>.sql` — historical migrations, not applied on fresh installs
- `db/baseline/schema_sessions_baseline.sql` — LangGraph checkpointer tables

### 5.3 Curated content locations

- `enrichment/documents/document_requirements.py` — canonical EvidenceRequirement + DerivedSpec
- `db/doc_mappings/*.yaml` — per-doc-shape extraction hints
- `db/workbook_mappings/*.yaml` — per-workbook-tab extraction hints
- `db/templates/req__*.md` — 645+ template scaffolds
- `docs/tree_*.html` — per-control anatomy pages

## 6. When to escalate to codebase changes

The playbook + error catalog handle known failures. When a diagnostic
bundle shows a state that doesn't match any documented code:

1. **Snapshot the state**: preserve the bundle. Note the git SHA in
   `versions.txt`.
2. **Grep for prior**: is this a known regression class? Search
   `docs/memory/` for the affected subsystem (e.g. `posture_loader`,
   `extractor`, `casefile`).
3. **Add a new error code** to `docs/error_catalog.html` when the
   root cause is identified. Use the next N in the appropriate prefix.
4. **Update this file** with the new symptom → verify → fix in
   Section 3.
5. **Codify the lesson** as a memory entry under `docs/memory/` if
   the failure mode reveals a design issue.

## 7. Privacy invariants for anything Claude Code exports

When Claude Code helps a customer, it may generate: modified
diagnostic queries, follow-up SQL, error explanations. Rules:

- **Never suggest exfiltrating tenant PII** — user emails, evidence
  text, chat conversations, posture NC descriptions (may contain
  proprietary business context).
- **Prefer aggregate metrics** — counts, distributions, timings —
  over individual row samples when demonstrating a diagnosis.
- **Names/paths OK** — tenant slug, control ref, framework standard_id
  are public compliance vocabulary; not secrets.
- **API key values NEVER** — refer only to the last-4 or hash prefix.
- **If in doubt, redact** — safer to lose a datum than to leak PII.

## 8. What this playbook is NOT

- Not a curated remedy library — the fix commands are prescriptive
  but not automated. Human/AI judgment applies.
- Not exhaustive — new failure modes will emerge from real customer
  installs. Extend Section 3 + `error_catalog.html` as they surface.
- Not a substitute for reading code — pointers in Section 5 help
  navigate; understanding the change still requires the source.
- Not the human runbook — `docs/poc_install_guide.html` is for
  first-time operators; this is for AI-assisted troubleshooting.

---

*Last updated: Ship 48'.d, 2026-07-28. Update alongside
`docs/error_catalog.html` whenever new codes are added or when the
codebase layout in Section 5 changes materially.*
