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

<<DOC_CONTROL>>

> Evidence that the policy was actually communicated — distribution channels used, audience coverage, acknowledgement records, refresher cadence. 'Approved but not communicated' is a common audit finding

## What this template gives you

This template helps you document how your information security policy was shared with your team, including who received it, how it was sent, and how acknowledgements were tracked.

## When to use it

Use this whenever you need to show that your information security policy has been communicated to the right people. Update it whenever you distribute the policy or run a refresher.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on how easily you can gather details about your distribution and acknowledgement process.

## 1. Distribution channels stated (intranet, onboarding pack, all-hands, signed acknowledgement)

<<MUST item:5.2:com_channels>>
_Why: Clause 5.2 f) — communicated_

<<GUIDANCE>>

<<TEXT>>

## 2. Audience coverage stated (employees, contractors, third parties as relevant)

<<MUST item:5.2:com_audience>>
_Why: Clause 5.2 f) — within the organisation_

<<GUIDANCE>>

<<TEXT>>

## 3. Acknowledgement record (signed receipt, training completion, or equivalent)

<<MUST item:5.2:com_acknowledgement>>
_Why: Evidence preservation_

<<GUIDANCE>>

<<TEXT>>

## 4. Refresher cadence (annual re-acknowledgement or on policy update)

<<MUST item:5.2:com_refresher>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External-party communication (where 5.2g) requires availability to interested parties)

<<SHOULD item:5.2:com_external>>
_Why: Clause 5.2 g)_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
