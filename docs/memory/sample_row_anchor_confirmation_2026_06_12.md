---
name: sample-row-anchor-confirmation-2026-06-12
description: "SHIPPED 2026-06-12 (127a12c): deterministic data-shape inspection for borderline-confidence (30-70%) workbook fingerprint matches. New rag/intake/value_patterns.py (9 patterns) + _apply_sample_value_anchors in workbook_discovery.py + drop-threshold gate at 0.30 + anchor_decisions telemetry on SheetProposal. Pilot anchors on supplier_review_log (company_name) + personnel_security_attestation_register (person_name). Auto-catches the false-positive supplier match on Business Partners Assessment that F2 had to clean up manually."
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

  - `supplier_review_log.yaml` — vendor/supplier/partner-name
    column → `company_name` pattern. Catches sheets where
    "Partner" terminology is used for personnel, not vendors.
  - `personnel_security_attestation_register.yaml` — partner/
    employee/staff/personnel-name column → `person_name`
    pattern. Catches sheets where the personnel YAML title-
    matches a third-party register.

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
