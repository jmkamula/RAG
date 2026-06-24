-- schema_v45_templates.sql — template artefact storage
--
-- Templates are markdown skeletons per EvidenceRequirement leaf that
-- tenants download, edit, and upload back. Each template's body
-- contains <<MUST item:X>> section markers binding the structured
-- text to the leaf's checklist items — enabling deterministic
-- (no-LLM) extraction on the roundtrip.
--
-- Source of truth: db/templates/{leaf_kebab}.md (filesystem,
-- versioned with curation). Loader parses + validates MUST
-- coverage at startup and upserts into this table for runtime
-- serving.
--
-- Auto-generated scaffolds have template_version=1; hand-refined
-- versions get bumped to 2+. The generator preserves any file with
-- template_version >= 2.
--
-- Authored 2026-06-24.

BEGIN;

CREATE TABLE IF NOT EXISTS templates (
    leaf_id          TEXT        NOT NULL PRIMARY KEY,
    -- e.g. 'req:A.5.15:access_control_policy'

    template_version INTEGER     NOT NULL DEFAULT 1,
    -- 1 = auto-generated scaffold; 2+ = hand-refined. Generator
    -- skips files with template_version >= 2 to preserve
    -- hand-refinement across regen runs.

    body_md          TEXT        NOT NULL,
    -- Full markdown body including YAML frontmatter.

    source_file      TEXT        NOT NULL,
    -- Path relative to db/templates/, e.g.
    -- 'req__A_5_15__access_control_policy.md'. Diagnostic for
    -- troubleshooting load failures.

    must_count       INTEGER     NOT NULL DEFAULT 0,
    -- Number of <<MUST item:X>> markers found in body_md.
    -- Loader fails build when this doesn't equal len(leaf.must_contain).

    should_count     INTEGER     NOT NULL DEFAULT 0,
    -- Number of <<SHOULD item:X>> markers (advisory; not a build gate).

    last_loaded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_loaded_by   TEXT,
    -- Provenance — typically 'load_to_postgres.py' or 'manual_upsert'.

    CONSTRAINT templates_version_ge_1 CHECK (template_version >= 1),
    CONSTRAINT templates_counts_nonneg CHECK (must_count >= 0 AND should_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_templates_version ON templates(template_version);

COMMENT ON TABLE  templates IS
    'Markdown template skeletons per EvidenceRequirement leaf; canonical source is db/templates/*.md filesystem; this table is the runtime-serving copy.';
COMMENT ON COLUMN templates.leaf_id IS
    'EvidenceRequirement.id — e.g. req:A.5.15:access_control_policy';
COMMENT ON COLUMN templates.template_version IS
    'Auto-gen scaffolds=1; hand-refined=2+. Generator preserves files with version >= 2.';
COMMENT ON COLUMN templates.must_count IS
    'Count of <<MUST item:X>> markers in body; loader enforces equality with leaf.must_contain length.';

COMMIT;
