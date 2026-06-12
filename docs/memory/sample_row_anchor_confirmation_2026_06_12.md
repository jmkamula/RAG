---
name: sample-row-anchor-confirmation-2026-06-12
description: "SHIPPED 2026-06-12 (127a12c + 11c5362): deterministic data-shape inspection for borderline-confidence (30-70%) workbook fingerprint matches. value_patterns.py (9 patterns) + _apply_sample_value_anchors + drop-threshold gate + anchor_decisions telemetry. Pilot expanded to 10 anchors across YAMLs that cover Arion's full in-band proposal set. Inert-on-empty fix: empty sample columns produce no boost/penalty (None signal), so template-shape registers with unfilled cells aren't falsely penalised."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Born from the user's strategic question 2026-06-12 — see
[[feedback-intake-label-unreliability]]. The principle: when sheet
titles + column headers can't reliably identify evidence shape,
the only deterministic signal left is the **data values
themselves**. A "Name" column anchors to person/company by what's
in its cells, not what's in its header.

## Why deterministic, not LLM

LLM-judged anchors are non-deterministic — same bytes give
different judgments on different runs. For an evidence-grading
system that must be audit-defensible, reproducibility matters
more than recall. The pattern library is small, explicit, and
testable; the same workbook produces the same confidence
forever.

The user was explicit: **don't dilute compliance**. The right
move isn't to make the spec ask less; it's to find evidence
more carefully. Anchors do the latter.

## Architecture

Three layers, all in `rag/intake/`:

### 1. value_patterns.py (new module)

9 built-in patterns, each a pure `(value: str) -> bool` function:

  | pattern | matches |
  |---|---|
  | person_name | `Firstname Lastname …`, Unicode-tolerant, supports apostrophes/hyphens |
  | company_name | Legal suffixes (`Inc/Ltd/LLC/GmbH/SARL/Sp. z o.o.`) OR known SaaS brand tokens |
  | iso_date | Parses ISO + common date formats |
  | compliance_status | Enum: Compliant / In Progress / Active / Approved / N/A / etc. |
  | risk_rating | Enum: Low / Medium / High / Critical / Severe |
  | numeric_score | Numeric, allowing `%` / `pts` suffix |
  | control_ref | `A.X.Y` / `Art.X` / clause `\d+\.\d+` |
  | email | Standard regex |
  | frequency_value | Daily / Monthly / Quarterly / Annually / Ad hoc / etc. |

Plus `check_anchor(values, pattern_name, min_ratio) → (passed,
ratio)` — the entry point the discovery module calls.

### 2. _apply_sample_value_anchors() in workbook_discovery.py

Per-pass anchor evaluator. For each anchor declared in the YAML
pass:
  1. Resolve the matching column via `_find_column()` using
     the anchor's `column_fingerprint` (+ optional
     `alternative_fingerprints`). Fingerprint-based, not bound-
     MUST-id-based — so anchors work even when multiple
     bindings share the same MUST.
  2. Extract values from the first 5 data rows of the matched
     column.
  3. Run `check_anchor` against the value_pattern.
  4. Apply `confidence_boost` on match, `confidence_penalty`
     on miss. Record telemetry.

### 3. Wiring + drop gate in discover_sheet()

After the fingerprint pass computes initial confidence, IF the
confidence is in `[_ANCHOR_BAND_LO, _ANCHOR_BAND_HI]` (0.30–0.70),
anchors fire for all passes. Confidence is clamped to [0, 1].
Then: if final confidence < `_DROP_THRESHOLD` (0.30), the
proposal is filtered before `persist_proposals` ever sees it —
no orphan in `workbook_intake_proposal`.

## YAML schema extension

Optional `sample_value_anchors` block per pass:

```yaml
sample_value_anchors:
  - column_fingerprint: [vendor, name]
    alternative_fingerprints:
      - [supplier, name]
      - [partner, name]
    value_pattern: company_name
    min_match_ratio: 0.6
    confidence_boost: 0.10
    confidence_penalty: -0.30
```

Penalty magnitude > boost magnitude because false positives
hurt more than missed boosts.

## Pilot anchors shipped

Initial pilot (127a12c):

  - `supplier_review_log.yaml` — vendor/supplier/partner-name
    column → `company_name` pattern. Catches sheets where
    "Partner" terminology is used for personnel, not vendors.
  - `personnel_security_attestation_register.yaml` — partner/
    employee/staff/personnel-name column → `person_name`
    pattern. Catches sheets where the personnel YAML title-
    matches a third-party register.

Expansion (11c5362) — 8 more anchors across the YAMLs that
cover Arion's in-band proposal set:

  - `asset_register.yaml`                              → iso_date on `[last,updated]`
  - `change_management_review.yaml`                    → iso_date on `[review,date]`
  - `iso27001_2022_7_5_isms_document_register.yaml`    → iso_date on `[approval,date]`
  - `access_revocation_log.yaml`                       → iso_date on `[effective,date]`
  - `iso27001_2022_a_8_3_access_matrix_register.yaml`  → iso_date on `[last,recert]`
  - `iso27001_2022_9_1_measurement_record.yaml`        → iso_date on `[date]`
  - `access_register_pii.yaml`                         → person_name on `[name]`
  - `iso27001_2022_a_8_1_endpoint_register.yaml`       → person_name on `[owner]`

Pattern: a register's date column should hold ISO-parseable
dates; an access register's name column should hold person names.
Cheap to author (~10 LOC YAML each), high-precision (false-
positive rate is the inverse of the value pattern's false-
positive rate — for iso_date, near zero).

## Inert-on-empty fix (11c5362)

First post-pilot measurement on Arion's full workbook surfaced
a bug: anchors on empty date columns were producing
`ratio=0.0` and triggering the −0.25 penalty. Template-shape
registers (workbooks with header rows but no data rows yet)
got falsely demoted from ~0.6 to ~0.35 confidence. Empty isn't
"contradicting"; it's "no data to verify".

Fix in `value_patterns.check_anchor`: return signal type is
now `(passed: bool|None, ratio: float, sample_size: int)`.
When all sample cells are blank, `passed=None`. Caller
(`_apply_sample_value_anchors`) treats None as **inert** —
no boost, no penalty, logged for telemetry as
`decision="inert"`.

Result: empty columns are silently neutral. Anchors only
contribute confidence when they have real data to inspect.
The "inert" telemetry surface still lets operators see which
anchors were defeated by sparse workbooks and might benefit
from a different column choice.

## Validation

Direct simulation against today's Business Partners Assessment
data (Joseph Kamula, Libor Ballaty, Zorko Petrusa, Yusuf
Yusufov):

  - Pre-F2 state: matched `supplier_review_log.yaml` at 0.433
    confidence via `[business, partner]` fingerprint. Required
    manual YAML-fingerprint pruning (F2 commit f7c934f).
  - With anchor: company_name pattern fires on Partner Name
    column. 0/4 sample values match. Ratio 0.0 < min_ratio
    0.6 → penalty −0.30 applied. Confidence 0.433 → 0.133 <
    0.30 drop threshold → proposal **auto-dropped**.

The system would have caught the false positive without F2's
manual cleanup. Future tenants with similar mis-labels won't
require curation intervention.

## Measured impact on Arion's workbook (post-pilot expansion)

  - 38 proposals total
  - 5 proposals with anchor decisions (13%)
    - 4 inert (empty sample, no impact)
    - 1 boost (Access Rev. Log Non-PII → access_register_pii
      at +0.10 confidence: column matches person_name pattern
      via "Users Reviewed" / "Reviewer" sample data)
  - 0 false-positive penalties
  - 0 false-positive drops

The 4 inert decisions are on legitimately-template sheets
(Document Cont. Reg., User BYOD Compl. Log, Access Register
PII Systems, Info Sec KPI Metrics Tracker) where the date
columns exist but have no data yet. Future workbook re-runs
once those cells are populated will flip inert → boost.

## What this doesn't solve

  - **False negatives** (sheets that match no YAML) — anchors
    only confirm or refute proposed matches; they can't
    propose new ones. Still need separate work for false-
    negative detection (e.g. extending the unmatched-patterns
    admin endpoint to sub-40% workbook matches).
  - **Doc-side anchoring** — pilot is workbook-only. The
    value_patterns module is reusable; extending to docs is
    additional integration work.
  - **Anchor authoring quality** — patterns are author-
    judgment. Wrong pattern choice could mis-fire. Validated
    by reviewing each new anchor against real tenant data.

## Telemetry surface

`SheetProposal.anchor_decisions: list[dict]` — per-anchor record
with fingerprint, pattern, matched header, ratio, passed,
delta, decision. Available in the script CLI output today;
admin endpoint to surface from intake_trace_log is a follow-up.

## Related

- [[feedback-intake-label-unreliability]] — the strategic
  framing that motivated this.
- [[workbook-orphan-disposition-2026-06-11]] — the manual F2
  work that anchors would now do automatically.
- [[workbook-yaml-vocab-refresh-2026-06-11]] — the broader
  workbook-intake arc.
- [[intake-determinism-levers]] — the determinism principle
  this honours (no LLM, SHA-cacheable).
- [[doc-curation-engine-v1]] — sibling for doc side; pattern
  library is reusable.
