---
name: ship-57-prime-arc-2026-08-08
description: "Ship 57' arc retrospective — per-leaf prerequisites across the
  whole compliance catalog. 5 sub-arcs across 2026-08-07→2026-08-08 built a
  flat one-YAML-per-leaf architecture mirroring the Ship 56' guidance
  shape, delivered 100% coverage (844 YAMLs / 3,516 items) across
  ISO 27001 + ISO 27701 + GDPR, and wired the full pipeline (loader →
  runtime cache → renderer → docx → API → SPA). Codified lessons: P/E/O
  role vocabulary is a durable abstraction for the LLM; post-hoc
  deterministic recategorization beats prompt-tuning for semantic
  category slips; MVP-readiness sweep design costs more than raw check
  coverage when false positives are cheap to write; additive-over-
  replacement is the right default for tenant-facing UX with curator
  authorship; informational data surfaces should bypass gap-detection
  gates."
metadata:
  type: project
  ship: "57'"
---

# Ship 57' — Per-leaf prerequisites: from data model to SPA

## The arc in one sentence

Ship 57' delivered a per-leaf prerequisites store (mirror architecture
of Ship 56' guidance) with 844 gpt-4.1-generated YAMLs across three
frameworks, then wired the store through five surfaces: catalog
resolver, Neo4j loader, template renderers (markdown + docx), API
advisory endpoint, and the Topics SPA leaf-detail view.

## Motivation — templates need context, not just checklists

Ship 56' answered "what does 'done' look like per MUST?" via best-
practice guidance steps. But a tenant staring at a fresh template
still needed the context BEFORE drafting: what other artefacts must
exist, why they matter for THIS specific artefact, and what "done
enough" looks like on the prereqs to unblock the current task.

Framework-role model made this sharper. An Extension leaf (ISO 27701
A.7.2.2 lawful basis) can't be drafted without the Program's asset
register (ISO 27001 A.5.9) and the Obligation's legal yardstick (GDPR
Art.6). A generic "Before you start" hand-authored list gets some of
this but doesn't scale to 844 leaves, doesn't carry structured
Why/Good-enough per prereq, and doesn't get better as we curate.

## Sub-arc breakdown

| Sub-arc | Deliverable |
|---|---|
| 57'.a | `Prerequisite` dataclass + `EvidenceRequirement.prerequisites` field + `enrichment/prerequisites/apply_to_catalog.py` resolver + README locking the YAML shape and category vocab (task #572) |
| 57'.b | `enrichment/prerequisites/generate_from_catalog.py` with `--sample-print`/`--sample`/`--bulk` modes, gpt-4.1 with 3 seed inputs (foundational hints per P/E/O role, Neo4j PREREQUISITE_OF edges, template Before-you-start prose). Bulk generation: 844 YAMLs / 3,516 items over ~40 min. 0 LLM parse failures (line-based fallback parser from Ship 56' lesson held). Then diagnostic + curator scripts: `prereq_recategorize_cross_role.py` (fixed 138 category slips), `prereq_cleanup.py` (dropped 14 dangling refs + 1 dup), `prereq_sweep_check.py` (0 red / 0 yellow after 3 rounds of iteration). Filler-phrase scrub of 3 trailing "for accountability" / "for traceability" endings (task #573) |
| 57'.c | Neo4j loader wired: `apply_prerequisites_to_catalog` called after guidance apply, `_prereqs_to_json` serialises tuple to JSON string, both EvidenceRequirement MERGE sites (regular + DerivedSpec direct_evidence) persist `r.prerequisites` property. `rag/templates/prerequisites_lookup.py` runtime cache mirrors `guidance_lookup.py` shape — process-lifetime cache, keyed by leaf_id (task #574) |
| 57'.d | `renderer.py` gains `_PREREQUISITES_MARKER_RE` + `_format_prerequisites_markdown` + `_apply_prerequisites_blocks`, called from `render_template` right after `_apply_guidance_blocks`. `docx_renderer.py` parallel: `PREREQUISITES_MARKER_RE` + `_render_prerequisites_block` + `_humanize_std_ref` helper + marker handler in the line loop. 3 canonical templates seeded with `<<PREREQUISITES>>` marker (A.5.15 access control policy, Art.30 records of processing, A.7.2.2 lawful basis register). Postgres templates table synced (task #575) |
| 57'.e | `rag/posture/advisory.py::build_per_must_advisory_data` adds `prerequisites` field on each leaf-level dict (mirror of `must_items[*].guidance` shape but per-leaf not per-item). `api_server.py` `/api/v1/advisory/leaf/{leaf_id}/detail` endpoint passes it through, with a fallback path when the advisory builder returns None for Comply-verdict leaves. SPA `arioncomply.html` adds "Before you start" section between status and MUST-checklist, grouped by category with color-coded pills (foundational green / direct blue / cross-role brown), per entry showing ref+title + Why + optional Good-enough. Eval regression check: 230/232 PASS + 1 WARN + 1 FAIL (case #1 pre-existing stochastic physical-leak, unrelated to change scope) (task #576) |
| 57'.f | Retro (this doc); user-parked follow-up #577 for leaf-detail actionable-guidance rework |

## Key architectural decisions

**1. One YAML per leaf, not per MUST.**
Ship 56' guidance was per-MUST (5,385 YAMLs at ChecklistItem
granularity) because "how well is this specific requirement satisfied"
is a per-MUST question. Prerequisites are per-LEAF (844 YAMLs at
EvidenceRequirement granularity) because "what other artefacts do I
need before drafting this document?" is a per-document/register/policy
question, not a per-checkbox one. Different granularity for different
question shape.

**2. Nested directory by control_ref.**
`enrichment/prerequisites/{control_ref}/{evidence_type_slug}.yaml` —
same as Ship 56'. Human curators browse by compliance domain (all
A.5.15 leaves in one folder), programmatic access uses leaf_id key.

**3. P/E/O role vocabulary in the prompt.**
The generator prompt names the framework role explicitly: PROGRAM =
ISO 27001, EXTENSION = ISO 27701, OBLIGATION = GDPR. Foundational
hints vary by role. `cross_role` category means "prereq lives in a
different framework role than the target leaf." When the model sees
"target is OBLIGATION, hint list includes ISO 27001 refs," it
correctly labels the ISO 27001 prereqs as cross_role. When target and
prereq are same-framework, it collapses to `direct`. This worked
100% on cross-framework targets (GDPR + ISO 27701) — the miss was
same-framework "cross-domain" cases where the LLM overloaded
cross_role for what should be direct. Post-hoc recategorizer caught
those deterministically.

**4. YAML shape carries curation_status.**
```yaml
leaf_id: req:A.5.15:access_control_policy
control_ref: A.5.15
standard_id: ISO27001:2022
curation_status: draft         # draft | reviewed | approved
authored_by: llm-4.1
authored_at: '2026-08-07'
prerequisites:
  - ref: "4.3"
    standard_id: "ISO27001:2022"
    title: "ISMS Scope Statement"
    category: foundational       # foundational | direct | cross_role
    rationale: |
      1-3 sentences on WHY this prereq matters for THIS artefact
    good_enough: |
      1-2 sentences on the pragmatic threshold to unblock the task
```
Enables `approved / total` maturity tracking as Ship 56'.

**5. Neo4j persistence as JSON string.**
Prerequisites are structured objects (6 fields per entry). Neo4j
properties are scalars or lists of scalars — no native list-of-map.
Options were: JSON string (single field, deserialize on read),
parallel arrays (6 fields per entry), or related nodes (heaviest).
JSON string chosen for MVP. Readers use `json.loads` to reconstruct.
Trade-off accepted: not directly queryable in Cypher without
apoc.convert.

**6. `<<PREREQUISITES>>` marker sits once per template.**
Unlike `<<GUIDANCE>>` which sits once per MUST (looks up the preceding
MUST/SHOULD marker), `<<PREREQUISITES>>` resolves against the
template's target leaf_id directly. Simpler position semantics: the
marker can sit anywhere in the template, typically under "Before you
start".

**7. Additive-over-replacement for tenant-facing UX.**
The 3 canonical templates already had hand-authored "Before you
start" checkbox lists (curator judgment). I placed the new
`<<PREREQUISITES>>` marker AFTER the checklist rather than replacing
it. Rationale: curator-authored voice has institutional value; the
generated callout adds Why + Good-enough detail the hand-auth
doesn't. Both surface together; curator can strip the hand-auth
later if they prefer YAML-only.

**8. Informational data bypasses gap-detection gates.**
`build_per_must_advisory_data` returns None for Comply-verdict
leaves (it's a gap-finder). Prereqs are informational, not
gap-driven. The leaf-detail endpoint added a fallback: if adv is
None, look up prereqs directly via `get_prerequisites_for_leaf`.
Otherwise Comply leaves wouldn't render "Before you start" — which
would be wrong since prereqs exist regardless of posture.

## Coverage — three frameworks

| Framework | Leaves | % |
|---|---:|---:|
| ISO 27001 (ISMS + Annex A.5-A.8) | 472 | 55.9% |
| ISO 27701 (A.7 controller + B.8 processor) | 196 | 23.2% |
| GDPR (Art.*) | 176 | 20.9% |
| **Total** | **844** | **100.0%** |

Post-cleanup: 3,516 prereq items across 844 leaves. Median 4
prereqs per leaf (min 3, max 6). Rationale median 26 words, good-
enough median 18 words. Cross_role distribution (target ← prereq):
ISO 27701 ← ISO 27001 = 301, GDPR ← ISO 27001 = 121, ISO 27701 ←
GDPR = 64, ISO 27001 ← GDPR = 2.

## Codified lessons

### 1. P/E/O role vocabulary is a durable abstraction for the LLM

The `PROGRAM / EXTENSION / OBLIGATION` framing in the prompt made
gpt-4.1 correctly categorize cross-framework prereqs 100% of the
time when the target framework differed from the prereq framework.
Same-framework prereqs got a `direct` label consistently. The miss
was in a semantic gap of the vocabulary itself: "cross_role"
overloaded when the LLM interpreted it as "cross-domain within the
same framework." This is a specification-level ambiguity, not an LLM
failure. The vocabulary still earned its keep — cross-framework
detection is the hard part; a same-framework/cross-framework check
is trivial to deterministic-fix post-hoc.

Rule: when adding vocabulary for LLM prompts, be explicit that
category X applies only across dimension Y, and design a
deterministic post-hoc check for the dimension.

### 2. Post-hoc deterministic recategorization > prompt tuning for category slips

97.7% of cross_role entries were miscategorized (86 of 88 in the
initial ISO 27001 corpus). Two viable paths: sharpen the prompt +
regenerate the affected files (~$0.25 in tokens + ~5 min of
prompt-iteration risk), or run a 30-line deterministic
recategorizer (`prereq.standard_id == target.standard_id` → change
to `direct`). The deterministic path was cheaper, safer, and
exhaustive. Generalizes Ship 56' lesson #4 ("parser resilience >
prompt gymnastics") from syntactic to semantic categories.

Rule: if a categorization error has a deterministic definition,
fix it deterministically. Prompt-tune only when the categorization
is genuinely fuzzy.

### 3. Sweep-check design costs more than sweep-check coverage

My initial MVP-readiness sweep flagged 60 red blockers. Analysis:
46 were false positives from a check-design error — I flagged
`prereq.ref == target.control_ref` as "self-reference," but that's
actually legitimate (a leaf under control X can depend on the
primary artefact under control X, its control-level parent). I
also flagged "to ensure that" and "in order to ensure" as filler
without narrowing to trailing position, catching 34 legitimate
grammatical connectives as false positives.

Rule: a check that generates 70%+ false positives loses credibility
faster than a check that misses genuine issues. Design each check
with narrow, defensible triggers; iterate the check as evidence
accumulates.

### 4. Additive-over-replacement is the right default for tenant-facing UX with curator authorship

The 3 canonical templates I marked had hand-authored "Before you
start" checkbox lists with curator judgment ("access rules vary by
class", "the policy names the authoriser per asset class"). I
placed the new marker AFTER the existing list rather than replacing
it. Reason: hand-auth voice has value the LLM output doesn't (short,
opinionated, tenant-workflow-oriented); generated output has value
hand-auth doesn't (Why + Good-enough detail per prereq). Both
surfaces together lets curator strip either side later.

Rule: default to additive when replacing tenant-visible curator
work. Wholesale replacement erases institutional judgment.

### 5. Informational data surfaces should bypass gap-detection gates

`build_per_must_advisory_data` was written to find gaps — it
returns None for Comply-verdict leaves because there's nothing to
advise. But prereqs are informational, not gap-driven. Comply
leaves have prereqs just like NC leaves. The leaf-detail endpoint
had to add a fallback: if adv is None, look up prereqs directly.

Rule: when adding an informational field to a gap-detection
surface, verify the field surfaces for Comply-verdict leaves too.
Consider whether the field belongs on the gap surface at all, or
should live on a separate informational endpoint.

## What's now different in the product

**Every tenant on every leaf across every framework** sees prereq
context in:
- **Template renders** (`<<PREREQUISITES>>` marker → **Prerequisites:**
  callout with category-grouped entries between "Before you start"
  prose and the tenant edit zone)
- **Topics SPA leaf-detail** (new "Before you start" section between
  Current status and MUST checklist, with color-coded category pills)
- **Leaf-detail API** (`/api/v1/advisory/leaf/{leaf_id}/detail`
  returns `prerequisites` array; Comply-verdict leaves included)
- **Neo4j graph** (`EvidenceRequirement.prerequisites` JSON property
  — enables future graph queries like "what depends on A.5.9?")

Where Ship 56' left A.5.16 identity register with a bare MUST
checklist and a duplicative "How to close this gap" list, Ship 57'
adds sharp per-leaf prereq context ahead of the checklist:
- `Foundational: ISO 27001 4.3 ISMS Scope Statement` — Why the leaf
  can't be drafted without a scope, Good enough threshold
- `Foundational: ISO 27001 A.5.2 Roles & Responsibilities` — Why
  ownership matters for register accuracy
- `Direct: ISO 27001 A.5.9 Asset Register` — Why you need to
  enumerate systems before identities
- `Direct: ISO 27001 A.6.5 Post-employment responsibilities` — Why
  the lifecycle-close process must exist

## Follow-ons deferred

- **Curator review pass** — 844 YAMLs at `curation_status: draft`.
  Same pattern as Ship 56': sample-check (~1 hour for 100-file
  stratified sample) sets quality floor; full pass (~10-15 hours)
  can be trickle-curated. Track approved/total as a maturity
  metric.
- **Leaf-detail actionable guidance rework (#577)** — the "How
  to close this gap" section currently duplicates "What's
  missing" verbatim without added value. Also: Ship 56' per-MUST
  guidance is exposed on the API response `must_items[*].guidance`
  but the SPA leaf-detail MUST rows don't render it. Combined
  scope; parked pending templates arc.
- **Chat pipeline consumption** — prereqs aren't currently
  referenced by chat. Queries like "how do I close the A.5.16
  gap?" could pull prereqs into the answer via a casefile
  section. Future arc.
- **Regeneration on catalog change** — when a leaf is added or an
  existing leaf's evidence_type changes, generator should re-run
  for the affected files. Not wired yet.
- **Cite-mode integration** — tenants using external systems of
  record see the same generic prereq guidance as stored-mode
  tenants. Could add cite-mode overrides that adjust the
  Good-enough threshold ("Okta group-membership snapshot for
  {system} shows...").
- **Cross-framework querability in Cypher** — JSON string
  persistence blocks direct queries. Follow-up could add
  parallel arrays or Prerequisite nodes if a graph query pattern
  emerges.

## What Ship 57' costs to reproduce

- `gpt-4.1` API cost: ~$1.40 (457 leaves in the resumed bulk;
  earlier partial run cost extra ~$1.20)
- Wall clock: ~40 min bulk gen + ~5 min cleanup passes + ~1 hour
  wiring across 5 surfaces
- Human time: ~4-5 hours across the arc (design + sample review
  + wiring + verification + retro)
- Wire-up files: 6 modified + 1 new module + 3 diagnostic scripts
  + 3 templates seeded (+ 844 YAMLs generated)

Cheaper than one full curator sprint. Marginal Cost of adding a
fourth framework (e.g. SOC 2): a new foundational-hints list per
role + a bulk run for the framework's leaves + reload. Estimated
~2 hours + ~$0.30 per 200-leaf framework.
