---
leaf_id: req:A.5.24:framework_program_review
control_ref: A.5.24
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 180
template_version: 1
must_count: 7
should_count: 2
table_shape: true
---

# Periodic Incident Management Framework Review

<<DOC_CONTROL>>

> The framework creates value only if it actually runs when incidents hit — exercise results that surface gaps, team coverage gaps, framework-vs-actual-response divergence, GDPR-72h-feasibility check all signal the framework is or isn't ready. The review captures the planned-interval check: exercise-result analysis, team-readiness audit, real-incident-vs-framework divergence analysis, GDPR-readiness verification, and resulting framework adjustments. Cadence tightened to 180 days — IR readiness erodes between exercises

<!-- TABLE-COLUMNS leaf:req:A.5.24:framework_program_review -->
<!-- column: item:A.5.24:rev_date -->
<!-- column: item:A.5.24:rev_reviewer -->
<!-- column: item:A.5.24:rev_exercise_results -->
<!-- column: item:A.5.24:rev_team_readiness -->
<!-- column: item:A.5.24:rev_real_divergence -->
<!-- column: item:A.5.24:rev_gdpr_72h_feasibility -->
<!-- column: item:A.5.24:rev_actions -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you systematically review your incident management framework, ensuring your team is prepared, gaps are identified, and compliance with GDPR and ISO 27001 is maintained. It provides a clear record of your review process and any improvements made.

## When to use it

Use this template every 180 days, or about twice a year, to document your regular incident management framework review. It's designed for environments where ongoing readiness and compliance are essential.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 70 to 105 minutes completing this from scratch, as each of the seven required elements takes roughly 10-15 minutes to fill in. Additional time may be needed if you add recommended details.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.24:framework_program_review -->
| Rev Date | Rev Reviewer | Rev Exercise Results | Rev Team Readiness | Rev Real Divergence | Rev Gdpr 72H Feasibility | Rev Actions |
|---|---|---|---|---|---|---|
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
|          |          |          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.24:framework_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.24:rev_date>>
_Why: 27002:5.24 — periodic_

> _Standard text:_ Review date within the planned 180-day interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.24:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (CISO + IR lead + Data Protection Officer where personal data scope; Legal where regulator notification scope)

<<GUIDANCE>>

### Rev Exercise Results

<<MUST item:A.5.24:rev_exercise_results>>
_Why: 27002:5.24 — preparation effectiveness_

> _Standard text:_ Exercise-result analysis (last N exercises reviewed; gaps surfaced; remediation per gap; ratio-of-exercises-completed vs planned)

<<GUIDANCE>>

### Rev Team Readiness

<<MUST item:A.5.24:rev_team_readiness>>
_Why: 27002:5.24 — preparation_

> _Standard text:_ Team-readiness audit (training currency across responders; coverage gaps where a tier is under-staffed; backup-named compliance)

<<GUIDANCE>>

### Rev Real Divergence

<<MUST item:A.5.24:rev_real_divergence>>
_Why: Framework effectiveness_

> _Standard text:_ Real-incident vs framework divergence (where actual responses deviated from framework — was the framework too prescriptive, missing a path, or just unused?)

<<GUIDANCE>>

### Rev Gdpr 72H Feasibility

<<MUST item:A.5.24:rev_gdpr_72h_feasibility>>
_Why: GDPR Art.33 — 72hr feasibility verification_

> _Standard text:_ GDPR 72-hour feasibility check (when did the last personal-data incident notify? what was the gap to 72h? is the path actually under 72h?)

<<GUIDANCE>>

### Rev Actions

<<MUST item:A.5.24:rev_actions>>
_Why: 27002:5.24 — framework adjustments_

> _Standard text:_ Action items captured (e.g. add new role, refresh communications playbook, expand exercise scope, tighten 72h path)

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Peer Practice

<<SHOULD item:A.5.24:rev_peer_practice>>
_Why: Audit defensibility_

> _Standard text:_ Peer/industry practice scan (notable incidents in the sector; how peers responded; lessons applicable)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.24:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated (within 180d of this review)

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
