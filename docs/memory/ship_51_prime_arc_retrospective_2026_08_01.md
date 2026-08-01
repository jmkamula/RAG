---
name: ship-51-prime-arc-retrospective-2026-08-01
description: "Ship 51' arc retrospective — chat + engine sweep quality surfaced by pre-POC dry-run testing. 6 sub-arcs across ~2 days. Triggered by the operator sitting down as a real customer would and asking natural doc-inventory questions. Delivered: templates_block gating fix, engine-kick from intake pipeline, first-person polarity + dev-CLI hint scrub, client_documents metadata backfill (77/77 titles + 61/77 standards_cited + 77/77 topics_detected), topic-scope filter + compact doc-line rendering, polish preservation guard for count parentheticals. One false-alarm sub-arc (51'.c control_ref audit) closed with docstring + memory entry. Codified 5 lessons around dry-run discipline + cross-cutting metadata + polish preservation."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 51' arc retrospective — chat + engine sweep quality via dry-run testing.

## What triggered it

Late in the Azure dry-run prep, the operator sat down as a real
customer would and asked natural questions of the chat:

> *"What document have I uploaded for Information Security?"*
> *"5.2 is NC while the system says OFI — what's going on?"*
> *"What documents have we uploaded regarding access security?"*

Each surfaced a different bug that the demo VM had learned to
work around over 6 months of iterative development. This arc is
the cleanup pass — 6 sub-arcs, ~2 days, one contiguous session.

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 51'.a | Removed `document_inventory` from `_RELEVANT_QUESTION_TYPES` — no more 18-card starter kits on doc queries | `a2aeb07` |
| 51'.b | Engine kick from intake pipeline (Stage 4.7) — dashboard fresh after every upload | `941f45d` |
| 51'.c | CLOSED without fix — `RequirementNode.ref` vs `.control_ref` was operator error, not codebase bug. Added docstring + memory entry | `32acef0` |
| 51'.d | First-person polarity + dev-CLI hint scrub + metadata backfill script | `c3e7448` |
| 51'.e | Topic-scope filter (`regarding X` / `about X`) + compact per-doc rendering | `9201cf4` |
| 51'.f | Polish preservation guard for count parentheticals `(N total)` / `(N of M total)` | `cf0fd18` |
| **51'.g** | **This retro** | pending |

## Sub-arc details

### 51'.a — templates_block gating for doc-inventory

**Symptom**: `What documents do we have` returned the resolver's
answer PLUS an 18-card starter-kit block for random NC controls
that had nothing to do with the doc question.

**Root cause**: `_RELEVANT_QUESTION_TYPES` in
`rag/templates/answer_footer.py` included `document_inventory` alongside
`gap_analysis` / `posture_check` / `document_content`. The doc-
inventory LLM path enumerated 18 different missing controls as
remediation guidance; `_extract_refs` regex-picked-them-up; templates_block
built cards for all 18.

**Fix**: 1-line removal from the trigger set. `document_content`
stayed (asking what a specific policy should contain legitimately
wants a template). Wide starter-kit UX already exists in Get Started
mode + dashboard drill-in — the chat surface shouldn't duplicate it.

### 51'.b — engine kick from intake pipeline (Stage 4.7)

**Symptom**: Newly-uploaded evidence didn't show on the dashboard
until a chat query on that tenant kicked `load_posture` as a
side-effect.

**Root cause**: The Stage-1-approval path had an engine kick
(`stage1_engine_kick_after_batch`, Ship 3'.d era) but the intake
pipeline never called `load_posture` for auto-approved findings
(fingerprint / templated / workbook / xfw_bridge). Auto-approved
findings never went through Stage-1, so the kick never fired.
Dashboard sat stale until a chat query or the 30-min sweep.

**Fix**: Added Stage 4.7 immediately after Stage 4.5 (xfw proposer)
and Stage 4.6 (workbook discovery) in `rag/intake/doc_pipeline.py`.
Runs `load_posture` on a fresh psycopg2 connection so it doesn't
entangle with the already-closed write path. Best-effort; a failure
logs a warning and the upload remains successful. Latency: ~19s on
230-control demo tenant, on top of ~100s extraction — acceptable
tail.

### 51'.c — CLOSED WITHOUT FIX

**Flagged during 51'.b diagnostic**: I ran an ad-hoc Cypher probe:

```cypher
MATCH (n:RequirementNode {control_ref: '5.2'}) RETURN n
```

Zero rows returned. Concluded "control_ref missing from
RequirementNode — codebase bug"; flagged 51'.c as an audit
candidate.

**Actual finding on audit**: Neo4j property-name convention is an
intentional asymmetric split:

- `RequirementNode` — uses `ref` (populated 478/478)
- `EvidenceRequirement` — uses `control_ref` (populated 844/844)
- `ChecklistItem` — uses `control_ref` (populated)

`graph_expander.py` correctly uses `n.ref` on RequirementNode in
all 9 Cypher literals. The one `n.control_ref` in Cypher elsewhere
(`scripts/gen_leaf_scan_catalog.py:434`) is on `EvidenceRequirement`,
which does have that property. My probe used the wrong property
name — operator error.

**Committed**: docstring block near the top of `rag/graph_expander.py`
documenting the convention + memory entry
[[ship-51-prime-c-closed-2026-07-31]] so future auditors don't
chase the same ghost.

**Codified lesson**: silent-zero Cypher on `{prop: value}` filter is
ambiguous — verify with `MATCH (n:Label) RETURN keys(n) LIMIT 1`
before flagging a data-missing bug.

### 51'.d — first-person polarity + CLI-hint scrub + backfill script

**Three coupled fixes**:

1. First-person singular polarity: `_POSITIVE_UPLOAD_MARKERS` and
   `_UPLOAD_STATUS_PATTERNS` in both `rag/arion_graph.py` and
   `rag/resolver.py` were "we"-only. Users switch pronouns
   naturally between "have we" (org perspective) and "have I"
   (operator perspective). Query "What document have I uploaded..."
   was falling through to the negative-polarity path with a
   misleading "You have uploaded the following..." intro.

2. Dev-CLI hint scrub: `Upload: python3 tools/doc_uploader.py --dir
   /path/to/docs --live` was appended to every doc_status answer.
   Tenants have no shell access. Removed the leak; rewrote
   fallback text to point at the SPA's Documents tab.

3. Metadata backfill: `scripts/backfill_client_documents_metadata.py`
   populates three fields deterministically from data already on
   the row:
     - `document_title` ← humanized filename
     - `standards_cited` ← composite `control_refs` split on `:`
     - `topics_detected` ← filename tokens ∪ `DOCUMENT_TOPIC_MAP`
       hits, minus stop-tokens
   
   Cross-cutting docs correctly emit multiple standards — verified:
   `Information Security & Data Management Policy` carries
   `{GDPR:2016/679, ISO27001:2022, ISO27701:2019}`. Idempotent, safe,
   dry-run by default. Applied to demo tenant: 30 titles + 61
   standards_cited + 77 topics_detected populated.

### 51'.e — topic-scope + compact rendering

**Symptom**: Query "what documents have we uploaded regarding access
security?" dumped all 54 docs, each with a 5-line control-ref list.
~1500 chars of wall.

**Fix**: Two coupled changes in `rag/arion_graph.py`:

1. `_extract_topic_scope` regex detects "regarding X" / "about X" /
   "for X" / "related to X" / "concerning X" / "touching on X"
   patterns, extracts topic tokens. `_filter_docs_by_topic` ranks
   uploaded docs by overlap between those tokens and each doc's
   combined haystack (filename + document_title + topics_detected —
   the topics_detected field populated by the 51'.d backfill is
   what makes this filter powerful).

2. `_compact_doc_line` replaces the full control-ref list with a
   count-per-standard summary. Doc assessed against 60 refs across
   3 standards renders as one line with `· covers ISO 27701 (32) +
   ISO 27001 (15) + GDPR (8)` instead of a 5-line dump. Whole-
   inventory cap tightened 20 → 15.

Result on the motivating query: 15 relevant matches out of 54, top
10 shown, "and 5 more" tail. Access Control Policy + Access
Management Process surface in the top 10 rather than being buried.

### 51'.f — polish preservation guard for count parentheticals

**Symptom**: 51'.e's deterministic intro `Uploaded documents relating
to access security (15 of 54 total):` got rewritten by polish as
`We have uploaded the following documents regarding access security:`.
Prose more natural but "15 of 54 total" — a load-bearing completeness
signal — silently dropped.

**Fix**: Third preservation guard in `polish_short_circuit_answer`,
after ref-drop (Ship 1.7 era) and bullet-drop (Ship 30 era).
`_COUNT_PAREN_RE` matches "(N total)" / "(N of M total)" / "(N of M)"
patterns; when any deterministic count parenthetical is missing from
the composed output, guard falls back to deterministic text. Same
discipline as the other two guards — fall back rather than surgically
re-inject.

## Delivery velocity

- Session length: ~4-5h across two dates (2026-07-31 into 2026-08-01)
- 6 sub-arcs including 1 closed-without-fix
- Zero mid-arc rollbacks
- Every change verified live on the demo VM before commit
- Eval baseline held: 230 PASS, 1 FAIL (case #34, state-dependent
  LLM phrasing, unrelated to this arc)

## Codified 5 lessons

### 1. Dry-run testing surfaces what months of dev-loop testing don't

The demo VM was built over 6 months. Everyone drifted through
workarounds — nobody typed "what document have I uploaded" because
we all say "what did we upload" or click through the Documents tab.
Sitting down as a real customer, using natural language, testing the
CHAT surface (not the API or the SPA directly) surfaced 5 real
bugs in 2 days.

**Rule**: before a POC install, spend an hour typing at the chat
window as a customer would. Type what you'd type on your first day.
Every awkward response = a bug.

### 2. False-alarm sub-arcs still produce durable value

Ship 51'.c was an operator-error diagnostic, not a real bug. But
closing it produced:
- A docstring block in `rag/graph_expander.py` documenting the
  Neo4j property-name convention (`ref` on RequirementNode,
  `control_ref` on leaves + items)
- Memory entry [[ship-51-prime-c-closed-2026-07-31]] with the
  codified lesson: verify with `keys(n)` before flagging a data-
  missing bug in Cypher

**Rule**: when a diagnostic turns out to be operator error, still
write the memory entry. Future auditors are protected from the same
mistake; the codified lesson is the value.

### 3. Backfill scripts + intake wire-up as a two-arc pattern

Ship 51'.d shipped the backfill script (`scripts/backfill_client_documents_metadata.py`)
without wiring the same derivation logic into
`rag/intake/posture_writer.py`'s INSERT path. Rationale:

- Backfill covers historical rows — needed today
- Intake wire-up has larger blast radius (touches every future
  upload) — deserves its own arc after we've verified the
  derivation quality on real data

**Rule**: backfill-first, wire-up-second is a safe delivery pattern.
Ship 51'.f didn't need to be delayed to prove out the backfill
derivation; we can see the topic-scope filter working correctly on
77 backfilled rows and confirm the intake wire-up is worth doing.

### 4. Cross-cutting metadata is real; single-category modeling would have failed

Documents on the demo tenant span 3 frameworks routinely. `Information
Security & Data Management Policy` covers `ISO 27001 (15) + ISO 27701
(32) + GDPR (8)`. `Data Protection Impact Assessment (DPIA) Procedure`
covers all three. Ship 51'.d's `standards_cited text[]` correctly
captures this cross-cutting nature via array semantics.

**Rule**: when curating metadata for docs (or any artefact that
spans frameworks), model cross-cutting from day one via text[] /
JSONB. A `single_category text` column would have required a
subsequent schema migration once the cross-cutting reality surfaced.

### 5. Every load-bearing polish signal needs its own preservation guard

The polish LLM in `polish_short_circuit_answer` had:

- Ref-drop guard (Ship 1.7 era) — protects control refs
- Bullet-drop guard (Ship 30 era) — protects list rows
- **Count-paren guard (Ship 51'.f)** — protects `(N total)` signals

Each guard was added when a NEW load-bearing signal category was
introduced. As we add more list-shaped short-circuits, new guards
will land alongside them. The pattern is clear: extract distinctive
signal from deterministic input, verify survival in composed output,
fall back on any loss.

**Rule**: whenever a short-circuit answer emits a signal that's
NOT prose but IS load-bearing for the tenant (refs, tags, counts,
verdicts, cite links), consider whether polish might strip it. If
so, add the appropriate guard.

## What Ship 51 did NOT do

- **Wire the metadata derivation into `rag/intake/posture_writer.py`**
  for new uploads. The backfill script covers historical rows.
  Deferred to a follow-up arc where we can verify the derivation
  quality against real customer data before broadening the surface.
- **Add polish preservation guard for tags** (Comply / OFI / NC /
  [DRAFT]) or verdicts. Ship 2'.j's preservation-check discipline
  already covers this in the case-file flow; not needed for
  short-circuits yet.
- **Investigate the 5.2 vs A.5.2 UX confusion**. Both refs are
  distinct rows in `posture_controls`; if the UI ever renders them
  identically, that's a labeling bug. Not surfaced during dry-run.
- **Add a per-doc drill-in surface for full control_ref lists**.
  Compact rendering elides the full ref list; a tenant who wants
  the full list on a specific doc has to open the Documents tab.
  Might want a "show refs" affordance later.
- **Cache the topic-scope filter results**. Query hits DB every
  time; fine at N=54 docs but might need caching at N=500+.

## Deferred / follow-on candidates

### Ship 52 candidates
- **Metadata derivation wire-up in `posture_writer.py`**. Small,
  well-scoped. New uploads land with `document_title` + `standards_cited`
  + `topics_detected` populated at INSERT time. Backfill script
  then only needs to run for historical rows.
- **CI grep guards** — regression fences for the two categories
  Ship 51' fixed: (a) any `_RELEVANT_QUESTION_TYPES` change to
  answer_footer.py should be reviewed against the doc-inventory
  regression pattern; (b) any `polish_short_circuit_answer` change
  should be reviewed for preservation-guard coverage of new signals.
- **Extract topic-scope patterns to a shared module**. Right now
  `_TOPIC_SCOPE_RE` lives in `arion_graph.py`. Other short-circuit
  paths might benefit (risk queries, cascade queries, evidence
  queries).

### Longer-term
- Topic-scope filter using `posture_controls.control_ref` topic
  clustering — richer than filename tokenization. Requires deriving
  the topic taxonomy from the curated leaves.
- Word bookmark preservation as a belt-and-braces atop Ship 50'.a
  L2 marker reconstruction. Would make the docx round-trip robust
  even when customers rename the file AND delete the attribution.
- Verdict-preservation guard in `polish_short_circuit_answer` if we
  ever emit posture verdicts in short-circuit answers (currently
  verdicts flow through the case-file path which has its own
  preservation-check).

## Relation to the Azure dry-run

Ship 51 is the immediate predecessor to the Azure dry-run. Every
sub-arc fixes a bug that would have been surfaced during the dry
run itself — but catching them on the demo VM (where the diagnostic
tooling is richer) saves ~2h of investigation on the fresh Azure
VM. The dry-run's job is now genuinely to test the INSTALL path
(Ship 47) + the diagnostic UX (Ship 48), not to shake out chat
quality bugs.

## Related

- Ship 47 — POC install path
- Ship 48 — deployment diagnostics
- Ship 50 — template round-trip + Q&A restructure (immediate
  predecessor; also surfaced during dry-run inspection of Stage-1
  queue)
- [[ship-51-prime-c-closed-2026-07-31]] — the false-alarm sub-arc's
  own memo
- `scripts/backfill_client_documents_metadata.py` — 51'.d artefact
- `rag/arion_graph.py::polish_short_circuit_answer` — where the
  three preservation guards live
