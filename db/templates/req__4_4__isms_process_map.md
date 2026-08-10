---
leaf_id: req:4.4:isms_process_map
control_ref: 4.4
standard_id: ISO27001:2022
evidence_type: process_map
trigger_type: universal
template_version: 1
must_count: 4
should_count: 1
---

# ISMS Process Interaction Map

<<DOC_CONTROL>>

> The visual or tabular representation of how ISMS processes connect — what's an input, what's an output, who hands off to whom. Distinct from the prose manual: the map is what gets shown to auditors and onboarding staff

## What this template gives you

This template helps you clearly show how your information security processes connect, including who is responsible for each step and how information moves between teams. It’s a useful visual or table for onboarding and audit purposes.

## When to use it

Use this whenever you need to demonstrate how your ISMS processes interact, especially for ISO 27001 compliance. Update it whenever your processes change or when preparing for audits or new staff onboarding.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes creating this from scratch, as each required element takes roughly 10-15 minutes to document.

## 1. All ISMS processes from the manual represented on the map

<<MUST item:4.4:map_processes>>
_Why: Cross-leaf coherence_

<<GUIDANCE>>

<<TEXT>>

## 2. Inputs and outputs labelled per process node

<<MUST item:4.4:map_inputs_outputs>>
_Why: Clause 4.4 — their interactions_

<<GUIDANCE>>

<<TEXT>>

## 3. Sequence / dependency arrows between processes

<<MUST item:4.4:map_sequence>>
_Why: Clause 4.4 — interactions_

<<GUIDANCE>>

<<TEXT>>

## 4. Ownership overlay (which role owns which process node)

<<MUST item:4.4:map_ownership>>
_Why: Accountability_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External integrations shown (supplier handoffs, auditor touchpoints)

<<SHOULD item:4.4:map_external>>
_Why: Completeness_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
