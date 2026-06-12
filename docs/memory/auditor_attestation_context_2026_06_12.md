---
name: auditor-attestation-context-2026-06-12
description: "SHIPPED 2026-06-12 (da893b0): deterministic posture compose now surfaces auditor-report attestations as context lines under each affected control. Engine verdict unchanged; auditor's authoritative statement visible alongside so the gap between cert-audit blessing and per-MUST evidence is operator-visible. Bug squashed: state['tenant_id'] is the tenant name not UUID in retrieve."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

When an external certification audit blesses an ISMS clause but
the engine still reports NC because per-MUST evidence isn't
bound, the previous UX surface hid the auditor's view entirely.
This shipped a context-annotation layer.

## The trigger

An external ISO 27001 cert auditor uploaded a 16-page Czech-
language report with positive findings on 9.1/9.2/9.3/7.5/10.1
and an improvement recommendation on A.5.10. All 8 findings
landed in Stage-1, were approved, but produced **0 posture
flips** because LLM-extracted findings have no
`checklist_item_id` → engine Phase-2 can't bind to specific
leaf MUSTs. The chat still showed 9.2 (Internal audit) as NC
even though the auditor literally wrote "internal audit
programme fully implemented and effective".

Optically poor. Substantively *correct* (see
[[feedback-audit-blessing-not-immunity]]). The fix surfaces
the auditor's view as context without weakening the engine's
strictness.

## What ships

`_fetch_auditor_attestations(tenant_id)` queries
`document_findings JOIN client_documents` for the most recent
approved finding per control where `cd.evidence_type =
'audit_report'`. Returns
`{control_ref → {report, attested_at, excerpt}}`. Best-effort:
DB error returns empty dict, compose still runs.

The deterministic posture-enumeration compose threads this dict
through to the row formatter. Each row gets a continuation
line under the engine verdict:

```
- **ISO 27001 9.2 — Internal audit**: 0 of 4 requirements met ...
  ↳ *External auditor (214427_Client Report 27001_DG3D87.pdf,
     2026-06-12): "program interního auditu byl plně
     implementován a prokazuje svoji účinnost..."*
```

Excerpt truncated to ~140 chars + ellipsis if longer; no
attempt to translate the auditor's language (Arion's report
is Czech — surfaces verbatim).

## What doesn't change

  - Engine verdict — still strict per-MUST binding
  - Posture state — `posture_controls.finding` unchanged
  - Stage-2 proposals — engine doesn't propose flips based on
    auditor attestations
  - Other compose paths (rank_and_answer LLM path) — only the
    deterministic enumeration compose has the context line so
    far. LLM path could add it but would need prompt-side
    instruction; deferred until needed.

## The bug found while building

`state["tenant_id"]` in the retrieve node is the tenant
**name** ("Arion Networks") not the UUID. Surfaced when the
fetcher returned 0 rows under API context vs 8 rows under
direct test. Fix: pass `str(getattr(tenant, "tenant_id", ""))`
directly to the fetcher. The same shadowing happens in other
call sites (rank_and_answer's `tenant_name=state["tenant_id"]`
is intentional — passes name as label — but if anyone tries
to use it as a UUID they'll hit the same trap).

## Related

- [[feedback-audit-blessing-not-immunity]] — the principle that
  motivated this design (auditor attestation is context, not
  authority to flip posture)
- [[posture-claim-hallucination-guard]] — the L1 guard runs
  AFTER the auditor lines are added; lines don't contain
  status claims so they pass through unfiltered
- [[stage1-contract-change-path-a-2026-05-25]] — explains why
  Stage-1 approval doesn't directly mutate posture, which is
  the architecture this annotation layer respects
