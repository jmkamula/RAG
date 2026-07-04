---
leaf_id: req:A.7.4.6:applicable_scope
control_ref: A.7.4.6
standard_id: ISO27701:2019
evidence_type: scope_note
trigger_type: profile_fact
template_version: 1
must_count: 3
should_count: 1
---

# Applicable Temp-File Contexts Scope

> The upstream — which infrastructure surfaces create PII-touching temp files (application tier + database + cache + log-processing).

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Infrastructure surfaces enumerated (app servers + DB + cache + queue + log processors + backup staging)

<<MUST item:A.7.4.6:scope_infrastructure>>
_Why: Coverage_

<<TEXT>>

## 2. File types per surface (application temp / journal / roll-back / cache spillover)

<<MUST item:A.7.4.6:scope_file_types>>
_Why: Coverage_

<<TEXT>>

## 3. Undeletable-file exceptions (circumstances where deletion isn't possible per §7.4.6) with rationale + compensating controls

<<MUST item:A.7.4.6:scope_undeletable_exceptions>>
_Why: §7.4.6 — circumstances in which they cannot be deleted_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new infrastructure component)

<<SHOULD item:A.7.4.6:scope_change_drivers>>
_Why: Currency_

<<TEXT>>
