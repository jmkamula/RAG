---
leaf_id: req:A.7.10:storage_media_procedure
control_ref: A.7.10
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 1
---

# Storage Media Lifecycle Procedure

> A.7.10 requires storage media to be managed through their lifecycle (acquisition, use, transportation, disposal). The procedure documents acquisition controls, use controls, transport rules, disposal handoff, inventory. The media register, applicable-classes scope and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Acquisition controls (approved media types, sourcing controls)

<<MUST item:A.7.10:acquisition>>
_Why: 27002:7.10 — acquisition_

<<TEXT>>

## 2. Use controls (encryption, classification labels per A.5.13, allowed-use rules)

<<MUST item:A.7.10:use_controls>>
_Why: 27002:7.10 — use_

<<TEXT>>

## 3. Transport rules (encryption in transit, courier requirements, chain of custody)

<<MUST item:A.7.10:transport>>
_Why: 27002:7.10 — transportation_

<<TEXT>>

## 4. Disposal controls (handoff to A.7.14 secure disposal procedure with chain-of-custody preserved)

<<MUST item:A.7.10:disposal>>
_Why: 27002:7.10 — disposal_

<<TEXT>>

## 5. Inventory of removable media issued (who holds what)

<<MUST item:A.7.10:inventory>>
_Why: 27002:7.10 — life cycle_

<<TEXT>>

## 6. Individual media tracking via serial or asset tag

<<MUST item:A.7.10:individual_tracking>>
_Why: Loss detection_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception process for legacy media that cannot meet current controls

<<SHOULD item:A.7.10:legacy_exception>>
_Why: Pragmatic transition_

<<TEXT>>
