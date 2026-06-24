---
leaf_id: req:A.5.32:intellectual_property_procedure
control_ref: A.5.32
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Intellectual Property Rights Protection Procedure

> A.5.32 requires appropriate procedures to protect IPR — both the organisation's own and third parties'. The procedure documents usage controls, third-party respect mechanisms, employee-creation rules and the linkage to acquisition. The licensed/IPR inventory, the acquired-works upstream and the annual audit are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope of IPRs covered (software licences, trademarks, copyrights, patents, trade secrets, AI model weights / training data where applicable)

<<MUST item:A.5.32:scope_iprs>>
_Why: 27002:5.32 — IPR scope_

<<TEXT>>

## 2. Usage controls preventing unlicensed software installation (allow-listing, MDM/EDR enforcement, procurement gate)

<<MUST item:A.5.32:usage_controls>>
_Why: 27002:5.32 — appropriate procedures_

<<TEXT>>

## 3. Third-party IPR respect (citation, attribution, royalty payment, open-source licence compliance)

<<MUST item:A.5.32:third_party_respect>>
_Why: 27002:5.32 — protect IPR_

<<TEXT>>

## 4. Employee-creations rule (work-product ownership, open-source contribution policy, prior-IP carve-out)

<<MUST item:A.5.32:employee_creations>>
_Why: 27002:5.32 — protect_

<<TEXT>>

## 5. Handling path for suspected IPR infringement (internal report, takedown, internal remediation, cease-and-desist response)

<<MUST item:A.5.32:incident_handling>>
_Why: 27002:5.32 — protect_

<<TEXT>>

## 6. Named owner of the procedure (typically legal/IT lead jointly)

<<MUST item:A.5.32:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Cross-link to A.6.3 awareness — staff training on IPR (especially open-source and AI-tool usage)

<<SHOULD item:A.5.32:training_link>>
_Why: Effectiveness_

<<TEXT>>

### 2. Bring-your-own-licence handling (personal licences brought into a business context, freelancer-supplied software)

<<SHOULD item:A.5.32:bring_your_own>>
_Why: Real-world coverage_

<<TEXT>>
