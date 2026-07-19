---
name: ship-6-prime-b-grounding-provenance-2026-07-18
description: "Ship 6'.b — auditor-facing per-finding grounding_method column + formal grounding tests"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 6'.b (2026-07-18) — first fix out of the Ship 6'.a LLM-role
audit. Motivation: the extractor already runs a strict
`_evidence_grounded()` verbatim-substring check that drops any
LLM-invented quote before it reaches the DB, but once a finding is
persisted, we lost the record of WHICH safeguard it passed
through. Auditors reviewing the Stage-1 queue asked "how do you
know this evidence is real, not paraphrased by the LLM?" and the
answer had to be reconstructed from `inference_source` + code
reading.

## What shipped

1. **schema_v81** — new `document_findings.grounding_method`
   column with CHECK-constrained allowlist:
   - `extractor_verbatim` (LLM path, substring-verified)
   - `workbook` (YAML matcher — value is the row's data)
   - `template` (`<<MUST item:X>>` fast path)
   - `fingerprint` (auto-approve, ≥2 signals)
   - `leaf_scan` (rare HITL-only)
   - `manual` (UI/API direct)
   - `form` (retired 2026-07-04)
   - `unknown` (pre-6'.b backfill; xfw_bridge; anything else)

   Idempotent migration. Backfilled 3839 rows from
   `inference_source` (near-1:1 proxy): 1415 extractor_verbatim,
   1385 fingerprint, 741 workbook, 174 unknown, 68 template, 56
   leaf_scan. Btree index `(tenant_id, grounding_method)` for
   auditor queries.

2. **`rag/intake/posture_writer.py`** — new `_grounding_method()`
   helper mapping `inference_source` → grounding_method. Both
   `INSERT INTO document_findings` sites now populate the column
   explicitly. Fallback INSERT (where `inference_source` uses DB
   default `'extracted'`) hardcodes `'extractor_verbatim'`.

3. **`tests/test_extractor_grounding.py`** — 8 assertions across
   6 test functions:
   - real quote is grounded (verbatim substring)
   - fabricated quote is dropped
   - punctuation drift (dash→semicolon bullets) is tolerated
   - quotes below `_MIN_EVIDENCE_LEN` (40 chars) are dropped
   - markdown source is checked when full_text empty
   - both-sources-empty → lenient (deferred to Stage-1 HITL)

   All 8 PASS locally.

## Ship 6'.a corrected framing

The audit memo characterised extractor hallucination as a
material risk. Investigation surfaced that
`_evidence_grounded()` at `rag/intake/extractor.py:1989` already
runs a punctuation-normalised substring check at BOTH call sites
(line 385 pass1 + line 2151 pass2). Findings whose quote can't
substring-match get silently dropped BEFORE reaching the writer.

So the LLM path isn't hallucinating findings into the DB —
that specific path is deterministically safe. What was missing
was **auditor visibility** into which safeguard fired. That's
what Ship 6'.b delivers.

The stronger characterization now: even the Determinative role
is bounded by a deterministic verifier gate. LLM proposes,
grounding gate disposes.

## Baseline

Eval running to confirm no regression. `grounding_method` column
is additive — no reads depend on it yet.

## Ship 6' progress

| Sub-arc | Status |
|---|---|
| 6'.a Role audit + safeguard inventory | ✓ |
| **6'.b Grounding provenance column + tests** | **✓** |
| 6'.c Preservation-check retrospective | next |
| 6'.d Chat prose claim-check | pending |
| 6'.e Joined LLM decision-trail view | pending |
| 6'.f Arc retrospective | pending |

## Related

- [[ship-6-prime-a-llm-role-audit-2026-07-18]] — parent audit
  memo that surfaced the gap
- [[ship-5-prime-arc-retrospective-2026-07-18]] — previous arc
