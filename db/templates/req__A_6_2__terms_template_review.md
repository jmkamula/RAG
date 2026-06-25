---
leaf_id: req:A.6.2:terms_template_review
control_ref: A.6.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
table_shape: true
---

# Periodic Employment Terms Template Review

> Periodic verification that the template still reflects current InfoSec policy (referenced policies haven't drifted), current employment law (jurisdictional shifts), and that all signers are on a current-enough version. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.2:terms_template_review -->
<!-- column: item:A.6.2:rev_date -->
<!-- column: item:A.6.2:rev_reviewer -->
<!-- column: item:A.6.2:rev_policy_drift -->
<!-- column: item:A.6.2:rev_legal_drift -->
<!-- column: item:A.6.2:rev_signer_currency -->
<!-- column: item:A.6.2:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.6.2:terms_template_review -->
| Rev Date | Rev Reviewer | Rev Policy Drift | Rev Legal Drift | Rev Signer Currency | Rev Register Update |
|---|---|---|---|---|---|
|          |          |          |          |          |          |
|          |          |          |          |          |          |
|          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.6.2:terms_template_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.6.2:rev_date>>
_Why: 27002:6.2 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.6.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR + InfoSec + Legal jointly)

### Rev Policy Drift

<<MUST item:A.6.2:rev_policy_drift>>
_Why: Cross-control coherence_

> _Standard text:_ Referenced-policy drift check — has A.5.1/A.5.10/A.5.15 changed in ways that require template amendment?

### Rev Legal Drift

<<MUST item:A.6.2:rev_legal_drift>>
_Why: 27002:6.2 — applicable laws_

> _Standard text:_ Employment-law drift check per jurisdiction (legal counsel input)

### Rev Signer Currency

<<MUST item:A.6.2:rev_signer_currency>>
_Why: 27002:6.2 — current_

> _Standard text:_ Signer-currency analysis — what fraction of active workers on the current template? plan for recontracting the gap

### Rev Register Update

<<MUST item:A.6.2:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the live template and to the signer-recontracting plan

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.2:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (major policy change, employment-law reform, regulator action affecting employment InfoSec terms)

### Rev Next Date

<<SHOULD item:A.6.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
