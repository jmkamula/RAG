---
name: applies-when-warning-suppression
description: "Neo4j 01N52 'property key does not exist' fires on every engine sweep because applies_when is absent on all FulfilmentSpec/REQUIRES_EVIDENCE — suppress at driver level"
metadata: 
  node_type: memory
  type: project
  originSessionId: ab2912f3-a587-4819-891f-14d62eba574c
---

Neo4j emits `01N52 property key does not exist (applies_when)` on every `compute_engine_verdicts` call because `spec_builder.py` queries reference the property but **0 of 429** FulfilmentSpec nodes and **0 of 25** REQUIRES_EVIDENCE edges currently carry it. The migration created them with `applies_when: NULL`, which in Cypher is equivalent to "property absent" — hence the warning. Suppress at driver configuration level.

**Why:** Phase-1 ship-with-DSL-but-no-rules is intentional (see [[applies-when-phase1-regression-tests]]). The warning is expected behavior, not a defect, but it spams the log on every engine sweep. Persistent low-signal warnings train responders to ignore real ones.

**How to apply:** When configuring the Neo4j driver (currently `posture_loader._build_engine_neo4j_driver`), pass a notification filter to silence `UNRECOGNIZED` classifications, or the more specific `01N52` code. Re-enable once any FulfilmentSpec node actually carries an `applies_when` value — even one sentinel populated row registers the key in Neo4j's schema and the warning naturally goes away.

Related: [[applies-when-phase1-regression-tests]], [[hitl-two-stage-approval-design]].
