---
name: ship-36-prime-a-flip-flag-design-2026-07-25
description: "Ship 36'.a — design memo for the first real cutover test. Flip USE_CONSENSUS_EXTRACTION=1 on the Arion demo tenant, re-extract the 5-doc corpus via the actual API endpoint (not just measurement script), capture intake_consensus_log rows, spot-check wiring, decide on keep-on-or-flip-back. First production-shape data for post-cutover tuning."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 36'.a — opens Ship 36 arc (first real cutover test).
Ship 35 shipped the cutover behind a default-OFF env flag; no
tenant has seen the new path in production shape. Ship 36 flips
the flag on the demo tenant to (a) prove wiring works end-to-end,
(b) capture the first `intake_consensus_log` rows, (c) surface
any issues Ship 33-35 measurement missed.

## What "flip the flag" means concretely

`USE_CONSENSUS_EXTRACTION=1` set in the API process environment.
Restart API. Every subsequent `extract()` call takes the consensus
branch instead of fingerprint + critic-verifier + concat.

Distinction from Ship 33'.b/c measurement:
- **Ship 33 measurement**: standalone script calling `extract()`
  directly. No writer, no `write_findings`, no
  `posture_writer._apply_auto_approve`, no engine reload.
- **Ship 36 flip**: real API endpoint
  `/api/v1/admin/uploads/{upload_id}/reextract` → `doc_pipeline`
  → `extract()` → `write_findings()` → engine reload → engine
  proposals. Full end-to-end.

The wiring that was NEVER exercised in shadow mode:
- Does the writer's `inference_source='fingerprint_match'` auto-
  approve gate work with consensus-emitted findings? (Ship 35'.b
  uses `fingerprint_match` for compat, but auto-approve requires
  N-of-M corroboration; consensus findings may not meet it)
- Does `intake_consensus_log` receive rows via
  `_extract_via_consensus`'s telemetry write?
- Does engine reload + Stage-1 queue behave sanely with the new
  finding distribution?
- Any exceptions in the new code path under real doc-pipeline
  invocation?

## Corpus + procedure

**Target tenant**: Arion demo (`00000000-0000-0000-0000-000000000001`)

**Docs to re-extract**: 5 Ship-10-baseline docs
1. Data Quality Accuracy Procedure.docx
2. Data Protection Impact Assessment (DPIA) Procedure.docx
3. Records of Processing Activities.docx
4. Consent Management Procedure.docx
5. Processor Operations Procedures.docx

Same corpus Ship 32/33/34 measured against — direct comparison
possible.

**Procedure**:
1. Wait for Ship 34'.c v2 eval to finish (avoid OpenAI concurrency)
2. Set `USE_CONSENSUS_EXTRACTION=1` in API env
3. Restart API
4. Clear existing findings on the 5 docs (Ship 30 hygiene: any
   residue from prior runs); use demo_tenant_cleanup pattern OR
   direct DELETE
5. Re-extract each doc via
   `/api/v1/admin/uploads/{upload_id}/reextract`
6. Verify findings landed in `document_findings`
7. Verify `intake_consensus_log` has 5 rows (one per doc)
8. Query row shape (verdict counts, LLM movement, signals summary)
9. Compare vs Ship 33'.c/34'.b shadow measurements (should match
   within noise since same code)
10. Chat spot-check on a few controls to verify no runtime break

## Success signals

- ✅ 5 `intake_consensus_log` rows land (telemetry wiring works)
- ✅ Per-doc verdict counts within ±10% of shadow-mode
  measurements (Path B: DQA 23, DPIA 32, RoPA 29, Consent 78,
  Processor Ops 35 accepted)
- ✅ Findings written to `document_findings` with
  `inference_source='fingerprint_match'` + non-zero counts
- ✅ Chat queries against affected controls return non-empty
  answers, no exceptions
- ✅ No new errors in API log

## Failure signals + rollback triggers

- ❌ `intake_consensus_log` empty after re-extract → telemetry
  write broken (likely tenant_id lookup or connection issue in
  `_extract_via_consensus`)
- ❌ Zero findings written → writer path rejects consensus-emitted
  findings; likely `inference_source='fingerprint_match'` auto-
  approve gate failing without N-of-M corroboration signals
- ❌ Findings count wildly different from shadow measurement
  (>20% deviation) → something in the doc_pipeline wrapper
  affects consensus behavior
- ❌ API exceptions during re-extract → bug in the wiring
- ❌ Chat regression on the 5 docs' controls

**Rollback**: unset `USE_CONSENSUS_EXTRACTION` + restart API.
Sweep residue via `scripts/dev/demo_tenant_cleanup.py`.

## What Ship 36 does NOT do

- **Ship 36 does not flip the flag on non-demo tenants** —
  ArionComply doesn't have real customers yet, but if it did,
  they'd stay on the default-OFF path.
- **Ship 36 does not retire old code** — retirement still needs
  4-6 weeks of clean flag=1 running per Ship 35 plan.
- **Ship 36 does not add signals** — LLM discovery pass as 9th
  signal is a bigger arc.
- **Ship 36 does not retune thresholds** — first production data
  needed; tuning follows from `intake_consensus_log` observation.

## Sub-arc plan

| Sub-arc | Focus | Outcome |
|---|---|---|
| **36'.a** (this) | Design memo — procedure + success/failure signals | Locked plan |
| 36'.b | Flip + re-extract + verify + spot-check | intake_consensus_log rows landed; wiring validated OR failure surfaced |
| 36'.c | Eval + retro | Baseline held; keep-on / flip-back decision codified |

## Related

- [[ship-35-prime-arc-retrospective-2026-07-25]] — the arc whose
  cutover this validates end-to-end
- [[ship-34-prime-arc-retrospective-2026-07-25]] — HITL that
  unblocked cutover
- [[ship-33-prime-arc-retrospective-2026-07-25]] — the consensus
  module this arc puts in production
- `docs/memory/ship_30_prime_arc_retrospective_2026_07_25.md` —
  `scripts/dev/demo_tenant_cleanup.py` used for rollback
- `db/schema_v89_ship34b_intake_consensus_log.sql` — the table
  Ship 36 populates for the first time
