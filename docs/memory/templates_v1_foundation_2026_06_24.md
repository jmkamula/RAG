---
name: templates-v1-foundation-2026-06-24
description: "SHIPPED 2026-06-24: template authoring + storage foundation. db/templates/{leaf_kebab}.md filesystem source-of-truth → loader → Postgres templates table. Auto-scaffold generator emits markdown with <<MUST item:X>> + <<SHOULD item:X>> section markers binding the structured text to leaf checklist items. 645 scaffolds generated covering 3388 MUSTs + 891 SHOULDs. Idempotent loader; version-based preservation (v1=auto; v2+=hand-refined). Foundation for tenant download/edit/upload roundtrip + future deterministic (no-LLM) extraction."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

## Architecture (decided this session)

Three layers:

| Layer | Role |
|---|---|
| `db/templates/{leaf_kebab}.md` | Source of truth; versioned with curation; diff-able in PRs |
| `enrichment/templates/load_to_postgres.py` | Validates MUST coverage 1:1; upserts to Postgres |
| Postgres `templates` table (schema_v45) | Runtime serving |

Decisions:
- **Format**: markdown with structured `<<MUST item:X>>` + `<<SHOULD item:X>>` section markers. Tenant-natural to read/write; deterministic to extract on roundtrip.
- **Edit path** (v1): tenant downloads MD, edits locally, uploads back. In-app form-render is future.
- **Shared fields**: tenant_profile auto-fill for `<<NAME>>` placeholders (ISMS Manager, CISO, etc.) — render layer applies at serve time, not in source.
- **Refine guard**: version-based preservation. Auto-gen scaffolds = `template_version: 1`. Hand-refined = bumped to `2+`. Generator skips files with `template_version >= 2`.
- **Bootstrap**: all 645 leaves at once (auto-scaffolds); hand-refinement of top ~20 anchor templates is an ongoing separate workstream.

## Markdown shape

```
---
leaf_id: req:A.5.15:access_control_policy
control_ref: A.5.15
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Access Control Policy

> [Leaf description as blockquote — taken from EvidenceRequirement.description]

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD
> markers untouched — they bind this document to the checklist when
> you upload it back.**

## 1. {MUST item.text}

<<MUST item:A.5.15:physical_rules>>
_Why: {item.rationale}_

<<TEXT>>

## 2. ...

---

## Recommended additions

### 1. {SHOULD item.text}
<<SHOULD item:A.5.15:emergency_access>>
...
```

## Files shipped

| File | Lines | Role |
|---|---|---|
| `db/schema_v45_templates.sql` | 60 | Postgres table + indexes |
| `scripts/generate_template_scaffolds.py` | 200 | Auto-gen all 645 from `ALL_EVIDENCE_REQUIREMENTS` + `ALL_DERIVED_SPECS.direct_evidence` |
| `enrichment/templates/load_to_postgres.py` | 230 | Parser + validator + upserter |
| `db/templates/*.md` (645 files) | ~1.5MB total | The scaffolds themselves |

## Coverage check

Loader's MUST-coverage check is the integrity contract: any curation
change that adds/removes a MUST without updating the corresponding
template fails the loader's parse-time validation. The build gate
forces templates to evolve with curation.

Caught two bugs at load time:
1. Generator's instruction text contained literal `<<MUST item:X>>`
   example — collided with regex; loader flagged it as "unknown MUST
   marker" on every template.
2. Loose `item:[^>\s]+` regex matched the example placeholder.

Both fixed: instruction text reworded, regex tightened to real item-ID
shape `item:[A-Za-z0-9.]+:[a-z0-9_]+`.

## State on Arion

```
templates (645 rows)
  total      : 645
  auto_gen   : 645 (template_version = 1)
  hand_refined: 0  (template_version >= 2)
  MUSTs       : 3388
  SHOULDs     : 891
```

## What's NOT shipped yet (open chunks)

| # | Chunk | Notes |
|---|---|---|
| 3 | Render endpoint `GET /api/v1/templates/{leaf_id}` | Applies `tenant_must_overrides` + ClientFacts auto-fill |
| 4 | Download serving `GET /api/v1/templates/{leaf_id}/download` | Clean `.md` (later `.docx`) |
| 5 | Extractor fast-path for templated uploads | Detect `<<MUST item:X>>` markers; bind deterministically (no LLM) |
| 6 | Hand-refine top ~20 anchor templates | Foundation policies first (ISMS Policy, Scope, Risk, Access Control, etc.) |
| 7 | Neo4j thin `:Template` attachment | `(req)-[:HAS_TEMPLATE]->(t:Template{version})` for graph queries |
| 8 | Tenant journey wizard | Wraps templates into the guided onboarding flow (Profile → Foundation → Operational → Annual) |

## Related

- [[curation-document-templates-idea]] — original idea memory; this
  entry realises it
- [[doc-curation-engine-v1]] — Direction C (per-MUST extractor)
  prerequisite; templates produce the per-MUST-shaped content the
  extractor expects
- [[curation-phase-b-retrospective]] — the curation arc that
  produced the 645 leaves these templates skeleton
- [[feedback-anchor-before-choices]] — applied this session: anchored
  architecture before asking the build-sequence question
