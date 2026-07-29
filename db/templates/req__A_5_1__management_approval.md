---
leaf_id: req:A.5.1:management_approval
control_ref: A.5.1
standard_id: ISO27001:2022
evidence_type: approval
trigger_type: universal
template_version: 2
must_count: 3
should_count: 1
---

# Top Management Approval of InfoSec Policy

> A.5.1 asks top management to formally approve the InfoSec policy. The approval can live inside the policy as a signed cover page, in a board minute, or as a separate signed cover letter — any form that names a top-management signatory, an approval date, and the version being approved.

## Question 1: Who is the top-management signatory approving this policy?

**Enter:** the signatory's name and title.

**Examples:** `Jane Doe — CEO` · `Board of Directors (as delegated to Chief Information Officer)` · `John Smith, Managing Partner`.

<<MUST item:A.5.1:approval_signatory>>

<<TEXT>>

> **Why we ask:** 27002 §5.1 requires approval by management. The signatory must hold authority to commit the organisation to the policy — CEO, board chair, or a delegated equivalent.

## Question 2: When did top management approve this policy?

**Enter:** the date the approval was signed. ISO format (YYYY-MM-DD) is preferred but any unambiguous date works.

**Example:** `2026-01-15`.

<<MUST item:A.5.1:approval_date>>

<<TEXT>>

> **Why we ask:** 27002 §5.1 requires the approval to be dated so the ISMS knows when the policy took effect and when it needs reaffirming (typically annually).

## Question 3: Which specific policy version is being approved?

**Enter:** the exact policy name and version.

**Examples:** `Information Security Policy v1.4 (2026-01-15)` · `ISMS Master Policy Rev 3`.

<<MUST item:A.5.1:approval_target>>

<<TEXT>>

> **Why we ask:** 27002 §5.1 requires the approval to name what's being approved. Ambiguous references (`the policy`) fail because auditors can't trace the approval back to the exact document that governs behaviour today.

---

## Recommended additions

_The item below strengthens the artefact but is not strictly required for the MUST checks. Fill it in if it applies to your environment._

### Question 4: What is the signatory's authority to approve? (Delegation chain if not CEO)

**Enter:** the delegation chain that gave the signatory authority. Skip this if the CEO personally approved.

**Example:** `The Board delegated ISMS policy approval to the CIO on 2024-06-01 (Board Minute 2024-06)`.

<<SHOULD item:A.5.1:approval_authority>>

<<TEXT>>

> **Why we ask:** When the signatory isn't CEO, auditors look for the delegation chain that gave them authority to approve on behalf of top management. Missing this doesn't fail the MUST but weakens the artefact.
