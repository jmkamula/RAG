---
name: workbook-orphan-disposition-2026-06-11
description: "SHIPPED 2026-06-11 (f7c934f): F2 dispositions for 3 structurally-tricky Arion orphan sheets. Tightened isms_manual_change_log + supplier_review_log + 4_1_context_issues_register (overly-broad fingerprints removed). Broadened 4_2_interested_parties_register (alt sheet shape). New personnel_security_attestation_register.yaml (multi-pass: A.6.3 + A.6.6). 11 new findings, 1 sheet correctly unmatched."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Follow-up to F1 ([[workbook-yaml-vocab-refresh-2026-06-11]]):
after the vocab broadening + G1/G2 fixes left 3 still-orphan
sheets in Arion's workbook, F2 worked through them. Each had a
different structural mismatch and required a different
disposition.

## The three F2 cases

### 1. This Doc Chng Control → correctly unmatched

Sheet is a workbook-front-matter sign-off block (Title / Owner /
Date / Signatures) followed by a 1-row revision history. NOT
ISMS-wide change evidence — it's the workbook file's own version
history.

Existing match: `isms_manual_change_log.yaml` at 0.475
confidence via `[doc, change, control]` fingerprint.

Fix: removed `[doc, change, control]` from
`isms_manual_change_log.yaml` sheet_name_fingerprints (too
broad). Tightened to ISMS-specific fingerprints only
(`[isms, manual, change]`, `[manual, change]`,
`[isms, change, log]`).

Result: sheet now unmatched. That's the correct outcome —
workbook metadata isn't compliance evidence.

### 2. Internal&External Parties → 4.2 (was 4.1)

Sheet is a stakeholder map: per-party rows with Category column
holding "Internal"/"External" as ROW VALUES (not column names).
Columns: Nature of the Party, Category, Interest/Concern, ISMS
Requirement, Communication Method. Same 4.2 evidence as the
existing "Interested Parties" sheet, different visual layout.

Existing match: `4_1_context_issues_register.yaml` at 0.433
confidence (wrong-shape — 4.1 wants issues columns, this sheet
has parties).

Fix:
  - Tightened `4_1_context_issues_register.yaml`: removed
    `[internal, external]` fingerprint (matched the parties
    sheet instead of an issues register).
  - Broadened `4_2_interested_parties_register.yaml`: added
    `[internal, external, parties]` + `[stakeholder, *]`
    sheet fingerprints; added column bindings for `[nature,
    party]`, `[interest]`, `[concern]`, `[needs, expectations]`,
    `[isms, requirement]`, `[communication, method]`,
    `[category]`.

Result: 4.2 match at 1.0 confidence, 4/6 satisfied. 4.1 no
longer matches.

### 3. Business Partners Assessment → new YAML (A.6.3 + A.6.6)

Sheet header lives on row 7 (rows 1-6 are narrative intro). The
"partners" are Arion's own people (Joseph Kamula, Libor Ballaty,
Zorko Petrusa, Yusuf Yusufov). Columns: Partner Name, Assessment
Date, NDA signed, Access Registry, Training Completed, BYOD
Attestation, Overall Status, Assessed By, Next Review, Notes.

This is **personnel security attestation**, not supplier review.
Common structure across tenants — contractors/consultants
attest to NDA + training + BYOD compliance.

Existing match: `supplier_review_log.yaml` at 0.433 confidence
via `[business, partner]` / `[partner, assessment]` fingerprints.

Fix:
  - Tightened `supplier_review_log.yaml`: removed `[business,
    partner]` / `[partner, assessment]` / `[partner, risk]`
    fingerprints (overloaded — "partner" used for both
    personnel and third-party suppliers).
  - Created **new** `personnel_security_attestation_register.yaml`
    with two passes:
      - Pass 1 → `req:A.6.3:training_completion_register`
        (4 bindings: personnel_id, completion_date, next_due, status)
      - Pass 2 → `req:A.6.6:nda_signature_register`
        (3 bindings: signatory_id, signature_date, expiry_or_active)
    `header_row_hints: [1, 7]` to handle the narrative-intro layout.

Result: 7 findings (4 + 3), 1.0 confidence on both passes.

## Structural caveat — summary registers vs per-event registers

The personnel attestation YAML produces findings on A.6.3 +
A.6.6, but those leaves expect PER-EVENT records (one row per
training module completion, one row per NDA signature). Arion's
sheet is a PER-PERSON summary (one row per person with
last-training-date and last-NDA-date).

This means several leaf MUSTs (`module_id`, `score`,
`signature_method`, `template_version`, `variant`) genuinely
don't fit summary registers. Even with the new YAML, A.6.3 +
A.6.6 leaves stay PARTIAL — not fully satisfied — when summary
register is the only evidence.

Three paths forward (F3 candidates):
  - **Spec expansion**: add a `summary_attestation_register`
    sibling leaf to A.6.3 / A.6.6 with fewer MUSTs. Tenants
    who maintain only summary registers get full credit there.
  - **MUST→SHOULD demotion** on per-event-specific items
    (module_id, score, signature_method, template_version,
    variant). Loosens the per-event leaves to accept summary
    registers; G2-shape change.
  - **Accept partial coverage as the answer** for tenants who
    only maintain summary attestation. Stage-1 surface shows the
    evidence; engine carries the leaf at partial; OFI stays
    OFI instead of becoming Comply.

Deferred — none urgent, all three are policy/curation
discussions rather than mechanical fixes.

## Operational summary

| sheet | prior | now |
|---|---|---|
| This Doc Chng Control | matched isms_manual_change_log @ 0.475, 0 findings | unmatched (correct) |
| Internal&External Parties | matched 4.1 @ 0.433, 0 findings | matched 4.2 @ 1.0, 4 findings |
| Business Partners Assessment | matched supplier_review_log @ 0.433, 0 findings | matched personnel_security_attestation_register @ 1.0, 7 findings |

11 new pending Stage-1 findings; 4 stale orphan proposals
superseded; 4 YAMLs touched (3 tightened, 1 broadened) + 1
created.

## Lesson

This batch was qualitatively different from F1/G1/G2 — those
were all "make existing matches work better". F2 was "decide
the right disposition when fingerprint matching gives a
wrong-shape match at moderate confidence". The fix required
**judgment per sheet**, not a mechanical rule. The fingerprint-
matching layer can't make these calls on its own — see
[[feedback-intake-label-unreliability]] for the broader
architectural implication.

## Related

- [[workbook-yaml-vocab-refresh-2026-06-11]] — F1 + G1 + G2 arc;
  this is F2.
- [[feedback-intake-label-unreliability]] — strategic position
  on what we still owe.
- [[feedback-workbook-yamls-semantic-class]] — sibling rule on
  generalising fingerprints; F2 dispositions also embody it.
