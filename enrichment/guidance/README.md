# Per-MUST Guidance

Curator-authored best-practice steps that walk a tenant through
capturing evidence for each `ChecklistItem` (MUST or SHOULD) in the
catalog. Resolved at catalog-load time and written to Neo4j as
`ChecklistItem.guidance`.

Shipped in Ship 56'.a (2026-08-05). Retires the tier machinery from
Ship 55' (Tier 1 exact / Tier 2 prefix / Tier 3 leaf) in favour of a
flat, one-YAML-per-MUST architecture.

## Storage

One YAML per unique MUST id, nested by control ref for browsing:

```
enrichment/guidance/
  4.3/
    boundaries.yaml
    interfaces.yaml
    ...
  5.2/
    owner.yaml
    approved.yaml
    ...
  A.5.15/
    least_privilege.yaml
    ...
  Art.30/
    purposes.yaml
    ...
```

Filename convention: `{control_ref}/{slug}.yaml` where `slug` is the
trailing segment of `must_id` (`item:{control_ref}:{slug}`).

## YAML shape

```yaml
must_id: item:5.2:owner
control_ref: 5.2
standard_id: ISO27001:2022
must_text: "Named owner of the policy (ISMS Manager)"
category: must                  # or "should"
curation_status: draft          # draft | reviewed | approved
authored_by: llm-4o-mini        # generator handle, or curator email
authored_at: "2026-08-05"
guidance:
  - Name a specific person (not "the team") as the policy owner in the document header
  - Confirm they still hold the role — replace with successor if not
  - Document the deputy or backup for continuity when the owner is unavailable
  - Cross-reference the owner in the org chart / RACI so all sources match
```

## Content principles

- **Imperative voice** — steps, not questions. Each guidance line
  reads as an action the tenant should take.
- **Plain English** — no jargon, no auditor-speak, no `snake_case`
  slugs surfaced.
- **3-5 steps per MUST** — enough to guide, not enough to overwhelm.
- **Ends in evidence** — each pack leads the tenant to something an
  auditor could look at.

## Load

```bash
set -a && source .env && set +a && \
  PYTHONPATH=/data/arioncomply python3 enrichment/documents/load_to_neo4j.py
```

The Neo4j loader calls `apply_guidance_to_catalog()` before writing,
which mutates every ChecklistItem's `.guidance` from the matching YAML
(if present). Missing YAMLs ⇒ empty `.guidance` ⇒ renderer suppresses
the `<<GUIDANCE>>` block.

## Related

- `enrichment/guidance/apply_to_catalog.py` — resolver
- `enrichment/documents/document_requirements.py:20-32` — dataclass
- `enrichment/documents/load_to_neo4j.py` — Neo4j write site
- `rag/templates/guidance_lookup.py` — runtime cache used by renderer + API
- Ship 56'.b: LLM generator that populates this directory

## Curation workflow

Each YAML carries `curation_status`:

- `draft` — LLM-generated, not human-reviewed
- `reviewed` — a curator read the guidance and either accepted or
  edited the wording
- `approved` — signed off; treat as authoritative

Coverage stats can be computed as `approved / total` for a maturity
metric.
