---
name: ship-12-prime-a-iso27000-grounding-audit-2026-07-21
description: "Ship 12'.a — audit of ISO 27000-family grounding; 27003/27004/27005 not enrolled; per-leaf enrichment targets enumerated"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 12'.a (2026-07-21) — opening audit memo for the ISO 27000-
family grounding expansion arc. Surfaces the gap the user
flagged: we use ISO 27002 as authorial reference for Annex A
controls, but ISO 27003 (ISMS clause guidance), 27004
(monitoring & measurement), and 27005 (risk management) are
completely absent from the codebase.

## Current grounding state

| Standard | In `standards` table | Codebase refs | Role | Curation depth |
|---|---|---|---|---|
| ISO 27001:2022 | ✓ | 357 | program | Full (Annex A + ISMS clauses 4-10) |
| ISO 27002:2022 | ✓ | 119 | guidance | Authorial reference; not explicitly cited in leaf descriptions |
| **ISO 27003** | ✗ | **0** | — | Missing |
| **ISO 27004** | ✗ | **0** | — | Missing |
| **ISO 27005** | ✗ | **0** | — | Missing |
| ISO 27017:2015 | ✗ | 1 (stray) | — | Not curated |
| ISO 27018:2019 | ✓ | 6 | extension | Enrolled but 0 leaves curated |
| ISO 27701:2019 | ✓ | 222 | extension | Full (196 leaves) |

## What each missing standard would provide

### ISO 27003:2022 — Management-system clause implementation guidance

Enriches: **26 ISMS clause leaves** (chapters 4-10).

- 4.1/4.2/4.3/4.4 — Context (external/internal issues, interested
  parties, scope determination, ISMS establishment)
- 5.1/5.2/5.3 — Leadership + Policy + Roles/Responsibilities
- 6.1.1/6.1.2/6.1.3 — Risk actions + Risk Assessment + Risk
  Treatment (also touched by 27005)
- 6.2/6.3 — Objectives + Change planning
- 7.1/7.2/7.3/7.4/7.5 — Resources + Competence + Awareness +
  Communication + Documented information
- 8.1/8.2/8.3 — Operational planning + Risk assessment execution
  + Risk treatment execution (overlap with 27005)
- 9.1/9.2/9.3 — Monitoring (overlap with 27004) + Internal audit
  + Management review
- 10.1/10.2 — Continual improvement + Nonconformity + corrective
  action

Current shape: each leaf's `business_description` in Neo4j is
the direct 27001 clause text (e.g. 4.1 = "The organization shall
determine external and internal issues that are relevant to its
purpose..."). 27003 would enrich with implementation guidance:
how to conduct the context analysis, what workshops look like,
what artefacts to produce, how to link to the risk process.

### ISO 27004:2022 — Monitoring, measurement, analysis, evaluation

Enriches: **7 monitoring/measurement leaves**.

- 9.1 (primary) — the whole monitoring/measurement framework
- A.5.22 — Supplier monitoring metrics
- A.5.36 — Compliance monitoring
- A.5.37 — Operating procedure effectiveness
- A.7.4 — Physical security monitoring
- A.8.15 — Logging (log-analysis metrics)
- A.8.16 — Monitoring activities (real-time detection metrics)

27004 provides: what metrics/KPIs to select, how to define an
information-need→measure→analysis→decision chain, how to
present results to management, sample metric templates by
control family.

### ISO 27005:2022 — Information security risk management

Enriches: **14 risk-adjacent leaves**.

- 6.1 / 6.1.1 / 6.1.2 / 6.1.3 (primary) — Risk framework +
  assessment methodology + treatment planning
- 6.3 — Change-planning risk analysis
- 8.1 / 8.2 / 8.3 — Operational risk execution
- A.5.5 — Contact with authorities (relates to consulted risk
  advisors)
- A.5.7 — Threat intelligence (feeds risk identification)
- A.5.24 — Incident planning (risk-informed IR triggers)
- A.5.29 / A.5.30 — Disruption / ICT readiness (BIA link to risk)
- A.7.5 — Physical/environmental threats

27005 provides: risk-assessment methodology options (asset-based
/ event-based / scenario-based), likelihood-consequence
taxonomies, risk-acceptance criteria examples, risk-register
schema fields, risk-treatment plan structure, ownership
patterns.

## Why this matters — concrete product impact

1. **Chat citation authority**. Today a user asking "how do I
   structure my risk assessment per ISO 27005?" gets no
   grounded answer — the LLM might respond from training data
   without a citable source. Post-Ship-12 (once texts land),
   the LLM can cite ISO 27005:2022 §7 methodology + §8
   treatment options as authority.

2. **Auditor-facing authority strengthening**. Evidence Package
   rows currently say "per ISO 27001 clause 6.1.2". Enriched
   rows would say "per ISO 27001 6.1.2 + ISO 27005:2022 §8".
   Same for 9.1 → +27004:2022 §7 metrics framework.

3. **MUST-level under-specification**. Our 6.1.2 leaf's MUSTs
   describe the artefact (procedure specifying criteria +
   identification + analysis + evaluation rules). 27005 would
   likely add MUSTs for: methodology declaration, likelihood-
   consequence matrix, risk-acceptance criteria document,
   ownership register, review triggers.

4. **Template thinness**. Our 6.1.2 template describes what to
   produce; 27005 has a canonical risk-register schema (asset,
   threat, vulnerability, likelihood, impact, level, owner,
   treatment, residual) our template could mirror.

## Constraint — standard texts not available

Only ISO 27701 is in `private/` (docx + PDF + OCR text). ISO
27003, 27004, 27005 texts are NOT stored anywhere accessible.
Full MUST-level curation requires the source texts.

Two paths:
- User acquires the standards → Ship 13+ delivers full curation
- Work from public summaries + domain knowledge → accuracy risk
  unacceptable for a compliance product

Ship 12 (this arc) works within the constraint: **audit +
enrollment stub + citation pointers**. Actual curation
batches wait for texts.

## Ship 12 sub-arc plan

**12'.a — this memo.**

**12'.b — Enroll 27003/27004/27005 in `standards` table.**
INSERT rows with `role='guidance'` and `standard_type='guidance'`.
Populates the standards registry so downstream code paths (chat
citation format, external API standard_id lookups) recognise
these standards even if we don't have their content curated yet.

**12'.c — Citation stub enrichment on existing leaves.**
For the 47 target leaves identified above, add authority-
citation pointers to the leaf's `business_description` field
in the Python curation source (e.g. `enrichment/documents/`).
Format: append ` [Guidance: ISO 27005:2022 §7-8]` at the end
of the description. No new MUSTs; no new content; just
authority pointers that:

- Surface in Evidence Package auditor prose
- Appear in chat citation prompts (LLM sees the guidance
  reference in the digest)
- Signal to future curators which leaves to enrich when texts
  land

**12'.d — Arc retrospective.**

## Deferred to Ship 13+ (texts required)

- 27005 MUST-level enrichment on 6.1.2/6.1.3 + risk-adjacent
  Annex A. Likely adds 3-5 MUSTs per leaf covering methodology
  declaration, risk-acceptance criteria, ownership, review
  triggers.
- 27004 MUST-level enrichment on 9.1 + monitoring-adjacent
  Annex A. Likely adds MUSTs for KPI selection framework,
  information-need declaration, presentation cadence.
- 27003 MUST-level enrichment across ISMS clauses. Likely
  adds implementation-guidance MUSTs (e.g. 4.3 scope MUSTs
  for boundary documentation, exclusion justification).
- Chroma collections for each guidance standard (queryable
  for retrieval).
- Cross-standard eval cases (chat asks "risk methodology per
  27005" → citation surfaces).

## Related

- User raised the question during Ship 11 close (2026-07-21)
- Ship 7'.a output audit already documented the citation
  format conventions in [[dejargonize-ux-pass-2026-07-01]]
- Standard-vocabulary infrastructure in `rag/output/vocab/`
  ready to accept new families
