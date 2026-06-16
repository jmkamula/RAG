---
name: strategic-pause-2026-06-15
description: "2026-06-15 audit/cleanup day. 29 commits shipped: TOC filter, schema_v41 intake quality, per-MUST binding in extractor (B), 64 catalogs, crosscheck (schema_v42), then a deliberate pause to write 4 strategy docs (intake architecture, LLM provider, 27701 readiness, road to MVP). Rule surfaced: don't default to production-grade everything — push back to actual blockers. Five honest MVP blockers identified, ~6-9 days work, two-week sprint scoped."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## The arc

Started as a continuation of yesterday's eval-offenders thread. Shipped:

- **TOC filter** (`5216168`) + cleanup of 47 stranded findings
- **Eval state-drift re-author of #2** (`564c737`) — closed the last
  formally-known-stale case
- **Intake quality signals v41** (`7d5c30d` + `45f20fa`) — dashboard
  couldn't see its own catches; schema_v41 + inert-findings flag +
  legacy-fallback yield suppression
- **Per-MUST binding in extractor** (`307dbdc`) — structural fix; the
  extractor now sets `checklist_item_id` when doc_mappings narrows to
  target_leaves
- **64 autogen catalogs** (`9f4b7dc`) + `--cap-fanout` filter
- **Catalog crosscheck** (`732d0a5`, schema_v42) — extractor's
  LLM-emitted bindings now validated against the must_fingerprints
  catalogs; soft signal, dual-purpose catalogs (back-bind + 2nd opinion)
- **5 spurious leaf-scan approvals** reverted via DB UPDATE with
  audit-trail rejection_reason

29 commits in the day. Eval held 197-199/199 throughout. Yellow count
on Arion went 2 → 13 (honest signal exposed) → 10 (after expansion +
filter work).

## The pause shift

Mid-day the user pushed back: *"we keep bumping up the code each time
we find a gap, where is our code right now? i worry we might lose
control of the code"*.

The pause that followed produced **4 strategy docs in `docs/`**:

1. **`docs/intake_pipeline_architecture.md`** — one-page reference for
   the 3 finding-producing paths (doc extraction / workbook / leaf-scan
   back-bind), their stages, failure modes & guards, cross-cutting
   concerns (telemetry-coordination pair rule, finding state machine,
   schema migration discipline).
2. **`docs/llm_provider_strategy.md`** — provider abstraction strategy.
   Drivers: privacy + vendor independence. Five-phase path (abstraction
   first, specific provider second). Cost framing: self-hosted only
   beats cloud at ~10K tenants.
3. **`docs/framework_readiness_27701.md`** — first multi-framework
   expansion brief. 27701 has highest pre-staged readiness (code stubs
   exist in `framework_refs`, `enricher`, `workbook_importer`); 0
   Neo4j data. 6-phase ~5-7 day plan. 5 architectural stress-tests
   to watch for.
4. **`docs/road_to_mvp.md`** — path to first paying customer.
   Five blockers, ~6-9 days, two-week sprint. Cloudflare Access +
   Entra ID for auth+authz. Cold-standby HA Tier 1 (manual failover,
   30-60 min RTO).

The 4 docs are NOT memory entries (they're persistent architectural
references). This memory entry just makes them discoverable from
the memory index.

## Rule surfaced

**Don't auto-engineer "production-grade everything" defaults — push
back to actual blockers.**

When the user asked "why hosted Postgres?" I had reflexively listed
managed Postgres, HA load balancers, multi-region — all
production-SaaS defaults. The honest MVP infra is:
- Self-hosted Postgres + cron `pg_dump` to blob
- Single VM with systemd respawn (no load balancer)
- Cloudflare in front of Cloudflare Tunnel (no public IP exposure)
- VM2 cold standby with documented restore (no streaming replication)

This shrunk the MVP-deploy estimate from "weeks" to ~5 days.

The rule generalises: when listing "what's needed", check whether each
item is a *blocker* or a *best-practice default*. For MVP, ship the
blockers; defer the defaults.

Sibling rules: [[feedback-anchor-before-choices]] (explain plan before
offering choices), [[feedback-telemetry-before-trouble]] (build
observability alongside, not after).

## What today's work made structurally cleaner

| Before today | After today |
|---|---|
| Doc-side extraction never set `checklist_item_id` | Set natively when doc_mappings matches |
| Dashboard couldn't see filter outcomes (questionnaire / TOC) | Schema v41 captures them; dashboard surfaces |
| Catalogs were leaf-scan-only assets | Catalogs are dual-purpose (back-bind + extractor 2nd opinion) |
| Architecture mental model lived in 80+ memory entries | One-page diagram + 3 supporting strategy docs |
| Yellow count on dashboard was 2 (false-clean) | Yellow count is 10 (honest signal) |
| 3 formally-known-stale eval cases | 0 known-stale; #16 jitter within band |
| Schema at v40 | Schema at v42 (additive only) |

## Open for next thread

In rough strategic priority (per the 4 strategy docs):

1. **Refine the 64 autogen catalogs** (high leverage at multi-framework
   scale; crosscheck telemetry will reveal which to prioritize)
2. **27701 onboarding** — the first multi-framework stress-test
   (~5-7 days, fully scoped in framework_readiness_27701)
3. **LLM provider abstraction Phase 1** — when privacy/sovereignty
   signal appears (~2 days for the abstraction, then Mistral cloud
   addition in ~3 days)
4. **Road to MVP sprint** — when first paying customer signal appears
   (~6-9 days focused work in a 2-week sprint)
5. **Target-side fanout filter on leaf-scan** — catches today's
   Art.26 ×3 cross-doc fanout pattern (~30 min code, not yet built)
6. **PDF Layer A (pdfplumber + markdown)** — closes 60-70% of the
   PDF extraction gap (~1 day)

## Related

- [[intake-quality-signals-v41-2026-06-15]] — schema_v41 work
- [[per-must-binding-in-extractor-2026-06-15]] — the structural fix
  (B path)
- [[extractor-toc-filter-2026-06-15]] — doc-shape filter family member
- [[extractor-catalog-crosscheck-2026-06-15]] — crosscheck telemetry
- [[feedback-eval-state-drift]] — the eval-decay rule applied to #2
- [[feedback-anchor-before-choices]] — sibling pushback discipline
- [[feedback-telemetry-before-trouble]] — pair rule reinforced today
- [[curation-phase-b-retrospective]] — the prior arc-level summary
  this builds on; both demonstrate the value of arc-level memory
  alongside per-commit detail
