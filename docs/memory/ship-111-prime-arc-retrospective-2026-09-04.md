---
name: ship-111-prime-arc-retrospective-2026-09-04
description: Ship 111' arc — canonical env-var scheme + update-flow fix + deployment tracking, triggered by first Ship 110' PoC update
metadata:
  type: project
---

# Ship 111' — canonical env-var scheme + update-flow fix + deployment tracking

**Date:** 2026-09-04 (one day)
**Commits:** `ea431732` (a) → `b77da436` (b) → `3c90f7c2` (c) → `2b102a55` (d) → this doc (e)
**Trigger:** Ship 110' PoC deployment failed at install.sh's `prompt_pw ARION_OWNER_PW` in a headless SSH session — first-ever update on arionlabs-dr-01 hit a design gap that never surfaced during Ship 102'.f's fresh install.

## Motivation

Ship 102'.f delivered the golden-image install path and verified it end-to-end on a **fresh** arionlabs-dr-01 (2026-09-01, `wipe → git pull → install.sh`). Nobody had ever exercised the **update** path against an existing install. When Ship 110' shipped a schema migration + code that needed to reach the PoC, the update flow revealed three latent bugs:

1. **install.sh rejects sudo re-invocation.** Sanity check at line 108: `[[ "$EUID" -eq 0 ]] && fail`. Fine for interactive install, but the natural `ssh ... 'sudo bash deploy/install.sh'` SSH one-liner triggers it.
2. **install.sh doesn't read `.env` before prompting.** `prompt_pw` looks up the four secrets in shell env, sees empty, blocks on `read -s -p` waiting for a TTY that isn't there. Update hangs silently in the SSH session.
3. **Install-time and runtime env-var names differ.** install.sh: `OPENAI_KEY`, `NEO4J_PW`. Runtime `.env` + code: `OPENAI_API_KEY`, `NEO4J_PASSWORD`. Even if install.sh had read `.env`, the values wouldn't have matched the variable names it was looking for.

A fourth latent bug surfaced during audit: **5 runtime code sites read `POSTGRES_PASSWORD` which was never in the canonical `.env` template.** These have been silently broken since forever — they only worked when a developer manually exported `POSTGRES_PASSWORD` in their shell.

## Delivery summary

### 111'.a — Canonical env-var scheme in install.sh + .env (`ea431732`)

Consolidates install-time and runtime naming so `install.sh` internals match runtime canonical names 1:1.

| Concern | Retired | Canonical |
|---|---|---|
| OpenAI key | `OPENAI_KEY` | `OPENAI_API_KEY` |
| Neo4j pw | `NEO4J_PW` | `NEO4J_PASSWORD` |
| App-role pw | `ARION_APP_PW` (install-time only) | derived from `DATABASE_URL` at runtime |
| Owner-role pw | `ARION_OWNER_PW` | `ARION_OWNER_PW` (already canonical, now added to `.env`) |

New update-mode secret loader at step 0: if `.env` exists, read the four secrets directly (no name translation needed post-rename). App password parsed back out of `DATABASE_URL`'s `postgresql://user:pw@host` shape with %XX decoding. `prompt_pw` skips anything already set → SSH one-liner updates no longer hang.

`.env` writer at step 6 extended to:
- **Fresh install**: stash all 5 secrets (adds `ARION_OWNER_PW`) with replace-or-append semantics.
- **Update mode**: backfill missing `ARION_OWNER_PW` into an existing `.env`. Pre-111 installs get it on their next update; 111+ installs already have it.

`.env.example` gains an `ARION_OWNER_PW=CHANGE_ME` placeholder with a comment explaining owner vs app role distinction.

### 111'.b — Runtime `POSTGRES_PASSWORD` migration + grep guard (`b77da436`)

Five runtime code sites (customer-impacting) migrated:

| File | Sites | Role connected as | Migrated to |
|---|---|---|---|
| `rag/arion_graph.py` | 4 | `arioncomply_app` | `PGPASSWORD` |
| `rag/incident_materializer.py` | 1 | `arioncomply` | `ARION_OWNER_PW` w/ POSTGRES_PASSWORD fallback |

Plus 4 dogfood scripts (`scripts/ship{78,80,81,83}c_dogfood.py`) migrated for consistency — they were dev-box-only but had the same latent bug shape.

New `tests/test_env_var_conventions.py` — 3 static grep guards:
1. No runtime code (`rag/` + `api_server.py`) reads `POSTGRES_PASSWORD` as its primary source.
2. `install.sh` has the canonical `prompt_pw` set.
3. `.env.example` has `ARION_OWNER_PW=`.

Runs cheap (<100ms, no DB). Grandfathered list documents which historical scripts still read the legacy name and don't need to change (dev-box-only + docstrings that document the requirement).

### 111'.c — client_facts backfill for pre-Ship-110'.b tenants (`3c90f7c2`)

`scripts/dev/backfill_client_facts_for_existing_tenants.py` — retroactively creates `client_facts` rows for tenants provisioned before Ship 110'.b's initializer landed. Reuses `_initial_client_facts()` from `rag/onboarding/quickstart.py` so retrofitted rows are byte-shape-identical to what today's Quickstart produces.

Idempotent (only inserts for tenants without a row). First arc to depend on the `ARION_OWNER_PW`-in-`.env` canonical scheme — proves the Ship 111'.a scheme works end-to-end from a script (not just install.sh).

Verified on dev: `ArionComply External-API Test Tenant` went from 0 → 3 declared/derived columns. Arion demo state unchanged (12 declared columns intact from Ship 110'.a backfill).

### 111'.d — Deployment logs (dev-side + PoC-side) (`2b102a55`)

**Dev side** (committed to git):
- `docs/deployments/README.md` — convention doc + jq query examples
- `docs/deployments/arionlabs-dr-01.md` — first target's timeline in table + narrative form

Updated **before** ssh commands run. Reader = future Claude picking up the arc, or a human wanting deployment history. Cross-links to `ship-*-prime` retro memos.

**PoC side** (never committed — `.gitignore .deployment_log.jsonl`):
- `/data/arioncomply/.deployment_log.jsonl`

One JSON line per `install.sh` run appended by the new final step, before "Install complete" summary. Fields:

```json
{
  "ts": "2026-09-04T08:20:15Z",
  "git_sha": "b77da436",
  "git_branch": "main",
  "git_subject": "ship 111'.b — migrate runtime POSTGRES_PASSWORD sites + grep guard",
  "migrations_applied": ["schema_v112_client_facts_scoping_consolidation"],
  "invoker": "arionops",
  "invoker_sudo": "",
  "hostname": "arionlabs-dr-01",
  "install_sh_step_9": "already_running",
  "outcome": "GREEN"
}
```

Uses `jq` if available, sed-escape fallback otherwise. Migration accumulator wired into step 4 loop (`APPLIED_MIGRATIONS[]` bash array) — records what actually landed each run.

Query patterns documented in the README (`jq -r ... | tail -5` etc.). Feeds Ship 112'+ automated deploy scripts.

## Lessons codified

### Lesson 187 — Fresh-install paths and update paths are different

Ship 102'.f's fresh install verified end-to-end. Nobody exercised the update path until Ship 110' shipped, three days later. Result: 3 latent bugs surfaced at once. Fix: **treat install and update as separate first-class scenarios** — every future arc that touches `install.sh` should test both paths. Same rule for `.env` — the file's shape must survive **update runs**, not just first-write.

### Lesson 188 — Name drift between layers is silent debt

Runtime code, install-time script, and `.env` template were three separate name registries. Nothing surfaced the drift because everything worked in isolation. Then Ship 110' tried to read `.env` from install.sh and the drift bit immediately. **When multiple layers reference the same secret, use the same name in all of them.** Grep guard test (`tests/test_env_var_conventions.py`) prevents regression.

### Lesson 189 — Backfill scripts prove the canonical scheme

The Ship 111'.c backfill script is the first non-install.sh consumer of `ARION_OWNER_PW` from `.env`. Writing it also validated that the canonical scheme reaches beyond install.sh. Future admin scripts should follow the same shape: `_owner_conn()` helper reading `os.getenv("ARION_OWNER_PW")` with the URL fallback pattern.

### Lesson 190 — Deployment state needs to be tracked, not remembered

The Ship 110' PoC deployment required us to reconstruct "what's on arionlabs-dr-01" from conversation history + memory retros + a live SSH probe. That's brittle across Claude sessions. Fix: **two-log pattern** — dev-side markdown timeline (committed intent) + PoC-side JSONL (append-only actual). Future automated deploy scripts (Ship 112'+) will compute delta between the two.

### Lesson 191 — install.sh should log itself

Every `install.sh` run now writes a machine-parseable line to `.deployment_log.jsonl`. Zero-friction for operators (it just happens); future automation gets a structured event stream to reason about. Same pattern applies to other admin-privileged scripts — future refactor could apply this to `backfill_client_facts_*` and similar.

### Lesson 192 — Update-mode loader is a durable pattern

The Ship 111'.a update-mode loader (source .env, populate install-time vars if unset, prompt only for what's genuinely missing) generalizes. Any provisioning script that has both first-install and update modes should adopt this shape: **detect .env presence → source it → prompt as fallback**. Never assume TTY input in an SSH context.

## Deferred to Ship 112'+

1. **Automated deploy script** driven by both logs. Delta computation: dev intent vs PoC actual → ordered ship + verification between steps.
2. **JSONL retention/rotation** — the log grows unbounded. Not a problem for a couple years, but should tackle before it hits >1MB per box.
3. **Non-arionlabs-dr-01 deployment targets** — as new PoCs land, one new `docs/deployments/<host>.md` per box.
4. **Remaining `POSTGRES_PASSWORD` sites** — 15+ historical dev/curation scripts (Ship 80/81/82/90/91). Grandfathered in the guard test. Cleanup arc later if any become customer-facing.

## Related arcs

- [[ship-102-prime-arc-retrospective-2026-09-01]] — golden-image install path this arc extends
- [[ship-104-prime-arc-retrospective-2026-09-02]] — Quickstart flow; `create_first_tenant` predates Ship 110'.b initializer, hence the backfill script need
- [[ship-110-prime-arc-retrospective-2026-09-03]] — the arc that surfaced these gaps by needing to reach the PoC
- [[feedback-poc-context-low-security-friction]] — arionlabs-dr-01 is a self-owned PoC; ARION_OWNER_PW in `.env` is acceptable in this context

## PoC deployment status after Ship 111'

`arionlabs-dr-01` state at end of arc:
- **Code**: git head `b77da436` (Ship 111'.b) as of last SSH-driven update
- **Schema**: `schema_v112` applied via install.sh update-mode
- **`.env`**: `ARION_OWNER_PW` present (backfilled 2026-09-04)
- **Arion Networks s.r.o. client_facts**: not yet backfilled — pending Ship 111'.c script deployment

To land 111'.c on the PoC and verify 111'.d's PoC-side log fires:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash deploy/install.sh &&
  PYTHONPATH=. python3 scripts/dev/backfill_client_facts_for_existing_tenants.py &&
  sudo systemctl restart arioncomply-api &&
  echo "=== deployment log check ===" &&
  jq -c . .deployment_log.jsonl | tail -3
'
```

Expected new events after this ssh block:
1. `install.sh` appends one JSONL line (no new migrations — all already applied).
2. Backfill script inserts 1 client_facts row for Arion Networks s.r.o.
3. `docs/deployments/arionlabs-dr-01.md` gets its next timeline row (append manually next dev-side session).
