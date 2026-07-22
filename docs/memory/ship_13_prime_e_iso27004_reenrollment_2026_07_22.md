---
name: ship-13-prime-e-iso27004-reenrollment-2026-07-22
description: "Ship 13'.e — ISO 27004:2016 re-enrollment + curation + Chroma after user supplied second-edition PDF; reverses Ship 13'.a skip decision"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 13'.e (2026-07-22) — unplanned fifth sub-arc of Ship 13.
User landed the actual ISO 27004:**2016** second-edition PDF at
`/data/arioncomply/private/iso27004_2016.pdf` mid-day, closing
the constraint that forced Ship 13'.a's skip decision.

## What ships

Symmetric reversal of Ship 13'.a's 27004 unenrollment, plus the
delivered curation work Ship 13'.a would have shipped had the
right text been available:

1. **`schema_v86`** — re-INSERTs `ISO27004:2016` into `standards`
   (inverse of `schema_v85`). No shape change, purely a registry
   population.
2. **`rag/output/vocab/iso27004_2016.json`** restored — vocab file
   comes back, noting the edition-mismatch backstory in its
   `notes[]` array for future auditors.
3. **`scripts/enrich_iso27004_leaves.py`** — combined
   footer-restore + enrichment for the 7 target leaves (9.1 +
   A.5.22, A.5.36, A.5.37, A.7.4, A.8.15, A.8.16):
   - 9.1's Ship 12'.c footer swaps from
     `[Related guidance: ISO 27003:2017]` back to
     `[Related guidance: ISO 27003:2017 · ISO 27004:2016]`
   - 6 monitoring Annex A leaves get their standalone
     `[Related guidance: ISO 27004:2016]` footer re-appended
   - Then each leaf receives a fresh authored paragraph from
     27004:2016 §5-§8 (paraphrased, verified against source)
4. **Chroma extension** — `scripts/index_iso_guidance_to_chroma.py`
   extended to build a third collection `iso27004_2016` (23
   sections extracted from chapters 4-8 body content).
5. **Digest hint extractor** widened to recognize
   `Per ISO 27004:2016` as a third valid marker (was: 27003 +
   27005 only). Also fixed a sentence-boundary bug — the extractor
   previously missed `.\n` boundaries (only matched `. `), which
   caused 2-paragraph hint lines to concatenate. Fix: match
   `re.search(r"\.\s", tail)` for any post-period whitespace.
6. **Classifier addition** — 3 new DOCUMENT_TOPIC_MAP entries
   ("monitoring and measurement", "monitoring, measurement",
   "isms performance") all route to 9.1 so chat queries about
   27004's core domain reach the enriched leaf.
7. **Eval case #224** — locks 27004 surfacing via the digest hint.

## Per-leaf enrichment table

| Leaf | 27004 § | Bytes added | Focus |
|---|---|---|---|
| 9.1 | §6-§8 | 868 (largest — 6-step lifecycle + role model) | Full measurement lifecycle + perf/effectiveness split |
| A.5.22 | §6.2 + §7.2 | 577 | Third-party monitoring measures |
| A.5.36 | §7.2 + §7.3 | 561 | Compliance monitoring perf + effectiveness split |
| A.5.37 | §7.3 | 504 | Op'g procedure effectiveness (not just existence) |
| A.7.4 | §6.2 + §7.2 | 562 | Physical monitoring measures + data lifecycle |
| A.8.15 | §8.6 | 554 | Log analysis effectiveness (MTTD, FP rate) |
| A.8.16 | §8.5 | 580 | Monitoring activities → documented procedure |

Total added: ~4.2 KB across 7 leaves.

## What did NOT ship

- **No SHOULD promotions.** Ship 13'.b's deferred candidates
  (§6.4.2 acceptance-criteria signoff, §8.6.1 treatment-plan
  elements, §7.2.2 risk-owner authority) stay deferred to the
  arc retrospective. Adding 27004-specific SHOULDs would
  further widen scope; better to review all three families'
  candidates together at 13'.f.
- **No text-file cleanup.** The 2009 first-edition PDF and its
  .txt extract remain in `/data/arioncomply/private/` as an
  audit trail. Both are gitignored so there's no repository
  pollution.

## Why this reversal was worth doing

The Ship 13'.a skip was a defensible call at the time — citing
2009 § pointers with a 2016 badge would confuse auditors. Once
the correct edition landed, re-enrollment was a mechanical
symmetric operation (schema_v85 out, schema_v86 in). Zero
architectural changes; the curation work itself scales linearly
with the number of target leaves.

**Lesson**: the enrollment-stub pattern from Ship 12'.b holds
value even when curation gets deferred. When the missing input
arrives, the registry doesn't need re-architecting.

Corresponding pair-rule: **don't discard scrub scripts even after
their work looks "done".** Ship 13'.a's
`scripts/scrub_iso27004_citations.py` is complementary to today's
enrich script — both remain in the repo as documentation of the
scrub → restore cycle for future reference.

## Impact on baseline

Eval confirmed: **228/229 PASS + 1 WARN + 0 FAIL** (up from
227/228; the new #224 27004-surfacing case passes cleanly).
The single WARN remains the pre-existing #200 gap_analysis vs
posture_check mismatch. Zero regressions from the re-enrollment,
enrichment, or the sentence-boundary fix in the digest hint
extractor.

## Ship 13 progress (revised)

| Sub-arc | Status |
|---|---|
| 13'.a Design + 27004 unenrollment | ✓ |
| 13'.b 27005 batch (14 leaves) | ✓ |
| 13'.c 27003 batch (26 ISMS clauses) | ✓ |
| 13'.d Chroma + digest promotion + 2 eval cases | ✓ |
| **13'.e 27004:2016 re-enrollment + curation + Chroma** | **✓ (this doc)** |
| 13'.f Arc retrospective (was 13'.e) | next |

Ship 13' arc: 5 delivery sub-arcs + retrospective. Largest arc
count since ISO 27701 close.

## Related

- [[ship-13-prime-a-iso27000-curation-design-2026-07-21]] — the
  original design memo whose 27004 skip this arc reverses
- [[ship-13-prime-d-chroma-digest-eval-2026-07-22]] — the digest
  hint mechanism this arc extends
- [[ship-12-prime-b-standards-enrollment]] — the enrollment-stub
  pattern this arc validates by exercising re-enrollment
- Ship 13'.f: arc retrospective — codifies scrub-then-restore
  cycle + SHOULD-promotion review deferred here
