---
name: ship-23-prime-b-curation-fill-2026-07-24
description: "Ship 23'.b — filled 55 structural cross-role edges (Gap 1: 40 SUPPORTS 27701→27001 parent + Gap 3: 19 A.8 Tech→GDPR DEMONSTRATES). Skipped Gap 2 text enrichment per user directive"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 23'.b — structural curation batch closing Gap 1 + Gap 3
from the Ship 23'.a audit. Zero digest bloat — edges are
structural metadata composed deterministically at query time,
not injected into prompts. Commit `cf7e417`.

## Gap 1 fill — ISO27701_BATCH4_PARENT_EDGES (40 SUPPORTS)

Every previously-unlinked ISO 27701 extension (30 nodes) now
has a documented SUPPORTS → ISO 27001 parent program.

Mapping strategy:
- **Controller-side (A.7.2.x, A.7.3.x, A.7.4.x)** — primary
  parent = A.5.34 (Privacy and protection of PII, the ISO
  27001 privacy anchor). Secondary edges where the ISO/IEC
  27002 clause or 27701 clause text makes another relationship
  explicit (A.5.31 legal on lawful-basis controls, 6.1.2
  risk assessment on PIA, A.5.9 inventory on records-shaped
  controls, A.5.19 supplier for third-party handling).
- **Processor-side (B.8.x)** — primary parent = A.5.19/A.5.20
  supplier controls (processor obligations are supplier-
  contract-shaped). Secondary edges for transfer + deletion
  specialisations.
- High-confidence mappings only; each edge cites ISO/IEC
  27701:2019 + ISO/IEC 27002:2022 clauses.

Coverage: **26 → 66 SUPPORTS edges (+40)**;
**26/49 → 49/49 extensions with parent (53% → 100%)**.

## Gap 3 fill — A8_TECH_GDPR_BRIDGE_EDGES (19 DEMONSTRATES)

Every previously-unlinked A.8 tech control (15 nodes) now
has a documented DEMONSTRATES → GDPR Article edge.

Mapping strategy:
- Every A.8 tech control DEMONSTRATES at least Art.32
  (Security of processing) — technical safeguards are the
  direct implementation surface for Art.32.1's TOM
  requirement.
- A.8.28 secure coding + A.8.31 environment separation also
  DEMONSTRATES Art.25 (Data protection by design).
- A.8.30 outsourced development also DEMONSTRATES Art.28
  (Processor) — external-supplier development is a processor
  arrangement.
- A.8.33 test information also DEMONSTRATES Art.5 (purpose
  limitation) — test datasets must not reuse PII outside its
  collection basis.

Coverage: **A.8 unlinked 15/34 (44%) → 0/34 (0%)**;
**ISO 27001 total linked 55/126 (44%) → 70/126 (55.6%)**.

## Gap 2 intentionally skipped

ISO 27701 `cross_framework_summary` property (0/49) was NOT
filled. Per user directive: deterministic composition from the
now-filled structural edges gives the same UX outcome without
bloating the digest / LLM prompt with 10-25KB of narrative
text. Aligns with the codified property from Ship 20-22 that
structural metadata never comes from an LLM emission.

## Verification

Ran `enrichment/relationships/load_to_neo4j.py`:
- 725 total edges merged (+55 new + minor re-merge idempotence).

Re-ran `scripts/audit_cross_role_edges.py`:
- ISO 27001 linked: 44% → 55.6%
- A.8 Tech: 100% linked (was 56%)
- ISO 27701 → parent (SUPPORTS): 100% (was 53%)

## Ship 23 progress

| Sub-arc | Status |
|---|---|
| 23'.a Audit + gap report | ✓ (3a730d1) |
| **23'.b Fill Gap 1 + Gap 3 (this)** | **✓ (cf7e417)** |
| 23'.c Role-grouped chat surface | next |
| 23'.d Eval + retro | pending |

## Related

- [[ship-23-prime-a-audit-2026-07-24]] — audit that surfaced
  these gaps
