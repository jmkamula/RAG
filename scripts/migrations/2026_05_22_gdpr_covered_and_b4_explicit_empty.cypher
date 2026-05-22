// =============================================================================
// 2026-05-22  GDPR COVERED + B4 → explicit_empty (bulk curation closure)
//
// Closes 148 of the 298 uncurated GDPR FulfilmentSpec nodes by marking them
// explicit_empty with a per-cluster reason. The classification mirrors the
// v2 triage at scripts/triage_gdpr_curation.py:
//
//   COVERED (47) — sub-clause of an already-curated parent (Art.13/14/15/28/30/33);
//                  the parent's EvidenceRequirement already captures these as
//                  MUST items, so no separate curation is needed.
//   B4 (101)     — definitional / scope / institutional / transitional articles
//                  with no tenant-side evidence obligation.
//
// After this migration: GDPR uncurated 298 → 150
//   B1 (57)  — direct-evidence, LLM-draft using current model
//   B2 (24)  — implementation-derived, awaits derives_from primitive
//   B3 (38)  — operational / DSR workflows, LLM-draft
//   UNCLASSIFIED (31) — manual review (per 31 rows in
//                       results/triage_gdpr_20260522_1348/unclassified.csv)
//
// Idempotent: every clause filters on curation_status='uncurated' so re-running
// is a no-op for nodes already marked.
//
// Introduces a new convention: FulfilmentSpec.explicit_empty_reason (string).
// Records WHY a spec was marked explicit_empty so the engine and chat surface
// can render attribution ("captured by parent Art.13" beats opaque silence).
//
// Background: [[posture-engine-alignment-plan-2026-05-22]] Phase B.
// =============================================================================


// ──────────────────────────────────────────────────────────────────────────
// SECTION 1 — COVERED: sub-clauses of curated parents
// ──────────────────────────────────────────────────────────────────────────
// Curated GDPR parents today: Art.13, Art.14, Art.15, Art.28, Art.30, Art.33.
// Every uncurated sub-clause whose ref starts with '<parent>.' is captured by
// its parent's checklist MUST items and should not be curated separately.
// Expected: 47 nodes.

MATCH (m:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(fsCur:FulfilmentSpec)
WHERE fsCur.curation_status = 'curated'
WITH collect(m.ref) AS curated_parents

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND any(parent IN curated_parents WHERE parent <> '' AND n.ref STARTS WITH (parent + '.'))
WITH n, f,
     head([parent IN curated_parents WHERE n.ref STARTS WITH (parent + '.') | parent]) AS parent_ref
SET f.curation_status        = 'explicit_empty',
    f.explicit_empty_reason  = 'captured by parent ' + parent_ref,
    f.covered_by_parent_ref  = parent_ref,
    f.updated_at             = datetime()
RETURN 'COVERED' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 2 — B4: Chapter I (Art.1-4) scope and definitions
// ──────────────────────────────────────────────────────────────────────────
// Articles 1-4 define subject matter, material/territorial scope, and the
// canonical defined terms ('personal data', 'controller', 'processor' etc).
// No tenant-side evidence; these are interpretive frames for everything else.

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND n.ref STARTS WITH 'Art.'
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) <= 4
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Chapter I — scope and definitions; no tenant evidence required',
    f.updated_at            = datetime()
RETURN 'B4: Ch I (Art.1-4)' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 3 — B4: Art.11 (processing not requiring identification)
// ──────────────────────────────────────────────────────────────────────────
// Article 11 is a scope rule that *narrows* obligations on the controller
// when identification isn't possible; it does not impose its own evidence
// requirement. Treated as applies_when context for other articles.

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND n.ref STARTS WITH 'Art.11'
  AND (n.ref = 'Art.11' OR n.ref STARTS WITH 'Art.11.')
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Art.11 — scope-narrowing rule for non-identifying processing; no standalone evidence',
    f.updated_at            = datetime()
RETURN 'B4: Art.11' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 4 — B4: Chapter VI (Art.51-59) supervisory authority structure
// ──────────────────────────────────────────────────────────────────────────
// Governs how Member States constitute and empower their supervisory
// authorities. These are state-side obligations, not controller/processor
// evidence requirements.

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND n.ref STARTS WITH 'Art.'
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) >= 51
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) <= 59
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Chapter VI — supervisory authority structure (Member State obligation, not tenant)',
    f.updated_at            = datetime()
RETURN 'B4: Ch VI (Art.51-59)' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 5 — B4: Chapter VII (Art.60-76) cooperation and consistency
// ──────────────────────────────────────────────────────────────────────────
// Governs how supervisory authorities cooperate (one-stop-shop, mutual
// assistance, joint operations) and the European Data Protection Board's
// consistency mechanism. Institutional, not tenant-facing.

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND n.ref STARTS WITH 'Art.'
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) >= 60
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) <= 76
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Chapter VII — supervisory cooperation and consistency (institutional, not tenant)',
    f.updated_at            = datetime()
RETURN 'B4: Ch VII (Art.60-76)' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 6 — B4: Chapter VIII (Art.77-84) remedies, liability, penalties
// ──────────────────────────────────────────────────────────────────────────
// Defines data subjects' rights to complaint/judicial remedy, controller/
// processor liability, and the fine regime. The fines and remedies *apply
// to* tenants but they don't require tenants to produce evidence in their
// own right — they're the consequences of failures evidenced elsewhere.

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND n.ref STARTS WITH 'Art.'
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) >= 77
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) <= 84
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Chapter VIII — remedies, liability, penalties (consequences regime, no evidence to produce)',
    f.updated_at            = datetime()
RETURN 'B4: Ch VIII (Art.77-84)' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 7 — B4: Chapter IX (Art.85-91) specific situations / national law
// ──────────────────────────────────────────────────────────────────────────
// Reconciles GDPR with freedom of expression, public access, employment,
// research, churches' existing data protection rules etc. These are mostly
// derogation hooks for national law to fill in — not direct tenant duties.

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND n.ref STARTS WITH 'Art.'
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) >= 85
  AND toInteger(split(replace(n.ref, 'Art.', ''), '.')[0]) <= 91
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Chapter IX — Member State derogations and specific-situation reconciliation',
    f.updated_at            = datetime()
RETURN 'B4: Ch IX (Art.85-91)' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 8 — B4: definitional text patterns ("'X' means Y", "is defined as")
// ──────────────────────────────────────────────────────────────────────────
// Catches any residual nodes whose obligation_text is a definition or
// scope-statement style that escapes the chapter-range filters above.
// Pattern is tight ("' means " requires the closing quote of a defined term)
// to avoid false positives from "by means of" / "purposes and means".

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND (toLower(coalesce(n.obligation_text,'')) CONTAINS "' means "
       OR toLower(coalesce(n.obligation_text,'')) CONTAINS 'means any'
       OR toLower(coalesce(n.obligation_text,'')) CONTAINS 'is defined as'
       OR toLower(coalesce(n.obligation_text,'')) STARTS WITH 'this regulation'
       OR toLower(coalesce(n.obligation_text,'')) CONTAINS 'subject matter')
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Definitional / scope-statement text; no tenant evidence required',
    f.updated_at            = datetime()
RETURN 'B4: definitional residue' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// SECTION 9 — B4: empty-container nodes (no obligation_text AND no title)
// ──────────────────────────────────────────────────────────────────────────
// Nodes whose content is wholly in their sub-clauses — the parent is a
// pure structural header. Engine should treat these as Comply (substance
// lives in children, not here).

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
WHERE f.curation_status = 'uncurated'
  AND coalesce(n.obligation_text,'') = ''
  AND coalesce(n.title,'') = ''
SET f.curation_status       = 'explicit_empty',
    f.explicit_empty_reason = 'Structural-header node; substance lives in sub-clauses',
    f.updated_at            = datetime()
RETURN 'B4: structural header' AS cluster, count(*) AS n;


// ──────────────────────────────────────────────────────────────────────────
// FINAL VERIFICATION
// ──────────────────────────────────────────────────────────────────────────
// Counts curation_status distribution across GDPR FulfilmentSpecs.
// Expected after this migration:
//   curated         5
//   explicit_empty  148 (47 COVERED + 101 B4)
//   uncurated       150 (57 B1 + 24 B2 + 38 B3 + 31 UNCLASSIFIED)

MATCH (n:RequirementNode {standard_id: 'GDPR:2016/679'})-[:SATISFIED_BY]->(f:FulfilmentSpec)
RETURN f.curation_status AS curation_status, count(*) AS n
ORDER BY curation_status;
