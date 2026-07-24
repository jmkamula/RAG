---
name: ship-22-prime-b-bridge-retire-2026-07-24
description: "Ship 22'.b — retired ↳ Bridges to ISO 27001 prose footer; cross_framework_bridge + demonstrated_by cards in related[] already cover the footer content since Ship 18/19/20"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 22'.b — retired the `↳ Bridges to ISO 27001 for Art.X:`
prose footer (Ship 1.14). Commit `dd5791d`. Symmetric with
Ship 21'.b — bridge footer became structurally redundant with
`related[]` cross_framework_bridge + demonstrated_by cards
since Ship 18/19/20.

## Two changes

### 1. rag/casefile/repair.py::check_and_repair

Removed the `footers.append(spec.bridge_footer)` append line.
Retained the `missing_bridge_footer` repair event — auditors
can still identify bridge misses via
`chat_casefile_log.repair_events` + `scripts/audit_retired_
footer.sql`. Only the visible prose append was removed.

`_build_bridge_footer` helper stays in `preservation.py` for
any future caller wanting the string (same discipline as
`_compliance_facts_footer` in Ship 21'.b).

### 2. scripts/audit_retired_footer.sql

Extended the header comment to document the retired-footer
coverage across Ship 21/22 arcs. Query SELECT unchanged;
clarifies which prose footer each event kind corresponds to.

## Coverage verification (live on Art.32 query)

- Zero `↳ Bridges to` in prose ✓
- Zero `↳ Compliance facts:` in prose (Ship 21 still holds) ✓
- `## Related controls` section renders 7 cards:
    Art.32   [NC]  primary
    A.5.23   [NC]  demonstrated_by
    A.7.2.1  [NC]  demonstrated_by
    A.7.4.9  [NC]  demonstrated_by
    A.8.5    [NC]  demonstrated_by
    6.1.2    [OFI] demonstrated_by
    A.5.15   [OFI] cross_framework_bridge
- Every ref the retired footer would have listed is present
  as a card with verdict + evidence summary + drill-in.

## Known limitation (surfaced in Ship 22'.d)

Coverage above relies on the LLM citing ISO refs in prose so
`build_related_cards` picks them up via ref scanning. If LLM
cites only obligation refs (Art.5 without any ISO controls),
the demonstrator cards go missing. Ship 22'.d addresses this
with the demonstrator auto-inject.

## Ship 22 progress

| Sub-arc | Status |
|---|---|
| 22'.a Design memo | ✓ (539670d) |
| **22'.b Bridge footer retirement (this)** | **✓ (dd5791d)** |
| 22'.c RiskCard + risk footer retirement | next |
| 22'.d Eval + retro | pending |

## Related

- [[ship-22-prime-a-footers-design-2026-07-24]] — design
- [[ship-21-prime-arc-retrospective-2026-07-23]] — retire-visible
  + keep-observability pattern established here
