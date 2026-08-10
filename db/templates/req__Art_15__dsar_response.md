---
leaf_id: req:Art.15:dsar_response
control_ref: Art.15
standard_id: GDPR:2016/679
evidence_type: dsar_response
trigger_type: operational
template_version: 1
must_count: 14
should_count: 2
---

# Data Subject Access Request Response

<<DOC_CONTROL>>

> Per-request evidence that a specific DSAR was answered in line with Art.15. Each response covers confirmation, the Art.15(1)(a-h) information set, third-country transfer safeguards under Art.15(2), the copy of personal data per Art.15(3), and was delivered within Art.12(3) timing

## What this template gives you

This template helps you respond to data subject access requests by ensuring all required GDPR Article 15 information is included, such as confirmation of processing, data details, and delivery within the legal timeframe.

## When to use it

Use this document whenever you receive a data subject access request and need to provide a compliant response. Complete a new version each time a request is made.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 2.5 to 3.5 hours preparing a full response from scratch, as each required section takes around 10-15 minutes to complete.

## 1. Confirmation that personal data is or is not processed

<<MUST item:Art.15:confirmation>>
_Why: Art.15.1 opening_

<<GUIDANCE>>

<<TEXT>>

## 2. Purposes of the processing

<<MUST item:Art.15:purposes>>
_Why: Art.15.1.a_

<<GUIDANCE>>

<<TEXT>>

## 3. Categories of personal data concerned

<<MUST item:Art.15:categories>>
_Why: Art.15.1.b_

<<GUIDANCE>>

<<TEXT>>

## 4. Recipients or categories of recipients (including any in third countries)

<<MUST item:Art.15:recipients>>
_Why: Art.15.1.c_

<<GUIDANCE>>

<<TEXT>>

## 5. Envisaged storage period or criteria used to determine it

<<MUST item:Art.15:retention>>
_Why: Art.15.1.d_

<<GUIDANCE>>

<<TEXT>>

## 6. Existence of rights to rectification, erasure, restriction and objection

<<MUST item:Art.15:rights>>
_Why: Art.15.1.e_

<<GUIDANCE>>

<<TEXT>>

## 7. Right to lodge a complaint with a supervisory authority

<<MUST item:Art.15:complaint>>
_Why: Art.15.1.f_

<<GUIDANCE>>

<<TEXT>>

## 8. Source of the personal data where not collected from the data subject (any available information)

<<MUST item:Art.15:source>>
_Why: Art.15.1.g_

<<GUIDANCE>>

<<TEXT>>

## 9. Existence of automated decision-making / profiling, with meaningful information on logic and consequences where applicable

<<MUST item:Art.15:automated_decision>>
_Why: Art.15.1.h / Art.22_

<<GUIDANCE>>

<<TEXT>>

## 10. Where data is transferred to a third country or international organisation, the appropriate safeguards under Art.46

<<MUST item:Art.15:transfer_safeguards>>
_Why: Art.15.2_

<<GUIDANCE>>

<<TEXT>>

## 11. Copy of the personal data undergoing processing provided to the data subject

<<MUST item:Art.15:copy>>
_Why: Art.15.3_

<<GUIDANCE>>

<<TEXT>>

## 12. Responded within one calendar month of receipt OR Art.12.3 two-month extension formally applied with notification

<<MUST item:Art.15:timing>>
_Why: Art.12.3_

<<GUIDANCE>>

<<TEXT>>

## 13. Structured SLA-met flag per response — boolean against the Art.12.3 1-month clock (or extended clock where Art.12.3 extension was formally invoked); analogous to A.5.16:rev_sla_met

<<MUST item:Art.15:sla_met>>
_Why: Auditor-critical SLA proof — drives the rev_timing aggregation on the review leaf_

<<GUIDANCE>>

<<TEXT>>

## 14. Identity verification step recorded (proportionate to sensitivity per Art.12.6) — modern baseline treats Art.12.6 as MUST not SHOULD when reasonable doubt is the default posture for unauthenticated channels

<<MUST item:Art.15:identity_check>>
_Why: Art.12.6 (promoted SHOULD→MUST Phase C batch 1)_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Provided in a commonly used electronic format where the request was made electronically

<<SHOULD item:Art.15:format>>
_Why: Art.15.3_

<<GUIDANCE>>

<<TEXT>>

### 2. Where other people's rights would be affected, redaction or partial-response justification noted

<<SHOULD item:Art.15:third_party_redaction>>
_Why: Art.15.4_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
