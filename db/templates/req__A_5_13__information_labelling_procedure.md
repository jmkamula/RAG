---
leaf_id: req:A.5.13:information_labelling_procedure
control_ref: A.5.13
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Information Labelling Procedure

> A.5.13 requires procedures for information labelling aligned with the classification scheme defined in A.5.12. The procedure documents per-level marking conventions, automated tooling rules, persistence requirements, training links, and legacy-asset handling. The coverage register, periodic program review and per-platform application record are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Visual marking conventions per classification level (headers, watermarks, banners, footers)

<<MUST item:A.5.13:visual_marks>>
_Why: 27002:5.13 — labelling_

<<TEXT>>

## 2. Digital metadata tags or sensitivity labels (e.g. Microsoft Purview / Google labels / equivalent) per level

<<MUST item:A.5.13:metadata_tags>>
_Why: 27002:5.13 — labelling_

<<TEXT>>

## 3. Physical media labelling rules (paper documents, removable storage, archive boxes; cross-link to A.7.10)

<<MUST item:A.5.13:physical_media>>
_Why: 27002:5.13 + cross-link to [[A.7.10]]_

<<TEXT>>

## 4. Label persistence on copying, export, transformation (PDF print, file format conversion, copy-paste into new container)

<<MUST item:A.5.13:label_persistence>>
_Why: 27002:5.13 — implemented_

<<TEXT>>

## 5. References training so personnel know how to apply labels (cross-link to A.5.12 classification training)

<<MUST item:A.5.13:training_ref>>
_Why: 27002:5.13 — implemented_

<<TEXT>>

## 6. Alignment with the A.5.12 classification scheme stated explicitly (level names match; level count matches; semantics match)

<<MUST item:A.5.13:scheme_alignment>>
_Why: 27002:5.13 + cross-link to [[A.5.12]]_

<<TEXT>>

## 7. PII / personal-data overlay rule where applicable (additional labelling beyond confidentiality level — e.g. 'Contains PII' footer for GDPR compliance)

<<MUST item:A.5.13:pii_overlay>>
_Why: 27002:5.13 + GDPR alignment_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Handling of legacy unlabelled assets (default-classify rule with retro-labelling timeline)

<<SHOULD item:A.5.13:legacy_handling>>
_Why: Pragmatic adoption_

<<TEXT>>

### 2. Automation / tooling references where labelling is auto-applied (DLP, sensitivity-label policies)

<<SHOULD item:A.5.13:automation>>
_Why: Scalability_

<<TEXT>>

### 3. Handling of inbound third-party documents that arrive unlabelled (default-classify and add internal label)

<<SHOULD item:A.5.13:external_handling>>
_Why: Real-world coverage_

<<TEXT>>
