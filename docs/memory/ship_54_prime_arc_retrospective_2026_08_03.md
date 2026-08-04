---
name: ship-54-prime-arc-retrospective-2026-08-03
description: "Ship 54' arc retrospective — templating + advisory framework extension. 18 sub-arcs across 2026-08-02→08-04 delivered: topics data layer (17 curated bundles, 185 leaf-refs across Program/Extension/Obligation mesh), advisory API + SPA Topics view + leaf-scoped drill-in with per-leaf state chip, chat topic-bundle intent routing + trigger-verb tightening addendum, doc-control renderer block, 3-phase structural evidence intake round-trip (detector library + standalone lane + consensus signal fusion), root-cause fixes on eval FAILs #222 (Signal C ref lock in gatekeeper) + #205 (applicability CLEAR_INTENT gap), and 4-iteration atlas/playbook border sharpening (Dashboard = compliance ATLAS, Topics = compliance PLAYBOOK, explicit cross-nav pills + escape hatch). Round-trip binding + dual-role structural fusion codified as IP-worthy elements per operator note. 11 codified lessons captured. Eval baseline post-arc: 231/232 PASS 0 FAIL 1 WARN (only pre-existing #200 documented unrelated to LLM behavior)."
metadata:
  node_type: memory
  type: project
---

Ship 54' arc retrospective — templating + advisory framework
extension. 12 sub-arcs across 2 days (2026-08-02 → 2026-08-03).
Direct follow-on from Ship 53' consultant-grade grounding arc;
this arc extends the advisory framework with workflow-oriented
topic bundles + closes the doc-control round-trip between renderer
output and extractor input.

## What triggered it

Ship 53' had shipped consultant-grade grounding — remediation
answers now cite EDPB Guidelines / ISO 27002 / ISO 27701 by
document number. The operator then provided
`/data/arioncomply/private/Share.zip` — a 324-file consultant
toolkit library (Defradar GDPR templates + ISO 27001 Options 1
+ 2) — and asked:

> *"read through and lets revisit our templating, advisory
> discipline, i want to have formally formed templates both doc
> and xls with maximum clarity and to glean what we can improve
> in our overal advisory framework"*

The Share.zip analysis surfaced two structural gaps in our
existing 845 per-leaf templates + advisory:

1. **No workflow bundling.** Real compliance work happens at
   topic level (DSR management, incident response, consent
   lifecycle) — a policy + procedure + form + register + review
   grouped by workflow. Our advisory surfaced per-leaf; a topic
   view was missing.

2. **No doc-control shape in output/input.** Share references
   carried consultant-toolkit convention (Doc No / Rev / Prepared
   / Reviewed / Approved header + Revision History table). Our
   renderer emitted markdown scaffolds without those blocks;
   our extractor didn't recognize them when tenants uploaded
   docs that had them.

The operator constraint was explicit:

> *"i think i dont understand what the drill in is doing"*
> *"the topics drilldown needs cleaning"*
> *"correct me if im wrong"*

And on scope:

> *"i dont want to wonder too far from where we are, i want A + B
> preserving per-leaf and bringing in topical as an addition"*

Additive scope. Preserve the 845 per-leaf templates untouched.
Bring in the workflow layer + doc-control shape as pure overlay.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 54'.a | Topics data model + 12 curated bundles + `topics` / `topic_leaves` schema (schema_v91) | `63f0cf2` |
| 54'.a addendum 1 | ISO 27701 mesh coverage — added 12 extension refs across 5 privacy-heavy topics; closed the "obligation without programs" gap in dpia_workflow + records_of_processing | `cb82a4e` |
| 54'.a addendum 2 | 5 new 27701-anchored topics (consent, privacy notice, PII lifecycle, transfers, processor operations) + 4 small folds. 12 topics → 17 topics; 100 → 185 leaf-refs | `0aa5d65` |
| 54'.b | Advisory API (list + detail) + SPA Topics view with grid + detail; deep-linked to dashboard drill-in | `c44e2aa` |
| 54'.b addendum 1 | Inline drill-in in the topics view + text scrub (strip `[Bridge:…]` / `[leaf-scan back-bind]` / markdown escapes) | `14baf08` |
| 54'.b addendum 2 | Leaf-scoped MUST checklist + per-leaf detail endpoint. Replaced dashboard-style noise with clean 5-section shape: role_note / status / MUST checklist / remediation / actions | `5791f49` |
| 54'.b addendum 3 | Per-leaf state chip (Complete/In progress/Not started) alongside parent control finding. Resolves the "A.5.34 leaf shows 8/8 but parent NC" UX confusion | `7da35e9` |
| 54'.c | Chat topic-bundle intent routing — new `QuestionType.TOPIC_BUNDLE` + `rag/topic_matcher.py` + pre-consensus intercept + deterministic short-circuit response | `71b3b4b` |
| 54'.c addendum | Tighten topic-matcher trigger verbs — remove `implement` + bare `do` from the trigger-verb set (per-control verbs, not workflow-scope). Caught by eval case #20 over-routing to `topic_bundle` when the case expects `implementation` | `226ecef` |
| 54' post-eval fix | Root-cause fixes for eval cases #222 (Signal C's refs cleared by LLM gatekeeper) + #205 (CLEAR_INTENT gap on "is X applicable?"). Neither was stochastic — both were traceable via `chat_consensus_log.disagreement_notes` + `chat_casefile_log.question_type` | `1155fbd` |
| 54' cross-nav 1 | Dashboard ↔ Topics cross-nav pills. New endpoint `GET /api/v1/dashboard/control/{ref}/topics`; "Part of N compliance topics" panel in Dashboard drill-in; sharpened "Open X in Dashboard" label on Topics leaf escape hatch | `4fb3f7d` |
| 54' border 1 | Complete Option A — drop Evidence-classes panel + "How to strengthen X" advisory from Dashboard drill-in (over-shoot; removed too much including the sources list) | `efb5652` |
| 54' border 2 | Restore gap-text box for leaf-only controls where slim verdict tree returned empty (under-shoot fix — Gap description heading was appearing with empty content) | `7052792` |
| 54' border 3 | Restore evidence-classes panel in `atlasMode: true` — keeps yield stats + per-leaf sources list (auditor-forensic); suppresses template CTA + Evidence Package + Cite external source buttons (self-service, Topics job) | `11630e8` |
| 54'.d | Doc-control renderer block — `<<DOC_CONTROL>>` + `<<REVISION_HISTORY>>` markers → DOCX tables with Doc No / Rev / Prepared / Reviewed / Approved + revision history seed | `cde5190` |
| 54'.e Phase 1 | Structural evidence detector library — 5 pattern detectors + 13 unit tests + mammoth-normalization for docx-extracted markdown | `2b0d7e5` |
| 54'.e Phase 2 | Intake wiring — schema_v92 adds `structural_pattern` inference_source + `structural` grounding_method; new binding logic emits document_findings for detected patterns with per-MUST bindings + provenance-preserving excerpts | `bc139eb` |
| 54'.e Phase 3 | `structural_maturity` consensus signal — 10th signal in the extraction consensus pass; doc-level boost (weight 0.15) scales with pattern-count (40%→100%); closes the dual-role hybrid design | `f3513e4` |

Total: 4 sub-arcs (a/b/c/d/e) with 8 addenda/phases = 12 commits
of substantive delivery.

## Sub-arc details

### 54'.a — Topics as a curated data layer

The additive-overlay design was locked before writing any code
after operator confirmed *"preserve per-leaf and bring in topical
as an addition"*. Three artefacts:

- **schema_v91_ship54a_topics.sql** — two tables:
  - `topics` (slug PK, title, description, primary_framework,
    auditor_expects, display_order, source_file)
  - `topic_leaves` (topic_slug + leaf_id composite PK, role,
    workflow_order, role_note)
  - No FK from `topic_leaves.leaf_id` to `templates.leaf_id`
    because topics can reference not-yet-templated leaves; loader
    validates against `ALL_EVIDENCE_REQUIREMENTS ∪
    ALL_DERIVED_SPECS.direct_evidence` canonical catalog union.

- **12 initial topic YAMLs** in `db/topics/*.yaml` covering DSR,
  incident response, breach notification, risk assessment,
  DPIA, supplier onboarding, employee lifecycle, business
  continuity, access rights, RoPA, change management, continual
  improvement.

- **Loader** — `enrichment/topics/load_to_postgres.py` mirrors the
  templates loader shape (dry-run mode, fail-fast validation,
  orphan sweep).

**Operator audit surfaced the 27701 gap** (post-shipment).
Original 12 topics had 100 leaf-references with **ZERO** ISO
27701 extensions — every primary_framework was `GDPR`,
`ISO27001`, or `multi`, none `ISO27701`. The operator caught it:

> *"how did we do with our models Program → Extension →
> Obligation? what about 27701, it feels like the lost child in
> this shipment"*

Two-step remediation:
1. **Addendum 1** — enriched 5 privacy-heavy topics (DSR, DPIA,
   supplier, RoPA, breach) with ISO 27701 mirrors. Also fixed
   two topics with zero programs backing their obligations —
   obligation-without-program is theatre, not compliance.
2. **Addendum 2** — added 5 new 27701-anchored topics: consent
   lifecycle, privacy notice transparency, PII lifecycle,
   data transfers/disclosures, processor operations. Also small
   folds into existing topics (A.7.3.9 to DSR, A.7.2.6+7 to
   supplier, A.7.3.10 + Art.22 to DPIA, A.7.2.8 to RoPA).

Framework-role coverage progression:

| Point | Topics | 27701 ext | GDPR obl | Programs | Total refs |
|---|---|---|---|---|---|
| Ship 54'.a original | 12 | 0 | 23 | 77 | 100 |
| Addendum 1 | 12 | 12 | 23 | 79 | 114 |
| Addendum 2 | **17** | **60** | **40** | **85** | **185** |

Every 27701-anchored topic carries the full Program → Extension
→ Obligation mesh — no purely-27701 theatre.

### 54'.b — Consumer surfaces (with three UX iterations)

Two new API endpoints:
- `GET /api/v1/advisory/topics` — list + per-topic verdict
  roll-up + framework-role composition (LEFT JOIN topic_leaves
  ⋈ posture_controls with tenant RLS)
- `GET /api/v1/advisory/topics/{slug}` — bundle detail with
  per-leaf status ordered by `workflow_order`

New SPA "Topics" mode with landing grid + detail view. Initially
clicking a leaf redirected to the dashboard drill-in.

**Iteration 1** (operator: *"the topics drilldown needs cleaning
and we probably need to put it on the topics side bar not the
dashboard because it is different from the dashboard drilldown"*):

- Removed dashboard redirect; added inline expansion in the
  topics view
- Added `_scrub_topic_gap_text()` — strips `[Bridge: ...]`,
  `[leaf-scan back-bind ...]`, `\-`/`\.` markdown escapes

**Iteration 2** (operator: *"i thought it would be per leaf status
and remediation like the dashboard"*):

- Rewrote inline drill-in as a lazy-fetched 5-section shape:
  role_note / status / MUST checklist / remediation / actions
- New endpoint `GET /api/v1/advisory/leaf/{leaf_id:path}/detail`
  reuses `build_per_must_advisory_data` filtered to the specific
  leaf, JOINs with `document_findings` for source names
- Confidence weights (high/medium/low) dropped per operator note
  — Stage-1 review concern, not workflow-drill-in concern

**Iteration 3** (operator: *"add the leaf-level state chip"*):

- Added per-leaf state chip (Complete/In progress/Not started/
  No MUSTs) alongside the parent control finding pill
- Derived from MUST-completion ratio via
  `_leaf_must_ids()` cache + one extra bulk query
- Resolves the "A.5.34 8/8 present but parent NC" ambiguity
  the operator surfaced during testing

### 54'.c — Chat topic-bundle routing

`QuestionType.TOPIC_BUNDLE` = "topic_bundle" added to the enum.
`rag/topic_matcher.py` — curator-authored keyword→slug map for
all 17 topics + trigger-verb detector
(`how do I set up / walk me through / what's involved in ...`).
Both trigger AND topic keyword required to route.

**Pre-consensus intercept** turned out to be necessary. First
implementation added topic detection to `classifier._check_
explicit`, which is downstream of the consensus layer. Consensus
was resolving "how do I set up DSR?" to `implementation` type
with high confidence and skipping the LLM classifier entirely.
Fix: add topic detection BEFORE `run_consensus()` fires.

Response is deterministic — no LLM call:
- `_build_topic_bundle_answer` in `arion_graph.py` loads the
  bundle from Postgres + composes the answer text
- Verdict roll-up + ordered workflow list + deep-link prompt to
  Topics tab

Verified across 4 topic queries (DSR, incident response, consent,
supplier). Regression clean on non-topic queries (`how do I
remediate A.5.15?` still routes to Ship 53' consultant answer).

**Addendum — trigger-verb tightening** (post-Ship-54' eval rerun
surfaced case #20 over-routing):

The initial trigger regex included `implement` alongside genuine
workflow verbs (set up / walk me through / manage / etc.). Eval
case #20 ("how do we implement a formal access rights review?")
routed to `topic_bundle` (access_rights_lifecycle) when the case
expects `implementation` — the query is asking about a specific
compliance activity within a bundle, not the whole bundle.

Root cause: `implement` is a per-control verb — natural phrasing
is "how do I implement A.5.15?" — while `set up / walk me through`
are inherently workflow-scope. Both patterns felt "how do I
approach X" on the surface but carry different scope.

Fix — remove `implement` + bare `do` from the trigger set. Final
alternatives: `set up / set-up / handle / run / manage / approach`
+ `walk me through / what's involved in / tell me about / guide
me through / help me with / show me the workflow for`. All
inherently workflow-scope, none per-control.

Verified — 6 positive cases still route (DSR/incident/consent/
supplier/breach/DPIA); #20 re-run PASS; regression check clean
on `how do I remediate A.5.15?` and `what are our NC findings?`.

### 54'.d — Renderer half of the doc-control round-trip

`docx_renderer.py` gained two opt-in markers:

- `<<DOC_CONTROL>>` — 2-column table with Doc No / Revision /
  Revision Date / Prepared By / Reviewed By / Approved By
  (approval rows have wet-sign underscore placeholders —
  deliberate; tenant fills at doc-control review)

- `<<REVISION_HISTORY>>` — 4-column table (Version / Date /
  Description of Change / Author) seeded with the current
  template_version + today

**Doc No derivation** — `_derive_doc_number(leaf_id,
template_version)` maps leaf_type keyword to a convention prefix:
`policy → POL`, `procedure → PRC`, `register → REG`,
`record`/`log` → `REC`, etc. Deterministic + curator-overridable.

Pilot on `req:5.2:information_security_policy` — top-of-stack
ISMS policy, canonical controlled document. All 11 expected
labels present in the rendered DOCX; doc number renders as
`POL-5.2-Rev03` at template_version=3.

### 54'.e — Intake round-trip closure (3 phases)

**Phase 1 — Detector library** (`rag/intake/structural_
evidence.py`):

5 pattern detectors matched to compliance evidence each proves:

  | Detector | Proves |
  |---|---|
  | `detect_doc_control_header` | Formal doc control + named owner + approval |
  | `detect_revision_history` | Continual improvement via versioned control |
  | `detect_signature_blocks` | Approval discipline |
  | `detect_interested_parties` | ISO 27001 clause 4.2 stakeholders |
  | `detect_table_of_contents` | Document-maturity signal |

Handles two input shapes:
- Prose (`Label: value` on same line — consultant reference docs)
- Mammoth docx table shape (`__Label__` \n `value` — each cell
  on its own line)

`_normalize_mammoth_output()` strips markdown-escape artifacts
(`\-`, `\.`, `\_`, `\(`, `\)`, `\/`) before pattern matching so
detectors work uniformly on both shapes.

13 unit tests covering: same-line prose (6/6 fields), mammoth
two-line, below-threshold guard, revision-history inline table +
docx one-cell-per-line table, interested parties bullet list,
TOC with page numbers, full consultant shape, casual note
negative test.

**Design conversation at Phase 1↔2 handoff** (operator note):

> *"we need to agree on how these additions get absorved/strengthen
> existing signals or constitute new signals. remember the quality
> of our intake is a diferentiator and if it turns out that we
> have come up with a solid intake mechanism, it is a possible
> patent"*

Three integration shapes considered:
- **A**: New inference_source lane only
- **B**: New consensus signal only (boost, no direct evidence)
- **C**: Hybrid — dual-role (self-standing evidence AND signal)

Operator picked C. Phase 2 delivers the self-standing lane;
Phase 3 delivers the signal fusion.

**Phase 2 — Standalone inference_source lane**:

Schema_v92 adds `structural_pattern` to
`document_findings.inference_source` CHECK constraint +
`structural` to `grounding_method` per Ship 6'.b provenance
discipline.

Binding logic in `structural_evidence_to_findings()`:

  Pattern signal → MUST slug → target leaves count
  Prepared_By populated → `:owner` → 37 leaves
  Approved_By populated → `:approved` → 2 leaves
  Signature block → `:approved` → 2 leaves
  Revision_Date populated → `:rev_date` → 198 leaves
  Revision history table → `:rev_date` + `:rev_reviewer` → 198 each
  Interested parties → `:parties_listed` → 1 leaf (4.2)

Each finding is provenance-preserving:
`Approved By: Maria Silva, CEO — structural: doc-control header
Approved By field` rather than `we detected a doc-control block`.

Verified end-to-end on our own 5.2 DOCX round-trip: mammoth
extraction + detector + finding conversion emits 3 structural
findings on the 5.2 program_review leaf. Approved/owner
correctly skipped when wet-sign placeholders present.

**Phase 3 — Consensus signal fusion**:

New signal `rag/intake/consensus_extraction/signals/structural_
maturity.py`. Reads
`doc.extraction_metrics['structural_evidence']` (Phase 2 stash)
and emits per-candidate boost proportional to pattern count.

Weight scale:
| Patterns | Scale | Boost | Corroborators |
|---|---|---|---|
| 0 | doesn't fire | — | — |
| 1 | 40% | 0.060 | +1 |
| 2 | 70% | 0.105 | +1 |
| ≥3 | 100% | 0.150 | +1 |

Weight 0.15 sits between `per_protocol_scope` (0.10 tiebreaker)
and `bm25` (0.25 lexical) — subordinate to per-candidate signals
but adds real corroboration for formal artefacts.

Added to `_POSITIVE_SIGNAL_NAMES` corroborator allowlist.
Also added `bm25_topk` while there — was missing since Ship 43'.b
(minor drive-by fix).

Verified on real 5.2 DOCX: 2 patterns detected
(doc_control + revision_history), boost=0.105, contributes +1
corroborator to every scoped candidate.

### 54' post-arc — atlas/playbook border sharpening

After the arc was declared "closed," operator surfaced two follow-
ons that turned into 5 additional commits:

**Root-cause fixes on eval FAILs (`1155fbd`)**

Ship 54' initial eval rerun showed 229/232 with 1 FAIL (#222)
and 2 WARNs. Operator pushed back on the retro's optimistic
"stochastic" framing:

> *"we should not have any stochastic cases please investigate
> the cases"*

Correct — CLAUDE.md's codified rule is *"LLM-stochastic is not an
acceptable category — it usually hides a real infra defect."*
Diagnostic paths landed both fixes in one commit:

- **#222** — `chat_consensus_log.disagreement_notes` showed the
  LLM gatekeeper's reasoning: *"clear refs as none are from ISO
  27005."* Signal C emitted 6.1.2 at curator-tier weight 1.00
  (via DOCUMENT_TOPIC_MAP "risk assessment" → 6.1.2), but the
  gatekeeper cleared it because 6.1.2 is an ISO 27001 ref and
  the query mentioned ISO 27005. The LLM didn't understand that
  6.1.2 IS the ISMS clause that ISO 27005 provides guidance for.

  Fix: `_signals_lock_refs()` helper + wire into
  `_apply_decision`. Mirrors the existing question_type + framework
  locks. Deterministic-signal refs (Signal B explicit + Signal C
  curated) cannot be dropped by the arbiter — only augmented.

- **#205** — `chat_casefile_log.question_type = 'unknown'`.
  Scanned CLEAR_INTENT_PHRASES — no pattern for "is X applicable?"
  / "does X apply to us?" / "are we in scope for X?" Applicability
  interrogatives fell through to the LLM classifier which returned
  `unknown`.

  Fix: three new CLEAR_INTENT_PHRASES patterns + extended the
  27701 direct-ref pattern to accept "applicable" / "in scope"
  alongside existing verdict words.

Full rerun post-fix: 231/232 PASS, 0 FAIL, 1 WARN (only #200
pre-existing). Back to the pre-Ship-54' baseline.

**Atlas/Playbook border sharpening (4 iterations)**

Operator raised the design concern:

> *"we developed topics and created a topics page and a leaf drill
> in it feels to me that there is a collition between the topics
> page and the dashboard, can we start by distinguishing what
> each represents and investigate whether we can have both on a
> single page."*

Design conclusion: keep both surfaces, sharpen borders + explicit
cross-nav. Dashboard = compliance ATLAS (auditor lens). Topics =
compliance PLAYBOOK (DPO lens). But executing the border took
four iterations because "drop the advisory panel" turned out to
be more nuanced than the initial option-picking suggested:

1. **`4fb3f7d` cross-nav pills** — added Dashboard→Topics pills
   ("Part of N compliance topics") + sharpened Topics→Dashboard
   escape hatch label. Both surfaces gain explicit awareness of
   the other lens. But didn't remove any overlapping content —
   operator surfaced that as under-delivery on Option A.

2. **`efb5652` over-removal** — dropped both the Evidence-classes
   panel (yield stats + per-leaf sources) AND the "How to
   strengthen X" advisory. Operator paste confirmed the drill-in
   became too thin: standard text · finding · gap · pills · ask
   button. Missing: **which docs cite this control?** — that's
   audit-forensic content, not workflow content.

3. **`7052792` gap-text restore** — for leaf-only controls where
   the slim verdict tree returns empty AND there's no advisory
   panel to catch, "Gap description" heading rendered with
   nothing beneath. Added `_gapBox()` helper that ALWAYS renders
   gap-prose (or "(no gap text recorded)" fallback).

4. **`11630e8` evidence-classes atlas mode** — restored the
   Evidence-classes panel with new `opts.atlasMode` parameter.
   Keeps yield stats + per-leaf sources list (audit forensics);
   suppresses template CTA + Evidence Package + Cite external
   source buttons (self-service, Topics-owned). Correct border.

Final border, per audit vs. author lens:

| Content | Home |
|---|---|
| Which docs cite each leaf (sources list) | **Dashboard** |
| Per-leaf coverage stats + yield percentages | **Dashboard** |
| Cross-framework mesh (demonstrated-by) | **Dashboard** |
| Cascade pressure | **Dashboard** |
| Template downloads (MD/Word/Excel) | **Topics** |
| Evidence Package export | **Topics** |
| Cite external source workflow | **Topics** |
| "How to strengthen X" per-MUST advisory prose | **Topics** |
| Ask AI CTA | **Topics** + Chat |
| Cross-nav pills / escape hatch | Both |

## Codified lessons

### 1. Additive-overlay scoping is the safer default

Operator constraint *"preserve per-leaf and bring in topical as
an addition"* pinned the arc. Topics data model uses a many-to-
many overlay (`topic_leaves`) — leaves know nothing about topics;
topics reference leaves. No changes to the 845 per-leaf templates
across the whole arc.

Result: same tenant can use per-leaf drill-in (dashboard) AND
workflow-oriented view (topics) without conflict. Existing eval
suite unchanged. Zero migration on per-leaf work.

**Rule**: when extending a mature system, ask if the new shape
can be a pure overlay first. Overlays preserve the working
substrate + reduce blast radius. Reserve invasive refactors for
cases where overlay costs are demonstrably higher.

### 2. Framework role model must be audited before claiming coverage

Ship 54'.a original had 12 topics → **0 ISO 27701 extensions**
across 100 leaf-refs. Purely GDPR obligations + ISO 27001 programs.
Missing the whole extension layer.

The gap was invisible until the operator asked *"27701 feels
like the lost child"*. The initial coverage audit
(programs/extensions/obligations count per topic) was the
right diagnostic — and it surfaced two problems: no 27701
extensions AND two topics (dpia_workflow, records_of_processing)
that were obligation-only without program backing.

**Rule**: when curating a taxonomy that spans a framework role
model, audit coverage by role before shipping. A topic that
carries an obligation without a program backing it is theatre.
Same for extension coverage — if the framework has a role, at
least some topics should carry that role.

### 3. Consensus intercepts trump downstream short-circuits

Ship 54'.c initial implementation added topic-bundle detection
to `classifier._check_explicit` — a downstream helper. Live
test showed the query still routed to `implementation` type.

Root cause: `arion_graph.py::make_classify_node` runs
`run_consensus()` first (Ship 2'.o retired the legacy classifier
fallback). Consensus resolved "how do I set up DSR?" to
`implementation` with high confidence (the trigger verb was
enough to lock the type) and returned early.

Fix: add topic detection BEFORE `run_consensus()` fires, not
after. Same pattern as document_inventory intercepts.

**Rule**: consensus runs first. If a stronger classifier resolves
confidently to intent X, no downstream short-circuit for intent
Y will fire. Add new intent detection at the same layer as
consensus (or explicitly before it), not below.

### 4. Operator UX feedback catches things automated tests can't

54'.b required THREE addendums after initial ship, all from
operator feedback:
- Addendum 1: "the topics drilldown needs cleaning"
- Addendum 2: "i thought it would be per leaf status and
  remediation like the dashboard"
- Addendum 3: "add the leaf-level state chip"

Each was a distinct UX concern. None would have been caught
by test-suite alone — they required someone driving the surface
and asking "does this read right?" Test suite catches shape
regressions; operator eyes catch communication gaps.

**Rule**: build with live operator review in the loop. Ship a
first iteration + solicit feedback + iterate. The alternative
is over-engineering the first shot based on assumptions.

### 5. Round-trip binding discipline is IP-worthy (per operator)

Ship 54'.d emits `<<DOC_CONTROL>>` shape in generated DOCX.
Ship 54'.e recognizes the same shape when tenants upload docs.
Output schema = input schema. Templates become self-documenting:
what we emit IS what we recognize.

Consultant-toolkit norms (Doc No / Rev / Prepared / Reviewed /
Approved header, revision-history table, interested-parties
enumeration) are treated as first-class compliance evidence —
not just "boilerplate to preserve in Word." Each detected
pattern binds to a specific MUST with a specific excerpt.

**Rule to codify** (per operator's *"possible patent"* note):
when input and output shapes match by design, the audit trail
travels with the document. This is genuinely differentiated
from most compliance-intake tools that treat structural elements
as noise to skip.

### 6. Dual-role signal fusion — direct evidence AND corroborator

Ship 54'.e explicitly chose the hybrid design (Option C) over
"just a lane" (Option A) or "just a signal boost" (Option B).

Structural patterns act on both axes from the SAME detection
pass:
- **Direct evidence** (Phase 2): Prepared_By populated →
  `item:*:owner` binding with excerpt "Prepared By: Jane Doe"
- **Signal boost** (Phase 3): doc-level structural presence →
  +0.06 to +0.15 corroboration on every content-based candidate
  in the same doc

Most intake systems treat these as separate concerns —
structural extractors vs. NLP extractors vs. content classifiers.
The dual-role design lets one detection pass fuel multiple
downstream consumers.

**Rule**: when a signal has both intrinsic value AND extrinsic
context, don't force a choice. Design for both roles from the
detection pass onward.

### 7. Signal weight tuning is contextual — subordinate vs. sovereign

`structural_maturity_weight = 0.15` sits deliberately between
`per_protocol_scope` (0.10) and `bm25` (0.25). Not competing
with per-candidate signals like `fingerprint_keyword` (0.50) or
`doc_mappings_target` (0.60).

Rationale: structural presence is document-level context, not
per-MUST evidence. It SHOULDN'T overpower content-based matches
on specific requirements. It should tilt borderline cases and
add corroboration where the doc IS a formal artefact.

**Rule**: signal weight belongs in a tier hierarchy. Per-
candidate exact matches at the top (0.5-1.0). Semantic/lexical
in the middle (0.2-0.4). Document-context or tiebreakers at the
bottom (0.1-0.2). Assigning a doc-level signal a per-candidate
weight distorts the aggregator.

### 8. New intent types need trigger-verb precision

Ship 54'.c's initial trigger regex over-routed on `implement`.
"How do I implement A.5.15?" is per-control; "how do I set up
DSR management?" is per-bundle. Both use `how do I <verb>` shape
but carry different scope.

The eval baseline rerun caught this via case #20 — the trigger
regex was catching per-control queries whenever they happened to
mention a topic keyword. Fix: audit each trigger verb for its
natural scope and remove the ambiguous ones.

Final workflow-shape verbs (all inherently bundle-scope):
`set up / set-up / handle / run / manage / approach / walk me
through / what's involved in / tell me about / guide me through /
help me with / show me the workflow for`.

**Rule**: when adding a new intent type via CLEAR_INTENT_PHRASES-
style routing, audit each trigger token for how it commonly
co-occurs. Ambiguous verbs (`implement`, `do`, `handle` sometimes)
that appear naturally in BOTH per-control and per-bundle phrasing
need to be tested against the eval suite before shipping. New
intents pass through the whole normal-query surface + risk over-
routing on shared vocabulary.

### 9. "LLM-stochastic" is never an acceptable diagnosis

Post-Ship-54' eval showed 1 FAIL (#222) and 2 WARNs (#200,
#205). The retro's initial framing hedged #222 as "stochastic
under long-session context accumulation." Operator correctly
pushed back — CLAUDE.md's codified rule is:

> *"'LLM-stochastic' is not an acceptable category — it usually
> hides a real infra defect. Root-cause intermittent failures
> rather than hedging assertions."*

Both #222 and #205 had specific infra defects traceable via
existing diagnostic logs:

- `chat_consensus_log.disagreement_notes` captured the LLM
  gatekeeper's reasoning verbatim: *"clear refs as none are
  from ISO 27005."* Signal C's curator-tier refs (weight 1.00)
  were being cleared by the arbiter because there was no
  hard-lock protecting refs (only question_type + framework
  had locks). Genuine architectural gap.

- `chat_casefile_log.question_type` recorded `unknown` for
  "is X applicable?" queries. Scan of `CLEAR_INTENT_PHRASES`
  confirmed no applicability pattern existed. Genuine coverage
  gap.

Fixes landed as curator-tier discipline additions (Signal B/C
ref lock + CLEAR_INTENT gap fill) — no "hedge the assertion"
route needed.

**Rule** (reinforcing CLAUDE.md): every "stochastic" failure
report should trigger a diagnostic-log trace. `chat_consensus_
log`, `chat_casefile_log`, `ai_call_log` capture enough state
that the specific infra cause is almost always recoverable.
Hedging the assertion instead of finding the cause accumulates
untracked infra debt.

### 10. Option-picking is easy; executing the option is nuanced

The atlas/playbook border-sharpening (post-arc) took FOUR
iterations to land — despite the design conclusion (Option A:
"keep both, sharpen borders") being clear at the option-pick
moment.

The nuance revealed itself only through operator paste of the
rendered output at each iteration:

1. Cross-nav pills only → operator: "advisory should MOVE to
   topics" (initial commit under-delivered)
2. Removed BOTH advisory + evidence-classes → operator: "still
   feels incomplete" (over-shot; lost audit-forensic sources)
3. Restored gap-text fallback → operator: "still feels
   incomplete" (missing the sources list — different from
   advisory)
4. Restored evidence-classes with atlasMode flag → correct
   border

The lesson: "drop the advisory panel" turned out to mean
different things at different levels:
- Drop the per-MUST "Have/Still-needed" prose ✓
- Drop the template download CTA buttons ✓
- Drop the Evidence Package export ✓
- Drop the Cite external source CTA ✓
- KEEP the per-leaf sources list (audit-forensic) — NOT
  self-service
- KEEP the yield stats (audit-forensic) — NOT self-service

Each of those had to be teased apart by looking at the actual
rendered output. Option labels are necessarily coarse.

**Rule**: when executing an ambitious UX option, paste the
rendered output back at each iteration. What "sharpen borders"
means at the abstraction level is different from what it
means at the CSS/DOM level. Operator eyes catch the granularity
gaps that code review + tests don't.

### 11. Provenance-preserving structural extraction

Every structural finding carries:
- `checklist_item_id` — the specific MUST it binds to
- `evidence_text` — auditor-facing narrative naming the pattern
  and its extracted content ("Approved By: Maria Silva, CEO —
  structural: doc-control header Approved By field")
- `inference_source = 'structural_pattern'` — the lane
- `grounding_method = 'structural'` — the auditable method

An auditor tracing the finding sees exactly which line/table
row generated it. Not "we detected a doc-control block" — but
"line 34: Prepared By: Jane Doe proves item:5.2:owner".

**Rule** (same as Ship 6'.b): every finding needs a provenance
chain that lets an auditor reconstruct why we bound this
evidence to this MUST. Structural evidence is no exception.

## What Ship 54' did NOT do

- **Bulk-add doc-control markers to templates.** Only pilot on
  `req:5.2:information_security_policy`. Curator task to walk the
  845 templates + add `<<DOC_CONTROL>>` + `<<REVISION_HISTORY>>`
  where appropriate.
- **Auto-fill Prepared_By / Reviewed_By / Approved_By from
  tenant_profile.** Would need new tenant_profile fields
  (`isms_manager_name`, `ceo_name`, `dp_officer_name`). Deferred.
- **Revision-history append on template edits.** MVP seeds one
  row for the current version + today. When the template_version
  bumps, a new row would ideally append. Deferred to a future
  arc.
- **Test coverage for Phase 3 signal integration end-to-end.**
  Signal unit-tested in isolation via mocked doc; not
  end-to-end verified against a real intake run with
  USE_CONSENSUS_EXTRACTION=1. Deferred.
- **SPA Documents tab list view + per-doc detail modal.**
  Deferred from Ship 51 + 52 + 53. Still deferred.
- **Metadata derivation wire-up in posture_writer.py.** Deferred
  from Ship 51 + 52 + 53. Still deferred.
- **Extract `_TOPIC_SCOPE_RE` to shared module.** Deferred.
- **CI grep guards** for polish preservation + raw Chroma
  HttpClient + Rule 10 bracket-form. Deferred.
- **Retire `pillWithLabel` alias.** Deferred from Ship 52.

## Deferred / follow-on candidates

### Ship 55 candidates (near-term)

- Bulk-add `<<DOC_CONTROL>>` + `<<REVISION_HISTORY>>` markers to
  policy/procedure templates (curator arc)
- tenant_profile schema addition for Prepared_By / Reviewed_By /
  Approved_By auto-fill in doc-control renderer
- End-to-end intake test with USE_CONSENSUS_EXTRACTION=1 to
  measure Phase 3 signal impact on precision/recall
- Documents tab list view + per-doc detail modal
- Metadata derivation wire-up in posture_writer.py
- Chat: structured TopicBundleCard schema for the topic-bundle
  response (currently prose + deep-link only)

### Longer-term

- **Patent filing preparation** for the intake mechanism —
  round-trip binding, dual-role structural fusion, provenance-
  preserving structural extraction (per operator's IP note).
  Prior art search + spec draft.
- Structural detection extension: records-produced section
  (auto-cross-link procedures to registers) + reference-to-
  other-documents (dependency graph writes).
- Topic view: chat + topic-bundle context — asking follow-ups
  inside a bundle context (session continuation).
- Bulk-audit: run structural detectors across the whole Arion
  demo document corpus + surface structural coverage metrics
  in the dashboard.

## The round-trip diagram

```
                   Ship 54'.d               Ship 54'.e
                   ─────────                ─────────

    db/templates/  →  DOCX renderer  →  tenant fills in
    req__5_2__     →  <<DOC_CONTROL>> →  Prepared/Reviewed/
    isp.md            block emitted       Approved names
        │
        │                                        │
        │            downloaded                  │  uploaded back
        ▼                                        ▼
    tenant_profile                    intake/readers.py
    substituted                       (mammoth for docx)
        │                                        │
        │                                        ▼
        ▼                             structural_evidence.py
    doc-control                       ├─ detect_doc_control_header
    table with                        ├─ detect_revision_history
    signature lines                   ├─ detect_signature_blocks
                                      ├─ detect_interested_parties
                                      └─ detect_table_of_contents
                                                 │
                                                 ├─ Phase 2:
                                                 │   structural_evidence_to_findings()
                                                 │   → document_findings rows
                                                 │     with inference_source='structural_pattern'
                                                 │
                                                 └─ Phase 3:
                                                     doc.extraction_metrics['structural_evidence']
                                                     → structural_maturity signal
                                                     → boost every candidate
```

Output schema = input schema. Same detection pass fuels both
self-standing evidence AND consensus signal. That's the round-
trip binding + dual-role fusion that IS the intake differentiator.

## Verified state

- Topics data: 17 topics, 185 leaf-references, cleanly grounded
  across Program → Extension → Obligation
- Topics API: 200 on list + detail endpoints; deep-linked to
  dashboard for legacy drill-in
- Topics SPA: nav mode added; landing grid + inline drill-in
  with 5-section shape + per-leaf state chip
- Chat topic-routing: 4 topic queries route correctly (DSR,
  incident, consent, supplier); regression clean on non-topic
  queries
- Doc-control renderer: 5.2 ISP DOCX contains all 11 expected
  labels; doc number renders as POL-5.2-Rev03
- Structural detector: 13 unit tests pass; round-trip on our own
  5.2 DOCX yields 3 findings on 5.2 program_review leaf
  (item:5.2:rev_date × 2 + item:5.2:rev_reviewer)
- Consensus signal: emits boost=0.105 for the 2-pattern 5.2 DOCX
  case; scales correctly through the 40%/70%/100% ranges

Ship 54' arc closes. The templating + advisory + intake round-
trip is operationally complete across all three phases of the
54'.e hybrid design. The workflow layer is a first-class
consumer surface alongside the dashboard.
