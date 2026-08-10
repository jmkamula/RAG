---
leaf_id: req:7.5:isms_document_register
control_ref: 7.5
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 7
should_count: 1
table_shape: true
---

# ISMS Document Register

<<DOC_CONTROL>>

> Per-document record — every controlled ISMS document with owner, version, approval date, next review date. The live inventory that proves the policy is being applied. Annual refresh (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.5:isms_document_register -->
<!-- column: item:7.5:reg_doc_id -->
<!-- column: item:7.5:reg_title -->
<!-- column: item:7.5:reg_owner -->
<!-- column: item:7.5:reg_version -->
<!-- column: item:7.5:reg_approval_date -->
<!-- column: item:7.5:reg_next_review -->
<!-- column: item:7.5:reg_classification -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, up-to-date list of all your important ISMS documents, showing who owns each one, its version, and key review dates. It’s useful for tracking compliance and demonstrating that your document management policy is being followed.

## When to use it

Use this register whenever you need to maintain oversight of your ISMS documents—it's always relevant for your environment. Plan to review and update it about once a year to keep information current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per document entry for the required details. If you’re starting from scratch, setting up the register for a handful of documents may take 1-2 hours.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.5:isms_document_register -->
| Reg Doc Id | Reg Title | Reg Owner | Reg Version | Reg Approval Date | Reg Next Review | Reg Classification |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.5:isms_document_register -->

## Column guidance — what to fill in

### Reg Doc Id

<<MUST item:7.5:reg_doc_id>>
_Why: Audit defensibility_

> _Standard text:_ Unique document identifier per row

<<GUIDANCE>>

### Reg Title

<<MUST item:7.5:reg_title>>
_Why: Discoverability_

> _Standard text:_ Document title per row

<<GUIDANCE>>

### Reg Owner

<<MUST item:7.5:reg_owner>>
_Why: Accountability_

> _Standard text:_ Document owner per row

<<GUIDANCE>>

### Reg Version

<<MUST item:7.5:reg_version>>
_Why: Clause 7.5.3 — control_

> _Standard text:_ Current version per row

<<GUIDANCE>>

### Reg Approval Date

<<MUST item:7.5:reg_approval_date>>
_Why: Currency_

> _Standard text:_ Last approval date per row

<<GUIDANCE>>

### Reg Next Review

<<MUST item:7.5:reg_next_review>>
_Why: Currency_

> _Standard text:_ Next review date per row (drives staleness alerts)

<<GUIDANCE>>

### Reg Classification

<<MUST item:7.5:reg_classification>>
_Why: Clause 7.5.3 — protected_

> _Standard text:_ Information classification per row (cross-link to A.5.12)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Retention

<<SHOULD item:7.5:reg_retention>>
_Why: Clause 7.5.3 — retention_

> _Standard text:_ Retention period per row (cross-link to A.5.33 / A.5.34)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
