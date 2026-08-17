---
name: ship-76-prime-priming-2026-08-17
description: "Ship 76' priming note. Ship 75'.f investigation of eval case #5's rare 'physical' trip surfaced a systemic gap: Ship 66'.a's applicability_status SSoT is enforced at 3 sites only; N/A dominance has NOT cascaded exhaustively. 6 LEAK sites catalogued (RelatedCard builder, digest xfw_bridges + demonstrated_by, dashboard endpoint, external API bulk + detail). Ship 76' will do the cascade fix — priming here so a future session picks up context cleanly."
metadata:
  type: project
  ship: "76'"
---

# Ship 76' priming note

Not a full design doc — a stub so future work picks up cleanly.
Ship 76' proper starts with 76'.a (design doc + sub-arc plan).

## Why Ship 76'

Ship 75'.f investigation of eval case #5's rare "physical" trip
surfaced the root cause: `A.7.2 DEMONSTRATES Art.32` edge in Neo4j
pulls A.7.2 (Physical entry, N/A on cloud tenants) into
`build_related_cards` as a demonstrator card. The card renders as
"A.7.2 — N/A" in tenant chat answers. Case #5's `must_not_contain=["physical"]`
trips.

Fix attempt was going to be a filter in `build_related_cards`, but
that would have been a THIRD copy of a predicate that already exists
in 2 other places. User pushed back on SSoT grounds ("we are trying
to make sure there is only one truth").

Broader audit revealed the pattern is systemic: Ship 66'.a
introduced `posture_controls.applicability_status ∈ {applicable, na}`
as scope SSoT, but Ship 66'.b/c/d enforced at only 3 sites:

1. `rag/posture_loader.py:324` — engine-overlay guard
2. `rag/posture/stage2_approval_chat.py:339` — Stage-2 approval
3. `rag/casefile/digest.py:290` — OBLIGATIONS section render

## LEAK sites catalogued (2026-08-17 audit)

Every posture-rendering surface that reads posture data but doesn't
check `applicability_status`:

| File:line | Surface | Leak shape |
|-----------|---------|------------|
| `casefile/answer_augment.py:1054` `build_related_cards` | Tenant chat "## Related controls" | Case #5 confirmed: A.7.2 renders when Art.32 cited |
| `casefile/digest.py:180` `_render_xfw_bridges` | LLM digest XFW BRIDGES | N/A primary refs in bridge lines |
| `casefile/digest.py:486` `_render_demonstrated_by` | LLM digest DEMONSTRATED BY | N/A demonstrators surface |
| `api_server.py:2792` `/api/v1/dashboard/posture` | Dashboard heatmap | N/A in theme buckets |
| `rag/external/endpoints/posture.py:118` bulk endpoint | External API | Partners see N/A as assessed |
| `rag/external/endpoints/posture.py:248` detail endpoint | External API | N/A drillable via API |

Plus 1 FINDING-CHECK site (works today via legacy `finding == "N/A"`
mirroring but not the SSoT):

| File:line | Site |
|-----------|------|
| `casefile/digest.py:121` `_rank_posture_refs` | Uses `finding` column, should migrate to `applicability_status` |

## Sub-arc sketch (to be firmed up in 76'.a)

- **76'.a** — Full design doc + audit table with per-site policy
  (hard-filter vs soft grounding-carve-out per Ship 66'.c model).
- **76'.b** — Promote `CaseFile.in_scope(ref) -> bool` as the SSoT
  predicate (delegates to `applicability_status`). Migrate CLEAN
  sites + the FINDING-CHECK site to use it. No behavior change,
  just SSoT consolidation.
- **76'.c** — Fix casefile LEAK sites (build_related_cards soft,
  xfw_bridges + demonstrated_by hard). Dogfood: re-run case #5
  stress test 50+ times, confirm 0 physical leaks.
- **76'.d** — Fix API LEAK sites (dashboard hard, external bulk
  soft with `?include_na=true` opt-in, external detail hard 404 on
  N/A). External API contract change — needs OpenAPI schema note.
- **76'.e** — Retro + close.

## Design decisions to lock in 76'.a

- `CaseFile.in_scope(ref)` treats missing rows as in-scope (not
  N/A) — preserves current behavior for unassessed-but-applicable
  refs.
- Per-site policy: hard filter (drop always) vs soft grounding
  carve-out (drop unless LLM cited) per surface family. Mirrors
  Ship 66'.c's obligations rule.
- External `GET /posture/{ref}` returns 404 on N/A (D3 candidate).
  Contract change; document in endpoint OpenAPI.
- Retire `finding == "N/A"` scope checks; use SSoT predicate.

## Cross-arc pattern

Ships 66 → 76 mirror Ships 72 → 74 → 75:
- Ship 66 (schema SSoT + 3 critical enforcement) → Ship 76
  (exhaustive cascade)
- Ship 72 (contract SSoT) → Ship 74 (observability) → Ship 75
  (extractor coverage)

Same shape: SSoT introduced with strategic enforcement, then a
follow-up arc completes the cascade across every consumer.

## Follow-on: eval case #5 stays potentially-flaky until 76'.c ships

Rare stochastic depending on LLM voluntarily citing Art.32.
Baseline still 231-233/233; 76'.c will lock it deterministically.
