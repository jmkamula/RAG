---
name: ship-13-prime-b-iso27005-enrichment-2026-07-21
description: "Ship 13'.b — 14 risk-adjacent leaves enriched with authored ISO 27005:2022 paragraphs; specific § pointers verified against source text"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 13'.b (2026-07-21) — second sub-arc of Ship 13. Enriched
14 risk-adjacent ISO 27001 leaves' `business_description` with
authored paragraphs paraphrasing ISO 27005:2022 guidance, each
carrying a specific § pointer verified against the source text.

## What ships

`scripts/enrich_iso27005_leaves.py` — idempotent Neo4j enrichment.
Appends per-leaf paragraphs AFTER the Ship 12'.c citation footer;
skips if the `Per ISO 27005:2022` marker is already present.

Applied to demo Neo4j: **14 leaves updated, 0 skipped, 0 missing**.
Second pass reports 14 already-marked, 0 updates — idempotent.

Total added: ~7.6 KB across the 14 leaves (avg ~540 chars per
paragraph). Length range: 419c (8.2 op'l assessment, terse) to
820c (6.1.2 risk assessment, the most content-rich leaf).

## Per-leaf enrichment table

| Leaf | 27005 § | Bytes added | Focus |
|---|---|---|---|
| 6.1 | §5-§6 | 534 | Framework + context + iterative cycles |
| 6.1.1 | §5.1 | 499 | Iteration + decision points |
| 6.1.2 | §7 (§6.4.2) | 820 | Three activities + risk owner + acceptance criteria |
| 6.1.3 | §8 (§8.5, §8.6) | 769 | 4 treatment options + preventive/detective/corrective + SoA + plan |
| 6.3 | §5.2 | 536 | Strategic + operational cycles + significant-change trigger |
| 8.1 | §9 | 554 | Planned intervals + budget cycles + change-triggered rounds |
| 8.2 | §7 + §9.1 | 419 | Op'l execution of assessment process |
| 8.3 | §8.6 + §9.2 | 606 | Treatment plan required elements + residual acceptance |
| A.5.5 | §7.2 | 486 | Authority contact as threat sensing |
| A.5.7 | §7.2 | 552 | Threat intel feeds identification |
| A.5.24 | §8.6 | 558 | IR framework as corrective/detective treatment |
| A.5.29 | §8.2 + §8.6 | 517 | Disruption treatment options + performance indicators |
| A.5.30 | §8.6 | 527 | BIA-driven RTO/RPO + technical measures |
| A.7.5 | §7.2 (§8.6) | 607 | Physical/environmental threat identification |

## Curation discipline

**Guidance-not-normative principle upheld.** No new MUSTs added;
no `must_contain` mutations to existing EvidenceRequirements.
All content lives in `business_description` prose — auditor-facing
authority pointers, not compliance obligations.

**§ pointers verified against source text.** Every citation was
read directly from `/data/arioncomply/private/iso27005_2022.txt`
(pdftotext extract) before authoring. Example provenance:

- 6.1.2 paragraph cites §7 identify-analyse-evaluate (lines 1077-1096
  of extract) + §6.4.2 risk acceptance criteria (lines 813-897 of
  extract). Both read and paraphrased before authoring.
- 6.1.3 paragraph cites §8 four treatment options (lines 1494-1538)
  + preventive/detective/corrective classification (lines 1626-1673)
  + §8.5 SoA + §8.6 plan (line 1769). All verified.
- A.5.24 paragraph cites §8.6.1 treatment-plan performance
  indicators (line 1817-1819 of extract). Verified.

**Paraphrase, not verbatim.** No block-quoting from the standard
— copyrighted text stays in `/data/arioncomply/private/`
(gitignored). Curator authored English paraphrases, then verified
against source before commit.

**Composability with Ship 12'.c footers.** The new paragraphs
append to `business_description` AFTER the existing
`[Related guidance: …]` citation footer, so the reader sees:
existing prose → footer → enrichment paragraph. Order documents
progression: raw obligation → authority pointer → implementation
guidance.

## Surface impact

Enriched content surfaces on:
- **Evidence Package "What this is about"** — auditor prose via
  `evidence_prose` output-gateway surface (verified in Ship 12'.c)
- **External API `/posture/{ref}`** — same field
- **Neo4j queryable state** — future retrieval / Signal C /
  fingerprint index

Does NOT yet surface on chat digest — that flip is Ship 13'.d
scope (see [[ship-12-prime-arc-retrospective-2026-07-21]]
deferred item). Until 13'.d, chat citations to 27005 rely on
the LLM's training-data knowledge; Evidence Package + admin
surfaces are the first beneficiaries of the enrichment.

## Impact on baseline

Data-only change. Chat digest doesn't consume business_description
by default (obligation_text priority). Eval expected unchanged.

Eval run confirmed: **225/226 PASS + 1 WARN + 0 FAIL** — the
1 WARN is the pre-existing #200 gap_analysis vs posture_check
mismatch; baseline unchanged. Zero regressions from the 27005
prose enrichment.

## What NOT to add without more work

Some potentially-prescriptive fragments were deliberately kept
prose-only rather than promoted to SHOULDs:

- 27005 §6.4.2 j) "risk acceptance criteria should be approved by
  the authorized management level" — would be a candidate for
  `risk_acceptance_criteria_signoff` SHOULD on 6.1.2. Deferred.
- 27005 §8.6.1 "for each treated risk the treatment plan should
  include: rationale, accountable owner, actions, resources,
  performance indicators, constraints, reporting, timeline,
  status" — would be a candidate for expanding 6.1.3's
  `risk_treatment_plan` MUST to enumerate required elements.
  Deferred.
- 27005 §7.2.2 "risk owners should have appropriate accountability
  and authority for managing identified risks" — would be a
  candidate for `risk_owner_authority_check` SHOULD on 6.1.2.
  Deferred.

Rationale for deferral: Ship 13'.b's job was prose enrichment
across all 14 leaves. Adding MUSTs / SHOULDs is a separate
curator decision (each addition can flip existing tenant
postures). Batching the SHOULD promotions into a review pass
after 13'.c 27003 batch lets the curator judge cross-standard
consistency before mutating checklist items. Ship 13'.e is a
candidate arc-close item to sweep for high-confidence
promotions.

## Ship 13 progress

| Sub-arc | Status |
|---|---|
| 13'.a Design + 27004 unenrollment | ✓ |
| **13'.b 27005 batch (14 leaves)** | **✓ (this doc)** |
| 13'.c 27003 batch (26 ISMS clauses) | next |
| 13'.d Chroma + chat digest promotion + eval | pending |
| 13'.e Arc retrospective | pending |

## Related

- [[ship-13-prime-a-iso27000-curation-design-2026-07-21]] — design + sub-arc plan
- [[ship-12-prime-c-iso27000-citation-stubs-2026-07-21]] — the citation footers this arc builds on
- [[curation-phase-b-retrospective]] — prior curation-arc discipline template
- Ship 13'.c: 27003 ISMS clause batch (next)
