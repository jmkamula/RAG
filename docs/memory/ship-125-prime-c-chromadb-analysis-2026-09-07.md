---
name: ship-125-prime-c-chromadb-analysis-2026-09-07
description: Ship 125'.c — CVE analysis for chromadb 1.5.9; 4 CVEs, none apply to our deployment (localhost-only + no tenancy + no trust_remote_code + no RBAC)
metadata:
  type: project
---

# Ship 125'.c — chromadb 1.5.9 CVE analysis

**Date:** 2026-09-07
**Trigger:** Ship 124'.c's pip-audit surfaced 4 chromadb CVEs. Fix version listed as blank — chromadb 1.5.9 is the latest release; no fix available upstream.
**Verdict:** None of the 4 CVEs apply to our deployment. `--ignore-vuln` entries retained in `scripts/ci/security_scan.sh` with per-CVE rationale. Re-review triggered by (a) upstream ships a fix, or (b) our deployment model changes.

## The 4 CVEs

Fetched via `pip-audit -r requirements.txt --no-deps --desc on`:

### PYSEC-2026-311 — pre-authentication code injection

> A pre-authentication, code injection vulnerability in version 1.0.0 or later of the ChromaDB Python project allows an unauthenticated attacker to run arbitrary code on the server by sending a malicious model repository and `trust_remote_code` set to true in the `/api/v2/tenants/{tenant}/databases/{db}/collections` endpoint.

**Applies to us: NO.** Two independent conditions must be met:
1. Attacker reaches `/api/v2/...` HTTP endpoint — our Chroma binds to `127.0.0.1:8000` under systemd (`arioncomply-chroma.service`), not exposed to any network. Only the local API process on the same VM can reach it.
2. `trust_remote_code=true` on the collection create call — we never set this. All 9 collections are created via `scripts/build_must_index.py`, `scripts/index_*.py`, and `scripts/reindex_all.py`; none pass `trust_remote_code=true`. Default is `false` in chromadb.

Both conditions are false. Attack vector doesn't exist in our deployment.

### CVE-2026-45830 — cross-tenant read/write

> A lack of authorization validation in version 0.4.17 or later of the ChromaDB Python project allows any authenticated users to arbitrarily read, write, update, or delete data in any tenant's collection regardless of which tenant they belong to.

**Applies to us: NO.** Requires ChromaDB's tenancy features. We use the single-database, single-tenant-per-collection model:
- All collections live in the default database (`default_database`).
- Collections are keyed by purpose (e.g. `musts_arioncomply`, `iso27001_2022`, `edpb_guidelines`), not by tenant.
- Per Ship 122'.b analysis: Chroma holds compliance catalog (public MUSTs, EDPB guidelines) — no tenant PII in Chroma. Even if cross-tenant access existed conceptually, there's no tenant data to leak.

### CVE-2026-45833 — authenticated code injection

> A code injection vulnerability in version 0.4.17 or later of the ChromaDB Python project allows an authenticated attacker to run arbitrary code on the server by sending a malicious model repository and `trust_remote_code` set to true in the `/api/v2/tenants/default_tenant/databases/default_database/collections/{collection_id}` if they have the `UPDATE_COLLECTION` permission.

**Applies to us: NO.** Same two conditions as PYSEC-2026-311:
1. Network exposure of `/api/v2/...` — Chroma is localhost-bound.
2. `trust_remote_code=true` in the update — we never set it.

Additionally requires `UPDATE_COLLECTION` permission, which requires the auth provider to be enabled (see next CVE).

### CVE-2026-45831 — RBAC cross-tenant permission bypass

> The `SimpleRBACAuthorizationProvider` authorization provider in versions 0.5.0 or later of the ChromaDB Python project evaluates whether a user holds a given permission but never checks which tenant, database, or collection that permission applies to allowing users to perform cross tenant actions.

**Applies to us: NO.** We don't use `SimpleRBACAuthorizationProvider`. Our Chroma runs with default auth config (none), and our access-control model is at the ArionComply API layer:
- Chroma is not accessible from outside `127.0.0.1`.
- All Chroma calls come from `rag/intake/must_embedding_lookup.py`, `rag/casefile/digest.py`, `scripts/build_must_index.py`, `scripts/index_*.py`.
- Every one of these runs inside the API process (which itself gates on `require_api_key` before executing any tenant-scoped read).

## Structural conditions we depend on

The `--ignore-vuln` decisions hold as long as ALL of these remain true:

1. **Chroma binds only to `127.0.0.1`**. Verifiable via `sudo systemctl status arioncomply-chroma` + `ss -tlnp | grep 8000`. If we ever expose Chroma to another host (multi-node deploy, container-to-container network), PYSEC-2026-311 + CVE-2026-45833 become live.
2. **No `trust_remote_code=true` anywhere**. Verifiable via `grep -rn "trust_remote_code" /data/arioncomply/rag /data/arioncomply/scripts` — must return zero hits (or only False values). Same PYSEC-2026-311 + CVE-2026-45833 apply if this changes.
3. **No tenancy features used**. Verifiable via checking that `chromadb.HttpClient(...)` + `PersistentClient(...)` calls don't pass `tenant=` / `database=` args or use non-default values. CVE-2026-45830 becomes live if we adopt tenancy.
4. **`SimpleRBACAuthorizationProvider` not configured**. Verifiable via chromadb env vars: `CHROMA_SERVER_AUTH_PROVIDER` unset / not `SimpleRBACAuthorizationProvider`. CVE-2026-45831 becomes live if RBAC is enabled without full tenant/database/collection scoping.

## Verification commands (for future re-review)

```bash
# Chroma bind check
ss -tlnp 2>/dev/null | grep 8000
# Expected: 127.0.0.1:8000 only, NOT 0.0.0.0:8000 or a public IP

# trust_remote_code sweep
grep -rn "trust_remote_code" /data/arioncomply/rag /data/arioncomply/scripts
# Expected: no hits, OR only hits with `=False`

# Tenancy config sweep
grep -rn "tenant=\|database=" /data/arioncomply/rag/intake/must_embedding_lookup.py \
  /data/arioncomply/rag/casefile/digest.py /data/arioncomply/scripts/index_*.py
# Expected: no non-default tenant/database args

# Auth provider check (env vars set on the systemd unit)
sudo systemctl cat arioncomply-chroma | grep -iE "auth|rbac"
# Expected: no CHROMA_SERVER_AUTH_PROVIDER or set to something other than SimpleRBACAuthorizationProvider
```

If any of these change, re-open Ship 125'.c and either upgrade or add compensating controls.

## Re-review triggers

Reopen this analysis when ANY of the following:

1. **Upstream ships a fix** — chromadb releases 1.5.10+ or 2.x with these CVEs marked resolved. Verify + upgrade + drop the `--ignore-vuln` entries.
2. **Chroma bind changes from localhost-only** — any multi-host or container network configuration change.
3. **Tenancy features adopted** — if we start using per-tenant Chroma databases or collections (relevant if we ever embed tenant-specific documents).
4. **Auth provider enabled** — if we configure any `CHROMA_SERVER_AUTH_PROVIDER`.
5. **Deploy model changes** — moving Chroma to a shared/managed instance instead of embedded systemd.

## Related arcs

- [[ship-124-prime-arc-retrospective-2026-09-07]] — parent arc that surfaced the CVEs
- [[ship-122-prime-arc-retrospective-2026-09-05]] — Chroma tenant-scoping analysis (no tenant PII in Chroma; catalog only)
- [[ship-102-prime-arc-retrospective-2026-09-01]] — Chroma golden-image cutover; documents the systemd + localhost deployment

## Deferred

- **Ship 125'.c doesn't change anything on the PoC** — no code change, no schema, no deploy. Purely a documented risk-analysis decision + comment on the `--ignore-vuln` entries.
- Automated verification of the 4 structural conditions above could be added to `scripts/ci/check_forbidden_patterns.sh` as a chromadb-config drift guard. Small arc; not urgent.
