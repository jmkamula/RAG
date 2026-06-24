---
leaf_id: req:Art.16:applicable_systems_scope
control_ref: Art.16
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Systems Scope for Rectification

> The upstream — every system holding rectifiable personal data that needs to be touched on a rectification request

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Systems enumerated (PII inventory cross-reference — A.5.34:pii_inventory + Art.30 RoPA)

<<MUST item:Art.16:scope_systems>>
_Why: Coverage proof_

<<TEXT>>

## 2. Replica + backup handling rules — when rectification reaches them, when supplementary statement substitutes

<<MUST item:Art.16:scope_replicas>>
_Why: Art.16 — all instances_

<<TEXT>>

## 3. Third-party processor handling — where requests propagate via Art.28 DPA flow

<<MUST item:Art.16:scope_third_parties>>
_Why: Cross-article coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new system holding PII, new processor onboarded)

<<SHOULD item:Art.16:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
