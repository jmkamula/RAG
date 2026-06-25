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

> A.5.6 requires contact with special interest groups (SIGs), security forums, and professional associations. The register lists current memberships and engagements with the basis for each. Engagement procedure, the risk-topic scope (which threats/skills drive the membership choices) and annual review are sibling leaves

<!-- TABLE-COLUMNS leaf:req:A.5.6:special_interest_group_register -->
<!-- column: item:A.5.6:sigs_listed -->
<!-- column: item:A.5.6:basis_of_contact -->
<!-- column: item:A.5.6:topics_shared -->
<!-- column: item:A.5.6:last_engaged -->
<!-- column: item:A.5.6:owner -->
<!-- /TABLE-COLUMNS -->

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

### Basis Of Contact

<<MUST item:A.5.6:basis_of_contact>>
_Why: 27002:5.6 — contact_

> _Standard text:_ Basis of contact per entry (paid membership, subscription, named-individual attendance, community access)

### Topics Shared

<<MUST item:A.5.6:topics_shared>>
_Why: 27002:5.6b — keep current_

> _Standard text:_ Topics or threat categories that drive each engagement

### Last Engaged

<<MUST item:A.5.6:last_engaged>>
_Why: 27002:5.6 — maintain_

> _Standard text:_ Last-engaged date per entry (event attended, briefing received, working group meeting)

### Owner

<<MUST item:A.5.6:owner>>
_Why: Accountability_

> _Standard text:_ Named owner responsible for the register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Representative

<<SHOULD item:A.5.6:representative>>
_Why: Accountability_

> _Standard text:_ Internal representative or point of contact per group

### Renewal Dates

<<SHOULD item:A.5.6:renewal_dates>>
_Why: Continuity of access_

> _Standard text:_ Subscription or membership renewal dates tracked

### Topic Tag

<<SHOULD item:A.5.6:topic_tag>>
_Why: Cross-leaf coherence_

> _Standard text:_ Each entry tagged with the risk topics that drove inclusion (links back to the scope leaf)
