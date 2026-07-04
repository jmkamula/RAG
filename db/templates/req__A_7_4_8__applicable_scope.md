---
leaf_id: req:A.7.4.8:applicable_scope
control_ref: A.7.4.8
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Disposal Contexts Scope

> The upstream — which disposal contexts arise (end-of-processing per A.7.4.5 + failed hardware + decommissioned equipment + returned devices + paper records).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Disposal contexts enumerated (end-of-processing / hardware failure / decommission / device return / paper archive)

<<MUST item:A.7.4.8:scope_contexts>>
_Why: Coverage_

<<TEXT>>

## 2. Media types in inventory (SSD / HDD / tape / paper / cloud volume / mobile device)

<<MUST item:A.7.4.8:scope_media_types>>
_Why: Coverage_

<<TEXT>>

## 3. Cloud disposal dependencies (provider attestations required, retention windows outside org's control)

<<MUST item:A.7.4.8:scope_cloud_dependencies>>
_Why: Cloud specifics_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new media type / new cloud provider)

<<SHOULD item:A.7.4.8:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
