---
name: ship-20-prime-a-short-circuit-design-2026-07-23
description: "Ship 20'.a — design memo for extending Ship 18 structured payload to the 15 short-circuit paths in arion_graph.py; per-site card shapes + CaseFileShim helper so build_related_cards works without a CaseFile"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 20'.a — opens Ship 20 arc (structured payload for
short-circuits). Ship 18 shipped structured chat responses via
the case-file (LLM) path only. Ship 19 polished the render.
Ship 20 extends the same UX to the 15 deterministic short-circuit
paths in `arion_graph.py`.

## Inventory of the 15 short-circuit sites

| # | Line | Query family | Data shape | Target cards |
|---|---|---|---|---|
| 1 | 2147 | Deictic clarify | No refs, prose only | Intro only (clarify text); actions=[]; related=[] |
| 2 | 2242 | Stage-1 acknowledge gap | Single ref | Intro (ack summary); actions=[]; related=[1 card for the ref] |
| 3 | 2308 | Stage-1 review (list/approve/reject) | 0-1 ref (control-scoped) or N refs (queue list) | Intro (action summary); actions=[]; related=[N cards for enumerated refs] |
| 4 | 2376 | Stage-2 engine-verdict approval | Same shape as Stage-1 | Same shape as Stage-1 |
| 5 | 2402 | Scope N/A response | No refs, prose | Intro only |
| 6 | 2432 | Cascade follow-ups | No refs, prose | Intro only |
| 7 | 2454 | Risk register | No refs, prose (has its own risk-cards surface elsewhere) | Intro only |
| 8 | 2470 | Cascade suppressions | No refs, prose | Intro only |
| 9 | 2487 | Cascade implications | 0-1 ref (query-extracted) | Intro; related=[1 card if ref present] |
| 10 | 2514 | Timeline query | Single ref | Intro; related=[1 card for the ref] |
| 11 | 2555 | Upload status (doc inventory) | No refs, prose | Intro only |
| 12 | 2605 | Resolver short-circuit | cited_refs=[] by convention | Intro only |
| 13 | 2678 | Posture enumeration (deterministic) | N refs (all cited) | Intro (summary count); actions=[]; related=[N cards for cited refs] |
| 14 | — | (LLM case-file flow — Ship 18/19, unchanged) | — | intro + actions[] + related[] (existing) |
| 15 | 2151 | (Deictic clarify — same as #1) | — | — |

Note: sites #14 + #15 collapse in the counting; effective 15
short-circuit sites but 12 distinct card-shape families.

## Card-shape families

Three broad families emerge from the inventory:

### Family A — Intro-only (no refs)
Sites: deictic_clarify (2147), scope_na (2402), cascade_followups
(2432), risk (2454), cascade_suppressions (2470), upload_status
(2555), resolver_short_circuit (2605).

Payload:
```
{
  intro: { text: <composed prose>, primary_ref: null },
  actions: [],
  related: []
}
```

Card render: single intro bubble. Same visual as the current prose
render — but consistency with the LLM path. Templates/advisory
already off for these sites.

### Family B — Single-ref (intro + 1 related card)
Sites: acknowledge_gap (2242), cascade_implications (2487), timeline
(2514).

Payload:
```
{
  intro: { text: <prose>, primary_ref: <ref> },
  actions: [],
  related: [<RelatedCard for the ref>]
}
```

Card render: intro + 1 related card (verdict badge, evidence
summary, leaves checklist if applicable). Frontend already handles
this via Ship 18/19 rendering.

### Family C — Multi-ref list (intro + N related cards)
Sites: stage1 (2308), stage2 (2376), posture_enumeration (2678).

Payload:
```
{
  intro: { text: <count summary>, primary_ref: null },
  actions: [],
  related: [<N cards, one per enumerated ref>]
}
```

Card render: intro + N related cards. For enumeration queries
(30+ NCs), this could be a LOT of cards. Cap at ~15 in the intro
+ note "showing 15 of N; full list in dashboard". Or: paginate.
Design decision → cap at 15, note the total in intro.

## The shared refactor: CaseFileShim

`build_related_cards(cf, structured, ...)` currently requires a
`CaseFile` for role/verdict/relation lookup. Short-circuits don't
have one. Two clean options:

**Option A** — build a lightweight `CaseFile` via `SimpleNamespace`
(the same pattern `_casefile_flow` already uses at line 1132).
Requires marshalling posture + tenant scope into the expected shape.

**Option B** — extract a `CaseFileShim` class in `answer_augment.py`
that duck-types the methods `build_related_cards` needs:
`all_nodes()`, `posture_for(ref)`, `needs_draft_tag(ref)`,
`role_of(ref)`, `demonstrated_by(ref)`.

**Choice: Option B.** Cleaner call sites (one `CaseFileShim(tenant,
posture)` construction vs. per-site SimpleNamespace boilerplate).
Reusable across all short-circuits. Doesn't touch `build_related_cards`
signature (no downstream ripple).

Shim implementation:
```python
class CaseFileShim:
    def __init__(self, tenant, posture, node_lookup=None):
        self.tenant  = tenant
        self._posture = posture or {}
        self._node_lookup = node_lookup or {}  # {ref: (title, standard_id)}

    def all_nodes(self):
        # short-circuits typically don't carry resolved graph nodes
        return []

    def posture_for(self, ref):
        # posture keyed by node_id; short-circuits pass a pre-indexed
        # dict keyed by ref for convenience
        return self._posture.get(ref)

    def needs_draft_tag(self, ref):
        rec = self.posture_for(ref) or {}
        # replicate CaseFile.needs_draft_tag logic
        return (rec.get("finding") in ("NC", "OFI", "Comply")
                and rec.get("confirmation_status") not in
                    ("system_confirmed", "auditor_confirmed"))

    def role_of(self, ref):
        # Use tenant scope's role_map (already populated per Phase 1
        # framework-role-model-arc)
        rec = self.posture_for(ref) or {}
        sid = rec.get("standard_id") or self._node_lookup.get(ref, ("", ""))[1]
        if not sid or self.tenant is None:
            return None
        scope = getattr(self.tenant, "scope", None)
        # Reuse the same role-map lookup CaseFile does
        return _role_from_scope(scope, sid)

    def demonstrated_by(self, ref):
        rec = self.posture_for(ref) or {}
        return list(rec.get("demonstrated_by") or [])
```

Plus a helper to build the node_lookup for a set of refs by querying
Neo4j (batch fetch: `MATCH (rn:RequirementNode) WHERE rn.control_ref
IN $refs RETURN rn.control_ref, rn.title, rn.standard_id`).

## Sub-arc plan

### 20'.b — Family A (7 sites, intro-only)
- Build `CaseFileShim` + shared `build_short_circuit_structured()`
  helper in `answer_augment.py`.
- 7 sites just pass composed answer_text as intro; return
  StructuredAnswer with actions=[] and related=[].
- All 7 already have `attach_templates=False`, `attach_advisory=False`;
  no additional payload changes.
- Frontend: no changes needed (Ship 18/19 renderer handles
  intro-only fine).

### 20'.c — Family B (3 sites, intro + 1 related)
- Same shim; each site builds a 1-ref RelatedCard via
  `build_related_cards(shim, ...)`.
- Sites: acknowledge_gap, cascade_implications, timeline.
- Extra: fetch title + standard_id for the single ref via Neo4j
  (or reuse from `_control_entity` if it carries them).

### 20'.d — Family C (3 sites, intro + N related, capped 15)
- Stage-1 + Stage-2 + posture_enumeration.
- Enumerate the refs from the site's listing data; batch-fetch
  titles from Neo4j; build up to 15 RelatedCards.
- Intro summary: "You have N pending Stage-1 findings across M
  controls (showing 15)." + "See full queue in the dashboard →"
  link.
- Frontend: consider a `sa-related-showing` chip that indicates
  "showing 15 of 47" — small UI addition.

### 20'.e — Eval + arc retrospective
- Full eval regression check. Baseline should stay 231/232.
- Manual visual verification of each family on real queries.
- Arc retrospective.

## Design decisions locked in 20'.a

1. **CaseFileShim over SimpleNamespace boilerplate.** Reusable
   duck-typed helper; one construction per short-circuit; keeps
   `build_related_cards` signature unchanged.

2. **Family A intro-only is a legit target shape.** Not every
   response needs cards; some (clarifications, no-refs summaries)
   are naturally single-bubble. Intro-only structured payload gives
   the frontend a uniform envelope AND lets the intro-render code
   apply consistently.

3. **Cap Family C enumeration at 15 refs.** 30+ cards would
   overwhelm the chat surface. Intro summarises total; drill-in to
   dashboard for the full list. Matches auditor mental model
   (chat is a triage surface; dashboard is the full inventory).

4. **Short-circuits DO NOT get JSON-mode LLM.** They already have
   deterministic prose (some go through `polish_short_circuit_answer`
   which is a prose LLM call, NOT JSON mode). Ship 20 doesn't
   change that. We wrap the existing prose as intro.text.

5. **`answer_text` still composed the same way.** Backend-composed
   prose stays in `answer_text` (backward compat for SDK / prose
   consumers). `answer_structured` is additive; frontend prefers
   cards when present, falls back to prose otherwise.

6. **No changes to `attach_templates` / `attach_advisory`
   defaults.** Ship 20 doesn't touch what the envelope currently
   attaches for each site. Structured payload is a parallel
   enrichment.

## What Ship 20 does NOT do

- **Change LLM path** (site #14). It already emits structured;
  no changes.
- **Migrate the resolver's own short-circuit branch** at line 2595.
  That's the "resolver found a direct Postgres answer" path and
  is one of the 15 sites (counted as site #12 above); it gets
  Family A treatment.
- **Redesign risk cards.** The risk short-circuit (2454) has its
  own richer visualization elsewhere in the UI (`renderRisks` +
  `showRiskDetail`). Ship 20 just wraps its chat prose in an
  intro-only structured payload; the risk-drill UI stays.
- **Backfill historical chat_casefile_log rows.** Only the
  case-file (LLM) flow logs there. Short-circuits don't touch
  the log; Ship 20 doesn't add new logging paths.
- **Retire `polish_short_circuit_answer`.** The prose polish call
  in postgres+llm sites stays — we wrap its output as intro.text,
  not replace it.

## Ship 20 progress

| Sub-arc | Status |
|---|---|
| **20'.a Design memo + per-site inventory (this)** | **✓** |
| 20'.b Family A: intro-only (7 sites) | next |
| 20'.c Family B: intro + 1 related (3 sites) | pending |
| 20'.d Family C: intro + N related (3 sites, capped 15) | pending |
| 20'.e Eval + arc retrospective | pending |

## Related

- [[ship-18-prime-arc-retrospective-2026-07-23]] — the LLM-path
  structured payload arc Ship 20 extends
- [[ship-19-prime-arc-retrospective-2026-07-23]] — the card polish
  arc providing the render this arc feeds into
- [[framework-role-model-arc]] — the role model that
  `CaseFileShim.role_of` reuses
- [[dejargonize-ux-pass-2026-07-01]] — the consistency-across-
  surfaces principle Ship 20 extends to chat card rendering
