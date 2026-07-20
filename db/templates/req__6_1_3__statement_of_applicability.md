---
leaf_id: req:6.1.3:statement_of_applicability
control_ref: 6.1.3
standard_id: ISO27001:2022
evidence_type: statement_of_applicability
trigger_type: universal
freshness_days: 365
template_version: 2
must_count: 7
should_count: 1
table_shape: hybrid
---

# Statement of Applicability (SoA)

## What this template gives you

The **single most important artefact** in your ISMS — and **the first
thing an external auditor opens**. The SoA is the master ledger: every
one of the 93 Annex A controls listed, marked Applicable or Not
Applicable, justified, status-tracked, and cross-referenced to the
implementing policy. The quality of your SoA signals the maturity of
the entire ISMS.

## When to use it

You're producing the SoA mandated by **ISO/IEC 27001:2022 Clause
6.1.3(c-d)**. The SoA is **annually refreshed at minimum** (freshness
= 365 days) and on any significant change.

## Before you start

- [ ] **6.1.2 Risk Assessment** done — risks drive control selection
- [ ] **6.1.3 Risk Treatment Plan** in progress (co-produced with SoA)
- [ ] **4.3 ISMS Scope** stable — applicability decisions depend on
      scope (e.g. A.7 physical controls N/A for cloud-only orgs)
- [ ] **A.5.31 Compliance register** — drives Applicable=Yes for
      controls tied to legal/contractual obligations

## Cross-references

- **Every Annex A control** — the SoA is the source-of-truth for
  whether each one is in scope
- **6.1.3 Risk Treatment Plan** (sibling) — treatment rows resolve to
  Applicable controls in the SoA
- **9.2 Internal Audit** — the audit programme covers every
  Applicable control over its cycle
- **9.3 Management Review** — SoA changes are a standing input

## Estimated effort

**8-16 hours** for v1 (one pass through 93 controls + cross-link
work); **2-4 hours** for annual refresh. Use a spreadsheet — many
tenants find their SoA outgrows a word-processor.

---

## The 93-row control table

This is the **heart of the SoA**. One row per Annex A control (all
93). The auditor's first check is **count** — if you don't have 93
rows, you've already failed Clause 6.1.3(d).

<!-- TABLE-COLUMNS leaf:req:6.1.3:statement_of_applicability -->
<!-- column: item:6.1.3:soa_all_annex_a -->
<!-- column: item:6.1.3:soa_inclusion_status -->
<!-- column: item:6.1.3:soa_justification -->
<!-- column: item:6.1.3:soa_implementation_status -->
<!-- column: item:6.1.3:soa_reference -->
<!-- /TABLE-COLUMNS -->

<!-- EDIT-ZONE-START leaf:req:6.1.3:statement_of_applicability -->
| Control Ref | Applicable (Yes/No) | Justification | Implementation Status | Implementing Policy / Procedure |
|---|---|---|---|---|
| A.5.1       |                     |               |                       |                                  |
| A.5.2       |                     |               |                       |                                  |
| ... (add rows A.5.3 through A.8.34 — all 93) | | | | |
<!-- EDIT-ZONE-END leaf:req:6.1.3:statement_of_applicability -->

## Column guidance — what to fill in

### Control Ref (all 93)

<<MUST item:6.1.3:soa_all_annex_a>>

> _Standard text:_ All 93 Annex A controls enumerated (no omissions)

Use the ISO/IEC 27001:2022 Annex A as the authoritative list —
A.5.1 through A.8.34 across four control categories. Don't omit
"obvious" exclusions (e.g. A.7.x physical if you're cloud-only) —
they MUST appear with explicit Not Applicable status + justification.

**✓ Good**: Spreadsheet with one row per control, sorted by Annex A
id. Count check at top: "93/93".

**✗ Avoid**: Omitting Not-Applicable controls — auditor will catch
this on first scan.

### Applicable (Yes/No)

<<MUST item:6.1.3:soa_inclusion_status>>

> _Standard text:_ Inclusion status per control (Applicable / Not
> Applicable)

Each row: **Applicable** (in scope, you implement it) or **Not
Applicable** (out of scope, you don't). "Partially applicable" is
not a valid SoA status.

**✓ Good**: Discrete column with Yes/No. Implementation depth lives
in the "Implementation Status" column, not here.

**✗ Avoid**: Mixing applicability and implementation status — they're
separate dimensions.

### Justification

<<MUST item:6.1.3:soa_justification>>

> _Standard text:_ Justification per control (why included / why
> excluded)

For **Applicable=Yes**: risk-driven (R-XXX), legal/regulatory
(law Y), contractual (customer Z), or best-practice.

For **Applicable=No**: defensible reasoning — "cloud-only, no
premises in 4.3" is fine; "we're small" is not.

**✓ Good**: `Risk-driven (R-001, R-002 access mismanagement);
contractual (customer MSAs require RBAC)`

**✗ Avoid**: "Standard ISO control" — says nothing about why it
applies to YOU.

### Implementation Status

<<MUST item:6.1.3:soa_implementation_status>>

> _Standard text:_ Status of implementation per included control
> (Implemented / Partially / Planned)

Discrete: `Implemented` (fully operating), `Partial` (operating with
known gaps), `Planned` (committed + dated). "Not Implemented" without
a plan is a finding.

**✓ Good**: `Partial — gap: <specific>, target Q3`, `Planned —
target Q4, owner: <named>`

**✗ Avoid**: All rows "Implemented" on day 1 — be honest. Partial +
planned is expected and respected.

### Implementing Policy / Procedure

<<MUST item:6.1.3:soa_reference>>

> _Standard text:_ Reference to the implementing policy/procedure
> per included control

For each Applicable=Yes row, name the document that *implements* the
control. This is what the auditor asks for sample evidence from.

**✓ Good**: `Access Control Policy (DOC-014)`, `Incident Response
Procedure (DOC-024)`

**✗ Avoid**: "Various" or "the ISMS" — auditor needs a specific
artefact.

---

## Document-level fields

These are properties of the SoA AS A DOCUMENT — not per-row data.

### Owner

<<MUST item:6.1.3:soa_owner>>

> _Standard text:_ Named owner of the SoA (typically ISMS Manager)

The ISMS Manager owns the SoA. Significant SoA changes go to top
management for approval.

<!-- EDIT-ZONE-START item:6.1.3:soa_owner -->
<<TEXT>>
<!-- EDIT-ZONE-END item:6.1.3:soa_owner -->

### Version + Approval Date

<<MUST item:6.1.3:soa_version>>

> _Standard text:_ Version number and approval date stated

Standard metadata. The SoA is the most-versioned ISMS artefact —
expect 4-12 versions per year as the control landscape evolves.

**Example header block**:
```
Version:        v2.4
Approved:       <<APPROVAL_DATE>> by <<ISMS_OWNER_NAME>>
Next review:    <<NEXT_REVIEW_DATE>> (annually)
Change history: v1.0 initial — v1.1 added A.8.27 — v2.0
                certification body audit cycle — ...
```

<!-- EDIT-ZONE-START item:6.1.3:soa_version -->
<<TEXT>>
<!-- EDIT-ZONE-END item:6.1.3:soa_version -->

---

## Recommended additional columns

_For tenants who carry additional control sets._

### External / Additional Controls

<<SHOULD item:6.1.3:soa_external_controls>>

> _Standard text:_ External / additional controls beyond Annex A
> listed where used (sectoral, contractual)

If you operate sectoral or contractual controls beyond Annex A (PCI
DSS, HIPAA Technical Safeguards, customer-specific obligations, SOC2
controls), list them here as additional table rows so the SoA is a
complete view.

---

## PIMS extension — for ISO 27701-enrolled tenants

If your organisation is enrolled in **ISO/IEC 27701:2019** (Privacy
Information Management System), your SoA MUST enumerate the 27701
Annex A + Annex B anchors alongside the 93 ISO 27001 controls above.
27701's own clause 5.4.1.3 mirrors 27001's 6.1.3 and requires the
same applicability + implementation-status table for PIMS-specific
controls.

**49 anchors total** — extend your SoA table below the 93 ISO 27001
rows with:

- **A.7.2.1 – A.7.2.8** (Batch 1 — 7 controls for identify + lawful
  basis + consent + PIA + processor contracts + joint controllers +
  records of processing PII)
- **A.7.3.1 – A.7.3.10** (Batch 2 — 10 controls for data subject
  rights: information, providing information, mechanisms to modify
  or withdraw consent, object, access, correct, erase, controller
  obligations to inform third parties, provide copy, handle
  requests, automated decision-making)
- **A.7.4.1 – A.7.4.9** (Batch 2 PbD — 9 controls: limit collection,
  limit processing, accuracy, minimisation, de-identification at
  end of processing, temp files, retention, disposal, transmission)
- **A.7.5.1 – A.7.5.4** (Batch 3 transfers — 4 controls: basis for
  transfer, countries, records of transfer, records of disclosure)
- **B.8.2.1 – B.8.2.6** (Batch 1 processor mirror — 6 controls for
  customer agreement, org purposes, marketing, infringing
  instruction, customer obligations, RoPA)
- **B.8.3.1** (processor subject-rights obligation — route DSAR to
  controller)
- **B.8.4.1 – B.8.4.3** (Batch 2 processor retention — 3 controls:
  temp files, return/transfer/disposal on churn, transmission)
- **B.8.5.1 – B.8.5.8** (Batch 3 processor transfers — 8 controls:
  basis for transfer, countries, disclosure records, notification of
  disclosure requests, legally-binding disclosures, disclosure of
  subcontractors, engagement of subcontractor, change of
  subcontractor)

**Applicability by role:**

- If tenant is a **controller only** (`role_controller = true`,
  `role_processor = false`), only A.7.x applies. Mark all B.8.x
  rows Not Applicable with justification "Arion acts as controller
  only — processor obligations do not apply".
- If tenant is a **processor only**, only B.8.x applies. A.7.x
  Not Applicable.
- If tenant is **both** (like ArionComply which is a controller for
  its own data AND a processor for customer-uploaded PII), enumerate
  ALL 49 anchors with per-anchor applicability.
- **A.7.2.7** (joint PII controller) is Not Applicable unless
  `role_joint_controller = true`.
- **A.7.3.10** (automated decision-making) is Not Applicable unless
  `automated_decision_making = true` in your data-processing facts.

**Row format:** identical to the 93 ISO 27001 rows above — the SoA
is a single table with all applicable controls under one header,
sorted by standard then ref. Do not fork into a separate document;
auditors expect one master ledger.

**Example rows:**

| Control Ref | Applicable (Yes/No) | Justification | Implementation Status | Implementing Policy / Procedure |
|---|---|---|---|---|
| A.7.2.1 | Yes | PII processing purposes documented per ISO 27701:2019 §5.4.1.1 | Partial — purpose register drafted, per-purpose retention pending | Privacy Program Charter (DOC-041) |
| A.7.2.7 | No | Arion has no joint-controller arrangements (role_joint_controller = false) | — | — |
| A.7.3.10 | No | Automated decision-making = false in data-processing facts | — | — |
| B.8.2.1 | Yes | Arion holds customer-uploaded PII under DPA; processor role active | Partial — DPA in place, contract-scope register pending | Data Processing Agreement (DOC-052) |
