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

> The visual or tabular representation of how ISMS processes connect — what's an input, what's an output, who hands off to whom. Distinct from the prose manual: the map is what gets shown to auditors and onboarding staff

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. All ISMS processes from the manual represented on the map

<<MUST item:4.4:map_processes>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 2. Inputs and outputs labelled per process node

<<MUST item:4.4:map_inputs_outputs>>
_Why: Clause 4.4 — their interactions_

<<TEXT>>

## 3. Sequence / dependency arrows between processes

<<MUST item:4.4:map_sequence>>
_Why: Clause 4.4 — interactions_

<<TEXT>>

## 4. Ownership overlay (which role owns which process node)

<<MUST item:4.4:map_ownership>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. External integrations shown (supplier handoffs, auditor touchpoints)

<<SHOULD item:4.4:map_external>>
_Why: Completeness_

<<TEXT>>
