---
leaf_id: req:Art.10:criminal_data_authorisation_procedure
control_ref: Art.10
standard_id: GDPR:2016/679
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Criminal Convictions Data Authorisation Procedure

> Art.10 permits processing of criminal convictions / offences data ONLY under control of official authority OR when Member State law specifically authorises it with appropriate safeguards. The procedure is the canonical artefact. Sibling leaves: processing register, applicable legal-basis scope, program review

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Legal-basis verification step — official-authority OR Member State authorisation cited per activity

<<MUST item:Art.10:proc_legal_basis_check>>
_Why: Art.10_

<<TEXT>>

## 2. Member State law identified per applicable jurisdiction (where MS authorisation is the route)

<<MUST item:Art.10:proc_member_state_law>>
_Why: Art.10_

<<TEXT>>

## 3. Safeguards required by Art.10 (specific to the Member State authorisation — typically retention limits + access restrictions)

<<MUST item:Art.10:proc_safeguards>>
_Why: Art.10 — appropriate safeguards_

<<TEXT>>

## 4. Restriction — comprehensive register of criminal convictions only under official authority (e.g. police, public prosecution); other controllers process only specific cases

<<MUST item:Art.10:proc_comprehensive_register>>
_Why: Art.10 — comprehensive register limit_

<<TEXT>>

## 5. Approval authority for any criminal-data activity (DPO + executive sponsor + legal counsel)

<<MUST item:Art.10:proc_approval>>
_Why: Risk-proportionate authority_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Link to Art.35 DPIA — Art.10 processing nearly always triggers DPIA

<<SHOULD item:Art.10:proc_dpia_link>>
_Why: Art.35.3.b_

<<TEXT>>
