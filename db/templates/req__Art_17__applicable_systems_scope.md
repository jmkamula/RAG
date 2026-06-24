---
leaf_id: req:Art.17:applicable_systems_scope
control_ref: Art.17
standard_id: GDPR:2016/679
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# Applicable Systems Scope for Erasure

> The upstream — every system holding erasable personal data including backups + replicas + third-party processors (per Art.17 'all instances' + Art.28 flow-through)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Systems enumerated (cross-ref to A.5.34:pii_inventory + A.8.10:scope_systems + Art.30 RoPA)

<<MUST item:Art.17:scope_systems>>
_Why: Coverage_

<<TEXT>>

## 2. Backup + replica erasure rules (synchronous-on-restore vs delete-cycle vs immutable-record handling)

<<MUST item:Art.17:scope_backup_rules>>
_Why: Art.17.1 — all instances_

<<TEXT>>

## 3. Third-party processor handling via Art.28 DPA flow-through

<<MUST item:Art.17:scope_third_parties>>
_Why: Cross-article coherence_

<<TEXT>>

## 4. Public-data overlay — when org has made data public, Art.17.2 reasonable-measures scope applies

<<MUST item:Art.17:scope_public_data>>
_Why: Art.17.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new PII store, new processor, public-data disclosure)

<<SHOULD item:Art.17:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
