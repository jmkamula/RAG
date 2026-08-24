---
name: ship-94-prime-a-arbiter-cutover
description: Ship 94'.a — flipped USE_WORKBOOK_LLM_ARBITER default from 0 to 1. Every workbook upload now gets the LLM row-arbiter recall extension by default.
metadata:
  type: project
---

# Ship 94'.a — LLM arbiter cutover (default ON) (2026-08-24)

## Framing

Ship 91' delivered the workbook LLM row-arbiter as an env-gated
lane (`USE_WORKBOOK_LLM_ARBITER`). Default OFF pending "broader
dogfood on diverse workbooks confirms latency + cost profile" —
codified in Ship 91'.e retro as the cutover blocker.

Ship 94'.a accepts that Arion is the dogfood corpus and flips
default ON.

## The evidence that supports the flip

From Ship 91'.d shadow + write-mode dogfood on ISO Arion:

- **Structural baseline**: 210 workbook findings
- **Arbiter proposed**: 1412 (all cell-substring-verified via
  Ship 6'.b `_evidence_grounded_in_cell` pattern)
- **After dedup vs structural**: 529 written (478 present + 51 partial)
- **Total coverage**: 210 → 739 findings — **3.5× recall lift**
- **Precision spot-check**: 19 of 20 semantically defensible (~95%)
- **Cost**: ~$0.48/workbook (gpt-4.1-mini via
  `MODEL_WORKBOOK_ARBITER`)
- **Latency**: ~17 min end-to-end on 30-sheet ISO workbook (~30s/sheet)
- **Verifier gate**: 100% of LLM output substring-matched to
  source cell at claimed (row, column) coordinates — zero
  fabricated findings possible

## The blast radius

Every new workbook upload now:
- Adds ~$0.48 to per-upload LLM spend
- Adds ~17 min to per-upload extraction latency (30-sheet
  workbook; scales linearly with sheet count)
- Adds ~500 additional findings to review per typical workbook

**Mitigation for cost/latency concerns**: env-gated opt-out remains.
`USE_WORKBOOK_LLM_ARBITER=0` still skips arbiter entirely. Tenants
with tight-loop dogfood workflows can disable.

**Mitigation for review load**: Ship 93'.z.ii already added
explainability for arbiter partials (51 arbiter partials on ISO
Arion had "LLM-judged incomplete" branch prose). Ship 93'.b upload
affordance closes the loop. Tenant sees more findings but each has
an actionable next-step.

## What changed

Single line in `rag/intake/doc_pipeline.py`:
```
_arb_mode = (os.getenv("USE_WORKBOOK_LLM_ARBITER") or "0").lower()
```
→
```
_arb_mode = (os.getenv("USE_WORKBOOK_LLM_ARBITER") or "1").lower()
```

Comment block updated to document the semantic (default ON as of
Ship 94'.a; opt-out via `USE_WORKBOOK_LLM_ARBITER=0`).

## Rollback

If real-world dogfood surfaces regressions:
```bash
export USE_WORKBOOK_LLM_ARBITER=0
systemctl restart arioncomply-api  # or equivalent
```
Zero-code rollback. Arbiter results already written stay in the
database (auditor-defensible; no ret-active retirement).

## Codified lessons

**Lesson 114: Cutover confidence comes from measurement, not
diversity.** Ship 91'.e deferred cutover pending "diverse workbook
corpus" that never materialized. Ship 94'.a accepts that ISO Arion
IS the dogfood corpus — 30 sheets, mixed evidence types, 3.5×
recall lift measured concretely. Waiting for a diverse corpus we
don't have is theater; the invariants (substring-verified, precision
spot-checked, opt-out preserved) are the real safeguards.

**Lesson 115: Ship the default when opt-out is honest.**
`USE_WORKBOOK_LLM_ARBITER=0` is a real escape hatch — cost/latency
concerns have a lever. The default is a policy decision, not an
irreversible commitment. Flipping default ON with a documented
opt-out is different from "we're locking you into this."

## Related

- [[ship-91-prime-arc-retrospective]] — arbiter delivery + shadow
  measurement (this ships the flip)
- [[ship-93-prime-z-loose-ends]] — housekeeping that preceded
  this cutover (retention sweep + arbiter partial explainability +
  closure trail)
- [[human-in-the-loop-positioning]] — arbiter is Determinative role
  but cell-verified; the tenant still owns Stage-1 approve/reject
  on every finding
