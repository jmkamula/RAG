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
---

# Periodic Employment Terms Template Review

> Periodic verification that the template still reflects current InfoSec policy (referenced policies haven't drifted), current employment law (jurisdictional shifts), and that all signers are on a current-enough version. Annual cadence (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.6.2:rev_date>>
_Why: 27002:6.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (HR + InfoSec + Legal jointly)

<<MUST item:A.6.2:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Referenced-policy drift check — has A.5.1/A.5.10/A.5.15 changed in ways that require template amendment?

<<MUST item:A.6.2:rev_policy_drift>>
_Why: Cross-control coherence_

<<TEXT>>

## 4. Employment-law drift check per jurisdiction (legal counsel input)

<<MUST item:A.6.2:rev_legal_drift>>
_Why: 27002:6.2 — applicable laws_

<<TEXT>>

## 5. Signer-currency analysis — what fraction of active workers on the current template? plan for recontracting the gap

<<MUST item:A.6.2:rev_signer_currency>>
_Why: 27002:6.2 — current_

<<TEXT>>

## 6. Changes propagated to the live template and to the signer-recontracting plan

<<MUST item:A.6.2:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers (major policy change, employment-law reform, regulator action affecting employment InfoSec terms)

<<SHOULD item:A.6.2:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.6.2:rev_next_date>>
_Why: Planning_

<<TEXT>>
