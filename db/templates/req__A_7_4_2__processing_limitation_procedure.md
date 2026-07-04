---
leaf_id: req:A.7.4.2:processing_limitation_procedure
control_ref: A.7.4.2
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# Processing Limitation Procedure

> §7.4.2 limits processing operations to what's adequate + relevant + necessary. Covers disclosure limits, retention-during-processing, and access controls (who can access which PII).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Disclosure limitation — who PII is disclosed to (internal + external) constrained per purpose

<<MUST item:A.7.4.2:proc_disclosure_limit>>
_Why: §7.4.2 — disclosure_

<<TEXT>>

## 2. Access limitation — role-based access controls scoped by purpose

<<MUST item:A.7.4.2:proc_access_limit>>
_Why: §7.4.2 — who is able to access_

<<TEXT>>

## 3. Storage-during-processing limitation — no unnecessary retention in intermediate systems

<<MUST item:A.7.4.2:proc_storage_limit>>
_Why: §7.4.2 — period of PII storage_

<<TEXT>>

## 4. Default-minimum — limited to minimum necessary by default; expansions require documented rationale

<<MUST item:A.7.4.2:proc_default_minimum>>
_Why: §7.4.2 — limited by default_

<<TEXT>>

## 5. Link to information-security + privacy policies (§6.2 / A.5.1) as the governance vehicle

<<MUST item:A.7.4.2:proc_policy_link>>
_Why: §7.4.2 implementation — managed through policies_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO + Engineering)

<<SHOULD item:A.7.4.2:proc_owner>>
_Why: Accountability_

<<TEXT>>
