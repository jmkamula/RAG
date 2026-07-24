---
name: ship-24-prime-a-bridge-design-2026-07-24
description: "Ship 24'.a — design memo with explicit mapping table for ~35 new edges (27 ISO 27001 → GDPR bridges + 8 weak ISO 27701 ties); pushes ISO 27001 linked from 55.6% → ~78%"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 24'.a — opens Ship 24 arc (bridge fill completion).
Follow-on to Ship 23'.b which closed the 3 highest-priority
gaps (A.8 tech + 27701 parent). This arc closes the remaining
27 meaningful ISO 27001 gaps + 8 weak 27701 ties. After
Ship 24, every ISO 27001 unlinked control will be
structurally defensible (management-system process clauses,
cloud-N/A physical, or umbrella refs).

## Coverage question — why 55.6% linked and what does it mean

Post-Ship-23'.b: 70/126 ISO 27001 controls linked (55.6%);
56 unlinked. Breakdown into three classes:

**Defensibly unlinked (~29)** — legitimate structural
absence:
- ISMS 4-5 (8 nodes) — Context + Leadership clauses.
  Describe HOW to run the ISMS, not WHAT to control.
- A.7 Physical (13 nodes) — cloud-only orgs mark N/A; even
  architecturally physical has diffuse GDPR mapping (folded
  into Art.32 "technical + organisational" but not direct).
- Umbrella clause refs (6, 7, 9, 10) — container refs,
  not controls.

**Real gaps — GDPR bridges (~27)**:
- A.5 Org (10) — access/identity/incident family; A.5.7/10/
  11/13/16/17/27 all have Art.32 or Art.33/34 relevance.
- A.6 People (4) — personnel security; screening/NDA/remote
  working all → Art.32 personnel TOM.
- ISMS with obvious GDPR ties (~13) — 6.1.1/6.1.3 risk →
  Art.35 DPIA + Art.24; 7.2/7.3/7.4/7.5 support → Art.29/
  30/32/39; 8.1/8.2/8.3 operations → Art.35/24;
  9.2/10.1/10.2 → Art.24 accountability.

**Weak ISO 27701 ties possible (~8)** — where the PII
overlay is real but the extension standard designed it
additive not annotative:
- A.5.16 Identity → A.7.3.4 (Consent withdraw) +
  A.7.3.9 (Handling requests)
- A.5.17 Authentication → A.7.3.9 (Identifying requestor)
- A.5.11 Return of assets → A.7.4.5 (PII deletion at end)
- A.5.27 Learning from incidents → A.7.3.9 (Handling
  requests / breach-adjacent)
- A.6.5 Post-termination → A.7.4.5 (deletion tie)
- A.6.6 NDA → A.7.2.6 (Processor contracts pattern)
- A.5.13 Labelling → A.7.4.4 (Minimization / classification)

Total Ship 24 batch: **~35 edges** (~27 GDPR + ~8 27701).
Post-Ship-24 projected coverage: **~97/126 linked (77%)**.
Remaining unlinked (~29) all defensibly unlinked.

## Mapping table — 27 GDPR bridges

### A.5 Organisational (10 edges)

| Source | Edge | Target | Rationale |
|---|---|---|---|
| A.5.5 Contact with authorities | DEMONSTRATES | Art.33 | Breach notification to supervisory authority is the primary Art.33 mechanism. |
| A.5.6 Contact with special interest groups | SUPPORTS | Art.32 | Threat-intel from special-interest groups feeds Art.32.1.d regular testing/evaluation. |
| A.5.7 Threat intelligence | DEMONSTRATES | Art.32 | Threat intelligence feeds the "regularly test + evaluate" leg of Art.32.1.d. |
| A.5.10 Acceptable use of assets | DEMONSTRATES | Art.32 | Acceptable-use policy establishes the personnel-side handling of PII assets, an Art.32.1 confidentiality measure. |
| A.5.11 Return of assets | DEMONSTRATES | Art.32 | End-of-employment asset return prevents PII leakage post-departure, an Art.32.1 confidentiality control. |
| A.5.13 Labelling of information | DEMONSTRATES | Art.5 | Data classification via labelling supports Art.5.1.b purpose limitation + Art.5.1.f integrity. |
| A.5.13 Labelling of information | SUPPORTS | Art.32 | Classification labels enable the differentiated protection Art.32 requires. |
| A.5.16 Identity management | DEMONSTRATES | Art.32 | Identity management is the foundational access-control TOM of Art.32.1. |
| A.5.17 Authentication information | DEMONSTRATES | Art.32 | Credential controls are a core Art.32.1 confidentiality + integrity measure. |
| A.5.27 Learning from incidents | DEMONSTRATES | Art.32 | Post-incident lessons feed Art.32.1.d "regularly evaluate the effectiveness" of security measures. |

### A.6 People (4 edges)

| Source | Edge | Target | Rationale |
|---|---|---|---|
| A.6.1 Screening | DEMONSTRATES | Art.32 | Personnel screening reduces insider risk for PII-processing roles, an Art.32.1 confidentiality measure. |
| A.6.5 Post-termination responsibilities | DEMONSTRATES | Art.32 | Post-employment obligations preserve PII confidentiality after role change / departure. |
| A.6.6 Confidentiality / NDA | DEMONSTRATES | Art.32 | NDAs create the legal wrapper for PII confidentiality with personnel + contractors. |
| A.6.7 Remote working | DEMONSTRATES | Art.32 | Remote-work controls extend Art.32.1 TOM to non-office environments where PII is accessed. |

### ISMS clauses (13 edges)

| Source | Edge | Target | Rationale |
|---|---|---|---|
| 6.1.1 General planning | DEMONSTRATES | Art.24 | General risk-planning at 6.1.1 is a foundational Art.24 controller-accountability step. |
| 6.1.3 Risk treatment | DEMONSTRATES | Art.35 | Information-security risk treatment overlaps materially with GDPR Art.35 DPIA outputs. |
| 6.1.3 Risk treatment | SUPPORTS | Art.24 | Risk-treatment decisions are documented as part of Art.24 controller-accountability evidence. |
| 6.2 Information security objectives | DEMONSTRATES | Art.24 | Documented objectives are one of the artefacts controllers cite under Art.24. |
| 6.3 Planning of changes | DEMONSTRATES | Art.25 | Change-planning is the operational surface of Art.25 privacy-by-design — every change is a design decision. |
| 7.2 Competence | DEMONSTRATES | Art.39 | Personnel competence (training + awareness) is one of Art.39.1.b DPO monitoring tasks. |
| 7.3 Awareness | DEMONSTRATES | Art.32 | Personnel awareness of PII-handling responsibilities is an Art.32.1 organisational measure. |
| 7.3 Awareness | SUPPORTS | Art.29 | Processors' + subprocessors' personnel act only on instruction — awareness training encodes this. |
| 7.4 Communication | DEMONSTRATES | Art.13 | Internal communication frameworks support Art.13 information-to-be-provided obligations. |
| 7.5 Documented information | DEMONSTRATES | Art.30 | Documented information includes the RoPA (records of processing) required by Art.30. |
| 8.1 Operational planning | DEMONSTRATES | Art.24 | Operational planning + control is Art.24 accountability at the day-to-day layer. |
| 9.2 Internal audit | DEMONSTRATES | Art.24 | Internal audit is one of the primary Art.24 accountability mechanisms. |
| 10.1 Continual improvement | DEMONSTRATES | Art.24 | Continual improvement of the ISMS demonstrates Art.24 ongoing controller-accountability. |

## Mapping table — 8 weak ISO 27701 ties (SUPPORTS 27701 → 27001)

Direction: extension → parent, matching existing pattern.

| Source (27701) | Target (27001) | Rationale |
|---|---|---|
| A.7.3.4 Consent modify/withdraw | A.5.16 Identity management | Identifying + authenticating PII principals for consent-change requests. |
| A.7.3.9 Handling requests | A.5.16 Identity management | Request-handling requires identity verification of the requestor. |
| A.7.3.9 Handling requests | A.5.17 Authentication information | Verifying requestor identity leans on the authentication controls at A.5.17. |
| A.7.3.9 Handling requests | A.5.27 Learning from incidents | Request-handling patterns feed the incident-learning loop when patterns emerge. |
| A.7.4.5 PII de-identification / deletion | A.5.11 Return of assets | End-of-employment asset return is a specific instance of the PII deletion pattern. |
| A.7.4.5 PII de-identification / deletion | A.6.5 Post-termination responsibilities | Deletion-at-end-of-processing extends to leaver PII-access cleanup. |
| A.7.2.6 Contracts with PII processors | A.6.6 NDA | Processor contract terms include NDA-like confidentiality obligations. |
| A.7.4.4 PII minimization objectives | A.5.13 Labelling of information | Classification labels enable minimization decisions at the data layer. |

## Verification plan

Post-implementation:
- `enrichment/relationships/load_to_neo4j.py` — expect ~35 new edges merged.
- `scripts/audit_cross_role_edges.py`:
  - ISO 27001 linked: 55.6% → ~77% projected.
  - A.5 unlinked: 10 → 0.
  - A.6 unlinked: 4 → 0.
  - ISMS clauses unlinked: 29 → ~16 (13 filled; the 8 top-level Context/Leadership + 8 umbrellas + 6.1.1 already covered stay).

Post-Ship-24 unlinked pattern (should be defensible):
- ISMS 4-5 (Context + Leadership) — 8 nodes, all process-shaped, no natural GDPR mapping.
- A.7 Physical — 13 nodes, cloud-only N/A.
- Umbrella clause refs (6, 7, 9, 10) — 4 nodes.
- A.5.32 Intellectual property — 1 node, no PII overlap.

## Scope revision (post-user-feedback)

User challenged the "A.7 Physical defensibly unlinked" call
— correctly noting that tenant-N/A ≠ structural absence.
The catalog is shared across all tenants; if a bank /
hospital / manufacturer onboards with physical premises,
their A.7 queries should surface Art.32 obligations. The
edges must exist in the catalog to be composable.

Same reasoning applies to ISMS 4-5 Context/Leadership —
those clauses have Art.24 accountability relationships even
if they're process-shaped.

**Revised Ship 24 batch: ~54 edges.**

Additional 13 edges for A.7 Physical → Art.32:

| Source | Edge | Target | Rationale |
|---|---|---|---|
| A.7.1 Physical security perimeters | DEMONSTRATES | Art.32 | Physical perimeter prevents unauthorised access to PII systems, Art.32.1 confidentiality. |
| A.7.2 Physical entry | DEMONSTRATES | Art.32 | Entry controls to PII-processing facilities, Art.32.1 confidentiality. |
| A.7.3 Securing offices/rooms/facilities | DEMONSTRATES | Art.32 | Room-level access controls, Art.32.1 confidentiality. |
| A.7.4 Physical security monitoring | DEMONSTRATES | Art.32 | CCTV + intrusion detection — Art.32.1.d regular monitoring. |
| A.7.5 Protecting against physical/environmental threats | DEMONSTRATES | Art.32 | Fire, flood, earthquake — Art.32.1.b availability + integrity. |
| A.7.6 Working in secure areas | DEMONSTRATES | Art.32 | Sensitive-area work restrictions, Art.32.1 confidentiality. |
| A.7.7 Clear desk / clear screen | DEMONSTRATES | Art.32 | Bystander-proof workstations, Art.32.1 confidentiality. |
| A.7.8 Equipment siting and protection | DEMONSTRATES | Art.32 | Hardware placement to reduce exposure, Art.32.1 confidentiality + integrity. |
| A.7.10 Storage media | DEMONSTRATES | Art.32 | Physical storage of PII (backups, portable drives), Art.32.1 confidentiality + integrity. |
| A.7.11 Supporting utilities | DEMONSTRATES | Art.32 | Power / cooling / network availability, Art.32.1.b resilience. |
| A.7.12 Cabling security | DEMONSTRATES | Art.32 | Tap-proof cabling for PII in transit, Art.32.1 confidentiality. |
| A.7.13 Equipment maintenance | DEMONSTRATES | Art.32 | Preserves availability + integrity of PII-processing hardware, Art.32.1.b. |

Additional 6 edges for ISMS 4-5 → Art.24 (Context + Leadership):

| Source | Edge | Target | Rationale |
|---|---|---|---|
| 4.2 Understanding the needs and expectations of interested parties | DEMONSTRATES | Art.24 | PII principals + supervisory authorities are interested parties whose needs shape controller accountability. |
| 4.3 Determining the scope of the ISMS | DEMONSTRATES | Art.24 | ISMS scope establishes the perimeter within which Art.24 controller responsibility applies. |
| 4.4 Information security management system | DEMONSTRATES | Art.24 | The ISMS itself IS the accountability framework Art.24 requires. |
| 5.1 Leadership and commitment | DEMONSTRATES | Art.24 | Top-management commitment is the leadership evidence Art.24 requires from controllers. |
| 5.2 Policy | DEMONSTRATES | Art.24 | Documented information-security policy is one of the Art.24 accountability artefacts. |
| 5.3 Organisational roles, responsibilities and authorities | DEMONSTRATES | Art.37 | Role-and-responsibility documentation is where DPO designation (Art.37) is captured. |
| 5.3 Organisational roles, responsibilities and authorities | SUPPORTS | Art.24 | Role clarity underlies controller accountability. |

Total Ship 24 batch (revised): **54 edges** (27 GDPR + 13
A.7 + 7 ISMS 4-5 + 8 weak 27701). Projected coverage:
**~120/126 = 95% linked**. Remaining unlinked (~6):
umbrella refs (4, 5, 6, 7, 9, 10) — legitimate container
refs, not controls.

Skipped intentionally:
- **A.5.32 Intellectual property** — no natural PII overlay
  in the base standard.
- **6.1.1 General** (already in original 27 list) — kept.
- **Umbrella refs** (4/5/6/7/9/10) — container refs.

## Design decisions locked in 24'.a

1. **Explicit mapping table before implementation.** Same
   discipline as Ship 23'.a's audit-first — reviewers can
   check each edge before it's authored.

2. **Skip A.7 Physical entirely.** 13 controls remain
   unlinked but the mapping is diffuse (Art.32 "physical
   security" is fold-in language, not a distinct edge).
   Fill decision deferred; cloud-only tenants make this
   low-value.

3. **Skip A.5.32 Intellectual property.** No PII overlap;
   IP protection is scoped to the org's own IP not
   personal data.

4. **Skip ISMS umbrella refs (6/7/9/10).** Container refs
   for sub-clauses; edges belong on the sub-clauses.

5. **Weak 27701 ties stay strictly high-confidence.** Only
   8 edges — no forcing 27701 extensions onto 27001
   controls without natural PII overlap.

## Ship 24 progress

| Sub-arc | Status |
|---|---|
| **24'.a Design + mapping table (this)** | **✓** |
| 24'.b Implement + load + verify | next |
| 24'.c Eval + retrospective | pending |

## Related

- [[ship-23-prime-arc-retrospective-2026-07-24]] — arc that
  Ship 24 completes (curation-fill continuation)
- [[ship-23-prime-b-curation-fill-2026-07-24]] — the batch
  pattern this arc extends
