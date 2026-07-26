---
name: ship-46-prime-arc-retrospective-2026-07-26
description: "Ship 46' arc closer — engineering-review demo prep across chat/dashboard/documents/risks. Backfilled evidence_group_id (Stage-1: 327→129 groups, 60% collapse); installed sweep timer; prioritised backlog memo; canonical trace waterfalls documented; standalone HTML architecture + innovations brief."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 46' arc retrospective — engineering-review demo prep.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 46'.a | Audit checklist across all 4 surfaces | (inline) |
| 46'.b | Backfill script + sweep timer install + prioritised backlog | c9f3934 |
| 46'.c | Trace walk-through + HTML architecture brief | 9104a23 |
| **46'.d** | **Retro (this)** | pending |

## Delivered

### 46'.a — audit
Systematically walked the 4 demo surfaces (chat / dashboard / documents /
risks) + supporting infrastructure. Clean: API health, chat quality,
OTel spans render, Risk Register has 35 real risks, Evidence Package
renders as markdown, static UI serves. Polish opportunities: 190
pre-Ship-42 pending findings without evidence_group_id, missing sweep
timer, 0-Comply dashboard state.

### 46'.b — fixes
- **`scripts/backfill_evidence_group_id.py`** — idempotent script that
  computes evidence_group_id for legacy document_findings rows using
  the same normalize+sha1 as posture_writer. Ran on Arion:
  4245 rows backfilled with 54.8% collapse ratio. Stage-1 queue:
  327 → 129 unique groups (60% reduction in visual clutter).
- **Sweep timer installed** via `ops/install_sweep_timer.sh`.
  30-min cadence; runs fact_recompute + notification_delivery +
  overdue_followups + freshness_expiry.
- **Prioritised backlog memo** in `docs/memory/`. 🟢 Now / 🟡 Near /
  🔵 Strategic categorisation.

### 46'.c — brief
- **Canonical trace waterfalls** documented for chat + intake pipeline.
  Trace URLs work via SSH tunnel (Jaeger 16686, Phoenix 6006).
- **`docs/architecture_brief.html`** — 483-line standalone HTML
  deliverable for engineering-review audience. Renders in any
  browser, no CDN. Charter serif headings + system sans body + mono
  ASCII diagrams. Covers positioning, 4-layer architecture,
  datastore justification, 6 breakthrough innovations, live telemetry
  section, backlog, delivery velocity table.

## Chat latency note (for the demo)

Post-Ship 45.c on the deterministic short-circuit path: 3.5-7s. Post
Ship 45.c on the LLM path: 8-13s. **First chat after cache expiry can
be 30s** because compute_engine_verdicts runs inside load_posture on
cache miss. **Recommendation for demo**: fire a throwaway chat before
showing (warms tenant_context cache); subsequent chats stay fast.

Also: 0 Comply findings on Arion (all NC/OFI/N/A). Narrative framing:
"mid-cycle assessment showing what a struggling tenant looks like;
here's how the tool helps them close gaps." Alternative: force-mark
a few Comply for balance — dishonest, not recommended.

## Codified 2 lessons

### 1. Backfill scripts pay off retroactively

Ship 42 added `evidence_group_id` with `COALESCE(evidence_group_id,
id::text)` fallback for legacy rows. The fallback works but leaves
legacy rows visible as N-per-item, defeating the dedup. Backfill
was ~50 LOC + one run, and instantly upgraded 4245 rows across
one tenant.

**Rule**: when adding a group-key or lineage column with fallback
semantics, ship a matching backfill script in the same arc — even
if the immediate use case doesn't require it. When the demo /
scale need arrives (as here), the tool exists.

### 2. Standalone HTML beats a slide deck for engineering audiences

The `architecture_brief.html` renders in any browser, no build step,
no CDN dependencies, no PowerPoint. Engineering audience can:
- Read at their own pace
- Copy code snippets directly
- Click through to trace URLs (if tunneled)
- Search / annotate in their browser
- Re-open later for reference

**Rule**: for technical audiences, ship a self-contained HTML page.
Not markdown (needs rendering context), not PDF (breaks copy-paste),
not slides (linearizes non-linear content).

## What Ship 46 did NOT do

- **Force-mark Comply findings** — dishonest; narrative framing works
- **Trim Stage-1 queue below 129** — after backfill the shape is
  demo-friendly + realistic
- **Fix the 30s cold-cache chat latency** — needs deeper investigation
  into `_apply_engine_overlay`; recommendation is warmup before demo
- **UI polish across static/arioncomply.html** — the dejargonize pass
  (2026-07-01) already covered visible surfaces
- **Screenshots of Jaeger + Phoenix UIs** — text descriptions in the
  HTML brief; live UIs will render better than screenshots

## Deferred / follow-on candidates from Ship 46

- **`_apply_engine_overlay` optimization** — cold-cache chat is 30s
  because compute_engine_verdicts runs O(N) curated controls; possible
  fix is TTL cache on posture (not just eval_ctx) or lazy overlay
- **Screenshot capture pipeline** — for a screencast-friendly
  demo, capture actual Jaeger/Phoenix screenshots to embed in the
  HTML brief
- **Live demo dry-run** — walk the actual demo script through each
  surface once before showing; note anything embarrassing

## Related

- [[ship-46-prime-b-prioritised-backlog-2026-07-26]] — the backlog
- `scripts/backfill_evidence_group_id.py` — reusable backfill helper
- `docs/architecture_brief.html` — the engineering-review deliverable
- `ops/install_sweep_timer.sh` — the sweep installer (predates Ship 46)
- All Ship-N' retrospectives referenced in the HTML brief
