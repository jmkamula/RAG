-- schema_v91_ship54a_topics.sql
--
-- Ship 54'.a (2026-08-02) — topic bundles as an ADDITIVE overlay on top
-- of the existing per-leaf template + posture surfaces.
--
-- The user's framing: "preserve per-leaf and bring in topical as an
-- addition". No changes to templates / db/templates/*.md / per-leaf
-- advisory. Topics reference leaves; leaves know nothing about topics.
-- Many-to-many so the same leaf can appear in multiple topics with
-- different roles (e.g., A.5.15 is "primary" in Access Rights Lifecycle
-- but "supporting" in Employee Onboarding).
--
-- Source of truth: db/topics/*.yaml — curator-authored. Loader
-- (enrichment/topics/load_to_postgres.py) syncs → these tables.

BEGIN;

-- One row per topic bundle
CREATE TABLE IF NOT EXISTS topics (
    slug                text        PRIMARY KEY,
    title               text        NOT NULL,
    description         text        NOT NULL,
    -- ISO27001:2022 | GDPR:2016/679 | ISO27701:2019 | multi
    primary_framework   text        NOT NULL,
    -- Narrative for the "what auditors expect from this bundle" surface.
    -- Deliberate consultant-grade text — the LLM won't paraphrase it.
    auditor_expects     text,
    -- Sort key so the dashboard can render topics in a curated order.
    -- Lower = higher priority (0=featured, 100=default). Set per curation.
    display_order       smallint    NOT NULL DEFAULT 100,
    -- Provenance
    source_file         text        NOT NULL,
    last_loaded_at      timestamptz NOT NULL DEFAULT now(),
    last_loaded_by      text
);

-- Many-to-many topic → leaf with per-topic role + ordering
CREATE TABLE IF NOT EXISTS topic_leaves (
    topic_slug          text        NOT NULL REFERENCES topics(slug) ON DELETE CASCADE,
    leaf_id             text        NOT NULL,
    -- Role within THIS topic. Curator-authored, small controlled vocab:
    --   primary_policy | primary_procedure | primary_register
    --   supporting_prerequisite | supporting_iso_mirror | supporting_cross_framework
    --   form | log | review_record | evidence
    -- (Extendable — no CHECK constraint so curator can add roles without
    -- schema migration. Advisory surfaces filter by known values + fall
    -- through on unknown.)
    role                text        NOT NULL,
    -- 1..N ordering within the topic. Two leaves at the same order = ok
    -- (parallel steps). Dashboard/chat renders in workflow_order asc.
    workflow_order      smallint    NOT NULL DEFAULT 100,
    -- Optional per-topic note about how this leaf fits the topic.
    -- Kept short (< 500 chars). Deliberate consultant note.
    role_note           text,
    PRIMARY KEY (topic_slug, leaf_id)
);

CREATE INDEX IF NOT EXISTS idx_topic_leaves_leaf_id
    ON topic_leaves (leaf_id);

CREATE INDEX IF NOT EXISTS idx_topics_display_order
    ON topics (display_order);

-- Note: no FK from topic_leaves.leaf_id → templates.leaf_id because a
-- topic can reference leaves that don't yet have a template scaffold
-- (leaf exists in the catalog but the scaffold hasn't been generated).
-- The loader validates leaf_id against ALL_EVIDENCE_REQUIREMENTS +
-- ALL_DERIVED_SPECS.direct_evidence — the canonical catalog union.

-- Grants — same shape as templates + posture tables
GRANT SELECT, INSERT, UPDATE, DELETE ON topics       TO arioncomply_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON topic_leaves TO arioncomply_app;

COMMIT;
