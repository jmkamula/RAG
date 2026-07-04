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

> §7.4.4 requires documented data-minimization objectives + mechanisms (de-identification / pseudonymisation / aggregation). Ties to ISO/IEC 20889 de-identification techniques.

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Minimization objectives stated per processing activity (target level of identifiability required)

<<MUST item:A.7.4.4:proc_objectives_stated>>
_Why: §7.4.4 — define and document objectives_

<<TEXT>>

## 2. Mechanism map — de-identification / pseudonymisation / aggregation / generalisation / suppression per activity

<<MUST item:A.7.4.4:proc_mechanism_map>>
_Why: §7.4.4 — mechanisms used_

<<TEXT>>

## 3. De-identification technique selection referencing ISO/IEC 20889 taxonomy

<<MUST item:A.7.4.4:proc_deidentification_technique>>
_Why: §7.4.4 NOTE 1 — ISO/IEC 20889_

<<TEXT>>

## 4. Technical configurations documented (how the minimisation is implemented in code / infrastructure)

<<MUST item:A.7.4.4:proc_technical_config>>
_Why: §7.4.4 — technical system configurations_

<<TEXT>>

## 5. Where processing requires non-minimised PII (identified purpose demands it), justification documented

<<MUST item:A.7.4.4:proc_full_pii_justification>>
_Why: §7.4.4 — describe such processing_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Named owner (Privacy Engineering + Data Science)

<<SHOULD item:A.7.4.4:proc_owner>>
_Why: Accountability_

<<TEXT>>
