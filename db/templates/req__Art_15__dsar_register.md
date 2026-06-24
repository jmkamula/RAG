---
leaf_id: req:Art.15:dsar_register
control_ref: Art.15
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 6
should_count: 2
---

# DSAR Register

> Living log of every access request received and its handling. Distinct from the per-event response leaf: the register is the universal record showing the population of requests, status, and timing compliance — auditor-facing evidence that the procedure operates in practice. Style v2 freshness 180d — high-volume DSAR data, slower than incident-register fast-data (90d) but faster than annual review

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Request received date (the start of the Art.12.3 clock) per row

<<MUST item:Art.15:reg_received_date>>
_Why: Art.12.3 timing_

<<TEXT>>

## 2. Requester identity (verified) or pseudonymous reference where verification used a token

<<MUST item:Art.15:reg_requester>>
_Why: Art.12.6_

<<TEXT>>

## 3. Scope of the request as understood (full Art.15 / specific data set / repeat copy)

<<MUST item:Art.15:reg_scope>>
_Why: Operational clarity_

<<TEXT>>

## 4. Date the response was issued

<<MUST item:Art.15:reg_response_date>>
_Why: Art.12.3_

<<TEXT>>

## 5. Timing compliance flag (within 1 month / extended per Art.12.3 / late)

<<MUST item:Art.15:reg_timing_flag>>
_Why: Art.12.3_

<<TEXT>>

## 6. Outcome per row (fulfilled / partial under Art.15.4 / refused under Art.12.5 with reason)

<<MUST item:Art.15:reg_outcome>>
_Why: Art.12.5 / Art.15.4_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Extension reason captured when Art.12.3 two-month extension was used

<<SHOULD item:Art.15:reg_extension_reason>>
_Why: Art.12.3_

<<TEXT>>

### 2. Linkage to the per-request response artifact (req:Art.15:dsar_response instance)

<<SHOULD item:Art.15:reg_response_link>>
_Why: Cross-leaf traceability_

<<TEXT>>
