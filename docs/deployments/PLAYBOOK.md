# ArionComply — PoC deployment playbook

**Audience:** operator (Claude Code or human) installing / updating ArionComply on a customer VM.
**Companion:** [[CLAUDE_OPERATOR.md]] for the pre-install handoff protocol + safety guardrails; [[README.md]] in this directory for the deployment-log convention.

Two flows, both driven from the operator's Mac (or wherever your SSH keys live):

- **Fresh install** — brand-new customer box, zero ArionComply state. One SSH one-liner runs `install.sh` end-to-end.
- **Per-arc update** — existing customer box, apply one shipped arc. One SSH one-liner runs the arc's `scripts/ops/ship-N-poc-update.sh`.

Both flows use the **same invocation shape**: SSH into the box, run something bundled in git. No copy-paste of SQL. No secret shuffling. Everything reproducible.

---

## Prerequisites

Before touching a customer box, verify these are in place (see [[../customer_prep_checklist.html]] for the customer-side side):

| Requirement | Why |
|---|---|
| Ubuntu 24.04 host (VM or bare metal), ≥8 GB RAM, ≥60 GB disk | Runtime + Neo4j + Chroma need this shape |
| SSH from operator IP to `:22` on the box | Every interaction is SSH-driven |
| Non-root user with passwordless sudo (typically `arionops`) | `install.sh` refuses to run as root; internal `sudo` calls escalate for postgres/systemd only |
| Operator's SSH public key in `~/.ssh/authorized_keys` on the box | Enables key-based auth (`~/.ssh/arion_operator_ed25519` is our convention) |
| `git` installed on the box | For pulling code + tracking version |
| `git-lfs` installed on the box | Chroma golden tar is LFS-tracked (147 MB) |
| Repo already cloned to `/data/arioncomply` | Everything works from that path |

---

## Fresh install (one-time per box)

### 1. Clone the repo

Operator runs from their Mac:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  sudo mkdir -p /data && sudo chown arionops:arionops /data &&
  cd /data &&
  git clone https://github.com/jmkamula/RAG.git arioncomply &&
  cd arioncomply &&
  git lfs install &&
  git lfs pull
'
```

Verify LFS hydrated the Chroma tar:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  ls -la /data/arioncomply/db/baseline/chroma_prebuilt.tar.gz
'
```

If the tar is <1 MB, it's still an LFS pointer. Rerun `git lfs pull`. Real size is ~147 MB.

### 2. Run install.sh (interactive)

`install.sh` prompts for 4 secrets on a fresh install (Ship 111'.a — reads them from `.env` on update mode; fresh install has no `.env` yet):

- `ARION_OWNER_PW` — Postgres owner role password
- `ARION_APP_PW` — Postgres app role password (RLS-scoped runtime pool)
- `NEO4J_PASSWORD` — Neo4j password
- `OPENAI_API_KEY` — OpenAI key (or leave blank if using another provider)

Run interactively (not in an SSH one-liner — needs TTY for password input):

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host>
# Once inside the shell:
cd /data/arioncomply
bash deploy/install.sh
```

Store the four passwords in your password manager or `handback.md` (see [[CLAUDE_OPERATOR.md]] §5). Ship 111'.a stashes them in `/data/arioncomply/.env` so update mode reads them automatically.

**What install.sh does** (9 phases):

| # | Phase | Notes |
|---|---|---|
| 0 | Sanity checks | Refuses EUID=0; reads `.env` if present (update mode auto-skips prompts) |
| 1 | System packages | Installs postgresql-16, python3, curl, lsof, git via apt |
| 2 | Neo4j 5 | Install + set initial password + verify auth |
| 3 | Postgres roles + databases + extensions | 2 databases (`arioncomply_compliance`, `arioncomply_sessions`) + 2 roles (`arioncomply` owner, `arioncomply_app` RLS-scoped) |
| 4 | Schema baseline + curator seed | Loads `schema_baseline.sql` (pg_dump snapshot up to Ship 114') + `seed_curator_data.sql` (curator tables like `templates`, `topic_leaves`) + `schema_sessions_baseline.sql`. Bootstraps `schema_migrations` tracker + applies any un-applied `schema_v*.sql` |
| 5 | Python dependencies | `pip install -r deploy/requirements.txt` |
| 6 | `.env` from template | Writes secrets from prompts (or update-mode re-appends any missing) |
| 7 | Chroma dir + systemd units | Extracts `chroma_prebuilt.tar.gz` (147 MB compressed / 263 MB raw, all 9 collections) + installs systemd units for `arioncomply-{api,chroma,sweep}` |
| 8 | Neo4j graph load | Loads `neo4j_baseline.json` via `load_neo4j_baseline.py` (8148 nodes / 14378 relationships) |
| 9 | Start the API | `systemctl start arioncomply-api` + wait 60s for `/docs` to respond |

Also writes one line to `/data/arioncomply/.deployment_log.jsonl` (Ship 111'.d).

### 3. Post-install verification

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  echo "=== systemd status ==="
  sudo systemctl status arioncomply-{api,chroma,sweep.timer} --no-pager | head -20
  echo
  echo "=== API health ==="
  curl -sf http://127.0.0.1:8080/docs > /dev/null && echo OK
  echo
  echo "=== deployment log ==="
  jq -c . /data/arioncomply/.deployment_log.jsonl
'
```

Everything should be `active (running)`. First line in `.deployment_log.jsonl` should show `outcome: GREEN`.

### 4. Grant browser access (SSH tunnel)

From your Mac:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 -L 8080:127.0.0.1:8080 arionops@<host>
# Then open http://localhost:8080/ in your browser
```

You'll see the **Quickstart overlay** (Ship 104') — first tenant provisioning happens in the browser, no CLI needed.

### 5. Register the deployment

Create a new `docs/deployments/<host>.md` markdown following [[README.md]] convention:

```
docs/deployments/customer-x-poc-01.md
```

Header + first row of the deployment record table. Commit + push. Future updates flip this row to `GREEN` / `RED` per operation.

---

## Per-arc update (every ship that touches the customer)

### The one-liner

Same shape for every arc going forward — only the script name changes:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-<N>-poc-update.sh
'
```

Replace `<N>` with the ship number of what you're deploying.

### What each `ship-N-poc-update.sh` does (convention)

Each per-arc script (Ship 113'.d established the convention) runs **on the customer box** as `arionops` and does:

1. `bash deploy/install.sh` — applies any new `schema_v*.sql` migrations idempotently, reads `.env` in update mode (Ship 111'.a) so no prompts.
2. `sudo systemctl restart arioncomply-api` — pick up new Python + static HTML.
3. Health probe with retry.
4. **Arc-specific verification queries** — the delta between "what this arc changed" and "what we can measure":
   - New schema migrations in tracker
   - New columns / tables exist
   - Any post-deploy backfill scripts run
   - Current tenant state reflects the change
5. Tail last 3 lines of `.deployment_log.jsonl` — install.sh appends one line per run.

### Update the dev-side deployment log after

After a successful deploy, from your dev checkout:

```bash
# Edit docs/deployments/<host>.md — flip the row to GREEN + note anything surprising
git add docs/deployments/<host>.md
git commit -m "deployment log: <host> Ship N' GREEN"
git push
```

This closes the loop — the dev-side markdown reflects PoC-side reality.

### If the update fails

`install.sh` fails loud with `ERROR: ...` and exits non-zero. `set -e` in the ship script propagates. Nothing partial gets restarted.

Recovery:
1. Read the error output.
2. Fix the underlying issue (usually a schema migration edge case).
3. Rerun the ship script — everything already-applied is a no-op.

Rollback (if the code is bad, not the schema):

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  cd /data/arioncomply &&
  git reset --hard HEAD~1 &&
  sudo systemctl restart arioncomply-api
'
```

Schema stays applied — the additive-column convention means old code that doesn't know about new columns just doesn't read them. Bad Python restored to previous version.

---

## Golden images — what they are, when refreshed

Golden images (Ship 102'.a-f) replace the incremental loader chain that would otherwise replay every Postgres migration + reload every Neo4j fixture + reindex every Chroma collection. Fresh installs load from golden = ~2 minutes vs. ~90 minutes previously.

**Where they live**: `db/baseline/` directory. Committed to git; `.tar.gz` files use LFS.

| File | Contents | Refreshed by | Refresh trigger |
|---|---|---|---|
| `schema_baseline.sql` | `pg_dump --schema-only` of `arioncomply_compliance` | Pre-commit hook (Ship 102'.d) | Any staged change under `db/schema_v*.sql` or `enrichment/database/` |
| `schema_sessions_baseline.sql` | Same for `arioncomply_sessions` | Pre-commit hook | Same trigger |
| `seed_curator_data.sql` | `pg_dump --data-only` of curator tables (templates, topic_leaves, topics, enricher_cache, fact_source_config, retention_policies) | Pre-commit hook | Any staged change under `db/curator_seed/`, `enrichment/database/`, or curator tables |
| `neo4j_baseline.json` | Business-key export of every Neo4j label + relationship (KEY_MAP-driven) | Pre-commit hook | Any staged change under `enrichment/documents/*.py` (framework catalog sources) |
| `chroma_prebuilt.tar.gz` | Compressed dump of all 9 Chroma collections (~147 MB) | **Manual** (pre-commit is warn-only) | Chroma content changes are rare + expensive to rebuild (~90s + ~$2 OpenAI). Rebuild only when you deliberately re-embed. |
| `chroma_prebuilt.meta.json` | SHA-256 + row counts for verification | Manual, alongside the tar | Same as tar |
| `load_neo4j_baseline.py` | The single loader replacing the old 5-loader chain | Code, not data | Rarely — Ship 102'.b defined it |

### Auditing golden currency (before shipping a new arc)

```bash
cd /data/arioncomply

# Are all staged changes reflected in golden?
git status db/baseline/  # should be clean after pre-commit hook fires

# schema_baseline includes latest schema_v* content?
grep -oE "schema_v[0-9]+[a-z_]*" db/baseline/schema_baseline.sql | sort -u | tail -5
# Should match the highest schema_v*.sql file in db/

# Neo4j baseline sanity
python3 -c "import json; d=json.load(open('db/baseline/neo4j_baseline.json')); print(f'nodes: {len(d[\"nodes\"])} rels: {len(d[\"relationships\"])}')"
# Expected: 8148 nodes / 14378 relationships (Ship 102'.b baseline, stable through Ship 114')

# Chroma tar sanity
ls -la db/baseline/chroma_prebuilt.tar.gz
# Expected size ~147 MB. <1 MB = LFS pointer, not the real blob
cat db/baseline/chroma_prebuilt.meta.json
# Should list all 9 collections + their row counts + SHA-256
```

### Rebuilding a stale golden

**Postgres schema + seed**: touch any file under `db/schema_v*.sql` (add a whitespace-only change), stage it, `git commit`. Pre-commit hook fires, rebuilds `schema_baseline.sql` + `seed_curator_data.sql`, restages them. Then unstage the whitespace change.

Alternative direct:
```bash
bash scripts/build_pg_baseline.sh
git add db/baseline/schema_baseline.sql db/baseline/seed_curator_data.sql
git commit -m "rebuild pg golden"
```

**Neo4j**: touch any file under `enrichment/documents/*.py`, or run directly:
```bash
bash scripts/build_neo4j_baseline.sh
git add db/baseline/neo4j_baseline.json
git commit -m "rebuild neo4j golden"
```

**Chroma** (rare — costs ~$2 OpenAI + 90s):
```bash
bash scripts/build_chroma_baseline.sh
git add db/baseline/chroma_prebuilt.tar.gz db/baseline/chroma_prebuilt.meta.json
git commit -m "rebuild chroma golden"
git lfs push origin main  # LFS blob push
```

### If a customer box is missing a golden

install.sh's safe-cutover pattern (Ship 102'.f) detects this and falls back to the incremental loader chain — schema_v*.sql migrations + 5 Neo4j loaders + `scripts/reindex_all.py` for Chroma. Slower (~90 min) but works even without the golden files.

---

## Recovery scenarios

### API won't start after update

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  journalctl -u arioncomply-api -n 100 --no-pager
'
```

Usually a Python exception on startup. Fix the code, push, rerun the ship script.

### Schema migration fails

`install.sh` exits with `ERROR: migration schema_vN failed — inspect: sudo -u postgres psql -d arioncomply_compliance -f <path>`. Run the suggested inspect command, fix the SQL (usually a constraint violation on existing data), commit the fix, rerun.

### Tenant state got corrupted

For arionlabs-dr-01 shape issues, we've established two backfill scripts (Ship 111'.c + Ship 114'.a). Same pattern for future data-cleanup: write a `scripts/dev/backfill_<what>.py` that's idempotent + uses `ARION_OWNER_PW` (canonical scheme).

### Full rollback to a previous ship

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  cd /data/arioncomply &&
  git reset --hard <sha-of-previous-ship> &&
  sudo systemctl restart arioncomply-api
'
```

Schema stays applied (additive-only convention). Code reverts. If a schema change was actually harmful (rare — we haven't hit this yet), a manual `DROP COLUMN` on the customer box is safe.

### Full box wipe + reinstall

Ship 102'.f verified this on arionlabs-dr-01:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
  # Stop services + drop databases
  sudo systemctl stop arioncomply-{api,chroma,sweep.timer}
  sudo -u postgres dropdb arioncomply_compliance
  sudo -u postgres dropdb arioncomply_sessions
  sudo rm -rf /data/arioncomply/chroma_db
  # Wipe Neo4j
  sudo systemctl stop neo4j
  sudo rm -rf /var/lib/neo4j/data/{databases,transactions,dbms}
  sudo systemctl start neo4j
  # Now rerun install.sh — fresh state
  cd /data/arioncomply && git pull && bash deploy/install.sh
'
```

Interactive prompts return (no `.env` to read from). Store new passwords.

---

## Convention: per-arc deploy scripts (`scripts/ops/ship-N-poc-update.sh`)

Every ship that touches the customer box gets its own script. Established by Ship 113'.d, hardened by Ship 114'.d. Design principles:

1. **Runs on the customer VM** as `arionops` (or whoever has passwordless sudo). Not on the operator's Mac.
2. **git pull is NOT in the script** — the operator's SSH block does `git pull` first (must, because the script itself is fetched by the pull).
3. **Verification is arc-specific** — checks what the arc introduced (new columns, new endpoints, new backfill run). Generic checks (API health, deployment log tail) at the end.
4. **Order matters** — schema first (via install.sh), API restart second, data-mutation scripts third, verification last.
5. **Idempotent** — re-running the script is safe. Every step no-ops if already applied.
6. **Fails loud** — `set -euo pipefail` at the top. If any step fails, subsequent steps don't run.

### Template (copy for a new arc)

```bash
#!/usr/bin/env bash
#
# scripts/ops/ship-<N>-poc-update.sh
# One-line summary of what this arc changes.
#
# Invocation from operator's Mac:
#   ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> '
#     cd /data/arioncomply &&
#     git pull &&
#     bash scripts/ops/ship-<N>-poc-update.sh
#   '

set -euo pipefail

ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
cd "$ARION_ROOT"

echo "=== 1. install.sh (applies schema_v<N> idempotently) ==="
bash deploy/install.sh 2>&1 | tail -25

echo
echo "=== 2. Restart arioncomply-api ==="
sudo systemctl restart arioncomply-api

echo
echo "=== 3. Wait for API + probe /docs ==="
for i in 1 2 3 4 5 6 7 8; do
    if curl -sf --max-time 3 http://127.0.0.1:8080/docs > /dev/null; then
        echo "API up after $((i*3))s"; break
    fi
    sleep 3
    if [[ "$i" -eq 8 ]]; then
        echo "WARN: API did not respond within 24s"
        exit 1
    fi
done

# ── Arc-specific verification queries below ──
# Replace with:
#  · Schema tracker check for this arc's migration
#  · Column / table existence checks
#  · Any backfill scripts (like Ship 111'.c or 114'.a)
#  · Tenant-state probe

echo
echo "=== N. Deployment log — last 3 entries ==="
if [[ -f .deployment_log.jsonl ]]; then
    jq -c . .deployment_log.jsonl | tail -3
fi

echo
echo "=== Ship <N>' deployment complete ==="
```

Commit the script in the same arc that ships the code. Deploy pattern from the operator's Mac never varies.

---

## The two logs — how state is tracked (Ship 111'.d)

Two complementary logs so PoC state is persistent + machine-parseable across sessions:

**Dev side** (`docs/deployments/<host>.md`, committed to git):
- Timeline table + narrative context + credential vault reference
- Updated **before** ssh commands run (planned action) and **after** they succeed (flip to GREEN)
- Reader: future Claude picking up the arc, human wanting deployment history

**PoC side** (`/data/arioncomply/.deployment_log.jsonl`, NOT committed):
- One JSON line per `install.sh` run (appended automatically)
- Fields: `ts`, `git_sha`, `git_branch`, `git_subject`, `migrations_applied[]`, `invoker`, `invoker_sudo`, `hostname`, `install_sh_step_9`, `outcome`
- Machine-parseable — future automated deploy scripts will diff dev-side intent against PoC-side actual

### Query patterns

```bash
# All entries, pretty-printed
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> \
    'jq . /data/arioncomply/.deployment_log.jsonl'

# Most recent 5 runs, compact
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> \
    "jq -r '[.ts, .git_sha, (.migrations_applied|length|tostring)+\" migs\", .outcome] | @tsv' \
     /data/arioncomply/.deployment_log.jsonl | tail -5"

# Any RED outcomes ever
ssh -i ~/.ssh/arion_operator_ed25519 arionops@<host> \
    "jq -c 'select(.outcome != \"GREEN\")' /data/arioncomply/.deployment_log.jsonl"
```

---

## Where things are

| Component | Path |
|---|---|
| Fresh installer | `deploy/install.sh` (9 phases, idempotent) |
| Golden images | `db/baseline/` (Ship 102') |
| Per-arc deploy scripts | `scripts/ops/ship-<N>-poc-update.sh` (Ship 113'.d convention) |
| Data-fix scripts (as needed) | `scripts/dev/backfill_<what>.py` |
| Diagnostic bundle producer | `scripts/ops/diagnose.sh` (Ship 48') |
| Remote diagnose wrapper | `scripts/ops/remote_diagnose.sh` (Ship 100') |
| Systemd unit templates | `ops/systemd/arioncomply-{api,chroma,sweep}.{service,timer}` |
| Operator handbook (pre-install phase) | `CLAUDE_OPERATOR.md` |
| Deployment-log convention | `docs/deployments/README.md` (Ship 111'.d) |
| PoC-side deployment log (on customer VM) | `/data/arioncomply/.deployment_log.jsonl` |
| This playbook | `docs/deployments/PLAYBOOK.md` (you're reading it) |

---

## Ship history reference (deploys with per-arc scripts)

| Arc | Script | Landed on arionlabs-dr-01 |
|---|---|---|
| Ship 113' | `scripts/ops/ship-113-poc-update.sh` | 2026-09-04 |
| Ship 114' | `scripts/ops/ship-114-poc-update.sh` | 2026-09-04 |

Future arcs append here. The two logs (dev-side markdown + PoC-side JSONL) stay authoritative for actual state.
