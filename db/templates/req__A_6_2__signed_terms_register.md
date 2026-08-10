---
leaf_id: req:A.6.2:signed_terms_register
control_ref: A.6.2
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Signed Employment Terms Register

<<DOC_CONTROL>>

> The operational catalogue of who has signed which version of the employment terms. Each row: personnel identifier, template version signed, signature date, current-version check. Drives the 'every active employee has current terms' completeness check

<!-- TABLE-COLUMNS leaf:req:A.6.2:signed_terms_register -->
<!-- column: item:A.6.2:reg_personnel_id -->
<!-- column: item:A.6.2:reg_template_version -->
<!-- column: item:A.6.2:reg_signature_date -->
<!-- column: item:A.6.2:reg_signature_method -->
<!-- column: item:A.6.2:reg_current_version_check -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear record of which employees have signed which version of your employment terms, making it easy to confirm everyone is up to date.

## When to use it

Use this register at all times to track employment terms signatures for every active employee, and update it whenever someone new signs or when terms change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Setting up the register for the first time may take 1-2 hours, plus about 10-15 minutes for each employee you add; ongoing updates are much quicker.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.2:signed_terms_register -->
| Reg Personnel Id | Reg Template Version | Reg Signature Date | Reg Signature Method | Reg Current Version Check |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.2:signed_terms_register -->

## Column guidance — what to fill in

### Reg Personnel Id

<<MUST item:A.6.2:reg_personnel_id>>
_Why: Accountability_

> _Standard text:_ Per-row personnel identifier (links to identity register A.5.16)

<<GUIDANCE>>

### Reg Template Version

<<MUST item:A.6.2:reg_template_version>>
_Why: 27002:6.2 — current_

> _Standard text:_ Template version signed per row (drives currency check — old-version signers may need recontract on material changes)

<<GUIDANCE>>

### Reg Signature Date

<<MUST item:A.6.2:reg_signature_date>>
_Why: 27002:6.2 — before access_

> _Standard text:_ Signature date per row (proves signing happened BEFORE access granted per A.5.18)

<<GUIDANCE>>

### Reg Signature Method

<<MUST item:A.6.2:reg_signature_method>>
_Why: Audit defensibility_

> _Standard text:_ Signature method per row (wet signature scanned / e-signature platform reference; ensures non-repudiation)

<<GUIDANCE>>

### Reg Current Version Check

<<MUST item:A.6.2:reg_current_version_check>>
_Why: 27002:6.2 — currency_

> _Standard text:_ Current-version check flag per row (yes / no-with-rationale-for-grandfathering) — surfaces personnel on outdated terms

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Amendment History

<<SHOULD item:A.6.2:reg_amendment_history>>
_Why: Operational discipline_

> _Standard text:_ Amendment history per row where contracts were amended mid-employment (drives change tracking)

<<GUIDANCE>>

### Reg Worker Category

<<SHOULD item:A.6.2:reg_worker_category>>
_Why: Cross-leaf coherence_

> _Standard text:_ Worker category per row (employee / contractor / intern — different categories may use different templates)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
