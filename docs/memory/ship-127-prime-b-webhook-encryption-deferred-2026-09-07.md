---
name: ship-127-prime-b-webhook-encryption-deferred-2026-09-07
description: Ship 127'.b — deferred; field-level encryption on tenant_notification_channel.endpoint doesn't earn its complexity while 0 rows exist. Threat model + implementation plan captured for when it becomes worth doing.
metadata:
  type: project
---

# Ship 127'.b — Slack webhook encryption: deferred with rationale

**Date:** 2026-09-07
**Trigger:** Ship 124'.c agent security review flagged `tenant_notification_channel.endpoint` (plaintext webhook URLs) as MEDIUM.
**Verdict:** Defer. Zero rows exist today; the complexity buys nothing until a real customer configures a webhook.

## The finding, restated

`tenant_notification_channel.endpoint TEXT NOT NULL` stores different things per `channel_kind`:

- `email` — comma-separated recipient addresses. Not a secret; sending to an already-known address doesn't leak anything.
- `slack` — full Slack webhook URL like `https://hooks.slack.com/services/T00000/B00000/XXXXXXXX`. **This IS a bearer token** — anyone with the URL can post messages to that channel as the tenant.
- `webhook` — generic outgoing webhook URL. Similar risk profile to Slack.

If the compliance DB is compromised, an attacker gets the plaintext webhook URLs + can impersonate the tenant in their Slack workspace + spam their configured outbound webhooks.

## Why we're deferring

**1. Zero rows.** Live query on dev VM (2026-09-07): `SELECT COUNT(*) FROM tenant_notification_channel = 0`. Same expected on the PoC. No tenant has configured Slack or webhook delivery yet — the field is unused capability. Encrypting an empty table is design theatre.

**2. Bigger prize is elsewhere.** The threat model where webhook encryption matters (direct DB compromise or backup exposure) is the same threat model where the ENTIRE compliance dataset leaks — postures, findings, evidence, tenant scoping facts, audit trail. Encrypting a subset of one column doesn't materially improve the tenant's position when the same attacker has everything else.

**3. Real defence lives at other layers.** For direct-DB-compromise + backup exposure:
   - Postgres access control (only owner + `arioncomply_app` can read)
   - RLS on the table (app scopes to same-tenant)
   - **OS-level backup encryption** (proper `pg_dump` → encrypted destination)
   - **Disk-level encryption** (`dm-crypt` on the data volume for production; PoC-acceptable to defer)
   - **Rotation via Slack** (if URL leaks, the tenant revokes it in Slack + generates a new one — this is Slack's design intent for webhooks)

**4. The field-level encryption threat model is narrow.** The one case where it moves the needle is: **app-role compromise (SQLi or credential leak) WITHOUT owner-role compromise WITHOUT physical/backup access**. In that scenario, plaintext columns are readable but encrypted ones (with key in `.env` not `db_url`) aren't. Real but narrow.

## What implementing it would look like (Option A, kept for reference)

If/when this becomes worth doing:

**Schema changes (`schema_v_TBD_encrypt_webhook_endpoint.sql`):**
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Add encrypted column; keep the old one during migration
ALTER TABLE tenant_notification_channel
    ADD COLUMN endpoint_ct bytea;

-- Encrypt existing rows with pgp_sym_encrypt using key from GUC
-- (the setter runs before this migration; see notes below)
UPDATE tenant_notification_channel
   SET endpoint_ct = pgp_sym_encrypt(endpoint, current_setting('arion.endpoint_key'))
 WHERE endpoint IS NOT NULL AND endpoint_ct IS NULL;

-- Verify + drop plaintext
ALTER TABLE tenant_notification_channel
    DROP COLUMN endpoint,
    ALTER COLUMN endpoint_ct SET NOT NULL;
ALTER TABLE tenant_notification_channel
    RENAME COLUMN endpoint_ct TO endpoint_encrypted;
```

**Application code (`rag/notifications/deliver.py`):**
- On read: `SELECT ..., pgp_sym_decrypt(endpoint_encrypted, %s) AS endpoint FROM ...` with the key passed as parameter
- On write: `INSERT ... VALUES (..., pgp_sym_encrypt(%s, %s), ...)` with (endpoint, key) tuple
- Key sourced from `os.environ["ARION_ENDPOINT_ENCRYPTION_KEY"]`

**Key management (`.env` + `deploy/.env.example`):**
```
# Ship 127'.b — pgcrypto key for tenant_notification_channel.endpoint.
# Generated at install time (32 URL-safe chars, via openssl rand); NEVER
# committed. Losing the key means webhook URLs cannot be decrypted;
# tenants must re-enter them. Rotation: decrypt-all + re-encrypt-all in
# one migration.
ARION_ENDPOINT_ENCRYPTION_KEY=CHANGE_ME
```

**Ceremony added:**
- `scripts/ops/init-secrets.sh` generates the key (same shape as ARION_OWNER_PW)
- Backup restoration requires the key to be present + matching
- Rotation is a new arc (currently zero code exists to do it)
- Two flow paths in `deliver.py` (encrypt/decrypt) instead of one
- Test coverage for encryption round-trip + missing-key fail-loud

## Re-review triggers

Reopen this decision when ANY of the following:

1. **First customer configures a webhook.** `SELECT COUNT(*) FROM tenant_notification_channel WHERE channel_kind IN ('slack', 'webhook') > 0`. Now the threat is real, not theoretical.
2. **DB-access boundary changes.** Introducing read replicas, DBA access, or shared managed Postgres — any expansion of who can read the raw tables — makes the "narrow" threat model less narrow.
3. **Ship 128'+ implements OS-level backup encryption.** Once the surrounding defence is in place, adding field-level encryption for the highest-value column completes the layered story rather than being a lone lifeline.
4. **Compliance requirement.** A customer or auditor explicitly requires "webhook URLs must be encrypted at rest" — then we implement, even at zero rows.

## Related decisions

- Ship 126'.b — PII redaction on log tables is a related "reduce data-at-rest sensitivity" arc, but log preview + user query text ARE actively written. Encryption of unused capability is different from redaction of live data.
- Ship 125'.c (chromadb CVE analysis) — same shape: don't spend arc-time closing gaps in surfaces we don't expose; document the reasoning + re-review triggers.
- Ship 122'.b (Neo4j write-path audit) — codified Lesson 233 "absence-of-gap is a delivery outcome not a non-arc." This deferral is another instance: documenting WHY we're not implementing IS the deliverable.
