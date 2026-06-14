# ArionComply — Claude Code Guide

## Project
Compliance RAG platform on Azure VM (172.211.244.144).
Stack: FastAPI + LangGraph + Neo4j + ChromaDB + PostgreSQL + GPT-4o.

## VM Access
```bash
ssh -i ~/.ssh/arioncomplySK.pem arionlabs@172.211.244.144
cd /data/arioncomply
```

## Start / Stop
```bash
# Start API
PYTHONPATH=/data/arioncomply python3 api_server.py > /tmp/api.log 2>&1 &

# Stop API
kill $(lsof -ti:8080) 2>/dev/null

# Check logs
tail -f /tmp/api.log
grep -E "ERROR|WARNING" /tmp/api.log
```

## Run Evals (always run before restarting after code changes)
```bash
PYTHONPATH=/data/arioncomply python3 tests/eval_suite.py \
  --csv results/eval_$(date +%Y%m%d_%H%M).csv --pause 2 \
  2>&1 | grep -E "PASS|FAIL|RESULTS"
# Must be 195/198 PASS before any restart (198 cases; #2 + #24 + #25 known-stale;
#   #3 + #21 + #33 also LLM-stochastic but ~85-95% PASS — not formally known-stale):
#   #24 + #25 — "what is our GDPR Art.32 status?" / "is Art.5 a non-conformity?"
#         (re-authored 2026-06-14 to shape="cross_framework" — verifies at least
#         one ISO bridge ref appears). #24 stochastic (~60-70% pass rate, LLM
#         sometimes drops bridges; sometimes cites a non-canonical bridge like
#         A.5.35 which is valid). #25 consistently failing — Art.5 has its own
#         DerivedSpec posture now, and the LLM answers from that without
#         invoking bridges. Follow-up: prompt or compose-side fix to force
#         bridge enumeration on cross-framework queries. See
#         memory case_24_art32_bridge_followup.md.
#   #2  — "what are our main compliance gaps?" (~40-60% pass rate; LLM-stochastic
#         A.5.26 mention; since Phase C batch 1 / Stage-2 mass-approval session
#         brought Arion to 168 NCs on 2026-06-02 — A.5.26 no longer reliably
#         tops the answer among 168 candidates. Follow-up: case_2_drift_followup.md).
# Any non-#2/#24/#25 regression blocks restart.
# Whenever you add a user-facing feature/fix, append an EvalCase that would
# have failed pre-change and passes post-change — see the feedback-memory rule.
```

## Test Streaming
```bash
curl -s -N "http://localhost:8080/api/v1/chat/stream?question=what+are+our+NC+findings&session_id=test_1" \
  -H "X-API-Key: arion_dev_key_2026"
```

## Test Sync Chat
```bash
curl -s -X POST http://localhost:8080/api/v1/chat \
  -H "X-API-Key: arion_dev_key_2026" \
  -H "Content-Type: application/json" \
  -d '{"question": "what are our NC findings?"}' \
  | python3 -m json.tool
```

## Key Files
api_server.py              — FastAPI server, streaming endpoint, auth
rag/arion_graph.py         — LangGraph pipeline, nodes, checkpointers
rag/llm_answer.py          — LLM answer generation, layered node presentation
rag/classifier.py          — Query classification, CLEAR_INTENT_PHRASES
rag/resolver.py            — Per-taxonomy data source dispatch
rag/graph_expander.py      — Neo4j graph traversal, xfw edge expansion
static/arioncomply.html    — UI (single file, streaming chat)
tests/eval_suite.py        — 21-query evaluation suite

## Architecture
Query → classify node → retrieve node → update_session node → END
↓                ↓
clarify node    (LLM rank_and_answer OR Postgres short-circuit)

### Answer layers
- Layer 1: Primary standard nodes (ISO 27001 with posture NC/OFI/Comply)
- Layer 2: Cross-framework nodes (GDPR xfw edges from Neo4j)
- Short-circuit: document_inventory, scope N/A → direct Postgres answer, no LLM

### Session persistence
- Sync chat: PostgresSaver (arioncomply_sessions DB)
- Streaming: AsyncPostgresSaver (same DB)
- thread_id format: `{tenant_id[:8]}:{session_id}`

## Known Issues to Fix

### 1. Code duplication in rag/arion_graph.py (CRITICAL)
The file contains duplicate definitions of these functions:
- `_is_scope_na_query` (lines ~844 and removed, but verify)
- `_answer_scope_na`
- `make_retrieve_node`
- `make_clarify_node`
- `make_update_session_node`
- `route_after_classify`
- `build_arion_graph`

**How to find duplicates:**
```bash
grep -n "^def " rag/arion_graph.py
```
Any function appearing twice must have the second copy removed.
The FIRST copy of each function is the correct/patched version.
The graph uses the LAST definition — so duplicates shadow fixes.

**Fix approach:** For each duplicate, keep the first definition, remove the second.
After removing duplicates, always run eval (60/62 must pass; #24 + #25 known-stale) before restarting.

### 2. Clarification loop (depends on fix #1)
Query: "what documents are missing?" triggers clarification instead of
routing directly to document_inventory.

Root cause: `make_update_session_node` (second duplicate) doesn't reset
`needs_clarif=False` and `clarif_question=''` — so the next turn still
sees `needs_clarif=True` and loops.

Fix already applied to FIRST copy of `make_update_session_node`:
```python
def update_session(state: ArionState) -> dict:
    return {
        "turn_count":      state["turn_count"] + 1,
        "clarif_count":    0,
        "needs_clarif":    False,
        "clarif_question": "",
    }
```
Once duplicate is removed, this fix will take effect.

### 3. Classifier duplicate pattern (minor)
`rag/classifier.py` has the document_inventory pattern added twice around line 630.
Remove the duplicate entry.

## Databases
```bash
# Compliance data
psql -U arioncomply -h 127.0.0.1 -d arioncomply_compliance

# Session persistence
psql -U arioncomply -h 127.0.0.1 -d arioncomply_sessions

# Key tables
# arioncomply_compliance: posture_controls, api_keys, document_uploads
# arioncomply_sessions: checkpoints (LangGraph state)
```

## Neo4j
```bash
# Check node/edge counts
python3 -c "
from neo4j import GraphDatabase
import os; from dotenv import load_dotenv; load_dotenv('.env')
d = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))
with d.session() as s:
    print('nodes:', s.run('MATCH (n) RETURN count(n) AS c').single()['c'])
    print('rels:', s.run('MATCH ()-[r]->() RETURN count(r) AS c').single()['c'])
"
# Expected: 654 nodes, 778 relationships
```

## Eval Baseline
- Most recent: results/eval_20260602_b26.csv (157 cases — 21 core
  + 18 feature-locked + 2 engine-NC/posture-discipline + 4 calibration multi-leaf
  + 5 Phase B records + 5 Phase B policy_program + 5 Phase B op_process supplier
  + 2 Phase B op_process incident family + 1 Phase B op_process threat-intel +
  1 Phase B op_process evidence-handling + 1 Phase B op_process project-security
  + 1 Phase B op_process return-of-assets + 1 Phase B op_process labelling +
  1 Phase B policy_program information-transfer + 1 Phase B op_process identity
  + 1 Phase B op_process authentication-info + 1 Phase B op_process incident-planning
  + 1 Phase B op_process disruption-security + 1 Phase B op_process ICT-readiness
  + 1 Phase B records_program records-protection
  + 1 Phase B records_program PII-protection
  + 3 Phase B A.5.3x close-out 3-pack records_program
  + 7 Phase B A.6 People Controls 7-pack
  + 14 Phase B A.7 Physical Controls 14-pack
  + 33 Phase B A.8 Technological Controls 33-pack
  + 7 Phase B ISMS chapters 4+5 close-out 7-pack
  + 10 Phase B ISMS chapters 6+7 close-out 10-pack
  + 8 Phase B ISMS chapters 8+9+10 close-out 8-pack — ISO 27001 fully closed
  + 5 Phase B GDPR Chapter II Principles 5-pack — FIRST GDPR BATCH
  + 11 Phase B GDPR Chapter III Rights 11-pack — largest GDPR batch
  + 11 Phase B GDPR Chapter IV core 11-pack — Art.24/25/26/27/28/29/31/32/33/34/35
  + 8 Phase B GDPR Ch IV DPO+codes+cert 8-pack — closes Ch IV
  + 6 Phase B GDPR Ch V Transfers 6-pack — closes Ch V + entire curation arc)
- Score: 195/198 PASS target on 2026-06-03 (#2 + #24 + #25 known-stale).
  Clean-run upper bound is 195/198; lucky runs may hit 196/198 (#24 PASS) or
  197/198 (#24 + #2 both PASS). Cases #3 + #21 + #33 also occasionally fail on
  LLM citation-list position / phrasing — re-runs pass, not known-stale):
  - #25 known-stale since 2026-05-27 (anti-hallucination on "is Art.5 a non-
    conformity?", needs separate fix)
  - #24 known-stale since 2026-05-30 batch 2 (~30-50% pass rate; LLM-stochastic
    on whether Art.32 answer surfaces the A.5-bridge control; was reported as
    PASS in batch 2 commit msg but CSV evidence shows it had already started
    failing — see memory case_24_art32_bridge_followup.md)
  - #2 known-stale since 2026-06-03 (~40-60% pass rate; LLM-stochastic on whether
    A.5.26 surfaces among the top NCs. Drift cause: Phase C batch 1 Stage-2
    mass-approval session brought Arion from ~25 NCs to 168 NCs on 2026-06-02
    — A.5.26 no longer reliably tops the answer among 168 candidates. Data is
    intact; problem is LLM ranking among many NC candidates. Follow-up: see
    memory case_2_drift_followup.md)
- Never deploy with a regression below the current case count
- Cases 22-26 lock in: cited refs in POSTURE_STATUS / STANDARD_KNOWLEDGE,
  xfw posture inheritance, Layer-2 anti-hallucination, uploaded-doc short-circuit
- Cases 27-28 lock in: xfw proposer HITL queue (chat surface + isolation guard)
- Cases 33-36 lock in: Stage-1 HITL surfaces (list / approve / acknowledge)
- Cases 37-38 lock in: Stage-2 HITL surfaces (engine-verdict list / approve)
- Case 39 locks in: [DRAFT] label fix — document_confirmed rows must not be
  hedged via the CONFIRMATION RULE
- Cases 40-41 lock in: engine 0/N → NC (was OFI) + posture-tag-is-the-verdict
- Cases 42-45 lock in: multi-leaf calibrations #2-#5 (A.8.2, A.5.2, Art.30, Art.15)
  via Stage-2 list_one surface — "0/4 children satisfied" reason text PROVES
  the 4-leaf shape end-to-end. Pre-promotion would have been "0/1".
- Cases 46-50 lock in: Phase B records_program 5-pack (A.5.5/6/9/31/32; #48 is
  A.5.9 register/review both freshness=90; #50 is A.5.32 procedure-variant)
- Cases 51-55 lock in: Phase B policy_program 5-pack (A.5.3/4/10/12/15; #51-52
  are matrix + directive primary-leaf variants; #55 is A.5.15 partial-evidence
  OFI 1/4 path — companion to 0/4 default in 46-54)
- Cases 56-60 lock in: Phase B operational_process supplier+cloud 5-pack
  (A.5.19/20/21/22/23; #57 is A.5.20 template variant; #58 is A.5.21 review
  freshness=180; #59 is A.5.22 review-record-shaped variant; #60 is A.5.23
  partial-evidence OFI 1/4 + profile_fact triggering — second partial-evidence
  case in suite after #55)
- Cases 61-62 lock in: Phase B operational_process incident family
  (A.5.25/27; both review freshness for incident-hot controls and uniform-
  procedure-primary shape). A.5.26 also promoted to 4-leaf but NOT eval-
  covered — engine NC at 0/4 verified via direct compute_engine_verdicts()
  but doesn't reach Stage-2 surface because engine agrees with live NC
  (posture_loader.py:343 no-op suppression keeps Stage-2 queue clean)
- Case 63 locks in: Phase B operational_process threat-intel (A.5.7;
  per-product-record lifecycle-end variant — program output IS the
  closure artefact, distinct from triage_decision / incident_closure /
  improvement_action / offboarding / deviation / EOL / exit-migration /
  change-response variants on prior batches; program review freshness
  180d for detection-landscape volatility)
- Case 64 locks in: Phase B operational_process evidence-handling
  (A.5.28; disposal_record lifecycle-end variant — chain-of-custody
  *end*, distinct from per-event / per-product / per-action variants;
  first op_process batch with 365d review freshness — forensic
  discipline doesn't churn like detection/IR/threat-intel; closes the
  incident-evidence triangle alongside A.5.25-27 from batch 4)
- Case 65 locks in: Phase B operational_process project-security
  (A.5.8; closure_record lifecycle-end variant — first OWNERSHIP-
  transferring variant: per-project three-way signoff (sponsor +
  InfoSec + operational owner) with residual-risk register transfer;
  review freshness 365d (stable PM methodology); cross-control links
  to A.8.25/A.8.26 SDLC + A.5.20 supplier + A.5.23 cloud + A.5.27
  lessons)
- Case 66 locks in: Phase B operational_process return-of-assets
  (A.5.11; per-leaver return_record lifecycle-end variant — inclusive
  write-off path captures BOTH confirmed returns AND risk-accepted
  non-returns; new non_return_path MUST surfaces real-world friction;
  review freshness 365d (HR methodology stable); cross-control links
  to A.5.9 asset register + A.8.10 information deletion)
- Case 67 locks in: Phase B operational_process labelling (A.5.13;
  per-platform application_record lifecycle-end variant — proves
  labelling extended to each new system; first cascade-cadence pattern
  (review freshness inherited from A.5.12 parent scheme); new
  pii_overlay MUST pins ISO confidentiality × GDPR PII integration
  at spec level; cross-control links to A.5.12 scheme + A.7.10 media)
- Case 68 locks in: Phase B policy_program information-transfer
  (A.5.14; first policy_program batch since batch 2 — re-validates
  spine consistency after 8 op_process batches; new legal_jurisdiction
  MUST encodes GDPR Chap V Art.44-49 cross-border alignment at MUST
  level — second ISO × GDPR integration MUST after pii_overlay)
- Case 69 locks in: Phase B operational_process identity-management
  (A.5.16; per-identity revocation_record lifecycle-end with **SLA-
  met flag** — auditor-critical proof of the "24h of last day"
  timeliness promise; service_accounts SHOULD → MUST promotion;
  review freshness 180d (high-volume identity drift); cross-control
  links to A.5.11 leaver register, A.5.17 authn info, A.5.18 access
  rights review)
- Case 70 locks in: Phase B operational_process authentication-info
  (A.5.17; per-credential revocation_record lifecycle-end with
  rev_identity_pair MUST that enforces bidirectional A.5.16 ↔ A.5.17
  lifecycle pairing — closes "identity disabled but creds linger"
  gap; MFA SHOULD → MUST promotion (modern baseline, phishable auth
  no longer acceptable); review freshness 180d; cross-control links
  to A.5.16 identity, A.5.25/A.5.26 incident scope-expansion)
- Case 71 locks in: Phase B operational_process incident-planning
  (A.5.24; A.5.24 sits ABOVE the operational A.5.25-27/28 incident
  family — strategic planning layer; per-exercise framework_exercise_
  record lifecycle-end variant tracks READINESS DRILLS distinct from
  real-incident records; third batch with GDPR-required MUSTs — new
  rev_gdpr_72h_feasibility audits the 72h notification SLA empirically;
  third consecutive SHOULD→MUST promotion (tested → exercise_cadence))
- Case 72 locks in: Phase B operational_process disruption-security
  (A.5.29; plan-as-primary variant + per-activation plan_activation_
  record as HYBRID lifecycle-end — covers BOTH real disruptions AND
  scheduled tests via type field; new degradation_levels MUST encodes
  "appropriate level" = graceful degradation explicitly; fourth
  consecutive SHOULD→MUST promotion (test_schedule); cross-control
  links to A.5.7 threat intel, A.5.21 supplier, A.5.22 supplier review,
  A.5.24 IR framework, A.5.26 incident register, A.5.27 lessons,
  A.5.30 ICT readiness)
- Case 73 locks in: Phase B operational_process ICT-readiness (A.5.30;
  plan-as-primary, natural pair with A.5.29; second HYBRID lifecycle-
  end variant — pattern validated as reusable for paired BCP controls;
  new rec_success_status MUST is RTO-met auditor-critical proof
  (analogous to A.5.16 SLA-met flag); new bia_link + bcp_alignment
  MUSTs pin BIA traceability and pair-control coherence; freshness-
  convention cleanup moved freshness_days from plan to review)
- Case 74 locks in: Phase B records_program records-protection (A.5.33;
  first records_program promotion since batch 1 — re-validates spine
  consistency after 11 op_process + 2 policy_program batches in
  between; pairs naturally with the batch 1 records-family A.5.5/6/9/
  31/32; procedure leaf preserves the prior single-leaf id; annual
  review cadence 365d matches the stable-doctrine records-family
  controls A.5.5/A.5.6 (A.5.31 is the regulatory-change-driven 180d
  exception); ITEM-ID PRESERVATION critical — SPEC_ART_5_1_E (GDPR
  Art.5.1.e storage limitation derivation) references four A.5.33
  items by id, all four preserved across the promotion; new
  proc_pii_overlay SHOULD encodes the ISO × GDPR Art.5.1.e
  integration at spec level — third ISO × GDPR integration leaf
  after pii_overlay on A.5.13 + legal_jurisdiction on A.5.14)
- Cases 86-99 lock in: Phase B A.7 Physical Controls 14-pack (batch 22,
  2026-06-01; LARGEST batch yet — 14 controls × 4 leaves = 56 evidence
  requirements; closes the A.7 block). Spine mix: 11×op_process +
  3×policy_program (A.7.1/A.7.7/A.7.9). A.7.14 uses op_process with
  disposal_record lifecycle-end (parallel to A.5.28 evidence-disposal
  pattern). Live postures: 8×N/A (Arion cloud-only) + 4×Comply +
  2×missing-rows; all 14 engine NC 0/4 surface in Stage-2 (engine NC
  differs from live N/A AND live Comply — no agreement suppression).
  No DerivedSpec refs to A.7.x items so item-id preservation trivial.
  Cross-control links: A.7.4 → A.5.26 incident SIEM; A.7.5/A.7.11 →
  A.5.29/A.5.30 BCP; A.7.10 → A.7.14 disposal; A.7.14 → A.5.9 retired
  assets. Compact-style elaboration (5-7 MUSTs per leaf, 1-2 SHOULDs)
  reflects bulk-batch pragmatism vs single-control depth
- Cases 79-85 lock in: Phase B A.6 People Controls 7-pack (batch 21,
  2026-06-01; LARGEST MULTI-CONTROL BATCH YET — 7 controls × 4 leaves
  = 28 new evidence requirements; closes A.6 block, A.6.7 was already
  curated). Spine mix: A.6.1/3/4/5/8 = op_process (procedure-as-
  primary); A.6.2/6 = records_program (template-as-primary). All 7
  engine verdicts NC 0/4; live postures 6×Comply + 1×OFI (A.6.4) all
  flip to engine-proposed NC in Stage-2. No DerivedSpec refs to A.6.x
  items so item-id preservation trivial. Cross-control links: A.6.5
  is the contractual layer above operational A.5.11/A.5.16/A.5.17/
  A.5.18 offboarding; A.6.8 → A.5.25 triage handoff; A.6.2 + A.6.6
  together form personnel info-security contract package; A.6.4
  cross-links to A.5.36 nonconformity register
- A.5.18 Style v2 alignment (2026-06-01, batch 20 — closes A.5 arc):
  NOT a promotion (A.5.18 was already 4-leaf op_process from 2026-05-26,
  predates Phase B numbered batches). Brings A.5.18 up to A.5.16/A.5.17
  identity-family modern conventions: review freshness 365→180d, new
  rev_sla_met MUST (auditor-critical "24h of role-change" proof), new
  rev_identity_pair MUST (bidirectional A.5.16↔A.5.18 lifecycle pairing),
  new rev_residual_cleanup MUST (mailbox/file-share/group cleanup),
  reg_idmgmt_link promoted SHOULD→MUST, 6 new MUSTs total + 3 new
  SHOULDs, elaborate descriptions. All 17 existing item-ids preserved.
  No new eval case — engine NC == live NC → Stage-2 suppression
  (A.5.26 precedent). Cases #1 + #2 still PASS (live posture unchanged).
  A.5 Organisational Controls arc now FULLY ALIGNED — every A.5 control
  multi-leaf at modern Style v2 conventions
- Cases 76-78 lock in: Phase B A.5.3x close-out 3-pack records_program
  (A.5.35/A.5.36/A.5.37; FIRST MULTI-CONTROL BATCH SINCE BATCH 4 —
  pattern locked in, batches can bundle conceptually-related controls;
  closes the A.5.3x review/procedure block and the full A.5
  organisational controls arc that started with case #46 batch 1.
  A.5.35 = review-record-as-primary variant same shape as A.5.22
  supplier review (independent_review_report + schedule_register +
  program_meta_review + finding_response_register lifecycle-end);
  A.5.36 = batch-mate of A.5.35 (compliance_review_record + schedule
  + program_meta_review + nonconformity_register lifecycle-end —
  reviews COMPLIANCE WITH policies vs A.5.35's review of the FUNCTION);
  A.5.37 = register-as-primary variant same shape as A.5.9 asset
  register (operating_procedures_register + maintenance_procedure +
  applicable_facilities_scope + program_review). Per-record
  freshness=365 on A.5.35/A.5.36 primary leaves. New
  significant_change_check MUST on A.5.35 enforces 27002 §5.35's
  "or on significant change" explicit consideration. New
  pgm_method_review MUST on A.5.36 audits "rubber-stamping" failure
  mode. New rev_accuracy_sample MUST on A.5.37 prevents "documented
  but wrong" drift. Cross-control links: A.5.35 ↔ A.5.36 finding
  registers can share infrastructure; A.5.37 → A.5.9 asset register;
  A.5.37 → A.5.24/26/29/30 incident + DR procedures)
- Case 75 locks in: Phase B records_program PII-protection (A.5.34;
  natural pair with A.5.33 — A.5.33 protects records, A.5.34 protects
  the PII subset; PARTIAL-EVIDENCE shape — third such case after #55
  (A.5.15) + #60 (A.5.23), engine sits at OFI 1/4 because Arion's
  legacy privacy-policy upload satisfies the policy leaf via
  semantic matching but the three new leaves carry no evidence yet;
  ITEM-ID PRESERVATION TWO-WAY — SPEC_ART_24 (controller responsibility)
  references 5 A.5.34 items, SPEC_ART_25 (DPbD) references 4; combined
  set of 7 unique items (overlap on :applicable_laws +
  :security_controls_ref) ALL preserved; new transfer_restrictions
  MUST encodes GDPR Chap V at MUST level — fourth ISO × GDPR
  integration MUST after A.5.13 pii_overlay, A.5.14
  legal_jurisdiction, A.5.33 proc_pii_overlay; new owner MUST + 4th
  SHOULD pims_alignment encode the ISO/IEC 27701 PIMS extension
  where in scope)
- Cases 193-198 lock in: Phase B GDPR Ch V Transfers 6-pack (batch 30,
  2026-06-02; FINAL BATCH OF THE CURATION ARC). All op_process 4-leaf.
  Art.44 transfer principle universal; Art.45 adequacy profile_fact;
  Art.46 SCCs/safeguards profile_fact; Art.47 BCRs profile_fact;
  Art.48 foreign authority universal; Art.49 derogations profile_fact.
  Transfer mechanism hierarchy + Schrems II TIA + EDPB 01/2020
  supplementary measures + EDPB 2/2018 derogation strict-construction
  all encoded in MUSTs. Arion posture: 4 OFI (Art.44/45/46/48 — uses
  US-hosted cloud informal mechanisms) + 2 N/A (Art.47/49 no BCRs no
  derogations). **PHASE B CURATION ARC COMPLETE** — ISO 27001 + GDPR
  fully multi-leaf at Style v2
- Cases 185-192 lock in: Phase B GDPR Ch IV DPO + codes + certification
  8-pack (batch 29b, 2026-06-02). All 8 op_process profile_fact 4-leaf.
  Art.36 prior consultation; Art.37/38/39 DPO cluster (designation +
  position + tasks); Art.40/41 codes of conduct (adherence + monitoring
  body); Art.42/43 certification (scheme + cert body). Most uniform
  spine batch — every spec same shape, no promotions/expansions.
  Arion posture: 6 N/A + 3 OFI (CISO informal DPO without formal Art.37
  designation despite likely Art.37.1.b applicability). GDPR Ch IV
  FULLY CLOSED (19 articles across 29a + 29b)
- Cases 174-184 lock in: Phase B GDPR Chapter IV core 11-pack (batch 29a,
  2026-06-02). 3 DerivedSpec expansions (Art.24 0→4 direct = 10 children;
  Art.25 1→4 = 10; Art.32 1→4 = 9) + 2 promotions (Art.28 DPA + Art.33
  breach-to-SA both → 4-leaf, primary ids preserved) + 6 new specs
  (Art.26/27/29/31/34/35). Spine: 1×policy_program + 7×op_process +
  3×DerivedSpec expansion. **Art.24 is FIRST DerivedSpec to go from 0 to
  4 direct_evidence in one batch** — 10-child verdict (largest verdict
  surface). Art.26+Art.27 N/A on Arion (no joint controllers, EU
  established). GDPR Ch IV core CLOSED; Art.36-43 deferred to batch 29b
- Cases 163-173 lock in: Phase B GDPR Chapter III Data Subject Rights
  11-pack (batch 28, 2026-06-02; LARGEST GDPR batch). Art.12 + Art.13
  promote + Art.14 + Art.16 expand + Art.17 expand + Art.18 + Art.19 +
  Art.20 + Art.21 + Art.22 + Art.23. Three structural patterns in one
  batch: EvidenceRequirement promotion (Art.13), DerivedSpec expansion
  (Art.16 1+4=5 children; Art.17 2+4=6 children), new 4-leaf specs
  (Art.12/14/18/19/20/21/22/23). Spine: 2×policy_program + 7×op_process +
  2×DerivedSpec expansion. Primary-leaf ids preserved: req:Art.13:
  privacy_notice + req:Art.16:rectification_procedure + req:Art.17:
  erasure_procedure. profile_fact+N/A applied to Art.22+Art.23.
  GDPR Ch III FULLY CLOSED (12/12 inc. Art.15)
- Cases 158-162 lock in: Phase B GDPR Chapter II Principles 5-pack
  (batch 27, 2026-06-02; FIRST GDPR BATCH after ISO 27001 fully closed).
  Art.6 (Lawfulness) — DerivedSpec expanded from 1 direct_evidence to
  4 = 6 children total (2 ISO deps + 4 direct). Art.7 (Consent) new
  op_process 4-leaf universal. Art.8/9/10 (Children / Special category /
  Criminal convictions) new op_process 4-leaf profile_fact. **TWO
  STRUCTURAL PATTERNS established for GDPR**: (1) DerivedSpec
  expansion — add direct_evidence inline to SPEC_*.direct_evidence,
  NOT to ALL_EVIDENCE_REQUIREMENTS; engine reports "0/N children
  satisfied" where N = deps + direct. (2) profile_fact + live N/A —
  when tenant narrative excludes the profile fact (e.g. B2B no
  minors), live posture set to N/A; engine still proposes NC because
  spec is empty; surfaces in Stage-2 as a 'did-you-really-mean-N/A?'
  checkpoint (engine-agreement specifically NC==NC, so N/A surfaces).
  Posture seed: Art.6 + Art.7 OFI, Art.8/9/10 N/A
- Cases 150-157 lock in: Phase B ISMS chapters 8+9+10 close-out 8-pack
  (batch 26, 2026-06-02; 8 controls × 4 leaves = 24 new evidence requirements;
  closes ISMS chapters 8 + 9 + 10 — FINAL ISO 27001 BATCH). Most uniform
  single-batch spine — all 8×op_process. Primary-leaf ids preserved:
  req:9.2:internal_audit_programme + req:9.3:management_review. NEW
  freshness conventions: 8.3 review=180d (operational tempo); 9.1
  measurement_record=90d FIRST freshness=90 in ISMS clauses (faster-data /
  slower-meta pattern). LOAD-BEARING REGEX BUG FIX in stage1/stage2/
  acknowledge_chat — control-ref pattern `\d\.\d+` failed on 10.1/10.2;
  changed to `\d+\.\d+`. **ISO 27001 FULLY CLOSED** — Annex A 93/93 +
  ISMS clauses 25/25 = 118 multi-leaf. Next: GDPR
- Cases 140-149 lock in: Phase B ISMS chapters 6+7 close-out 10-pack
  (batch 25, 2026-06-02; 10 controls × 4 leaves = 30 new evidence
  requirements; closes ISMS chapters 6 + 7). Most diverse single-batch
  spine mix to date: 6×op_process (6.1.1/6.1.2/6.1.3/6.3/7.3/7.4) +
  3×records_program (6.2/7.1/7.2) + 1×policy_program (7.5). Primary-leaf
  ids preserved: req:6.1.2:risk_assessment + req:6.1.3:risk_treatment_plan
  (anchor REQs from 2026-05-22). NEW SoA leaf — Statement of
  Applicability promoted from a should_contain item to its own distinct
  sibling leaf on 6.1.3 with 7 MUSTs (mandatory under 6.1.3 c-d). Pattern
  established: any clause-mandated specific-named artefact distinct from
  the primary deserves its own leaf, not a should_contain item. 10
  posture rows seeded with finding='OFI' matching Arion's pre-ISMS
  narrative
- Cases 133-139 lock in: Phase B ISMS chapters 4+5 close-out 7-pack
  (batch 24, 2026-06-02; 7 controls × 4 leaves = 28 new evidence
  requirements; closes ISMS chapters 4 + 5). FIRST management-system
  clauses (vs Annex A controls) promoted to 4-leaf. Spine mix:
  2×records_program (4.1+4.2 register-as-primary) + 5×policy_program
  (4.3/4.4/5.1/5.2/5.3 with scope/manual/directive/policy/matrix as
  primary). Primary-leaf ids preserved: req:4.3:isms_scope +
  req:5.2:information_security_policy + all item:4.3:* / item:5.2:* ids
  (anchor REQs since 2026-05-22). NEW PREREQUISITE STEP for ISMS clauses:
  workbook_importer doesn't cover clauses 4-10, so posture_controls rows
  must be SEEDED before engine surface can fire (rows for 4.1-4.4 missing
  entirely on Arion; 5.1-5.3 existed but inactive). Seeded with
  finding='OFI' matching Arion's pre-ISMS narrative (verbal commitment,
  informal scope notes, privacy policy in place, CISO appointed; no
  formal ISMS artefacts). Engine NC 0/4 surfaces in Stage-2 for all 7
  (engine NC ≠ live OFI). Same posture-seed step needed for batches 25 +
  26 (18 more ISMS clauses across chapters 6-10)
- Prior known-stale cases (#2, #3, #4, #24, #25, #28) restored to PASS on
  2026-05-25 via Path A: replayed status_before from posture_status_log to
  revert the 27 Stage-1-driven finding mutations, and stripped the offending
  UPDATE from stage1_review_chat.py (commit d6329c4). Stage-1 now only
  confirms evidence; engine + Stage-2 own posture. #24 regressed again
  2026-05-30 (separate cause from the Stage-1 fix; xfw context injection).
- TODO: add case for incident obligations once the chat surface (commit 40ad607)
  exposes a non-clarification answer path
- TODO: add case for SPEC_ART_25 (GDPR Art.25 DPbD DerivedSpec, 6 deps + 1 direct
  evidence leaf). Engine→chat wiring landed 2026-05-25 (commit 9ac0ac3); the
  prerequisite is now met but the regression test still needs writing.

## Git
```bash
git add -A
git commit -m "description"
git push origin main
```
