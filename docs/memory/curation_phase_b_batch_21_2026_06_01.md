---
name: curation-phase-b-batch-21-2026-06-01
description: Phase B batch 21 — A.6 People Controls 7-pack. LARGEST multi-control batch yet — 7 controls × 4 leaves = 28 new evidence requirements. Closes the A.6 block. Eval 77/78 → 83/85 (all 7 new cases PASS).
metadata: 
  node_type: memory
  type: project
  originSessionId: cc746afe-8680-4e51-a963-96eb379653f8
---

Phase B batch 21 — A.6 People Controls 7-pack bulk promotion. A.6.1
+ A.6.2 + A.6.3 + A.6.4 + A.6.5 + A.6.6 + A.6.8 all promoted from
single-leaf to 4-leaf. A.6.7 was already curated as REQ_REMOTE_WORKING
(profile_fact triggered), so 7 of 8 A.6 controls in this batch closes
the A.6 block.

**Why:** User chose "A.6 People bulk - all 7 controls" after batch 20
closed A.5. Phase B multi-control batching pattern is locked in
(batches 1, 3, 4, 19 precedent). This is the largest such batch yet —
previous record was batch 3 with 5 controls (supplier+cloud 5-pack).

**How to apply:** Largest-batch-yet pattern works. Spine mixing within
a batch is fine — A.6 used 2 spine variants (op_process procedure-as-
primary for 5 controls; records_program template-as-primary for 2
controls). Future blocks can mix freely too — A.7 (14 physical
controls) would likely be a similar mix of op_process and policy.

**Shipped (commit pending — current session 2026-06-01):**
- 28 leaves total (7 × 4-leaf):
  - **A.6.1 Screening** (op_process): screening_procedure (preserves
    id) + screening_record_register + applicable_roles_scope +
    program_review (freshness=365)
  - **A.6.2 Employment terms** (records_program template-as-primary):
    employment_terms_template (preserves id) + signed_terms_register
    + applicable_workers_scope + template_review (freshness=365)
  - **A.6.3 Security awareness** (op_process programme-as-primary):
    security_awareness_programme (preserves id, freshness=365) +
    training_completion_register + audience_curriculum_scope +
    programme_review (freshness=365)
  - **A.6.4 Disciplinary process** (op_process): disciplinary_process
    (preserves id) + disciplinary_case_register + applicable_
    jurisdictions_scope + process_review (freshness=365)
  - **A.6.5 Post-employment** (op_process): post_employment_
    responsibilities (preserves id) + leaver_briefing_register +
    surviving_obligations_scope + program_review (freshness=365)
  - **A.6.6 NDA** (records_program template-as-primary): nda_template
    (preserves id, freshness=365) + nda_signature_register +
    applicable_parties_scope + template_review (freshness=365)
  - **A.6.8 Event reporting** (op_process): event_reporting_procedure
    (preserves id) + event_report_register + reporting_audience_scope
    + program_review (freshness=365)
- All 7 engine verdicts: NC at 0/4 children satisfied. Live postures
  (1 OFI + 6 Comply) all flip to engine-proposed NC in Stage-2.
- 7 eval cases added (79-85), all PASS on first run.
- Eval 77/78 → 83/85 (#3 stochastic + #25 known-stale fail; both
  documented non-blocking).

**Item-id preservation:**
NO DerivedSpec references to any A.6.x items. Only the 7 primary-leaf
ids need preservation — all preserved. Clean batch on preservation
grounds — easiest of the recent batches.

**Spine variant mix (validates the flexibility):**
This batch demonstrates that a single bulk batch can mix spine variants:
- 5 op_process variants (procedure / programme as primary)
- 2 records_program template-as-primary variants

No new spine variants introduced — both are already-proven patterns
from earlier batches. The mix is determined by the control's natural
primary-artefact shape (procedure vs template).

**Cross-control link web — A.6 is the HR/contractual integration layer:**
A.6 doesn't operate standalone — it's the HR/contractual layer that
sits ABOVE the technical/operational controls in A.5 and A.8. The
batch establishes these cross-control links:

- **A.6.1 ↔ A.5.18**: screening_record_register.decision_date proves
  screening completed BEFORE A.5.18 access granted (gates the
  A.5.18 grant)
- **A.6.1 ↔ A.5.31**: applicable_roles_scope sources jurisdictional
  check legality from the single legal-obligations register
- **A.6.2 + A.6.6**: together form the personnel info-security
  contract package; A.6.2 = duties during employment, A.6.6 = duties
  during AND after access (NDA survives)
- **A.6.3 ↔ A.5.18**: onboarding training BEFORE access granted
- **A.6.3 ↔ A.8.25/A.5.15/A.8.2/etc**: role-specific deep-dive
  modules connect to the technical controls each role operates
- **A.6.4 ↔ A.5.36**: disciplinary cases are a particular type of
  compliance nonconformity; both registers can be one artefact in
  mature programs
- **A.6.5 ↔ A.5.11/A.5.16/A.5.17/A.5.18**: A.6.5 is the contractual
  layer ABOVE the operational offboarding (return of assets +
  identity revocation + credential revocation + access revocation);
  A.6.5 is "what they agreed to", A.5.x are "what actually happens"
- **A.6.6 ↔ A.5.12**: NDA info_classes sources from classification
  scheme
- **A.6.6 ↔ A.6.5**: NDA continuation note reinforced at exit
  briefing (most NDAs survive employment)
- **A.6.8 ↔ A.5.25**: handoff_to_triage MUST closes the reporting
  → triage → incident pipeline
- **A.6.8 ↔ A.6.3**: awareness_promotion SHOULD drives channel
  discoverability (channel awareness decays without reminders)

**Three new patterns introduced:**

1. **Anonymised case register pattern (A.6.4)**:
   The disciplinary_case_register MUST preserve anonymity at the
   audit-trail layer to comply with privacy requirements while
   internal traceability to personnel record is preserved. New
   pattern for sensitive operational registers.

2. **Trigger-threshold-driven scope pattern (A.6.6)**:
   The applicable_parties_scope encodes a "trigger threshold" — only
   parties touching confidential-class info and above need an NDA.
   Some scopes are universal (every employee), some are conditional
   (only some parties). Encoded explicitly as a MUST.

3. **Contractual-layer-vs-operational-layer pattern (A.6.5 + A.6.2 +
   A.6.6)**:
   A.6 controls are the contractual/HR layer; A.5/A.8 are the
   operational/technical layers. The A.6.5 offboarding_integration
   MUST makes this explicit — A.6.5 + A.5.11/16/17/18 together form
   the full offboarding shape, neither alone is sufficient.

**Reporting culture MUSTs (A.6.8):**
A.6.8 introduces "reporting culture" as a first-class concept:
- `no_blame` MUST (encourages honest reporting; under-reporting is
  the #1 risk for incident programs)
- `anonymity_option` SHOULD (drives reporting of insider-threat and
  whistleblower-territory cases)
- `awareness_promotion` SHOULD (channel discoverability decays
  without reminders)
- `acknowledgment` SHOULD (closes the feedback loop — reporters
  who never hear back stop reporting)
- `rev_volume_trend` MUST on review (sudden volume drops surface
  under-reporting risk)

This is the auditor-critical "is the program actually being used?"
slice — most programs have a reporting channel but no usage; A.6.8
encodes the cultural conditions for usage.

**Freshness cadence:**
All 7 controls use 365d (annual) freshness on review leaves. A.6.3
+ A.6.6 also have 365d freshness on their primary leaves (programme
and template need annual refresh). All other primary leaves are
operational and continuously maintained.

No tighter cadences here — none of the A.6 controls have the high-
volume drift that drives the 180d cadence used by A.5.16/A.5.17/
A.5.18/A.5.25/A.5.26/A.5.31.

**Eval coverage strategy:**
All 7 controls eval-covered (cases 79-85). All return NC 0/4 with
clean engine-proposes-NC text. No partial-evidence cases in this
batch (live postures don't match well enough with the new richer
MUST sets to trigger semantic matching) — different from A.5.34
which had a partial-evidence A.6 leaf already in Arion's documents.

**Where this leaves the curation arc:**
- **A.5 Organisational Controls** — fully multi-leaf at Style v2
  (37/37 controls, closed by batch 20)
- **A.6 People Controls** — fully multi-leaf (8/8 — 7 from this
  batch + A.6.7 already curated)
- **A.7 Physical Controls** — all single-leaf today (14 controls)
- **A.8 Technological Controls** — mixed multi-leaf status (6
  already multi-leaf: A.8.2/A.8.11/A.8.24/A.8.25/A.8.26/A.8.27;
  rest single-leaf — large bulk batch candidate)
- **GDPR Articles** — 4 already multi-leaf (Art.15/Art.28/Art.30
  + the DerivedSpec articles); rest mixed

Natural next batches:
1. **A.7 Physical 14-pack** (largest possible batch — 14 controls;
   may want to subdivide into A.7.1-7 perimeter/entry/areas +
   A.7.8-14 equipment/cabling/maintenance for reviewability)
2. **A.8 single-leaf bulk** (large set, mix of spines)
3. **GDPR mixed bulk** (smaller, more curation per control)

The Phase B program is approximately 60-70% complete at this batch
count. A.7 + A.8 + GDPR completion would close out Phase B entirely.
