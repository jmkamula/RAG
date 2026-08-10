---
leaf_id: req:7.5:applicable_document_classes_scope
control_ref: 7.5
standard_id: ISO27001:2022
evidence_type: scope_note
trigger_type: universal
template_version: 1
must_count: 3
should_count: 1
---

# Applicable ISMS Document Classes Scope

<<DOC_CONTROL>>

> The upstream that bounds the register — which document classes are 'ISMS documented information' (ISO-required, org-determined-necessary) vs incidental

## What this template gives you

This template helps you clearly define which types of documents in your organization are considered part of your Information Security Management System, as required by ISO 27001, and which are not.

## When to use it

Use this whenever you need to clarify or update the scope of your ISMS documentation, as it always applies to your environment and should be refreshed whenever your document classes change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 30 to 45 minutes completing this from scratch, as it involves describing three required elements in clear, concise prose.

## 1. ISO 27001:2022-required document classes enumerated (scope statement, policy, SoA, risk register, audit programme, etc.)

<<MUST item:7.5:scope_iso_required>>
_Why: Clause 7.5 — required by this document_

<<GUIDANCE>>

<<TEXT>>

## 2. Organisation-determined classes enumerated (procedures, standards, work instructions)

<<MUST item:7.5:scope_org_determined>>
_Why: Clause 7.5 — necessary for the effectiveness_

<<GUIDANCE>>

<<TEXT>>

## 3. External-origin classes in scope (regulator guidance, supplier policies referenced, framework docs)

<<MUST item:7.5:scope_external>>
_Why: Clause 7.5.3 — external origin_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Exclusions stated explicitly (e.g. operational logs not classified as documented information)

<<SHOULD item:7.5:scope_exclusions>>
_Why: Defensible bounding_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
