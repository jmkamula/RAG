---
name: ship-127-prime-arc-retrospective-2026-09-07
description: Ship 127' arc — MEDIUM security-gap closes (diagnostic-log DELETE restriction + API-key partial-logging hygiene + deferred webhook encryption with rationale)
metadata:
  type: project
---

# Ship 127' — MEDIUM security-gap closes

**Date:** 2026-09-07 (4th security arc same day as Ship 124/125/126)
**Sub-arcs:** 127'.a → 127'.b (deferred) → 127'.c → 127'.d
**Trigger:** Ship 124'.c agent security review flagged 3 MEDIUM app-layer gaps that Ship 126' explicitly deferred to Ship 127'+.

## Motivation

Ship 126' closed 5 HIGH-severity gaps + the PRIORITY-0 dev-key exposure. Ship 127' closes 2 of the 3 remaining MEDIUM gaps + documents the third as "deferred with rationale" (rather than skipped). The through-line: convert the last of the review-surfaced items into either shipped fixes or documented decisions — no ambient TODOs left standing.

## Delivery summary

### 127'.a — Diagnostic-log DELETE restriction via SECURITY DEFINER function

Ship 4'.b (schema_v79, 2026-07-17) granted DELETE on 5 diagnostic tables to `arioncomply_app` "so a future retention sweep could run under the app role." That sweep was never built. Ship 121' extended the classification to 7 tables + kept the DELETE grants. Ship 124'.c flagged the standing DELETE as a same-tenant self-erasure risk.

**Fix design chosen: SECURITY DEFINER function pattern** (rather than new `retention_sweeper` role):
- Simpler ops — no new credential + no systemd EnvironmentFile changes + no `.env` additions
- Cleaner audit — every DELETE goes through a named function with validated args + can be swapped for a provenance-logging variant later with a single body change
- Matches existing pattern — `arioncomply` owner role already has full table access; SECURITY DEFINER is a well-worn Postgres idiom for this

**`schema_v118_diagnostic_log_delete_restriction.sql`**:
- `sweep_delete_diagnostic_log_rows(p_table_name, p_retention_days, p_tenant_id)` function
- Owned by `arioncomply` (owner role) → runs with owner privileges → bypasses app-role DELETE revoke + RLS
- `SECURITY DEFINER SET search_path = public, pg_temp` for injection safety
- Table_name validated against inline allowlist (the 7 tables); any other name raises exception
- Retention_days must be `>= 1`; NULL/0/negative raises exception
- Timestamp column looked up dynamically via `information_schema.columns` (created_at / called_at / started_at / timestamp / ts — most tables use created_at; ai_call_log uses called_at)
- Returns row count deleted
- Uses `format()` with `%I` (quote_ident) on table + column names + `%L` on tenant_id for safe SQL construction
- REVOKE DELETE on the 7 tables from arioncomply_app in a `to_regclass()`-guarded DO block
- GRANT EXECUTE on the function to arioncomply_app

**Extended `deploy/baseline_grants.sql`**:
- Diagnostic-log loop now revokes UPDATE + DELETE (was just UPDATE)
- New DO block re-grants EXECUTE on the sweep function (defence-in-depth against the same class of grant-clobber Ship 120' fixed for tables — a future ALTER FUNCTION could reset the ACL)

**`tests/test_audit_table_grants.py`** extended:
- `DIAGNOSTIC_LOG_TABLES` shape flipped from `{SELECT, INSERT, DELETE}` to `{SELECT, INSERT}` for all 7 tables
- Docstring on `test_diagnostic_logs_have_no_update` updated to explain the new Ship 127'.a shape
- 4/4 pass post-migration

**Live verification on dev VM:**
- Raw DELETE from `arioncomply_app`: `ERROR: permission denied for table ai_call_log` ✓
- Function call from `arioncomply_app`: returns row count (0 for 10-year retention on already-clean table) ✓
- Bad table name in function call: `ERROR: table_name X is not in allowlist` ✓
- Bad retention_days (0): `ERROR: p_retention_days must be >= 1, got 0` ✓

### 127'.b — Slack webhook encryption: DEFERRED with rationale

Live count on dev VM: `SELECT COUNT(*) FROM tenant_notification_channel = 0`. Zero rows for `slack` or `webhook` channel kinds. Same expected on the PoC.

**Decision: defer.** Full rationale + threat-model breakdown + implementation plan for when it's worth doing is in [[ship-127-prime-b-webhook-encryption-deferred-2026-09-07]].

Short version: field-level encryption on an unused column earns nothing today. The threat model where webhook encryption matters (DB compromise / backup exposure) is the same model where the entire compliance dataset leaks anyway — bigger prize is elsewhere. Real defence lives at OS-level backup encryption + disk-level encryption + rotation via Slack (webhook URL leak = tenant revokes + re-issues, per Slack's design intent). Encryption complexity (key management + rotation + backup restore + two flow paths in `deliver.py`) doesn't pay for itself while zero rows exist.

**Re-review triggers documented**: first customer configures a webhook, DB access boundary expands, Ship 128'+ implements backup encryption, compliance requirement demands it.

This is the same pattern as Ship 122'.b's "absence-of-gap is a delivery outcome" — the deferred rationale IS the deliverable.

### 127'.c — API-key partial-logging hygiene

`vector/build_index.py:100+106` printed the first 8 characters of `OPENAI_API_KEY` + `ANTHROPIC_API_KEY` at startup. Grep audit confirmed those were the only two sites in the codebase (`vector/` only; no api_server.py, no rag/, no other scripts).

**Fix**: replaced `print(f"✓ OPENAI_API_KEY set ({api_key[:8]}...)")` with `print("✓ OPENAI_API_KEY set")` on both lines. Comment inline explains: "aggregated logs (Jaeger, syslog, systemd journal) may propagate the string; 8 chars is not enough to reconstruct a key but leaks patterns that suggest which provider + key generation the operator is using."

Not runtime-critical (this script runs only during vector reindex operations, not on API startup) but the pattern was documented in the security review + is quick to fix.

### 127'.d — deploy + eval + retro + close

`scripts/ops/ship-127-poc-update.sh` runs install.sh (applies schema_v118 + baseline_grants) → verifies DELETE revoked + function present → restarts API → smoke-tests raw DELETE denial + function call success → runs `tests/test_audit_table_grants.py` → deployment log tail.

## Lessons codified

### Lesson 254 — SECURITY DEFINER function beats new role for gated ops

The obvious answer for "app can no longer DELETE" is "new role that can." That path requires: new credential in `.env`, new EnvironmentFile in systemd unit, install.sh CREATE ROLE step, worker code that knows which credential to use, .env.example update, secret rotation dance. All that ceremony for a capability the app already had via a different role.

The SECURITY DEFINER function path: one file, one function, one GRANT EXECUTE. The app still uses its existing credential + connection pool; the function runs with owner privileges + is audit-traceable by name + can be swapped for a provenance-logging variant later. The only durable requirement is discipline: EVERY caller MUST go through the function; a future PR that does raw DELETE via the owner connection sidesteps this — but that PR is anomalous + reviewable, and the app-role REVOKE keeps the enforcement mechanism.

Rule of thumb: when the fix is "app can't do X but a controlled path can," prefer SECURITY DEFINER over new-role for cases where (a) the operation has clean args, (b) the number of call sites is small, (c) the audit story wants a named entry point.

### Lesson 255 — "Deferred with rationale" is a decision, not a punt

Ship 122'.b + Ship 125'.c + Ship 127'.b all landed as "not implementing X because Y" decisions with dedicated rationale docs. Each doc has:
- The finding, restated in operator terms
- Why we're deferring (evidence-based: live query counts, threat-model analysis, alternatives that already exist)
- What implementing WOULD look like (kept for reference — future maintainer doesn't have to re-derive)
- Explicit re-review triggers that flip the decision back to "implement"

This pattern is now the codified default for "we considered X and chose not to do it." It ages better than either "TODO: implement X someday" (which decays into ambient debt) or silent omission (which loses the reasoning). The document itself becomes the auditor answer: "why didn't you encrypt webhook URLs?" → "here's the threat model + zero-rows-yet reasoning + the triggers under which we'll revisit."

### Lesson 256 — Ship-arc closure requires zero ambient TODOs from the parent scope

Ship 124'.c's agent review flagged N gaps; Ship 126' closed 5 of 6, Ship 127' closed the last 2 of 3 MEDIUMs — even the deferred one shipped its rationale doc. The scope from that one review is now completely accounted for. Every finding is either: closed by shipped code, or documented as a decision with re-review triggers. Nothing lives in "we should do that eventually."

The alternative — leaving open items floating — is what turns "we reviewed" into "we reviewed and forgot." Every arc-family (in this case Ship 124-127 spanning 3 days) should close its parent-scope's items OR make the deferrals explicit + queryable. If Ship 128 opens tomorrow with a mystery TODO from a review nobody remembers, discipline has failed silently.

## Related arcs

- [[ship-124-prime-arc-retrospective-2026-09-07]] — the 3-agent review that surfaced all the Ship 126/127 items
- [[ship-125-prime-arc-retrospective-2026-09-07]] — 4-arc parallel scope (CVE dep closes)
- [[ship-126-prime-arc-retrospective-2026-09-07]] — closed 5 HIGH gaps + dev-key rotation
- [[ship-127-prime-b-webhook-encryption-deferred-2026-09-07]] — full deferred-decision doc
- [[ship-120-prime-arc-retrospective-2026-09-05]] — the grant-shape discipline this arc extends
- [[ship-122-prime-arc-retrospective-2026-09-05]] — Lesson 233 codified "absence-of-gap is a delivery outcome"

## Deferred to Ship 128'+

- **LOW gaps (production hardening):**
  - CDN SRI for Tabler icons
  - Data-at-rest encryption doc + implementation (`dm-crypt` on data volume)
  - Secrets rotation policy doc (referenced by Ship 126'.a; hasn't landed as a written playbook)
  - LangGraph checkpoint redaction (state may contain PII)
  - `pyproject.toml` Python version upper bound

- **Trigger-driven:**
  - Superuser erasure workflow (Ship 120 item 3 — plumbing exists via `rag/deletion_service.py`)
  - Full-test CI runner (needs merge-review flow decision + secret management)
  - Prompt-injection resistance testing via `promptmap` / `garak`
  - chromadb 2.x upgrade if/when upstream ships a fix
  - chromadb config-drift guard in `check_forbidden_patterns.sh`
  - Slack webhook field-level encryption (see 127'.b rationale doc for triggers)

- **Test-cleanup opportunistic:** `scripts/test_intake_quality_endpoint.py:39` hardcodes `arioncomply:arioncomply2026` DB owner password in `DEFAULT_DB_URL`. Same class as Ship 126'.e items but scoped to a test helper. Small edit; deferred as not blocking.

## PoC deployment plan

`scripts/ops/ship-127-poc-update.sh` follows the Ship 118+ convention. Expected: schema_v118 applied, DELETE revoked on 7 tables verified, function exists + owned by arioncomply, raw DELETE from app role fails (permission denied), function call succeeds. Deployment log at 14 entries.

**No user-visible change** — this arc tightens the security surface without changing any tenant-facing behavior. The webhook rationale doc + the vector/build_index.py logging change are both dev-side only.
