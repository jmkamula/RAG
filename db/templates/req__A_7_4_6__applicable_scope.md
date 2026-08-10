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

<<DOC_CONTROL>>

> The upstream — which infrastructure surfaces create PII-touching temp files (application tier + database + cache + log-processing).

## What this template gives you

This template helps you clearly identify which parts of your infrastructure create temporary files that may contain personal data, making it easier to manage privacy risks and meet compliance requirements.

## When to use it

Use this document whenever your systems or processes change in a way that could affect where temporary files with personal information are created, and update it as needed to stay current.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as you'll need to describe three required areas and optionally add further details.

## 1. Infrastructure surfaces enumerated (app servers + DB + cache + queue + log processors + backup staging)

<<MUST item:A.7.4.6:scope_infrastructure>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 2. File types per surface (application temp / journal / roll-back / cache spillover)

<<MUST item:A.7.4.6:scope_file_types>>
_Why: Coverage_

<<GUIDANCE>>

<<TEXT>>

## 3. Undeletable-file exceptions (circumstances where deletion isn't possible per §7.4.6) with rationale + compensating controls

<<MUST item:A.7.4.6:scope_undeletable_exceptions>>
_Why: §7.4.6 — circumstances in which they cannot be deleted_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Trigger list (new infrastructure component)

<<SHOULD item:A.7.4.6:scope_change_drivers>>
_Why: Currency_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
