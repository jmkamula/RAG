---
name: ship-32-prime-a-reextraction-measurement-design-2026-07-25
description: "Ship 32'.a — design memo for 5-doc re-extraction measurement checkpoint. Deferred through Ships 27→31 while 4 catalog + loader fixes landed. Aim: validate the extraction pipeline end-to-end with grounding_method distribution vs the Ship 27 baseline of 89.2% deterministic. First measurement arc after a 4-arc patching stretch."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 32'.a — opens Ship 32 arc (5-doc re-extraction measurement).
First forward-motion arc after 4 consecutive maintenance arcs
(28→31). User signal: "we are patching quite a bit right now which
is not good. do we have a real problem, i want us not move away
from our case file model role architecture."

The right forward move given the audit-train work: **validate the
architecture works end-to-end by measuring the impact of the fixes
we've been shipping**. Ship 27 established grounding_method as the
quality signal (89.2% deterministic baseline). Ships 28+29+30+31
all touched pipeline-adjacent surfaces. Time to check whether the
numbers moved the right way.

## What changed since Ship 27's baseline

| Arc | Change | Extraction impact expected |
|---|---|---|
| Ship 28 | Redundant singleton suppression in fingerprint catalog (976 auto-gen singletons → 0) | Fewer false-positive fingerprint matches |
| Ship 29 | Topic-anchor injection extended to all 397 auto-gen files (was Ship 17's 6 family × standard combos) | Cross-leaf collisions dropped substantially; Ship 17'.b motivating pattern `[review, date, planned, interval]` from 48 leaves → 0 |
| Ship 30 | `posture_loader.load_posture` SELECT gained `confirmation_status` | None on extraction; affects chat DRAFT surfacing only |
| Ship 31 | `_fetch_not_assessed_obligation_rows` gained `confirmation_status`; `load_client_facts` gained 8 semantic fields (incl. `uk_data_subjects=True` on Arion) | `applies_when` DSL now sees correct fact values — UK-scoped obligations activate correctly. Not directly extraction — but engine-time posture derivation gets more accurate |

**Expected on extraction output** (5 procedural docs):
- Total finding count: flat-to-slightly-lower vs Ship 17 baseline (192)
- Deterministic grounding_method %: **≥ 89.2%** (Ship 27 baseline), ideally higher
- Cross-leaf collisions on `[per, row]`, `[each, row]` families: unchanged (these are intentionally cross-register templates, Ship 16'.b runtime gate catches them)
- Fingerprint findings absent from Ship 17 that should now be caught by anchor-distinctive keywords: some (~5-10)

## Baseline reference points

| Baseline | Findings | Notes |
|---|---|---|
| Ship 10 (2026-06 HITL review) | 97 | Human ground truth: 48 approve / 49 reject |
| Ship 11'.e (2026-07-21) | ~102 | Post-Ship 11'.b/c/d filters (content-shape + semantic-fit + bridge substantiveness) |
| Ship 17 (2026-07-23) | 192-198 | Post-anchor injection on 27701/GDPR/ISO27001 program_review + applicable_scope (6 combos) |
| Ship 27 (2026-07-24) | Same 192 | 89.2% deterministic grounding_method distribution |
| **Ship 32 (this)** | **TBD** | Post Ship 28+29 catalog tightening + Ship 30+31 loader fixes |

## What to capture

Ship 32'.b runs `scripts/measure_ship11_reextraction.py` (now
hygiene-retrofit with demo_tenant_cleanup so no queue residue).
It already reports:
- Per-doc finding count + by_source breakdown
- Drop counters (dropped_content_shape / critic_verifier drops /
  dropped_low_specificity)
- Comparison to Ship 10 baseline

**Ship 32 adds** a post-run query on the demo tenant BEFORE the
cleanup sweep fires — captures the write-through grounding_method
distribution the script itself doesn't render:

```sql
SELECT grounding_method, inference_source, COUNT(*) AS n
  FROM document_findings
 WHERE tenant_id  = '00000000-...-01'
   AND extracted_at >= $run_start
 GROUP BY grounding_method, inference_source
 ORDER BY n DESC;
```

Ship 27's audit tool `scripts/audit_finding_quality.py` is another
option for a broader-window comparison.

## Success + failure signals

**Success**:
- Deterministic % (fingerprint + extractor_verbatim + workbook +
  template + leaf_scan) ≥ 89.2%
- Total finding count within ±20% of Ship 17 baseline (192)
- Cross-leaf fanout audit shows program_review family collapse

**Neutral (interesting but not failing)**:
- Finding count higher — could be genuine gains from anchor-
  distinctive keywords catching more real evidence
- Finding count lower — could be Ship 28 singleton suppression
  correctly rejecting noise

**Failure (regression)**:
- Deterministic % drops below 89.2%
- New `grounding_method='unknown'` cluster
- Bridge fanout re-appears at Ship 17-pre levels
- LLM cost per doc spikes 2x+

## What Ship 32 does NOT do

- **Change the extraction pipeline** — this is pure measurement.
  If we find regressions, they get their own arc, not shoehorned
  into this one.
- **Update Ship 10 baseline** — the 97-finding number is a
  historical fixed point. We compare against it; we don't
  overwrite it.
- **Re-run HITL review** — no human-in-the-loop grading. If a
  new false positive/negative shows up, it's a finding for a
  future curator arc.
- **Extend measurement to more docs** — 5-doc corpus is the
  reference. Broader corpus is a bigger arc.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **32'.a** (this) | Design + expected shape | Signals + baselines locked |
| 32'.b | Run + capture + interpret | Concrete numbers; comparison to Ship 27 baseline |
| 32'.c | Eval + retro | Baseline holds; measurement finding codified |

## Related

- [[ship-27-prime-arc-retrospective-2026-07-24]] — established
  grounding_method as the quality signal + the 89.2% deterministic
  baseline
- [[ship-11-prime-arc-retrospective-2026-07-21]] — the arc that
  first ran this measurement (198 findings post-filters)
- [[ship-17-prime-arc-retrospective-2026-07-23]] — anchor injection
  arc; expected primary contributor to Ship 32's expected numbers
- [[ship-28-prime-arc-retrospective-2026-07-24]] — singleton
  suppression; catalog tightening contributor
- [[ship-29-prime-arc-retrospective-2026-07-24]] — consolidated
  anchor injection to all auto-gen files
