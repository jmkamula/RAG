---
name: ship-54-prime-arc-2026-08-03
description: "Ship 54' templating + intake round-trip arc — 12 sub-arcs 2026-08-02→08-03. Topics data layer (17 curated bundles, 185 leaf-refs across P/E/O mesh via schema_v91), advisory API + SPA Topics view + leaf-scoped drill-in with per-leaf state chip, chat topic-bundle intent routing, doc-control renderer block, and 3-phase structural evidence intake round-trip (detector library + standalone inference_source lane + structural_maturity consensus signal). Full retro at docs/memory/ship_54_prime_arc_retrospective_2026_08_03.md."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 54' delivered the templating + workflow + intake round-trip
extension over 2 days (2026-08-02 → 2026-08-03) as a follow-on
to Ship 53' consultant-grade grounding.

**Commits** (chronological):
- `63f0cf2` — 54'.a topics data model + 12 bundles + schema_v91
- `cb82a4e` — 54'.a addendum 27701 mesh coverage
- `0aa5d65` — 54'.a addendum 2 — 5 new 27701 topics (17 total)
- `c44e2aa` — 54'.b advisory API + SPA Topics view
- `14baf08` — 54'.b addendum inline drill-in + text scrub
- `5791f49` — 54'.b addendum 2 leaf-scoped MUST checklist
- `7da35e9` — 54'.b addendum 3 per-leaf state chip
- `71b3b4b` — 54'.c chat topic-bundle intent routing
- `cde5190` — 54'.d doc-control + revision-history renderer blocks
- `2b0d7e5` — 54'.e Phase 1 detector library + 13 unit tests
- `bc139eb` — 54'.e Phase 2 intake wiring (schema_v92 + lane)
- `f3513e4` — 54'.e Phase 3 structural_maturity consensus signal
- `1dc4846` — Retrospective

**Key architectural takeaways**:

- **Topics as additive overlay** — `db/topics/*.yaml` referenced
  by many-to-many `topic_leaves`, leaves know nothing about
  topics. Pure overlay preserves the 845 per-leaf templates.

- **Framework role model must be audited by role BEFORE shipping**.
  Original 54'.a shipped with 0/100 ISO 27701 refs; operator
  caught it. Now enforce P/E/O composition per topic.

- **Consensus intercepts trump downstream short-circuits**.
  Ship 54'.c needed pre-consensus intercept in
  `arion_graph.py::make_classify_node` — consensus was resolving
  workflow queries to `implementation` with high confidence
  before any short-circuit fired.

- **Structural evidence dual-role**:
  - Direct evidence via `inference_source='structural_pattern'`
    lane (Ship 54'.e Phase 2) — per-MUST bindings with
    provenance excerpts ("Approved By: Maria Silva, CEO")
  - Consensus signal via `structural_maturity` (Ship 54'.e Phase 3)
    — weight 0.15, scales 40%/70%/100% by pattern count
  - Signal added to `_POSITIVE_SIGNAL_NAMES` corroborator allowlist
  - `bm25_topk` also added (was missing since Ship 43'.b)

- **Round-trip binding** — `<<DOC_CONTROL>>` marker in renderer
  output = shape recognised by structural detector on re-upload.
  Templates carry their own audit trail.

- **17 curated topics** covering the workflow-shape flows real
  compliance work actually follows (DSR, incident, consent,
  DPIA, RoPA, transfers, processor ops, etc.).

**IP posture** (per operator note "possible patent"):
- Round-trip binding discipline (output shape = input shape)
- Dual-role structural fusion (direct evidence + signal boost
  from one detection pass)
- Provenance-preserving structural extraction (every finding
  traces to a specific line/table row)

**Verified**: 4 topic queries route correctly in chat; SPA
Topics grid + leaf-state chip visible per topic; DOCX for 5.2
policy carries all 11 doc-control labels + POL-5.2-Rev03 doc
number; 13 unit tests pass on structural detectors; end-to-end
round-trip on our own 5.2 DOCX yields 3 structural findings +
signal boost=0.105 (2-pattern case).

**Cost impact**: none for topics API (deterministic Postgres);
chat topic-bundle is deterministic (zero LLM cost);
structural detection is O(text length); consensus signal adds
one extra Postgres query per doc during extraction (bulk
document_findings lookup). All cheap.

**Deferred to Ship 55+**:
- Bulk-add `<<DOC_CONTROL>>` + `<<REVISION_HISTORY>>` markers to
  policy/procedure templates (curator arc)
- tenant_profile Prepared_By/Approved_By fields for auto-fill
- End-to-end intake test with USE_CONSENSUS_EXTRACTION=1
- Documents tab list view + per-doc detail modal (deferred
  from Ship 51+52+53, still deferred)
- Records-produced section + reference-to-other-documents
  detectors (bigger scope, need graph writes)
- Patent filing prep

See full retrospective at
`docs/memory/ship_54_prime_arc_retrospective_2026_08_03.md`
for the 8 codified lessons + round-trip diagram.
