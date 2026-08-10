---
leaf_id: req:A.7.2.8:pii_processing_ropa
control_ref: A.7.2.8
standard_id: ISO27701:2019
evidence_type: register
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 8
should_count: 1
table_shape: true
---

# PII Records of Processing (RoPA)

<<DOC_CONTROL>>

> §7.2.8 requires records of PII processing activities to demonstrate accountability. Register-as-primary (records_program spine): the RoPA is the canonical artefact. Per-activity row — type / purpose / categories of PII + subjects / recipients + international transfers / retention / security measures. Bridges to GDPR Art.30 with the same required fields.

<!-- TABLE-COLUMNS leaf:req:A.7.2.8:pii_processing_ropa -->
<!-- column: item:A.7.2.8:ropa_activity_id -->
<!-- column: item:A.7.2.8:ropa_type_purpose -->
<!-- column: item:A.7.2.8:ropa_pii_categories -->
<!-- column: item:A.7.2.8:ropa_recipients -->
<!-- column: item:A.7.2.8:ropa_transfer_safeguards -->
<!-- column: item:A.7.2.8:ropa_retention -->
<!-- column: item:A.7.2.8:ropa_security_measures -->
<!-- column: item:A.7.2.8:ropa_owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of how your organization handles personal data, making it easier to show compliance with privacy regulations like ISO 27701 and GDPR.

## When to use it

Use this register when your activities involve processing personal information and your compliance profile requires formal documentation. Plan to review and update it about once a year, or whenever your processing activities change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10 to 15 minutes per required section for each processing activity you document. Completing the register from scratch typically takes 1–2 hours for a small set of activities, but more if you have many processes.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.2.8:pii_processing_ropa -->
| Ropa Activity Id | Ropa Type Purpose | Ropa Pii Categories | Ropa Recipients | Ropa Transfer Safeguards | Ropa Retention | Ropa Security Measures | Ropa Owner |
|---|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.2.8:pii_processing_ropa -->

## Column guidance — what to fill in

### Ropa Activity Id

<<MUST item:A.7.2.8:ropa_activity_id>>
_Why: Referenceability_

> _Standard text:_ Unique processing-activity identifier per row

<<GUIDANCE>>

### Ropa Type Purpose

<<MUST item:A.7.2.8:ropa_type_purpose>>
_Why: §7.2.8 — type + purposes + Art.30.1.b_

> _Standard text:_ Type + purpose of processing per row (link to A.7.2.1 register)

<<GUIDANCE>>

### Ropa Pii Categories

<<MUST item:A.7.2.8:ropa_pii_categories>>
_Why: §7.2.8 — categories of PII + PII principals + Art.30.1.c_

> _Standard text:_ Categories of PII per row + categories of subjects (e.g. employees, customers, minors)

<<GUIDANCE>>

### Ropa Recipients

<<MUST item:A.7.2.8:ropa_recipients>>
_Why: §7.2.8 + Art.30.1.d + Art.30.1.e_

> _Standard text:_ Categories of recipients per row (including third countries + international orgs)

<<GUIDANCE>>

### Ropa Transfer Safeguards

<<MUST item:A.7.2.8:ropa_transfer_safeguards>>
_Why: Art.30.1.e + Chap V_

> _Standard text:_ Transfer safeguards per row where third-country transfer occurs (Chap V mechanism cited)

<<GUIDANCE>>

### Ropa Retention

<<MUST item:A.7.2.8:ropa_retention>>
_Why: Art.30.1.f_

> _Standard text:_ Retention period per row (or criteria)

<<GUIDANCE>>

### Ropa Security Measures

<<MUST item:A.7.2.8:ropa_security_measures>>
_Why: §7.2.8 + Art.30.1.g_

> _Standard text:_ General description of technical + organizational security measures per row

<<GUIDANCE>>

### Ropa Owner

<<MUST item:A.7.2.8:ropa_owner>>
_Why: §7.2.8 — owner responsible_

> _Standard text:_ Named owner responsible for accuracy + completeness

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Ropa Dpia Link

<<SHOULD item:A.7.2.8:ropa_dpia_link>>
_Why: §7.2.8 implementation — PIA report + cross-link_

> _Standard text:_ DPIA report link per row where PIA performed (A.7.2.5)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
