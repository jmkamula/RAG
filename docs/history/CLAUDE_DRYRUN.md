# CLAUDE_DRYRUN.md

**Mission brief for Claude Code running the Ship 48 dry-run end-to-end on a fresh Azure VM.**

Read this file first. Then read `CLAUDE.md` for codebase orientation and `CLAUDE_DEPLOY_GUIDE.md` for troubleshooting reference. The HTML runbook (`docs/dry_run_azure_playbook.html`) is the human-oriented version of Phase 1 + Phase 2 below — helpful for cross-reference, but this file is your authoritative task spec.

---

## 1. Mission

You are Claude Code running on a **fresh Azure D4s v3 VM** (`ariondryrun`, Ubuntu 24.04, West Europe). Your job is to execute a **Ship 48 dry-run validation** end-to-end and report findings.

**What green looks like at the end of the run:**

- ArionComply installed and running via `deploy/install.sh` (systemd services active, ports bound, admin/status endpoint returns 200 with all four services healthy)
- One tenant provisioned via `scripts/dev/create_tenant.py` (API key issued)
- Chat + upload smoke tests pass
- Four Ship 48 break/diagnose scenarios executed; for each, `scripts/ops/diagnose.sh` bundle was produced and a Claude session (this one or a fresh one) diagnosed the issue from the bundle alone in under 30 seconds
- A final report at `/data/arioncomply/dry_run_report.md` summarising phases, timings, deviations, and any bugs found

**What red looks like:**

- Any install step blocks and you can't resolve it after two attempts + reading `docs/error_catalog.html`
- A diagnostic bundle fails to be produced
- A break/diagnose scenario produces false or absent diagnosis
- Any escalation criterion (Section 7) trips

If you go red, **write the state, write the report, stop**. Do not attempt destructive workarounds.

---

## 2. Environment

| Property | Expected |
|---|---|
| OS | Ubuntu 24.04.4 LTS (noble) |
| VM SKU | Standard D4s v3 (4 vCPU / 16 GB) |
| Admin user | `arionlabs` (was `arioncomply`; renamed pre-arrival) |
| Install root | `/data/arioncomply` |
| Repo | `github.com/jmkamula/RAG` on branch `main` |
| Latest ref expected | `b3eb53d` or newer at session start |
| Data disk | 128 GB attached at LUN 1; may be unmounted (skip if so, install on OS disk) |
| Public IP | Set by Azure — read from `ip -4 addr show eth0` or the environment |
| Region | West Europe |
| NSG rules | SSH + 8080 (+ optionally 8001) allowed from operator IP |

**Secrets you need before you start** (should be exported in your environment already; if not, ask the human):

```
ARION_OWNER_PW    Postgres owner role password
ARION_APP_PW      Postgres app role password (RLS-scoped)
NEO4J_PW          Neo4j admin password
OPENAI_KEY        OpenAI API key (with $20/mo cap set BEFORE arriving)
ANTHROPIC_API_KEY Your own API key (used only for this Claude session)
```

`install.sh` supports `--yes` mode and reads these from the environment. **Use `--yes`** so the run is unattended.

---

## 3. Phases

### Phase 1 — Install + smoke test (~45 min)

Sequential steps. Update `/data/arioncomply/dry_run_state.md` (see Section 4) after each.

**P1.1 — Sanity check the VM**
- `cat /etc/os-release` — expect `24.04`
- `whoami` — expect `arionlabs`
- `df -h /` — expect ≥60 GB free
- `free -h` — expect ≥14 GB RAM
- `command -v git python3 sudo psql` — all present (psql may not be; install.sh will handle)
- Record findings in state file

**P1.2 — Clone the repo**
```bash
sudo mkdir -p /data && sudo chown arionlabs:arionlabs /data
git clone https://github.com/jmkamula/RAG.git /data/arioncomply
cd /data/arioncomply
git rev-parse --short HEAD    # log this to state file
```

**P1.3 — Run install.sh with `--yes`**
```bash
cd /data/arioncomply
bash deploy/install.sh --yes 2>&1 | tee /tmp/install.log
```
- Expected duration: ~15 min. Slow stages: apt package install (~2 min), Chroma reindex (~5-8 min).
- If a stage fails: consult `docs/error_catalog.html` for the ARION-INSTALL-* code, apply the fix, re-run. install.sh is idempotent.
- Two-attempt rule (see Section 7).

**P1.4 — Verify services**

Preferred (single command, machine-parseable):
```bash
bash deploy/arion_status.sh --json | python3 -m json.tool
```
- Expect: every `"ok": true` in the JSON, all 5 systemd units `"active"`, exit code 0.
- The script probes Postgres + Neo4j + Chroma + API + docs + systemd unit states in one pass. Use its exit code to gate proceeding: `if bash deploy/arion_status.sh --json >/dev/null; then continue; else stop; fi`.

Also acceptable (individual probes, for reference / when you want the detail):
```bash
sudo systemctl status arioncomply-api arioncomply-chroma --no-pager | head -30
sudo systemctl list-timers 'arioncomply-*' --no-pager
ss -tlnp | grep -E ':(8080|8000|7474|7687) '
```
- Expect: `arioncomply-api` active, `arioncomply-chroma` active, `arioncomply-sweep.timer` active, ports 8080 + 8000 + 7474 + 7687 all listening.

**P1.5 — Provision first tenant**
```bash
cd /data/arioncomply
PYTHONPATH=. python3 scripts/dev/create_tenant.py \
    --name "Dry Run Tenant" \
    --industry technology \
    --admin-email dryrun@example.local
```
- Capture the printed API key to a scratch note. **Do not write the raw key to the report file** — write the first 8 chars + last 4 for reference.
- Grant `admin:status` scope:
```bash
psql "$DATABASE_URL" -c "UPDATE api_keys SET scopes = array_append(scopes, 'admin:status') WHERE 'chat' = ANY(scopes);"
```

**P1.6 — Smoke test three endpoints**
```bash
KEY='<paste the API key>'
# a) Deployment status
curl -sf -H "X-API-Key: $KEY" http://127.0.0.1:8080/api/v1/admin/deployment/status | python3 -m json.tool
# b) One chat turn
curl -sf -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
     -X POST http://127.0.0.1:8080/api/v1/chat \
     -d '{"question": "what are our NC findings?"}' | python3 -m json.tool
# c) SPA HTML
curl -sf http://127.0.0.1:8080/ui/arioncomply.html | head -20
```
- Expect: (a) 4 services healthy JSON, (b) some answer text (may say "no evidence yet" — that's OK), (c) HTML with `<title>ArionComply</title>` visible.

**P1.7 — Phase 1 exit criteria**
All three green:
- 3 systemd units active + 4 ports listening (P1.4)
- Tenant created with API key (P1.5)
- All three smoke tests return 200 with sane bodies (P1.6)

Write "Phase 1 GREEN" to the state file with timings. Proceed to Phase 2.

### Phase 2 — Ship 48 UX validation (~60 min)

Four break/diagnose scenarios. **For each: break the thing, run `diagnose.sh`, then diagnose from the bundle alone.**

Two ways to run the diagnosis step:

- **Option A (recommended)**: keep using this session. After producing the bundle, do a `Read` of the extracted files + read `CLAUDE_DEPLOY_GUIDE.md` afresh (drop prior turn context mentally — pretend you don't already know what you broke). Time yourself.
- **Option B**: end the current session, start a fresh `claude` session, paste the bundle + `CLAUDE_DEPLOY_GUIDE.md` and see if diagnosis lands. This is the honest test. Do at least one scenario this way.

For each scenario, log to state file: break command, verify command, diagnostic bundle path, diagnosis correctness (yes / no / partial), time-to-diagnosis in seconds.

**P2.1 — Scenario 1: Chroma down (`ARION-BOOT-002`)**
```bash
# BREAK
sudo systemctl stop arioncomply-chroma
curl -sf -H "X-API-Key: $KEY" -X POST http://127.0.0.1:8080/api/v1/chat \
     -H "Content-Type: application/json" -d '{"question":"hi"}' -w "%{http_code}\n"
# Expect: 500
# DIAGNOSE
bash scripts/ops/diagnose.sh
# → should show services.txt with chroma inactive, journal-api.txt with connection refused
# RESTORE
sudo systemctl start arioncomply-chroma
```

**P2.2 — Scenario 2: Missing PYTHONPATH (`ARION-BOOT-005`)**
```bash
# BREAK
sudo systemctl edit arioncomply-api
# In the drop-in file that opens, add:
#   [Service]
#   Environment=
# Save + exit
sudo systemctl daemon-reload
sudo systemctl restart arioncomply-api
sleep 3
sudo systemctl status arioncomply-api --no-pager | head -10
# Expect: failed / auto-restart loop
# DIAGNOSE
bash scripts/ops/diagnose.sh
# → journal-api.txt should show ModuleNotFoundError: No module named 'rag'
# RESTORE
sudo systemctl revert arioncomply-api
sudo systemctl daemon-reload
sudo systemctl start arioncomply-api
```

**P2.3 — Scenario 3: Fresh tenant, no evidence (`ARION-RUNTIME-002`)**
- This isn't a bug — it tests whether Claude distinguishes expected states from bugs.
```bash
# BREAK — create a second tenant
PYTHONPATH=. python3 scripts/dev/create_tenant.py \
    --name "Empty Tenant" --industry retail \
    --admin-email empty@example.local
NEW_KEY='<paste new key>'
# VERIFY
curl -sf -H "X-API-Key: $NEW_KEY" http://127.0.0.1:8080/api/v1/posture/dashboard | python3 -m json.tool | head -30
# Expect: all controls Not assessed
# DIAGNOSE
bash scripts/ops/diagnose.sh
# → should diagnose as: expected fresh-tenant state, matches ARION-RUNTIME-002
# (RESTORE not applicable — Empty Tenant stays; note in report)
```

**P2.4 — Scenario 4: Bogus OpenAI key (deliberately no ARION code yet)**
- Tests catalog coverage — should surface a gap.
```bash
# BREAK
sudo sed -i.bak 's/^OPENAI_API_KEY=.*/OPENAI_API_KEY=sk-bogus-key-fail/' /data/arioncomply/.env
sudo systemctl restart arioncomply-api
sleep 3
curl -sf -H "X-API-Key: $KEY" -X POST http://127.0.0.1:8080/api/v1/chat \
     -H "Content-Type: application/json" -d '{"question":"any NCs?"}' -w "%{http_code}\n"
# Expect: 500
# DIAGNOSE
bash scripts/ops/diagnose.sh
# → no exact ARION-* code fits; diagnostic bundle should show OpenAI 401s in journal
# EXPECTED FOLLOW-UP (log this for the report; do NOT edit the catalog now):
#   Ship 51'.b candidate: add ARION-RUNTIME-011 for LLM auth failures.
# RESTORE
sudo mv /data/arioncomply/.env.bak /data/arioncomply/.env
sudo systemctl restart arioncomply-api
```

**P2.5 — Phase 2 exit criteria**

- Each scenario: bundle produced, diagnosis correct or documented gap
- P2.4 documents the missing code as a Ship 51'.b candidate (do not add the code — that's for a future arc with human oversight)
- All services restored after Phase 2

Write "Phase 2 GREEN" to the state file with per-scenario timings.

---

## 4. State file convention

Path: **`/data/arioncomply/dry_run_state.md`**

Update after every phase step. Structure:

```markdown
# Dry-run state — <ISO timestamp of run start>

## Phase 1
- [x] P1.1 sanity checked at HH:MM:SSZ — OS 24.04.4, RAM 15.5GB, disk 62GB free
- [x] P1.2 cloned at HH:MM:SSZ — ref b3eb53d
- [x] P1.3 install.sh completed at HH:MM:SSZ — 14m32s (Chroma reindex 6m10s)
- [x] P1.4 services verified at HH:MM:SSZ — 3 units active, 4 ports listening
- [x] P1.5 tenant created at HH:MM:SSZ — id 12345678-... key arion_ab34...zzzz
- [x] P1.6 smoke tests passed at HH:MM:SSZ
- [x] P1.7 GREEN at HH:MM:SSZ

## Phase 2
- [x] P2.1 Chroma-down at HH:MM:SSZ — bundle /tmp/arion-diag-...tar.gz, diagnosed 18s, correct
- [ ] P2.2 pending
...
```

If interrupted and re-invoked, read this file first to know where to resume. Never re-run a step marked `[x]`.

---

## 5. Report spec

Path: **`/data/arioncomply/dry_run_report.md`**

Write once, at end of run. Structure:

```markdown
# Dry-run report — <ISO timestamp>

## Summary
- Overall: GREEN | RED (one word)
- Phase 1 duration: X min
- Phase 2 duration: X min
- Total: X min

## Phase 1 findings
- Install completed in Xm Ys (breakdown of slow stages)
- Deviations from `docs/dry_run_azure_playbook.html`: (list, or "none")
- Any warnings during install.sh worth capturing

## Phase 2 findings
Per scenario:
- Scenario 1 Chroma down: bundle produced (path), diagnosed in Xs, correctness (yes/no/partial), notes
- Scenario 2 Missing PYTHONPATH: ...
- Scenario 3 Fresh tenant: ...
- Scenario 4 Bogus OpenAI key: ...

## Bugs found
- If P1 or P2 surfaced any codebase bug, describe it here with:
  - Symptom
  - Suspected cause
  - Recommended Ship-N candidate

## Catalog gaps
- Any error code that should exist but doesn't (from P2.4 and any similar)
- Any error code that fired but was undocumented

## Improvements suggested
- Playbook clarifications
- install.sh polish opportunities
- Diagnostic bundle content additions
- CLAUDE_DEPLOY_GUIDE.md corrections

## What I did NOT do
- Anything Section 7 gated me out of
- Anything I would have needed human input for
```

**Do not** paste raw API keys, .env content, or evidence text into the report. First-8/last-4 of the API key is fine as a reference.

---

## 6. Safety guardrails

Hard rules — no exceptions without explicit human OK:

- **No `git push`.** Ever. This VM is a dry-run environment; nothing should reach `origin`. Local commits are OK if you need to preserve a fix, but push is banned.
- **No `git commit` unless it's a fix to a bug you found.** If you commit, describe what and why in the report.
- **No destructive DB ops.** `DROP`, `TRUNCATE`, `DELETE` without a `WHERE` clause are all banned. Read-only `SELECT` + `psql` inspection is fine. Data changes (`INSERT` / `UPDATE`) only if a scenario explicitly requires it (e.g., P1.5's `array_append` to grant a scope).
- **No `rm -rf`** on anything outside `/tmp`. If a fix requires removing files, ask first.
- **No touching other VMs.** You are on `ariondryrun`. Do not `ssh` to the demo VM. Do not `curl` the demo VM's API. Do not read demo tenant IDs.
- **Do not exfiltrate secrets.** Never write raw passwords, API keys, or `.env` content to the report file or stdout. Use `env.redacted.txt` shape from `diagnose.sh` as your standard.
- **Do not modify install.sh, systemd units, or schema baselines to "make things work".** If they don't work as-is, that's a bug worth reporting — don't paper over it.
- **Do not run migrations.** The install uses `db/baseline/schema_baseline.sql`. `db/schema_v*.sql` files are historical migrations — do not apply them.
- **No package installs beyond what install.sh does.** Except Claude Code itself + `nodejs`/`npm`, which were installed pre-arrival.

Soft rules — favour these unless you have a good reason to deviate:

- Prefer reading `CLAUDE_DEPLOY_GUIDE.md` and `docs/error_catalog.html` over grepping code, when the answer is procedural
- Prefer `systemctl` over `kill` for stopping services
- Prefer `sudo systemctl edit <unit>` over editing files directly under `/etc/systemd/system/`
- Prefer running `bash scripts/ops/diagnose.sh` over collecting logs manually

---

## 7. Escalation criteria

**Stop and write the report** if any of these trip:

1. **Two-attempt rule**: A step failed twice with the same symptom, after applying the documented fix from `error_catalog.html`. Do not try a third invention.
2. **Data appears corrupted**: Postgres refuses to start; Neo4j reports inconsistency; schema baseline apply produces errors that aren't in the catalog.
3. **A safety guardrail trips**: You catch yourself about to do something Section 6 forbids. Stop, note it, ask.
4. **You disagree with the playbook**: If your judgment says the playbook step is wrong for the current state, note it in the report and stop rather than deviate. The human will decide.
5. **Ambiguous scope**: You're about to do something not covered here. Ask.
6. **Time budget exceeded**: Phase 1 > 90 min OR Phase 2 > 90 min. Something is off.

**Proceed autonomously** on:

- Retrying an idempotent step (`install.sh` is idempotent by design)
- Applying a documented fix from `error_catalog.html` (only once per code)
- Reading files, running read-only queries, producing diagnostic bundles
- Restoring state after a break/diagnose scenario
- Writing to `dry_run_state.md` and `dry_run_report.md`

---

## 8. Handoff

At end of run, whether GREEN or RED:

1. `/data/arioncomply/dry_run_state.md` — every step marked `[x]` (green) or `[!]` (red / stopped)
2. `/data/arioncomply/dry_run_report.md` — full report per Section 5
3. All Phase 2 diagnostic bundles left at `/tmp/arion-diag-*.tar.gz` (do not delete)
4. Final message in the Claude Code session: one paragraph summary + pointer to the report

If GREEN: the human can now use this VM as a validated POC install shape, or destroy the RG for cost cleanup.

If RED: the state file + report tell the human where you stopped and what they need to look at. Do not attempt automatic remediation of a RED state.

---

## Related documents

- `CLAUDE.md` — codebase orientation (product direction, key files, DB layout)
- `CLAUDE_DEPLOY_GUIDE.md` — AI-first ops playbook (symptom → verify → fix)
- `docs/dry_run_azure_playbook.html` — human-oriented version of Phases 1 + 2
- `docs/poc_install_guide.html` — general install runbook
- `docs/error_catalog.html` — stable `ARION-*` error codes
- `scripts/ops/diagnose.sh` — diagnostic bundle generator
- `deploy/arion_status.sh` — service status probe (`--json` for parseable output; exit code gates proceed/stop). Use this at the top of each phase to confirm state.
- `deploy/install.sh` — the one-command installer (supports `--yes`)
- `scripts/dev/create_tenant.py` — tenant provisioning

Written for Ship 48/49/50 as-of `b3eb53d`. Update this file when the phase structure or exit criteria change.
