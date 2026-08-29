# CLAUDE_OPERATOR.md

**Runbook for Claude Code running on an operator laptop, driving an ArionComply install into a customer's Ubuntu 24.04 host via SSH.**

The host is provider-agnostic: cloud VM (Azure / AWS / GCP), on-prem physical box, or a customer-owned hypervisor VM all work identically. `install.sh` doesn't know or care where it's running.

Read this file first. Then read `CLAUDE.md` for codebase orientation and `CLAUDE_DEPLOY_GUIDE.md` for post-install troubleshooting.

This runbook **supersedes** `CLAUDE_DRYRUN.md` — that file was written for a one-time Ship 48 validation where Claude ran ON a fresh dry-run VM. This file is for the forward model: **Claude on operator laptop, customer VM as the target.**

---

## 1. Mission

You are Claude Code running on an ArionComply support engineer's laptop. The customer has already provisioned an Ubuntu 24.04 host per `docs/customer_prep_checklist.html` and handed off SSH access. The host may be a cloud VM (Azure / AWS / GCP) or an on-prem box — the runbook is identical either way. Your job is to:

1. **Verify handoff** — confirm the customer sent the minimum information to connect safely.
2. **Install ArionComply** on the customer VM via `deploy/install.sh --yes`.
3. **Provision the customer's first tenant** and smoke-test end-to-end.
4. **Deliver a handback** — health report + credential delivery pattern.
5. **Support post-install troubleshooting** using `scripts/ops/diagnose.sh` bundle → local analysis.

**Green** at end of run: customer has a working ArionComply on their VM, one tenant provisioned, tenant API key delivered via the customer's own secret channel, and a signed-off health report.

**Red**: any escalation criterion in §7 trips, or a step you cannot resolve after two documented attempts.

If you go red: write state, write the handback with what was and wasn't achieved, tell the operator, stop.

---

## 2. Handoff acceptance

**Before touching the customer VM**, verify the operator has these from the customer:

| Item | Format | Example |
|---|---|---|
| Host address | Public IP + hostname (cloud) or LAN IP + reachability method (on-prem) | Cloud: `40.68.12.34` / `arioncomply-poc.example.cloud`. On-prem: `10.0.1.85` reachable via WireGuard peer |
| SSH user | Named operator account (never `root`) | `arionops` |
| SSH access | One of: pubkey installed / cert authority signature / bastion tunnel | operator's `~/.ssh/id_ed25519` accepted |
| NSG allowlist status | Customer confirmed operator IP is allowlisted for :22 | screenshot / written confirmation |
| Customer's secret-delivery channel | How you'll return the tenant API key (never email/chat) | "1Password shared vault `arion-poc`" |
| OpenAI API key or equivalent | For the install `.env` — customer provides or gates via their own key | scoped throwaway key with billing cap set |
| Postgres passwords the customer picks | Two: owner + app | customer-provided or customer says "you pick and store in vault" |

If **any** of these is missing, **stop and ask the operator to close the gap with the customer** before continuing. Do not guess.

**Confirm SSH works before running anything**:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 arionops@<vm-ip> 'whoami && cat /etc/os-release | head -3'
# Expect: arionops + Ubuntu 22.04 or 24.04
```

If this fails: escalation, not troubleshooting. Ask the operator.

---

## 3. Environment

### Operator laptop

| Thing | Purpose |
|---|---|
| `ssh`, `scp`, `rsync` | remote command driving |
| `~/.ssh/id_ed25519` (or equivalent) | signed by customer's CA or added to VM authorized_keys |
| Local scratch dir | e.g. `~/arion-ops/<customer-name>/` — holds diagnostic bundles + logs; NEVER commit or upload |
| Secrets manager access | how tenant credentials get to the customer at the end |

### Customer host (per customer_prep_checklist.html)

| Thing | Location |
|---|---|
| OS | Ubuntu 24.04 LTS (22.04 acceptable) |
| Spec | ≥4 vCPU / ≥16 GB RAM / ≥60 GB disk. Cloud VM SKU examples: Azure D4s v3, AWS t3.xlarge, GCP n2-standard-4. On-prem: 4-core Intel/AMD box with 16 GB RAM. Older CPUs (Haswell/Broadwell) work; expect slower Chroma reindex on the first API start. |
| Deployment path | Cloud VM (Azure / AWS / GCP) or on-prem — install.sh doesn't differ; the operator only cares that SSH works |
| Install root | `/data/arioncomply` (customer has directory pre-created, chown to `arionops`) |
| Sudo user | `arionops` (or whatever the customer named it) |
| Firewall | :22 from operator IP only (NSG / security group / ufw). :8080 initially closed; customer tunnels via SSH post-install |
| Outbound | HTTPS to `api.openai.com`, `debian.neo4j.com`, `pypi.org`, `github.com` |

### Local scratch layout (recommended)

```
~/arion-ops/<customer-name>/
├── handoff.txt                 # customer's info (redacted before archival)
├── install.log                 # tee of remote install.sh --yes
├── diagnose-<timestamp>.tar.gz # bundles from customer VM
├── handback.md                 # what you deliver back to customer
└── credentials.private         # never in git — tenant keys before secret-vault delivery
```

---

## 4. Phases

### Phase 1 — Connect + install (~30 min)

Sequential. Update `handback.md` (§5) after each step with timing + outcome.

**P1.1 — Verify handoff** — §2 above. If any gap, stop.

**P1.2 — Confirm VM readiness**

```bash
ssh arionops@<vm-ip> 'bash -s' <<'EOF'
set -e
cat /etc/os-release | grep VERSION_ID
uname -m
df -h / | awk 'NR==2 {print "disk free:", $4}'
free -h | awk '/^Mem:/ {print "ram:", $2}'
nproc | xargs echo "cpu:"
command -v git python3 curl sudo || echo "missing basic tools"
[ -d /data/arioncomply ] && ls -ld /data/arioncomply || echo "install dir missing"
EOF
```

- OS 22.04 or 24.04, ≥60G free, ≥14G RAM, sudo user, install dir exists + owned by arionops.
- If anything is off: back to customer, don't work around.

**P1.3 — Clone repo (or pull if pre-cloned)**

```bash
ssh arionops@<vm-ip> 'bash -s' <<'EOF'
if [ ! -d /data/arioncomply/.git ]; then
    git clone https://github.com/jmkamula/RAG.git /data/arioncomply
fi
cd /data/arioncomply
git fetch origin main
git checkout main
git reset --hard origin/main
git rev-parse --short HEAD
EOF
```

Log the SHA to `handback.md`.

**P1.4 — Run install.sh --yes**

Pre-load the secrets into the SSH session env, then run:

```bash
ssh arionops@<vm-ip> \
  ARION_OWNER_PW="$ARION_OWNER_PW" \
  ARION_APP_PW="$ARION_APP_PW" \
  NEO4J_PW="$NEO4J_PW" \
  OPENAI_KEY="$OPENAI_KEY" \
  'cd /data/arioncomply && bash deploy/install.sh --yes' \
  2>&1 | tee ~/arion-ops/<customer>/install.log
```

Expected duration: ~15 min. Slow stages: apt (~2 min), Chroma reindex (~5-8 min after API start). install.sh is idempotent — safe to re-run if it exits partial.

**Two-attempt rule** (§7): if a stage fails, consult `docs/error_catalog.html` for the ARION-INSTALL-* code, apply the fix, re-run install.sh. If it fails again with the same symptom, stop.

**P1.5 — Verify services**

```bash
ssh arionops@<vm-ip> 'bash /data/arioncomply/deploy/arion_status.sh --json' | jq .
```

- Expect every `"ok": true`, all systemd units `"active"`.
- Gate: if exit code non-zero, stop and diagnose (§Phase 3).

Log status snapshot to `handback.md`.

### Phase 2 — Tenant + smoke test (~15 min)

**P2.1 — Provision customer's first tenant**

```bash
ssh arionops@<vm-ip> "cd /data/arioncomply && \
  PYTHONPATH=. python3 scripts/dev/create_tenant.py \
    --name '<Customer Corp>' \
    --industry <sector> \
    --country <ISO2> \
    --admin-email <customer-admin-email> \
    --admin-name '<Customer Admin>'"
```

**Capture the printed API key immediately into `credentials.private`** on the operator laptop. The key is SHA-256 hashed at rest — you cannot retrieve it later.

**P2.2 — Grant admin:status scope** (needed for deployment-status endpoint):

```bash
ssh arionops@<vm-ip> "psql \"\$DATABASE_URL\" -c \
  \"UPDATE api_keys SET scopes = array_append(scopes, 'admin:status') WHERE 'chat' = ANY(scopes);\""
```

**P2.3 — Smoke tests over SSH tunnel**

Open an SSH tunnel from your laptop:

```bash
# In one shell — leave running through Phase 2
ssh -N -L 8080:127.0.0.1:8080 arionops@<vm-ip>
```

Then locally:

```bash
KEY='<from credentials.private>'
# a) deployment status
curl -sf -H "X-API-Key: $KEY" http://127.0.0.1:8080/api/v1/admin/deployment/status | jq .
# b) one chat turn
curl -sf -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
     -X POST http://127.0.0.1:8080/api/v1/chat \
     -d '{"question": "what are our NC findings?"}' | jq .
# c) SPA loads
curl -sf http://127.0.0.1:8080/ui/arioncomply.html | head -5
```

All three green → Phase 2 GREEN. Log to `handback.md`.

### Phase 3 — Troubleshooting (as needed)

When something breaks — either in Phase 1/2 or post-install support:

```bash
# On customer VM: produce the bundle
ssh arionops@<vm-ip> 'bash /data/arioncomply/scripts/ops/diagnose.sh'
# Get its path (script prints e.g. /tmp/arion-diag-<host>-<ts>.tar.gz)

# On operator laptop: retrieve
scp arionops@<vm-ip>:/tmp/arion-diag-*.tar.gz ~/arion-ops/<customer>/

# Extract locally
cd ~/arion-ops/<customer>/
tar xzf arion-diag-*.tar.gz -C ./bundle/
```

Read the bundle files with the `CLAUDE_DEPLOY_GUIDE.md §2.1` table as your index. Diagnose without SSHing back — the whole point of the bundle is that it's self-contained.

**When you find the fix**: SSH in, apply it, re-run `bash deploy/arion_status.sh --json` to confirm green.

### Phase 4 — Handback (~15 min)

**P4.1 — Deliver tenant credentials via customer's channel**

- Copy the tenant API key from `credentials.private` into the customer's chosen secret-vault (§2 handoff).
- Confirm receipt with the customer.
- **Delete `credentials.private` from the operator laptop.**

**Never** email, chat, or SMS the API key. If the customer's secret-delivery channel isn't yet defined, delivery blocks until it is.

**P4.2 — Handback artifact**

Write `handback.md` (customer-facing version, redacted). Template in §6.

**P4.3 — Archive + wipe local scratch**

```bash
# Optional: encrypt + archive
tar czf ~/arion-ops-archive/<customer>-<yyyymmdd>.tar.gz.gpg \
    --encrypt -r <your-key> ~/arion-ops/<customer>/
# Then wipe unencrypted
rm -rf ~/arion-ops/<customer>/
```

---

## 5. State + report files

Two files during the run, both under `~/arion-ops/<customer>/`:

- `state.md` — running log; each phase marked `[ ]` / `[x]` / `[!]` with timings + notes. Not shared with customer.
- `handback.md` — customer-facing outcome document. §6 template.

Neither goes into git. Neither goes into a diagnostic bundle. Both stay on the operator laptop until archived + wiped per P4.3.

---

## 6. Handback template

```markdown
# ArionComply install handback — <Customer Name>

**Date**: <yyyy-mm-dd>
**VM**: <public IP or hostname>
**Operator**: <name / initials>

## Install
- ArionComply git SHA: <short SHA>
- Install duration: <mm:ss>
- Stages: all green / issues encountered (list)
- Post-install `arion_status.sh --json` output attached below

## Tenant provisioned
- Tenant name: <name>
- Industry / country: <values>
- Frameworks enrolled: ISO 27001:2022 + GDPR:2016/679
- Admin email: <email>
- API key: **delivered via <customer's secret-vault name> to <recipient>**; not included in this document

## Smoke tests
- Deployment status endpoint: <all 4 services healthy | issue detail>
- Chat endpoint: <ok | issue>
- SPA loads: <ok | issue>

## Health snapshot
<paste arion_status.sh --json output>

## What the customer can do next
- Access SPA: `ssh -L 8080:127.0.0.1:8080 arionops@<vm-ip>` then open http://127.0.0.1:8080/ui/arioncomply.html; set API key top-right
- Upload evidence: SPA → Documents → drag/drop; also `POST /api/v1/documents` via API key
- Second tenant: run `scripts/dev/create_tenant.py` on the VM
- Troubleshoot: `bash /data/arioncomply/scripts/ops/diagnose.sh` produces a bundle; send it to the operator

## Support contract
- SSH access retained: yes / no / rotate-key by <date>
- Diagnostic-bundle delivery method: <e.g. customer uploads to shared bucket>
- Response-time expectation: <as agreed>

## Bugs / issues surfaced during install
- <none | list with error catalog code references>
```

---

## 7. Safety guardrails

You are working on a **customer's production system**. Every rule below is a hard rule — no exceptions without explicit customer OK routed through the operator.

**Hard rules — no exceptions without explicit customer OK (via the operator):**

- **No `git push`** on the customer VM. Ever. The VM is not your dev environment.
- **No `git commit`** on the customer VM. If you find a bug in ArionComply that needs a fix, note it in `handback.md` and file it in your own dev environment; do not commit on the customer's machine.
- **No destructive DB ops.** `DROP`, `TRUNCATE`, `DELETE` without a `WHERE` clause are banned. Read-only `SELECT` + `psql` inspection is fine.
- **No `rm -rf`** on anything outside `/tmp` on the VM or `~/arion-ops/<customer>/` on the laptop. Ask first.
- **No touching other customer VMs** or other tenants on this VM. If another tenant exists, it's not yours.
- **Do not exfiltrate secrets.** Never write raw passwords, API keys, or `.env` content to any file outside `credentials.private` on the operator laptop. `.env` stays on the customer VM.
- **Do not modify install.sh, systemd units, or schema baselines** to work around a problem. If they don't work as-is, that's a bug; report it, don't paper over.
- **Do not run migrations.** Install uses `db/baseline/schema_baseline.sql`. `db/schema_v*.sql` files are historical — do not apply them.
- **No package installs beyond what install.sh does.** If a dependency is missing, that's a bug in install.sh; report it.
- **Never share credentials via email, chat, or SMS.** Only the customer's own secret-vault.
- **Confirm before any `systemctl restart` or `systemctl stop`** — the customer may have live traffic.

**Soft rules:**

- Prefer `arion_status.sh --json` for health checks (single command, machine-parseable)
- Prefer reading `CLAUDE_DEPLOY_GUIDE.md` + `docs/error_catalog.html` over grepping code for procedural questions
- Prefer `sudo systemctl edit <unit>` over editing files under `/etc/systemd/system/`
- Prefer `bash scripts/ops/diagnose.sh` over collecting logs manually

---

## 8. Escalation criteria

**Stop and hand back to the operator** if any of these trip:

1. **Two-attempt rule**: A step failed twice with the same symptom after applying the documented fix from `error_catalog.html`. Do not try a third invention.
2. **Data appears corrupted or unexpected**: Postgres refuses to start; Neo4j reports inconsistency; the VM has state you didn't expect (e.g. another tenant already provisioned, previous install partial).
3. **Safety guardrail trips**: You catch yourself about to do something §7 forbids. Stop, note it, ask.
4. **You disagree with this playbook for the current state**: Note it in `handback.md` and stop rather than deviate. The operator + customer decide.
5. **Ambiguous scope**: You're about to do something not covered here. Ask.
6. **Time budget exceeded**: Phase 1 > 60 min, or Phase 2 > 30 min, or single troubleshooting scenario > 30 min. Something is off.
7. **Customer credentials at risk**: Anytime you'd have to write an API key or password somewhere other than `credentials.private` or the customer's secret-vault. Stop.

**Proceed autonomously** on:

- Retrying an idempotent step (`install.sh` is idempotent by design; `arion_status.sh` is read-only)
- Applying a documented fix from `error_catalog.html` (only once per code)
- Reading files, running read-only queries, producing + retrieving diagnostic bundles
- Writing to `state.md` / `handback.md` / `credentials.private` on the operator laptop
- Running SSH tunnel for local smoke-test access
- Restarting arioncomply-api or arioncomply-chroma **only if** the customer signed off in advance for maintenance windows

---

## 9. Handback (end-of-engagement)

Whether green or red:

1. `handback.md` finalized — timings, outcomes, issues, next steps
2. Tenant credentials delivered via customer's secret-vault; receipt confirmed; `credentials.private` deleted from operator laptop
3. Diagnostic bundles archived per P4.3 (encrypted, or wiped)
4. Customer confirms they can SSH in as their own user (independent of `arionops`) and that they know how to run `diagnose.sh` themselves

If red:

- `handback.md` marks phases stopped with the trip criterion
- Customer VM left in a **safe, documented** state — never in a half-configured state without a note
- Bugs found are filed in the operator's own dev environment for follow-up

---

## Related documents

- `docs/customer_prep_checklist.html` — what the customer does BEFORE this runbook applies
- `docs/poc_install_guide.html` — customer's DIY install alternative (no Claude operator)
- `CLAUDE_DEPLOY_GUIDE.md` — troubleshooting playbook + diagnostic bundle index
- `docs/error_catalog.html` — stable ARION-* error codes with fixes
- `CLAUDE.md` — codebase orientation
- `docs/history/CLAUDE_DRYRUN.md` — retired Ship 48 UX validation runbook (kept for reference; do not use for forward engagements)
