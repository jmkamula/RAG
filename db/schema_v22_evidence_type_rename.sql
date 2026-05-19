-- =============================================================================
-- schema_v22_evidence_type_rename.sql
--
-- Rename client_documents.document_type → client_documents.evidence_type to
-- align Postgres column with Neo4j EvidenceRequirement.evidence_type after
-- the commit-1 graph rename. The values themselves are unchanged (same
-- vocabulary: 'policy', 'procedure', 'dpa', etc.); only the column name
-- moves so the cross-vocab caveat in incident_fulfillment.py can be dropped.
--
-- client_documents.document_title intentionally stays as-is: it's the
-- artifact's display name (the filename / human-readable title of the
-- uploaded document), not the auditor-facing leaf title that was renamed
-- in Neo4j. Different conceptual things; the name suits the column.
--
-- The index idx_docs_type is also renamed to keep the codebase self-
-- consistent.
--
-- Per [[sql_dry_run_nested_transaction]]: the COMMIT below makes this file
-- self-committing — wrap it in psql's transaction or expect it to land
-- atomically when run alone. Do not rely on an outer BEGIN/ROLLBACK to
-- undo it.
-- =============================================================================

BEGIN;

ALTER TABLE client_documents RENAME COLUMN document_type TO evidence_type;
ALTER INDEX  idx_docs_type    RENAME TO        idx_docs_evidence_type;

COMMIT;
