# Per-Leaf Prerequisites

Curator-authored prerequisite artefacts that a tenant should have
in place before drafting the target leaf's evidence. Resolved at
catalog-load time and consumed by the template renderer's
`<<PREREQUISITES>>` marker + the Topics/Dashboard drill-in APIs.

Shipped in Ship 57' (2026-08-07). Same architecture as the Ship
56' guidance store.

## Storage

One YAML per leaf, nested by control ref:

```
enrichment/prerequisites/
  4.3/
    isms_scope.yaml
  5.2/
    information_security_policy.yaml
  A.5.15/
    access_control_policy.yaml
  A.7.2.7/
    consent_capture.yaml
  Art.30/
    records_of_processing.yaml
```

Filename convention: `{control_ref}/{evidence_type_slug}.yaml`.

## YAML shape

```yaml
leaf_id: req:A.5.15:access_control_policy
control_ref: A.5.15
standard_id: ISO27001:2022        # PROGRAM
curation_status: draft             # draft | reviewed | approved
authored_by: llm-4.1
authored_at: '2026-08-07'
prerequisites:
  - ref: "4.3"
    standard_id: "ISO27001:2022"
    title: "ISMS Scope Statement"
    category: foundational
    rationale: |
      Access control rules only make sense inside a bounded scope.
      Without a scope statement, the policy will either try to cover
      too much (unfulfillable) or too little (regulator gap).
    good_enough: |
      A signed scope statement naming products, locations, and
      exclusions — no formal ISMS certification required at this stage.
  - ref: "A.5.1"
    standard_id: "ISO27001:2022"
    title: "Policies for Information Security"
    category: direct
    rationale: |
      A.5.15 sits under the A.5.1 policy framework. The framework
      defines document control, approval flow, and policy-owner role
      that A.5.15 inherits.
    good_enough: |
      A published policy framework document naming the policy owner
      role and describing how topic-specific policies fit under it.
```

## Categories

- **`foundational`** — cross-cutting baseline (scope, roles, asset
  register, classification for Program; PIMS scope + role for
  Extension; RoPA + legal basis for Obligation)
- **`direct`** — specific upstream artefact in the same framework
- **`cross_role`** — prereq lives in a different framework role
  than the target leaf (e.g. Extension leaf's Program base clause,
  or an Obligation article that sets the yardstick)

The `standard_id` field carries the framework role of the prereq
(`ISO27001:2022` = Program, `ISO27701:2019` = Extension,
`GDPR:2016/679` = Obligation). The renderer groups by
(role × category) for presentation.

## Content principles

- **Rationale** answers "why does this leaf depend on this prereq?"
  — 1-3 sentences.
- **Good enough** answers "how done does this prereq need to be
  before I can start the current leaf?" — pragmatic threshold,
  not full compliance.
- Plain language, tenant voice, no jargon.

## Load

```bash
set -a && source .env && set +a && \
  PYTHONPATH=/data/arioncomply python3 enrichment/documents/load_to_neo4j.py
```

The Neo4j loader calls `apply_prerequisites_to_catalog()` before
writing. Empty YAMLs ⇒ empty `.prerequisites` ⇒ renderer suppresses
the `<<PREREQUISITES>>` block.

## Related

- `enrichment/prerequisites/apply_to_catalog.py` — resolver
- `enrichment/prerequisites/generate_from_catalog.py` — LLM generator
- `enrichment/documents/document_requirements.py` — `Prerequisite` dataclass + `EvidenceRequirement.prerequisites` field
- `rag/templates/prerequisites_lookup.py` — runtime cache
