---
name: templates-arc-closer-2026-08-14
description: "Task #577 landed — closes the templates arc that Ships 583–71' orbited around. Per-MUST guidance now renders on the SPA leaf-detail advisory panel; the redundant \"How to close this gap\" section retired. Backend was ready since Ship 56'; the detour into SSoT + bridge attribution kept the SPA piece parked. Now shipped."
metadata:
  type: project
  ship: templates
---

# Templates arc closer — Task #577 shipped

## The story

The templates arc's tenant-facing loop was designed as:

> Tenant clicks a control showing NC/OFI → sees which MUSTs are
> unmet, WHY they matter, what auditors expect, and which controls
> to fix first → downloads a starter template pre-filled with
> tenant profile + prior evidence → fills → uploads → posture
> flips.

Backend for every step of that loop was done by 2026-08-08:

- **Ship 56'** authored 5-bullet guidance per MUST
  (`what to write / what auditors flag`).
- **Ship 57'** authored prerequisites per leaf with rationale +
  `good_enough` acceptance criterion.
- **Ship 586** taught the template renderer per-MUST tick
  indicators.
- Backend `/api/v1/advisory/leaf/{id}/detail` returned all three
  fields on `must_items[*]` + `prerequisites[]`.

But the SPA didn't render the guidance. And the "How to close
this gap" section was a plain projection of missing MUST text —
duplicating what MUST rows already showed.

The reason the SPA piece parked: **the templates arc needed a
Single Source of Truth (SSoT) for per-MUST state before the
guidance could be conditionally surfaced.** Rendering "guidance
for missing MUSTs" without an authoritative "what's missing"
answer would drift every time a different surface computed the
answer differently. So we detoured into SSoT + all its
downstream reader migrations.

The detour spanned ~30 sub-arcs (Ships 583 → 71'.a) — SSoT
schema, sweep, triggers, bootstrap, reader migrations for
advisory + findings + Evidence Package, bridge writer walking
all edge types, N/A dominance schema split, numeric fabrication
fix, bridge attribution honesty, sub-clause retargeting, stub
creation, dimension metadata, ranker rework, expandable N-more.
All valuable, all now behind us.

Task #577 was the flag we planted saying "come back for this
once SSoT is solid." Today: SSoT is solid, and #577 landed.

## What shipped

`static/arioncomply.html` — one file. Changes:

1. **Per-MUST guidance rendered on unmet rows.** Each MUST row
   with `satisfied_state !== 'present'` now has a
   `<details><summary>Show writing tips (N)</summary>` block
   showing the 5 bullets from Ship 56'. Collapsed by default so
   leaves with many MUSTs stay scannable; auditor idiom mirrors
   Ship 71'.a's expandable `<details>` for asserted mappings.
2. **"How to close this gap" section retired.** It was a plain
   projection of missing MUST text — the same text already
   visible on the MUST rows. Post-Task-#577 the guidance is
   attached where it belongs (on the MUST that needs it) instead
   of duplicated in a section below.
3. **CSS added** for `.topic-must-guidance` — small caret icon
   (▸/▾), muted color palette matching existing MUST-row styling.

Prerequisites already rendered rationale + `good_enough`
(lines 3717-3720 of arioncomply.html) so no change needed
there. That part of the original #577 scope had been
implemented at some point during the detour without me
noticing.

## What the tenant sees now

For `req:A.5.16:identity_revocation_record` on Arion (NC 0/7):

- 4 prerequisites in a "Before you start" section, each with
  ref + title + rationale + `Good enough:` acceptance line.
- 7 MUSTs in the "What's covered / what's missing" list. Each
  unmet MUST shows a small `▸ Show writing tips (5)` link
  under the row. Click → expands to 5 bullets like *"Record
  the identity being revoked, including full name, unique
  identifier, and date of revocation..."*, *"Avoid listing
  groups or departments as signatories..."*
- Actions section with template downloads (MD/DOCX/XLSX) and
  Ask AI. Unchanged.

Total added content is ~35 bullets of curator-authored auditor
guidance per NC leaf, all pre-existing on the backend, now
finally visible.

## Files touched

- `static/arioncomply.html` — ~30 LOC added (guidance block +
  CSS) + ~12 LOC removed (retired remediation section).

Zero backend. Zero schema. Zero data. The templates loop is
now end-to-end reachable on the SPA.

## Second iteration (same day) — per-bullet ☑/☐ in template markdown

Dogfooding the A.5.15 template download surfaced that the
Ship 586 tick indicator lived only on the MUST-level "Best
practice" header (e.g. `**Best practice ✓ — covered:**`). The
5 auditor cues under the header stayed flat. A tenant reading
the download couldn't tell WHICH of the 5 cues their evidence
addressed vs which still needed work.

Second commit added deterministic per-bullet marks:

- **`rag/templates/renderer.py::_tokenize_bullet`** — extracts
  content-bearing tokens from a bullet (lowercased, ≥5 chars,
  minus a small stopword list of imperative writing verbs like
  `state / specify / avoid`). Keeps domain nouns like
  `policy / document / record / name` because they carry
  substance when they appear in tenant evidence.
- **`_bullet_evidenced`** — deterministic keyword overlap:
  the bullet is ☑ when ≥40 %% of its content-bearing tokens
  appear as substrings in the tenant's evidence corpus. Otherwise
  ☐. No LLM; pure string ops.
- **`_format_guidance_markdown`** — new `evidence_corpus`
  parameter; emits `- ☑ …` or `- ☐ …` per bullet. Silent when
  no corpus is available (fresh tenants) — degrades to Ship 56'.a
  flat rendering.
- **`_apply_guidance_blocks`** — new `evidence_by_item` param
  threaded through from `render_template`.
- **`render_template`** — fetches ONE control-scoped corpus
  (aggregate of tenant's approved `document_findings.excerpt`
  for all MUSTs under this control) and reuses it across every
  MUST. Bullets on one MUST often reference cues the tenant
  documented under a sibling MUST — control-level scope catches
  those without needing per-MUST semantic matching.

Threshold tuned empirically on Arion A.5.15: 50 %% marked only
2 %% of bullets ☑ (excerpts are snippets, not full policies).
40 %% catches the specific-noun matches without demanding the
auditor's exact phrasing.

Verified UX on A.5.15:logical_rules (MUST-level ✓, 2 ☑ / 3 ☐
per-bullet). Tenant reads: "You have coverage at MUST level, and
your evidence addresses 2 of the 5 auditor cues; the other 3
(named individual approving, cross-reference to procedures,
signed approval date) still need work." Actionable.

## Files touched (2nd iteration)

- `rag/templates/renderer.py` — 3 new functions + query widening
  + threshold + threading (~90 LOC net).

Zero schema. Zero data.

## Codified lesson

### 39. Park deliberately, come back deliberately

Ship 56' (guidance) + Ship 57' (prereqs) landed backend-only in
early 2026 because the SPA piece exposed an SSoT gap. That gap
took 30+ sub-arcs to fill. The value of parking Task #577
explicitly (rather than either forcing the SPA render on top of
broken SSoT, OR forgetting about it) was that when we finally
returned, the backend was still positioned to receive the SPA
render with zero data migration.

Rule: when a feature exposes a foundational gap, park the
feature-facing piece explicitly, ship the foundation, come
back. The foundation makes MANY future features cheaper (that's
the SSoT bill of goods); the parked feature just needs the
final render.

## Follow-ons

Templates arc is closed. Remaining pending items in this
neighborhood:

- **docx renderer parallel** — the `_render_guidance_block` in
  `rag/templates/docx_renderer.py` still uses the flat Ship 56'.a
  format (no state marker on the header, no per-bullet ☑/☐).
  When we ship a docx tweak in this area, port both.
- **Task #595** — 22 tenant-facing GDPR articles without ISO
  bridges. Independent arc.
- **Dogfood friction #4 from Ship 69** — false-positive-feeling
  bridge edges (A.6.3 training → Art.32:program_review). Curator
  review, not code.

The next natural cycle after this is either template-loop
dogfood (walk the loop on a live NC → template → upload → flip
scenario) or task #595 (GDPR bridge coverage).
