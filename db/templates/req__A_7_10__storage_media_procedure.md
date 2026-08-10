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

<<DOC_CONTROL>>

> A.7.10 requires storage media to be managed through their lifecycle (acquisition, use, transportation, disposal). The procedure documents acquisition controls, use controls, transport rules, disposal handoff, inventory. The media register, applicable-classes scope and periodic review are sibling leaves

## What this template gives you

This template helps you document how you manage storage media throughout their lifecycle, including acquisition, use, transport, and disposal. It ensures you have clear procedures and records to meet ISO 27001 requirements.

## When to use it

Use this template whenever you need to define or update your process for handling storage media in your environment. Review and refresh the document as needed to keep it current with your practices.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes drafting this from scratch, depending on the detail needed for each required section and the size of your media inventory.

## 1. Acquisition controls (approved media types, sourcing controls)

<<MUST item:A.7.10:acquisition>>
_Why: 27002:7.10 — acquisition_

<<GUIDANCE>>

<<TEXT>>

## 2. Use controls (encryption, classification labels per A.5.13, allowed-use rules)

<<MUST item:A.7.10:use_controls>>
_Why: 27002:7.10 — use_

<<GUIDANCE>>

<<TEXT>>

## 3. Transport rules (encryption in transit, courier requirements, chain of custody)

<<MUST item:A.7.10:transport>>
_Why: 27002:7.10 — transportation_

<<GUIDANCE>>

<<TEXT>>

## 4. Disposal controls (handoff to A.7.14 secure disposal procedure with chain-of-custody preserved)

<<MUST item:A.7.10:disposal>>
_Why: 27002:7.10 — disposal_

<<GUIDANCE>>

<<TEXT>>

## 5. Inventory of removable media issued (who holds what)

<<MUST item:A.7.10:inventory>>
_Why: 27002:7.10 — life cycle_

<<GUIDANCE>>

<<TEXT>>

## 6. Individual media tracking via serial or asset tag

<<MUST item:A.7.10:individual_tracking>>
_Why: Loss detection_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exception process for legacy media that cannot meet current controls

<<SHOULD item:A.7.10:legacy_exception>>
_Why: Pragmatic transition_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
