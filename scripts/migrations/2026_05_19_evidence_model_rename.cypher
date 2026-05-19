// =============================================================================
// 2026-05-19  Evidence model rename
//
// Renames:
//   :DocumentRequirement                  -> :EvidenceRequirement
//   :REQUIRES_DOCUMENT                    -> :REQUIRES_EVIDENCE
//   DocumentRequirement.document_type     -> EvidenceRequirement.evidence_type
//   DocumentRequirement.document_title    -> EvidenceRequirement.title
//
// Adds:
//   :FulfilmentSpec  (one per :RequirementNode)
//   :SATISFIED_BY    (RequirementNode -> FulfilmentSpec, 1..1)
//
// Edge sourcing after migration:
//   RequirementNode -[:SATISFIED_BY]-> FulfilmentSpec -[:REQUIRES_EVIDENCE]-> EvidenceRequirement
//   Event           -[:REQUIRES_EVIDENCE]-> EvidenceRequirement       (no spec; direct)
//
// Each phase is idempotent. Safe to re-run.
//
// The Python runner (run_2026_05_19_evidence_model_rename.py) executes these
// phases sequentially and asserts pre/post counts. Direct execution via
// cypher-shell is supported but skips the count assertions.
// =============================================================================


// === PHASE 1: rename label DocumentRequirement -> EvidenceRequirement
MATCH (n:DocumentRequirement)
SET   n:EvidenceRequirement
REMOVE n:DocumentRequirement;


// === PHASE 2a: rename property document_type -> evidence_type
MATCH (n:EvidenceRequirement)
WHERE n.document_type IS NOT NULL
SET    n.evidence_type = n.document_type
REMOVE n.document_type;


// === PHASE 2b: rename property document_title -> title
MATCH (n:EvidenceRequirement)
WHERE n.document_title IS NOT NULL AND n.title IS NULL
SET    n.title = n.document_title
REMOVE n.document_title;


// === PHASE 3: create FulfilmentSpec for every RequirementNode (idempotent)
MATCH (rn:RequirementNode)
WHERE NOT (rn)-[:SATISFIED_BY]->(:FulfilmentSpec)
WITH rn,
     EXISTS { (rn)-[:REQUIRES_DOCUMENT]->() } AS has_legacy_leaves
CREATE (fs:FulfilmentSpec {
    id:              'spec:' + rn.id,
    op:              'ALL',
    n:               NULL,
    applies_when:    NULL,
    curation_status: CASE WHEN has_legacy_leaves THEN 'curated' ELSE 'uncurated' END,
    updated_at:      datetime()
})
CREATE (rn)-[:SATISFIED_BY]->(fs);


// === PHASE 4: move RequirementNode-sourced edges from REQUIRES_DOCUMENT
//              to REQUIRES_EVIDENCE on the spec
MATCH (rn:RequirementNode)-[old:REQUIRES_DOCUMENT]->(er:EvidenceRequirement),
      (rn)-[:SATISFIED_BY]->(fs:FulfilmentSpec)
WHERE NOT (fs)-[:REQUIRES_EVIDENCE]->(er)
CREATE (fs)-[:REQUIRES_EVIDENCE {
    role:         coalesce(old.role, er.evidence_type),
    applies_when: NULL
}]->(er)
DELETE old;


// === PHASE 5: rename Event-sourced edges REQUIRES_DOCUMENT -> REQUIRES_EVIDENCE
//              (Event remains the edge source; no spec in between)
MATCH (e:Event)-[old:REQUIRES_DOCUMENT]->(er:EvidenceRequirement)
WHERE NOT (e)-[:REQUIRES_EVIDENCE]->(er)
CREATE (e)-[:REQUIRES_EVIDENCE]->(er)
WITH old
DELETE old;


// === PHASE 6: add uniqueness constraint on FulfilmentSpec.id
CREATE CONSTRAINT fulfilment_spec_id_unique IF NOT EXISTS
FOR (fs:FulfilmentSpec) REQUIRE fs.id IS UNIQUE;
