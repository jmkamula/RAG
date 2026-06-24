---
leaf_id: req:A.5.12:information_classification_scheme
control_ref: A.5.12
standard_id: ISO27001:2022
evidence_type: classification_scheme
trigger_type: universal
template_version: 1
must_count: 6
should_count: 3
---

# Information Classification Scheme

> A.5.12 requires information to be classified per the organisation's security needs across confidentiality, integrity, availability, and interested-party requirements. The scheme defines levels and handling implications. Approval, communication and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Classification levels defined (e.g. Public / Internal / Confidential / Restricted)

<<MUST item:A.5.12:levels_defined>>
_Why: 27002:5.12 — classified_

<<TEXT>>

## 2. Each level addresses confidentiality, integrity, and availability dimensions

<<MUST item:A.5.12:cia_dimensions>>
_Why: 27002:5.12 — based on C/I/A_

<<TEXT>>

## 3. Definition and indicative examples per level

<<MUST item:A.5.12:level_definitions>>
_Why: 27002:5.12 — needs of the organisation_

<<TEXT>>

## 4. Handling implications per level (links to A.5.13 labelling, A.5.10 acceptable use, A.5.14 transfer)

<<MUST item:A.5.12:handling_per_level>>
_Why: 27002:5.12 — security needs_

<<TEXT>>

## 5. Decision authority for classifying information (owner-led by default)

<<MUST item:A.5.12:classification_authority>>
_Why: 27002:5.12 — classified_

<<TEXT>>

## 6. Default classification for unclassified information (typically 'Internal' as fail-safe)

<<MUST item:A.5.12:default_class>>
_Why: 27002:5.12 — pragmatic adoption_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Considerations for interested-party requirements (regulator-imposed classifications, contract-imposed)

<<SHOULD item:A.5.12:interested_parties>>
_Why: Completeness_

<<TEXT>>

### 2. Declassification or reclassification process

<<SHOULD item:A.5.12:declassification>>
_Why: Lifecycle_

<<TEXT>>

### 3. Aggregation rule (combined low-class data items that, in aggregate, warrant higher class)

<<SHOULD item:A.5.12:aggregation>>
_Why: Realistic threat model_

<<TEXT>>
