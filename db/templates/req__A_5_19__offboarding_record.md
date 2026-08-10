---
leaf_id: req:A.5.19:offboarding_record
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Supplier Offboarding Records

<<DOC_CONTROL>>

> A.5.19 requires that transitions at the end of a supplier relationship are managed — anything that needs to move (information, processing facilities, access) does move. Offboarding records evidence that those transitions actually happened: data returned/destroyed, access removed, lessons captured. One record per offboarding event, traceable back to the supplier register

<!-- TABLE-COLUMNS leaf:req:A.5.19:offboarding_record -->
<!-- column: item:A.5.19:off_trigger -->
<!-- column: item:A.5.19:off_data_return -->
<!-- column: item:A.5.19:off_access_removal -->
<!-- column: item:A.5.19:off_transition -->
<!-- column: item:A.5.19:off_authoriser -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and track the key steps taken when ending a supplier relationship, such as returning or destroying data and removing access, ensuring nothing is missed during offboarding.

## When to use it

Use this template every time you end a relationship with a supplier, and update it whenever there are changes or new offboarding events to record.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing a new record from scratch, as each required section takes around 10 to 15 minutes to fill in.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.19:offboarding_record -->
| Off Trigger | Off Data Return | Off Access Removal | Off Transition | Off Authoriser |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.19:offboarding_record -->

## Column guidance — what to fill in

### Off Trigger

<<MUST item:A.5.19:off_trigger>>
_Why: 27002:5.19m_

> _Standard text:_ Offboarding trigger captured (termination / non-renewal / supplier failure / re-tendering)

<<GUIDANCE>>

### Off Data Return

<<MUST item:A.5.19:off_data_return>>
_Why: 27002:5.19m_

> _Standard text:_ Data return or destruction evidence (with attestation from supplier where applicable)

<<GUIDANCE>>

### Off Access Removal

<<MUST item:A.5.19:off_access_removal>>
_Why: 27002:5.19m_

> _Standard text:_ Logical and physical access removal evidence (link to A.5.18 / A.7.2)

<<GUIDANCE>>

### Off Transition

<<MUST item:A.5.19:off_transition>>
_Why: 27002:5.19m_

> _Standard text:_ Transition completion evidence (operational handover, replacement supplier engaged where applicable)

<<GUIDANCE>>

### Off Authoriser

<<MUST item:A.5.19:off_authoriser>>
_Why: Accountability_

> _Standard text:_ Authoriser of the offboarding decision

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Off Timeliness

<<SHOULD item:A.5.19:off_timeliness>>
_Why: Operational sufficiency_

> _Standard text:_ Timeliness target stated (e.g., access removed within 5 business days of contract end)

<<GUIDANCE>>

### Off Lessons

<<SHOULD item:A.5.19:off_lessons>>
_Why: Continual improvement_

> _Standard text:_ Lessons-learned link feeding back into the procedure or selection criteria

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
