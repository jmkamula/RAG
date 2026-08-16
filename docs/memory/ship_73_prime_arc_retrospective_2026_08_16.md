---
name: ship-73-prime-arc-retrospective-2026-08-16
description: "Ship 73' arc close-out (73'.a → 73'.c). Closes Task #595 (GDPR bridge-coverage gap). Wide-audit addendum revealed GDPR curation is near-complete on every surface except bridges; 73'.b authored 19 defensible bridge edges. Bridges surface end-to-end on Arion's Art.39 Evidence Package with the exact curator-authored rationale + auto-computed dimension summary + source-posture attribution."
metadata:
  type: project
  ship: "73'"
---

# Ship 73' arc close-out

Three sub-arcs + retro over ~1 day (2026-08-16). Zero schema, zero
code — pure curation + one audit script.

Opens directly out of Ship 68'.b's honest-mapping reframe: the
"asserted implementation via related controls" UX made the
uncurated-gap-signal legible for the first time, and Task #595
was the follow-on to author the missing pieces.

## Sub-arcs

| Sub | What shipped | Files | Retro |
|-----|---|---|---|
| 73'.a | Triage 91 GDPR articles → 14 bridgeable + 7 unbridgeable + 32 regulatory-internal + 38 already-bridged. 22 draft edges proposed. | `scripts/curation/audit_gdpr_bridge_gap_73a.py` + `results/gdpr_bridge_gap_audit.csv` | [[ship-73-prime-a-2026-08-16]] |
| 73'.a addendum | Wide curation audit across every surface (bridges, leaves, MUSTs, guidance, prereqs, doc/workbook mappings, fingerprints, eval, posture seeds). Confirmed GDPR is near-complete everywhere except bridges. Meta-lesson on audit-bugs. | `scripts/curation/audit_gdpr_curation_wide_73a.py` + `results/gdpr_curation_wide_audit.csv` | (same) |
| 73'.b | Refine 22 → 19 defensible edges (3 drops for auditor-defensibility, 2 upgrades). Author into relationship_catalog.py. Neo4j: 784 → 803 bridge edges. | `enrichment/relationships/relationship_catalog.py` | [[ship-73-prime-b-2026-08-16]] |
| 73'.c | This retro + dogfood on Arion Art.39 EP | — | (self) |

## The numbers

**GDPR bridge coverage** (whole-article, ISO source or GDPR
governance-target):
- Before Ship 73': **62%** (57 of 91 articles bridged or
  intentionally regulatory-internal)
- After Ship 73': **75%** (12 more articles bridged; 7 remain
  intentionally unbridged per honest carve-out)

The 7 unbridged carve-outs are documented and honest:
Art.77-80 (data-subject remedies), Art.81 (procedural), Art.84
(Member State penalties), Art.86 (public documents), Art.91
(church rules). None are ISO-implementable — leaving empty is
signal, not gap.

**Wide GDPR curation state (per surface, tenant-facing articles):**

| Surface | Gaps | Status |
|---|---:|---|
| Neo4j node existence | 0 | Complete |
| bridges_whole (before 73'.b) | 22 | **Closed by 73'.b** |
| Evidence Requirement leaves | 16 | 14 deliberate carve-outs + Art.5 DerivedSpec-only + Art.11 narrow. All defensible. |
| MUST guidance (Ship 56') | 0 | Complete |
| Prereqs (Ship 57') | 0 | Complete |
| doc_mappings | 0 | Complete |
| workbook_mappings | 0 | Complete |
| Fingerprints | 2 | Art.15, Art.30 — micro-arc candidate |
| Eval cases | 1 | Art.85 — micro-arc candidate |
| Posture seeds (Arion) | 0 | Complete |

GDPR curation is **essentially complete** on every surface except
2 fingerprints + 1 eval case (all micro-arcs).

## The 19 authored edges

By article + edge direction:

| Article | Source (ISO)  | Target (GDPR) | Type       | Confidence |
|---------|---------------|---------------|------------|------------|
| Art.11  | A.8.11, A.5.34 | Art.11        | IMPLEMENTS + SUPPORTS | medium |
| Art.23  | Art.23         | A.5.31        | GOVERNANCE | high    |
| Art.27  | A.5.19 + Art.27| Art.27, A.5.31| SUPPORTS + GOVERNANCE | medium, high |
| Art.31  | A.5.24, A.5.26 | Art.31        | SUPPORTS×2 | high, medium |
| Art.39  | A.5.2, A.5.4   | Art.39        | IMPLEMENTS + SUPPORTS | high, medium |
| Art.40  | A.5.31         | Art.40        | SUPPORTS   | medium  |
| Art.42  | A.5.36         | Art.42        | SUPPORTS   | high    |
| Art.82  | A.5.28, A.5.33 | Art.82        | SUPPORTS×2 | medium  |
| Art.87  | A.8.11         | Art.87        | IMPLEMENTS | high    |
| Art.88  | A.6.6, A.6.5   | Art.88        | SUPPORTS×2 | medium  |
| Art.89  | A.5.33, A.8.11 | Art.89        | IMPLEMENTS + SUPPORTS | high×2 |
| Art.90  | A.6.6          | Art.90        | SUPPORTS   | medium  |
| **Total** | **12 articles / 19 edges** |             |            |         |

## Dogfood verification

Arion Art.39 Evidence Package after Ship 73'.b (Art.39 chosen
because A.5.2 + A.5.4 have satisfied MUSTs on Arion — the bridges
LIGHT UP with real bridge_coverage rows):

```
# DPO Tasks Procedure — Coverage Summary
_Art.39 · GDPR · Generated 2026-08-16_

**Status:** Not yet covered — 0 of 5 required elements covered (0%).
**Related-control implementation paths asserted:** 5 of the missing
elements below have one or more asserted implementation paths via
ISO 27001:2022 controls…

- ↗ **Inform + advise the controller/processor + employees who carry
      out processing (Art.39.1.a)** (asserted implementation via
      related controls)
  _Related controls address monitoring and training._
  ↳ Asserted implementation via _ISO 27001:2022 A.5.2_ (IMPLEMENTS, confidence: HIGH)
    Rationale: Information security roles and responsibilities defines
    the DPO's operational tasks under Art.39 — advising the controller,
    monitoring compliance, cooperating with the SA. The DPO's role
    definition + reporting lines live here.
    _ISO 27001:2022 A.5.2_ posture: **NC** (2 of 15 MUSTs satisfied)
    Example evidence available on this source control: …
  ↳ Asserted implementation via _ISO 27001:2022 A.5.4_ (SUPPORTS, confidence: MEDIUM)
    Rationale: Management responsibilities ensures top management
    supports DPO independence + resource allocation for the Art.39
    tasks (monitoring, training, cooperating with SAs).
    _ISO 27001:2022 A.5.4_ posture: **NC** (2 of 16 MUSTs satisfied)
    Example evidence available on this source control: …
  _(Mapping is an ArionComply catalog assertion; auditor-defensibility
  depends on evidence specificity and mapping acceptance.)_
```

Six things work end-to-end without extra plumbing:

1. **Bridges surface at header level** — "5 of the missing elements
   have… asserted implementation paths via ISO 27001:2022 controls"
   (was 0 before).
2. **Exact curator rationale rendered** — verbatim from
   `relationship_catalog.py`.
3. **Confidence tag visible** — `HIGH` / `MEDIUM` from `role` field.
4. **Source posture attribution** — "A.5.2 posture: NC (2 of 15
   MUSTs satisfied)" tells the auditor where ISO-side work needs to
   happen too. Ship 68'.b's "asserted mapping + source progress"
   frame carries through.
5. **Dimension summary auto-computed** — "_Related controls address
   monitoring and training._" — Ship 69'.c parser extracted the
   dimensions from my rationale text automatically. New bridges
   inherit the UX.
6. **Epistemic disclaimer intact** — Ship 68'.b's honest-mapping
   frame ("catalog assertion; auditor-defensibility depends on…")
   applies uniformly.

The arc closed the visible-gap surface without any UX code changes.
That's the payoff of Ships 68' + 69' + 71' laying the SSoT correctly.

## Codified lessons

Two new + reinforced two existing.

### 46. Audit before curating — count what's there first

Ship 73'.a's classifier reduced the arc scope decisively: from
"22 articles to research + author" to "22 specific edges with
confidence signals to refine + author, 7 legitimate carve-outs,
32 out-of-scope." The 200-LOC audit script paid for itself many
times over.

### 47. Draft proposals ≠ authored bridges

Ship 73'.a produced 22 drafts with confidence signals. Ship 73'.b's
authoring pass refined the list (3 drops + 2 upgrades) before
writing anything into the catalog. The confidence signal is a
review checkpoint, not decoration.

### Reinforced: 44 (domain rules at highest layer)

The wide audit sanity-checked my initial instinct that Task #595
was the whole GDPR curation gap. It was — bridges ARE the biggest
remaining piece. But the check also revealed 2 fingerprint + 1
eval gap that we now KNOW to size for future micro-arcs, and
importantly saved us from chasing phantom guidance gaps that the
first-pass audit falsely surfaced.

### Reinforced: audit-the-audit

The wide-audit's first pass showed massive false gaps (guidance
"missing" across 44 articles; fingerprints "missing" across 44).
Both were audit-script bugs — wrong data-access pattern for
guidance (raw dataclass attribute vs lazy applier), wrong
directory for fingerprints. **The addendum codified: any audit
that claims a big surprise should get double-checked before you
build an arc around it.**

## What's parked

Micro-arcs that would round out GDPR curation:
- **Art.15 + Art.30 fingerprints** — 2 leaf-scan yaml files.
  Small enough to bundle into any next intake-adjacent arc.
- **Art.85 eval case** — freedom of expression / journalism
  processing scope. Uncommon control; low priority.

Neighbourhood arcs still open from earlier ships:
- Docx dogfood friction #1 / #3 / #4 / #5 — SDT-based placeholders,
  header/footer editability, multi-version Word testing.
- Ship 72' deterministic-path migration (consensus / critic /
  fingerprints extractors).

## Session shape

The arc followed the audit → refine → author → dogfood cadence
Ships 30-32 + 69'.a-d established. The user's "why do we keep
dropping to narrower scope?" question mid-Ship-72' made 73'.a
land as a wide audit BEFORE the specific bridge work; the wide
audit itself needed correction, teaching us to audit the audit.

Task #595 CLOSED. Framework-mapping honesty (Ship 68'.b) meets
framework-mapping completeness (Ship 73'.b).
