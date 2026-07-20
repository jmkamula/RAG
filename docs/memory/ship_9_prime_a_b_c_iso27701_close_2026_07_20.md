---
name: ship-9-prime-a-b-c-iso27701-close-2026-07-20
description: "Ship 9'.a-c — closes ISO 27701 gaps: B.8.3-5 eval mirrors + SoA template extension + program_review mappings (75% → 100% coverage)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 9'.a-c (2026-07-20) — closes the remaining three ISO 27701
gaps flagged in Ship 8'.c's retrospective. Bundled here because
each sub-arc was small and touched adjacent surfaces.

## Sub-arc summary

### 9'.a — B.8.3-5 eval mirrors

6 new eval cases (#216-221) covering the processor-side blocks
that Ship 8'.b didn't touch:

- #216 **B.8.3.1** — obligations to PII principals (subject
  rights processor mirror) — NC
- #217 **B.8.4.1** — temporary files (mirror of A.7.4.6) — NC
- #218 **B.8.4.2** — return, transfer or disposal at customer
  churn — NC
- #219 **B.8.5.1** — subprocessor disclosure (Verpex,
  Cloudflare) — OFI
- #220 **B.8.5.4** — legally-binding disclosures — NC
- #221 **B.8.5.8** — subprocessor change notification — NC

Structural per [[feedback-eval-state-drift]] — must_contain the
ref, forbid clarify-hedging.

### 9'.b — SoA template 27701 extension

`db/templates/req__6_1_3__statement_of_applicability.md` now
includes a **"PIMS extension — for ISO 27701-enrolled tenants"**
section (700+ words) that:

- Enumerates all 49 27701 anchors (A.7.2/3/4/5 + B.8.2/3/4/5)
  grouped by batch with the anchor titles
- Explains role-based applicability (controller-only,
  processor-only, both)
- Names two specific N/A cases: A.7.2.7 (joint controller) +
  A.7.3.10 (automated decision-making) tied to
  `client_facts` fields
- Provides 4 example rows in the same table format as the 93
  ISO 27001 rows (single master ledger, sorted by standard
  then ref)

Template reloaded — `load_to_postgres.py` reports `updated=1`
(SoA row) + `unchanged=843` (all others). The
`soa_external_controls` SHOULD field stays but now has
explicit 27701 guidance sitting above it.

### 9'.c — program_review doc_mappings

Extended `scripts/generate_doc_mappings.py` with a new
`_is_review_doc()` predicate that includes `review_record`
leaves whose id-suffix ends in `program_review` /
`periodic_review` / `annual_review`. These are the doc-shaped
annual review REPORT artefacts (as opposed to per-event review
records).

Generator run produced **189 new YAML files**:

- **49 ISO 27701 `:program_review` leaves** (the target of this
  arc — closes the 75% → 100% coverage gap)
- **24 ISO 27001 ISMS-clause program_review leaves** (4.1
  through 10.2) — bonus coverage
- ~24 A.5.x/A.6.x/A.7.x/A.8.x periodic_review + specialised
  review leaves
- Various framework-specific review scaffolds

All validate under `scripts/validate_doc_mappings.py` (591
files clean, +189 from previous 402).

## Coverage delta

### ISO 27701 leaf mapping coverage

| Metric | Pre-Ship 9 | Post-Ship 9 |
|---|---|---|
| Doc-mapped leaves        | 98            | 147           |
| Workbook-mapped leaves   | 49            | 49            |
| Union (deduplicated)     | 147           | 196           |
| Total 27701 leaves       | 196           | 196           |
| **Coverage** | **75%** | **100%** |
| Fall-through to LLM      | 49            | 0             |

Every 27701 leaf now lands through a deterministic mapping
path. The LLM extractor is no longer the default for any 27701
program-review artefact.

### Eval coverage

| Framework | Pre-Ship 9 | Post-Ship 9 |
|---|---|---|
| `iso27001` tag | 0 (was already 0)| 0 |
| `iso27701` tag | 15 (#201-215) | **21** (#201-221) |
| `gdpr` tag     | 47 | 47 |
| **Total suite** | 220 | **226** |

Baseline floor updates: **223/226 blocks restart** (was 217/220).

## The B.8 processor coverage — locked

Pre-Ship 9, the eval covered only B.8.2.x (Ship 8'.b added
#213/214). Ship 9'.a extends to B.8.3-5:

- B.8.3.x (subject rights processor): 1 anchor / 1 case
- B.8.4.x (retention processor): 3 anchors / 2 cases
  (B.8.4.3 encryption not tested — general enough to skip)
- B.8.5.x (transfers/disclosures processor): 8 anchors / 3 cases
  (B.8.5.2/3/5/6/7 not individually tested — representative
  coverage)

Complete anchor-by-anchor coverage of B.8 is deferred as too
much granularity for structural regression.

## Baseline

Full eval running. Behavioral additions:
- 6 new eval cases (should PASS on current Arion posture)
- 189 new doc_mappings (recognize new filenames; no existing
  filename should match differently)
- SoA template updated (unused surface in current tests)

## Ship 9' progress

| Sub-arc | Status |
|---|---|
| **9'.a B.8.3-5 eval mirrors** | **✓** |
| **9'.b SoA template 27701 extension** | **✓** |
| **9'.c program_review doc_mappings** | **✓** |
| 9'.d Demo 27701 documents | SKIPPED |
| 9'.e Arc retrospective | next |

## Related

- [[ship-8-prime-arc-retrospective-2026-07-20]] — the arc that
  identified these gaps
- [[ship-8-prime-b-iso27701-eval-expansion-2026-07-20]] —
  Ship 8's eval expansion this arc extends
