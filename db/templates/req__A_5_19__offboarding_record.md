---
leaf_id: req:A.5.19:offboarding_record
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Supplier Offboarding Records

> A.5.19 requires that transitions at the end of a supplier relationship are managed — anything that needs to move (information, processing facilities, access) does move. Offboarding records evidence that those transitions actually happened: data returned/destroyed, access removed, lessons captured. One record per offboarding event, traceable back to the supplier register

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Offboarding trigger captured (termination / non-renewal / supplier failure / re-tendering)

<<MUST item:A.5.19:off_trigger>>
_Why: 27002:5.19m_

<<TEXT>>

## 2. Data return or destruction evidence (with attestation from supplier where applicable)

<<MUST item:A.5.19:off_data_return>>
_Why: 27002:5.19m_

<<TEXT>>

## 3. Logical and physical access removal evidence (link to A.5.18 / A.7.2)

<<MUST item:A.5.19:off_access_removal>>
_Why: 27002:5.19m_

<<TEXT>>

## 4. Transition completion evidence (operational handover, replacement supplier engaged where applicable)

<<MUST item:A.5.19:off_transition>>
_Why: 27002:5.19m_

<<TEXT>>

## 5. Authoriser of the offboarding decision

<<MUST item:A.5.19:off_authoriser>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Timeliness target stated (e.g., access removed within 5 business days of contract end)

<<SHOULD item:A.5.19:off_timeliness>>
_Why: Operational sufficiency_

<<TEXT>>

### 2. Lessons-learned link feeding back into the procedure or selection criteria

<<SHOULD item:A.5.19:off_lessons>>
_Why: Continual improvement_

<<TEXT>>
