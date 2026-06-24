---
leaf_id: req:10.1:improvement_action_register
control_ref: 10.1
standard_id: ISO27001:2022
evidence_type: register
trigger_type: universal
template_version: 2
must_count: 7
should_count: 1
freshness_days: 365
---

# Improvement Action Register

## What this template gives you

The **live ledger** where every improvement opportunity — audit
finding, monitoring gap, lessons-learned outcome, party feedback,
management-review decision — gets a row, an owner, and a target
date. Auditors trace findings IN (from 9.2/9.3) → register → closure
with effectiveness check. A clean register is the operating heartbeat
of a continually-improving ISMS.

## When to use it

Standing artefact required by **ISO/IEC 27001:2022 Clause 10.1**.
This is a **register** (spreadsheet, ticketing-system view, or
table) not a one-off document — it's referenced constantly.

## Before you start

- [ ] **5.3 Roles** clear (every action needs an owner with authority)
- [ ] **9.2 Audit Programme** + **9.3 Management Review** in place
      (they're the biggest inflow of register rows)
- [ ] **A.5.27 Lessons-learned** process running (post-incident
      learnings feed here)

## Cross-references

- **10.2 Nonconformity Register** — sister artefact for the
  *negative* findings; some orgs merge 10.1+10.2, others keep
  separate. Either is fine — be explicit about which approach
- **9.2 Audit findings** — primary inflow
- **9.3 Management Review** — decisions become rows here
- **A.5.27 Lessons learned** — post-incident improvements

## Estimated effort

**1-2 hours** to design the register structure for v1; **ongoing
operational cost** of updating per finding.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Assign a unique action identifier per row

<<MUST item:10.1:reg_action_id>>
_Traceability — every row needs an identifier the org references
in audit reports, management reviews, change records._

Use a stable prefix + numeric sequence. Avoid recycling IDs after
closure.

**✓ Good**: "Action ID format: AC-NNN (e.g. AC-001, AC-042,
AC-117). Sequence is org-wide and never recycled. Closed rows
retain their ID in the historical view of the register."

<<TEXT>>

## 2. Record the trigger type per row

<<MUST item:10.1:reg_trigger_type>>
_Clause 10.1 — improvement comes from multiple sources; the
register makes the inflow visible._

Common trigger types: **audit_finding** (from 9.2), **measurement_gap**
(from 9.1), **mgmt_review_decision** (from 9.3), **lessons_learned**
(from A.5.27), **party_feedback** (customer / regulator), **risk_treatment**
(from 6.1.3), **opportunity** (proactive — no triggering finding).

**✓ Good**: Discrete column with values from the list above.
Auditor can pivot the register by trigger to see flow rate from
each source.

<<TEXT>>

## 3. Record the improvement dimension per row

<<MUST item:10.1:reg_dimension>>
_Clause 10.1 — suitability, adequacy, or effectiveness._

ISO 27001 distinguishes three: **suitability** (is the control
right for the situation?), **adequacy** (is it complete?),
**effectiveness** (does it actually work?). Categorising helps the
review process — different remedies apply.

**✓ Good**: Discrete column with values {suitability, adequacy,
effectiveness}. Example rows: "Replace single-factor login with
MFA" → suitability; "Add break-glass procedure for emergency
access" → adequacy; "Tighten access-review automation cadence to
weekly" → effectiveness.

<<TEXT>>

## 4. Record per-row owner

<<MUST item:10.1:reg_owner>>
_Accountability — each row has a single named owner with authority._

The owner is responsible for delivering the action — not for the
control's normal operation, but for the *change* the action requires.

**✓ Good**: "Owner column: named individual (not 'IT' or 'the
security team'). Role-holder accountable for delivering by target
date. Re-assignment must be explicit (recorded in row history)."

<<TEXT>>

## 5. Record per-row target completion date

<<MUST item:10.1:reg_target_date>>
_Time-bounded — improvements without deadlines drift indefinitely._

Each row gets a target date. Slippage is OK — but it must be
visible (date moves with reason captured), not hidden.

**✓ Good**: "Target date column: initial target + history of slips.
Format: '2026-09-30 (slipped from 2026-06-30: vendor dependency)'.
Slip > 60 days requires re-approval at next ISMS Steering Committee."

<<TEXT>>

## 6. Record per-row status

<<MUST item:10.1:reg_status>>
_Lifecycle — every row moves through a finite set of states._

Common: **proposed** (raised, not yet approved) → **approved**
(authorised + funded) → **in_progress** (work happening) → **closed**
(implemented + effectiveness verified) → **superseded** (replaced by a
later row) / **rejected** (formal decision not to act).

**✓ Good**: Discrete column with values above. Each transition
records who + when in the row history.

<<TEXT>>

## 7. Record effectiveness assessment on closure

<<MUST item:10.1:reg_effectiveness>>
_Clause 10.1 — confirm the corrective action achieved its intended
effect. This MUST is the one auditors most often find weak._

When a row moves to "closed", record **did it work?** — measurable
before/after, sample evidence, signoff. Without this, "closed" rows
are theatre.

**✓ Good**: "Effectiveness assessment captured at closure: (a)
intended effect re-stated, (b) measurable outcome (metric delta /
re-audit result / control test outcome), (c) verifier identity
(NOT the same person as the owner), (d) closure decision recorded.
Example: AC-117 SBOM tooling — intended effect: cover 100% of
production components in SBOM; outcome at closure: 100%
(0/127 → 127/127) verified by re-running A.5.21 supply-chain
review; verifier: SecOps Manager; closed 2026-06-15."

**✗ Avoid**: "Done" as the closure note (no measurable evidence).

<<TEXT>>

---

## Recommended additions

### Per-row source cross-reference

<<SHOULD item:10.1:reg_source_xref>>
_Traceability back to the originating finding / decision / review._

Each row points back to its source artefact: audit report ID,
management-review minutes date, incident PIR doc, etc. Lets the
auditor close the loop in either direction.

<<TEXT>>
