---
name: ship-104-prime-arc-retrospective-2026-09-02
description: Ship 104' arc — self-serve tenant onboarding from a genuinely empty install. Quickstart form → tenant provisioned → framework picker gates Get Started → foundation templates + topics scoped to enrolled frameworks. First arc that lets a customer set themselves up entirely through the UI without CLI intervention. Verified end-to-end against Ship 102'.f wiped state on arionlabs-dr-01.
metadata:
  type: project
---

# Ship 104' — self-serve onboarding + enrolment-aware scoping (2026-09-02)

## Framing

Ship 102' + 103' proved a customer could receive a fully-populated install (Postgres + Neo4j + Chroma goldens via install.sh + LFS). But the last mile — a fresh customer actually CREATING their tenant + configuring their program — still routed through `scripts/dev/create_tenant.py` at the CLI. A real customer opening the UI on their on-prem box hit a topbar asking for an API key they didn't have.

Ship 104' closes that gap: **anonymous first-visit to a working tenant in one form.**

Verification target: the customer box (arionlabs-dr-01) after 102'.f's fresh install. Zero tenants, zero users, zero enrolments. Provision "Arion Networks s.r.o." entirely through browser interaction.

## What shipped

| Sub-arc | SHA | Deliverable |
|---|---|---|
| **104'.a** | `29926950` | Backend `POST /api/v1/quickstart` + `GET /api/v1/quickstart/status`. Bootstrap-only (409 once any tenant exists). Creates tenant + admin user + API key with runtime scopes. Neo4j untouched (no per-tenant graph state at signup). |
| **104'.b** | `da299cd4` → `bd26ef3c` (multi-commit) | UI Quickstart overlay + boot-time three-state router (localStorage key → connect / bootstrap available → overlay / neither → wait). Later commits fixed origin-defaulting for the topbar URL (was hardcoded to dev host), origin-namespaced localStorage keys (prevent cross-server key contamination), and a subtle urlparse-doesn't-decode-passwords bug in `_owner_conn()`. |
| **104'.c/d** | `16b7567d` | Framework picker card gating Get Started for empty tenants + Profile → Frameworks section for adding secondary frameworks post-signup. Shared enrolment logic in `rag/tenant_standards.py::enroll()` — one code path, two entry points (UI + create_tenant.py CLI). Seeds posture_controls for the enrolled standard. |
| **104'.e** | `475ade5c` | Enrolment-aware scoping across three surfaces: Get Started foundation templates filtered to enrolled frameworks; Topics greyed (not filtered — discovery preserved) for out-of-scope items with "add framework" hint; Dashboard already scoped by RLS on posture_controls. Chat left cross-framework (feature, not bug). |
| **104'.f** | this file | Arc retrospective. |

## Verified end-to-end

Live customer-box flow captured during the arc:

1. Fresh install on arionlabs-dr-01 (Ship 102'.f state — zero tenants)
2. Open `http://10.0.1.85:8080/ui/arioncomply.html`
3. Quickstart overlay renders — fill "Arion Networks s.r.o." / mutua@labguide.io / IT Consulting / Czechia / cloud-only
4. Overlay dismisses → Get Started renders → framework picker gates the page
5. Select ISO 27001 (marked Recommended) → "Enrol and continue"
6. `enrolments=1, postures=126, enrolled_standards='ISO27001:2022'` in Postgres
7. Get Started re-renders with filtered ISO 27001 foundation templates + hint about hidden GDPR/27701
8. Profile → Frameworks section shows ISO 27001 enrolled + Add buttons for GDPR + ISO 27701

Zero CLI touches to reach a working tenant. First time this has been true.

## Codified patterns

**Lesson 174: bootstrap-only signup gates prevent on-prem tenant spam.** The customer box exposes its API on the LAN. Anyone on the LAN could hit `/api/v1/quickstart` and provision themselves as the primary tenant, displacing the real customer. The bootstrap-only design (409 once any active tenant exists) prevents this without needing auth. Later flows will need real signup (email verification, rate limits) — that's out of scope for on-prem PoC.

**Lesson 175: urlparse does not decode URL-encoded passwords.** `urlparse("postgresql://u:P%40ng0@host/db").password` returns `'P%40ng0'`, not `'P@ng0'`. This bit `_owner_conn()` in `rag/onboarding/quickstart.py` for a full hour of on-box debugging — the API returned `bootstrap_available: false` masked by the fail-safe try/except, and the direct psycopg2 call finally showed the auth failure. Fix: use keyword-arg `psycopg2.connect(host=..., user=..., password=unquote(u.password))`, never round-trip through a DSN string. Documented in the module's comment so future readers see it.

**Lesson 176: hardcoded dev-server URLs + un-namespaced localStorage keys leak between origins.** The UI's topbar `api-url` input had `value="http://172.211.244.144:8080"` (the dev host) hardcoded. First customer to visit their own box's UI got auto-connected to the dev host, saw dev data. Fix: default the input to empty; JS sets it to `window.location.origin` on boot. Also namespaced `localStorage` keys by origin (`apiKey:http://10.0.1.85:8080`) so a session on one server doesn't populate the key for another.

**Lesson 177: framework picker as a gate, not a redirect.** Considered a signup wizard (welcome → framework → profile → get-started sequence) but chose to gate Get Started itself with the framework picker. Reason: the phase strip + landing already establish the mental model; a wizard would duplicate. Empty state → Framework picker replaces the templates list until one is picked. Once enrolled, Get Started renders normally with filtered scope. Simpler than a wizard; equally clear about "you must pick before proceeding."

**Lesson 178: grey-out beats filter for discovery surfaces.** For Topics, filtering to enrolled frameworks would hide the 8 GDPR-primary topics from an ISO 27001-only tenant, robbing them of the "oh, DSR handling exists — I should think about that when I enrol in GDPR later" signal. Greying non-enrolled topics preserves discovery while making scope visible. For Get Started (curated foundation sequence), the same reasoning DOESN'T apply — that IS a strict sequence and hiding out-of-scope prevents wasted downloads. Rule of thumb: **filter operational surfaces, grey discovery surfaces.**

**Lesson 179: mode='dashboard' at page bottom fires loadDashboard even without connect().** During the Quickstart overlay diagnostic, we saw 401s on `/api/v1/dashboard/coverage` etc even though Case 3 in `bootQuickstartCheck` explicitly avoided calling `connect()`. Cause: `mode = 'dashboard'` at global JS scope + `_applyHashRoute()` at page-end apparently triggers dashboard loads regardless. Not fixed in this arc (goes away once user completes Quickstart + normal flow resumes), but a future cleanup should route boot-time loads through a single async guard so unauth'd background fetches don't fire.

**Lesson 180: shared enrolment logic + two entry points.** `rag/tenant_standards.py::enroll()` is called by both the UI POST endpoint (framework picker + Profile Add button) and `scripts/dev/create_tenant.py --frameworks` at CLI. One code path → identical state regardless of entry. Same pattern applied in Ship 102'.b for Neo4j loading (single-loader → JSON snapshot replacing 5-loader chain). Convention emerging: **when a workflow has multiple entry points, extract to a module + call from all callers.** Duplicated business logic drifts.

## Deferred

- **Document upload verification from empty tenant.** The natural next step. Provisioned tenant, enrolled framework, seeded postures — but haven't yet fed a document through the intake pipeline to confirm it lands correctly. Not shipped in this arc because the pipeline is already well-covered by earlier ship arcs (11', 17', 33'). Verification will happen the first time you upload a real document; if anything breaks, it's a Ship 105' issue.

- **Post-boot loadDashboard 401 cleanup.** The 401 stream on unauth'd boot noted in Lesson 179. Cosmetic — no functional impact after signup — but should be tidied.

- **Real SaaS signup flow (Ship 200'? distant).** If ArionComply ever ships as multi-tenant SaaS, bootstrap-only is wrong. Need: real auth (email verification), rate limits, tenant-quota enforcement, terms acceptance. Different threat model, different arc.

- **Un-enroll from framework.** Currently `enroll()` inserts + seeds; no complement to remove. Un-enrol has knock-on effects (posture rows with evidence, cascade events, cross-framework bridges) — deserves its own arc after real customer usage shows what the un-enrol scenarios actually look like.

- **Framework prerequisite hints.** ISO 27701 is a privacy extension on top of ISO 27001. A tenant enrolling in 27701 without 27001 will have a weird posture surface. Future: warn or gate at the picker level. Not urgent while the picker only offers 3 standards.

## Related

- [[ship-102-prime-arc-retrospective-2026-09-01]] — golden-image consolidation that gave us the fresh-install target
- [[ship-103-prime-arc-retrospective-2026-09-01]] — Git LFS distribution that made the 141 MiB Chroma tar reachable on customer clone
- `rag/onboarding/quickstart.py` — the module that fires when nobody's home
- `rag/tenant_standards.py` — shared enrolment logic used by both UI + CLI
