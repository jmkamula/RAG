---
name: applies-when-warning-suppression
description: "Neo4j 01N52 'property key does not exist' on applies_when — SUPPRESSED 2026-05-20 at engine driver via notifications_disabled_classifications=['UNRECOGNIZED']"
metadata: 
  node_type: memory
  type: project
  originSessionId: ab2912f3-a587-4819-891f-14d62eba574c
---

Neo4j emits `01N52 property key does not exist (applies_when)` on every `compute_engine_verdicts` call because `spec_builder.py` queries reference the property but **0 of 429** FulfilmentSpec nodes and **0 of 25** REQUIRES_EVIDENCE edges currently carry it. The migration created them with `applies_when: NULL`, which in Cypher is equivalent to "property absent" — hence the warning.

**Why:** Phase-1 ship-with-DSL-but-no-rules is intentional (see [[applies-when-phase1-regression-tests]]). The warning is expected behavior, not a defect, but it spams the log on every engine sweep. Persistent low-signal warnings train responders to ignore real ones.

**Status:** Suppressed 2026-05-20 in `rag/posture_loader.py:_build_engine_neo4j_driver` via `notifications_disabled_classifications=["UNRECOGNIZED"]`. Scoped to the engine driver only — `graph_expander.py` uses its own driver, so the unrelated `01N51`/`01N52` warnings flagged in [[neo4j-graph-unused-element-warnings]] are unaffected and still need the schema audit before being touched.

**How to apply (revert):** Remove the `notifications_disabled_classifications` kwarg once any FulfilmentSpec or REQUIRES_EVIDENCE edge actually carries an `applies_when` value — even one sentinel populated row registers the key in Neo4j's schema and the warning naturally goes away.

Related: [[applies-when-phase1-regression-tests]], [[hitl-two-stage-approval-design]].
