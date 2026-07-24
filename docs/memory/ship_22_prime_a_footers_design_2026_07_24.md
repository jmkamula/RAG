---
name: ship-22-prime-a-footers-design-2026-07-24
description: "Ship 22'.a — design memo: retire bridge footer (already covered by cross_framework_bridge cards) + retire risk footer (needs new RiskCard type + `risks: list[RiskCard]` on StructuredAnswer)"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 22'.a — opens Ship 22 arc (retire bridge + risk footers).
Ship 21 retired the `↳ Compliance facts:` footer; Ship 22
retires the remaining two: `↳ Bridges to ISO 27001 for Art.X:
...` (Ship 1.14) and `↳ Risk register: R-...` (Ship 14'.e).

## Eval coverage check (blowback prevention)

grep of `tests/eval_suite.py`:
- 0 assertions on `"↳ Bridges to"` or `"Bridges to"` in
  `must_contain=[]` — 2 grep hits total, both in `notes=`
  documentation strings.
- 0 assertions on `"↳ Risk register:"` or `"Risk register:"`.

Both footers can be retired without touching eval assertions.

## Two footers, two shapes of removal

### Bridge footer (Ship 1.14) — leaner retirement

Current format:
```
↳ Bridges to ISO 27001 for Art.X: A.5.15 [Comply], A.5.18 [NC-DRAFT]
```

Data class: cross-framework edges (IMPLEMENTS / SUPPORTS /
ENABLES / GOVERNANCE) from the query's article to implementing
controls in another standard.

**Coverage in structured payload**: `RelatedCard.relation`
already has a `cross_framework_bridge` value (Ship 18/19/20).
When the query cites an article (e.g. Art.32), the case-file
flow populates related[] with:
- The article's own card (primary if that's the query focus)
- `demonstrated_by` cards for each program/extension control
  that DEMONSTRATES the article (via
  `cf.demonstrated_by(article_ref)` → posture record's
  `demonstrated_by` list)
- `cross_framework_bridge` cards for controls in a different
  standard that have IMPLEMENTS/SUPPORTS edges

**Verification needed**: confirm that a Family B or LLM-path
query "what does Art.32 need for compliance?" produces
related[] cards covering the same primary refs the bridge
footer would list. If yes → straightforward retirement (like
Ship 21). If gaps exist → extend `build_related_cards` first.

Existing bridge cards already appear in prose via
`structured_to_prose`'s `## Related controls` bulleted list —
each with verdict + evidence summary. Auditor content is
preserved on the card render.

### Risk footer (Ship 14'.e) — needs schema extension

Current format:
```
↳ Risk register: R-042, R-108
```

Data class: `external_ref` identifiers from the tenant's
risk register that the digest surfaced.

**Coverage in structured payload**: NONE. `RelatedCard` is
control-shaped (ref, standard_id, verdict, role, evidence
summary, leaves). Risks aren't controls:
- No standard_id
- Verdict is risk_score / treatment_status, not NC/OFI/Comply
- Role is "risk_owner", not program/extension/obligation
- No leaves; no evidence_summary in the same sense
- Cross-linking is `linked_controls[]`, not
  `cross_framework_bridge`

Squeezing risks into RelatedCard would require weird semantic
mapping. Cleaner: new **RiskCard** type + separate `risks:
list[RiskCard]` field on StructuredAnswer.

### Proposed RiskCard shape

```python
class RiskCard(BaseModel):
    external_ref:     str                    # "R-042"
    threat:           Optional[str] = None
    risk_score:       Optional[int] = None   # residual/inherent — TBD
    treatment_status: Optional[str] = None   # "in_treatment" / "accepted" / etc.
    risk_owner_text:  Optional[str] = None
    linked_controls:  list[str] = []         # refs of controls, ordered by role
    dashboard_url:    Optional[str] = None   # /#risks?risk_id=<id>
```

Every field derives from `CaseFile.risks[]` (already populated
by Ship 14'.e when question_type == posture_risk). No new
LLM emission surface — RiskCard is 100% deterministic like
RelatedCard.

### Updated StructuredAnswer shape

```python
class StructuredAnswer(BaseModel):
    intro:   IntroCard
    actions: list[ActionCard]  = Field(default_factory=list)
    related: list[RelatedCard] = Field(default_factory=list)
    risks:   list[RiskCard]    = Field(default_factory=list)  # NEW
```

Additive; existing consumers keep working.

## Prose reconstruction updates

`structured_to_prose` (Ship 21'.b) needs a new section:

```markdown
{intro.text}

## {action.title}
{action.body}

## Related controls
- **A.5.15** (Access control, ISO 27001:2022) — OFI-DRAFT — 1 of 4 items present

## Risks
- **R-042** — Unauthorized data exfiltration — score 16/25 — treatment: in_treatment — linked A.5.15, A.8.24
```

Section rendered only when `structured.risks` is non-empty.
Applied uniformly to LLM path (`_casefile_flow`) and any
short-circuits that carry risks (currently just the risk
short-circuit at line 2454 — Family A intro-only. That
site doesn't have `cited_refs` so it wouldn't get risk cards
via the Ship 20'.c/d flow. Handle in 22'.c by extending
`build_short_circuit_structured` to accept a `risks[]` param.)

## Auditor-trail guarantee (blowback prevention)

Same pattern as Ship 21:
- Repair events (`missing_bridge_footer`, `missing_risk_ref`)
  still fire in `check_and_repair`; only the visible appends
  are removed.
- `chat_casefile_log.repair_events` continues to populate.
- Extend `scripts/audit_retired_footer.sql` — the query
  already joins `jsonb_array_elements(repair_events)`; add
  the two new event kinds to the filter comment. Same
  auditor surface, more coverage.

## Sub-arc plan

### 22'.b — Bridge retirement (leaner)

- Verify cross_framework_bridge cards cover the footer's
  content via a live smoke test on a bridge query (e.g. "what
  does Art.32 require for compliance?").
- Remove the `bridge_footer` handling from `check_and_repair`.
  Repair events (`missing_bridge_footer`) still fire above the
  removal block.
- Keep the `_build_bridge_footer` helper in
  `preservation.py` — same discipline as Ship 21 (retire the
  call, not the function).
- No schema changes; no prose changes beyond removing the
  bridge_footer append site.

### 22'.c — RiskCard + risk footer retirement

- Add `RiskCard` to `rag/casefile/answer_schema.py`.
- Add `risks: list[RiskCard]` to `StructuredAnswer`.
- Populate risks in `augment_and_repair` from `cf.risks[]`.
- Extend `build_short_circuit_structured` with a `risks[]`
  parameter for the risk short-circuit.
- Update `structured_to_prose` with `## Risks` section.
- Remove the risk-facts footer from
  `check_and_repair` (`spec.required_risk_refs` handling).
  Repair events (`missing_risk_ref`) still fire.
- Update `static/arioncomply.html` to render risk cards.

### 22'.d — Eval + retrospective

Same discipline as Ship 21'.c. Full eval regression check +
arc retrospective.

## Design decisions locked in 22'.a

1. **Bridge footer: no schema change.** Cross_framework_bridge
   cards already exist in `related[]`; retirement is symmetric
   with Ship 21.

2. **Risk footer: new RiskCard, not a RelatedCard variant.**
   Risks aren't controls; forcing them into RelatedCard would
   contort verdict/role/leaves semantics. Cleaner as a
   parallel array.

3. **RiskCard is deterministic.** Every field derives from
   `CaseFile.risks[]` (Postgres-authored). No LLM emission
   surface; APPEND-ONLY preserved.

4. **`_build_bridge_footer` helper kept in-file.** Same
   pattern as `_compliance_facts_footer` (Ship 21'.b) — remove
   the call, not the function. Prevents accidental capability
   loss.

5. **RiskCard `dashboard_url` uses `/#risks?risk_id=<uuid>`.**
   Matches the existing risk mode router in
   `static/arioncomply.html`.

## What Ship 22 does NOT do

- **Retire the prose `answer` field.** Backward compat.
- **Change short-circuit prose composition.** Only the risk
  short-circuit (Family A intro-only) gets extended to carry
  risk cards; other short-circuits unchanged.
- **Retire the `bridge_footer` / `required_risk_refs` fields
  from `PreservationSpec`.** They still gate the repair-event
  firing (which we want kept for the audit log). Removing the
  fields is scope creep for a future arc.
- **Add a RiskCard leaves-checklist equivalent.** Risks don't
  have per-MUST breakdowns. Treatment status is a single
  string, not a decomposition.
- **Migrate the risk short-circuit to Family C.** It stays
  Family A (intro-only) — the risk PROSE is still composed
  by `_answer_risk_query` and polished by the LLM. The new
  RiskCard[] just becomes additional metadata alongside the
  intro. Card render decorates the intro-only shape.

## Ship 22 progress

| Sub-arc | Status |
|---|---|
| **22'.a Design memo + eval + audit plan (this)** | **✓** |
| 22'.b Retire bridge footer | next |
| 22'.c RiskCard + retire risk footer | pending |
| 22'.d Eval + arc retrospective | pending |

## Related

- [[ship-21-prime-arc-retrospective-2026-07-23]] — the arc
  this one continues (retire-visible + keep-observability
  pattern)
- [[ship-14-prime-a-role-model-arc-2026-07-22]] — the risk
  feature this arc extends with card rendering
- [[ship-15-prime-d-demonstrates-sdk-2026-07-22]] — RiskDetail
  drill-in surface + the linked_controls shape RiskCard uses
- [[ship-1-14-bridge-footer]] (via
  `cross_framework_bridge_footer_2026_06_14`) — the original
  bridge footer this arc retires
