---
name: ship-112-prime-arc-retrospective-2026-09-04
description: Ship 112' arc — country name normalization + Quickstart dropdown, triggered by Ship 111'.c PoC deployment surfacing "Czechia" != "CZ" mismatch
metadata:
  type: project
---

# Ship 112' — country name normalization + Quickstart dropdown

**Date:** 2026-09-04 (same day as Ship 111')
**Commits:** `285f3f2f` (a) → `ab959765` (b) → this doc (c)
**Trigger:** Ship 111'.c backfill script output on arionlabs-dr-01 revealed `country='Czechia'` in the tenant row — a free-text display name captured by Ship 104's Quickstart form, silently mismatching Ship 110'.b's ISO-alpha-2 `_EU_EEA_COUNTRIES` set.

## Motivation

Ship 111'.c backfill produced this diagnostic output for arionlabs-dr-01's tenant:

```
'Arion Networks s.r.o.'  (2b6db5af, sector='IT Consulting',
                          country='Czechia', cloud_only=True)
declared: ['country', 'sector', 'has_physical_premises', 'uses_cloud_services']
derived:  []
```

The `derived: []` was the tell. Czechia is in the EU/EEA — `eu_data_subjects` should have been derived True. It wasn't.

Root cause traced to a three-layer disconnect:

1. **Ship 104's Quickstart form** — free-text `<input type="text">` for country.
2. **Ship 110'.b `_initial_client_facts()`** — assumed input was an ISO 3166-1 alpha-2 code and did `country.upper()` before checking `_EU_EEA_COUNTRIES = {"AT", "BE", ..., "CZ", ...}`.
3. **No canonicalization layer** between them. `"Czechia".upper() == "CZECHIA"`, `"CZECHIA" not in {"CZ", ...}`, derivation skipped, no error.

The bug had been latent since Ship 104' (2026-09-02) and only surfaced when Ship 111'.c backfill printed the `declared`/`derived` split visibly.

## Delivery summary

### 112'.a — Country normalization in initializer (`285f3f2f`)

Adds two primitives to `rag/onboarding/quickstart.py`:

- **`_COUNTRY_NAME_TO_CODE`** — 44-entry map from display names + common variants to ISO alpha-2 codes. Coverage: EU (27) + EEA (3) + UK + US (with `USA` / `United States` aliases) + Canada, Australia, New Zealand, Switzerland, Japan, Brazil, India, Singapore, South Africa.
- **`_normalize_country(raw)`** — accepts any of: ISO code (passthrough, up-cased), display name (mapped via lookup), 2-letter alias like `"UK"` (mapped to `"GB"` via alias map). Unknown input returns unchanged (fail-open). Empty/null returns `""` so caller can apply its own default.

Design choice: display-name lookup runs **before** the 2-letter shortcut, so `"UK"` (not a valid ISO code, since GB is the correct one) resolves via the alias map instead of being returned verbatim.

`_initial_client_facts()` normalizes country **before** `_EU_EEA_COUNTRIES` membership check + writes the normalized value into `values["country"]`. `create_first_tenant()` normalizes before `INSERT INTO tenants` too, so `tenants.country` and `client_facts.country` stay in sync.

10 test assertions in `tests/test_country_normalization.py`:
- Ship 111'.c bug scenario (`"Czechia" → "CZ"` end-to-end)
- UK variants + Brexit correctness (GB drives `uk_data_subjects=True`, `eu_data_subjects=None`)
- US variants (`"USA"` / `"United States"` → `"US"`)
- ISO codes passthrough (case-insensitive)
- Whitespace + case handling
- Empty/null input (returns `""`)
- Unknown input fails open (returns as-is, never crashes)

### 112'.b — Quickstart form dropdown (`ab959765`)

Replaces the free-text `<input>` with `<select>` — 41 options grouped by region (Europe/EU/EEA/UK, North America, Asia-Pacific, Rest of world). Value is ISO alpha-2, label is display name. United Kingdom is the default selected option (matches Ship 104's old free-text default of `"GB"`).

Ship 112'.a's backend normalization stays as defence-in-depth:
- API-direct callers (POST /api/v1/quickstart without going through UI)
- Admin scripts (`scripts/dev/create_tenant.py`)
- Future ingest paths (CSV import, etc.)

JS version bumped to `country-dropdown`.

### 112'.c — Retrospective + deployment log update (this)

Updates `docs/deployments/arionlabs-dr-01.md` timeline with the Ship 111'.e deployment success + Path B ad-hoc fix + pending Ship 112' deployment row. Retrospective committed here.

## PoC-side state after Path B (2026-09-04 pre-Ship-112')

Path B was the one-shot SQL fix applied to arionlabs-dr-01 while Ship 112' was in flight. Sequence:

1. `UPDATE tenants SET country='CZ'` for the affected tenant.
2. `UPDATE client_facts SET country='CZ', eu_data_subjects=TRUE, fact_source=fact_source || {country: declared, eu_data_subjects: derived from country}`.
3. Ran `derive_applicability(pg, tenant_id)` directly via Python, bypassing the HTTP admin endpoint (which needs a raw API key not recoverable from the hash column).
4. Result: 14 A.7.% controls marked N/A with reason `[cloud_only_no_physical] Cloud-only tenant — physical premises controls do not apply.`

## Lessons codified

### Lesson 193 — Free-text at intake needs normalization at both ends

Ship 104's Quickstart form asked "country" as free text. Ship 110'.b's initializer assumed ISO alpha-2. The mismatch was invisible until Ship 111'.c printed the `derived: []` output. Fix: **normalize at every ingest point that touches a field with a controlled downstream vocabulary**. Ship 112'.b tightens the UI too — but the backend normalization stays because free-text APIs remain.

### Lesson 194 — Silent-skip bugs need diagnostic output to surface

If Ship 111'.c had just done `INSERT` and moved on, we'd never have noticed the country mismatch. The `declared: [...]` / `derived: [...]` print statements at insertion time made the empty derived list impossible to miss. Same pattern: **admin scripts that write data should print what they wrote, especially when the shape is data-shape-sensitive**.

### Lesson 195 — Post-deployment feedback loops surface real-world data-shape issues

Ship 111'.c was designed to backfill 100% correctly. It ran successfully, but because it printed intermediate state, the operator caught a bug that would have gone silent forever. **Deployment isn't done until the data has been reviewed by human eyes** — automated verification catches errors, but doesn't catch design-vs-reality mismatches.

### Lesson 196 — Defence-in-depth normalization

Even after Ship 112'.b's dropdown lands, the backend normalization stays. Reasons:
- API-direct callers can bypass the UI (`create_tenant.py`, admin scripts, ingest workers).
- Future frontends (mobile, third-party integrations) may not use the same dropdown.
- Ingest pipelines from spreadsheets, CSVs, etc. always need normalization.

The principle: **UI validation is user-experience; backend validation is correctness. Both, not either.**

### Lesson 197 — Fail-open normalization

`_normalize_country("Neverland")` returns `"Neverland"` unchanged rather than raising or dropping. Rationale: the caller shouldn't crash if a customer types a country we didn't anticipate. The downstream derivation just silently skips (which is correct — we don't know if Neverland is EU/EEA). If unrecognised inputs accumulate in production data, that's a signal to expand the map, not to break the flow.

## Related arcs

- [[ship-104-prime-arc-retrospective-2026-09-02]] — Quickstart free-text form; the source of the bug
- [[ship-110-prime-arc-retrospective-2026-09-03]] — `_EU_EEA_COUNTRIES` set + eu_data_subjects derivation; the destination that couldn't read what was written
- [[ship-111-prime-arc-retrospective-2026-09-04]] — Ship 111'.c backfill script whose diagnostic output surfaced this bug
- [[dejargonize-ux-pass-2026-07-01]] — precedent for controlled-vocabulary UI (dropdowns for framework enrolment, etc.)

## Deferred to Ship 113'+

1. **Country coverage expansion** — 44 countries covered by the map; if a customer needs one we didn't include, the fail-open behaviour surfaces it as a normalize-passthrough. Expand on demand.
2. **Sector normalization** — free-text `sector` field is next candidate for the same treatment. Ship 104's Quickstart takes free text; there's no downstream sector-based derivation yet, so no bug — but the shape is the same.
3. **Automated normalization guard test** — could grep the initializer for other silent-skip candidates (any `x.upper() in {...}` pattern against uncontrolled input). Deferred.

## PoC deployment plan for Ship 112'

To land 112' on arionlabs-dr-01:

```bash
ssh -i ~/.ssh/arion_operator_ed25519 arionops@10.0.1.85 '
  cd /data/arioncomply &&
  git pull &&
  bash deploy/install.sh &&
  sudo systemctl restart arioncomply-api
'
```

No new migrations. `install.sh` writes a `.deployment_log.jsonl` line (Ship 111'.d). Existing arionlabs-dr-01 tenant already fixed by Path B — no backfill needed. Verify by opening the Quickstart UI in a fresh browser (SSH tunnel) and confirming the country field is a dropdown.
