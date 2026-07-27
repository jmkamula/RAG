---
name: ship-47-prime-arc-retrospective-2026-07-27
description: "Ship 47' arc closer — POC install path complete. One-command install (deploy/install.sh) takes a fresh Ubuntu 22.04+ VM to running ArionComply in ~15 min: apt packages, Neo4j apt repo, Postgres role/DB bootstrap, schema baseline + curator seed, Python deps, .env from template, Chroma + API systemd, Neo4j graph load. Tenant provisioning via create_tenant.py. Full HTML runbook + VM appliance design memo also shipped."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 47' arc retrospective — POC install path complete.

## What shipped

5 sub-arcs + retro over a single Sunday session (2026-07-27). Fresh
VM → running ArionComply in one command; fresh tenant → issued API
key in a second.

| Sub-arc | Delivery | Commit |
|---|---|---|
| 47'.a | Design memo — baseline strategy (pg_dump vs sequential replay) | 213fe4e |
| 47'.b | schema_baseline.sql (8721 LOC) + seed_curator_data.sql + schema_sessions_baseline.sql | 878fa10 |
| 47'.c | deploy/install.sh + postgres_preamble.sql + requirements.txt + .env.example | b4ef596 |
| 47'.d | scripts/dev/create_tenant.py | acc2b26 |
| 47'.e | poc_install_guide.html + VM appliance design memo + cross-linked docs | a3d5226 |
| **47'.f** | **This retro** | pending |

## Delivery velocity

- Session length: ~5 hours (afternoon into evening)
- Design → measurement → implementation → verification → docs, on
  every sub-arc
- Each sub-arc committed + pushed independently. Zero mid-arc rollbacks.

## The three commands

For a customer with a fresh Ubuntu 22.04+ VM:

```bash
git clone https://github.com/jmkamula/RAG.git /data/arioncomply
cd /data/arioncomply
bash deploy/install.sh
```

Prompts for four passwords (Postgres × 2, Neo4j, OpenAI API key) OR
reads them from env with `--yes`. ~15 min to a running system. Then:

```bash
PYTHONPATH=. python3 scripts/dev/create_tenant.py \
    --name "Customer Corp" --industry technology
```

Prints an API key ONCE (SHA-256 hashed at rest). Customer is running.

## Key decisions

### Baseline SQL, not sequential migrations
92 migration files (schema_v1 → schema_v90) worked when applied
incrementally over ~90 arcs; never tested against an empty DB in
order. Baseline via `pg_dump --schema-only` captures the exact live
schema shape. Historical migrations retained under `db/schema_v*.sql`
for provenance; not applied on new installs.

### Curator seed data split
Six tables carry portable-across-tenants reference data
(standards + standard_relationships + retention_policies +
ref_prefixes + ref_sequences + roles = 54 rows). Everything else
per-tenant, seeded on first `create_tenant.py` invocation, or
runtime-populated. Clean split makes install idempotent and keeps
per-tenant data out of the reproducibility surface.

### install.sh is idempotent by design
Every stage checks existing state before acting: skip apt installs
if packages present; skip Neo4j apt repo if binary in PATH; skip
schema apply if compliance DB has ≥1 table; skip systemd service
start if port already bound. Safe to re-run.

### Tenant provisioning uses the schema-owner role
`create_tenant.py` connects as `arioncomply` (owner) not
`arioncomply_app` (RLS-scoped). Tenants INSERT trips the RLS policy
on the tenants table before the `app.tenant_id` context can be set.
Owner role bypasses RLS for exactly this bootstrap case; all other
INSERTs run through the app role via `set_config('app.tenant_id')`.

### API keys are SHA-256 hashed, printed once
`create_tenant.py` generates a random `arion_<32-hex>` key, hashes
with SHA-256, prints the raw key at the very end. No way to
retrieve it later. Standard "we don't store your credentials" idiom.

## Codified 3 lessons

### 1. psql variable interpolation doesn't work inside DO blocks
`:'var'` substitution happens in the outer psql text stream before
the query is sent to the server. Inside a `DO $$ ... $$` PL/pgSQL
block, the `$$ ... $$` body is a single string literal — psql
doesn't interpolate inside it. Postgres executes it verbatim, sees
`:'var'` as a syntax error, and fails.

**Correct idiom**: `SELECT format('CREATE ROLE ... PASSWORD %L', :'var') \gexec`
— psql substitutes in the SELECT text, format() escapes the value
safely, `\gexec` runs the resulting string as SQL.

Caught during preamble validation; fixed in postgres_preamble.sql.

### 2. `pip freeze` on a Mac dev env leaks AppleInternal paths
The pre-existing `requirements.txt` had entries like:

```
future @ file:///AppleInternal/Library/BuildRoots/.../future-0.18.2-py3-none-any.whl
```

Not installable on Ubuntu. Regenerating on the actual target OS via
`pip freeze` on the deployment VM produces a clean requirements.txt
(also filtered Ubuntu-system leaks like `python-apt`).

**Rule**: freeze requirements on the target OS, not the dev OS.
Better still: switch to pyproject.toml with pinned direct-deps only.

### 3. Baseline schema pg_dump captures things the migrations forgot
The live DB has drift accumulated across ~90 arcs — column-comment
edits, trigger tweaks, index rebuilds via
`REINDEX CONCURRENTLY` — that aren't necessarily represented in any
single `schema_v*.sql` file. `pg_dump --schema-only` captures the
actual current shape, which is what the running API expects.

**Rule**: for POC install purposes, treat the live production
schema as authoritative. Migrations are for evolving it; the
baseline is for standing up new instances.

## What Ship 47 did NOT do

- **VM appliance images** (Packer VHD/AMI/OVA) — design memo written
  (`ship_47_prime_e_vm_appliance_design_2026_07_27.md`); implementation
  deferred to Ship 48+ once we have ≥5 customer installs to feel the
  first-boot install-time cost
- **Cloud-init user-data templates** — sketched in the appliance memo
  as the recommended next step (option 1 in that memo). ~1 day work
  when a customer needs it.
- **Terraform module** — deferred; wraps cloud-init when we need it
- **Marketplace listings** — deferred to product-mature phase
- **Container images (Docker/Podman)** — deferred; systemd approach
  is fine for POC
- **OIDC / SSO** — static API keys per Ship 46 shape; enterprise
  SSO deferred
- **TLS / reverse proxy** — SSH tunnel is fine for POC access; TLS
  layer deferred
- **Backup / restore automation** — deferred; POC customers add
  pg_dump timer if they care
- **Chroma index pre-bake in the install** — installer notes that
  first API startup does the reindex; ~5-10 min at first chat. Could
  be pre-baked into a Packer image later.
- **`db/schema_v91.sql` and beyond** — new schema changes now
  append against the baseline; the pattern is documented in the
  Ship 47'.a design memo but the first v91 hasn't landed yet.

## Deferred / follow-on candidates

### Ship 48 candidates
- **Cloud-init templates** (deploy/cloud-init/user-data.tpl + one
  Terraform snippet per major cloud). Makes appliance-style deploy
  real without image baking.
- **Chroma index pre-bake** — snapshot the Chroma dir post-install
  with a fresh reindex done; ship as an optional download. Saves
  10 min on first chat.
- **A `--dry-run` on install.sh** — print what it would do without
  making changes. Common Ansible-style ask.

### Longer-term (Ship 49+)
- Packer pipeline for baked images (VHD/AMI/OVA)
- OIDC identity integration (Entra ID / Okta / etc)
- TLS via Caddy or Nginx front-door with LetsEncrypt or corporate CA
- Backup / restore playbooks
- Multi-tenant onboarding UX inside the SPA
- pyproject.toml migration replacing requirements.txt

## Deployment shape locked in for POC

From Ship 46's deployment discussion:

> Shape C (on-prem VM) + OpenAI (or Azure OpenAI in their tenant)

Ship 47 realises exactly that shape. Any customer with an Ubuntu VM
+ an OpenAI API key can now run the three-command install. VM lives
anywhere they want (their cloud, our cloud, on-prem, laptop VM).
Data stays where the VM lives.

## Related

- [[ship-47-prime-a-poc-install-baseline-design-2026-07-27]] — the
  design memo Ship 47 executed
- [[ship-47-prime-e-vm-appliance-design-2026-07-27]] — the appliance
  design memo (deferred implementation)
- [[ship-46-prime-b-prioritised-backlog-2026-07-26]] — the backlog
  that flagged POC install as a Now-priority item
- `db/baseline/schema_baseline.sql` — the install target
- `deploy/install.sh` — the installer
- `scripts/dev/create_tenant.py` — the tenant provisioning helper
- `docs/poc_install_guide.html` — the human-readable runbook
