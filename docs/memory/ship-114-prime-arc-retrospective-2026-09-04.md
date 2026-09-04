---
name: ship-114-prime-arc-retrospective-2026-09-04
description: Ship 114' arc — region backfill for pre-Ship-113' tenants + sector CHECK constraint + strict API sector validation
metadata:
  type: project
---

# Ship 114' — sector CHECK + region backfill + strict validation

**Date:** 2026-09-04 (fourth arc same day as Ship 110'/111'/112'/113')
**Commits:** `9b9d7d91` (a+b+c bundled) → this doc + deploy script (d)
**Trigger:** two loose ends surfaced during Ship 113' deploy:
1. Arion Networks s.r.o. showed `eu_data_subjects=FALSE` after Ship 113' deployment — Path B never persisted OR got reverted.
2. Ship 113' shipped a soft-validated sector column (Ship 113'.b rejected empty string only) — customer had legacy `sector="IT Consulting"` free-text that pre-dated the controlled vocab.

## Motivation

Ship 113' added the controlled-vocabulary infrastructure (21 canonical sector codes + 6 region columns) but didn't tighten the ingest boundary. That left:

- The sector column silently accepting any string (customer expectation from Ship 113' UI was "controlled dropdown"; API-direct callers could still send anything)
- Region facts un-derived on tenants provisioned before Ship 113'.a's `region_of_country()` landed
- Arion Networks s.r.o.'s known-state (Czech company → EU data subjects) not reflected in the DB after Ship 113'

None of these were code bugs — they were consequences of the pace of Ship 110'-113' landing all in one day. Ship 114' cleans them up in one bundle.

## Delivery summary

### 114'.a — Region backfill script (`9b9d7d91`)

`scripts/dev/backfill_region_facts_for_existing_tenants.py` — mirrors Ship 111'.c's `backfill_client_facts_for_existing_tenants.py` shape.

For each active tenant with a `client_facts` row but no region declared/derived in `fact_source`:
1. Read `tenants.country` (may be free-text like "Czechia" or an ISO code).
2. Normalize via Ship 112'.a's `_normalize_country()` → canonical ISO alpha-2.
3. Update `tenants.country` + `client_facts.country` to the normalized value.
4. Derive region via Ship 113'.a's `region_of_country()`.
5. Set the matching `*_data_subjects` column TRUE.
6. Add `country=declared` + `*_data_subjects=derived (from country)` markers to `fact_source`.
7. Run `derive_applicability()` so posture_controls N/A flags update.

Idempotent — skips tenants that already have any region declared/derived. Uses `ARION_OWNER_PW` from `.env` (Ship 111'.a canonical scheme).

Dev-side dry-run: no-op (all dev tenants already have declared regions). PoC-side Arion Networks s.r.o.: will fix `country="Czechia" → "CZ"` + `eu_data_subjects=TRUE` + `apac/us/ca/other=FALSE (implicit default)`.

### 114'.b — `schema_v114` sector backfill + CHECK constraint (`9b9d7d91`)

`db/schema_v114_sector_backfill_and_check.sql` — one migration, three steps in a single transaction:

**Step 1 — Legacy free-text mapping.** 13 UPDATE branches covering common variants observed or anticipated:

| Free-text patterns | Canonical code |
|---|---|
| technology, tech, IT, IT Consulting, IT services, cybersecurity, security, software, saas, cloud | `ict_services` |
| finance, financial services, bank, banking | `banking` |
| trading, exchange, capital markets | `finance_markets` |
| healthcare, medical, pharma, pharmaceutical | `health` |
| retail, ecommerce, consumer | `retail` |
| consulting, legal, law, accounting, professional services | `professional` |
| manufacturing, industrial | `manufacturing` |
| energy, utilities, oil, gas, electricity | `energy` |
| transport, logistics, shipping, aviation | `transport` |
| government, public sector, public administration | `public_admin` |
| nonprofit, ngo, charity, foundation | `nonprofit` |
| research, academic, university | `research` |
| media, social media, platform | `digital_providers` |

Case-insensitive coverage (both `"technology"` and `"Technology"` in the map).

**Step 2 — Residual sweep.** Any remaining `sector` value not in the canonical 21-value vocabulary → `NULL`. Safer than dropping the row or the migration; tenant re-picks via Profile dropdown.

**Step 3 — CHECK constraint.** `client_facts_sector_check` locks the column to the 21 canonical codes (or NULL). Guarded by a DO block that skips add if the constraint already exists (Postgres has no native `ADD CONSTRAINT IF NOT EXISTS` for CHECK).

Applied on dev: 1 UPDATE (Arion `"technology"` → `"ict_services"`). Verified constraint fires:

```
NOTICE: CHECK constraint fired correctly  (on UPDATE sector = 'not_a_real_sector')
```

### 114'.c — Backend PUT /facts strict sector validation (`9b9d7d91`)

`api_server.py` sector-in-`_scoping_facts_text_allowed` branch tightens from Ship 113'.b's soft-validate (only rejects empty string) to hard-validate against `rag.scoping.sectors.is_valid_sector_code()`.

Both layers (DB CHECK + API validation) reject the same set → API returns `400` with a helpful hint pointing to the canonical vocab file, instead of a Postgres check_violation surfacing as an opaque 500.

Verified on dev:
- `PUT /facts {"sector": "Cybersecurity"}` → `400 sector must be one of the 21 canonical codes...`
- `PUT /facts {"sector": "ict_services"}` → `200` + applicability derivation fires
- `PUT /facts {"sector": ""}` → `400 sector cannot be empty string`

### 114'.d — Deploy script + retro (this)

`scripts/ops/ship-114-poc-update.sh` follows the Ship 113' per-arc script convention. Order matters:

1. `install.sh` — schema_v114 (backfill + CHECK) applies. If any legacy value fails to map, the residual sweep NULLs it out; migration succeeds.
2. Restart API — strict validation code activates.
3. Region backfill script — Arion `country=Czechia → CZ` + `eu_data_subjects=TRUE` derived.
4. Verification queries — schema tracker + CHECK constraint + tenant state + deployment log tail.

## Lessons codified

### Lesson 203 — Soft-validation is a foothold for drift

Ship 113'.b accepted any non-empty string on `sector` to avoid breaking existing rows. That was correct at the time (would have needed a migration to enforce), but every day it stayed soft, another tenant could add another legacy free-text value the CHECK constraint would then have to accommodate. **The gap between "controlled vocabulary defined" and "controlled vocabulary enforced" is technical debt.** Ship 114' closes it same-day.

### Lesson 204 — Backfill first, constrain second — always in one migration

`schema_v114` bundles backfill + CHECK constraint in a single BEGIN/COMMIT. Two separate migrations would leave a window where new writes could still add non-canonical values between step 1 and step 2. Single transaction = atomic cutover: at any observed state the DB is either fully pre-migration or fully post-migration.

### Lesson 205 — Fail-open for legacy data, fail-closed for new writes

Residual sweep NULLs out unmapped legacy values rather than dropping rows or failing the migration. Meanwhile the CHECK constraint fails ALL non-canonical writes going forward. Result: no data loss on migration, no dirty data added afterward. **Different error policies for historic vs. new data are legitimate.**

### Lesson 206 — Small arcs closing loose ends compound

Ship 114' is a small arc — 3 pieces, all cleanups from Ship 113' surface area. Not glamorous. But leaving these loose ends means the next arc's operator (maybe future Claude, maybe human) hits the same "why doesn't Arion show as EU?" question all over again. Closing the loop while the context is fresh is cheaper than re-diagnosing later.

## Related arcs

- [[ship-113-prime-arc-retrospective-2026-09-04]] — established the controlled vocab this arc enforces + region columns this arc backfills
- [[ship-112-prime-arc-retrospective-2026-09-04]] — country normalization used by 114'.a backfill
- [[ship-111-prime-arc-retrospective-2026-09-04]] — `backfill_client_facts_for_existing_tenants.py` pattern this arc mirrors
- [[ship-110-prime-arc-retrospective-2026-09-03]] — original `_EU_EEA_COUNTRIES` derivation that missed "Czechia"

## Deferred to Ship 115'+

1. **Regional-regulation curator arcs** — Ship 113'/114' set up the region column infrastructure. LGPD (Brazil), CCPA (California), APPI (Japan), PIPEDA (Canada), PDPA (Singapore) are each their own multi-day curator arc.
2. **Country map expansion** — 30+ countries currently in `_COUNTRY_NAME_TO_CODE` (Ship 112'.a). Expand when actual customers surface unlisted countries.
3. **Sector CHECK constraint expansion** — if a legitimate sector need surfaces (e.g. "insurance", "hospitality") not in the current 21-value list, extend `rag/scoping/sectors.py` + a schema_v115 migration to expand the CHECK constraint.
4. **Diagnostic-log retention** — dependent Ship 4'.b addendum work. Post-PoC signal.
