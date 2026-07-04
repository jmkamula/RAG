---
leaf_id: req:B.8.4.2:applicable_scope
control_ref: B.8.4.2
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable End-of-Service Scope

> The upstream — every customer whose contract terminates; also cases of merger / acquisition where PII moves.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Termination triggers enumerated (contract expiry / customer offboarding / product discontinuation)

<<MUST item:B.8.4.2:scope_termination_triggers>>
_Why: Coverage_

<<TEXT>>

## 2. M&A events — where PII moves to another controller (transfer scenario)

<<MUST item:B.8.4.2:scope_ma_events>>
_Why: §8.4.2 — transfer to another PII controller_

<<TEXT>>

## 3. Post-termination retention window before disposal (accidental-lapse protection)

<<MUST item:B.8.4.2:scope_retention_window>>
_Why: §8.4.2 — retention period_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new customer tier / new offboarding flow)

<<SHOULD item:B.8.4.2:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
