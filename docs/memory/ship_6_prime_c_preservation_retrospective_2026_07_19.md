---
name: ship-6-prime-c-preservation-retrospective-2026-07-19
description: "Ship 6'.c — data-driven retrospective on the case-file preservation-check repair pass"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 6'.c (2026-07-19) — a data-driven look at how often the
case-file preservation-check repair pass fires, what it fires on,
and what that tells us about the balance between digest + LLM +
repair.

The case-file flow is documented at
[[ship-2-prime-casefile-arc-2026-07-15]]. Its repair-pass is
APPEND-ONLY: never rewrites LLM prose, only adds a footer for
elements the LLM stochastically dropped. Ship 6'.a called this
out as a load-bearing safeguard; Ship 6'.c asked: *how load-
bearing?*

## Dataset

`chat_casefile_log` from 2026-07-15 (arc opened) through
2026-07-18 21:33 UTC: **1417 turns, 0 errors**.

## The headline number

**87.7% of turns fire ≥1 repair event.**

- 1243 / 1417 turns had `repair_events_count > 0`
- Modal turn has 4 events (24% of turns)
- Distribution: 0/12%, 1/2%, 2/19%, 3/15%, 4/24%, 5/17%, 6/11%, 7/0.1%

Per-day trend:

| day | turns | repaired | pct |
|---|---|---|---|
| 2026-07-15 | 56 | 34 | 60.7% |
| 2026-07-16 | 291 | 261 | 89.7% |
| 2026-07-17 | 638 | 581 | 91.1% |
| 2026-07-18 | 432 | 367 | 85.0% |

The 07-15 low is Ship 2'.a shipping day when the case-file was
still gated. 07-16 was Ship 2'.n retiring the legacy fallback —
every turn since goes through repair. Steady-state is ~87-91%.

## What kinds of events fire

Total 4693 repair events across 1417 turns.

| kind | occurrences | pct |
|---|---|---|
| `missing_draft_near_ref` | 1751 | 37.3% |
| `missing_ref` | 1532 | 32.7% |
| `missing_verdict_near_ref` | 1105 | 23.6% |
| `missing_bridge_footer` | 301 | 6.4% |

The three ref-adjacent kinds together are 94% of all events. So
the failure mode is **LLM cites a ref but drops one of the
annotations we require adjacent to it** (`[DRAFT]` tag,
NC/OFI/Comply verdict), or **LLM omits a ref entirely** despite
having posture data in the digest.

`missing_bridge_footer` at 6.4% confirms Ship 1.14's deterministic
bridge-footer fix is doing its job — the LLM only drops the
xfw-bridge line on ~6% of turns and repair catches those.

## By question_type — some intents ALWAYS fire repair

| question_type | turns | repaired | pct | avg events |
|---|---|---|---|---|
| `document_inventory` | 99 | 99 | 100.0% | 4.89 |
| `cross_framework` | 137 | 137 | 100.0% | 3.80 |
| `posture_check` | 368 | 367 | 99.7% | 2.63 |
| `document_content` | 71 | 69 | 97.2% | 3.70 |
| `definition` | 191 | 177 | 92.7% | 3.63 |
| `gap_analysis` | 450 | 323 | 71.8% | 3.12 |
| `implementation` | 101 | 71 | 70.3% | 3.52 |

`document_inventory` + `cross_framework` are **100%** — the LLM
never once managed to render these without missing an element.
`posture_check` at 99.7% is basically also 100%. These are all
intents where the digest is dense with refs + postures that MUST
survive.

`gap_analysis` + `implementation` at ~70% are relatively better —
they're free-form guidance queries where the LLM has more prose
freedom and fewer strict citations.

## Top-dropped refs (heavy hitters)

Refs the LLM most often drops or drops annotations from:

| ref | drops |
|---|---|
| 10.2 | 296 |
| A.5.15 | 271 |
| A.8.3 | 263 |
| A.5.18 | 234 |
| 10.1 | 228 |
| A.5.36 | 211 |
| A.5.10 | 186 |
| 6.1.2 | 157 |
| A.8.2 | 148 |
| Art.32.1.d | 134 |

These are Arion's most-cited controls (baseline NC controls that
show up in almost every query touching access / identity /
policy / management-review). High-volume drop count is partly a
consequence of high citation volume — not necessarily
LLM-specific weakness on these refs.

## Latency cost of repair

| turns with repair | avg digest ms | avg repair ms | avg total ms | repair pct |
|---|---|---|---|---|
| 1243 | 5 | 3 | 4615 | 0.1% |

**Repair is essentially free** — 3 ms average, 0.1% of turn time.
The audit-completeness win costs nothing.

## Interpretation

Two competing readings:

**Reading 1: repair is essential, LLM freely drops.**
The LLM stochastically drops mandatory annotations on almost
every turn. Without the repair pass, ~87% of answers would
silently omit `[DRAFT]` tags, verdicts, or cited refs that had
posture data. Repair is load-bearing.

**Reading 2: the digest under-sells the preservation-critical
elements.**
The dominant failure is `missing_draft_near_ref` — the LLM keeps
losing the `[DRAFT]` tag. If the digest surfaced DRAFT status
more prominently, or the system prompt stressed "preserve DRAFT
tags", the LLM might drop it less often, reducing repair-
dependence.

Both are true. Reading 1 justifies keeping repair as-is; Reading
2 suggests digest tuning is a good next investment.

## Verdict — is this a bug or a feature?

**It's a feature.** The design contract from
[[ship-2-prime-casefile-arc-2026-07-15]] was:

> LLM drafts + polishes prose; deterministic repair guarantees
> that audit-critical elements survive.

87.7% is high but the pass is APPEND-ONLY — it never rewrites the
LLM's prose. Users get natural language + a `↳ Compliance facts`
audit footer at the bottom. Auditor completeness is preserved
without capping LLM creativity.

The concern would be if repair started REWRITING prose (it
doesn't) or if it were expensive (it isn't — 3ms).

## Follow-ups (deferred, not shipped in this arc)

1. **Digest DRAFT-prominence experiment** — try emitting DRAFT-
   status refs in a dedicated `DRAFT POSTURES (must keep tag)`
   section of the digest. If `missing_draft_near_ref` drops
   materially, we know digest structure was the constraint.

2. **System-prompt DRAFT emphasis** — add an explicit line to
   the slim system prompt: "Preserve `[DRAFT]` tags — they
   signal to auditors that this posture is unconfirmed." A/B
   against the current prompt.

3. **Alerting** — a sudden drop in repair rate might mean the
   digest is regressing (LLM sees less to cite); a sudden spike
   might mean a new model is behaving differently. Worth a
   Grafana panel eventually.

4. **Per-intent tuning** — `document_inventory` at 4.89 avg
   events/turn suggests the digest for that intent might benefit
   from a compact format that surfaces every doc's ref inline
   rather than the LLM reconstructing them.

Not committing any of these in Ship 6'.c — this is a
retrospective arc. Insights feed Ship 6'.d+ or later.

## Baseline

No code changes. No eval impact. Read-only analysis.

## Ship 6' progress

| Sub-arc | Status |
|---|---|
| 6'.a Role audit + safeguard inventory | ✓ |
| 6'.b Grounding provenance column + tests | ✓ |
| **6'.c Preservation-check retrospective** | **✓** |
| 6'.d Chat prose claim-check | next |
| 6'.e Joined LLM decision-trail view | pending |
| 6'.f Arc retrospective | pending |

## Related

- [[ship-6-prime-a-llm-role-audit-2026-07-18]] — parent audit
- [[ship-6-prime-b-grounding-provenance-2026-07-18]] — 6'.b
- [[ship-2-prime-casefile-arc-2026-07-15]] — arc that shipped
  the preservation-check + repair pass
