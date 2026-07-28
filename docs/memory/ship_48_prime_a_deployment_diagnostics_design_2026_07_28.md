---
name: ship-48-prime-a-deployment-diagnostics-design-2026-07-28
description: "Ship 48'.a design memo — deployment diagnostics + Claude-Code-consumable operational context. Four surfaces: (1) scripts/ops/diagnose.sh bundle generator, (2) docs/error_catalog.html with ARION-INSTALL-* / ARION-RUNTIME-* codes, (3) /api/v1/admin/deployment/status endpoint, (4) CLAUDE_DEPLOY_GUIDE.md AI-consumption playbook. Enables debugging N customer deployments without SSH into each."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 48'.a — deployment diagnostics design memo.

## Problem

Ship 47 shipped a one-command install path. Customers can bring up
ArionComply on any Ubuntu VM. Now: when a specific customer install
misbehaves, how does support (human or Claude Code) diagnose it?

Real-world constraints:

- **No SSH into the customer VM.** Corporate perimeter, VPN rules,
  "no external access to production" policy. Common in Fortune-500.
- **Fresh state, not our demo state.** Their tenants, their evidence,
  their config, their network policy.
- **State is scattered.** Postgres (compliance + sessions), Neo4j
  graph, Chroma vector store, `.env` (with secrets), systemd
  journals, `/tmp/*.log`, OTel spans (if enabled).
- **Claude Code is only powerful when given structured context.**
  Raw log tails work at N=1; they scale badly at N=many.

Solution: bake diagnostic surfaces into the install so any deployment
can serialise its own state for AI-assisted (or human) troubleshooting.

## Four surfaces

### 1. Diagnostic bundle — `scripts/ops/diagnose.sh`

Customer runs one command; produces `/tmp/arion-diag-<host>-<date>.tar.gz`.
Contents (each a plain-text or JSON file):

| File | Contents |
|---|---|
| `system.txt` | uname, os-release, disk usage (df), memory (free), uptime, timezone |
| `services.txt` | `systemctl status` for arioncomply-api / -chroma / -jaeger / -phoenix / -sweep.timer + `is-enabled` flags |
| `journal-api.txt` | `journalctl -u arioncomply-api -n 500 --no-pager` |
| `journal-chroma.txt` | same for chroma |
| `api-log.txt` | tail -500 of /tmp/arioncomply-api.log |
| `postgres.txt` | version, DB sizes, connection count, active queries, `\l`, RLS enabled tables, extension list |
| `neo4j.txt` | node counts by label, edge counts by type, database status |
| `chroma.txt` | collection list + document counts per collection |
| `tenants.txt` | tenant list (name, slug, created_at, framework enrolment, posture counts) — no user PII, no evidence text |
| `env.redacted.txt` | contents of .env with values masked to `***REDACTED***` (schema visible, secrets not) |
| `versions.txt` | git rev-parse HEAD, python3 --version, pg_config --version, neo4j --version, chroma --version, pip freeze |
| `deploy_state.md` | when install ran, what stages completed, what failed if anything |

Customer emails/uploads the tarball. Support (or Claude Code) unpacks
locally, reads structured files, diagnoses.

**Privacy discipline**: `.env` values redacted; no evidence excerpts;
no user emails beyond tenant admin (which they already know); no
chat conversation content. Tenant NAMES and control REFS ok (already
non-secret compliance vocabulary).

### 2. Error code taxonomy — `docs/error_catalog.html`

Every install + boot-time error carries a code. The catalog maps
code → symptom → root cause → confirmation command → fix.

Prefixes:
- `ARION-INSTALL-NNN` — install.sh time failures
- `ARION-BOOT-NNN` — API startup / lifespan failures
- `ARION-RUNTIME-NNN` — post-boot operational failures
- `ARION-TENANT-NNN` — tenant provisioning failures

Example entries:

| Code | Symptom | Cause | Confirm | Fix |
|---|---|---|---|---|
| `ARION-INSTALL-001` | install.sh fails at "System packages" step | apt lock held | `sudo lsof /var/lib/dpkg/lock-frontend` | wait for other apt process, or reboot |
| `ARION-INSTALL-005` | Neo4j graph load fails with ClientError | Neo4j still warming up | `curl -sf http://localhost:7474` | retry `enrichment/documents/load_to_neo4j.py` after 30s |
| `ARION-BOOT-002` | API 500s with "RAG pipeline failed" | Chroma not on :8000 | `lsof -i :8000` | start arioncomply-chroma, verify it binds |
| `ARION-RUNTIME-011` | Chat 30s cold-cache | posture_cache miss | (expected — Ship 45'.c) | warmup chat before demoing |
| `ARION-TENANT-003` | create_tenant.py 'RLS policy' error | Running as app-role not owner | check DATABASE_URL user is `arioncomply_app` | tenant scripts use `_admin_dsn()` — verify import path |

Codes are stable across releases. New failures get new codes.
Catalog lives in `docs/error_catalog.html` served on 8001.

### 3. Deployment status endpoint — `/api/v1/admin/deployment/status`

Read-only endpoint exposing non-sensitive metadata. Scoped to an
admin API key (existing `api_keys.scopes` array; add `admin:status`
scope in an existing schema-baseline-friendly way).

Response shape:

```json
{
  "arion_version":   "0.48.0",
  "git_sha":         "ab20d9c",
  "installed_at":    "2026-07-27T18:00:00Z",
  "uptime_sec":      3600,
  "services": {
    "api":    "healthy",
    "chroma": "healthy",
    "neo4j":  "healthy",
    "postgres": "healthy"
  },
  "postgres": {
    "compliance_size_mb": 120,
    "sessions_size_mb":    50,
    "connection_count":    3,
    "extensions":         ["pgcrypto","pg_trgm"]
  },
  "neo4j": {
    "requirement_nodes": 1247,
    "checklist_items":   4293,
    "bridges":            505
  },
  "chroma": {
    "collections": 5,
    "total_docs":  1247
  },
  "tenants": {
    "count":      3,
    "frameworks": ["ISO27001:2022","ISO27701:2019","GDPR:2016/679"]
  },
  "otel_enabled":     false,
  "consensus_extraction_enabled": true
}
```

Customer can share the JSON (no secrets, no evidence content) or
pipe it into a Claude Code session. `curl -H "X-API-Key: $KEY"
http://127.0.0.1:8080/api/v1/admin/deployment/status | python3 -m
json.tool` — one line.

### 4. `CLAUDE_DEPLOY_GUIDE.md` — Claude-Code-oriented playbook

Structured markdown checked into every install at `/data/arioncomply/CLAUDE_DEPLOY_GUIDE.md`.
Written for AI consumption, not human reading. Layout:

```
# ArionComply — deployment operations guide (Claude Code edition)

## Environment
- Install root:     /data/arioncomply
- Systemd units:    arioncomply-{api,chroma,jaeger,phoenix}, arioncomply-sweep.timer
- Config file:      /data/arioncomply/.env (chmod 600)
- Log locations:    journalctl -u arioncomply-* | /tmp/arioncomply-*.log

## Diagnostic surfaces (from surface 1-4 above)
[cross-links]

## Symptom → verification → fix
For every ARION-* error code, three lines:
- SYMPTOM: what the operator sees
- VERIFY:  one command that confirms this diagnosis
- FIX:    one command that resolves it (or file paths / SQL to inspect)

## Common queries
[Prewritten SQL/Cypher/curl queries for common ops tasks]

## Codebase orientation
Where to look for X, Y, Z if you need to modify behaviour.
```

This becomes the "system prompt" for anyone talking to Claude Code
about their deployment. Alongside the diagnostic bundle (surface 1),
Claude has the pattern-matching material it needs.

**Not** the human runbook (`docs/poc_install_guide.html`) — that's
narrative prose for a first-time operator. This is a reference
document for an AI that already knows how to grep and follow
pointers.

## What the four surfaces buy us together

**Support flow with a broken install**:
1. Customer runs `bash scripts/ops/diagnose.sh` → tarball
2. Customer emails/uploads tarball
3. Support opens a Claude Code session with:
   - `CLAUDE_DEPLOY_GUIDE.md` in context (system prompt)
   - Extracted tarball files on disk
4. Prompt: "Customer reports chat is slow. Look at their diagnostic
   bundle at ./arion-diag-*.tar.gz and diagnose."
5. Claude reads `deployment-status.json`, spots
   `otel_enabled: false`, checks `journal-api.txt` for cold-cache
   patterns, hits `error_catalog.html` for `ARION-RUNTIME-011`,
   recommends warmup + measurement.

Total time from tarball to answer: seconds. No SSH needed. No PII
leaves the customer's control (they chose what went in the tarball).

## Privacy invariants

- **Diagnostic bundle** never contains: evidence text, chat
  conversation content, LLM prompts/completions, user emails
  (beyond tenant admin), api_key raw values (only hashes/prefixes),
  posture NC descriptions (may contain proprietary tenant context).
- **Status endpoint** returns counts and versions only. No tenant
  names by default (behind an optional query param).
- **CLAUDE_DEPLOY_GUIDE.md** is generic — no tenant-specific info.

## Implementation shape

### 48'.b — bundle + catalog
```
scripts/ops/diagnose.sh                       ~200 LOC bash
docs/error_catalog.html                       ~15 initial codes
docs/memory/error_code_index.md               index of codes for future updates
```

### 48'.c — status endpoint
```
api_server.py + rag/admin/deployment_status.py    ~80 LOC
db/baseline: add 'admin:status' to scope check    (via CHECK constraint or code-side)
```

### 48'.d — CLAUDE_DEPLOY_GUIDE.md
```
/data/arioncomply/CLAUDE_DEPLOY_GUIDE.md          ~250 LOC markdown
install.sh: symlink or copy this file             1 LOC change
```

## What Ship 48 does NOT do

- **Automated remediation** — the fixes are prescriptive, not
  self-healing. Ship 49+ candidate.
- **Live remote debugging** — no SSH tunnel management, no
  reverse-connect debugger. Bundle-based is the boundary.
- **PII scanning of tenant data** — diagnostic bundle is
  hand-curated to exclude PII by design; no runtime scanner.
- **Cross-deployment fleet view** — every install is its own island.
  Multi-install fleet management is a much bigger arc (control
  plane, tenant tokens, per-install callback, etc).
- **OTel remote export** — if the customer allows it, they set
  `OTEL_ENABLED=1` + point at a collector. We don't operate one.

## Codified up-front decisions

1. **AI-first support model.** Every artefact designed for AI
   consumption; humans benefit as a side effect.
2. **Structured over unstructured.** JSON + column-format tables
   beat raw log tails. Diagnostic bundle files follow this rule.
3. **Privacy by omission.** Bundle contains only what's explicitly
   listed above. No "kitchen sink". Adding a new file to the bundle
   requires justification.
4. **Stable error codes.** Once assigned, `ARION-INSTALL-005`
   never gets reused. Deprecation via `[RETIRED]` marker in the catalog.

## Related

- Ship 47 (POC install path — the thing this diagnoses)
- Ship 44 (OTel — one existing observability surface)
- `docs/poc_install_guide.html` — human-first runbook (complements
  CLAUDE_DEPLOY_GUIDE.md's AI-first playbook)
