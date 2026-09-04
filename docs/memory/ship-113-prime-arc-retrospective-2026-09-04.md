---
name: ship-113-prime-arc-retrospective-2026-09-04
description: Ship 113' arc — de-jargonized Profile scoping section, 6-region multi-select, sector controlled vocabulary, 3-bucket employee size
metadata:
  type: project
---

# Ship 113' — de-jargonized Profile scoping + regions + sector vocab

**Date:** 2026-09-04 (same day as Ship 110' → 112' cluster)
**Commits:** `c58e46fc` (a) → `09c09d1b` (b) → `975cad2e` (c) → `672a887a` (d) → this doc (e)
**Trigger:** operator screenshot of the Profile "About your organisation" section (from Ship 110'.c) with an itemised critique — every question was framework-flavoured (GDPR/Article 30/EU/UK GDPR), Q2 depended on Q1's individuals ("which individuals?"), size was Yes/No 250+ instead of 3-bucket, sector was Quickstart-only free-text (Ship 111'.c PoC captured "IT Consulting" that way).

## Motivation

Ship 110'.c shipped the first pass of Profile scoping questions. It worked but leaked framework vocabulary into tenant-facing prose in a way that broke the [[dejargonize-ux-pass-2026-07-01]] discipline. Since we don't know which frameworks apply to a given tenant until AFTER they answer scoping questions, calling out specific regulations in the question text puts the cart before the horse.

Operator gave explicit direction:
1. No named frameworks in question text.
2. Every question self-contained (no "these individuals" references).
3. Q11 (company size) as 3-bucket radio, not yes/no.
4. Sector as controlled vocabulary (loosely NIS 2 aligned).
5. Q2 regions: extend beyond eu/uk to cover all regions.
6. Q4 roles: entity can hold multiple roles simultaneously (already booleans, keep as-is).
7. Sector moves from Quickstart to Profile (Q11 → Q12 in the new layout).

## Delivery summary

### 113'.a — Schema + constants + rule updates (`c58e46fc`)

**schema_v113:**
- 4 new region columns on `client_facts`: `us_data_subjects`, `ca_data_subjects`, `apac_data_subjects`, `other_data_subjects`. Existing `eu_data_subjects` + `uk_data_subjects` unchanged. 6 region buckets total.
- New `employee_size_bucket TEXT CHECK IN ('small','medium','large')`. Complements the existing `employee_count_250_plus` boolean — the bucket is what the UI writes; the boolean is what applicability rules read; Ship 113'.b keeps them in sync via a derivation on write.

**New modules:**
- `rag/scoping/regions.py` — `REGION_LABELS` list + `COUNTRY_TO_REGION` ISO alpha-2 map + `region_of_country()` helper. 6 region keys total.
- `rag/scoping/sectors.py` — 21 sector entries (10 NIS 2 Annex I essential + 7 NIS 2 Annex II important + 3 commercial + 1 catchall) with `code`/`label`/`tier` fields.

**Ship 110'.d rule updates in `applicability.py`:**
- `not_controller` — dropped `role_joint_controller` from `driving_facts`. The joint-controller question no longer appears in the Profile questionnaire (rare + confusing for most tenants). Keeping the guard would have prevented the rule from ever firing. Semantically: `role_controller=False` implies not a joint controller either.

### 113'.b — Backend PUT extensions + region derivation (`09c09d1b`)

`api_server.py`:
- `_SCOPING_FACTS_BOOL_ALLOWED` extended with 4 new region cols (16 booleans total).
- `_SCOPING_FACTS_TEXT_ALLOWED` extended with `employee_size_bucket`.
- New `_EMPLOYEE_SIZE_BUCKET_ALLOWED` enum.
- PUT `/api/v1/tenant/facts` gains:
  - Enum validation on `employee_size_bucket` (rejects non-`{small,medium,large}` with 400)
  - Reject empty-string `sector` (400)
  - Derive `employee_count_250_plus` from `employee_size_bucket` on write ("large" → True, small/medium → False, None → no-op)

`rag/onboarding/quickstart.py::_initial_client_facts()`:
- Uses `region_of_country()` from Ship 113'.a. Retires the inline `if ctry in _EU_EEA_COUNTRIES` + `if ctry == "GB"` block. Now covers all 6 regions.

Test coverage extended (13 assertions total in `tests/test_country_normalization.py`):
- US country → us_data_subjects=True derived
- Australia → apac_data_subjects=True derived
- Brazil (fallback) → other_data_subjects=True derived
- Existing eu/uk derivation tests still pass unchanged

### 113'.c — Profile UI rewrite (`975cad2e`)

`GET /api/v1/tenant/profile` response gains a `scoping_vocab` block:
- `regions[]` — 6 entries {key, column, label}
- `sectors[]` — 21 entries {code, label, tier}
- `sector_tiers` — tier code → group heading
- `employee_size_buckets` — 3 entries {code, label, detail}

Vocab lives in Python only (`rag/scoping/*`); client is a pure consumer. One place to add a new region or sector.

`static/arioncomply.html::renderScopingSection()`:
- `SCOPING_QUESTIONS_V2` structure supports 4 question types:
  - `boolean` — existing Yes/No radio pattern (10 questions use it)
  - `region_multi` — 6 checkboxes writing 6 boolean cols (one PUT per click)
  - `size_bucket` — 3-option radio writing employee_size_bucket
  - `sector_dropdown` — `<select>` grouped by tier writing sector code

Question re-writes:

| Old (Ship 110'.c) | New (Ship 113'.c) | Column(s) |
|---|---|---|
| "Do you process personal data about identifiable individuals?" | "Do you collect or store information about individual people?" | `processes_personal_data` |
| "Do any of the individuals live in the EU or EEA?" + "in the UK?" + "outside the EU/UK?" | "In which regions do the people whose information you hold live?" (6-checkbox multi-select) + "Does personal information cross international borders?" | 6 region bools + `transfers_data_outside_eu` |
| "Are you a data controller?" / "processor?" | "Do you decide what personal information gets collected and what happens to it?" / "Do you handle personal information for other organisations, following their instructions?" | `role_controller`, `role_processor` |
| "Are you a public authority or public body?" | (unchanged pattern, cleaner hint) | `public_authority` |
| "Do you handle special category personal data?" | "Do you handle any of these categories of information?" | `special_category_data` |
| "Do you make automated decisions about people?" | "Do computer systems make significant decisions about individuals without a human reviewing them?" | `automated_decision_making` |
| "Do you have physical premises where staff work?" | "Do you have physical offices, warehouses, retail locations, or facilities where staff work in person?" | `has_physical_premises` |
| "Do you develop or ship software products?" | "Do you build or sell software products?" | `develops_software` |
| "Do you have 250 or more employees?" (Yes/No) | "How many people work at your organisation?" (1-50 / 51-250 / >250 radio) | `employee_size_bucket` + auto-derived `employee_count_250_plus` |
| — | "Which sector best describes what your organisation does?" (dropdown) | `sector` (moved from Quickstart) |

Removed the joint-controller question. Removed the Article 30 exemption reference. Removed the UK GDPR reference.

JS version: `scoping-rewrite`.

### 113'.d — Quickstart form: remove sector (`672a887a`)

Sector drops from Quickstart's 6 fields → 5 fields. Backend `QuickstartRequest.sector` stays optional for API compatibility (`scripts/dev/create_tenant.py` still accepts `--sector`, direct API callers still can). Frontend body sends `sector: null` so newly-Quickstarted tenants get a clean-slate default and pick from the Profile dropdown.

JS version: `quickstart-no-sector`.

## Lessons codified

### Lesson 198 — De-jargonizing means asking about the fact, not the regulation

Ship 110'.c had questions like "Are you a data controller?" — this is asking the tenant to know GDPR vocabulary. The rewrite asks "Do you decide what personal information gets collected?" — the underlying fact. Same downstream boolean, better tenant experience. This principle generalizes: **whenever a compliance concept has a specific regulatory name, ask about the phenomenon it describes, not the name of the concept**.

### Lesson 199 — Multi-select simplifies "which of these applies"

Ship 110'.c split "EU subjects?" and "UK subjects?" into two Yes/No questions. Semantically they're facets of the same question ("where are your subjects?"), so a multi-select is more natural. It also generalizes: when we later add LGPD (Brazil), CCPA (US-state), APPI (Japan) applicability rules, the region checkboxes already exist and just need new derivation rules. No new questions.

### Lesson 200 — Company size buckets vs booleans

`employee_count_250_plus` (bool) is what the applicability rules read. But the tenant thinks in bands ("we're a small company", "we're mid-size"). Ship 113' captures the bucket in a text column AND derives the boolean on write. Same pattern applies to other numeric-threshold facts (revenue, headcount, data-subject volume) — capture the human-natural bucket, derive the boolean.

### Lesson 201 — Controlled vocabulary as data, not code

Ship 113'.a put sector list in `rag/scoping/sectors.py` — a Python constants file. Ship 113'.c serves it via the profile GET response. Adding a new sector means editing one file. If we'd hardcoded the dropdown options in HTML, we'd have UI + backend allowlist + validation all requiring separate edits. **Vocab is data. Data lives in one place.**

### Lesson 202 — Small removals compound

Removing sector from Quickstart (Ship 113'.d) was 6 lines of HTML + a `null` in one place. Trivial patch. But Quickstart is the tenant's first impression, and every field removed = faster time-to-first-value. Same principle applies to unnecessary confirmations, "advanced" toggles, sensible defaults. Cheap wins compound.

## Related arcs

- [[dejargonize-ux-pass-2026-07-01]] — the codified UX principle this arc doubles down on
- [[ship-110-prime-arc-retrospective-2026-09-03]] — Ship 110'.c which shipped the first-pass questions this arc rewrites
- [[ship-111-prime-arc-retrospective-2026-09-04]] — Ship 111'.c backfill script whose diagnostic output surfaced the country-format bug that led to Ship 112' and this arc
- [[ship-112-prime-arc-retrospective-2026-09-04]] — country normalization + dropdown; complementary to this arc's regions multi-select

## Deferred to Ship 114'+

1. **NIS 2 curation** — Ship 113'.a's sector vocab was designed to fit NIS 2 essential/important entities. When the operator resumes Ship 105' NIS 2 curation, sector-scope applicability rules can hang off `client_facts.sector`.
2. **Sector CHECK constraint** — currently `sector` is free-text soft-validated. Once the legacy free-text values on existing tenants are migrated (Ship 111'.c PoC has "IT Consulting" which maps to "ict_services"), add a CHECK constraint.
3. **`joint_controller` question** — dropped from the Ship 113' Profile section. If future demand emerges (organisations with genuine joint-controller structures), it can be added back as an "Advanced" section without touching the main questionnaire.
4. **Multi-region regulatory rules** — LGPD, CCPA, APPI, PDPA (Singapore) etc. Region columns now exist to hang derivation rules from; each new regulation needs a curator arc + one new `AppRule` in `rag/scoping/applicability.py`.

## Eval + PoC deployment plan

Eval running now on the dev box. Assuming baseline holds (237/238 PASS + 1 known WARN), push + deploy pattern is the standard Ship 111'.d flow:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash deploy/install.sh &&
  sudo systemctl restart arioncomply-api
'
```

`install.sh` applies `schema_v113` via the update-mode migration loop (Ship 111'.a). No manual backfill needed — existing arionlabs-dr-01 tenant will have `us/ca/apac/other_data_subjects=false` and `employee_size_bucket=null` from the schema defaults, which correctly renders as "Not answered" in the new Profile section.

The Path B fix from Ship 112' already put `eu_data_subjects=true` for Arion Networks s.r.o., so their region multi-select will show EU/EEA pre-checked with the "Assumed from your country" hint.
