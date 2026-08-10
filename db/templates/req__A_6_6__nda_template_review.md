---
leaf_id: req:A.6.6:nda_template_review
control_ref: A.6.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic NDA Template Review

<<DOC_CONTROL>>

> Periodic verification that the template still reflects current information classification (A.5.12), current jurisdictional enforceability (Schrems-style impacts on cross-border NDAs), and that all active signers are on a current-enough version. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.6:nda_template_review -->
<!-- column: item:A.6.6:rev_date -->
<!-- column: item:A.6.6:rev_reviewer -->
<!-- column: item:A.6.6:rev_classification_drift -->
<!-- column: item:A.6.6:rev_enforceability -->
<!-- column: item:A.6.6:rev_signer_currency -->
<!-- column: item:A.6.6:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep your NDA documents up to date by checking that they match current information classification rules, legal requirements, and that all signers are using the latest version.

## When to use it

Use this template once a year to review your NDA template, making sure it still fits your organization’s needs and legal obligations. It applies to every environment where NDAs are used.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 1.5 hours filling this out from scratch, depending on how many signers and versions you need to review.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.6:nda_template_review -->
| Rev Date | Rev Reviewer | Rev Classification Drift | Rev Enforceability | Rev Signer Currency | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.6:nda_template_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.6:rev_date>>
_Why: 27002:6.6 — regularly reviewed_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.6.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Legal counsel + InfoSec lead jointly)

<<GUIDANCE>>

### Rev Classification Drift

<<MUST item:A.6.6:rev_classification_drift>>
_Why: Cross-control coherence_

> _Standard text:_ Information-classification drift check — has A.5.12 classification scheme changed in ways affecting NDA info_classes?

<<GUIDANCE>>

### Rev Enforceability

<<MUST item:A.6.6:rev_enforceability>>
_Why: 27002:6.6 — applicable laws_

> _Standard text:_ Enforceability check per jurisdiction (legal counsel input — case-law shifts, Schrems-style impacts on cross-border data flows in NDA scope)

<<GUIDANCE>>

### Rev Signer Currency

<<MUST item:A.6.6:rev_signer_currency>>
_Why: 27002:6.6 — current_

> _Standard text:_ Signer-currency analysis (% on current template version; plan for re-signing the gap where material clauses changed)

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.6.6:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the live template and to the signer-re-signing plan

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.6:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (material classification change, case-law shift, M&A bringing new counterparty types)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.6.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
