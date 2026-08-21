---
name: product-principle-cite-expose-and-track
description: For cite-mode evidence, ArionComply exposes + tracks; the tenant attests. The system never auto-attests on the tenant's behalf.
metadata:
  type: project
---

# Product principle — cite-mode: expose + track, never auto-attest

**Codified 2026-08-21 in Ship 92'.f.**

## The principle

When workbook cites reference external evidence (SharePoint policies,
Google Drive docs, OneDrive files, Confluence pages, regulator URLs,
etc.), ArionComply:

1. **Exposes** the cite on the ledger — leaf, MUST, system, URL,
   verification cadence.
2. **Tracks** its lifecycle — when the cite was created, when it
   was last verified, when it's next due, when it went stale.
3. **Nudges** the tenant when action is needed — dashboard cards,
   Ship 3'.g cadence notifications, Ship 92'.b attestation prompts.
4. **Records** the tenant's decision — every `verification_log`
   row has a named human (`verified_by`) who owns the attestation.

The system NEVER writes `external_evidence_verification_log`
without an explicit tenant decision. No silent machine
attestations. Not on filename match. Not on `file=` query param
extraction. Not on any URL-shape heuristic — however clever.

## Why

**Auditor-defensible by construction.** A cite that says "we point
at Information Security Policy v3 in SharePoint" + tenant
attestation on 2026-08-21 with a named person + a
`changes_detected` narrative is auditor-strong evidence. A cite
auto-verified by a URL parser produces the same DB row but with
weaker provenance — "the system decided" doesn't hold up in a
compliance audit the way "the compliance owner attested" does.

**Scale-invariant.** Every SaaS + DMS URL scheme is different:
SharePoint's `file=` query param, Google Drive's file-id-in-URL,
OneDrive's short-link tokens, Confluence's page IDs, Notion's
slug+ID hybrids, Dropbox's `?rlkey=...`, Box's opaque tokens,
internal DMS URLs with query-based file lookups. Building N URL
parsers is combinatorial + fragile + auditor-opaque. Building
"we notice + ask the tenant" scales linearly and works on the
tenant's actual documents, whatever URL shape they use.

**Compliance-native.** ISO 27001 clause 6.1.3 (SoA) + ISO 27002
guidance + GDPR Art.5 accountability all frame evidence
maintenance as a tenant discipline. The auditor asks "how do you
know this is current?" and expects "our compliance owner reviewed
it on X" — not "the system fetched the URL and it returned 200."
The cite-mode surface should reflect this operating discipline.

**Trust boundary.** Processing external links crosses a boundary —
the system starts making inferences about tenant content stored in
external systems (some of which may be air-gapped or require creds
we don't have + would be uncomfortable holding). Exposing + tracking
keeps every system claim grounded in what the tenant explicitly
told us.

**Human-in-the-loop discipline** (see [[human-in-the-loop-positioning]]).
ArionComply assists, doesn't decide. Cite-mode attestation is one
of the most consequential decisions in the audit trail; it needs a
human at the point of decision.

## What this rules OUT

- Fetching cite URLs to check if they return 200
- Parsing SharePoint / Drive / OneDrive URLs to extract filenames
  for auto-match
- Any code path that writes `external_evidence_verification_log`
  without a `verified_by` set to a real user_id at the moment of a
  tenant action
- Automated "the URL looks like the file we already have, mark it
  verified" logic

## What this ALLOWS (candidate generation)

The system CAN and SHOULD do the noticing work — but every notice
lands as a **candidate for tenant confirmation**, not as an
attestation:

- **Ship 92'.b attestation prompts** — MUST overlap on doc upload
  creates a `cite_attestation_prompt`; tenant one-clicks confirm
  or dismiss. Confirm writes `verification_log`. The one-click is
  the human decision.
- **High-confidence signals inside a candidate** — if URL basename
  matches an uploaded filename AND MUSTs overlap AND (future)
  content extraction agrees, the prompt can carry a "we're 95%
  sure — one click to confirm" hint. Same one-click. Same
  auditor artifact.
- **Freshness reminders** — Ship 3'.g `cite_verification_overdue`
  nudges tenants when cadence expires. The tenant then attests via
  the existing modal with a `changes_detected` narrative.

The distinguishing feature: **every `verification_log` row has a
real human `verified_by` who acted at the moment of writing.**

## What Ship 92'.f retired (2026-08-21)

Ship 92'.a's `resolve_cites_on_document_upload` originally wrote
`verification_log` rows automatically when a URL basename matched
an uploaded filename + the linked doc had `status='present'`
findings on the same MUST. This was a silent machine attestation
— a low-blast-radius drift from the expose+track principle that
would have compounded as more URL-adapter code got added.

Ship 92'.f downgrades the function: on match, it now creates a
`cite_attestation_prompt` with `confidence='high'` (new field)
instead of writing `verification_log`. The prompt surfaces on the
same Ship 92'.d card as MUST-overlap-only prompts, but with a
"strong match — one-click confirm recommended" visual hint.

Tenant still owns the decision. Auditor still sees a
`verification_log` row when the tenant confirms. Same outcome,
better provenance.

## Codified follow-on rules

- **New cite features go through the attestation surface.** Any
  future work that surfaces cite-related information to tenants
  (new URL parsers, LLM link inspection, cross-system evidence
  matching, whatever) creates candidates, not attestations.
- **`external_evidence_verification_log.verified_by` is
  compliance-load-bearing.** No sentinel UUIDs. No system users.
  Real tenant user_id at the moment of the tenant's decision. If
  a code path can't populate it, that path can't write to the log.
- **Cite processing features are optional; cite tracking is
  mandatory.** The freshness cadence + attestation prompts are the
  non-negotiable path. Any processing improvement (better URL
  parsing, content extraction, cross-doc bridging) rides on top
  of the tracking surface.

## Related memories + arcs

- [[human-in-the-loop-positioning]] — ArionComply assists, client
  owns posture. Cite-mode expose+track is that principle applied
  to external evidence.
- [[product-principle-evidence-stored-vs-cited]] — stored vs cited
  coexistence. Cited = provenance; stored = evidence. Expose+track
  is what makes cited mode auditor-defensible.
- [[ship-89-prime-b-cite-columns]] — cite emission (workbook side)
- [[ship-92-prime-a-cite-auto-verify]] — original URL-basename
  auto-verify (retired via Ship 92'.f — downgraded to candidate
  generation)
- [[ship-92-prime-b-cite-attestation]] — MUST-overlap attestation
  prompts (the canonical cite lifecycle-close path)
- [[ship-92-prime-d-cite-attestation-dejargonize]] — humanized
  attestation card surface
