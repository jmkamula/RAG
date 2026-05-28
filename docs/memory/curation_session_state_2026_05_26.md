---
name: curation-session-state-2026-05-26
description: "SHIPPED 2026-05-28 (commit 13e44ad): calibration batch #2-#5 complete (A.8.2, A.5.2, Art.30, Art.15 all promoted to 4-leaf). Ratifies 5-spine model + adds records_program as sixth spine candidate. Ready for Phase B bulk drafting."
metadata: 
  node_type: memory
  type: project
  originSessionId: ff756701-cb76-4bff-81bd-53541186dace
---

**Status (2026-05-28):** SHIPPED in commit 13e44ad. The full calibration arc that started 2026-05-26 (after A.5.18 shipped in 9771185) is now complete. Five controls are now 4-leaf curated.

**Shipped calibrations:**

| # | Control | Spine | Engine on Arion | Stage-2 |
|---|---|---|---|---|
| 1 | A.5.18  | operational_process | NC, 0/4 | proposed (no-op vs live NC) |
| 2 | A.8.2   | technical_control | NC, 0/4 | proposed *(live Comply → NC flip)* |
| 3 | A.5.2   | policy_program *(governance-wrapper variant: responsibility_matrix, not policy)* | NC, 0/4 | proposed *(live OFI → NC flip)* |
| 4 | Art.30  | **records_program** *(new sixth spine candidate)* | NC, 0/4 | proposed |
| 5 | Art.15  | gdpr_rights *(expanded 2 → 4 leaves)* | NC, 0/4 | proposed |

Calibration #1 (A.5.18) was shipped earlier in commit 9771185; the bulk of this memo's batch (#2-#5) shipped in commit 13e44ad. Together they ratify the 5-spine model + add records_program as a sixth.

**Spine model after calibration:**

| Spine | Worked example | Leaves |
|---|---|---|
| policy_program | A.5.1, A.5.2 | policy/matrix, approval, communication, review |
| operational_process | A.5.18 | procedure, register, review, revocation |
| technical_control | A.8.2 | baseline, procedure, monitoring, recertification |
| gdpr_rights | Art.15 | procedure, register, response *(operational)*, review |
| gdpr_principle_article | (not yet calibrated) | policy/notice, register, dpia where applicable, review |
| **records_program (new)** | Art.30 | register, maintenance procedure, upstream inventory, review |

**Test-fixture sweep (2026-05-26):** 13 docs / 19 findings soft-deleted (`is_active=FALSE` on both client_documents and document_findings). Patterns cleaned: `_idem_layer2_a_*`, `_test_table_only_*`, pure-UUID-named docs. Stage-2 queue size unchanged at 95 — same controls, more honest verdicts.

**Loader hygiene (2026-05-28 discovery):** every multi-leaf promotion creates orphan ChecklistItems because `load_to_neo4j.py` uses MERGE only. This batch cleaned 19 orphans manually across A.5.18, A.5.2, A.8.2, Art.30, Art.15. Follow-up tracked in [[loader-orphan-cleanup-followup]] — extend loader with per-leaf declarative pruning (option b). Until shipped, the audit + DETACH DELETE pattern from this session is the manual fallback.

**Event↔EvidenceRequirement coupling (resolved 2026-05-27):** `EvidenceRequirement.trigger_event` removed in commit 9771185 — `Event.requires_evidence` is the single source of truth. The redundancy noted in the original memo is gone.

**Stage-1 contract change overlap:** Path A was shipped out of sequence 2026-05-25 (commit d6329c4, see [[stage1-contract-change-path-a-2026-05-25]]) — Stage-1 no longer mutates posture, so the engine + Stage-2 verdict proposals from this batch land cleanly with no Stage-1 interference.

**Next pickup — Phase B bulk drafting:**

With the 5-spine model ratified + a sixth identified, the calibration baseline is locked. The path forward per [[curation-program-full-multi-leaf]]:

1. LLM-drafted bulk curation of the remaining ~414 specs:
   - 112 single-leaf ISO controls to promote (117 thin total − 5 calibrated)
   - 297 empty GDPR articles to fill (303 total − 6 already curated through derived chains)
   - Group by spine; user reviews per family at ~5-10/day solo pace.
2. Before each multi-leaf promotion: audit + clean orphans per the loader-orphan-cleanup-followup pattern, until that follow-up ships.
3. Add EvalCases for calibrations #2-#5 (currently the eval suite only covers A.5.18 implicitly via case #5) — per the feedback-eval-with-each-feature rule, each should have a regression case before bulk Phase B starts.

**Open data hygiene items NOT addressed this session:**

- `document_uploads` (staging table) test-fixture sweep — engine doesn't read it, but UI history surfaces may show stale rows.
- 111 "PIMS"-excerpt approved findings (per [[stage1-contract-change-path-a-2026-05-25]]) still pending mass-rejection. Unrelated to this batch's work but on the active list.
- Pre-existing eval case #25 (`is GDPR Art.5 a non-conformity?`) failure carried from 2026-05-27 — independent from this batch, needs its own investigation. Anti-hallucination rule from commit 432605c is not firing as expected.
