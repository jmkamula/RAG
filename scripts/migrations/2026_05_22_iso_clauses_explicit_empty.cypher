// =============================================================================
// 2026-05-22  ISO 27001 structural-parent clauses → explicit_empty
//
// Run AFTER enrichment/documents/load_to_neo4j.py to mark the pure structural
// header clauses (those with no obligation text — their substance lives in
// sub-clauses) as explicit_empty so the engine returns Comply for them
// instead of UNKNOWN. The 8 affected clauses are ISO 27001:2022 chapter
// headers and one sub-header (6.1):
//
//   4        Context of the organization
//   5        Leadership
//   6        Planning
//   6.1      Actions to address risks and opportunities
//   7        Support
//   8        Operation
//   9        Performance evaluation
//   10       Improvement
//
// Idempotent — uses SET (no-op if already set).
//
// Background: [[posture-engine-alignment-plan-2026-05-22]] Phase B.
// =============================================================================

MATCH (n:RequirementNode {standard_id: 'ISO27001:2022'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE n.ref IN ['4', '5', '6', '6.1', '7', '8', '9', '10']
SET f.curation_status = 'explicit_empty',
    f.updated_at      = datetime()
RETURN n.ref AS ref, f.curation_status AS curation_status
ORDER BY n.ref;
