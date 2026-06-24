---
leaf_id: req:Art.6:lawful_basis_register
control_ref: Art.6
standard_id: GDPR:2016/679
evidence_type: lawful_basis_register
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 2
---

# Lawful Basis Register (Art.6)

> Art.6 obliges the controller to be able to point to a specific lawful basis per processing activity. The register (or RoPA extension) listing each activity with the chosen basis, justification, and supporting records is the canonical Art.6 artefact. Sibling direct-evidence leaves: determination procedure, applicable activities scope, program review

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Processing activities enumerated (links to Art.30 RoPA)

<<MUST item:Art.6:activities_enumerated>>
_Why: Art.6.1 — basis applies per activity_

<<TEXT>>

## 2. Chosen lawful basis named per activity (one of Art.6.1.a-f)

<<MUST item:Art.6:basis_per_activity>>
_Why: Art.6.1 — at least one of (a)-(f) applies_

<<TEXT>>

## 3. Justification recorded for the chosen basis per activity

<<MUST item:Art.6:justification>>
_Why: Art.5.2 accountability_

<<TEXT>>

## 4. For consent-based activities, link to Art.7 consent capture record

<<MUST item:Art.6:consent_link>>
_Why: Art.7 — conditions for consent_

<<TEXT>>

## 5. For legitimate-interests activities, link to LIA (necessity + balance test)

<<MUST item:Art.6:lia_link>>
_Why: Art.6.1.f — overriding interests test_

<<TEXT>>

## 6. Named owner of the register (typically DPO or Privacy Lead)

<<MUST item:Art.6:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Register reviewed within freshness window when activities or bases change

<<SHOULD item:Art.6:reviewed>>
_Why: Accountability — kept current_

<<TEXT>>

### 2. Log of lawful basis changes per activity (drives Art.13 notice amendments)

<<SHOULD item:Art.6:basis_change_log>>
_Why: Art.5.2 + Art.13 alignment_

<<TEXT>>
