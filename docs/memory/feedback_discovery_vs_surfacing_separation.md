---
name: feedback-discovery-vs-surfacing-separation
description: Strict subscription for evidence surfacing + jurisdiction-driven enrolment nudges + universal discovery universe for instant-flip and future automation
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

# Discovery universe vs evidence surface — separation rule

**Rule**: persistence layer is framework-agnostic (the "discovery
universe"); presentation layer (Stage-1 queue, Stage-2 queue,
dashboards, chat citations) is strictly filtered to the tenant's
enrolled frameworks (the "evidence surface"). Cross-framework
findings we discovered but didn't surface become the substrate
for jurisdiction-driven enrolment nudges — never surfaced as
evidence unless enrolled.

**Why**: user framing 2026-09-08 after seeing Art.30 GDPR findings
appear in an ISO-only tenant's Stage-1 queue. Two motivating uses
for the universal discovery layer: (1) instant compliance flip
when a tenant enrols a new framework — data is already landed,
posture just becomes visible; (2) foundation for future automated
evidence gathering (cite-mode arc from Ships 92'.a-f) where the
discovery universe becomes the substrate cite-mode automation
surfaces from.

**How to apply**:

- **Persist unconditionally** in `discover_workbook`,
  `discover_doc`, `persist_proposals`,
  `persist_arbitrated_findings`, `write_findings`. Do NOT add
  tenant_standards filters here. Catalog is universal;
  per-tenant scoping is a display concern.
- **Filter surfacing** in `list_queue` (Stage-1),
  `list_pending_for_control`, `list_pending_proposals` (Stage-2),
  notification producers on these tables, and chat xfw citations
  — INNER JOIN `tenant_standards` on `standard_id` where
  `status='enrolled'`.
- **Nudge on jurisdiction fulfilment**, not on discovery. Use
  `rag/scoping/applicability.py` fact-driven rules
  (Ship 110'.d) — if `client_facts.eu_data_subjects=TRUE` and
  GDPR is not enrolled, propose enrolment. Back the nudge with
  discovery counts ("your workbook already contains 4 GDPR
  Art.30 rows we can activate on enrolment") if available, but
  the trigger is JURISDICTION not DISCOVERY. Discovery counts
  are supporting evidence, not the primary signal.
- **Chat xfw bridge footer**: strict-mode aligns with this rule
  — cite refs from enrolled frameworks only. If discovery
  surfaced non-enrolled framework bridges, convert to an
  enrolment nudge rather than dropping silently.
- **Regression test invariant**: seed an out-of-scope finding
  → assert it's absent from Stage-1/Stage-2 queues → enrol the
  framework → assert it appears. Locks the "instant flip" property.

**What this rules out**:
- Filtering at write time / discovery time (loses "instant flip"
  and cite-mode automation substrate)
- Grey-out for evidence surfaces (worklists ≠ discovery surfaces
  per Ship 104'.f — Get Started/Topics grey-out is right for
  discovery; Stage-1/Stage-2 are worklists and get strict filter)
- Discovery-count-driven enrolment prompts as primary signal
  (jurisdiction fits the tenant's real regulatory scope;
  discovery just tells us what evidence would activate)

Related: [[ship-110-prime-arc-retrospective-2026-09-03]]
(applicability rules), [[ship-104-prime-arc-retrospective-2026-09-02]]
(grey-out vs filter pattern), [[ship-128-prime-arc-retrospective-2026-09-08]]
(surfaced this gap when workbook 656 findings landed with 2 GDPR
rows in an ISO-only tenant's queue).
