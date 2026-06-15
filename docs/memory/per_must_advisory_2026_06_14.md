---
name: per-must-advisory-2026-06-14
description: "SHIPPED 2026-06-14 (20a641c): per-MUST chat-side advisory appendix. Deterministic compose from evaluate_one_control() per-leaf items_recognised/unrecognised + upload-hint templates per evidence_type + source label per standard. Hooks rank_and_answer for POSTURE_CHECK or CROSS_FRAMEWORK intent with single control in intent.cited_refs. Locked by eval case 199."
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

## Same data, future surfaces

`build_per_must_advisory` is the data path for three downstream
surfaces:

1. Chat (shipped today)
2. **Per-control dashboard drill-in card** — same function, render
   as HTML/JSX checklist with ✓/✗ per MUST
3. **Document templates per evidence_type** — pre-built starter
   register / procedure that the tenant fills in, with MUST
   descriptions as section headings

Items 2 and 3 are in `[[curation-document-templates-idea]]`
backlog — both reuse `build_per_must_advisory`'s output as their
data source, so they're additive not duplicative.

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
