---
leaf_id: req:A.7.1:perimeter_register
control_ref: A.7.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 1
---

# Per-Site Perimeter Register

> The catalogue of perimeters across all sites — site identifier, perimeter id, area classification, barrier inventory, access-point list, owner. Drives 'show me every site has a defined perimeter' completeness check

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Site identifier per perimeter row (HQ, regional offices, data centres, co-locations)

<<MUST item:A.7.1:reg_site_id>>
_Why: 27002:7.1 — defined_

<<TEXT>>

## 2. Perimeter identifier per row (a site may have multiple perimeters — outer + inner + secure-room)

<<MUST item:A.7.1:reg_perimeter_id>>
_Why: 27002:7.1 — security perimeters_

<<TEXT>>

## 3. Area classification per row (matches policy's classification scheme)

<<MUST item:A.7.1:reg_classification>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Barriers in place per row (specific barrier inventory — what walls, what doors, what mechanisms)

<<MUST item:A.7.1:reg_barriers>>
_Why: 27002:7.1 — used to protect_

<<TEXT>>

## 5. Last assessment date per row (drives staleness detection)

<<MUST item:A.7.1:reg_last_assessed>>
_Why: 27002:7.1 — maintained_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Remediation log per row where barriers fall short of classification requirements

<<SHOULD item:A.7.1:reg_remediation>>
_Why: Operational discipline_

<<TEXT>>
