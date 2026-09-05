---
name: ship-119-prime-arc-retrospective-2026-09-05
description: Ship 119' arc — the Auditor's Ledger with PII redaction, one-time-download URLs, and Profile UI
metadata:
  type: project
---

# Ship 119' — the Auditor's Ledger

**Date:** 2026-09-05
**Commits:** (a) PII redactor + tests → (b) ledger compiler + admin endpoint → (c) schema_v116 + token endpoints → (d) UI + this doc
**Trigger:** operator question after Ship 118' — "did we ever agree on the shape and format of the auditors ledger? when a B2B sends an auditor, how soon can we retrieve and supply the ledger... do we dump everything or are we putting guard wheels to uphold privacy. what is legal for an auditor to see?"

## Motivation

Ship 118' delivered the point-in-time posture reconstruction — the raw material an auditor needs during a breach investigation. Ship 119' is the **presentation + delivery layer**: what does the tenant actually hand to the external auditor, how do they hand it over safely, and what does that mean for third-party PII in the source documents?

The auditor's ledger is the single most compelling artifact for the breach narrative. Ship 118' proved we could reconstruct posture. Ship 119' turns that capability into a deliverable a B2B customer can put in front of a real auditor without exposing every PII field their intake pipeline ever touched.

## Delivery summary

### 119'.a — PII redactor + user pseudonymisation

`rag/posture/pii_redactor.py` — pure functions, no I/O:

- `redact_pii(text, level='off'|'default'|'strict')` with regex patterns covering: email, US + international phone, US SSN, credit-card, IBAN, IPv4, Czech RČ, UK NINO, French NIR (defaults); IPv6 (strict only).
- `pseudonymise_user_id(user_id, salt)` — deterministic SHA-256 → `user-XXXXXX` (6 hex chars). Same input + same salt = same pseudonym across ledgers; different tenants get different pseudonyms because salt is per-tenant.
- `pseudonymise_users_in_text(text, user_ids, salt)` — longest-id-first replacement to avoid the "abc pre-matches abcdef" trap.
- `redaction_summary(level)` — human-readable one-liner describing what the level scrubs (used on the ledger cover page for auditor transparency).

**Deliberate non-redaction: names are not scrubbed by default.** Compliance evidence depends on named accountability — "reviewed by Jane Doe" is a load-bearing claim on the ledger. If a tenant wants stricter redaction, that's a per-engagement decision surfaced in a future arc (the ledger cover page states the current level explicitly, so ambiguity doesn't slip through).

`tests/test_pii_redactor.py` — 25 assertions covering pattern happy-paths, non-PII survival (control refs, dates, names), level semantics, idempotency (twice-redacted == once-redacted), and pseudonym determinism + salt-scoping. All 25 pass in the deploy script.

### 119'.b — Aggregate ledger compiler + admin endpoint

`rag/posture/audit_ledger.py::build_audit_ledger(pg_conn, tenant_id, options, generated_by) -> (LedgerMeta, html)`:

- Wraps Ship 118'.a `snapshot_posture` with cover page + tenant profile panel + 8-card summary grid + per-framework control tables + data-protection footer + watermark.
- `LedgerOptions` dataclass captures every generation parameter (as_of, auditor_firm, engagement_date/reference, redaction_level, include_verbatim_excerpts, pseudonymise_users, frameworks_filter, retention_days=2555 default = 7 years).
- Per-tenant salt: `hashlib.sha256(f"arion-ledger-salt-v1:{tenant_id}").hexdigest()[:32]`. Deterministic across ledgers, opaque to auditors.
- HTML output is print-optimised (Ship 118'.c pattern) — `@media print` page-break-before per framework section, watermark on every page.
- Every generation gets a `ledger_id` (UUID) embedded on the cover page + in the watermark so a specific PDF can be traced back to a specific token / access log entry.

`GET /api/v1/admin/audit-ledger` — admin endpoint returning `text/html`. Query params mirror LedgerOptions fields. This is the "test what you're about to deliver" surface for the tenant admin, distinct from the auditor-facing public endpoint added in 119'.c.

### 119'.c — One-time-download URL delivery

**How does the auditor download the ledger without an API key?** DB-backed opaque tokens, minted by the tenant admin, one-time-URL delivered via any channel the tenant + auditor already use.

`db/schema_v116_audit_ledger_download_tokens.sql`:

- `audit_ledger_download_token` — token PK (43-char URL-safe from `secrets.token_urlsafe(32)`), tenant_id, created_at, created_by, expires_at (REQUIRED — no indefinite tokens), max_uses (default 1), times_used, revoked_at, revoked_by, all ledger generation params frozen at creation, access_log JSONB (one entry per fetch: ts + IP + UA + outcome), label.
- FK `ON DELETE NO ACTION` — matches Ship 4'.b addendum + Ship 118'.b compliance-load-bearing table pattern.
- Grants: SELECT + INSERT + UPDATE to `arioncomply_app`. **No DELETE grant** — tokens age out via future retention sweep, never hard-deleted. Auditor's access history stays available for the tenant's own compliance record.

**Design decision: DB-backed opaque tokens, not signed JWTs.** JWTs would be shorter + require no DB round-trip on validation, but: revocation would need a blocklist (adding the DB round-trip back), the signing key becomes a distinct rotation concern, and the audit log would live in a separate place from the token metadata. DB-backed keeps everything in one row: state, params, access log, revoke button.

**Design decision: parameters frozen at token creation, not at fetch.** The auditor fetches N times (up to max_uses); every fetch regenerates the ledger with the same frozen params. If the tenant's underlying data drifts between fetches, the ledger drifts too — but the frozen params (as_of, redaction_level, verbatim opt-in) don't. This means "what the tenant agreed to hand over" is stable; only "the underlying state as of the fetch time" varies. For a real audit, an `as_of` past date freezes everything.

Four endpoints:

- `POST /api/v1/admin/audit-ledger/tokens` (admin) — mint token. Returns the URL exactly once. Body: LedgerOptions fields + max_uses + expires_in_days + label. Response includes the one-time URL + expiry + max_uses.
- `GET /api/v1/admin/audit-ledger/tokens` (admin) — list tokens for calling tenant. **Never re-exposes the token** — only `token_prefix` (LEFT 8 chars + ellipsis), metadata, and current state. Lose the URL → mint a new one.
- `POST /api/v1/admin/audit-ledger/tokens/{prefix}/revoke` (admin) — revoke by short prefix. Prefix must match exactly one active token; UPDATE sets `revoked_at + revoked_by`.
- `GET /api/v1/audit-ledger/download/{token}` — **public, unauth** endpoint. The token IS the auth. Every request appends to access_log even on failure (expired / revoked / max_uses_reached / not_found — audit-defensibility for the tenant's records). On success, increments `times_used` + regenerates the ledger with frozen params.

### 119'.d — UI + audit scope acknowledgement

**Design decision: skip separate `audit_scope_acknowledgement` schema. The token row IS the acknowledgement.**

Every token created via the mint endpoint carries `created_by` (which user did it), `created_at` (when), the full param set (what scope was agreed to), the label the admin wrote, and the auditor firm + engagement reference they attributed the release to. That row is the proof the tenant admin knowingly released the specified scope to the specified auditor. Adding a separate acknowledgement table would either duplicate this state or add a foreign-key indirection with no new information content.

The UI's job is to force the acknowledgement to be **explicit + gated** rather than a silent side-effect of clicking "generate":

`static/arioncomply.html` Profile section (after Frameworks):

- **Auditor packages list** — one row per active token showing label, prefix, auditor firm, uses / max_uses, expires-in-N-days, verbatim-excerpts badge, state pill, revoke button.
- **"Generate audit package" button** → opens modal.
- **Modal fields:** auditor firm, engagement date, engagement reference, label, as_of (optional past date), redaction level (default / strict / off with warnings), include_verbatim_excerpts checkbox, max_uses, expires_in_days.
- **Prominent yellow acknowledgement panel** with a checkbox: "I acknowledge that this URL will be shared with the auditor named above, may contain third-party personal data, and that its use is governed by the engagement referenced. Retention rules on the auditor's copy follow the engagement letter. This action is recorded in the tenant audit trail." **Generate button is disabled until the box is ticked.**
- **One-time URL reveal panel** replaces the form on success. Copy-to-clipboard button + explicit warning that the URL will not be shown again.
- **Revoke** requires confirm dialog; on success, list refetches.

`scripts/ops/ship-119-poc-update.sh` follows Ship 118'.d convention. install.sh → API restart → verify schema_v116 → verify table + grants → run PII redactor tests → smoke-test endpoint registration.

## Lessons codified

### Lesson 216 — Data minimisation is a per-generation decision, not a global default

Ledger PII redaction is not a system-wide toggle. Every generation gets its own redaction level + verbatim-excerpts choice + user-pseudonymisation choice, captured on the token row and displayed on the cover page. This makes the choice **auditable in both directions**: a strict auditor can see "we redacted everything except names, and here's what we consider PII"; a loose engagement can flip `redaction_level=off` and the cover page states it explicitly. Compare to a system-wide "PII redaction: on/off" toggle where a tenant would either be silently protected (auditor complains about missing data) or silently exposed (regulator complains about oversharing).

### Lesson 217 — The token row is the acknowledgement; don't build a separate one

The first schema draft for 119' had an `audit_scope_acknowledgement` table with FK to the token. Then we realised the token row already contained created_by + created_at + all params + label + auditor firm + engagement reference. The separate table added an FK indirection with no new information. The lesson: before adding a "log-of-a-log" table, check whether the primary row already carries the acknowledgement fields. The UI acknowledgement checkbox is a UX gate, not a schema requirement — the act of clicking "generate" with the box ticked is what the row proves.

### Lesson 218 — Frozen-at-creation params make one-time URLs actually one-shape

Auditor URLs are ephemeral by design (max_uses=1 default), but the "one shape" the auditor sees needs to be **the shape the tenant admin agreed to at the moment they generated the URL**, not "whatever the tenant's data looks like when the auditor happens to click". Freezing all generation params (redaction_level, verbatim-excerpts, as_of date, framework filter) on the token row + regenerating from those params on every fetch gives us: (a) revocability without invalidating past PDFs the auditor might have saved locally, (b) reproducibility if the auditor requests the same URL a second time before max_uses runs out, (c) audit-defensibility because "what was released" is a stable row, not a moving target.

### Lesson 219 — Log every access attempt, not just successful ones

The public download endpoint appends to `access_log` on every request outcome: `success`, `expired`, `revoked`, `max_uses_reached`, `not_found`. This gives the tenant a complete picture: "someone tried to use this token 3 days after expiry" is compliance-load-bearing information — it means the auditor kept the URL past its retention window, or a URL leaked. Silent failures on the public endpoint would strip the tenant of exactly the visibility the acknowledgement flow promised them.

### Lesson 220 — Print-optimised HTML scales one more turn than expected

Ship 118'.c chose HTML + browser Save-as-PDF for the point-in-time snapshot. Ship 119'.b considered whether the aggregate ledger needed a real server-side PDF (weasyprint / wkhtmltopdf) since it's the "delivered-to-a-third-party" artifact. Turns out no: the auditor opens the URL, browser renders, Save-as-PDF works, all print CSS carries over, watermark stays on every page. The dependency-free HTML approach scales through the entire Ship 119' arc. We'd only need server-side PDF for automated delivery (e.g. scheduled ledger emails, no-human-in-the-loop). Deferred to the arc that demands it.

## Related arcs

- [[ship-118-prime-arc-retrospective-2026-09-05]] — point-in-time snapshot; the load-bearing prerequisite for the ledger's per-control state
- [[ship-4-prime-b-addendum-audit-log-correction-2026-07-17]] — the compliance-load-bearing table pattern schema_v116 mirrors
- [[ship-61-prime-a-evidence-package]] — per-leaf evidence package pattern the ledger's per-control section reuses
- [[ship-104-prime-arc-retrospective-2026-09-02]] — Profile section rendering pattern the auditor-packages UI reuses

## Deferred to Ship 120'+

1. **Token retention sweep** — soft-delete access-log entries older than N days + fully-consumed tokens older than M days. Currently every access forever + every token forever. Same shape as Ship 3'.k notification retention sweep.
2. **Per-engagement URL bundle** — instead of one URL per auditor request, mint a bundle of related URLs (snapshot + ledger + specific evidence packages) tied to one engagement reference.
3. **Signed URL fallback for higher scale** — if we hit token-table row-count pain, offer HMAC-signed URLs as an alternative that trades revocability for stateless validation.
4. **Auditor firm registry** — tenants often work with the same firms repeatedly. A tenant-scoped lookup would autocomplete auditor_firm + engagement_reference across mint operations.
5. **Automatic ledger snapshot at incident close** — pair with Ship 118'.c deferred item #4: when a tenant marks an incident closed, auto-mint a long-expiry ledger URL frozen at the incident date.

## PoC deployment plan

`scripts/ops/ship-119-poc-update.sh` follows Ship 118'.d convention. From operator's Mac:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-119-poc-update.sh
'
```

Expected result: schema_v116 applied idempotently; API restarted; PII redactor test suite passes; token endpoints resolve (return 401 without api key = registered correctly).

To try the auditor packages UI from operator's Mac after deploy:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 -L 8080:127.0.0.1:8080 arionops@10.0.1.85
# then in browser at http://localhost:8080/  → sign in
# → Profile → 'Auditor packages'
# → 'Generate audit package' → fill form → tick acknowledgement → Generate URL
# → copy the one-time URL → open in a private/incognito window (no key needed)
# → browser Save as PDF → the auditor's deliverable
```
