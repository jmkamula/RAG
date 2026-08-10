---
leaf_id: req:A.7.4.4:minimization_procedure
control_ref: A.7.4.4
standard_id: ISO27701:2019
evidence_type: procedure
trigger_type: profile_fact
template_version: 1
must_count: 5
should_count: 1
---

# PII Minimization Procedure

<<DOC_CONTROL>>

> §7.4.4 requires documented data-minimization objectives + mechanisms (de-identification / pseudonymisation / aggregation). Ties to ISO/IEC 20889 de-identification techniques.

## What this template gives you

This template helps you document your approach to minimizing the use of personal data, including how you de-identify, pseudonymize, or aggregate information in line with privacy standards.

## When to use it

Use this procedure whenever your organization handles personal data and needs to demonstrate compliance with privacy requirements, especially when your activities match specific triggers. Update the document as needed when your processes or data handling change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 50 to 75 minutes completing this template from scratch, as each required section takes around 10 to 15 minutes to fill in thoughtfully.

## 1. Minimization objectives stated per processing activity (target level of identifiability required)

<<MUST item:A.7.4.4:proc_objectives_stated>>
_Why: §7.4.4 — define and document objectives_

<<GUIDANCE>>

<<TEXT>>

## 2. Mechanism map — de-identification / pseudonymisation / aggregation / generalisation / suppression per activity

<<MUST item:A.7.4.4:proc_mechanism_map>>
_Why: §7.4.4 — mechanisms used_

<<GUIDANCE>>

<<TEXT>>

## 3. De-identification technique selection referencing ISO/IEC 20889 taxonomy

<<MUST item:A.7.4.4:proc_deidentification_technique>>
_Why: §7.4.4 NOTE 1 — ISO/IEC 20889_

<<GUIDANCE>>

<<TEXT>>

## 4. Technical configurations documented (how the minimisation is implemented in code / infrastructure)

<<MUST item:A.7.4.4:proc_technical_config>>
_Why: §7.4.4 — technical system configurations_

<<GUIDANCE>>

<<TEXT>>

## 5. Where processing requires non-minimised PII (identified purpose demands it), justification documented

<<MUST item:A.7.4.4:proc_full_pii_justification>>
_Why: §7.4.4 — describe such processing_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Privacy Engineering + Data Science)

<<SHOULD item:A.7.4.4:proc_owner>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
