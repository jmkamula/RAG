---
leaf_id: req:5.2:isp_communication_evidence
control_ref: 5.2
standard_id: ISO27001:2022
evidence_type: communication_evidence
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Information Security Policy Communication Evidence

> Evidence that the policy was actually communicated — distribution channels used, audience coverage, acknowledgement records, refresher cadence. 'Approved but not communicated' is a common audit finding

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Distribution channels stated (intranet, onboarding pack, all-hands, signed acknowledgement)

<<MUST item:5.2:com_channels>>
_Why: Clause 5.2 f) — communicated_

<<TEXT>>

## 2. Audience coverage stated (employees, contractors, third parties as relevant)

<<MUST item:5.2:com_audience>>
_Why: Clause 5.2 f) — within the organisation_

<<TEXT>>

## 3. Acknowledgement record (signed receipt, training completion, or equivalent)

<<MUST item:5.2:com_acknowledgement>>
_Why: Evidence preservation_

<<TEXT>>

## 4. Refresher cadence (annual re-acknowledgement or on policy update)

<<MUST item:5.2:com_refresher>>
_Why: Currency_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External-party communication (where 5.2g) requires availability to interested parties)

<<SHOULD item:5.2:com_external>>
_Why: Clause 5.2 g)_

<<TEXT>>
