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

<<DOC_CONTROL>>

> The upstream — every customer whose contract terminates; also cases of merger / acquisition where PII moves.

## What this template gives you

This template helps you clearly define which situations are covered when a customer’s contract ends or when personal data is transferred due to mergers or acquisitions. It ensures you meet privacy requirements under ISO 27701.

## When to use it

Use this document whenever a customer’s contract is ending, or if there’s a merger or acquisition involving personal data. Update it as needed whenever these situations arise.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you’ll need to address three required elements and possibly one recommended element.

## 1. Termination triggers enumerated (contract expiry / customer offboarding / product discontinuation)

<<MUST item:B.8.4.2:scope_termination_triggers>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. M&A events — where PII moves to another controller (transfer scenario)

<<MUST item:B.8.4.2:scope_ma_events>>
_Why: §8.4.2 — transfer to another PII controller_

<<GUIDANCE>>

<<TEXT>>

## 3. Post-termination retention window before disposal (accidental-lapse protection)

<<MUST item:B.8.4.2:scope_retention_window>>
_Why: §8.4.2 — retention period_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new customer tier / new offboarding flow)

<<SHOULD item:B.8.4.2:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
