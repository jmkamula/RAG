---
leaf_id: req:A.5.25:triage_decision_record
control_ref: A.5.25
standard_id: ISO27001:2022
evidence_type: revocation_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
table_shape: true
---

# Per-Event Triage Decision Records

<<DOC_CONTROL>>

> Every triaged event must close — as a false positive, as a near-miss filed for trend tracking, or by escalation to incident response (A.5.26). The decision record evidences the actual closure: which event, what was decided, the rationale, the authority, and the handoff link where applicable

<!-- TABLE-COLUMNS leaf:req:A.5.25:triage_decision_record -->
<!-- column: item:A.5.25:dec_event_ref -->
<!-- column: item:A.5.25:dec_outcome -->
<!-- column: item:A.5.25:dec_rationale -->
<!-- column: item:A.5.25:dec_authority -->
<!-- column: item:A.5.25:dec_handoff -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you clearly document how each security event was handled, including what decision was made, why, and who approved it. It provides a reliable record for audits and ongoing security improvement.

## When to use it

Use this template every time you close out a triaged security event, whether it’s a false positive, a near-miss, or escalated to incident response. Update the record as needed whenever new events are reviewed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10-15 minutes per required element for each event, so completing a single entry from scratch typically takes around an hour.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.25:triage_decision_record -->
| Dec Event Ref | Dec Outcome | Dec Rationale | Dec Authority | Dec Handoff |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.25:triage_decision_record -->

## Column guidance — what to fill in

### Dec Event Ref

<<MUST item:A.5.25:dec_event_ref>>
_Why: 27002:5.25 — documented decision_

> _Standard text:_ Event identifier per record (links back to the triage log row)

<<GUIDANCE>>

### Dec Outcome

<<MUST item:A.5.25:dec_outcome>>
_Why: 27002:5.25 — decision_

> _Standard text:_ Decision outcome captured (false positive / filed near-miss / escalated to incident)

<<GUIDANCE>>

### Dec Rationale

<<MUST item:A.5.25:dec_rationale>>
_Why: Audit defensibility_

> _Standard text:_ Rationale stated (criteria-based reasoning, not just a binary outcome)

<<GUIDANCE>>

### Dec Authority

<<MUST item:A.5.25:dec_authority>>
_Why: 27002:5.25 — decision authority_

> _Standard text:_ Triage decision authority per record (named role or person)

<<GUIDANCE>>

### Dec Handoff

<<MUST item:A.5.25:dec_handoff>>
_Why: 27002:5.25 — incidents_

> _Standard text:_ Where escalated: handoff reference into A.5.26 incident register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Dec Timeliness

<<SHOULD item:A.5.25:dec_timeliness>>
_Why: Operational discipline_

> _Standard text:_ Timeliness target met (decision within stated triage timeline)

<<GUIDANCE>>

### Dec Retro Flag

<<SHOULD item:A.5.25:dec_retro_flag>>
_Why: Closes loop with [[A.5.27]]_

> _Standard text:_ Retroactive-review flag where a closed event was later reopened (drives missed-event analysis in the program review)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
