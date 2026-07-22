---
name: ship-14-prime-b-risk-register-schema-template-2026-07-22
description: "Ship 14'.b — schema_v87 adds 5 27005 §8.6.1 treatment-plan columns; canonical xlsx template built + importer extended"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 14'.b (2026-07-22) — second sub-arc of Ship 14. Extends
the `risks` table with the ISO 27005:2022 §8.6.1 treatment-plan
elements that schema_v2 didn't cover, ships the canonical xlsx
template tenants download to populate their register, and
extends the existing workbook importer to parse the new columns.

## What ships

**Schema (`db/schema_v87_ship14b_risk_register_columns.sql`)** —
5 NULL-permissive columns added to `risks`:
- `treatment_rationale TEXT` — why the option was chosen
- `resources_required TEXT` — budget / people / infrastructure
- `performance_indicators TEXT[]` — KPIs per §8.6.1
- `constraints TEXT` — dependencies + timing gates
- `reporting_cadence TEXT` — how often status is reported

Each column carries a `COMMENT ON` string with the 27005 §8.6.1
authority pointer so pg_dump / `\d risks` includes the citation
inline. All optional; 35 existing rows on the demo tenant
remain untouched (no backfill needed).

**Canonical template
(`db/templates/risk_register_canonical.xlsx`)** — static xlsx
built by `scripts/build_risk_register_template.py`. Four sheets:

- **Risk Register** (visible) — 10 columns matching
  `RowMappers.risks` in the existing workbook importer
- **Risk Treatment Plan** (visible) — 15 columns matching
  `RowMappers.risk_treatment`, extended with the 5 new schema
  columns
- **Guidance** (visible) — per-column authoritative text
  citing 27005 §7.2 / §8.2 / §8.6.1 as appropriate
- **_arion_meta** (hidden) — canonical-template marker
  (`template_kind = risk_register_canonical`, `auto_approve =
  true`), schema_version, ship_arc, guidance_source, and both
  linked leaf_ids for auditor provenance

9,716-byte deterministic build — re-running the script
produces the identical file. Committed as a static asset.

**Importer extension (`db/workbook_importer.py::RowMappers.risk_treatment`)** —
5 new fields parsed from the Treatment Plan sheet:
- `treatment_rationale`   ← "Treatment Rationale" column
- `resources_required`    ← "Resources Required" column
- `performance_indicators` ← "Performance Indicators" column
  (list, comma-split)
- `constraints`           ← "Constraints" column
- `reporting_cadence`     ← "Reporting Cadence" column

Existing 10 columns still parse unchanged — additive-only.
NULL-safe when older uploads don't carry the new headers.

## Verification

Round-trip unit test on `RowMappers.risk_treatment`:

- Sample row with all 15 Treatment Plan columns filled
- All 5 new fields extracted correctly
- `performance_indicators` parsed as `["backup_success_rate_pct",
  "restore_test_pass", "mttr_days"]` from comma-separated
- `control_refs` correctly picked up as
  `["ISO27001:2022:A.5.15", "ISO27001:2022:A.8.13"]`
  (framework-role-model alignment — no primary/xfw split)

schema_v87 applied cleanly on demo Postgres; `\d risks` shows
all 5 new columns with their `COMMENT ON` strings visible.

## Ship 14'.a addendum — reviewer discipline answers

Per the four alignment questions Ship 14'.a required of every
sub-arc:

**1. Role split? (Does the sub-arc render program / extension /
obligation / guidance as first-class citizens?)**

Yes. The canonical template's `ISMS Applicable Controls` and
`PIMS Applicable Controls` columns are visually side-by-side
(not hierarchically split), and the importer merges both into
a single `control_refs TEXT[]` array with `STANDARD:VERSION:REF`
format for each ref. No primary/xfw hierarchy is encoded. The
schema's `control_refs` array can hold GDPR obligations
(`GDPR:2016/679:Art.32`), extension refs (`ISO27701:2019:A.7.5.1`),
and program refs (`ISO27001:2022:A.5.15`) equally — a future
importer update to add a "GDPR Applicable Articles" column
would just extend the array in the same shape.

**2. Parallel CaseFile view? (Does the sub-arc build a data
structure that competes with `CaseFile` as ground truth?)**

Not applicable — Ship 14'.b is data-layer only. No chat
surfaces touched. The `RiskSummary` field on CaseFile lands
in Ship 14'.e.

**3. Deterministic routing? (Does the sub-arc rely on LLM
inference for anything routing / classification / policy-flip
related?)**

Not applicable — Ship 14'.b is data-layer only. The importer
uses deterministic column-name matching + type coercion. Zero
LLM calls.

**4. Guidance-normative discipline? (Does the sub-arc add
MUSTs from guidance content?)**

**No** — this was tested during design. Ship 14'.b's 5 new
schema columns are OPTIONAL DATA STORAGE for what a tenant
chooses to record. They are NOT new MUSTs on any leaf. The
existing 6 MUSTs on `req:6.1.2:risk_register` and the existing
MUSTs on `req:6.1.3:risk_treatment_plan` remain the ONLY
engine-verdict inputs. A tenant that never fills the
`treatment_rationale` column won't see an engine flip — the
column is auditor-visible context, not a compliance obligation.

## What did NOT ship

- **API endpoint for downloading the template** — deferred to
  Ship 14'.c along with the CRUD + summary endpoints
- **Dashboard-visible upload button** — deferred to Ship 14'.d
- **Chat surfacing** — deferred to Ship 14'.e (posture_risk
  question_type + RISKS digest slot)
- **Cascade events on risk changes** — deferred to Ship 14'.e
- **Backfill for the 35 existing demo rows** — deliberately
  skipped; older data lacks the new columns and that's fine

## Ship 14 progress

| Sub-arc | Status |
|---|---|
| 14'.a Design memo + role-model + case-file addendum | ✓ |
| **14'.b schema_v87 + xlsx template + upload path** | **✓ (this doc)** |
| 14'.c API surface (internal + external) | next |
| 14'.d Dashboard cards + heatmap + drill-in | pending |
| 14'.e Chat surfaces + cascade events | pending |
| 14'.f Eval + retro | pending |

## Related

- [[ship-14-prime-a-risk-register-design-2026-07-22]] — the
  design + architecture-constraint addendum this sub-arc respects
- [[templates-v2-anchors-complete-2026-06-25]] — the xlsx
  template pattern reused (though this template is cross-leaf,
  not driven by TABLE-COLUMNS markers)
- [[ship-13-prime-b-iso27005-enrichment-2026-07-21]] — the 27005
  §8.6.1 authority the schema comments cite
- Ship 14'.c: internal + external API endpoints for risk
  register CRUD + template download
