---
name: doc-mappings-no-tenant-specific
description: "POLICY 2026-06-10 (e3c209d + 153e171): db/doc_mappings/*.yaml and db/workbook_mappings/*.yaml are GLOBAL. No tenant-specific abbreviations, naming conventions, or sheet-shape shortcuts. Tenant overrides need a separate mechanism (none built yet)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

`db/doc_mappings/*.yaml` and `db/workbook_mappings/*.yaml` are
shared across all tenants. The fingerprint tokens determine which
docs/sheets get matched — pollute them with one tenant's
abbreviations and you create false positives for every other
tenant.

## The trigger case (2026-06-10)

`information_security_policy.yaml` carried
`[information, security, data, management]` flagged as "Arion
convention" — meant to match Arion's "Information Security & Data
Management Policy" upload.

Cross-fired on `ISMS Change Management Process.docx` via topic-
token union: topic_tokens supplied `information + security + data`
from the doc body, filename supplied `management`. All 4 tokens
present → match at filename score 1.0 → confidence 0.9 (top match)
→ wrong umbrella scope to the LLM.

The "win" from the Arion-specific entry was zero anyway: Arion's
filename also matches the generic `[information, security, policy]`
fingerprint (its tokens include `information`, `security`,
`policy`). So removal was pure subtraction of false positives.

Followed up with a sweep of `db/workbook_mappings/` — found 5
more YAMLs with the same shape of pollution:

| YAML | Removed token | Reason |
|---|---|---|
| `sig_register.yaml` | `[spec, int]` | Arion abbreviation |
| `sig_engagement_review.yaml` | `[spec, int]`, `[int, engagement]` | Arion + ambiguous |
| `isms_manual_change_log.yaml` | `[doc, chng, control]` | Arion "Chng" |
| `pentest_review.yaml` | `[sec, ass]` | Arion shorthand, ambiguous |
| `legal_register_review.yaml` | `[legal, compl]`, `[regul, compl]` | Pseudo-generic but Arion-derived |

All 5 still have their full-word fingerprints — the canonical
case still matches; only the shortcuts went.

## Rules going forward

- **No tenant-specific tokens.** If you're tempted to write a
  fingerprint that "matches what {tenant} calls their X", check
  whether the generic fingerprint already covers it. It probably
  does, because the generic form names the obvious words.
- **No "tenants commonly abbreviate X as Y".** That phrasing is
  the same anti-pattern wearing a generic mask — Y came from
  somewhere specific, and other tenants either use the generic
  form already or use a different abbreviation. Either way Y
  doesn't earn its slot.
- **Ambiguity check.** Even if a token IS generic, ask "could
  this fingerprint match something the YAML wasn't meant to
  cover?" `[sec, ass]` matched penetration tests OK but could
  also match Security Association or Section Assessment — drop
  for ambiguity even setting aside the tenant-origin issue.

## What's still in scope

Comments referencing a tenant by name are fine. E.g. "Arion has
'Access Rev. Log Non-PII Systems' sheet — that's why we accept
`[access, revocation]` and `[access, removal]` as variants."
Comments document WHY a generic fingerprint exists; they don't
change matching behaviour.

`header_row_hints` like `[1, 2, 3]` with a comment "Arion's
sheet has headers at row 3" are fine — the *hint* is generic
(scan rows 1-3), the *rationale* is the tenant example.

## Out of scope (tracked separately)

- `api_server.py` warm-up loads Arion's tenant UUID at startup.
  Runtime config debt — needs an env var or all-tenants loop.
  Different category of tenant pollution.
- Per-tenant override mechanism: if a tenant genuinely needs
  custom fingerprints (e.g. a deeply non-standard internal naming
  scheme), the right design is a `db/tenant_doc_mappings/<tid>/
  *.yaml` layer that the discovery code unions with the global
  set. Not built yet — wait until a real tenant needs it.

## Related

- [[doc-discovery-vocabulary-gap-fix]] — the synonym layer this
  rule depends on (synonyms ARE global; abbreviations are not).
- [[intake-determinism-levers]] — the unmatched-patterns endpoint
  surfaces gaps that a tenant override mechanism would otherwise
  cover.
