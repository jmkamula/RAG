---
leaf_id: req:A.5.6:special_interest_group_register
control_ref: A.5.6
standard_id: ISO27001:2022
evidence_type: contact_register
trigger_type: universal
template_version: 1
must_count: 5
should_count: 3
---

# Special Interest Group and Professional Forum Register

> A.5.6 requires contact with special interest groups (SIGs), security forums, and professional associations. The register lists current memberships and engagements with the basis for each. Engagement procedure, the risk-topic scope (which threats/skills drive the membership choices) and annual review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. SIGs and forums enumerated (ISACs, ISC2/ISACA chapters, vendor security groups, sector-specific councils)

<<MUST item:A.5.6:sigs_listed>>
_Why: 27002:5.6a_

<<TEXT>>

## 2. Basis of contact per entry (paid membership, subscription, named-individual attendance, community access)

<<MUST item:A.5.6:basis_of_contact>>
_Why: 27002:5.6 — contact_

<<TEXT>>

## 3. Topics or threat categories that drive each engagement

<<MUST item:A.5.6:topics_shared>>
_Why: 27002:5.6b — keep current_

<<TEXT>>

## 4. Last-engaged date per entry (event attended, briefing received, working group meeting)

<<MUST item:A.5.6:last_engaged>>
_Why: 27002:5.6 — maintain_

<<TEXT>>

## 5. Named owner responsible for the register

<<MUST item:A.5.6:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Internal representative or point of contact per group

<<SHOULD item:A.5.6:representative>>
_Why: Accountability_

<<TEXT>>

### 2. Subscription or membership renewal dates tracked

<<SHOULD item:A.5.6:renewal_dates>>
_Why: Continuity of access_

<<TEXT>>

### 3. Each entry tagged with the risk topics that drove inclusion (links back to the scope leaf)

<<SHOULD item:A.5.6:topic_tag>>
_Why: Cross-leaf coherence_

<<TEXT>>
