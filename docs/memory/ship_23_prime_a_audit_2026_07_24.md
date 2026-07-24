---
name: ship-23-prime-a-audit-2026-07-24
description: "Ship 23'.a — Neo4j cross-role edge + text-enrichment audit; surfaces 3 concrete curation gaps blocking the role-aware chat surface (ISO 27701 parent edges, ISO 27701 cross_framework_summary, A.8 Tech GDPR links)"
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 23'.a — opens Ship 23 arc (role-aware chat surface).
Read-only audit-first sub-arc. Objective: enumerate the
cross-role edges + text-enrichment coverage that a role-aware
chat surface would depend on, and report gaps.

## New tool: `scripts/audit_cross_role_edges.py`

Read-only Neo4j survey with 4 sections:
1. Cross-role edge coverage per standard (with_cross,
   zero_cross, avg, max).
2. Text-enrichment coverage (`cross_framework_summary`,
   `business_description`, `obligation_text`).
3. Per-standard family breakdown (A.5.x / A.6.x / A.7.x /
   A.8.x / ISMS clauses / B.x PIMS / GDPR Art.x).
4. Top-fanout controls + full cross-standard edge matrix.

Supports `--standard ISO27001:2022` filter + `--json` for
downstream processing.

## Key findings

### Cross-role edge coverage per standard

| Standard | Nodes | Linked | Unlinked | Avg fanout | Max fanout |
|---|---|---|---|---|---|
| ISO 27701:2019 (extension) | 49 | 49 (100%) | 0 | 2.3 | 7 |
| ISO 27001:2022 (program) | 126 | 55 (44%) | 71 | 1.4 | 15 |
| GDPR:2016/679 (obligation) | 303 | 51 (17%) | 252 | 0.8 | 21 |

Interpretation:
- **ISO 27701 (extension) is fully linked** — makes sense; every
  extension exists to extend a program or demonstrate an obligation.
- **ISO 27001 (program): 71 unlinked controls** — a real gap.
- **GDPR (obligation): 252 unlinked articles** — most of these are
  sub-articles (Art.5.1.a etc.) that inherit from parents; the
  17% coverage is the article-level rate rather than the
  sub-article-level rate.

### Text enrichment coverage

| Standard | Nodes | `cross_framework_summary` | `business_description` | `obligation_text` |
|---|---|---|---|---|
| ISO 27001:2022 | 126 | 126 (100%) | 126 (100%) | 126 (100%) |
| GDPR:2016/679 | 303 | 303 (100%) | 303 (100%) | 303 (100%) |
| **ISO 27701:2019** | **49** | **0 (0%)** | **49 (100%)** | **49 (100%)** |

**Surprising asymmetry**: ISO 27701 has ZERO cross_framework_
summary property despite being the highest structural-edge
coverage. Business description + obligation text are populated
— just this one enrichment field is missing.

### ISO 27001 unlinked by family

| Family | Unlinked / Total | % |
|---|---|---|
| ISMS clauses (4-10) | 29 / 33 | 88% |
| A.7.x (Physical) | 13 / 14 | 93% |
| A.6.x (People) | 4 / 8 | 50% |
| A.8.x (Technological) | 15 / 34 | 44% |
| A.5.x (Organisational) | 10 / 37 | 27% |

Interpretation:
- **A.7 Physical (93% unlinked)** — Arion is cloud-only, so most
  A.7 controls are N/A. Still, Art.32 covers "appropriate
  technical AND organisational measures" including physical
  safeguards. 13 unlinked = 13 missing GDPR bridges.
- **ISMS clauses (88% unlinked)** — clause 6.1.2 (risk
  assessment), 9.2 (internal audit), 10.1/10.2 (improvement)
  are the classic ones. Every clause SHOULD demonstrate at
  least Art.24 (controller responsibility) or Art.32 (security
  of processing).
- **A.8 Tech (44% unlinked)** — 15 tech controls without GDPR
  bridges. This is the biggest content gap; tech controls
  almost always have GDPR relationships (encryption ↔ Art.32.1.a,
  access control ↔ Art.32, incident response ↔ Art.33).

### Cross-standard edge matrix

```
DEMONSTRATES  ISO27001:2022  → GDPR:2016/679       149
IMPLEMENTS    ISO27001:2022  → GDPR:2016/679        90
IMPLEMENTS    ISO27701:2019  → GDPR:2016/679        86
DEMONSTRATES  ISO27701:2019  → GDPR:2016/679        86
IMPLEMENTS    GDPR:2016/679  → ISO27001:2022        82
SUPPORTS      ISO27001:2022  → GDPR:2016/679        41
SUPPORTS      GDPR:2016/679  → ISO27001:2022        37
SUPPORTS      ISO27701:2019  → ISO27001:2022        26  ← extension→parent edges
GOVERNANCE    GDPR:2016/679  → ISO27001:2022         7
GOVERNANCE    ISO27001:2022  → GDPR:2016/679         7
```

Observations:
- **Extension → Parent (ISO 27701 → ISO 27001) is 26 edges** for
  49 extension nodes. So **23 extensions (47%)** don't have a
  documented parent program via SUPPORTS. Critical for the
  user's "extension query → surface parent programs" ask.
- **No IMPLEMENTS: ISO 27701 → ISO 27001**. Extensions
  IMPLEMENT obligations (GDPR) via DEMONSTRATES/IMPLEMENTS
  edges; they SUPPORT programs (ISO 27001). Currently one-
  directional (SUPPORTS out of ISO 27701).
- **GDPR ↔ ISO 27001 is bidirectional** on IMPLEMENTS
  (90 out, 82 in). The reverse edge exists via curated inverse.

### Top-fanout controls (spot-check for correctness)

| Standard | Ref | Fanout | Title |
|---|---|---|---|
| GDPR | Art.5 | 21 | Principles relating to processing of personal data |
| GDPR | Art.28 | 15 | Processor |
| ISO 27001 | A.5.9 | 15 | Inventory of information and other associated assets |
| GDPR | Art.30 | 12 | Records of processing activities |
| GDPR | Art.32 | 11 | Security of processing |
| ISO 27001 | A.5.31 | 10 | Legal, statutory, regulatory and contractual requirements |

Looks right — these are the article/control families you'd
expect to have the broadest cross-role reach (principles,
processor obligations, asset inventory).

## Gap classification

Three concrete gaps blocking the role-aware chat surface:

**Gap 1 — ISO 27701 parent edges (23 controls, ~47% of extension)**
Extension → program (SUPPORTS) edges are sparse. When a tenant
asks about A.7.2.6 (ISO 27701 processor contracts), we can't
reliably tell them which ISO 27001 control it extends.

**Gap 2 — ISO 27701 cross_framework_summary property (0 of 49)**
Zero text-enrichment coverage. This asymmetry is likely a
Phase 2 loading omission — the property was populated for
ISO 27001 + GDPR but not ISO 27701.

**Gap 3 — A.8 Tech GDPR bridges (15 controls, 44% of family)**
Curator gap in the highest-value tech family. Encryption,
authentication, logging etc. should have GDPR Art.32 bridges.

Everything else (A.7 Physical, ISMS clauses, GDPR sub-article
low coverage) is defensible OR represents low-signal deferred
work.

## Sub-arc decision point

The user's role-aware chat surface design depends on:
- Program query → surface Extensions + Obligations
- Extension query → surface Programs + Obligations
- Obligation query → surface Programs + Extensions

**Gap 1 blocks extension queries** (can't surface parent
programs consistently).
**Gap 2 blocks intro-status-summary** (LLM was using
`cross_framework_summary` implicitly via the digest for the
"related standards" framing).
**Gap 3 blocks program queries on A.8** (Tech controls won't
surface obligations they should).

Two paths for Ship 23'.b + 23'.c:

**Path A — curation-fill first, then redesign**
- 23'.b: fill the 3 gaps via curator-authored edges + property
- 23'.c: implement role-grouped surface with confidence

**Path B — redesign first, ship with graceful degradation**
- 23'.b: implement role-grouped surface; when parent edge
  missing, section renders "No parent program documented"
- 23'.c: opportunistic gap-fill as tenants ask questions that
  surface empty sections

**Recommendation: Path A** — the gaps are concentrated (23
extensions + 15 A.8 controls + 49 property fills). Roughly
90 curator additions. That's a defined-scope curator arc, not
open-ended. Doing the fill first prevents the UI from
surfacing "no data" cards for the exact queries a tenant
would test the new surface with.

## Ship 23 progress

| Sub-arc | Status |
|---|---|
| **23'.a Audit + gap report (this)** | **✓ (script + memo)** |
| 23'.b Fill Gap 1 + Gap 2 + Gap 3 (curator arc) | next |
| 23'.c Role-grouped chat surface | pending |
| 23'.d Eval + arc retrospective | pending |

Actual sub-arc plan may split 23'.b further if any gap turns
out larger than expected during fill.

## Related

- [[framework-role-model-arc]] — the role model this arc's
  chat surface will make explicit
- [[dejargonize-ux-pass-2026-07-01]] — the consistent-across-
  surfaces principle Ship 23 extends to cross-role framing
- [[ship-14-prime-a-role-model-arc-2026-07-22]] — role model
  Ship 14 codified; Ship 23 makes it user-visible in chat
- [[ship-22-prime-arc-retrospective-2026-07-24]] — the arc
  whose demonstrator auto-inject introduced the "read the
  retired code as a spec" discipline this audit-first arc
  extends
