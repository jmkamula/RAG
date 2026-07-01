---
name: evidence-class-breakdown-backend-2026-06-26
description: "SHIPPED 2026-06-26: GET /api/v1/dashboard/control/{ref}/evidence-classes + rag/posture/advisory.build_evidence_class_breakdown. Per-control rollup grouped by evidence_type, with per-leaf MUSTs bound/total + source documents + template availability. Turns the templating arc's foundation into the actionable 'you need register/procedure/review evidence' UX the under-discovery audit identified."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What shipped

New endpoint `GET /api/v1/dashboard/control/{control_ref}/evidence-classes`
+ helper `rag/posture/advisory.build_evidence_class_breakdown` that
returns per-control coverage grouped by evidence_type.

Response shape (abridged):
```
{
  "control_ref": "A.5.18",
  "posture": "NC",
  "musts_total": 31,
  "musts_bound": 7,
  "overall_yield_pct": 23,
  "evidence_classes": [
    {
      "evidence_type": "register",
      "class_musts_total": 7,
      "class_musts_bound": 0,
      "class_yield_pct":   0,
      "upload_hint": "Add or extend a register ...",
      "leaves": [
        {
          "leaf_id": "req:A.5.18:access_rights_register",
          "musts_total": 7,
          "musts_bound": 0,
          "items_missing": [<text>...],
          "must_items": [{id, text, satisfied}],
          "source_documents": [],
          "template_available": true
        }
      ]
    },
    ...
  ]
}
```

Verified on two controls:
- A.5.18 (NC, 23%): surfaces `register 0/7 with template available, no
  source docs` — the actionable "you need register evidence" signal
- A.5.1 (OFI, 43%): surfaces `policy 5/5 fully covered;
  review/communication/approval all need evidence` — breaks the OFI
  rating down into specific actionable gaps

## Non-obvious decisions

### Separate endpoint, not an extension of /advisory

`/advisory` returns None when posture is Comply / N/A. The
evidence-class view should work for ALL controls (a Comply control
shows "100% covered" cells — that's useful information). Keeping it
separate also means the chat surface (which calls /advisory) doesn't
suddenly receive richer-than-expected data. Different concerns,
different endpoints; helper functions share the same
`evaluate_one_control` data source.

### Source documents from document_findings, not from verdict

The verdict's `items_recognised` gives MUST texts, not provenance.
The endpoint joins `document_findings` to `client_documents` keyed
on checklist_item_id to derive which docs backed each binding. Sort
by filename for deterministic UI rendering.

### Class ordering = total MUSTs descending

The biggest-impact class shows first (e.g. A.5.18 leads with
`revocation_record 0/8` because that's the most evidence requirements).
Tenants who only read the top of the page still see the most
material gap. Don't sort by yield_pct — a tiny class at 0% would
shout louder than a big class at 50%, which is the wrong priority
signal.

### Template availability per leaf (not per class)

`templates` table is keyed by leaf_id (schema_v45). One class can
have multiple leaves with different template availability. Surface
the flag per leaf so the UI can render "📄 download template" CTA
only where one exists.

## Why this is the actual product lever

Per [[llm-narrative-under-discovery-audit-2026-06-26]] the ~43% gap
at median yield is overwhelmingly **wrong evidence type uploaded for
the missing MUSTs** — tenant uploaded a policy doc; the missing
MUSTs need procedure/register/record evidence in different docs.
Telling them so via this UI is the real fix; no more extraction
re-engineering needed.

## Next: frontend

Render the breakdown on the per-control drill-in in
`static/arioncomply.html`. Each class group as a section with
expand-on-click; per-leaf rows show bound/total + source docs +
template CTA. Missing classes get a "Use template" / "Open form" CTA
that drives the templating arc's authoring lanes.

## Post-dejargonize note (2026-07-01)

Panel labels in this description reflect the pre-dejargonize
strings. Post-2026-07-01 the drill-in reads:

  - "Evidence coverage by type" → "Evidence coverage"
  - "Direct evidence" → "Evidence for this control"
  - "Composition · N of M satisfied" → "Coverage · N of M
    elements in place"
  - "no source yet" → "not yet evidenced"
  - "How to advance X" (sibling advisory) → "How to strengthen X"
  - evidence_type slugs rendered Title Case ("review_record" →
    "Review Record") via `_humanize_evidence_type`
  - `leaf_label` prefers `EvidenceRequirement.title` rather than
    the `leaf_id.split(":")` fallback

Backend data spine unchanged. See [[dejargonize-ux-pass-2026-07-01]].

## Related

- [[per-must-advisory-2026-06-14]] — the sibling surface (per-MUST
  advisory for chat + dashboard "How to strengthen" card stack).
  Same data spine (`evaluate_one_control`), different audience.
- [[llm-narrative-under-discovery-audit-2026-06-26]] — the audit
  dive that identified this UX as the real lever after the
  semantic-search arc was closed.
- [[templates-v2-anchors-complete-2026-06-25]] — the 20 v2 anchor
  templates that the "Use template" CTAs link to.
- [[templated-lane-discipline-2026-06-25]] +
  [[form-lane-parity-2026-06-26]] — the authoring lanes that
  template/form CTAs drive into.
- [[dejargonize-ux-pass-2026-07-01]] — the surface-wide natural-
  language pass that reworked this drill-in's labels.
