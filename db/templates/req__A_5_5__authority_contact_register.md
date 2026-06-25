---
leaf_id: req:A.5.5:authority_contact_register
control_ref: A.5.5
standard_id: ISO27001:2022
evidence_type: contact_register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
table_shape: true
---

# Authority Contact Register

> A.5.5 requires the organization to establish and maintain contact with relevant authorities. The register is the live source of truth for which authorities apply, who to reach, and on what trigger. Maintenance, the applicable-authorities scope and periodic review are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.5:authority_contact_register -->
<!-- column: item:A.5.5:authorities_listed -->
<!-- column: item:A.5.5:contact_details -->
<!-- column: item:A.5.5:escalation_criteria -->
<!-- column: item:A.5.5:last_verified -->
<!-- column: item:A.5.5:owner -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.5:authority_contact_register -->
| Authorities Listed | Contact Details | Escalation Criteria | Last Verified | Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.5:authority_contact_register -->

## Column guidance — what to fill in

### Authorities Listed

<<MUST item:A.5.5:authorities_listed>>
_Why: 27002:5.5a_

> _Standard text:_ Relevant authorities enumerated (DPA, sectoral regulator, law enforcement, CERT/CSIRT)

### Contact Details

<<MUST item:A.5.5:contact_details>>
_Why: 27002:5.5a — contact details_

> _Standard text:_ Current contact details per authority (name/role, phone, email, address)

### Escalation Criteria

<<MUST item:A.5.5:escalation_criteria>>
_Why: 27002:5.5b_

> _Standard text:_ Engagement criteria per authority (incident classes, regulatory deadlines that require contact)

### Last Verified

<<MUST item:A.5.5:last_verified>>
_Why: 27002:5.5 — maintained_

> _Standard text:_ Last-verified date per entry (proves the entry is current)

### Owner

<<MUST item:A.5.5:owner>>
_Why: Accountability_

> _Standard text:_ Named owner responsible for the register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Backup Contacts

<<SHOULD item:A.5.5:backup_contacts>>
_Why: Continuity at time of incident_

> _Standard text:_ Backup or secondary contacts per authority

### Notification Templates

<<SHOULD item:A.5.5:notification_templates>>
_Why: Speed at time of incident_

> _Standard text:_ Notification templates referenced per authority type

### Jurisdiction Tag

<<SHOULD item:A.5.5:jurisdiction_tag>>
_Why: Cross-leaf coherence_

> _Standard text:_ Each authority tagged with the jurisdiction(s) that drove its inclusion (links back to the scope leaf)
