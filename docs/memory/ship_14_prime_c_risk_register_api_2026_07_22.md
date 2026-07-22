---
name: ship-14-prime-c-risk-register-api-2026-07-22
description: "Ship 14'.c — Risk Register API surface: 4 internal endpoints + 3 external endpoints under external:risks:read scope; shared query module honours framework-role-model"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14'.c (2026-07-22) — third sub-arc of Ship 14. Wires the
schema_v87-extended `risks` table to a first request-layer
surface. Internal endpoints for the dashboard + admin flows;
external endpoints under the `external:risks:read` scope for
partner SDKs.

## What ships

### Shared query module (`rag/risk/`)

`rag/risk/__init__.py` + `rag/risk/queries.py` — single source
of truth for risk read shapes and query logic. Used by both
internal and external endpoint layers so their responses stay
identical modulo auth + rate-limit.

**Response models (Pydantic):**
- `LinkedControl` — one exploded control_ref carrying `role`,
  `subject`, `standard_id`, `standard_display`
- `RiskRow` — list-surface shape (13 core fields + linked_controls)
- `RiskDetail` — drill-in shape (RiskRow + 10 treatment-plan
  fields including all 5 schema_v87 additions)
- `RiskSummary` — dashboard aggregate (counts + heatmap + top-5)

**Query helpers:**
- `fetch_risks(conn, limit, offset, status, order)` — flat list
- `fetch_risk_detail(conn, risk_id)` — drill-in (None on RLS miss)
- `fetch_risk_summary(conn)` — counts + heatmap + top-5
- `linked_controls_view(control_refs, cur)` — explode array

Uses `rag/output/vocab/` for display names (Ship 7'.b) and a
lazy-cached read of the `standards` table for role + subject
metadata.

### Internal endpoints (`/api/v1/tenant/risks/*`)

All under `require_api_key` (existing internal auth):

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/tenant/risks` | Paginated flat list (limit 1-500, status filter) |
| `GET /api/v1/tenant/risks/summary` | Dashboard aggregate — feeds 14'.d |
| `GET /api/v1/tenant/risks/template` | Download canonical xlsx (14'.b static asset) |
| `GET /api/v1/tenant/risks/{risk_id}` | Drill-in (UUID validated via `RiskIdParam`) |

New `RiskIdParam` type in `rag/api_types.py` (per Ship 2'.k
path-param discipline).

### External endpoints (`/api/external/v1/risks/*`)

Under new `external:risks:read` scope (added to
`_EXTERNAL_SCOPES_ALLOWED` in api_server.py):

| Endpoint | Purpose |
|---|---|
| `GET /risks` | Bulk list + status filter + limit/offset + `summary` block |
| `GET /risks/summary` | Standalone aggregate |
| `GET /risks/{risk_id}` | Drill-in — 400 on malformed UUID / 404 on miss |

Registered via `rag/external/router.py` (imports new
`endpoints/risks.py`).

## Verification

API restarted cleanly; smoke tests confirm:

**Internal:**
- List: 35 total rows, linked_controls expanded with role +
  subject + display (e.g. `ISO27001:2022:5.15` → role=program,
  subject=['information_security'])
- Summary: total=35, by_treatment_option={'Accept':1,
  'Mitigate':34}, heatmap has 7 populated cells, top-5 returned
- Template: HTTP 200, 9716 bytes, `Microsoft Excel 2007+`
- Drill-in: valid UUID returns full RiskDetail with kpis=[] and
  rationale=null for pre-Ship-14'.b rows (nullable-safe)

**External:**
- List: same shape as internal + `summary` block + generated_at
- Summary: heatmap + top-5 + roles=['extension', 'program']
  present (framework-role-model discipline verified)
- Drill-in: 400 on malformed UUID, 404 on non-existent — RLS
  never leaks cross-tenant existence
- Requires `external:risks:read` scope on the API key

Dev key updated in-place to add the new scope for smoke
testing. Future keys created via the Profile UI (Ship 4'.g) can
select the new scope from the checkbox tree.

## Ship 14'.a addendum — reviewer discipline answers

**1. Role split?**

Yes — `linked_controls_view()` renders every control_ref as a
first-class entry carrying role + subject. Program (ISO 27001)
+ extension (ISO 27701) + obligation (GDPR when tenant refs
Art.X in a risk) all surface in the same array with no
hierarchical filter. Confirmed in smoke test: `roles=['extension',
'program']` returned side-by-side from a real risk row on Arion.

**2. Parallel CaseFile view?**

Not applicable — Ship 14'.c is HTTP-request-layer only. No
chat surfaces touched. `RiskSummary` is a Pydantic response
model, not a CaseFile field. Ship 14'.e adds the CaseFile
integration.

**3. Deterministic routing?**

Not applicable — no LLM calls, no classifier changes.
Endpoints route via FastAPI decorator paths.

**4. Guidance-normative discipline?**

Preserved — no engine mutations, no new MUSTs. Endpoints are
read-only over existing data.

## What did NOT ship

- **Write-side endpoints** (POST/PUT/DELETE for CRUD) — deferred.
  Primary flow is upload-driven via the canonical xlsx template
  (Ship 14'.b's `RowMappers.risks` + `risk_treatment` in
  workbook_importer). Direct API mutation could land in a future
  arc if partners request it.
- **DEMONSTRATES cascade lookup on obligation-linked risks** —
  when a risk references `GDPR:2016/679:Art.32`, the drill-in
  currently returns the raw ref with role=obligation. Full
  DEMONSTRATES traversal (per Ship's framework-role-model
  Phase 2b/2c) would additionally return the program/extension
  sources that demonstrate the obligation. Deferred to 14'.d or
  14'.e when the dashboard drill-in and chat surfaces need it.
- **Cross-collection Chroma retrieval on risks** — the `risks`
  table is structured. Semantic search on risk descriptions is
  the future Ship 15 candidate flagged in 14'.a.
- **SDK typed methods for the new endpoints** — the Python SDK
  in `sdk/python/arioncomply/` needs `.get_risks()` /
  `.get_risk_summary()` etc. Deferred to Ship 14'.f alongside
  eval + retro.

## Ship 14 progress

| Sub-arc | Status |
|---|---|
| 14'.a Design + role-model + case-file addendum | ✓ |
| 14'.b schema_v87 + xlsx template + upload path | ✓ |
| **14'.c API surface (internal + external)** | **✓ (this doc)** |
| 14'.d Dashboard cards + heatmap + drill-in | next |
| 14'.e Chat surfaces + cascade events | pending |
| 14'.f Eval + retro | pending |

## Impact on baseline

Eval confirmed: **228/229 PASS + 1 WARN + 0 FAIL** — baseline
unchanged. Only WARN is the pre-existing #200 gap_analysis vs
posture_check mismatch. Zero regressions from the new module +
7 endpoints + scope allowlist entry.

## Related

- [[ship-14-prime-a-risk-register-design-2026-07-22]] — design
  memo + architecture-constraint addendum
- [[ship-14-prime-b-risk-register-schema-template-2026-07-22]] —
  schema + template the endpoints serve
- [[ship-4-prime-arc-retrospective-2026-07-18]] — the external
  API discipline (auth + scope + rate-limit) the risks router
  inherits
- [[ship-7-prime-b-output-gateway-skeleton-2026-07-19]] —
  `*_display` companion pattern the LinkedControl surface uses
- [[framework-role-model-arc]] — the role model
  `linked_controls_view()` honours
- Ship 14'.d: dashboard cards + heatmap + drill-in (consumes
  these endpoints)
