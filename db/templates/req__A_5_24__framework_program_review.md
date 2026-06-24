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
---

# Periodic Incident Management Framework Review

> The framework creates value only if it actually runs when incidents hit — exercise results that surface gaps, team coverage gaps, framework-vs-actual-response divergence, GDPR-72h-feasibility check all signal the framework is or isn't ready. The review captures the planned-interval check: exercise-result analysis, team-readiness audit, real-incident-vs-framework divergence analysis, GDPR-readiness verification, and resulting framework adjustments. Cadence tightened to 180 days — IR readiness erodes between exercises

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned 180-day interval

<<MUST item:A.5.24:rev_date>>
_Why: 27002:5.24 — periodic_

<<TEXT>>

## 2. Reviewer identity (CISO + IR lead + Data Protection Officer where personal data scope; Legal where regulator notification scope)

<<MUST item:A.5.24:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Exercise-result analysis (last N exercises reviewed; gaps surfaced; remediation per gap; ratio-of-exercises-completed vs planned)

<<MUST item:A.5.24:rev_exercise_results>>
_Why: 27002:5.24 — preparation effectiveness_

<<TEXT>>

## 4. Team-readiness audit (training currency across responders; coverage gaps where a tier is under-staffed; backup-named compliance)

<<MUST item:A.5.24:rev_team_readiness>>
_Why: 27002:5.24 — preparation_

<<TEXT>>

## 5. Real-incident vs framework divergence (where actual responses deviated from framework — was the framework too prescriptive, missing a path, or just unused?)

<<MUST item:A.5.24:rev_real_divergence>>
_Why: Framework effectiveness_

<<TEXT>>

## 6. GDPR 72-hour feasibility check (when did the last personal-data incident notify? what was the gap to 72h? is the path actually under 72h?)

<<MUST item:A.5.24:rev_gdpr_72h_feasibility>>
_Why: GDPR Art.33 — 72hr feasibility verification_

<<TEXT>>

## 7. Action items captured (e.g. add new role, refresh communications playbook, expand exercise scope, tighten 72h path)

<<MUST item:A.5.24:rev_actions>>
_Why: 27002:5.24 — framework adjustments_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Peer/industry practice scan (notable incidents in the sector; how peers responded; lessons applicable)

<<SHOULD item:A.5.24:rev_peer_practice>>
_Why: Audit defensibility_

<<TEXT>>

### 2. Next planned review date stated (within 180d of this review)

<<SHOULD item:A.5.24:rev_next_date>>
_Why: Planning_

<<TEXT>>
