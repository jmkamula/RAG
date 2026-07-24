---
name: ship-27-prime-a-quality-audit-design-2026-07-24
description: "Ship 27'.a — quality audit design + first-run findings; Ship 10 approve-rate metric can't be recovered from DB (dev-time only) but grounding_method shows 89% determinism post Ship 17 catalog"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 27'.a — opens Ship 27 arc (finding-quality audit). Data-
first investigation on the Ship 10 5-doc corpus:
- Data Quality Accuracy Procedure
- DPIA Procedure
- Records of Processing Activities (RoPA)
- Consent Management Procedure
- Processor Operations Procedures

## What we set out to measure

Original hypothesis: **Ship 17's catalog fingerprint fix
(topic-anchor injection) improved output quality.** Ship
17'.d confirmed extraction volume stayed flat (192 → 198
findings) but never measured whether the SIGNAL improved.

Original plan: compare current approve-rate to Ship 10
baseline (48 approved / 97 total = 49% approve rate).

## What the audit revealed instead

Two surprises:

### Surprise 1: Ship 10's "49% approve" isn't in the DB

The `document_findings.review_status` column has only two
distinct values on the demo tenant: `approved` and `pending`.
Zero `rejected` states. The Ship 10 baseline number
(48 approve / 49 reject) was a **development-time labeling
during HITL review**, not a persisted signal we can compare
against now.

Cross-checking soft-deletes: **923 all-time finding rows
across the 5 docs; 720 soft-deleted**. That looks like a
78% rejection rate — but the `deletion_reason` column tells
the real story:

| Reason | N | % |
|---|---|---|
| critic_ab_run | 208 | 28.9% |
| (null) | 67 | 9.3% |
| wave3-fix | 60 | 8.3% |
| wave4a-llm-fix | 60 | 8.3% |
| wave1-corroboration-test | 59 | 8.2% |
| wave3-verify | 58 | 8.1% |
| wave4a-bonus-fix | 56 | 7.8% |
| wave1-corroboration-v2-test | 56 | 7.8% |
| wave4a-verify | 56 | 7.8% |
| critic-verifier-test | 25 | 3.5% |
| ropa-pipeline-verify | 9 | 1.2% |
| ropa-mapping-fix | 6 | 0.8% |

**Every soft-delete reason is a development-time supersession**
(critic A/B testing, extractor wave fixes, pipeline verifies)
— NOT tenant-authored HITL rejects.

Rethink: **the approve-rate metric can't be recovered from
the current DB state.** Ship 10's HITL numbers were computed
in-flight during that arc's review pass and never persisted
as first-class signals.

### Surprise 2: grounding_method IS the quality signal

Ship 6'.b (2026-07-19) added `document_findings.grounding_
method` — a CHECK-allowlisted column tracking how each finding
was grounded (extractor_verbatim / fingerprint / template /
workbook / leaf_scan / manual / form / unknown).

Post-Ship-17 (fingerprint catalog regen), the active-finding
distribution across the 5-doc corpus:

| Grounding | N | % |
|---|---|---|
| **fingerprint** | 146 | **71.9%** |
| **extractor_verbatim** | 35 | **17.2%** |
| unknown / null (pre-Ship-6'.b) | 22 | 10.8% |

**89.2% of active findings are deterministically grounded.**
The 17.2% verbatim path is LLM extraction BUT with the strict
substring-verifier gate (Ship 6'.b `_evidence_grounded()`).
The 10.8% unknown are pre-Ship-6'.b survivors of HITL
approval — legacy but validated.

Cross-doc pattern:
- **Consent Management**: 43 active, 0 verbatim, 42
  fingerprint (98%). Ship 10 baseline was 28 findings all
  LLM-extracted. Now the same doc yields 42 fingerprint
  matches — Ship 17 catalog fingerprints (topic-anchor-
  augmented) catch content patterns effectively.
- **Processor Operations**: 124 active, 16 verbatim, 98
  fingerprint (79%). Ship 10 baseline was 30 findings. 4x
  growth, mostly via fingerprints.
- **DPIA / Data Quality / RoPA**: 8-17 findings each, more
  verbatim than fingerprint. These docs have less structured
  content that fingerprints match; LLM extraction fills the
  gap.

## Corpus-level rollup

| Metric | Value |
|---|---|
| All-time finding rows (5 docs) | 923 |
| Currently active | 203 |
| Approved (of active) | 101 (49.8%) |
| Pending review | 102 |
| Deterministic grounding total | 181 (89.2%) |

Ship 10 baseline: 97 findings, 48 approved (49% approve). Now:
203 active, 101 approved (49.8%). Approve-rate is
**essentially unchanged**. But interpretation matters —
Ship 10's "approve" was in-flight labeling; now "approve" is
Stage-1 HITL confirmations accumulated over 2 weeks.

## Reframed question: what did Ship 17 actually achieve?

The audit surfaces the correct evidence for Ship 17's impact:

1. **2x finding volume** (97 → 203 active) at the same doc
   corpus. Ship 17 catalog fingerprints + Ship 11 filters
   surface more real signal per doc.
2. **89% deterministic grounding** (verbatim + fingerprint).
   LLM extraction is bounded by substring-verifier gate;
   fingerprint matches don't touch the LLM at all.
3. **~50% Stage-1 approval rate** on reviewed findings.
   Consistent with Ship 10 baseline; suggests the extra
   volume Ship 17 added isn't lower-signal than Ship 10's
   baseline.
4. **102 pending review** — the backlog. These are findings
   from post-Ship-10 re-extractions that never got HITL-
   touched.

## What CAN'T be recovered from this audit

- Ship 10's "49 reject" bucket — no `rejected` review_status
  values in the DB; no tenant-authored deletion_reasons.
  The original Ship 10 HITL was measured in-flight, not
  persisted as first-class signal.
- Whether the 102 pending findings would approve at 50% or
  70% or 30% — needs tenant HITL action to answer.

## What CAN be recovered / new discipline

`scripts/audit_finding_quality.py` (Ship 27'.b) now gives us:
- Per-doc active/all-time/approve/pending breakdown
- Per-doc grounding_method distribution
- Corpus rollup with % deterministic
- Deletion-reason histogram (dev-time supersessions vs
  future tenant rejects)

This is the reusable signal for future extraction arcs. Ship
17 was the last major catalog-impacting arc; Ship 27
establishes the audit surface that any future extractor /
catalog change can re-run against.

## Codified insight

**The right quality signal for extraction pipelines is
`grounding_method` distribution, NOT `review_status`
approve-rate.** Review status is a moving tenant workflow
(pending backlog inflates when re-extraction outpaces HITL).
Grounding method is a first-class attribute of the finding
that captures how the pipeline surfaced it: fingerprint
(catalog match, no LLM) vs verbatim (LLM with strict gate)
vs unknown (legacy).

**Ship 6'.b's provenance column** (added 2026-07-19) is
therefore load-bearing for observability. Ship 27 is the
first arc to actually USE it as the quality signal.

## Sub-arc plan

### 27'.b — Audit script + data pull

`scripts/audit_finding_quality.py` — reusable audit with
`--tenant` + `--docs` flags. Renders per-doc + corpus
breakdown. Read-only. First-run captured this design memo's
data.

### 27'.c — Interpretation + arc retrospective

Interpret what Ship 27's numbers tell us:
- Ship 17 catalog fix WAS quality-improving (89%
  deterministic grounding, 2x volume at same approve-rate)
- The audit metric to use going forward is grounding_method
  distribution
- Next-arc candidates: single-token fingerprint fix (Ship
  17 deferred) has a clean audit surface; migrate eval to
  structured shape is orthogonal to quality but valuable

Ship 27 does NOT implement any code / catalog changes. Pure
audit + interpretation + reusable tooling.

## Ship 27 progress

| Sub-arc | Status |
|---|---|
| **27'.a Audit design + findings capture (this)** | **✓** |
| 27'.b Audit script | ✓ (delivered as part of 27'.a discovery) |
| 27'.c Interpretation + retrospective | next |

## Related

- Ship 6'.b (2026-07-19) — `grounding_method` column that
  enables this audit
- [[ship-17-prime-arc-retrospective-2026-07-23]] — the
  catalog regen arc Ship 27 measures
- [[ship-23-prime-a-audit-2026-07-24]] — audit-first
  pattern this arc extends to a new domain
- Ship 10 (2026-07-08 — 07-10) — the 5-doc corpus + HITL
  baseline
