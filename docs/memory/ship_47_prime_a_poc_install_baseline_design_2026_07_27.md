---
name: ship-47-prime-a-poc-install-baseline-design-2026-07-27
description: "Ship 47'.a design memo — Postgres install baseline for POC deployments. pg_dump --schema-only produces db/schema_baseline.sql (77 tables, 15 views, 75 RLS policies). Curator seed data (9 standards + retention_policies + ref_prefixes + ref_sequences + standard_relationships) split into db/seed_curator_data.sql. Neo4j + Chroma retain their existing load paths (load_to_neo4j.py + Chroma HTTP mode with persistent SQLite dir)."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 47'.a — POC install baseline design.

## Context

Opens Ship 47 arc. Goal: fresh Ubuntu VM → running ArionComply with a
single install command. First customer POC target is
"they-provide-VM-we-install-anywhere" — cloud or on-prem, minimum
effort, OpenAI as the LLM. See Ship 46's deployment discussion for
the shape trade-offs.

## Current Postgres state (measured 2026-07-27)

- **PostgreSQL 16.14** on Ubuntu 24.04
- **2 databases**: `arioncomply_compliance` (120 MB) + `arioncomply_sessions` (50 MB)
- **77 tables + 15 views** in the compliance DB
- **75 RLS policies** across ~30 tenant-scoped tables
- **3 extensions**: `plpgsql`, `pg_trgm`, `pgcrypto`
- **3 roles**: `postgres` (superuser), `arioncomply` (schema owner),
  `arioncomply_app` (RLS-scoped app user; the API pool uses this)
- **92 schema_v*.sql** migrations under `db/` — v1 through v90 with
  a couple of gaps (schema_v8_phase3.sql, etc)

## Strategy: baseline SQL, not sequential replay

### Rejected: sequential apply of the 92 migration files

- Never tested against an empty DB in that order
- Some migrations depend on prior data existing (backfills, ID reservations)
- Some are ALTER-only and expect the target column/type
- Any one broken migration blocks the whole install

### Adopted: `pg_dump --schema-only` snapshot

Take a snapshot of the current live schema — the exact shape the running
API expects — and commit as `db/schema_baseline.sql`. This becomes the
canonical install target.

**Trade-off**: this schema is authoritative going forward. New schema
changes append as `schema_v91.sql`, `v92.sql`, ... on top of the
baseline. Migrations before v91 become historical artefacts (kept in
`db/schema_v*.sql` for provenance; not applied on new installs).

Analogous to Rails' `structure.sql` + `db/migrate/` split. Or Django's
`initial` migration.

## Two files, clean split

### `db/schema_baseline.sql`
DDL only: tables, views, indexes, sequences, RLS policies, functions,
triggers, extensions, roles. Produced via:

```bash
pg_dump --schema-only \
        --no-owner \
        --no-privileges \
        -U postgres -h 127.0.0.1 -d arioncomply_compliance \
    > db/schema_baseline.sql
```

Post-processing needed:
1. Ensure `CREATE EXTENSION IF NOT EXISTS pgcrypto`, `pg_trgm` at top
2. Wrap in `BEGIN; ... COMMIT;` for atomicity
3. Strip search_path preamble that pg_dump adds
4. Confirm role references (`arioncomply`, `arioncomply_app`) all use
   role names not OIDs

### `db/seed_curator_data.sql`
The portable-across-tenants seed data. Small (~200-500 rows total):

| Table | Rows | Purpose |
|---|---|---|
| `standards` | 9 | ISO 27001/27002/27003/27004/27005/27018/27701, GDPR, NIST-CSF |
| `standard_relationships` | 5 | Framework role model edges at the SQL layer (Neo4j has the graph) |
| `retention_policies` | 16 | Data class → retention_days for compliance retention |
| `ref_prefixes` | 8 | External-ref prefix reservations (R###, DOC###, etc) |
| `ref_sequences` | 7 | Per-prefix current sequence numbers |
| `roles` | 7 | RBAC role catalog for future tenant-user auth |
| Notification kind enum via CHECK constraint | — | Already in `schema_baseline.sql`; no data |

**Not seeded** (per-tenant data, expected to be empty on POC install):
- `tenants`, `posture_controls`, `document_findings`, `client_documents`,
  `document_uploads`, `client_facts`, `risks`, `assets`,
  `applicable_standards`, `api_keys`, `chat_*_log`, `ai_call_log`, etc.

**Excluded from seed** (per-VM state, not portable):
- `enricher_cache` — LLM-derived cache; rebuilds on demand
- `posture_history_*` — history tables partitioned by year
- `sweep_log` — telemetry from the sweep timer
- `sessions`-DB tables — LangGraph checkpointer state (fresh install
  starts empty)

Produced via a targeted extraction script (`scripts/dev/dump_curator_seed.py`)
that runs `COPY (SELECT ...) TO STDOUT` for each curator table.

## RLS policies — the tricky bit

`pg_dump --schema-only` includes RLS policies. Verify:

- `arioncomply_app` role is created BEFORE any policies reference it
- `set_config('app.tenant_id', ...)` context expectation is in the
  policy predicates (already the pattern across the codebase)
- No policies reference a specific tenant UUID (all should be
  `current_setting('app.tenant_id')`)

## Extensions + roles bootstrap sequence

The baseline SQL alone can't create roles or install extensions from
scratch (needs superuser). `install.sh` runs a preamble as `postgres`:

```sql
-- Preamble (superuser context)
CREATE ROLE arioncomply LOGIN;
CREATE ROLE arioncomply_app LOGIN;
CREATE DATABASE arioncomply_compliance OWNER arioncomply;
CREATE DATABASE arioncomply_sessions   OWNER arioncomply;
\c arioncomply_compliance
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

Then `schema_baseline.sql` runs as `arioncomply`, then
`seed_curator_data.sql` runs as `arioncomply`.

## Neo4j + Chroma — no changes needed

Both already have working load paths:

- **Neo4j**: `enrichment/documents/load_to_neo4j.py` populates the
  requirement graph (RequirementNode + EvidenceRequirement +
  ChecklistItem + FulfilmentSpec + all bridge edges). Idempotent.
  Just needs to run after Neo4j is up.

- **Chroma**: SQLite-backed persistence at `/data/arioncomply/chroma_db`.
  The install path is `chroma run --path /data/arioncomply/chroma_db`.
  Collections are populated by `scripts/reindex_all.py` on first
  install (or restored from a snapshot for faster onboarding).

## `install.sh` structure (Ship 47'.c)

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. System deps
sudo apt-get install -y postgresql-16 neo4j python3-pip

# 2. Postgres bootstrap
sudo -u postgres psql -f deploy/postgres_preamble.sql

# 3. Compliance schema + seed
psql -U arioncomply -d arioncomply_compliance -f db/schema_baseline.sql
psql -U arioncomply -d arioncomply_compliance -f db/seed_curator_data.sql

# 4. Sessions DB (much simpler — LangGraph checkpointer table)
psql -U arioncomply -d arioncomply_sessions -f db/schema_sessions_baseline.sql

# 5. Python deps
pip install --break-system-packages -r requirements.txt

# 6. Neo4j load
sudo systemctl enable --now neo4j
python3 enrichment/documents/load_to_neo4j.py

# 7. Chroma dir + systemd
mkdir -p /data/arioncomply/chroma_db
sudo cp ops/systemd/arioncomply-*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now arioncomply-chroma arioncomply-api

# 8. Print next steps
echo "Set OPENAI_API_KEY in /data/arioncomply/.env"
echo "Create your first tenant: python3 scripts/dev/create_tenant.py --name 'Your Corp'"
```

## What Ship 47 does NOT do

- **Container images** — Ubuntu + systemd; docker/podman is a follow-on
- **Multi-tenant onboarding UX** — `create_tenant.py` is CLI only for
  POC; web-based onboarding is later
- **OIDC / SSO** — static API keys for POC
- **TLS / reverse proxy** — SSH tunnel access is fine
- **Backup / restore automation** — daily pg_dump timer is a
  follow-on; POC customers can add manually if they care
- **Ansible/Terraform packaging** — the `install.sh` is the automation
- **Curated demo tenant seeding** — POC starts empty; the Arion demo
  tenant is not what customers want to see. Bulk-loading a demo
  tenant is an option later.
- **Chroma index bootstrapping** — first install rebuilds embeddings
  via `scripts/reindex_all.py`; this takes ~5-10 min at first API
  startup. Alternative: ship a pre-built Chroma dir. Deferred to
  47'.c decision point.

## Sub-arc plan

| Sub-arc | Delivery |
|---|---|
| 47'.a | This memo |
| 47'.b | Generate `db/schema_baseline.sql` + `db/seed_curator_data.sql` + `db/schema_sessions_baseline.sql`; verify apply on scratch DB |
| 47'.c | `deploy/install.sh` + `deploy/postgres_preamble.sql` + `requirements.txt` freeze |
| 47'.d | `scripts/dev/create_tenant.py` (or verify existing) |
| 47'.e | POC install runbook at `docs/poc_install_guide.html` |
| 47'.f | Retro + Ship 47 close |

## Related

- Ship 46 deployment discussion (this conversation)
- `db/schema_v*.sql` — the historical migrations (kept, not applied
  on new installs after 47'.b)
- `ops/systemd/arioncomply-*.service` — installed by 47'.c step 7
- `enrichment/documents/load_to_neo4j.py` — Neo4j load path (unchanged)
