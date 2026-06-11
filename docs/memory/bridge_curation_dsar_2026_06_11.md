---
name: bridge-curation-dsar-2026-06-11
description: "SHIPPED 2026-06-11 (cbba0d9): 14 wrong-shape DSAR-family bridges pruned + 7 A.5.34 IMPLEMENTS bridges added. Surfaced when Security Test Report (A.5.15 evidence) produced 4 GDPR xfw proposals including wrong-actor Art.18/Art.21. Bridges live in 3 places: iso_nodes_phase1.json, gdpr_nodes_phase2.json, Neo4j (forward+reverse edges)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

First targeted bridge-curation pass since the graph was built.
The trigger: a Security Test Report doc upload generated 4 GDPR
xfw proposals (Art.18, Art.21, Art.32.1.b, Art.5.1.f) from a
single A.5.15 finding. Art.18 (restriction) and Art.21 (objection)
are wrong-actor — they're subject-rights, not access-control
implementation. Audit found this was a *family-wide* issue across
all DSAR articles (Art.15-21).

## What was wrong before

Each DSAR article (Art.15-21) had bridges from access-control /
inventory / auth controls because those are the semantic
neighbours of "data subject rights" in vocabulary. But DSAR
rights are about *controller → subject* obligations
(procedures, response timelines, fulfilment workflows), not
about *who-can-read-what*. The wrong-actor confusion produced
noise on every access-control evidence upload.

Specific over-broad bridges pruned:
  - A.5.15 → Art.15/18/21 (3) — wrong actor
  - A.5.18 → Art.15/18 (2) — same family
  - A.5.9  → Art.15/16/17/18/20/21 (6) — inventory is prereq, not bridge
  - A.8.3  → Art.18 (1) — access restriction ≠ processing restriction
  - A.8.5  → Art.15/20 (2) — authentication isn't subject-access

## What was missing

**A.5.34 (Privacy and protection of PII) had ZERO outbound GDPR
bridges.** It's the most natural ISO primary for subject-rights
procedures (the procedural side of DSAR fulfilment), but the
graph had no edges connecting it to any GDPR article. This was a
structural gap, not a single-edge oversight.

Added: A.5.34 IMPLEMENTS each of Art.15/16/17/18/19/20/21.

## What was kept (still-correct bridges)

  - A.5.33 SUPPORTS Art.15 (records protection — retrievable for DSAR)
  - A.5.18 SUPPORTS Art.17 (revoke access on deletion — marginal)
  - A.8.13 SUPPORTS Art.16/17 (backups affect rect/erasure)
  - A.8.9  SUPPORTS Art.16
  - A.7.14 SUPPORTS Art.17
  - A.8.10 IMPLEMENTS Art.17 (right primary for erasure)
  - A.5.37 IMPLEMENTS Art.19
  - A.5.14 + A.8.24 IMPLEMENTS Art.20

## Curation principle (for future passes)

A bridge should reflect a control that **does the work** for
the obligation, not one that's a **prerequisite** for it. By
that test:

  - Asset inventory (A.5.9) is a prerequisite for every DSAR
    obligation — you need to know what data you have. But it
    doesn't IMPLEMENT or even ENABLE any specific right. SUPPORTS
    at most, and even that adds noise. Bridges removed.
  - Access control (A.5.15) IS a primary control for
    confidentiality/integrity (Art.32.1.b + Art.5.1.f). It is
    NOT primary for DSAR rights — restriction/objection/access
    are about whether/how data is processed, not about which
    user can read which row.

## Where bridges live (3 sources of truth)

  1. `iso_nodes_phase1.json` — keyed by ISO control id, with a
     `cross_framework_summary` object listing GDPR articles.
  2. `gdpr_nodes_phase2.json` — keyed by GDPR article id, with a
     `cross_framework_summary` object listing ISO controls.
  3. Neo4j — physical edges stored as TWO directed edges per
     bridge: `(iso)-[r:REL]->(gdpr)` AND `(iso)<-[r:REL]-(gdpr)`.
     The undirected query `-[r]-` returns both, which is why an
     earlier audit showed 10 results for what felt like 5 bridges.

Every edit needs to touch all three. The curation script
`scripts/curate_dsar_bridges_2026_06_11.py` does this in lockstep
and is a reusable shape for future bridge passes.

Reload note: changing Neo4j alone is ephemeral if the graph is
ever rebuilt from JSON. JSON edits are the durable authority.

## Inconsistencies discovered

The two JSON sides aren't perfectly mirrored. Found 2 ISO-side
entries (A.5.18 → Art.15 SUPPORTS, A.5.18 → Art.18 SUPPORTS) that
didn't have matching entries on the GDPR side or in Neo4j. These
were orphan entries — declared on ISO side but never propagated.
Future loader runs would have re-created them, so cleaning the
ISO side closes the loop.

## Verification

Post-curation, re-upload of Security Test Report.docx:
  - Before: 1 + 4 = 5 findings (A.5.15 + Art.18 + Art.21 +
    Art.32.1.b + Art.5.1.f), 2 of them wrong-shape.
  - After: 1 + 2 = 3 findings (A.5.15 + Art.32.1.b + Art.5.1.f).
    Art.18 and Art.21 no longer surface.

Eval 196/198 (only #25/#26 known-stale) — best result of the
session. Cases #2/#16/#21/#24 (frequently borderline) all PASSed
this run, suggesting bridge cleanup may help xfw-touching answers
stay on-target. Borderline LLM cases are stochastic, so single-run
shouldn't be over-claimed, but no regressions either.

## Related

- [[posture-claim-hallucination-guard]] — bridge curation
  complements the L1/L3 compose-time guards: both reduce noise,
  but at different stages (proposal vs presentation).
- [[doc-curation-engine-v1]] — the xfw_proposer reads bridges
  to fire GDPR proposals on every doc upload. Pruning saves
  Stage-1 cycles on every future doc that touches access control.
