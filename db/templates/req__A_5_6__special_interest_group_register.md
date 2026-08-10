---
leaf_id: req:A.5.6:special_interest_group_register
control_ref: A.5.6
standard_id: ISO27001:2022
evidence_type: contact_register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
table_shape: true
---

# Special Interest Group and Professional Forum Register

<<DOC_CONTROL>>

> A.5.6 requires contact with special interest groups (SIGs), security forums, and professional associations. The register lists current memberships and engagements with the basis for each. Engagement procedure, the risk-topic scope (which threats/skills drive the membership choices) and annual review are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.6:special_interest_group_register -->
<!-- column: item:A.5.6:sigs_listed -->
<!-- column: item:A.5.6:basis_of_contact -->
<!-- column: item:A.5.6:topics_shared -->
<!-- column: item:A.5.6:last_engaged -->
<!-- column: item:A.5.6:owner -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you keep track of your organization's memberships and participation in security and professional groups, making it easy to show how you stay informed about industry risks and best practices.

## When to use it

Use this register at all times to document your ongoing involvement with special interest groups and forums, updating it whenever your memberships or engagement details change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes to complete the required sections for the first time, with additional time needed for each group or forum you add.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.6:special_interest_group_register -->
| Sigs Listed | Basis Of Contact | Topics Shared | Last Engaged | Owner |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.6:special_interest_group_register -->

## Column guidance — what to fill in

### Sigs Listed

<<MUST item:A.5.6:sigs_listed>>
_Why: 27002:5.6a_

> _Standard text:_ SIGs and forums enumerated (ISACs, ISC2/ISACA chapters, vendor security groups, sector-specific councils)

<<GUIDANCE>>

### Basis Of Contact

<<MUST item:A.5.6:basis_of_contact>>
_Why: 27002:5.6 — contact_

> _Standard text:_ Basis of contact per entry (paid membership, subscription, named-individual attendance, community access)

<<GUIDANCE>>

### Topics Shared

<<MUST item:A.5.6:topics_shared>>
_Why: 27002:5.6b — keep current_

> _Standard text:_ Topics or threat categories that drive each engagement

<<GUIDANCE>>

### Last Engaged

<<MUST item:A.5.6:last_engaged>>
_Why: 27002:5.6 — maintain_

> _Standard text:_ Last-engaged date per entry (event attended, briefing received, working group meeting)

<<GUIDANCE>>

### Owner

<<MUST item:A.5.6:owner>>
_Why: Accountability_

> _Standard text:_ Named owner responsible for the register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Representative

<<SHOULD item:A.5.6:representative>>
_Why: Accountability_

> _Standard text:_ Internal representative or point of contact per group

<<GUIDANCE>>

### Renewal Dates

<<SHOULD item:A.5.6:renewal_dates>>
_Why: Continuity of access_

> _Standard text:_ Subscription or membership renewal dates tracked

<<GUIDANCE>>

### Topic Tag

<<SHOULD item:A.5.6:topic_tag>>
_Why: Cross-leaf coherence_

> _Standard text:_ Each entry tagged with the risk topics that drove inclusion (links back to the scope leaf)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
