---
leaf_id: req:A.7.4.8:disposal_procedure
control_ref: A.7.4.8
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# PII Disposal Procedure

> §7.4.8 requires documented policies / procedures / mechanisms for disposal. Focuses on the HOW (techniques + media) whereas A.7.4.5 is the WHEN + WHAT (trigger + scope). Cross-links to A.5.28 evidence handling.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Technique map per media type (electronic — cryptographic erase + overwrite / physical — shredding + degaussing / cloud — provider-attested)

<<MUST item:A.7.4.8:proc_technique_map>>
_Why: §7.4.8 — disposal techniques_

<<TEXT>>

## 2. Technique selection factors (nature + extent of PII + metadata associations + media characteristics)

<<MUST item:A.7.4.8:proc_technique_selection>>
_Why: §7.4.8 — factors to consider_

<<TEXT>>

## 3. Media lifecycle coverage (production + backup + archive + failed hardware + decommissioned equipment)

<<MUST item:A.7.4.8:proc_media_lifecycle>>
_Why: Comprehensiveness_

<<TEXT>>

## 4. Disposal certificate / attestation captured per action

<<MUST item:A.7.4.8:proc_certificate>>
_Why: Audit trail_

<<TEXT>>

## 5. Cross-link to A.5.28 evidence handling — disposal_record shape reused for evidence forensics

<<MUST item:A.7.4.8:proc_cross_link_a528>>
_Why: Integration_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Infrastructure + DPO)

<<SHOULD item:A.7.4.8:proc_owner>>
_Why: Accountability_

<<TEXT>>
