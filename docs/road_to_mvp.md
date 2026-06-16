# Road to MVP

Strategic placeholder for the path to first paying customer. Drafted
end-of-day after the architectural-pause discussion; captures the
revised (smaller, more honest) MVP scope after pushing back on
"production-grade everything" defaults.

## What "MVP" means here

The target: **first paying customer with a defensible deploy, auth, and
data-handling story**. Not a pre-revenue prototype; not a multi-tenant
SaaS launch.

Three flavors with different shapes:

| Model | First customer looks like | MVP shape |
|---|---|---|
| **High-touch B2B** ($50K+ ACV) | Manual onboarding, you're on first-name terms | Smaller MVP — skip self-serve, skip multi-user complexity |
| **Enterprise design partner** ($0-25K) | A logo, not much revenue, lots of feedback | Even smaller — ship behind their VPN, focus on the extraction outcome |
| **PLG SaaS** ($100-500/mo, self-serve) | Stranger signs up at 2am | Larger MVP — self-serve onboarding, Stripe, multi-user from day one |

**This doc assumes high-touch B2B or design partner.** PLG SaaS adds
~2 weeks of self-serve onboarding + billing on top.

## The honest MVP blocker list

Five things actually blocking first revenue:

| # | Blocker | Effort |
|---|---|---|
| 1 | **PDF extraction Layer A** — too many compliance docs are PDF (0% bound rate today vs 92% workbook) | ~1 day |
| 2 | **Cloudflare Access auth + Entra ID SSO** — covers identity, authz, MFA, audit trail | ~1.5-2 days |
| 3 | **HA cold standby + nightly backups** — Tier 1 HA on VM2 with documented restore | ~2-3 days |
| 4 | **Stage-1 UX hardening** — surface crosscheck signal, prevent rushed bulk-approve | ~1-2 days |
| 5 | **CSV export of posture / findings / uploads** — both GDPR Art.20 portability + customer trust | ~half day |

**Total: ~6-9 days of focused work.**

What's NOT a blocker (revised from earlier handwaving):

- Hosted/managed Postgres — self-hosted with cron backups is fine
- Load balancer — single VM with systemd respawn is fine
- HA Tier 2/3 (sub-15min RTO) — only if customer contracts demand it
- Self-serve tenant onboarding — manual / white-glove is fine for first 5-10
- Native OIDC integration — Cloudflare Access defers this to v1.x
- Multi-user RBAC complexity — single role per tenant works initially
- Multi-region deployment — wait for tenant ask
- Stripe / billing — invoicing is fine for first customers
- Multi-framework beyond ISO 27001 + GDPR — separate strategic thread
- Provider independence (LLM strategy) — separate strategic thread

## Cloudflare auth + authz plan

### The architectural split

```
Browser → Cloudflare Access → ArionComply VM(s)
              │                       │
              │ identity + URL-RBAC   │ tenant isolation + audit
              │ delegated to Entra ID │ + fine-grained role enforcement
              ▼                       ▼
        SOC 2 / ISO / etc.       (existing RLS + role logic)
        compliance posture
```

**CF handles**: identity, MFA, session management, URL-pattern RBAC,
password lifecycle, conditional access, audit of authentication events.

**App handles**: tenant isolation (existing RLS pattern), role
enforcement at action level, audit log of business actions.

### Configuration

Three CF Access "applications" cover the role split:

```yaml
# Admin policies
paths:    [/api/v1/admin/*, /api/v1/dashboard/admin/*]
require:  group "ArionComply-Admins"
additional: MFA required

# Reviewer policies
paths:    [/api/v1/findings/approve, /api/v1/findings/reject,
           /api/v1/posture/stage2/*]
require:  groups in ["ArionComply-Admins", "ArionComply-Reviewers"]

# Read policies (default)
paths:    [/api/v1/chat, /api/v1/posture/*, /api/v1/dashboard/*]
require:  any authenticated user in ArionComply-* groups
```

### App-side change

```python
# rag/auth/cf_access.py — new
def get_user_from_cf_access(request) -> UserContext:
    jwt = request.headers.get("Cf-Access-Jwt-Assertion")
    claims = verify_cf_jwt(jwt)  # signed by CF, verify with their public key
    email = claims["email"]
    groups = claims.get("groups", [])
    user = db.query(User).filter_by(email=email).first()
    if not user:
        deny("user not provisioned in ArionComply for this tenant")
    role = map_groups_to_role(groups)
    return UserContext(tenant_id=user.tenant_id, user_id=user.id, role=role)
```

Keep `X-API-Key` for machine-to-machine. CF Access JWT for human users.

### What customer's IT does

1. ArionComply registers as multi-tenant app in their Entra ID
2. Customer admin creates groups: `ArionComply-Admins`, `-Reviewers`, etc.
3. Customer admin assigns their users to groups
4. ArionComply reads group memberships at login

### What you skip

- Password reset flows (delegated)
- MFA enforcement (delegated)
- Session timeout (delegated)
- User lifecycle / offboarding (delegated — customer deactivates Entra user → access revoked automatically)

### Cost

- CF Access **free tier**: 50 users
- Above 50: $7/user/month (or ~$2.50 on enterprise volume)
- For first paying customer (5-15 internal users): free tier sufficient

## HA deploy plan (Tier 1: cold standby)

### Target SLA

| Metric | Target |
|---|---|
| Availability | 99% (~7 hours/month downtime budget) |
| RTO | 30-60 min (manual failover) |
| RPO | 24 hours (nightly snapshot) |

This meets most "first paying customer" SLA expectations. Escalate to
Tier 2 (warm standby, 5-10 min RTO) only when a contract demands it.

### Architecture

```
                      Cloudflare
                          │
              ┌───────────┴──────────┐
              │                      │
           VM1 (active)          VM2 (cold standby)
           ├── FastAPI           ├── FastAPI (idle)
           ├── Postgres          ├── Postgres (idle, ready to restore)
           ├── Neo4j             ├── Neo4j (idle, rebuilt from source)
           └── ChromaDB          └── ChromaDB (idle, restored from snapshot)
              │                      │
              └──────┬───────────────┘
                     │
              Azure Blob Storage
              ├── Uploaded files (shared)
              ├── Postgres dumps (nightly)
              └── Chroma snapshots (nightly)
```

### Migration & setup steps

| Step | What | Effort |
|---|---|---|
| 1 | Move uploaded files from local FS to Azure Blob — code change in `client_documents.storage_path` + reader changes | ~0.5 day |
| 2 | Provision VM2 in same region — identical OS + Python + dependencies via setup script | ~0.5 day |
| 3 | Cron `pg_dump` → Azure Blob on VM1, every night | ~30 min |
| 4 | Restore script on VM2 — pulls latest dump, restores Postgres | ~30 min |
| 5 | Neo4j: scripts to rebuild from `db/*.cypher` + curation YAMLs (already in repo) — Neo4j data is universal, no per-tenant state | ~30 min |
| 6 | ChromaDB: nightly snapshot to Blob + restore script | ~1 hr |
| 7 | TLS via Caddy on both VMs (auto Let's Encrypt) | ~30 min |
| 8 | DNS pointed at Cloudflare with origin to VM1 (CF Tunnel preferred — no public IP) | ~30 min |
| 9 | Uptime monitor (UptimeRobot / BetterStack) hitting health endpoint | ~30 min |
| 10 | Runbook: "VM1 died, here's how to flip to VM2" — half-page doc | ~30 min |
| 11 | Failover drill: actually do it, time the recovery | ~1 hr |

**Total: ~2-3 days.**

### What you skip

- Postgres streaming replication (Tier 2)
- Patroni cluster (Tier 3)
- Neo4j causal cluster (requires Enterprise license)
- Read replicas
- Multi-region
- Auto-failover orchestration

## Order of operations (recommended sequence)

A focused two-week sprint, eval-gated each step:

### Week 1: foundations

| Day | Work |
|---|---|
| 1 | **PDF extraction Layer A** — pdfplumber + markdown layer, eval validation |
| 2 | **CSV export** — endpoints + UI download buttons for posture / findings / uploads |
| 3 | **Backups + TLS + monitoring** — cron pg_dump, Caddy, uptime check, runbook |
| 4 | **Stage-1 UX hardening (part 1)** — surface crosscheck signal in UI |
| 5 | **Stage-1 UX hardening (part 2)** — anti-bulk-approve prompt, per-finding source provenance |

### Week 2: production deploy

| Day | Work |
|---|---|
| 1 | **Storage migration** — uploads to Azure Blob, code change, migration script |
| 2 | **Cloudflare Access + Entra ID** — DNS, tunnel, app registration, CF policies |
| 3 | **App-side CF JWT integration** — verify JWT, extract identity, map to role |
| 4 | **VM2 cold standby** — provisioning, sync jobs, restore scripts |
| 5 | **Failover drill + documentation** — practice the runbook, time recovery, document |

### Eval discipline

Eval (199-case suite) runs at end of each day. No regression below
197/199 (the LLM-stochastic band). Any drop investigates the day's
change before moving on.

## What's NOT in MVP (explicit out-of-scope)

Documenting these so they don't sneak in:

- **Multi-framework expansion** (27701/SOC2/AI Act) — separate roadmap
- **LLM provider abstraction** — works behind Anthropic for MVP
- **Self-serve tenant onboarding flow** — manual provisioning for first 5-10
- **Stripe / billing automation** — invoice manually
- **Native OIDC integration** — Cloudflare Access defers this
- **Fine-grained per-control authz** — role-level is enough for v1
- **Multi-region deployment** — wait for tenant ask
- **Tier-2/Tier-3 HA** — cold standby Tier-1 is the MVP target
- **Catalog refinement** — crosscheck flags noise; tenant triages in Stage-1
- **Re-extraction tool for old uploads** — leaf-scan back-bind exists as the manual path
- **Mobile UI** — desktop dashboard only

If a first-customer ask hits one of these, treat it as v1.x scope and
estimate independently.

## Open decisions before sprint starts

1. **Customer flavor (high-touch B2B / design partner / PLG)?** Drives
   whether self-serve onboarding is in or out.

2. **First paying customer's identity provider** — Entra ID assumed,
   but if they're on Google Workspace or Okta, CF Access supports
   those too. Configuration change only, but worth confirming.

3. **HA Tier 1 vs Tier 2?** Most likely Tier 1; escalate only if
   contract demands it. Decision drives 3-day vs 7-day deploy work.

4. **Multi-tenant Entra ID app registration?** If you'll onboard ≥2
   customers in v1, register as multi-tenant from the start (~1 extra
   day vs single-tenant).

5. **Where the customer's data lives geographically.** Azure region
   today; EU customers may require EU-resident infra. Affects VM
   provisioning + Blob storage location.

6. **Compliance posture of ArionComply itself.** First customer in
   compliance space will ask if you have SOC 2 / ISO 27001. Have an
   honest answer ("we are pre-certification; here's our security
   posture document") or get the ball rolling on Type 1.

## Prerequisites for executing

1. **Customer signal** — a real first-customer commitment (LOI, signed
   contract, or design partner agreement). Building MVP without that
   is premature optimization.
2. **Pricing decision** — how much does this cost? Affects which
   features are "MVP" vs "growth-tier".
3. **First customer's framework scope** — confirm ISO 27001 + GDPR is
   enough, or do they also need 27701? If 27701, the 27701 onboarding
   readiness brief is on the critical path.
4. **Eval baseline snapshot** — current 197-199/199; document at sprint
   start so regressions are measurable.
5. **Customer's Entra ID admin contact** — multi-tenant app registration
   requires their IT to grant consent.

## What this doc isn't

- Not a project plan. Day estimates are illustrative; firm numbers come
  when sprint starts.
- Not a vendor evaluation for Cloudflare. Could be Tailscale / Pomerium /
  custom OIDC instead. CF is the recommended path but not the only one.
- Not a sales playbook. Customer flavor + pricing are open decisions
  documented but not made.

## Related

- `[[intake-pipeline-architecture]]` — what the application does
- `[[llm-provider-strategy]]` — orthogonal vendor-independence work
- `[[framework-readiness-27701]]` — next-thread framework expansion
- `[[hitl-two-stage-approval-design]]` — the Stage-1 UX that needs
  hardening for MVP
- `[[extractor-catalog-crosscheck-2026-06-15]]` — the signal the
  Stage-1 hardening should surface
- `[[per-must-binding-in-extractor-2026-06-15]]` — the per-MUST work
  shipped today; relevant for PDF Layer A integration

## Next-thread starter

When MVP sprint kicks off:

1. Snapshot eval baseline → `results/eval_pre_mvp_baseline.csv`
2. Spike PDF Layer A on Arion's 17 PDFs — measure quality delta before
   committing the integration
3. Run a "what's broken right now" half-day audit — catch the obvious
   gaps (broken pages, stale data, edge cases) that don't show in evals
4. Then proceed in the Week-1 → Week-2 sequence above
5. End each day with eval + smoke test + brief status note

Same eval-gated rhythm as today's commits, but with a different
deliverable cadence — UX/infra polish rather than architectural shifts.
