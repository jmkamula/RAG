---
name: ship-46-prime-b-prioritised-backlog-2026-07-26
description: "Ship 46'.b prioritised backlog for engineering review + subsequent arcs. Ranked by (impact × ease). Front-of-queue items are demo-adjacent polish; back-of-queue items are strategic bets deferred from earlier arcs."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 46'.b — prioritised backlog for engineering review + follow-on arcs.

Legend:
- 🟢 **Now** — visible in the demo; ship before showing
- 🟡 **Near** — Ship 47-50 range; near-term follow-on
- 🔵 **Later** — strategic; needs product decision

## 🟢 Demo-adjacent (ship this week)

### A1. Backfill evidence_group_id on legacy findings — DONE (Ship 46'.b)
- 4245 legacy rows backfilled; 54.8% collapse ratio
- Stage-1 queue: 327 → 129 unique groups
- `scripts/backfill_evidence_group_id.py` (idempotent, reusable)

### A2. Install periodic sweep timer — DONE (Ship 46'.b)
- systemd unit installed via `ops/install_sweep_timer.sh`
- Fires every 30 min; runs fact_recompute + notification_delivery +
  overdue_followups + freshness_expiry sweeps

### A3. Trace walk-through documentation (Ship 46'.c) — PENDING
- Capture 2 representative trace IDs (one intake pipeline, one chat)
- Screenshot-worthy: Jaeger service map + waterfall; Phoenix
  LLM-first UI with prompts
- Include in engineering-review brief

### A4. Architecture + innovations brief (Ship 46'.c) — PENDING
- HTML deliverable for engineering-review audience
- Final architecture choices + breakthrough innovations across 44 arcs
- Focus: framework role model, case-file discipline, consensus
  extraction, dedup at surface, dual-backend OTel tracing

### A5. UI framing for 0-Comply demo state — DEFERRED (see A5-note)
- Dashboard shows 183 NC + 17 OFI + 0 Comply — reads as "all failing"
- Options: (a) demo narrative frames it, (b) add UI annotation
  "Mid-cycle assessment; 45% assessed"
- Recommend option (a) for engineering review; option (b) is a
  follow-on if we're showing to less-technical audiences

## 🟡 Near-term (Ship 47-52)

### B1. build_related_cards internal profile (Ship 45 deferred)
- Ship 45'.c fixed the biggest N+1 but build_related_cards still
  4.5s on LLM path
- Ship 46'.c traces will show exactly where the remaining time goes
- Ship 47 candidate: batch _classify_relation + _node_metadata calls

### B2. Retrieve LLM-path pipelining
- Currently rank_and_answer LLM → augment_and_repair sequential
- Could stream LLM tokens while augment prepares related cards
- ~2s potential savings; higher risk of regression

### B3. fingerprint_keyword consensus hotspot (Ship 44 finding)
- Ship 44 showed 7.8s in fingerprint_keyword during consensus extraction
- Ship 46'.c traces will show which leaves dominate
- Ship 48 candidate: per-leaf timing + per-fingerprint cache

### B4. Broader-doc eval on Arion's 68 other docs (Ship 41 backlog)
- Ship 41-43 covered 5 Ship 10 baseline docs
- Extending to 68 docs would validate consensus + BM25 signal quality
  at scale
- Half-day arc: re-extract subset + HITL sample

### B5. Persistent Jaeger + Phoenix storage
- Currently in-memory Jaeger + SQLite Phoenix
- For post-demo continuous observability: badger for Jaeger,
  Postgres for Phoenix
- Ship 49 candidate

## 🔵 Strategic (needs product decision)

### C1. Default-ON USE_CONSENSUS_EXTRACTION
- Consensus opt-in on Arion demo since Ship 36
- Ship 41 HITL + Ship 42 dedup + Ship 43 BM25 make the arc mature
- Blocker: broader-doc eval (B4) + retirement plan for legacy
  fingerprint+critic+concat paths

### C2. Multi-tenant broader eval
- Only Arion tenant has real docs
- Bringing on 2-3 test tenants would validate cross-framework
  extraction + role model across doc variety
- Requires tenant onboarding UX + demo tenant provisioning script

### C3. LLM cost tracking + budgets
- OTel captures token counts (Ship 44) but no per-tenant budget UI
- Ship 43 introduced BM25 which is free but LLM calls (consensus
  arbiter + chat) are the real cost
- Ship 50+: dashboard card showing "$/tenant/month" + rate limits

### C4. External API webhook subscriptions
- Ship 4 shipped external REST API + Python SDK
- Deferred: webhook subscriptions for
  posture-change / new-finding / cascade-event
- Ship 4'.h deferred candidate; still open

### C5. Retire legacy pipelines
- After default-ON (C1): delete fingerprint+critic+concat code
  paths from extractor
- After Ship 2'.n case-file locked: retire final legacy chat prose
  helpers
- Bigger commit; needs release notes

## Deprioritized / not-doing (unless a demo demands)

- **Force-mark Comply findings for demo balance** — dishonest; framing narrative better
- **Reduce Stage-1 queue below 129** — current shape is realistic
- **Streamline UI with less prose** — post-dejargonize (2026-07-01)
  UI is already tenant-friendly
- **Add per-tenant customization to Jaeger/Phoenix** — engineering review
  sees one tenant

## Related

- All Ship N' retrospectives in `docs/memory/`
- Ship 46'.a audit findings (this arc)
- CLAUDE.md build sequence — canonical arc-completion status
