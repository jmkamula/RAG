---
leaf_id: req:Art.23:restriction_register
control_ref: Art.23
standard_id: GDPR:2016/679
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Art.23 Restriction Application Register

<<DOC_CONTROL>>

> Per-invocation record — every time an Art.23 restriction is applied to deny / limit a subject right. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.23:restriction_register -->
<!-- column: item:Art.23:reg_invocation_id -->
<!-- column: item:Art.23:reg_law_citation -->
<!-- column: item:Art.23:reg_right_restricted -->
<!-- column: item:Art.23:reg_purpose -->
<!-- column: item:Art.23:reg_subject_notice -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record every time you apply a restriction under Article 23 of the GDPR, making it easier to track and review these decisions for compliance purposes.

## When to use it

Use this register whenever you deny or limit an individual's rights based on Article 23 restrictions. Review and update the register at least once a year to ensure it stays current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes to complete the initial required sections, plus additional time for each restriction event you need to record.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.23:restriction_register -->
| Reg Invocation Id | Reg Law Citation | Reg Right Restricted | Reg Purpose | Reg Subject Notice |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.23:restriction_register -->

## Column guidance — what to fill in

### Reg Invocation Id

<<MUST item:Art.23:reg_invocation_id>>
_Why: Audit_

> _Standard text:_ Unique invocation identifier per row

<<GUIDANCE>>

### Reg Law Citation

<<MUST item:Art.23:reg_law_citation>>
_Why: Art.23.1_

> _Standard text:_ Per-row Member State law cited (article + section)

<<GUIDANCE>>

### Reg Right Restricted

<<MUST item:Art.23:reg_right_restricted>>
_Why: Art.23.1_

> _Standard text:_ Per-row right restricted (Art.12-22 + Art.34)

<<GUIDANCE>>

### Reg Purpose

<<MUST item:Art.23:reg_purpose>>
_Why: Art.23.1_

> _Standard text:_ Per-row Art.23.1 a-j purpose

<<GUIDANCE>>

### Reg Subject Notice

<<MUST item:Art.23:reg_subject_notice>>
_Why: Art.23.2.h_

> _Standard text:_ Per-row subject notice (where required by Art.23.2.h)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Legal Review

<<SHOULD item:Art.23:reg_legal_review>>
_Why: Defensibility_

> _Standard text:_ Per-row legal counsel sign-off

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
