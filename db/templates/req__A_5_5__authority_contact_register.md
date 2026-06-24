---
leaf_id: req:A.5.5:authority_contact_register
control_ref: A.5.5
standard_id: ISO27001:2022
evidence_type: contact_register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
---

# Authority Contact Register

> A.5.5 requires the organization to establish and maintain contact with relevant authorities. The register is the live source of truth for which authorities apply, who to reach, and on what trigger. Maintenance, the applicable-authorities scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Relevant authorities enumerated (DPA, sectoral regulator, law enforcement, CERT/CSIRT)

<<MUST item:A.5.5:authorities_listed>>
_Why: 27002:5.5a_

<<TEXT>>

## 2. Current contact details per authority (name/role, phone, email, address)

<<MUST item:A.5.5:contact_details>>
_Why: 27002:5.5a — contact details_

<<TEXT>>

## 3. Engagement criteria per authority (incident classes, regulatory deadlines that require contact)

<<MUST item:A.5.5:escalation_criteria>>
_Why: 27002:5.5b_

<<TEXT>>

## 4. Last-verified date per entry (proves the entry is current)

<<MUST item:A.5.5:last_verified>>
_Why: 27002:5.5 — maintained_

<<TEXT>>

## 5. Named owner responsible for the register

<<MUST item:A.5.5:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Backup or secondary contacts per authority

<<SHOULD item:A.5.5:backup_contacts>>
_Why: Continuity at time of incident_

<<TEXT>>

### 2. Notification templates referenced per authority type

<<SHOULD item:A.5.5:notification_templates>>
_Why: Speed at time of incident_

<<TEXT>>

### 3. Each authority tagged with the jurisdiction(s) that drove its inclusion (links back to the scope leaf)

<<SHOULD item:A.5.5:jurisdiction_tag>>
_Why: Cross-leaf coherence_

<<TEXT>>
