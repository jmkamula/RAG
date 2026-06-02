---
name: curation-phase-b-batch-29b-2026-06-02
description: Phase B batch 29b — GDPR Ch IV DPO + codes + certification 8-pack. All 8 op_process profile_fact 4-leaf. Closes GDPR Ch IV. Most uniform spine batch — every spec same shape.
metadata: 
  node_type: memory
  type: project
  originSessionId: 88fd2fe5-4a85-43e3-a226-722db223d304
---

Phase B batch 29b — GDPR Chapter IV close-out. Art.36 prior consultation +
Art.37/38/39 DPO cluster + Art.40/41 codes + Art.42/43 certification.
8 articles, all new 4-leaf op_process profile_fact. 32 new evidence
requirements.

**Why:** User chose to split Ch IV into 29a (core, 11 articles) + 29b
(DPO + codes + cert, 8 articles, this batch) because these latter 8 are
mostly profile_fact / N/A for typical tenants. After 29b lands, Ch IV
fully closes and only Ch V Transfers remains (batch 30).

**How to apply:** Most uniform batch yet — all 8 specs follow the same
shape (op_process 4-leaf, profile_fact triggered). No DerivedSpec
expansions, no promotions, no spine variation. Just 8 fresh specs with
the standard 4-leaf shape.

The DPO trio (Art.37/38/39) is conceptually tightly coupled. They
COULD be merged into a single 12-leaf spec or kept separate. Kept
separate per the per-article curation principle — each article has
distinct demonstrability surface (designation document vs position
guarantees vs activity register).

**Shipped (commit pending — current session 2026-06-02):**

- Art.36 (prior consultation): consultation_procedure + register +
  applicable_scope + program_review. 8-week SA waiting period (Art.36.2)
  enforced in procedure MUST. Profile_fact: triggered by Art.35 DPIA
  flagging residual high risk.

- Art.37 (DPO designation): designation_procedure + designation_record
  + applicable_scope + program_review. Applicability assessment per
  Art.37.1 a-c criteria + Art.37.4 voluntary route + Art.37.5
  qualifications + Art.37.7 publication.

- Art.38 (DPO position): position_procedure + evidence_register +
  applicable_scope + program_review. Position guarantees: involvement,
  resources, independence, no COI. Quarterly evidence-register cadence
  for board attendance, budget approval, independence signals.

- Art.39 (DPO tasks): tasks_procedure + activity_register +
  applicable_scope + program_review. Art.39.1 a-e tasks operationalised;
  Art.39.2 risk-based prioritisation explicit.

- Art.40 (codes of conduct): adherence_procedure + adherence_register
  + applicable_scope + program_review. Profile_fact: org adheres to
  an approved code.

- Art.41 (monitoring of codes): monitoring_procedure + monitoring_record
  + applicable_scope + program_review. Profile_fact: org IS the
  accredited monitoring body (very rare).

- Art.42 (GDPR certification): certification_procedure + register +
  applicable_scope + program_review. Max 3-year validity (Art.42.7)
  in MUST.

- Art.43 (certification bodies): body_procedure + issuance_record +
  applicable_scope + program_review. Profile_fact: org IS an accredited
  cert body (extremely rare).

**Posture seed (Arion):**
- Art.36: N/A (no residual-high-risk DPIA yet)
- Art.37/38/39: OFI (CISO performs DPO-like functions informally; no
  formal designation despite likely Art.37.1.b applicability given
  Arion's compliance-RAG product systematically monitors organisational
  data. Formal Art.37 designation flagged as a real gap for the
  product narrative)
- Art.40/41/42/43: N/A (not adhering to a code, not a monitoring body,
  not seeking GDPR cert, not a cert body)

ENGINE VERDICTS: all 8 propose NC 0/4 (engine NC ≠ live OFI / N/A).

EVAL CASES ADDED (185-192): 8 cases all probing `0/4 children satisfied`.

**Item-id preservation:** All 8 specs are new — no preservation concerns.

**Spine variant mix:** 8×op_process. Most uniform single-batch spine
since batch 26 (ISO 8/9/10 — also all op_process).

**Cross-article web:**
- Art.36 → Art.35 DPIA (trigger: residual high risk after mitigations)
- Art.37 ↔ Art.38 ↔ Art.39 (DPO trio — designation enables position
  enables tasks)
- Art.37 → privacy notice (Art.13.1.b / 14.1.b — DPO contact published)
- Art.38 → Art.39 (position guarantees enable task performance)
- Art.39 → Art.31 (DPO is the SA cooperation contact point); → Art.35
  (DPO provides DPIA advice); → Art.36 (DPO involved in prior
  consultation)
- Art.40 → Art.41 (adherence body engages monitoring body)
- Art.40 → Art.46.2.e (codes may be transfer safeguard)
- Art.42 → Art.43 (certification scheme issued by cert body)
- Art.42 → Art.46.2.f (cert may be transfer safeguard)

**Three insights from the Ch IV close-out batch:**

1. **8 profile_fact + 6 N/A is a real-world realistic posture for a
   B2B SaaS tenant.** Arion's batch-29b posture shape (6 N/A out of 8)
   reflects how many controllers/processors approach Ch IV — most of
   these obligations only fire for specific organisational shapes
   (public authority, monitoring body, cert body) or specific risk
   profiles (high-risk DPIA → prior consultation). The product surface
   "engine proposes NC, you said N/A — affirm?" gives the reviewer
   defensibility without paperwork burden.

2. **The DPO trio reveals a curation tension.** Art.37/38/39 cover
   designation / position / tasks. They could be one 12-leaf spec or
   three 4-leaf specs. Chose three for: per-article surface alignment,
   easier engine verdict granularity (Art.38 position guarantees might
   degrade independently of Art.39 task performance), per-article
   evaluability against EDPB guidelines that themselves split by
   article. Tradeoff: 3× more leaves to fail at audit. Pragmatic
   alternative would be a DerivedSpec aggregating the three — explored
   if/when product feedback warrants.

3. **Art.40-43 codes/cert specs are 'compliance optionality' surfaces.**
   These articles don't impose universal obligations — they describe
   voluntary mechanisms that controllers/processors MAY adopt
   (codes) or MAY pursue (certification). Curating them gives the
   product the ability to surface them as opportunities ("you could
   adhere to Cloud Code of Conduct for additional transfer safeguards")
   rather than gaps. Most tenants will sit at N/A; the few who DO
   adopt benefit from the per-spec demonstrability surface.

**Where this leaves the curation arc (post batch 29b):**
- ISO 27001: fully closed
- GDPR Ch II Principles: closed (batch 27)
- GDPR Ch III Rights: closed (batch 28)
- GDPR Ch IV Controller/Processor: FULLY CLOSED (batches 29a + 29b — 19
  articles total: Art.24/25/26/27/28/29/30/31/32/33/34/35/36/37/38/39/40/
  41/42/43)
- GDPR Ch V Transfers: ~6 articles remaining for batch 30 (Art.44-49) —
  FINAL batch of the curation arc

**Next batch (batch 30 — GDPR Ch V Transfers, FINAL):**
- Art.44 (general principle for transfers)
- Art.45 (adequacy decision)
- Art.46 (appropriate safeguards: SCCs, BCRs, codes, certification)
- Art.47 (binding corporate rules)
- Art.48 (transfers not authorised by EU law)
- Art.49 (derogations for specific situations)

All 6 are op_process. Mix of universal (Art.44/48) + profile_fact
(Art.45/46/47/49 — apply to specific transfer mechanisms in use).
Most B2B SaaS using AWS / Azure / GCP outside EU will have Art.44 +
Art.46 in scope (SCCs).

See also: [[curation-phase-b-batch-29a-2026-06-02]] (Ch IV core),
[[curation-phase-b-batch-28-2026-06-02]] (Ch III), [[curation-phase-b
-batch-27-2026-06-02]] (Ch II, established profile_fact + N/A pattern).
