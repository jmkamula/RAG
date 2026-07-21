---
name: ship-13-prime-a-iso27000-curation-design-2026-07-21
description: "Ship 13'.a — design memo for ISO 27000-family MUST-level curation; source texts landed; per-leaf enrichment plan + sub-arc sequence"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 13'.a (2026-07-21) — opens Ship 13 arc. User provided
three source PDFs post-Ship-12 arc close:

- `/data/arioncomply/private/ISO27003_2017.pdf` (1.4 MB)
- `/data/arioncomply/private/iso27004.pdf` (1.0 MB) — **SKIPPED, edition mismatch (see below)**
- `/data/arioncomply/private/ISO27005_2022.pdf` (4.0 MB)

`pdftotext -layout` extracted cleanly → 9,277 total lines across
the three `.txt` counterparts. Ship 13 curates from 27003 + 27005
only; 27004 is unenrolled in-arc.

## Text integrity discoveries

### ISO 27003:2017 — matches enrollment; clean mapping to ISO 27001

Second edition 2017-03. Structure mirrors ISO 27001:2022 clauses
1:1: §4 Context → §5 Leadership → §6 Planning (6.1.1/6.1.2/6.1.3,
6.2) → §7 Support (7.1-7.5) → §8 Operation → §9 Performance
evaluation → §10 Improvement.

**Per-leaf mapping is trivial** — clause X.Y in 27001 aligns to
§X.Y in 27003. All 26 target ISMS clause leaves have direct
guidance content.

### ISO 27004:2009 — UNENROLLED in Ship 13'.a

**Ship 12'.b enrolled `ISO27004:2016`** (second edition, current).
**The source PDF is `27004:2009` first edition** (published
2009-12-15). The two editions restructured substantially — the
2016 second edition reorganised around "performance evaluation"
to align with ISO 27001:2013 clause 9.1 language.

**Decision: skip 27004 curation entirely.** Discussed with user
2026-07-21. Auditor-mismatch risk (citing 2009 § pointers under
a 2016 badge would confuse modern 27001:2022 auditors) outweighs
the value of curating from an obsolete edition. Bounded blast
radius: only 7 leaves, and 27004 is by far the least
customer-referenced of the three guidance standards.

Ship 13'.a therefore:
- Deleted `rag/output/vocab/iso27004_2016.json`
- `schema_v85` unenrolls `ISO27004:2016` from `standards`
- `scripts/scrub_iso27004_citations.py` removes `· ISO 27004:2016`
  from the 9.1 leaf's footer and drops the standalone
  `[Related guidance: ISO 27004:2016]` footer from the 6
  monitoring Annex A leaves (A.5.22, A.5.36, A.5.37, A.7.4,
  A.8.15, A.8.16).

**If the 2016 second edition text lands later**, re-enroll +
curate then. The 6 monitoring leaves will get their citations
back at that point.

### ISO 27005:2022 — matches enrollment; rich structural depth

Fourth edition 2022-10. Structure: §5 risk management overview
(process + cycles) → §6 context establishment (with §6.4 risk
criteria: acceptance / consequence / likelihood / level) → §7
risk assessment (identify / analyse / evaluate) → §8 risk
treatment (options / controls / SoA / plan) → §9 operation → §10
leveraging ISMS processes.

**Per-leaf mapping**: 6.1.2 (risk assessment) ↔ §7; 6.1.3 (risk
treatment) ↔ §8; 6.1 (framework) ↔ §5+§6; 8.2/8.3 (operational
execution) ↔ §9; A.5.7 (threat intel) ↔ §7.2 threat identification;
A.5.24/29/30 (incident + BCP) ↔ §8.6 treatment plan.

## Curation approach — architecture decision

**Guidance content is not prescriptive.** ISO 27003/27004/27005
explicitly are NOT normative — they're implementation guidance.
This is critical for how we integrate them.

**Rejected: adding MUSTs from guidance.** Elevating "guidance
recommends X" to a MUST_contain item on an EvidenceRequirement
would create false auditor obligations. Not doing this.

**Adopted: enrich `business_description` prose + selective SHOULDs.**

Two categories of enrichment per target leaf:

**Category A — Prose enrichment (all 38 leaves):**
- Append 1-3 authority-cited paragraphs to
  `business_description` after the current "[Related guidance:
  …]" footer from Ship 12'.c
- Paragraphs paraphrase the guidance's implementation direction
  in the leaf's specific area
- Format: `\n\nPer ISO 27005:2022 §7.2: …` then rest of the
  paragraph
- Non-load-bearing: doesn't change engine verdicts; feeds
  Signal C retrieval, chat digest (once digest priority flips),
  Evidence Package "What this is about", external API drill-in.

**Category B — SHOULD promotions (selective, per-leaf judgment):**
- ONLY when the guidance's language is unambiguously prescriptive
  in an implementation-critical area
- Added to existing EvidenceRequirement's `should_contain` list
  (not `must_contain`)
- Example candidates: 6.1.2 → `risk_acceptance_criteria` SHOULD
  (per 27005 §6.4.2); 9.1 → `information_need_declaration`
  SHOULD (per 27004 §7.3); 6.1.3 → `residual_risk_register`
  SHOULD (per 27005 §8.6.3).
- Conservative default: prose-only. SHOULDs added only when
  the case is airtight.

**Rejected: schema change for new `guidance` field.** Overkill
for this arc. The existing `business_description` + tier1
enrichment pattern is sufficient.

## § pointer format decision

Ship 12'.c dropped § specificity because we didn't have texts.
Now we do. New format for Ship 13 citations:

`\n\nPer ISO 27005:2022 §7.2: risk identification asks…`

The full citation → § → content chain is auditor-verifiable +
Chroma-retrievable + LLM-digest-friendly.

## Sub-arc plan (revised for 27004 skip)

| Sub-arc | Scope | Est. duration |
|---|---|---|
| **13'.a** | This design memo + 27004 unenrollment (schema_v85) + citation scrub on 7 leaves | ~½ day (this session) |
| **13'.b** | ISO 27005 batch — 14 risk-adjacent leaves (biggest customer-facing value; single family) | 1-1.5 days |
| **13'.c** | ISO 27003 ISMS clauses batch — all 26 ISMS clause leaves (largest, structurally uniform) | 1.5-2 days |
| **13'.d** | Chroma indexing (2 new collections) + chat digest promotion + eval case additions | ½-1 day |
| **13'.e** | Arc retrospective | ½ day |

Total: 3-4.5 days across 5 sub-arcs. Smaller than the original
6-arc plan (27004 batch dropped), but curation for 27003 + 27005
covers 32 of 38 originally-targeted leaves.

## Order rationale

- **27005 first** (13'.b) — biggest customer-facing signal (risk
  is universally scrutinised); single-family scope; validates
  the prose+SHOULD approach on the highest-stakes content
  before scaling to 27003
- **27003 second** (13'.c) — largest scope (26 leaves) but most
  uniform; benefits from lessons learned in b
- **Indexing + promotion third** (13'.d) — once curated content
  is stable, index into Chroma + flip chat digest priority to
  business_description so LLM sees the enriched prose

## Per-leaf enrichment mapping (previewed)

### 27005 batch (13'.b, 14 leaves)

| Leaf | 27005 § | Enrichment focus |
|---|---|---|
| 6.1 | §5, §6 | Risk mgmt process framework, context, cycles |
| 6.1.1 | §5.1 | Actions to address risks — process definition |
| 6.1.2 | §7 | Risk assessment: identify → analyse → evaluate |
| 6.1.3 | §8 | Risk treatment: options → controls → SoA → plan |
| 6.3 | §5.2 | Change-driven risk cycles |
| 8.1 | §9 | Operational risk process (assessment execution) |
| 8.2 | §7 | Op'l risk assessment execution |
| 8.3 | §8 | Op'l risk treatment execution |
| A.5.5 | §7.2 | Contact with authorities — risk sensing |
| A.5.7 | §7.2 | Threat intelligence — feeds identification |
| A.5.24 | §8.6 | Incident planning — risk-informed IR triggers |
| A.5.29 | §8.6 | Disruption security — BIA / continuity risk |
| A.5.30 | §8.6 | ICT readiness — BIA-driven RTO/RPO |
| A.7.5 | §7.2 | Physical/environmental threats — hazard identification |

### 27003 batch (13'.c, 26 leaves — same clause number in 27001 and 27003)

All 26 ISMS clauses (4.1-4.4, 5.1-5.3, 6.1-6.1.3, 6.2, 6.3,
7.1-7.5, 8.1-8.3, 9.1-9.3, 10.1-10.2). Enrichment per each is
direct-mapped by clause number to 27003:2017 §X.

## Success criteria

1. Every one of the 32 curated target leaves (17 27003-only + 8
   27003+27005 + 1 27003 formerly-27003+27004 + 6 27005-only)
   has ≥1 authority-cited paragraph appended to
   `business_description` sourced from the correct guidance
   standard. The 6 unenrollment-affected monitoring leaves
   (A.5.22/36/37, A.7.4, A.8.15, A.8.16) receive no citation
   in Ship 13 — reserved for a future 27004:2016 curation arc.
2. SHOULD additions where prescriptive language justifies them
   (targeted goal: ~5-10 new SHOULDs across the arc; NOT a
   requirement to add SHOULDs to every leaf).
3. Chroma collections built for each guidance standard;
   retrieval verified with sample queries.
4. Chat digest priority flipped (or guidance-line format added)
   so LLM sees the enriched prose at chat time (Ship 12'.d
   deferred item closed).
5. Eval suite still 225/226 PASS + 1 WARN + 0 FAIL — or better.
6. 2+ new eval cases citing the guidance authority (e.g.,
   "what risk assessment methodology does 27005 recommend?"
   → answer cites 27005 §7 correctly).

## Constraints + risk register

- **Copyright discipline**: source `.txt` files live in
  `/data/arioncomply/private/` — gitignored. Only paraphrased
  authority-cited paragraphs enter the curation source; no
  verbatim block extraction.
- **Prompt bloat risk**: Ship 11'.d violated case-file discipline
  by expanding critic prompts. Ship 13 curation writes to
  `business_description` (data), not to LLM prompts (code).
  Chat digest promotion (13'.e) will be measured carefully —
  if digest length balloons past current budgets, use a
  guidance line rather than full business_description swap.
- **Edition drift lesson**: Ship 12'.b enrolled 27004:2016 by
  assumption without seeing the text. Ship 13'.a discovered the
  actual available PDF is the 2009 first edition. Fixed by
  unenrollment (schema_v85) + citation scrub. Future arcs
  must confirm the exact edition of an available text before
  enrolling — same lesson as [[ship-8-prime-arc-retrospective-2026-07-20]]'s
  "verify data-driven hypotheses BEFORE building" applied
  retroactively to registry stubs.
- **Guidance-vs-normative discipline**: NO new MUSTs from
  guidance content. Reviewer discipline — check every
  proposed `must_contain` addition passes the "auditor could
  cite this as an obligation" test.

## Related

- [[ship-12-prime-a-iso27000-grounding-audit-2026-07-21]] — the audit that identified the 38 targets
- [[ship-12-prime-c-iso27000-citation-stubs-2026-07-21]] — the Ship 12'.c authority footers Ship 13 builds on
- [[ship-12-prime-arc-retrospective-2026-07-21]] — the deferred items 13'.e closes
- [[curation-phase-b-retrospective]] — the prior curation-arc discipline template
