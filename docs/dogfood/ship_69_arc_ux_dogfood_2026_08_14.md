# Ship 69' arc UX dogfood — internal review notes

_2026-08-14. Tenant: Arion Networks (`00000000-0000-0000-0000-000000000001`). Surface: Evidence Package renderer (`build_evidence_package`)._

Rough notes for internal product review. Captures actual EP output on 4 sample leaves that exercise the Ship 69'.a→d changes: sub-clause retargets, new stub attribution, dimension summaries, whole-to-whole fallback. What worked, what feels off.

---

## What Ship 69' changed (visible to a tenant)

Every ↗ block on the Evidence Package now shows three things it didn't before Ship 68'.b:

1. **Rationale** — the curator's specific sentence for why this control was asserted to implement the target
2. **Source posture** — the source control's own progress (`NC · 20 of 30 MUSTs satisfied`)
3. **Dimension summary** (Ship 69'.c) — a single italic sentence per ↗ block: *"Related controls address confidentiality, integrity, and access management."*

The retargets from 69'.b + 69'.d don't change what the tenant reads at the top of the page — they change WHAT rationale the auditor sees on each ↗ line. `A.5.18 → Art.32.1.b` rationale now says *"Access rights management implements Art.32.1.b ongoing confidentiality of processing systems"* — narrower + more auditor-testable than the pre-arc whole-article version.

---

## Sample 1 — `req:Art.32:program_review` (RETARGETED SUB-CLAUSES)

Status: `Partially covered — 1 of 5 required elements covered (20%)`.

Header:
```
**Related-control implementation paths asserted:** 4 of the missing elements
below have one or more asserted implementation paths via ISO 27001:2022,
ISO 27701:2019 controls (per ArionComply mapping catalog; see the ↗ blocks
below). Auditor-defensibility depends on the specific evidence and mapping
acceptance.
```

First ↗ block:
```
- ↗ **Review date within the planned interval** (asserted implementation via related controls)
  _Related controls address access management, confidentiality, availability, and incident response._
  ↳ Asserted implementation via _ISO 27001:2022 A.6.3_ (IMPLEMENTS, confidence: HIGH)
    Rationale: Information security awareness, education and training ensures
    staff processing personal data understand their obligations.
    _ISO 27001:2022 A.6.3_ posture: **OFI** (22 of 23 MUSTs satisfied)
    Example evidence available on this source control: ...
  ↳ Asserted implementation via _ISO 27001:2022 A.5.18_ (IMPLEMENTS, confidence: HIGH)
    Rationale: Access rights management implements Art.32.1.b ongoing
    confidentiality of processing systems.
    _ISO 27001:2022 A.5.18_ posture: **NC** (20 of 30 MUSTs satisfied)
    Example evidence available on this source control: ...
  ↳ Asserted implementation via _ISO 27001:2022 6.1.2_ (IMPLEMENTS, confidence: HIGH)
    Rationale: Information security risk assessment is the direct
    implementation of Art.32(2)'s requirement to assess risks to rights
    and freedoms when determining appropriate security measures.
    _ISO 27001:2022 6.1.2_ posture: **OFI** (18 of 23 MUSTs satisfied)
  ↳ …and 10 more asserted mappings.
```

**Works:**
- The A.5.18 rationale surfaces `Art.32.1.b` — the sub-clause retarget from Ship 69'.b is visible. Auditor reads a narrower claim than pre-arc.
- Dimension summary is honest: the group's rationales genuinely name access management + confidentiality + availability + incident response. Line is short + scannable.
- Source posture line does real work — the tenant sees A.5.18 is `NC (20/30)` while A.6.3 is `OFI (22/23)`. Nothing pretends coverage is transferred.

**Rough:**
- `…and 10 more asserted mappings` is a black hole. 13 total sources, 3 shown, 10 hidden. In markdown there's no click-to-expand. Auditor asks *"which 10?"* — the EP has no answer.
- 4 asserted paths for A.6.3 (training) → Art.32:program_review feels like a stretch. The rationale reads plausibly but training + program review isn't a natural pairing. Curator-wise: maybe the audit surfaced a false-positive edge that should be reviewed.

---

## Sample 2 — `req:Art.28:data_processing_agreement` (NEW STUB TARGETS)

Status: `Partially covered — 4 of 8 required elements covered (50%)`.

DPA confidentiality MUST — sources ranked by n_source_musts_satisfied:
```
1. A.7.2.6 → Art.28.3    IMPLEMENTS  n=14
2. A.5.19  → Art.28      IMPLEMENTS  n=9
3. A.5.20  → Art.28      IMPLEMENTS  n=8
4. B.8.2.1 → Art.28.3.f  IMPLEMENTS  n=7
5. B.8.3.1 → Art.28.3.e  IMPLEMENTS  n=6   ← Ship 69'.d new stub
6. B.8.4.2 → Art.28.3.g  IMPLEMENTS  n=4
7. B.8.5.4 → Art.28.3.a  IMPLEMENTS  n=4
...
12. B.8.5.8 → Art.28.2   IMPLEMENTS  n=1   ← Ship 69'.d new stub
13. B.8.5.6 → Art.28.2   IMPLEMENTS  n=1   ← Ship 69'.d new stub
14. B.8.5.7 → Art.28.2   IMPLEMENTS  n=1   ← Ship 69'.d new stub
```

Rendered ↗ block shows top 3 only:
```
- ↗ **Confidentiality obligations on processor staff** (asserted implementation via related controls)
  _Related controls address processor obligations, monitoring, and access management._
  ↳ Asserted implementation via _ISO 27701:2019 A.7.2.6_ (IMPLEMENTS, confidence: HIGH)
    Rationale: 27701 A.7.2.6 is the certifiable operationalisation of GDPR Art.28
    processor — mandatory Art.28.3 contract terms + Art.28.9 written form.
  ↳ Asserted implementation via _ISO 27001:2022 A.5.19_ (IMPLEMENTS)
  ↳ Asserted implementation via _ISO 27001:2022 A.5.20_ (IMPLEMENTS)
  ↳ …and 12 more asserted mappings.
```

**Works:**
- `processor obligations` in the dimension summary is exactly the right characterization for this MUST.
- A.7.2.6's rationale explicitly names Art.28.3 + Art.28.9 — the auditor can trace the mapping specificity.

**Rough:**
- **The Ship 69'.d retargets are buried.** B.8.3.1 → Art.28.3.e (a Ship 69'.d retarget that names the *narrower* sub-clause the curator intended) sits at position 5 — inside the "12 more" bucket. The whole-to-whole edges (A.7.2.6 → Art.28.3, A.5.19 → Art.28) rank higher because they carry more satisfied source MUSTs. **This is a real ranking bug**: the arc's precision work is hidden behind the arc's coarser predecessors.
- Auditor question: *"Show me the sub-clause-specific mappings first."* — no way to sort or filter by target granularity in the current display.

**Ship-69'-follow-on candidate:** Rank sources by target granularity (sub-clause > whole-article) with n_source_musts as a tiebreaker. Would surface the 69'.b/d work at the top of the ↗ block.

---

## Sample 3 — `req:Art.6:lawful_basis_register` (WHOLE-TO-WHOLE + DIMENSION)

Status: `Partially covered`.

First ↗ block:
```
- ↗ **Chosen lawful basis named per activity (one of Art.6.1.a-f)** (asserted implementation via related controls)
  _Related controls address lawfulness, pseudonymisation, and risk assessment._
  ↳ Asserted implementation via _ISO 27001:2022 6.1.2_ (GOVERNANCE, confidence: HIGH)
    Rationale: Risk assessment must consider lawfulness risks — processing without
    a legal basis is a high-probability, high-impact risk.
    _ISO 27001:2022 6.1.2_ posture: **OFI** (18 of 23 MUSTs satisfied)
  ↳ Asserted implementation via _ISO 27001:2022 A.5.31_ (IMPLEMENTS, confidence: HIGH)
    Rationale: Legal requirements control is the direct ISO mechanism for
    identifying and documenting the lawful basis for each processing activity —
    a mandatory GDPR requirement.
    _ISO 27001:2022 A.5.31_ posture: **NC** (9 of 23 MUSTs satisfied)
  ↳ Asserted implementation via _ISO 27701:2019 A.7.2.2_ (IMPLEMENTS, confidence: HIGH)
    Rationale: 27701 A.7.2.2 is the certifiable operationalisation of GDPR Art.6
    lawfulness of processing — determining + documenting the Art.6.1.a-f basis
    per activity.
```

**Works:**
- Dimension summary `lawfulness, pseudonymisation, and risk assessment` reads honestly. A.5.31 + A.7.2.2 both cite lawfulness; 6.1.2 cites risk assessment. Aggregated correctly.
- Rationale on 6.1.2 (GOVERNANCE edge) has different framing from the IMPLEMENTS edges — auditor sees the governance layer separately.

**Rough:**
- **`pseudonymisation` in the dimension summary is a stretch.** No rationale in the top-3 mentions it. Probably comes from a hidden source (the 4th-N block) that mentions `de-identification` (Ship 69'.c collapses `de-identification` → `pseudonymisation`). Summary aggregates from ALL sources' rationales, not just the displayed 3 — so tokens from hidden sources leak into the label. Not wrong per se, but reader may wonder *"where does pseudonymisation appear?"* and can't find it.
- Consider: only aggregate dimensions from the displayed source rationales. Or add a hover / footnote clarifying that dimensions cover the full set.

---

## Sample 4 — `req:A.5.15:management_approval` (FULLY-SATISFIED)

Status: `Fully covered — 3 of 3 required elements covered (100%)`.

No ↗ blocks. Every required element renders as `✓` with a verbatim excerpt. No cross-framework header, no dimension summary. **Ship 69' correctly does nothing here.**

**Works:**
- Fully-satisfied leaves render clean. No noise from the arc's additions.
- Snapshot test locks this behavior (`test_fully_satisfied_leaf_renders_no_bridge_header`).

---

## Cross-cutting observations

### Wins

- **Rationale-first framing** (Ship 68'.b) does most of the work. The dimension summary is a nice add-on but the auditor gets 80% of the value just from reading the curator's rationale line by line.
- **Source posture inline** ("A.5.18 posture: NC (20 of 30 MUSTs satisfied)") is auditor-critical context. Without it the ↗ block would feel like a claim; with it, it's grounded.
- **Idempotent tooling**. Re-running the retarget script + audit produces the "arc is done" signal (`retargetable_now=0`). Future curator edits to rationales can be checked with the same audit script.
- **Vocabulary hygiene** in Ship 69'.c. `access control`/`access rights`/`authorisation` all collapse to *access management*. Curator variants don't leak.

### Friction

1. **The top-3 rendering hides sub-clause precision.** Ship 69'.b/d moved 63 edges to narrower targets, but the reader ranks by `n_source_musts_satisfied` which favors coarser whole-article edges. Sub-clause work is often buried in "…and N more asserted mappings." → **Follow-on: rank by target granularity, then by satisfaction count.**

2. **`…and N more asserted mappings` is a black hole.** No way to see which N. Auditor's next question ("show me all of them") isn't answerable in the EP surface. → **Follow-on: EP expansion + JSON API for a full list.**

3. **Dimension summary can leak tokens from hidden sources.** Sample 3 (Art.6) mentions pseudonymisation via a de-identification token in a source that isn't rendered. The label describes the FULL set of asserted paths, not just the displayed top-3. → **Follow-on: either aggregate only from displayed sources, or footnote the label to clarify scope.**

4. **False-positive-feeling edges surface**. Sample 1 shows A.6.3 training → Art.32:program_review with high confidence. Reads plausible in isolation but the pairing is a stretch. → **Follow-on: manual curator review of edges where rationale mentions a dimension the source control doesn't obviously carry.**

5. **No filter / sort in the EP output.** All the friction above lands here. The EP is a static markdown snapshot; a proper HTML/SPA renderer with filters would let auditors sort by target granularity, confidence, source standard. → **Follow-on: EP-as-service with filterable JSON payload behind an HTML surface.**

### Overall

**Ship 69' delivered honest precision that the current renderer partially hides.** The retargets are correct; the rationales are more auditor-testable than pre-arc. But the display ranker was tuned for the pre-arc topology (rank by satisfied source MUSTs = favor coarser edges) and now hides the arc's precision work behind its predecessors. That's the biggest single follow-on: teach the display to prefer the narrower attributions the arc produced.

The dimension summary (Ship 69'.c) is a low-cost win that adds real scannability, but the token-leak-from-hidden-sources issue should be fixed before it's advertised as a filter mechanism.

### Suggested next arcs

- **Ship 70'-ish (Renderer ranking rework)**: sort ↗ sources by (target granularity, confidence, source progress) instead of just n_source_musts. Small — 20 LOC change in `evidence_package.py`.
- **Ship 71'-ish (EP JSON API + expandable UX)**: replace `…and N more` with a proper expansion pattern. Requires SPA work + API endpoint.
- **Task #595** — 22 unbridged GDPR articles, unchanged.
