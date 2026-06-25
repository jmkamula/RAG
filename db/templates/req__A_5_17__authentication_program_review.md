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
table_shape: true
---

# Periodic Authentication-Information Program Review

> The credential program creates value only if credentials actually rotate, MFA actually enrols, vault discipline actually holds and compromise responses actually fire. The review captures the planned-interval check: rotation-compliance audit, MFA enrolment coverage, vault-discipline audit (secrets outside the vault), compromise-response sample, and resulting program adjustments. Cadence tightened to 180 days — credential hygiene churns continuously

<!-- TABLE-COLUMNS leaf:req:A.5.17:authentication_program_review -->
<!-- column: item:A.5.17:rev_date -->
<!-- column: item:A.5.17:rev_reviewer -->
<!-- column: item:A.5.17:rev_rotation_compliance -->
<!-- column: item:A.5.17:rev_mfa_coverage -->
<!-- column: item:A.5.17:rev_vault_discipline -->
<!-- column: item:A.5.17:rev_compromise_sample -->
<!-- column: item:A.5.17:rev_actions -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.17:authentication_program_review -->
| Rev Date | Rev Reviewer | Rev Rotation Compliance | Rev Mfa Coverage | Rev Vault Discipline | Rev Compromise Sample | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.17:authentication_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.17:rev_date>>
_Why: 27002:5.17 — periodic_

> _Standard text:_ Review date within the planned 180-day interval

### Rev Reviewer

<<MUST item:A.5.17:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (IT identity-lead + InfoSec lead jointly; vault custodian where vault discipline is in scope)

### Rev Rotation Compliance

<<MUST item:A.5.17:rev_rotation_compliance>>
_Why: 27002:5.17 — rotation enforcement_

> _Standard text:_ Rotation-compliance audit (sample of credentials past their rotation cadence; root cause per stale credential)

### Rev Mfa Coverage

<<MUST item:A.5.17:rev_mfa_coverage>>
_Why: 27002:5.17 — MFA mandate verification_

> _Standard text:_ MFA enrolment coverage audit (% of in-scope identities with MFA enrolled; gap analysis per uncovered identity type)

### Rev Vault Discipline

<<MUST item:A.5.17:rev_vault_discipline>>
_Why: 27002:5.17 — storage discipline_

> _Standard text:_ Vault-discipline audit (sample of production systems re-checked: are credentials in the vault, or in config files / spreadsheets / chat history?)

### Rev Compromise Sample

<<MUST item:A.5.17:rev_compromise_sample>>
_Why: 27002:5.17 — compromise response_

> _Standard text:_ Compromise-response sample (recent compromise events re-examined: was rotation forced? was scope expansion checked?)

### Rev Actions

<<MUST item:A.5.17:rev_actions>>
_Why: 27002:5.17 — program adjustments_

> _Standard text:_ Action items captured (e.g. expand MFA to remaining identity types, automate rotation for service tokens, retire phishable factors)

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Phishing Progression

<<SHOULD item:A.5.17:rev_phishing_progression>>
_Why: Modern direction tracking_

> _Standard text:_ Phishing-resistance progression review (delta in phishing-resistant credential ratio since last review; roadmap to higher coverage)

### Rev Next Date

<<SHOULD item:A.5.17:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated (within 180d of this review)
