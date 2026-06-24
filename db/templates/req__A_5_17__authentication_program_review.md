---
leaf_id: req:A.5.17:authentication_program_review
control_ref: A.5.17
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
---

# Periodic Authentication-Information Program Review

> The credential program creates value only if credentials actually rotate, MFA actually enrols, vault discipline actually holds and compromise responses actually fire. The review captures the planned-interval check: rotation-compliance audit, MFA enrolment coverage, vault-discipline audit (secrets outside the vault), compromise-response sample, and resulting program adjustments. Cadence tightened to 180 days — credential hygiene churns continuously

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned 180-day interval

<<MUST item:A.5.17:rev_date>>
_Why: 27002:5.17 — periodic_

<<TEXT>>

## 2. Reviewer identity (IT identity-lead + InfoSec lead jointly; vault custodian where vault discipline is in scope)

<<MUST item:A.5.17:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Rotation-compliance audit (sample of credentials past their rotation cadence; root cause per stale credential)

<<MUST item:A.5.17:rev_rotation_compliance>>
_Why: 27002:5.17 — rotation enforcement_

<<TEXT>>

## 4. MFA enrolment coverage audit (% of in-scope identities with MFA enrolled; gap analysis per uncovered identity type)

<<MUST item:A.5.17:rev_mfa_coverage>>
_Why: 27002:5.17 — MFA mandate verification_

<<TEXT>>

## 5. Vault-discipline audit (sample of production systems re-checked: are credentials in the vault, or in config files / spreadsheets / chat history?)

<<MUST item:A.5.17:rev_vault_discipline>>
_Why: 27002:5.17 — storage discipline_

<<TEXT>>

## 6. Compromise-response sample (recent compromise events re-examined: was rotation forced? was scope expansion checked?)

<<MUST item:A.5.17:rev_compromise_sample>>
_Why: 27002:5.17 — compromise response_

<<TEXT>>

## 7. Action items captured (e.g. expand MFA to remaining identity types, automate rotation for service tokens, retire phishable factors)

<<MUST item:A.5.17:rev_actions>>
_Why: 27002:5.17 — program adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Phishing-resistance progression review (delta in phishing-resistant credential ratio since last review; roadmap to higher coverage)

<<SHOULD item:A.5.17:rev_phishing_progression>>
_Why: Modern direction tracking_

<<TEXT>>

### 2. Next planned review date stated (within 180d of this review)

<<SHOULD item:A.5.17:rev_next_date>>
_Why: Planning_

<<TEXT>>
