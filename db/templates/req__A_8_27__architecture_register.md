---
leaf_id: req:A.8.27:architecture_register
control_ref: A.8.27
standard_id: ISO27001:2022
evidence_type: register
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Reference Architecture Register

<<DOC_CONTROL>>

> Per-pattern catalogue — pattern id, applicable context, security principles embedded, last-review date

<!-- TABLE-COLUMNS leaf:req:A.8.27:architecture_register -->
<!-- column: item:A.8.27:reg_pattern_id -->
<!-- column: item:A.8.27:reg_context -->
<!-- column: item:A.8.27:reg_principles_embedded -->
<!-- column: item:A.8.27:reg_owner -->
<!-- column: item:A.8.27:reg_last_reviewed -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep a clear, organized record of your reference architecture patterns, including their context, security principles, and review history. It's useful for tracking compliance and ensuring your designs meet security standards.

## When to use it

Use this register whenever your project or system matches certain predefined criteria that require cataloguing architecture patterns. Update it as needed, especially after changes or periodic reviews.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each pattern you document. Completing the register from scratch may take 1-2 hours for a small set of patterns, and more as you add rows.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.8.27:architecture_register -->
| Reg Pattern Id | Reg Context | Reg Principles Embedded | Reg Owner | Reg Last Reviewed |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.8.27:architecture_register -->

## Column guidance — what to fill in

### Reg Pattern Id

<<MUST item:A.8.27:reg_pattern_id>>
_Why: Identification_

> _Standard text:_ Per-pattern unique identifier

<<GUIDANCE>>

### Reg Context

<<MUST item:A.8.27:reg_context>>
_Why: 27002:8.27 — applied_

> _Standard text:_ Per-pattern applicable context (when to use this pattern)

<<GUIDANCE>>

### Reg Principles Embedded

<<MUST item:A.8.27:reg_principles_embedded>>
_Why: Cross-leaf coherence_

> _Standard text:_ Per-pattern principles embedded (mapping back to policy's principle set)

<<GUIDANCE>>

### Reg Owner

<<MUST item:A.8.27:reg_owner>>
_Why: Accountability_

> _Standard text:_ Per-pattern named owner

<<GUIDANCE>>

### Reg Last Reviewed

<<MUST item:A.8.27:reg_last_reviewed>>
_Why: Drift detection_

> _Standard text:_ Per-pattern last-review date

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Reg Usage Count

<<SHOULD item:A.8.27:reg_usage_count>>
_Why: Operational visibility_

> _Standard text:_ Per-pattern usage-count (how many projects adopted it — drives 'is this pattern actually used' signal)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
