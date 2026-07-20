---
name: ship-11-prime-b-bridge-source-quality-gate-2026-07-20
description: "Ship 11'.b — bridge source-quality gate in xfw_proposer to suppress noisy source-finding bridges (Pattern 4 from Ship 10 HITL)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 11'.b (2026-07-20) — first execution sub-arc of the Ship
11 extractor quality plan. Targets Pattern 4 (bridge multiplier),
the single largest source of noise in the Ship 10 HITL review
(17 of 49 rejects, 35%).

## Motivation

From Ship 10 HITL data:

- 17 stage-1 rejects were bridge propagations
- 12 of those came from ONE source pattern:
  `A.7.2.6` (subprocessor label) → A.5.19 + A.5.20 + A.5.22 across 4 documents
- Each weak source multiplied into 3-4 bridge rejects

The critic-verifier confirms the source finding via verbatim
grounding, but bridges fire in a SEPARATE stage that doesn't
gate on source quality. A weak source with low confidence, no
MUST binding, or a fragment excerpt would still spawn N bridge
findings.

## What shipped

Extended `rag/intake/xfw_proposer.py` with two functions:

- **`_bridge_worthy_check(**fields)`** — pure gate; takes the
  raw fields (inference_source, confidence, checklist_item_id,
  excerpt) and returns `(worthy: bool, reason: str)`.

  Blocks three failure modes:
  1. **Bridge-of-bridge cascade** —
     `inference_source == 'xfw_bridge'` is auto-rejected.
     Prevents multi-hop noise amplification.
  2. **Low-confidence sources** — only `medium` or `high` seed
     bridges. `low` and unset are blocked.
  3. **Fragment sources** — either MUST-bound
     (`checklist_item_id` set) OR excerpt ≥ 40 chars of prose.
     Below both, drop.

- **`_source_is_bridge_worthy(finding)`** — convenience wrapper
  for the per-upload path that takes a `DocumentFinding`.

Wired into both bridge emission paths:

- **`propose_for_findings`** — filters `DocumentFinding` sources
  after the per-source deduplication step.
- **`propose_backfill`** — SQL updated to fetch
  `checklist_item_id` + `inference_source`; gate applied inline.

New telemetry: `ProposalSummary.sources_gated` counter — how
many sources the gate rejected. Included in the summary
`__str__` for observability.

## Threshold rationale

- **`_BRIDGE_ALLOWED_CONFIDENCES = {"medium", "high"}`** —
  Ship 10 rejects were mostly `medium` confidence, so this
  gate alone doesn't drop them; we still need the substance
  gate below. But `low` is universally noise.
- **`_BRIDGE_MIN_EXCERPT_CHARS = 40`** — matches the
  extractor's `_MIN_EVIDENCE_LEN` (Ship 6'.b grounding gate).
  Field-labels like "Subprocessors" (13 chars) fail; short
  full sentences pass. Longer field-labels like "Subprocessors
  / Any third parties involved" (44 chars) still pass this
  gate — those need the content-shape filter from Ship 11'.c.

## Coverage — what this gate catches

From the 17 Pattern-4 rejects in Ship 10:

| Reject cluster | Cases | Ship 11'.b catches? |
|---|---|---|
| A.7.2.6 → A.5.19/20/22 (subprocessor label, 4 docs) | 12 | ⚠️ Partial — source excerpt is 44c "Subprocessors / Any third parties involved". Fragment gate misses (>40c). Waits for Ship 11'.c content-shape filter. |
| A.7.2.8 → A.5.9 (Consent Register as RoPA) | 2 | ⚠️ Partial — source excerpt is longer. Waits for anchor-semantic filter (Ship 11'.d). |
| A.7.4.7 → A.5.33 (retention field label) | 2 | ⚠️ Same as above. |
| A.7.4.8 → A.7.14 (Odoo tenant, physical disposal) | 1 | ⛔ Not caught — needs tenant-applicability filter (Ship 11'.c). |

**Honest read: on Ship 10's specific data, this gate alone
catches ~0-3 of the 17 bridge rejects.** The gate is
structurally correct (blocks the three universal failure modes)
but the specific Ship 10 sources happened to be just over the
excerpt threshold OR MUST-bound. Ship 11'.c/d will catch the
rest.

**But the gate is future-proof:** any future weaker sources
(low confidence, sub-40-char fragments, cascading bridges) get
suppressed immediately.

## Tests

`tests/test_bridge_source_quality_gate.py` — 13 assertions:

- 2 positive cases (MUST-bound short excerpt; substantive
  long excerpt)
- 4 negative cases (bridge-of-bridge, low conf, missing conf,
  fragment)
- 2 boundary tests (excerpt length threshold at 39/40 chars)
- 4 Ship 10 replay cases (documents actual gate behavior on
  the specific rejects — honest about what the gate does and
  doesn't catch)

All PASS.

## Baseline

Full eval running. The gate is additive-suppression: it can
only reject bridges that would otherwise be emitted. Existing
approved bridges from prior extractions are unaffected (they
already live in `document_findings`; the gate runs only during
new extraction / backfill).

Eval baseline expectation: 225/226 PASS unchanged. If the gate
had a bug that incorrectly gated a legitimate source, we'd see
posture-check case regressions.

## Ship 11' progress

| Sub-arc | Status |
|---|---|
| 11'.a Extractor quality plan (design memo) | ✓ |
| **11'.b Bridge source-quality gate** | **✓** |
| 11'.c Pre-critic filters bundle (content-shape + fingerprint substance + tenant applicability) | next |
| 11'.d Critic prompt enhancement (business_description + MUST-prefix taxonomy) | pending |
| 11'.e Re-extraction measurement checkpoint | pending |
| 11'.f Arc retrospective | pending |

## Related

- [[ship-11-prime-a-extractor-quality-plan-2026-07-20]] — parent
  design memo (5-pattern taxonomy)
- Ship 10 HITL review (2026-07-20) — the 49-reject dataset this
  gate was designed against
- Ship 6'.b `_evidence_grounded` — the grounding gate whose
  40-char threshold this gate mirrors
