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

<<DOC_CONTROL>>

> §7.4.2 limits processing operations to what's adequate + relevant + necessary. Covers disclosure limits, retention-during-processing, and access controls (who can access which PII).

## What this template gives you

This template helps you document how your organization limits the processing of personal data to only what is necessary, including who can access information, how long it's kept, and when it can be disclosed.

## When to use it

Use this procedure whenever your data processing activities need to be reviewed for compliance with privacy requirements, especially if your operations match certain risk or profile triggers. Update the document as needed when your processes or access controls change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 60 to 75 minutes completing this template from scratch, as you'll need to address five required elements and provide clear details for each.

## 1. Disclosure limitation — who PII is disclosed to (internal + external) constrained per purpose

<<MUST item:A.7.4.2:proc_disclosure_limit>>
_Why: §7.4.2 — disclosure_

<<GUIDANCE>>

<<TEXT>>

## 2. Access limitation — role-based access controls scoped by purpose

<<MUST item:A.7.4.2:proc_access_limit>>
_Why: §7.4.2 — who is able to access_

<<GUIDANCE>>

<<TEXT>>

## 3. Storage-during-processing limitation — no unnecessary retention in intermediate systems

<<MUST item:A.7.4.2:proc_storage_limit>>
_Why: §7.4.2 — period of PII storage_

<<GUIDANCE>>

<<TEXT>>

## 4. Default-minimum — limited to minimum necessary by default; expansions require documented rationale

<<MUST item:A.7.4.2:proc_default_minimum>>
_Why: §7.4.2 — limited by default_

<<GUIDANCE>>

<<TEXT>>

## 5. Link to information-security + privacy policies (§6.2 / A.5.1) as the governance vehicle

<<MUST item:A.7.4.2:proc_policy_link>>
_Why: §7.4.2 implementation — managed through policies_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (DPO + Engineering)

<<SHOULD item:A.7.4.2:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
