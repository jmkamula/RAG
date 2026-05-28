---
name: curation-program-full-multi-leaf
description: "Full multi-leaf curation of all ISO 27001 controls + all GDPR articles. Decided 2026-05-26. Supersedes the 2026-05-22 'single-leaf where applicable' style. ISO 27002 + EDPB as cited authority; user is sole reviewer."
metadata: 
  node_type: memory
  type: project
  originSessionId: ff756701-cb76-4bff-81bd-53541186dace
---

User directive 2026-05-26: every ISO 27001:2022 control (126) and every GDPR 2016/679 article (303) must be curated to multi-leaf FulfilmentSpec depth, matching the A.5.1 pattern (policy + approval + communication_record + review_record, with MUST items per leaf).

**Why:** Stage-2 verdicts and "what evidence do we need to be compliant" queries lose credibility when most controls have one leaf or zero. Today: 1 multi-leaf, 127 single-leaf, 301 empty out of 429 specs. The thin ones force the engine into binary 1-of-1 verdicts against artificially narrow criteria; the 94 Stage-2 proposals from commit 0877f3b are the symptom.

**How to apply:**
- **Sources of authority (decided):** ISO 27002:2022 implementation guidance for ISO controls; article text + EDPB guidelines for GDPR. Every leaf and every MUST item must trace to a clause/paragraph in one of these. Add a `source_citation` style to the curation (today's `rationale` field already carries short citations like "A.5.1 — communicated"; extend with the 27002 / EDPB clause where it isn't already obvious).
- **Reviewer:** user, sole. LLM may draft from authoritative source text; user accepts/edits/rejects per control. Cadence at solo review is ~5-10 controls/day.
- **Style override:** the file header at `enrichment/documents/document_requirements.py:623-632` ("Single leaf per control where the obligation is a single document type") is **superseded**. New rule: every curated control gets a multi-leaf spec; single-leaf only acceptable when the obligation truly has one document class (rare — needs explicit justification in the description field). The 117 existing single-leafers join the 301 empties as Phase B work.
- **Spine model (to be ratified):** five proposed canonical spines so leaf names don't drift across 429 specs —
    - `policy_program` (e.g., A.5.1): policy, approval, communication_record, review_record
    - `operational_process` (e.g., A.5.18): procedure, process_record/register, review_record, (sometimes) policy if no sibling control owns it
    - `technical_control` (e.g., A.8.\*): configuration_baseline, procedure/work_instruction, test_log, monitoring_record
    - `gdpr_rights_article` (e.g., Art.15-22): procedure, response_record/register
    - `gdpr_principle_article` (e.g., Art.5, Art.32): policy_or_notice, register, dpia (when applicable), review_record
  Ratify before scaling — expect 1-2 spines to be added or renamed during the calibration walk-through.
- **Calibration first:** before bulk drafting, hand-curate 5 controls covering all spines as worked examples: A.5.18 (operational_process), A.8.2 (technical_control), GDPR Art.5 (gdpr_principle), Art.15 (gdpr_rights), and one policy_program that isn't A.5.1 (e.g., A.5.2 or A.5.31). User reviews. Spine model gets adjusted from what we learn. Only then scale.
- **Phase B (from [[posture-engine-alignment-plan-2026-05-22]]) is reframed:** target is now ~418 specs (117 thin + 301 empty), not 410. Scope nearly doubles in difficulty because re-curating a thin spec needs more care than filling an empty one (existing leaf id stays stable, ids of new sibling leaves must not collide, and the engine's current verdict on the control will flip when new leaves are added — expect Stage-2 queue churn during the migration).

**Open design calls during calibration:**
- When a leaf's natural document IS another control's primary artifact (e.g., A.5.18's "Access Control Policy" really lives at A.5.15), reference vs duplicate? Default: reference via SHOULD item, don't duplicate the leaf.
- `freshness_days` defaults per leaf type (review_record ~365, register no freshness, configuration_baseline ~365 or per change-control rhythm).
- Whether to introduce a sixth spine for **records-only controls** (e.g., A.5.27 lessons learned register, A.6.5 termination/change records).
