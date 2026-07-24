---
name: ship-22-prime-c-riskcard-retire-2026-07-24
description: "Ship 22'.c — added RiskCard + `risks: list[RiskCard]` to StructuredAnswer; retired ↳ Risk register prose footer; wired short-circuit + frontend renderer; fourth card type"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 22'.c — added a first-class risk representation to the
structured chat payload and retired the last remaining prose
footer. Commit `d1a4a44`.

## Schema additions (rag/casefile/answer_schema.py)

`RiskCard` — 11-field Pydantic model for one risk-register
entry. Fully deterministic; every field derives from the
tenant's risk-register row:

- `external_ref` — "R-042"
- `threat`, `vulnerability` — tenant-authored descriptions
- `risk_score`, `residual_risk_level` — likelihood × impact (0-25)
- `treatment_option` (avoid/reduce/transfer/accept),
  `treatment_status` (in_treatment/accepted/implemented)
- `risk_owner_text` — display name
- `review_date` — ISO date string
- `linked_controls: list[str]` — control refs, ordered by role
  (program → extension → obligation)
- `dashboard_url` — `/#risks?risk_id=<uuid>`

`StructuredAnswer.risks: list[RiskCard]` — parallel array
alongside `related[]`. Risks aren't controls (no standard_id,
verdict, role, leaves) so squeezing into RelatedCard would
distort semantics.

## Augment (rag/casefile/answer_augment.py)

- `build_risk_cards(risks_data)` — deterministic dict→RiskCard
  conversion. Sorts linked_controls by role. `dashboard_url`
  routes to the existing `/#risks` mode.
- `augment_and_repair` wires `CaseFile.risks` (Ship 14'.e —
  populated for posture_risk turns via
  `fetch_risks_for_casefile`) into `structured.risks`.
  Logs `missing_risk_ref` events when the LLM prose dropped
  a risk external_ref — auditor parity via
  `chat_casefile_log.repair_events`.
- `build_short_circuit_structured` gains a `risks_data` param.
- `structured_to_prose` gains a `## Risks` section:
    ## Risks
    - **R-042** — Data exfiltration — score 16/25 —
      treatment: in_treatment — linked A.5.15, A.8.24
  Rendered only when structured.risks is non-empty.

## Retirement (rag/casefile/repair.py)

Removed the `↳ Risk register:` prose append from
check_and_repair. `missing_risk_ref` repair events still fire.
Symmetric with Ship 21'.b + 22'.b retirements.

## Short-circuit wiring (rag/arion_graph.py)

Risk short-circuit (line 2507) swapped from
`build_intro_only_structured` to
`build_short_circuit_structured(risks_data=
fetch_risks_for_casefile(_tid, top_n=8))`. Stays Family A
(intro-only prose) + parallel RiskCard[] metadata for the
card render.

## Frontend (static/arioncomply.html)

`renderStructuredAnswer` emits a `## Risks` section under
`## Related controls`. Per-card render:
- ref tag + `score/25` badge + treatment_status chip
- threat description line
- owner display line
- linked-controls ref tags (capped 6 + `+N more` overflow)
- "Open risk register →" drill-in via `setMode('risks')`

New CSS: `.sa-risks`, `.sa-risk-card` (red left border
matching NC verdict color), `.sa-risk-score` badge.

## Verified end-to-end

`what are our top risks?` on demo tenant:
- 8 risk cards on the structured payload
- Zero footers of any kind (Compliance facts / Bridges to /
  Risk register all gone)
- Cards render on chat with drill-in to the existing risk
  register mode

`structured_to_prose` direct call verified `## Risks` markdown
renders correctly on manually-constructed payloads.

## Ship 22 progress

| Sub-arc | Status |
|---|---|
| 22'.a Design memo | ✓ (539670d) |
| 22'.b Bridge footer retirement | ✓ (dd5791d) |
| **22'.c RiskCard + risk footer retirement (this)** | **✓ (d1a4a44)** |
| 22'.d Eval + retro | next |

## Related

- [[ship-22-prime-a-footers-design-2026-07-24]] — design
- [[ship-14-prime-a-role-model-arc-2026-07-22]] — risk
  feature this arc extends with card rendering
- [[ship-15-prime-d-demonstrates-sdk-2026-07-22]] —
  RiskDetail drill-in surface + linked_controls shape
