---
leaf_id: req:9.2:internal_audit_programme
control_ref: 9.2
standard_id: ISO27001:2022
evidence_type: audit_programme
trigger_type: universal
template_version: 3
must_count: 7
should_count: 2
---

# Internal Audit Programme

## What this template gives you

The **plan** for how your ISMS audits itself — over which cycle,
covering what scope, by which auditors, against what criteria, and
how findings are reported and tracked to closure. Auditors check
that you actually run it; missing or empty audit records are one of
the most common reasons certifications slip.

## When to use it

You're producing the audit programme required by **ISO/IEC 27001:2022
Clause 9.2**. Distinct from individual audit *results* (those are
the per-execution records). This template is the standing programme
document.

## Before you start

- [ ] **4.3 ISMS Scope** stable — the audit programme covers the
      whole ISMS scope across its cycle
- [ ] **6.1.3 Statement of Applicability** complete — auditor uses
      the SoA to know which controls to cover
- [ ] **5.3 Roles** clear — auditor independence requirement
      depends on the role structure

## Cross-references

- **9.3 Management Review** — audit results are a standing input
- **10.1 Improvement Action Register** — audit findings open
  improvement-action rows; closure tracked there
- **A.5.35 Independent review** — separate annual independent
  review (don't conflate)
- **A.5.36 Compliance review** — programme reviews compliance with
  policies; pairs with this audit programme

## Estimated effort

**3-5 hours** for v1 programme document; **per audit**: 2-5 days of
auditor time depending on scope sample.

---

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Define audit frequency

<<MUST item:9.2:frequency>>

> _Standard text:_ Audit frequency defined

_Clause 9.2.2(a) — frequency and methods._

State how often audits run and the cycle by which the full ISMS
scope is covered. Common: annual full-scope OR rolling
quarterly-by-domain so the whole ISMS is covered each year.

**✓ Good**: "Frequency: continuous quarterly audit cycle. Q1 covers
ISMS governance + management-system clauses (4-10). Q2 covers
A.5 + A.6 (organisational + people). Q3 covers A.7 + A.8 (physical
+ technological). Q4 covers cross-cutting + targeted high-risk
deep-dives based on prior findings + threat-intel. Full SoA covered
within each 12-month cycle. Surveillance audits trigger gap audits
on areas flagged."

**✗ Avoid**: "Annually" (the standard expects more rigour for a
non-trivial ISMS).

<<TEXT>>

## 2. Define audit scope covering all ISMS processes

<<MUST item:9.2:scope>>

> _Standard text:_ Audit scope covering all ISMS processes

_Clause 9.2.2(a) — scope per audit._

Each audit cycle's scope, mapped to the ISMS clauses + Annex A
controls in the SoA. State explicitly that the full SoA is covered
across the cycle.

**✓ Good**: "Audit scope: every Applicable control in the
Statement of Applicability + every ISMS clause (4-10) covered at
least once per 12-month cycle. Per-cycle scope: the Q-plan above
allocates clauses + controls to quarters. Out-of-cycle scope:
incidents trigger targeted audits of affected control families;
significant changes trigger pre-deployment audit of new controls."

<<TEXT>>

## 3. Define audit criteria

<<MUST item:9.2:criteria>>

> _Standard text:_ Audit criteria defined

_Clause 9.2.2(a) — criteria for each audit._

The **standards** the audit measures against. Always includes ISO/IEC
27001:2022. May include sectoral standards, customer obligations,
internal policies.

**✓ Good**: "Audit criteria: (1) ISO/IEC 27001:2022 (the standard
itself). (2) ISO/IEC 27002:2022 guidance for Annex A controls.
(3) The current Statement of Applicability. (4) <<TENANT_NAME>>
internal policies (the A.5 set + ISMS procedures). (5) Applicable
regulatory requirements per A.5.31. (6) Customer-specific
obligations per signed MSAs where they exceed the standard's
baseline."

<<TEXT>>

## 4. Set auditor independence + competence requirements

<<MUST item:9.2:independence>>

> _Standard text:_ Auditor independence and competence requirements

_Clause 9.2.2(b) — auditor selection ensuring impartiality and
objectivity._

State independence rules (auditors don't audit work they own /
control) and competence requirements (training, certification,
experience).

**✓ Good**: "Auditor independence: auditors do not audit work
they personally implemented or processes they currently own. Cross-
team assignment is the default (Platform Eng audits SecOps; SecOps
audits Platform Eng; ISMS Manager audits cross-cutting clauses).
Competence requirements: at minimum ISO 27001 Lead Auditor (IRCA
or equivalent) training; 2 years' relevant experience; refresher
training every 3 years. External auditor used for the annual
independent review per A.5.35."

<<TEXT>>

## 5. Define the reporting process

<<MUST item:9.2:reporting>>

> _Standard text:_ Reporting process to management defined

_Clause 9.2.2(c) — report results to relevant management._

Where findings go, to whom, in what format, on what cadence.

**✓ Good**: "Reporting: each audit produces a report within 10
business days of audit closure. Report structure: scope, criteria,
sample evidence, findings (Major NC / Minor NC / Observation /
Opportunity for Improvement), recommendations. Report distributed
to: (a) ISMS Manager (always), (b) the audited control owners,
(c) ISMS Owner / Steering Committee, (d) input to next Management
Review. Quarterly roll-up published at the ISMS Steering Committee."

<<TEXT>>

## 6. Define corrective-action follow-up

<<MUST item:9.2:corrective>>

> _Standard text:_ Corrective action follow-up process

_Clause 9.2.2(d) — implement corrections + corrective actions._

Findings don't close themselves — state the closure mechanism. Pairs
with Clause 10.1.

**✓ Good**: "Each finding triggers a row in the 10.1 Improvement
Action Register within 5 business days of report distribution. Owner
assigned, target date set, status tracked. Auditor re-verifies on
target date; if implemented effectively, finding closes with
effectiveness assessment recorded. If not closed, escalates to ISMS
Manager + back into the next audit cycle."

<<TEXT>>

## 7. Name the programme owner

<<MUST item:9.2:owner>>

> _Standard text:_ Named owner of the programme (typically ISMS Manager + independent auditor)

_Accountability — every controlled doc needs a named owner._

Typically split: the **ISMS Manager** owns the programme; the
**Lead Auditor** runs each audit. State both.

**✓ Good**: "Programme owner: ISMS Manager
(<<ISMS_MANAGER_NAME>>) — owns the programme document, sets the
cycle plan, ensures auditor competence and independence. Per-audit
Lead Auditor named per-audit in the cycle plan; rotates to maintain
independence."

<<TEXT>>

---

## Recommended additions

### Publish the cycle schedule

<<SHOULD item:9.2:schedule>>

> _Standard text:_ Audit schedule for current period

_Visibility — auditees know when their area will be audited._

Publish the per-quarter schedule so audited teams can prepare.
Avoids the "ambush" feel that triggers political pushback.

<<TEXT>>

### Record-retention for audit artefacts

<<SHOULD item:9.2:records>>

> _Standard text:_ Record retention requirements (cross-link to 7.5)

_Audit records have specific retention needs (typically 6 years
or as required by certification body)._

State retention period for audit reports, evidence collected, sample
selections.

<<TEXT>>
