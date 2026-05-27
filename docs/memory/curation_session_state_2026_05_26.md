---
name: curation-session-state-2026-05-26
description: "Paused mid-session 2026-05-26. Calibration #1 (A.5.18) shipped; #2 (A.8.2) drafted not loaded; #3-5 not started. Event↔EvidenceRequirement coupling resolved 2026-05-27 (trigger_event removed; Event.requires_evidence is source of truth). Next: resume calibration #3 (A.5.2)."
metadata: 
  node_type: memory
  type: project
  originSessionId: ff756701-cb76-4bff-81bd-53541186dace
---

Session paused 2026-05-26 mid-calibration. Pick up here.

**What shipped during the session:**

1. **Test-fixture sweep** — 13 docs / 19 findings soft-deleted (`is_active=FALSE` on both client_documents and document_findings). Patterns cleaned: `_idem_layer2_a_*`, `_test_table_only_*`, pure-UUID-named docs. Affected verdicts: A.5.18, A.5.30, Art.5, Art.32 (no longer spuriously satisfied by these). Stage-2 queue size unchanged at 95 — same controls, more honest verdicts.

2. **Calibration #1 — A.5.18 promoted from single-leaf to 4-leaf** (`operational_process` spine). Loaded to Neo4j. Engine now reads `NC, 0/4 satisfied` (was `Comply, 1/1` against stale fixtures). Leaves:
   - `req:A.5.18:access_rights_procedure` (procedure) — id preserved from old single-leaf
   - `req:A.5.18:access_rights_register` (register)
   - `req:A.5.18:access_rights_review` (review_record, freshness 365)
   - `req:A.5.18:access_revocation_record` (revocation_record)
   Citations: ISO 27002:2022 § 5.18 a–k in `rationale` fields.

3. **Style v2 header at `enrichment/documents/document_requirements.py:623`** — multi-leaf is now default; supersedes the 2026-05-22 single-leaf rule. 5-spine model recorded inline.

**What's drafted but NOT loaded to Neo4j:**

- **Calibration #2 — A.8.2** (technical_control spine, 4 leaves). In `document_requirements.py` and registered in `ALL_EVIDENCE_REQUIREMENTS`. Module imports cleanly. Awaiting Neo4j load:
   - `req:A.8.2:privileged_access_baseline` (configuration_baseline)
   - `req:A.8.2:privileged_access_procedure` (procedure) — id preserved from old single-leaf
   - `req:A.8.2:privileged_activity_log` (monitoring_record)
   - `req:A.8.2:privileged_access_recertification` (review_record, freshness 180)

**What's NOT drafted yet:**

- **Calibration #3 — A.5.2** (policy_program spine, 4 leaves). Edit was started but rejected by user when they paused. Plan was: keep `req:A.5.2:roles_and_responsibilities` (responsibility_matrix) and add approval, communication_record, review_record siblings. Note: confirms the spine is a governance wrapper — artifact type can be `responsibility_matrix`, not specifically `policy`.
- **Calibration #4 — Art.30** (gdpr_principle adapted for records-driven article, 4 leaves). NOT Art.5 — that's already curated as 8 sub-article DerivedSpecs. Plan: existing `req:Art.30:records_of_processing` as the register leaf + RoPA Maintenance Procedure + Data Flow Inventory + RoPA Annual Review.
- **Calibration #5 — Art.15** (gdpr_rights, 4 leaves). Existing `req:Art.15:dsar_response` is `trigger_type=operational` — keep it as L2. Add DSAR Handling Procedure (universal) + DSAR Register (universal) + DSAR Process Review (universal).

**Why we paused — the holistic model audit:**

User asked to verify the curation isn't duplicating prior obligations/events work. Audit confirmed **three orthogonal layers, no abstract duplication**:

- **Applicability layer**: ClientFact (22) + ObligationRule (18) — "does this control apply to this tenant?"
- **Occurrence layer**: Event (11) + ClassificationDimension (2) + ClassificationValue (11) — "what fires when something happens?"
- **Evidence layer**: RequirementNode (429) + FulfilmentSpec (429) + EvidenceRequirement (134) + ChecklistItem (986) — "what document proves this control?"

Multi-leaf curation extends only the evidence layer. No changes needed to applicability or occurrence layers for curation work.

**One redundancy resolved 2026-05-27:**

The Event↔EvidenceRequirement link was stored as dual code-level fields. Resolution: kept `Event.requires_evidence: list[str]` as the source of truth and removed `EvidenceRequirement.trigger_event` entirely (dataclass field + all 47 `trigger_event=None` instance kwargs in `enrichment/documents/document_requirements.py`; loader writes + property cleanup in `enrichment/documents/load_to_neo4j.py` via `REMOVE r.trigger_event` on the MERGE pass). Neo4j reload cleared the property from all 134 EvidenceRequirement nodes. No Neo4j edge added — the list[str] on the Event side is the single source.

Eval after change: 40/41 effective (only pre-existing #25 still fails; #8 + #21 transient flakes on the suite run, both verified PASS on manual retry). Same eval run also bumped #31 FAIL→PASS as a side effect of loading the Art.5 umbrella spec backlog.

Followup: convert `Event.requires_evidence` to a proper Neo4j edge `(:Event)-[:REQUIRES_EVIDENCE]->(:EvidenceRequirement)` if/when the graph needs traversal in that direction. Not load-bearing yet.

**Resume order when session restarts:**

1. Resume calibration #3 (A.5.2 — already partially designed in conversation; edit was rejected only because of the pause, not because of substance).
2. Calibration #4 (Art.30), #5 (Art.15).
3. Then commit + push the calibration batch + load to Neo4j + re-run engine to see all five spines on Arion.
4. Only after all 5 spines validated, scale via LLM-drafted bulk curation per the program in [[curation-program-full-multi-leaf]].

**Open data hygiene items NOT addressed this session:**

- `document_uploads` (staging table) test-fixture sweep — engine doesn't read it, but UI history surfaces may show stale rows.
- Stage-2 queue contains 1 no-op proposal (A.5.18, where engine NC = live NC). Either auto-approve when engine agrees with live, or filter no-ops out of the surface. Minor.
- 111 "PIMS"-excerpt approved findings (per [[stage1-contract-change-path-a-2026-05-25]]) still pending mass-rejection. Unrelated to this session's work but on the active list.
