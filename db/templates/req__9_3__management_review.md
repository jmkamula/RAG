---
leaf_id: req:9.3:management_review
control_ref: 9.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 3
must_count: 7
should_count: 2
---

# Management Review (per-execution record)

<<DOC_CONTROL>>

## What this template gives you

The **annual checkpoint** where top management formally reviews the
ISMS. Output: a record of inputs considered, decisions taken,
actions agreed. Auditors check this exists, is signed by an
attending top-management member, and that decisions actually flow to
the improvement action register. Missing or "rubber-stamp" management
reviews are a common nonconformity — auditors interview attendees to
see what they actually discussed.

## When to use it

You're producing the per-execution record required by **ISO/IEC 27001:2022 Clause 9.3**. Annual cadence at minimum (freshness 365d);
many tenants run quarterly with one designated as the formal annual
review.

## Prerequisites

<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

**2-3 days** to gather inputs + prepare the pack; **2-3 hours** for the meeting itself; **1-2 hours** to write up the record.

---

## 1. Record internal audit results

<<MUST item:9.3:audit_results>>

> _Standard text:_ Internal audit results included

_Clause 9.3.2(c)(2) — internal audit results._

Summary of audits run in the period, count of findings by
severity, key themes. Detailed findings sit in the 10.1 register;
this record summarises what management saw.

**✓ Good**: "Internal audit results in period: 4 quarterly cycle
audits + 1 ad-hoc post-incident audit on A.5.24. Findings: 0 Major
NC, 4 Minor NC (3 closed, 1 in-progress on target), 11
Observations (7 closed, 4 in-progress), 14 Opportunities for
Improvement. Key themes: access-rights review cadence drift (A.5.18);
SBOM coverage gaps on legacy components (A.8.9). Full report:
attachment A."

<<GUIDANCE>>

<<TEXT>>

## 2. Record nonconformity + corrective-action status

<<MUST item:9.3:nonconf>>

> _Standard text:_ Nonconformities and corrective actions status

_Clause 9.3.2(c)(3) — status of nonconformities + corrective actions._

The open + closed ledger from the 10.1 register. Highlight any
overdue items — top management can authorise re-prioritisation.

**✓ Good**: "Corrective action status (snapshot at review date):
9 in-progress, 14 closed in period, 2 overdue. Overdue: AC-117
(SBOM tooling rollout slipped 6 weeks due to vendor dependency —
new target reaffirmed) and AC-203 (privileged-access review automation
slipped due to engineering capacity — re-prioritised vs other work
this review). Management directed: accept the slip; no further
escalation."

<<GUIDANCE>>

<<TEXT>>

## 3. Record monitoring + measurement results

<<MUST item:9.3:monitoring>>

> _Standard text:_ Monitoring and measurement results

_Clause 9.3.2(c)(4) — monitoring and measurement results._

The 9.1 metrics dashboard. State each metric, current value, trend,
and whether it's on/off target.

**✓ Good**: "Monitoring + measurement (current vs target):
(1) Platform availability: 99.93% / target 99.9% — on. (2) MTTR
critical vulns: 41h / target <72h — on. (3) Phishing
click-through (drilled): 4.2% / target <5% — on. (4) Open
high+critical risks: 6 / target <10 — on. (5) Access-review
freshness (% of accounts reviewed in last 90 days): 87% / target
>95% — OFF (trigger: 10.1 row AC-203). Full dashboard: attachment B."

<<GUIDANCE>>

<<TEXT>>

## 4. Record progress against information security objectives

<<MUST item:9.3:objectives>>

> _Standard text:_ Progress toward information security objectives

_Clause 9.3.2(c)(5) — extent of objectives fulfilment._

The objectives stated in your 5.2 policy / 6.2 plan, scored against
their targets.

**✓ Good**: "Objectives (FY26): (1) Maintain ISO 27001 certification
zero major NC — on track (annual surveillance audit clean).
(2) Platform availability >99.9% — achieved (99.93%). (3) <72h
MTTR critical vulns — achieved (41h average). (4) Zero confirmed
unauthorised data disclosures — achieved (0). All FY26 objectives
on track at this review."

<<GUIDANCE>>

<<TEXT>>

## 5. Record feedback from interested parties

<<MUST item:9.3:interested>>

> _Standard text:_ Feedback from interested parties

_Clause 9.3.2(c)(7) — feedback from interested parties._

Customers, regulators, certification bodies, contracted parties.
Be honest about complaints too — favourable-feedback-only reviews
read badly to auditors.

**✓ Good**: "Interested-party feedback: (a) Customer trust reviews:
12 customer security questionnaires completed in period; 3 customers
raised follow-up clarifications (all closed). (b) Certification body
surveillance: clean, no findings; auditor commended improvement
discipline. (c) Regulator: 1 ICO information request answered within
SLA (subject-access related); no enforcement action. (d) Employee
ISMS feedback (anon survey): security training pace flagged 'too
frequent' — review recommended (action: AC-220)."

<<GUIDANCE>>

<<TEXT>>

## 6. Record decisions + actions

<<MUST item:9.3:decisions>>

> _Standard text:_ Decisions and actions recorded

_Clause 9.3.3 — decisions related to continual improvement +
changes to the ISMS._

The output of the meeting. Decisions taken, who's accountable, what
goes to 10.1. Audit-traceability hangs on this.

**✓ Good**: "Decisions: (1) Approve risk treatment plan v2.4 with
the additional A.8.27 architecture-principles control (driven by
R-042). Action: ISMS Manager updates SoA; AC-225 opens in 10.1.
(2) Re-prioritise AC-203 from Q2 to Q3 given engineering capacity;
add automation work to the FY27 plan. (3) Extend security training
cadence from quarterly to semi-annually for non-engineering staff;
keep quarterly for engineering. Action: A.6.3 programme owner.
(4) Refresh the InfoSec Policy v3 to reflect the new objectives.
Action: ISMS Manager."

<<GUIDANCE>>

<<TEXT>>

## 7. Top-management attendance + sign-off

<<MUST item:9.3:approved>>

> _Standard text:_ Approved by top management attendee

_Top management commitment — a member must attend (and sign)._

Name the top-management attendee(s) and have them sign the record.
"Top management" = the person or group with authority to allocate
ISMS resources. CEO, CISO, ISMS Owner all qualify; "the ISMS team"
does not.

**✓ Good**: "Attended (top management): <<CEO_NAME>> (CEO, ISMS
Owner); <<CISO_NAME>> (CISO). Signed: <<CEO_NAME>>, on
<<APPROVAL_DATE>>."

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

### Meeting date + next planned date

<<SHOULD item:9.3:date>>

> _Standard text:_ Date of review

_Cadence discipline._

State this review's date + the next planned management review date.

<<GUIDANCE>>

<<TEXT>>

### Attendee list (beyond top management)

<<SHOULD item:9.3:attendees>>

> _Standard text:_ Attendees listed

_Completeness — who else was in the room shapes the conversation._

ISMS Manager, DPO, key control owners, internal auditor. Listing them
helps the auditor see the conversation was substantive.

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
