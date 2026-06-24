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

> **Replace the placeholders below with your content. Leave the
> MUST and SHOULD heading markers untouched — they bind this document
> to the checklist when you upload it back.**

## 1. Enumerate all 93 Annex A controls

<<MUST item:6.1.3:soa_all_annex_a>>
_Clause 6.1.3(d) — every Annex A control listed; no omissions._

The auditor's first check is **count**: do you have 93 rows? If you
don't, you've already failed Clause 6.1.3(d). Use the ISO/IEC
27001:2022 Annex A as the authoritative list — A.5.1 through A.8.34
across four control categories.

**✓ Good**: A spreadsheet with one row per control, sorted by Annex
A id, with columns: Ref, Title, Applicable (Yes/No), Justification,
Status (Implemented/Partial/Planned/Not-Applicable),
Implementing-Policy, Owner, Last-Reviewed.

**✗ Avoid**: Omitting "obvious" exclusions (e.g. A.7.x physical
controls if you're cloud-only) — they MUST appear with explicit
"Not Applicable" status + justification.

<<TEXT>>

## 2. State the Applicable / Not Applicable status per control

<<MUST item:6.1.3:soa_inclusion_status>>
_Clause 6.1.3(d) — applicability per control._

Each row gets a binary: **Applicable** (control is in scope, you
implement it) or **Not Applicable** (control is out of scope, you
don't). "Partially applicable" is not a valid SoA status — either
the control applies and you implement it, or it doesn't.

**✓ Good**: Discrete Applicable=Yes/No column. (Implementation
*depth* lives in MUST 4, not here.)

<<TEXT>>

## 3. Justify each inclusion AND exclusion

<<MUST item:6.1.3:soa_justification>>
_Clause 6.1.3(d) — justification for inclusion or exclusion._

For **Applicable=Yes**, justification is typically: "(a) Risk-driven
— addresses R-XXX from the register; (b) Legal/regulatory — required
by Y law; (c) Contractual — required by customer Z's MSA; (d)
Best-practice — sectoral expectation."

For **Applicable=No**, justification must be defensible — explain why
the control doesn't apply to your context. "Cloud-only, no physical
premises in ISMS scope per 4.3" is fine for A.7.x. "We're small"
is not.

**✓ Good** (excerpt):

| Ref | Applicable | Justification |
|---|---|---|
| A.5.15 | Yes | Risk-driven (R-001, R-002 access mismanagement); contractual (customer MSAs require RBAC) |
| A.7.1 | No | Cloud-only operations; no premises in 4.3 ISMS scope |
| A.7.10 | No | No physical storage media — cloud-only |
| A.8.25 | Yes | Risk-driven (R-007 supply-chain) + best practice for SDLC |

**✗ Avoid**: "Standard ISO control" (says nothing about *why* it
applies to YOU).

<<TEXT>>

## 4. Show implementation status per Applicable control

<<MUST item:6.1.3:soa_implementation_status>>
_Clause 6.1.3(d) — status of implementation._

For every Applicable=Yes row, status is one of: **Implemented**
(fully operating), **Partial** (operating with known gaps), **Planned**
(committed and dated). "Not Implemented" without a plan is a finding.

**✓ Good**: "Implemented", "Partial — gap: <specific>, target Q3",
"Planned — target Q4, owner: <named>."

**✗ Avoid**: All rows "Implemented" on day 1 of the ISMS (auditor
will pick this apart immediately). Be honest — partial + planned is
expected and respected.

<<TEXT>>

## 5. Reference the implementing policy / procedure per control

<<MUST item:6.1.3:soa_reference>>
_Audit defensibility — every Applicable control needs an artefact._

For each Applicable=Yes row, name the document that *implements* the
control. This is what the auditor asks for sample evidence from.

**✓ Good** (excerpt):

| Ref | Implementing Policy / Procedure |
|---|---|
| A.5.1 | Information Security Policy (DOC-001) |
| A.5.15 | Access Control Policy (DOC-014) |
| A.5.18 | Access Rights Procedure (DOC-015) |
| A.5.24 | Incident Response Procedure (DOC-024) |

**✗ Avoid**: References to "various" or "the ISMS" — the auditor
needs a specific artefact to sample.

<<TEXT>>

## 6. Name the SoA owner

<<MUST item:6.1.3:soa_owner>>
_Accountability — every controlled doc needs a named owner._

The **ISMS Manager** owns the SoA. They keep it current; significant
SoA changes go to top management.

**✓ Good**: "Document owner: ISMS Manager (<<ISMS_MANAGER_NAME>>).
Approver: ISMS Owner (<<CEO_NAME>>). Annual review at management
review per Clause 9.3."

<<TEXT>>

## 7. State version + approval date

<<MUST item:6.1.3:soa_version>>
_Document control — required by Clause 7.5._

Standard metadata. The SoA is the most-versioned ISMS artefact —
expect 4-12 versions per year as the control landscape evolves.

**✓ Good header block**:

```
Version:        v2.4
Approved:       <<APPROVAL_DATE>> by <<ISMS_OWNER_NAME>>
Next review:    <<NEXT_REVIEW_DATE>> (annually)
Change history: v1.0 initial — v1.1 added A.8.27 — v2.0
                certification body audit cycle — ...
```

<<TEXT>>

---

## Recommended additions

### List additional / external controls beyond Annex A

<<SHOULD item:6.1.3:soa_external_controls>>
_Completeness — your real control universe may exceed Annex A._

If you operate sectoral or contractual controls beyond Annex A (PCI
DSS for payment processing; HIPAA Technical Safeguards if you handle
PHI; customer-specific obligations; SOC2 controls), list them here so
the SoA is a complete view of what governs your ISMS.

<<TEXT>>
