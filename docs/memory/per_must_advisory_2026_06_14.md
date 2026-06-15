---
name: per-must-advisory-2026-06-14
description: "SHIPPED chat 2026-06-14 (20a641c) + dashboard endpoint 2026-06-15 (20ecd18) + dashboard UI 2026-06-15 (9cf5f8a): per-MUST advisory data path. Deterministic compose from evaluate_one_control() per-leaf items_recognised/unrecognised + upload-hint templates per evidence_type + source label per standard. Chat surface hooks rank_and_answer for POSTURE_CHECK/CROSS_FRAMEWORK with single control in intent.cited_refs (locked by eval #199). Dashboard endpoint GET /api/v1/dashboard/control/{control_ref}/advisory returns structured JSON; dashboard UI (static/arioncomply.html:renderAdvisoryPanel) renders 'How to advance' card stack below the verdict tree on heatmap drill-in. Three surfaces, one data path."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

The shift from "engine knows what's missing" to "tenant knows what
to do". After accepting the 35 Phase-1-retirement NCs as honest
posture (167 NC / 10 OFI live distribution), the natural next move
was surfacing the fulfilment criteria — the MUSTs we'd been
authoring for weeks — as actionable advisory.

## What ships

`rag/posture/advisory.py:build_per_must_advisory(pg, tenant_id,
control_ref, standard_id)` returns a deterministic markdown
appendix for a control's chat answer. Empty string for Comply / N/A
/ no-curated controls so the hook self-suppresses where advisory
makes no sense.

Output shape (per leaf, per control):

```
↳ How to advance A.5.15 (currently NC; 0 of 4 leaves satisfied, 1 partial)

  - access control policy (policy) — 2/7 elements covered.
    Have: principle of least privilege; RBAC.
    Still needed:
      - Authorisation rules ...
      - Logical access rules ...
      - Principle of need-to-know stated
      - Physical access rules ...
      - Cross-link to A.5.3 segregation of duties
    To address: Update the policy document to articulate each missing element.

  [... per-leaf repeated ...]

Source: ISO/IEC 27002:2022 §5.15 implementation guidance.
```

## Hook point

`rag/arion_graph.py:make_retrieve_node`, after `rank_and_answer`,
before the `return {answer_text, ...}`. Conditions:
  - intent.question_type in (POSTURE_CHECK, CROSS_FRAMEWORK)
  - intent.cited_refs has exactly 1 entry (the user's original
    mention; LLM result.cited_refs gets contaminated by xfw
    bridges so we prefer the classifier's view)
  - control's engine verdict is NC or OFI (Comply/N/A short-circuit
    inside build_per_must_advisory)

Self-suppressing on broad queries ("what is our overall posture?"
→ 0 cited refs → no advisory). Self-suppressing on positive
verdicts. ~2,200-2,400 chars added per single-control query on
Arion's NC-heavy posture.

## Upload-hint templates per evidence_type

`_UPLOAD_HINTS` maps evidence_type → short action sentence:
  - policy → "Update the policy document to articulate each missing element."
  - procedure → "Document each missing step in the procedure document."
  - register → "Add or extend a register with a column or row per missing element."
  - revocation_record / disposal_record / closure_record / exercise_record
    → "Capture per-event records with fields for each missing element."
  - review_record / audit_report → "Conduct a review/audit and produce a record covering each missing element."
  - approval → "Produce an approval record with the missing signature / scope details."
  - scope_note → "Add a scope-note section enumerating the missing elements."
  - agreement_template → "Update the agreement template to include clauses for each missing element."
  - ...
  - default → "Produce evidence (document, record, or register) that articulates each missing element."

Each template is short, concrete, and pegged to the evidence shape
the engine is looking for. The MUST descriptions inside the section
provide the per-MUST specifics.

## Source labels per standard

`_source_label(control_ref, standard_id)`:
  - Annex A controls (A.5.x / A.6.x / A.7.x / A.8.x) → "Source:
    ISO/IEC 27002:2022 §X implementation guidance."
  - ISMS clauses (4-10) → "Source: ISO/IEC 27001:2022 clause X."
  - GDPR articles → "Source: GDPR Art.X (EU Regulation 2016/679)
    + EDPB guidance."

The label anchors the advisory to the authoritative reference,
matching what an auditor would expect.

## Cost

One `evaluate_one_control()` call per chat answer that hits the
hook — Neo4j + Postgres round-trip, ~50-200ms in normal range.
Acceptable because POSTURE_CHECK/CROSS_FRAMEWORK is an
acknowledged-slow path. Driver lazily created from env vars,
cached on the module (`_DRIVER` module-level var).

## Scars from implementation

- `get_logger()` from chain_logger.py returns None when not in
  a chain-logger context. The advisory hook tried to use it and
  blew up. Fixed by using `logging.getLogger(__name__)` directly.
- `posture_db` isn't reliably in scope inside retrieve(); the
  surrounding code uses `posture_db if "posture_db" in dir() else
  None` which means existing trace-write was no-op. The advisory
  hook calls `build_pg_conn()` fresh each time and closes after —
  not optimal but works. A pooled connection would be better.
- `result.cited_refs` includes xfw bridges (e.g. Art.32.1.b on
  an A.5.15 query) which fails the single-ref check. Switched to
  preferring `intent.cited_refs` (classifier-extracted, reflects
  the user's literal mention) over `result.cited_refs`.

## Three surfaces sharing one data path

`build_per_must_advisory_data(pg, tenant_id, control_ref,
standard_id, neo4j_driver=None)` is the canonical data builder.
Returns dict (or None) with shape documented in the source file.
Three surfaces consume it:

1. **Chat appendix** (shipped 2026-06-14, 20a641c).
   `build_per_must_advisory()` → `_render_advisory_markdown(data)`
   → markdown string. Hook in `arion_graph.py:make_retrieve_node`
   after `rank_and_answer`. Locked by eval #199.

2. **Dashboard drill-in endpoint** (shipped 2026-06-15, 20ecd18).
   `GET /api/v1/dashboard/control/{control_ref}/advisory` →
   structured JSON. Auto-infers standard_id from control_ref
   prefix (`Art.*` → GDPR, default → ISO 27001:2022). Override
   via `?standard_id=...` query param. Returns
   `advisory: null` when no advisory warranted.

3. **Dashboard UI panel** (shipped 2026-06-15, 9cf5f8a).
   `static/arioncomply.html:renderAdvisoryPanel(advisory)` is
   the JS renderer. Called from the heatmap drill-in flow on
   NC/OFI controls — fetches the endpoint after the verdict
   tree, appends a "How to advance" card stack below the tree
   via `insertAdjacentHTML('beforeend', ...)`. Best-effort
   (silent on error so verdict tree always renders).

   Card shape per unmet leaf:
     ◐ <leaf_label> · <evidence_type> · N/M elements covered
     Have:   <recognised items, green>
     Still needed:  <missing items, red>
     To address: <upload hint pegged to evidence_type>
     [footer] Source: <standard citation>

The data builder is the single source of truth for "what's
missing and what to upload". All three surfaces emit the same
information in their native shape; any catalog/MUST change
propagates to all three automatically.

## Future surface still on backlog

3. **Document templates per evidence_type** — pre-built starter
   register / procedure that the tenant fills in, with MUST
   descriptions as section headings. Captured in
   `[[curation-document-templates-idea]]` — would reuse
   `build_per_must_advisory_data()` to determine sections to
   include per leaf.

## Eval lock

Case #199 (`is A.5.15 compliant?`) — must_contain:
  - "A.5.15"
  - "How to advance A.5.15"
  - "Still needed:"
  - "To address:"
  - "Source: ISO/IEC 27002:2022"

Any regression in the deterministic compose, the hook condition,
or the source label format will surface here.

## Related

- [[leaf-scan-catalog-campaign-2026-06-14]] — the fulfilment-
  criteria authoring that this advisory now surfaces
- [[feedback-phase-1-fallback-masks-gaps]] — the architectural
  finding that drove honest per-MUST scoring; advisory is the
  user-facing complement (honest scoring + honest guidance)
- [[cross-framework-bridge-footer-2026-06-14]] — sibling
  deterministic appendix in the same chat compose path; both
  ride after `rank_and_answer` returns
- [[curation-document-templates-idea]] — future surface that
  consumes the same `build_per_must_advisory` data path
