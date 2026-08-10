---
leaf_id: req:Art.15:dsar_handling_procedure
control_ref: Art.15
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 2
---

# DSAR Handling Procedure

<<DOC_CONTROL>>

> Art.15 read with Art.12 implies a documented operational process — the procedure prescribes how access requests are received, verified, fulfilled, timed and exception-handled, regardless of whether any DSAR has yet occurred. The actual responses are the per-event response leaf

## What this template gives you

This template helps you create a clear, step-by-step procedure for handling data subject access requests (DSARs) under GDPR, ensuring your team knows exactly how to receive, verify, and respond to these requests.

## When to use it

Use this document whenever your organization processes personal data and needs to be ready for DSARs at any time. Review and update it whenever your processes change or as needed to stay compliant.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1.5 to 2 hours completing this template from scratch, as it covers eight required elements and a couple of recommended ones.

## 1. Intake channels for DSARs enumerated (web form, email, post, in-person) and a single point of receipt named

<<MUST item:Art.15:proc_intake>>
_Why: Operational sufficiency_

<<GUIDANCE>>

<<TEXT>>

## 2. Identity verification approach stated, proportionate to data sensitivity (reasonable doubts trigger, Art.12.6)

<<MUST item:Art.15:proc_identity>>
_Why: Art.12.6_

<<GUIDANCE>>

<<TEXT>>

## 3. Fulfillment steps — who searches which systems against the data flow inventory to assemble the response

<<MUST item:Art.15:proc_fulfillment>>
_Why: Art.15.1 / Art.30 linkage_

<<GUIDANCE>>

<<TEXT>>

## 4. One-month timing clock from receipt, with the Art.12.3 two-month extension procedure (when justified, how notified)

<<MUST item:Art.15:proc_timing>>
_Why: Art.12.3_

<<GUIDANCE>>

<<TEXT>>

## 5. Default response format (electronic where request was electronic, structured layout for readability)

<<MUST item:Art.15:proc_format>>
_Why: Art.15.3_

<<GUIDANCE>>

<<TEXT>>

## 6. Exception handling: manifestly unfounded/excessive requests (Art.12.5), and partial response where rights of others apply (Art.15.4)

<<MUST item:Art.15:proc_exceptions>>
_Why: Art.12.5 / Art.15.4_

<<GUIDANCE>>

<<TEXT>>

## 7. Linkage to the data flow inventory (req:Art.30:data_flow_inventory) — fulfillment cannot operate without knowing where personal data lives; the procedure must name the inventory as the authoritative source

<<MUST item:Art.15:proc_inventory_link>>
_Why: Art.30 cross-control (promoted SHOULD→MUST Phase C batch 1 — load-bearing for fulfilment)_

<<GUIDANCE>>

<<TEXT>>

## 8. Bidirectional Art.15 ↔ Art.30 pair MUST — every system listed in the data flow inventory is reachable by DSAR fulfilment, and every system reached by fulfilment is captured in the inventory (closes the silent 'fulfilment queries somewhere RoPA doesn't list' gap)

<<MUST item:Art.15:proc_identity_pair_30>>
_Why: Art.30 cross-control coherence — analogous to A.5.16/A.5.17 rev_identity_pair MUSTs_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Front-line staff trained on DSAR recognition and routing (so a request in the wrong channel still reaches the procedure)

<<SHOULD item:Art.15:proc_training>>
_Why: EDPB 01/2022 — operational realism_

<<GUIDANCE>>

<<TEXT>>

### 2. DPO or legal escalation path for unusual requests (mixed-rights, joint controllers, processor-held data)

<<SHOULD item:Art.15:proc_escalation>>
_Why: Operational continuity_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
