---
name: ship-123-prime-arc-retrospective-2026-09-06
description: Ship 123' arc — expose the audit-defensibility APIs (point-in-time + ledger preview) to the tenant admin UI
metadata:
  type: project
---

# Ship 123' — audit-view entry points in the SPA

**Date:** 2026-09-06
**Sub-arcs:** 123'.a preview button → 123'.b compliance history section → 123'.c deploy + eval + retro
**Trigger:** After Ship 122' closed, an operator question surfaced: "did we design a surface to expose the auditors ledger?" The audit-defensibility APIs (Ship 118'.c snapshot HTML + Ship 119'.b ledger HTML) all worked end-to-end but had no buttons in the SPA. The tenant admin's only path to the ledger was "generate a token and open the URL" — burning a `max_uses` slot to preview.

## Motivation

Ship 118/119 shipped the deliverables and the API endpoints; Ship 119'.d added the token-management UI. What was missing was the daily-workflow surface: the tenant admin's ability to LOOK at the audit trail without minting anything, and to reach the point-in-time posture view without knowing the API URL.

Two entry points close the gap:

1. **Preview ledger** — see what an auditor URL would render, before minting.
2. **Compliance history** — reconstruct posture as of any past date.

The audit-log inspector (list rows from `posture_status_log` etc.) was scoped out — it's a bigger UI (filterable table) that deserves its own arc.

## Delivery summary

### 123'.a — Preview ledger button

Added a "Preview ledger" button to the Generate audit package modal, next to the existing "Generate URL" button. On click:

- Reads current form values (redaction_level, verbatim opt-in, as_of, auditor_firm, engagement_date/ref).
- Fetches `GET /api/v1/admin/audit-ledger?<params>` with `X-API-Key` header via raw `fetch()` (the `api()` helper is JSON-only; this endpoint returns `text/html`).
- Wraps the HTML response in a `Blob` and opens via `window.open()` + `URL.createObjectURL()`.
- Handles popup-blocker case with an in-modal error.

**No token minted, no `times_used` increment.** The Ship 119'.b endpoint has been API-reachable since it shipped; Ship 123'.a just wires it to a button. Zero API changes.

Also adjusted the button layout: "Preview ledger" (outlined) + "Generate URL" (filled) side-by-side, with an inline explainer noting the difference so operators don't accidentally hit Generate when they meant Preview.

### 123'.b — Compliance history section

Added a new Profile section titled "Compliance history" between Frameworks and Auditor packages. Contents:

- Section explainer: "Reconstruct your compliance posture as it stood on any past date. Reads the audit trail directly — same source data the auditor's ledger uses, without minting anything."
- Inline `<input type="date">` (default today, min 2026-01-01, max today).
- "View snapshot" button.
- Inline error slot + note: "Opens in a new tab. Come back here to pick a different date."

On click, the button fetches `GET /api/v1/admin/posture-snapshot?fmt=html&as_of=<date>` with the API key, opens via Blob URL (same pattern as 123'.a).

**Design decision on the picker location**: the snapshot HTML (Ship 118'.c) has its own inline date picker that submits a GET form with `?as_of=...`. That picker doesn't work when the HTML is opened via a Blob URL because form submits try to navigate the `blob:` URL. Rather than injecting SPA logic into the fetched HTML, we keep the picker in the SPA + document the "come back here to change date" flow. The trade-off is one extra tab-switch when the operator wants to browse multiple dates; the win is a clean separation of concerns (SPA owns the auth-bearing fetch; snapshot HTML is a pure render).

### 123'.c — deploy + verify + eval

`scripts/ops/ship-123-poc-update.sh` mirrors the Ship 120/121/122 shape: install.sh re-run (idempotent, no schema), API restart, JS version stamp check (`2026-09-06-audit-view-entries`), both new-endpoint smoke tests (should 401/403 without API key = registered), deployment log tail.

## Lessons codified

### Lesson 235 — API-reachable is not user-reachable

Ship 118'.c + 119'.b both shipped as text/html endpoints that were "complete" in the sense that a curl-with-api-key call rendered a full auditor-defensible document. But no button in the SPA reached either endpoint. The gap was invisible from the code perspective (endpoints tested, output correct) and invisible from the retro perspective (arc closed, deliverable defined). Only the operator's daily-workflow question surfaced it. Rule of thumb: for any tenant-facing capability, "API endpoint returns 200" is not the shipping criterion; "the tenant admin can find + use it in the SPA without knowing a URL" is.

### Lesson 236 — Blob URL is the right pattern for auth-bearing HTML in new tabs

Browser tab navigation doesn't send `X-API-Key` (or any auth header). Three options for opening an authenticated HTML response in a new tab:

- Pass the API key as a query param → security anti-pattern (URL leaks in browser history, Referer headers, server logs).
- Set a cookie from the SPA → more complex, doesn't fit the current stateless API design.
- Fetch the HTML with the auth header, wrap in a Blob, open via `URL.createObjectURL()` → clean, single-responsibility, works everywhere.

The Blob approach also gives a natural memory-management pattern: `setTimeout(() => URL.revokeObjectURL(url), 30000)` releases the blob after the new tab has had time to load. Codified as the standard pattern for "SPA needs to open API-served HTML in a new tab."

### Lesson 237 — Separate audit surfaces by task, not by data

Point-in-time posture and Auditor packages both read the audit trail, but they're different tasks: internal review vs external delivery. Combining them into one section would have crowded the UI + confused the "am I about to send this to an auditor?" gating. Two adjacent Profile sections with distinct titles + distinct actions map to the two mental models. The 5-line section explainer on each carries most of the UX weight — the operator reads the title, reads the one-liner, knows which one they want.

### Lesson 238 — Pre-existing HTML inline pickers don't survive Blob-URL delivery

The Ship 118'.c snapshot HTML has an inline `<form method="get">` date picker meant for the "SSH tunnel + hit the URL directly" workflow. When served via Blob URL, the form submits to `blob:...` which the browser rejects. We chose to document the "come back to SPA to change date" workflow rather than modify the snapshot HTML to detect Blob delivery. Simpler; keeps the two delivery paths independent (Blob-via-SPA vs direct-via-URL). If we later add SSO or session cookies, the inline picker starts working on both paths and the SPA workflow becomes shorter — a natural evolution, not a rewrite.

## Related arcs

- [[ship-118-prime-arc-retrospective-2026-09-05]] — the snapshot HTML this arc's Ship 123'.b button opens
- [[ship-119-prime-arc-retrospective-2026-09-05]] — the ledger HTML + admin endpoint this arc's Ship 123'.a button opens
- [[ship-120-prime-arc-retrospective-2026-09-05]] + [[ship-121-prime-arc-retrospective-2026-09-05]] + [[ship-122-prime-arc-retrospective-2026-09-05]] — grant-integrity chain protecting the audit trail these views read

## Deferred to Ship 124'+

1. **Audit-log inspector** — a filterable table view of the append-only audit tables (`posture_status_log`, `confirmation_log`, `client_facts_log`, etc.). Bigger UI scope (proper table pagination, per-column filters, tenant scoping via RLS). Would need a new admin endpoint per table or a unified `/api/v1/admin/audit-log?table=<name>&...` shape. Roughly a day of work; deferred until a real "the auditor is asking who confirmed what when" scenario prioritises it.
2. **Preview → Generate handoff** — after a preview, offer a "Generate URL for this exact configuration" prompt so the operator doesn't have to re-fill the form. Small UX win; not urgent.
3. **Snapshot inline picker via SSO/cookie** — see Lesson 238. When the auth model evolves, the inline picker becomes cross-workflow useful.

## PoC deployment plan

`scripts/ops/ship-123-poc-update.sh`:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash scripts/ops/ship-123-poc-update.sh
'
```

Expected: install.sh re-runs (baseline_grants.sql idempotent-fires; no schema changes), API restarts, JS version stamp shows `2026-09-06-audit-view-entries`, both new endpoints reachable (401/403 without API key = registered), deployment log at 12 entries.

Try in browser: Profile → "Compliance history" section (pick a date, click "View snapshot") + "Auditor packages" → "Generate audit package" modal → "Preview ledger" button opens a new tab without minting a token.
