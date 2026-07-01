---
name: dejargonize-ux-pass-2026-07-01
description: "SHIPPED 2026-07-01 (17 passes across ~10 commits): every tenant-facing surface rewritten to read as natural compliance language, no snake_case slugs, no leaf_id/edge-type/system machinery leaking into visible text. Started from a single Evidence Package rewrite that reused RequirementNode.business_description + EvidenceRequirement.description instead of hand-authoring per-node text; the pattern (reuse curated fields, humanize slugs at display, ratify vocabulary consistently) then extended to Evidence Package + dashboard + chat answers + templates (md + docx) + intake queue + notifications + profile + cascade renderers + docs upload trace + Stage-1/2 queue + heatmap tooltip + chat streaming status + inbox + admin re-extract + onboarding journey + session persistence + error messages. Eval held at ≥197/199 across every pass. Client helpers: humanizeSource() humanizeStandardId() humanizeNotifKind() humanizeSlug() humanizeEngineReason() humanizeStageName() humanizeErrorType(). Backend helpers: rag/posture/advisory.py `_humanize_evidence_type()` `_humanize_leaf_label()` + rag/templates/renderer.py `_SOURCE_HUMAN` `_humanize_source()` `_humanize_control_ref()`. Vocabulary decisions locked in CLAUDE.md."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## What this is

The de-jargonize UX pass shipped 2026-07-01. Every tenant-facing
surface reads as natural compliance language. Future work must
preserve the conventions.

## Trigger

Screenshot of A.5.15 detail panel had control text missing + 5
test upload artefacts polluting the sources list. Fixing that
surfaced a broader observation: the panel was "nicely detailed
but riddled with cryptic or system jargon". User asked how to
present hundreds of thousands of nodes across multiple frameworks
naturally rather than system-jargon-heavy. The answer: reuse the
curated fields we already spend time drafting (`business_
description` on RequirementNode + `description` on
EvidenceRequirement) instead of re-authoring per-node display
text. That pattern locked in with the Evidence Package rewrite,
then extended pass-by-pass to every other surface.

## Surfaces touched (in order)

1. **Evidence Package** (`rag/posture/evidence_package.py` rewrite +
   commit `ef026a8` then `ba360ef` follow-up) — leads with
   `business_description` + `EvidenceRequirement.description`.
   Strips `[leaf-scan back-bind from finding <uuid>]` admin trace.
   Confidence tag hidden when `high`. `humanize_standard_id`
   + `humanize_evidence_type` helpers.

2. **Dashboard detail panels** (commit `ba360ef`): backend
   `_humanize_evidence_type()` (Title Case + preserved acronyms),
   new `_humanize_leaf_label()` (prefers catalog title, strips
   trailing parenthetical ref). Frontend: "Composition" →
   "Coverage", "Direct evidence" → "Evidence for this control",
   "Derived from" → "Bridged from", "no source yet" → "not yet
   evidenced", "How to advance" → "How to strengthen", suppress
   duplicate label rows, fallback "leaf" → "Evidence".

3. **Chat answers** (commit `9f0f017`): `_humanize_slug()` helper
   in context_assembler + llm_answer prompt context; expanded
   `_ROLE_LABELS` from 28 → 70 entries covering every catalog
   evidence type (`agreement_template`, `audit_programme`,
   `breach_notification`, `dsar_response`,
   `records_of_processing`, `segregation_matrix`, etc.).
   Prevents LLM echo of raw slugs into answer prose.

4. **Templates** (commit `c9b471b`): .md preamble drops
   `Leaf: req:X:Y`; multi-source attribution humanized via
   `_SOURCE_HUMAN` (`extracted → uploaded document`); cross-
   framework citations via `_humanize_control_ref()`
   (`GDPR:2016/679:Art.32 → GDPR Art.32`). .docx markers
   `[ MUST · item:X ]` → `◆ Required element — X`;
   `⇣ EDIT START ⇣ (item:X)` → `▽ Enter your evidence for "X"
   below ▽`. Round-trip binding preserved by unchanged .md
   `<<MUST item:X>>` markers.

5. **Intake + notifications + profile + cascade** (commit
   `9837b88`, one omnibus): shared client helpers
   `humanizeSource()` / `humanizeStandardId()` /
   `humanizeNotifKind()` / `humanizeSlug()`. Stage-1 detail chip
   `req:A.5.15:...` → `A.5.15`; inferred-from block humanized;
   cascade timeline slug fields; notify() titles/bodies rewritten
   at four write sites (drops `TRIGGERS_OBLIGATION`,
   `BLOCKS_WHEN`, `triggered_implication` table name); inbox
   kind chip humanized; renderExternalSystemRow covers slugs;
   renderCascadeOverrides Kind → Scope, dropdown sentences;
   full cascade renderer pass (KPI tile labels, Triggered
   Implications → Follow-ups, Expected followups → Expected
   next steps, Focal (verification) → Verification event).

6. **Docs upload trace + queue + heatmap + streaming + inbox +
   admin + onboarding + session + errors** (pending omnibus):
   pipeline stage names humanized; queue qcard uses
   `humanizeStandardId`; new `humanizeEngineReason()` mirrors
   `_prettify_reason` server-side; heatmap tooltip "cascade
   implications" → "follow-ups"; chat streaming status texts
   ("Classifying intent" → "Understanding your question"); inbox
   toolbar subtitle "Cascade events" → "Recent events"; admin
   re-extract UI + backend messages; onboarding journey `why`
   strings; session-persistence 503/500 error text + chat memory
   hint on the empty state; error-message pass across all
   tenant-UI-facing `HTTPException` details.

## Vocabulary decisions (locked)

- MUST → "required element"; SHOULD → "recommended addition"
  (in tenant prose; auditor RFC 2119 sense preserved in
  system-internal docs).
- "cascade implication" → "follow-up".
- "cascade event" (system trigger noun) → "recent event" in
  tenant framing.
- "engine proposal" → "posture proposal".
- "extractor engine" / "RAG pipeline" → "extraction" / "the
  answer service".
- Pipeline stages `read/enrich/extract/write/xfw` →
  `read/classify/extract findings/post to posture/cross-
  framework`.
- Auditor acronyms (NC/OFI/Comply/N/A) kept — they're standard
  compliance vocabulary.
- Standard ids humanized (`ISO27001:2022` → `ISO 27001:2022`;
  `GDPR:2016/679` → `GDPR`).

## Helpers to keep in sync

**Backend:**
- `rag/posture/advisory.py`: `_humanize_evidence_type()`,
  `_humanize_leaf_label()`
- `rag/templates/renderer.py`: `_SOURCE_HUMAN`, `_humanize_source()`,
  `_humanize_control_ref()`
- `rag/arion_graph.py`: `_ROLE_LABELS` (70 entries),
  `_pretty_role()`, `_prettify_reason()`
- `api_server.py`: `_humanize_reason()` (dashboard-specific)

**Frontend** (`static/arioncomply.html`, near `escapeHtml`):
- `humanizeSource()` (mirror of `_SOURCE_HUMAN`)
- `humanizeStandardId()`
- `humanizeNotifKind()` (mirror of the 4 cascade notify kinds)
- `humanizeSlug()` (generic snake→space)
- `humanizeEngineReason()` (mirror of `_prettify_reason`)
- `humanizeStageName()` (`_STAGE_LABEL` mirror)
- `humanizeErrorType()` (`_ERROR_LABEL` mirror for pipeline
  error types)

When adding a new source / notification kind / event type /
pipeline stage / error code, ADD the mapping in the appropriate
helper so tenants don't see the raw slug.

## Deliberate exemptions (kept technical)

- `/api/v1/admin/*` staff-facing endpoints (unmatched-patterns,
  uploads/quality, cypher, structured_events validation) —
  admins consuming these are pipeline operators.
- HTML `data-` attributes carrying full leaf_ids /
  standard_ids — round-trip identifiers, invisible to tenants.
- HTML provenance comments in rendered templates (contain
  leaf_id + template version for audit trail).
- Server log messages — engineering telemetry.
- Machine ref placeholder in cascade override target input
  (`e.g. ISO27001:2022:A.6.4 (full machine ref — needed for
  exact match)`) — annotated so the tenant understands why.

## Related pattern

The Evidence Package pattern of **reusing curated content fields
rather than re-authoring per-node display text** scales to
arbitrary standards. When we curate a new framework, the
`business_description` + `EvidenceRequirement.description` fields
we already draft in the catalog automatically feed every
tenant-facing display. Any new tenant surface should follow the
same "reuse first, humanize slugs at display" principle rather
than hand-writing per-node text.

## Eval discipline

Every pass ran the full 199-case eval before commit; the floor
of 197/199 held across every commit (some hit 198/199).
Failure cases were the known-stochastic `#16` / `#27` state-
drift / `#5` LLM-jitter set; no new regressions.

## Files touched

- `rag/posture/advisory.py`
- `rag/posture/evidence_package.py` (new, then rewritten)
- `rag/templates/renderer.py`
- `rag/templates/docx_renderer.py`
- `rag/cascade/engine.py`
- `rag/cascade/posture_overlay.py`
- `rag/journey/state.py`
- `rag/context_assembler.py`
- `rag/llm_answer.py`
- `rag/arion_graph.py`
- `api_server.py`
- `static/arioncomply.html`
- `CLAUDE.md` (this pass documented)
