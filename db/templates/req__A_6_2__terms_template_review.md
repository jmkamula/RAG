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

<<DOC_CONTROL>>

> Periodic verification that the template still reflects current InfoSec policy (referenced policies haven't drifted), current employment law (jurisdictional shifts), and that all signers are on a current-enough version. Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.6.2:terms_template_review -->
<!-- column: item:A.6.2:rev_date -->
<!-- column: item:A.6.2:rev_reviewer -->
<!-- column: item:A.6.2:rev_policy_drift -->
<!-- column: item:A.6.2:rev_legal_drift -->
<!-- column: item:A.6.2:rev_signer_currency -->
<!-- column: item:A.6.2:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you confirm that your employment terms document stays up to date with your information security policies and current employment laws. It also tracks that everyone has signed the latest version.

## When to use it

Use this template once a year to review your employment terms document, making sure it matches your current InfoSec policies and legal requirements. It applies to all organizations, regardless of size or industry.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 90 minutes completing this review from scratch, depending on how many elements you need to check and how many signers you have.

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

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.6.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (HR + InfoSec + Legal jointly)

<<GUIDANCE>>

### Rev Policy Drift

<<MUST item:A.6.2:rev_policy_drift>>
_Why: Cross-control coherence_

> _Standard text:_ Referenced-policy drift check — has A.5.1/A.5.10/A.5.15 changed in ways that require template amendment?

<<GUIDANCE>>

### Rev Legal Drift

<<MUST item:A.6.2:rev_legal_drift>>
_Why: 27002:6.2 — applicable laws_

> _Standard text:_ Employment-law drift check per jurisdiction (legal counsel input)

<<GUIDANCE>>

### Rev Signer Currency

<<MUST item:A.6.2:rev_signer_currency>>
_Why: 27002:6.2 — current_

> _Standard text:_ Signer-currency analysis — what fraction of active workers on the current template? plan for recontracting the gap

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.6.2:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the live template and to the signer-recontracting plan

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.6.2:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers (major policy change, employment-law reform, regulator action affecting employment InfoSec terms)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.6.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
