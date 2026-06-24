---
leaf_id: req:Art.38:position_evidence_register
control_ref: Art.38
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# DPO Position Evidence Register

> Per-period record of position-guarantee evidence (board attendance, budget approval, independence demonstrations). Annual refresh (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Per-row reporting period (typically quarterly)

<<MUST item:Art.38:reg_period>>
_Why: Cadence_

<<TEXT>>

## 2. Per-row board / management forum attendance evidence

<<MUST item:Art.38:reg_board_attendance>>
_Why: Art.38.3 — reporting line_

<<TEXT>>

## 3. Per-row budget approval / spend evidence (Art.38.2 resources)

<<MUST item:Art.38:reg_budget_approval>>
_Why: Art.38.2_

<<TEXT>>

## 4. Per-row independence signals (no overruled DPO opinion; if overruled, formal record + escalation)

<<MUST item:Art.38:reg_independence_signal>>
_Why: Art.38.3_

<<TEXT>>

## 5. Per-row conflict-of-interest re-attestation (Art.38.6)

<<MUST item:Art.38:reg_coi_attestation>>
_Why: Art.38.6_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Per-row training / development hours (sustains expertise per Art.37.5)

<<SHOULD item:Art.38:reg_training>>
_Why: Cross-article_

<<TEXT>>
