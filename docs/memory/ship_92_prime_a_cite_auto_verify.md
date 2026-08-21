---
name: ship-92-prime-a-cite-auto-verify
description: Ship 92'.a — best-effort URL-basename resolver for workbook cite auto-verification. Scope-limited by design; Ship 92'.b system-attestation opens for the scalable path.
metadata:
  type: project
---

# Ship 92'.a — cite auto-verification (best-effort URL basename) (2026-08-21)

## Framing

Ship 89'.b + Ship 90'.a built the workbook-cite emission side. The
"loose end" was cite lifecycle close: when a tenant later uploads
the linked document, does the cite auto-verify? The intuitive
approach: match URL basename to `client_documents.filename`.

Ship 92'.a delivers this best-effort resolver. It works for tenants
whose cite URLs are clean file paths. It does NOT scale to
SharePoint / Google Drive / OneDrive / Confluence / Box / Notion
URLs where the filename lives in query params or is absent
entirely. Ship 92'.b opens with the scale-invariant model
(tenant-driven system attestation).

Design decisions locked with user:
- **Verify strictness**: URL match AND uploaded doc has present
  findings on same MUST (auditor-defensible; Ship 89'.b Lesson 98
  stored/cited separation)
- **Scope**: auto-verify only; missing-link notification deferred
  to Ship 92'.b (subsumed by system attestation)

## Delivered

**schema_v104** — `external_evidence_source.hyperlink_url TEXT NULL`
+ partial index `idx_external_evidence_source_url_active
(tenant_id, hyperlink_url) WHERE is_active AND hyperlink_url NOT NULL`.

**workbook_discovery.py** — new `_first_real_cite_url_in_column()`
extracts the first non-mailto data-row URL in a matched cite column.
`_column_has_real_cite_hyperlink` now delegates to it. `evaluate_pass`
stores `hyperlink_url` on `PassProposal.cite_bindings[must_id]`.

**workbook_persistence.py** — `_upsert_cite()` accepts `hyperlink_url`
kwarg + persists on both INSERT + UPDATE (COALESCE preserves existing
URL if new one is None).

**rag/cascade/cite_resolver.py** — new module:
- `_url_basename(url)`: extracts final path segment; strips query +
  fragment; unquotes URL-encoded; requires an extension (bare landing
  pages / mailto return None)
- `resolve_cites_on_document_upload(pg, tenant, doc_id, user_id)`:
  fetches active cites with URL; matches basename ILIKE filename;
  REQUIRES `document_findings` with `status='present'` on the same
  MUST as the cite; on match writes `external_evidence_verification_log`
  + updates cite (`last_verified_at=NOW()`, `next_review_due=NOW()+cadence`)
- Env gate: `USE_CITE_AUTO_VERIFY=1` default on (low blast radius —
  only fires when tenant has active cites)

**doc_pipeline.py** — new **Stage 4.8** after write path completes.
Best-effort: errors logged + swallowed; never blocks upload pipeline.

## Dogfood measurement

ISO Arion workbook has 5 active cites, all populated with URLs
after re-extract:

| MUST | URL kind | Result |
|---|---|---|
| `item:10.1:reg_trigger_type` | SharePoint (`.../:x:/s/labguide/IQCCI...`) | url_match=0 — basename is `Doc.aspx` fragment |
| `item:6.1.3:soa_reference` | SharePoint relative (`../../../.../Doc.aspx?...&file=Information Security Policy.docx`) | url_match=0 — basename is `Doc.aspx`; real filename in `file=` query param |
| `item:A.5.31:rev_scope_check` | Public URL (`https://nukib.gov.cz/`) | url_match=0 — no filename |
| `item:A.5.6:sigs_listed` | Public URL (`https://owasp.org/news/`) | url_match=0 — no filename |
| `item:A.6.3:rev_register_update` | SharePoint relative (`../../.../:x:/s/labguide/ETYphs...`) | url_match=0 — SharePoint URL |

**Auto-verify rate on Arion: 0/5** — the ISO workbook happens to
use SharePoint (path-fragment URLs) + public regulator sites (no
filename). No cite is expressed as a clean file path.

## Honest limitation

The URL-basename approach is **fundamentally scope-limited**:

- Fragile: every URL shape needs its own parser (SharePoint `file=`
  param, Google Drive metadata, OneDrive short-links, Box tokens...)
- Combinatorial: each new tenant tool = another adapter
- Auditor-opaque: "cite matched because SharePoint's `file=`
  convention" is brittle explanation
- Narrow overlap: only fires when URL is a clean path AND uploaded
  filename matches basename AND we parse the URL flavor correctly

Ship 92'.b pivots to **system attestation**: cite lifecycle closes
via tenant one-click confirmation when a matching upload lands,
not URL string-matching. Scale-invariant across every URL shape.

## Codified lessons

**Lesson 106: URL parsing doesn't scale as a matching primitive.**
Every SaaS + DMS URL scheme is different. Building N adapters is
combinatorial + fragile + brittle to break as vendors change URL
formats. Ship 92'.a's URL basename works ONLY where URLs are literal
file paths — a narrow slice. When the natural match dimension is
tenant-declared (which system does this doc belong to?) rather than
URL-parseable, the right primitive is tenant attestation, not URL
crawling.

**Lesson 107: Ship the honest scope, name the follow-up.** Ship
92'.a as-is catches the small subset that matters (clean-path
URLs). Not building the SharePoint / Drive / OneDrive adapters
avoids scope creep. Naming Ship 92'.b as the scalable follow-up
keeps the arc honest — best-effort resolver is a stepping stone,
not a destination.

## Files changed

- `db/schema_v104_cite_hyperlink_url.sql` (new)
- `rag/intake/workbook_discovery.py` — `_first_real_cite_url_in_column`
  helper + URL stored in `cite_bindings`
- `rag/intake/workbook_persistence.py` — `_upsert_cite` +
  `hyperlink_url` kwarg + persistence on INSERT/UPDATE
- `rag/cascade/cite_resolver.py` (new, ~200 LOC)
- `rag/intake/doc_pipeline.py` — Stage 4.8 wiring
- `docs/memory/ship_92_prime_a_cite_auto_verify.md` (this)

## Deferred to Ship 92'.b

- Tenant-driven attestation (one-click "yes, this doc is the cite target")
- `cite_attestation_prompt` schema
- Post-upload candidate detection via MUST-overlap (not URL shape)
- Notification kind `cite_attestation_pending` with inbox one-click
- Auditor-defensible: tenant confirms the match, not the URL parser

## Related

- [[ship-89-prime-b-cite-columns]] — cite emission side (prerequisite)
- [[ship-90-prime-a-cite-columns-sweep]] — catalog reach (prerequisite)
- Ship 3'-arc cite-mode: `external_evidence_verification_log`,
  `cite_verification_overdue` — the plumbing 92'.a hooks into
