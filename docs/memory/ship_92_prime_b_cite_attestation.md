---
name: ship-92-prime-b-cite-attestation
description: Ship 92'.b — MUST-overlap tenant attestation for workbook cites. Scale-invariant across every URL shape because the signal is MUST overlap, not URL parsing.
metadata:
  type: project
---

# Ship 92'.b — cite attestation (MUST-overlap tenant one-click) (2026-08-21)

## Framing

Ship 92'.a delivered URL-basename auto-verify. Dogfood confirmed
the honest limitation: 0/5 cites auto-verified on ISO Arion because
all 5 URLs are SharePoint (path fragment `Doc.aspx`; filename in
`file=` query param) or public regulator URLs (no filename).

URL parsing doesn't scale — every SaaS/DMS URL scheme is different,
combinatorial adapters are fragile + auditor-opaque.

**Ship 92'.b pivots to the scale-invariant primitive**: MUST
overlap between uploaded documents and active cites. When a doc's
findings hit the same MUST as a cite, that's the candidate signal.
Tenant one-click confirms the match. No URL parsing anywhere.

Design decisions (user-selected):
- **Surface**: dashboard drill-in (deferred to UI polish arc; API +
  server-side ready in Ship 92'.b)
- **Aggressiveness**: one prompt per (cite, candidate_doc, MUST) —
  tight overlap, low noise

## Delivered

**schema_v105** — `cite_attestation_prompt` table:
- Columns: id, tenant, cite_id, candidate_document_id, must_id,
  leaf_id, control_ref, status (`pending`/`confirmed`/`dismissed`/
  `auto_expired`), resolved_at, resolved_by, dismissed_reason,
  verification_log_id, expires_at (default `NOW() + 30 days`)
- UNIQUE(tenant, cite_id, candidate_document_id) WHERE
  status='pending' — dedup by construction; re-uploading same doc
  against same cite doesn't spam
- RLS: `USING + WITH CHECK` on `app.tenant_id` (Ship 92'.b.iv
  discovered `USING` alone rejects inserts — noted for future
  policy authoring)
- GRANT SELECT/INSERT/UPDATE/DELETE on arioncomply_app

**cite_resolver.py extensions** (~200 LOC on top of Ship 92'.a):
- `create_attestation_prompts_on_document_upload(pg, tenant, doc_id)`:
  scans active cites; for each cite whose must_id has a
  `status='present'` finding from the uploaded doc, INSERT prompt
  with ON CONFLICT DO NOTHING dedup
- `confirm_attestation(pg, tenant, prompt_id, user_id)`: writes
  `external_evidence_verification_log` (auditor trail) + bumps
  `last_verified_at` + `next_review_due` + marks prompt confirmed
- `dismiss_attestation(pg, tenant, prompt_id, user_id, reason)`:
  marks prompt dismissed with reason; no verification_log write

**doc_pipeline.py** — Stage 4.8b runs after Stage 4.8a
(URL-basename auto-verify), same DB connection.

**api_server.py** — 3 endpoints on `/api/v1/cite-attestations/`:
- `GET /pending` — list pending prompts with candidate + cite context
- `POST /{id}/confirm` — one-click tenant confirmation
- `POST /{id}/dismiss` — reason-tagged tenant dismissal

## Dogfood on ISO Arion

Re-extract triggered Stage 4.8b — 3 prompts created (workbook itself
extracts to 3 of its own cited MUSTs: A.5.6 sigs_listed / 10.1
reg_trigger_type / 6.1.3 soa_reference; the workbook is both cite
source AND finding source):

```
Stage 4.8a: cite auto-verify — scanned=5 url_match=0 must_match=0 verified=0
Stage 4.8b: cite attestation prompts — scanned=3 candidates=3 created=3 existing=0
```

**Confirm flow test** (`POST /api/v1/cite-attestations/{id}/confirm`):
- A.5.6 prompt → status=`confirmed`, verification_log row written,
  cite `last_verified_at=NOW()`, `next_review_due=NOW()+cadence`.
- ✓ End-to-end verified.

**Dismiss flow test** (`POST /api/v1/cite-attestations/{id}/dismiss`):
- 10.1 prompt → status=`dismissed`, reason "internal doc — not the
  SharePoint reference target" recorded. Cite NOT touched.
- ✓ Reason preserved in dismissed_reason column for auditor trail.

**Third prompt stays pending** for future tenant action.

## Codified lessons

**Lesson 108: MUST overlap is scale-invariant; URLs aren't.** Every
SaaS + DMS URL scheme is different (SharePoint `file=` param,
Drive metadata, OneDrive short links, Notion slugs). MUST overlap
is compliance-domain-native: two evidence sources for the same
compliance requirement CAN be the same evidence, and the tenant
knows. Building on the compliance signal (MUST-id equality) instead
of the vendor signal (URL parseability) gets scale for free.

**Lesson 109: RLS `USING` alone breaks INSERT.** Postgres RLS
policies default to `WITH CHECK false` when the clause is omitted
— reads scoped, writes rejected. Every new tenant-scoped table
needs BOTH `USING` and `WITH CHECK` (or an explicit `WITH CHECK
true` for permissive writes). Ship 92'.b.iv dogfood surfaced this
via silent 0-rows-created on the INSERT. Also: table-level GRANT
required — RLS scopes rows within an already-permitted table, but
doesn't grant table access. Both required for new tables.

**Lesson 110: Tenant owns match decisions when the system can't
verify.** Ship 92'.a tried to automate the cite→doc match; only
works on a narrow URL-shape slice. Ship 92'.b delegates the
decision to the tenant via one-click confirm/dismiss. The system
does the noticing (MUST overlap); the tenant does the judging.
Auditor-defensible without vendor-shape parsers. Same pattern
should apply anywhere the system can't reliably infer semantic
identity — surface candidates, ask, log.

## Files changed

- `db/schema_v105_cite_attestation_prompt.sql` (new)
- `rag/cascade/cite_resolver.py` — 3 new functions
  (`create_attestation_prompts_on_document_upload`,
  `confirm_attestation`, `dismiss_attestation`) + module docstring
- `rag/intake/doc_pipeline.py` — Stage 4.8b wiring (alongside 92'.a)
- `api_server.py` — 3 endpoints under `/api/v1/cite-attestations/`
- `docs/memory/ship_92_prime_b_cite_attestation.md` (this)

## Deferred to Ship 92'.c (or later)

- **UI** — dashboard drill-in card listing pending prompts with
  inline Confirm/Dismiss buttons. Server-side ready; UI hand-edit
  on the SPA HTML deferred to a UX polish arc. Tenant can act via
  API today; future arc adds discoverability.
- **Notification kind** — `cite_attestation_pending` notification on
  Inbox when prompts land. Optional aid to discovery; the dashboard
  card is the primary surface.
- **Auto-expire sweep** — background job to mark prompts >30d old
  as `status='auto_expired'`. Small addition to `rag/scheduler/tick.py`.

## Related

- [[ship-89-prime-b-cite-columns]] — cite emission
- [[ship-90-prime-a-cite-columns-sweep]] — catalog reach
- [[ship-91-prime-a-c-cite-columns-criterion]] — cite discipline codified
- [[ship-92-prime-a-cite-auto-verify]] — URL-basename resolver
  (best-effort, honest scope limit; Ship 92'.b succeeds where 92'.a couldn't)
