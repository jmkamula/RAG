"""
ArionComply — Unified Relationship Catalog

Single source of truth for typed edges in the obligation graph.
Loaded into Neo4j by `load_to_neo4j.py` (idempotent + declarative
orphan pruning, same pattern as the document catalog loader).

See:
  /data/arioncomply/docs/relationship_model_design_2026_06_29.md
  /data/arioncomply/docs/relationship_model_audit_2026_06_29.md

Edge types managed by THIS catalog (only the 6 new intra-framework
types at S1; cross-framework + composition + applicability are
still loaded by their existing loaders. S4 will migrate the
cross-framework edges here):

  PAIRS_WITH       — bidirectional lifecycle coupling
  PREREQUISITE_OF  — A must exist before B is meaningful (directional)
  ESCALATES_TO     — severity/scope expansion path (directional)
  CASCADES_FROM    — property inheritance from parent (directional)
  FEEDS_INTO       — output of A is input to B's operation (directional)
  AUDITED_BY       — independent verification (directional, target audits source)

S1 ships with ZERO edges. Authoring of intra-framework edges from
the curation memo corpus + ISO 27002 cross-references is S5-S6.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# Edge types this catalog owns. New edge types must be added here
# AND the loader must be updated to MERGE / prune them.
#
# S6 (intra-framework): PAIRS_WITH / PREREQUISITE_OF / ESCALATES_TO /
#                       CASCADES_FROM / FEEDS_INTO / AUDITED_BY
# S2b (cascade-suppression): BLOCKS_WHEN
#   Source: RequirementNode (an obligation).
#   Target: RequirementNode OR ClientFact representing a suppression
#           condition. Semantics: when target's state matches the
#           authored applies_when, the source obligation is SUPPRESSED
#           (does not fire from a cascade). Example: A.5.33 retention
#           expiry BLOCKS_WHEN A.5.31:legal_hold_active. Reserved at
#           S2b — no edges authored yet, awaits curation pass.
MANAGED_EDGE_TYPES = (
    "PAIRS_WITH",
    "PREREQUISITE_OF",
    "ESCALATES_TO",
    "CASCADES_FROM",
    "FEEDS_INTO",
    "AUDITED_BY",
    "BLOCKS_WHEN",
    # S4: cross-framework edges migrated from iso/gdpr source JSONs.
    # Owned by relationship_catalog after S4 — load_graph_relationships
    # cross-framework section deprecated.
    "IMPLEMENTS",
    "SUPPORTS",
    "ENABLES",
    "GOVERNANCE",
)

# Edge types that are SYMMETRIC — loader writes both directions.
# All others are directional (a→b only).
SYMMETRIC_EDGE_TYPES = (
    "PAIRS_WITH",
)

# Recognised standard ids — keep in sync with the catalog's
# RequirementNode population. Loader rejects unknown standards.
KNOWN_STANDARD_IDS = (
    "ISO27001:2022",
    "GDPR:2016/679",
    "ISO27701:2019",
)


@dataclass(frozen=True)
class RelationshipEdge:
    """One authored relationship between two controls/articles.

    For symmetric edge types (PAIRS_WITH), author the row ONCE.
    Loader writes both directions in Neo4j.
    """

    source_ref: str
    # Control/article ref WITHIN its standard, e.g. 'A.5.16' / 'Art.32'
    source_standard_id: str
    # Must be in KNOWN_STANDARD_IDS

    target_ref: str
    target_standard_id: str

    edge_type: str
    # Must be in MANAGED_EDGE_TYPES

    rationale: Optional[str] = None
    # 1-sentence why this relationship exists; appears in auditor-facing
    # surfaces + chat answers

    citation: Optional[str] = None
    # Reference, e.g. 'ISO27002:2022 §5.17' / 'GDPR Art.19' /
    # 'EDPB 4/2019 §3.2'. STRONGLY RECOMMENDED — validator warns
    # if absent so reviewers can spot-check.

    role: Optional[str] = None
    # Optional sub-typing, e.g. PAIRS_WITH with role='lifecycle'
    # vs role='topical'. Keeps edge-type list small while preserving
    # semantic specificity.

    applies_when: Optional[str] = None
    # Optional applicability gate. Same DSL as the existing
    # applies_when used in DerivedSpec — engine-side evaluation
    # (deferred until first edge needs it).

    def source_node_id(self) -> str:
        """Full Neo4j RequirementNode id for the source."""
        return f"{self.source_standard_id}:{self.source_ref}"

    def target_node_id(self) -> str:
        """Full Neo4j RequirementNode id for the target."""
        return f"{self.target_standard_id}:{self.target_ref}"


# ── Authored edges ────────────────────────────────────────────────────────
# Empty at S1. Authoring of the 669 candidate intra-framework pairs
# (from the audit's curation-memo mining) is S5-S6.

# ── Intra-ISO 27001 edges (S6, first batch) ───────────────────────────
# High-confidence clusters from the audit. Each edge cites either:
#   - ISO27002:2022 §X.Y (the implementation-guidance standard;
#     copyrighted, so only the section reference is included)
#   - A specific curation batch memo (already part of our corpus)
#   - ISO 27001:2022 clause text (for ISMS clause chain edges)
#
# Clusters covered in this batch:
#   1. Identity lifecycle (A.5.11/16/17/18 + A.6.5 contractual layer)
#   2. Incident family (A.5.7/24/25/26/27/28)
#   3. BCP pair (A.5.29/30 + threat-intel + IR framework feeds)
#   4. Records protection (A.5.31/32/33/34/35/36)
#   5. Classification cascade (A.5.9/10/12/13 + A.7.10/14)
#   6. People controls contractual (A.6.x → A.5.x offboarding)
#   7. Physical-to-cyber bridges (A.7.4/5/11/14 → A.5.x)
#   8. Supplier chain (A.5.19/20/21/22/23)
#   9. Information transfer (A.5.14)
#  10. Project security (A.5.8)
#  11. ISMS clause chain (4.x/5.x/6.1.x/9.2/10.x)
#  12. Compliance review (A.5.36 audits policy controls)

INTRA_ISO_EDGES: list[RelationshipEdge] = [

    # ── 1. Identity lifecycle ─────────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.16', source_standard_id='ISO27001:2022',
        target_ref='A.5.17', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Identity record + credential record share a lifecycle; '
                  'disabling one without the other leaves stale auth material.',
        citation='ISO27002:2022 §5.17 references §5.16',
        role='lifecycle',
    ),
    RelationshipEdge(
        source_ref='A.5.16', source_standard_id='ISO27001:2022',
        target_ref='A.5.18', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Identity changes drive access-rights review/revocation '
                  'in the same cycle.',
        citation='ISO27002:2022 §5.18 references §5.16',
        role='lifecycle',
    ),
    RelationshipEdge(
        source_ref='A.5.17', source_standard_id='ISO27001:2022',
        target_ref='A.5.18', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Authentication info changes (password reset, key rotation) '
                  'should align with access-rights review.',
        citation='ISO27002:2022 §5.17 + §5.18',
        role='lifecycle',
    ),
    RelationshipEdge(
        source_ref='A.5.11', source_standard_id='ISO27001:2022',
        target_ref='A.5.16', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Asset return and identity revocation are siblings in the '
                  'offboarding sequence — both fired by the same leaver event.',
        citation='ISO27002:2022 §5.11 + §5.16',
        role='offboarding',
    ),
    RelationshipEdge(
        source_ref='A.6.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.11', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Post-employment terms (A.6.5) frame and authorise the '
                  'A.5.11 return-of-assets operational step.',
        citation='ISO27002:2022 §6.5; curation batch 21',
    ),
    RelationshipEdge(
        source_ref='A.6.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.16', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Post-employment contractual obligations frame identity '
                  'revocation timeliness expectations.',
        citation='ISO27002:2022 §6.5; curation batch 21',
    ),
    RelationshipEdge(
        source_ref='A.6.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.17', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Post-employment contractual layer above credential revocation.',
        citation='ISO27002:2022 §6.5; curation batch 21',
    ),
    RelationshipEdge(
        source_ref='A.6.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.18', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Post-employment contractual layer above access-rights revocation.',
        citation='ISO27002:2022 §6.5; curation batch 21',
    ),

    # ── 2. Incident family ────────────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.24', source_standard_id='ISO27001:2022',
        target_ref='A.5.25', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Incident management framework (planning) sits above the '
                  'operational triage step — no meaningful triage without prior planning.',
        citation='ISO27002:2022 §5.24 → §5.25; curation batch 14',
    ),
    RelationshipEdge(
        source_ref='A.5.25', source_standard_id='ISO27001:2022',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='ESCALATES_TO',
        rationale='Triage decision elevates the event into the incident '
                  'register for tracked response.',
        citation='ISO27002:2022 §5.25 → §5.26',
    ),
    RelationshipEdge(
        source_ref='A.5.26', source_standard_id='ISO27001:2022',
        target_ref='A.5.27', target_standard_id='ISO27001:2022',
        edge_type='ESCALATES_TO',
        rationale='Closed incidents are reviewed for lessons learned.',
        citation='ISO27002:2022 §5.26 → §5.27',
    ),
    RelationshipEdge(
        source_ref='A.5.27', source_standard_id='ISO27001:2022',
        target_ref='A.5.24', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Lessons-learned outputs feed back into IR framework refinement.',
        citation='ISO27002:2022 §5.27 + §5.24',
    ),
    RelationshipEdge(
        source_ref='A.5.7', source_standard_id='ISO27001:2022',
        target_ref='A.5.25', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Threat intelligence signals feed the triage decision.',
        citation='ISO27002:2022 §5.7 + §5.25; curation batch 5',
    ),
    RelationshipEdge(
        source_ref='A.5.7', source_standard_id='ISO27001:2022',
        target_ref='A.5.24', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Threat intelligence informs incident-response planning assumptions.',
        citation='ISO27002:2022 §5.7 + §5.24',
    ),
    RelationshipEdge(
        source_ref='A.5.26', source_standard_id='ISO27001:2022',
        target_ref='A.5.28', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Closed incidents generate evidence for retention/disposal under A.5.28.',
        citation='ISO27002:2022 §5.26 + §5.28; curation batch 6',
    ),

    # ── 3. BCP / ICT readiness ────────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.29', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Disruption (general BCP) and ICT readiness are paired '
                  'continuity controls — A.5.30 is the ICT-specific counterpart.',
        citation='ISO27002:2022 §5.30 introduced as ICT-specific §5.29 counterpart',
        role='bcp_pair',
    ),
    RelationshipEdge(
        source_ref='A.5.24', source_standard_id='ISO27001:2022',
        target_ref='A.5.29', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='IR framework and BCP plans coordinate scope and activation '
                  'criteria — incident escalation may invoke disruption response.',
        citation='ISO27002:2022 §5.29 + §5.24; curation batch 15',
        role='response_coordination',
    ),
    RelationshipEdge(
        source_ref='A.5.7', source_standard_id='ISO27001:2022',
        target_ref='A.5.29', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Threat intelligence informs BCP scenarios and trigger criteria.',
        citation='ISO27002:2022 §5.7 + §5.29; curation batch 15',
    ),

    # ── 4. Records protection ─────────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Records protection (A.5.33) and PII protection (A.5.34) — '
                  'latter is the PII-specific overlay of the former.',
        citation='ISO27002:2022 §5.34 introduced as PII subset of §5.33',
        role='records_protection',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Legal/regulatory requirements register (A.5.31) scopes '
                  'retention and protection obligations applied in A.5.33.',
        citation='ISO27002:2022 §5.31 + §5.33',
    ),
    RelationshipEdge(
        source_ref='A.5.32', source_standard_id='ISO27001:2022',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='IPR register (A.5.32) and records protection (A.5.33) — '
                  'IPR is one category of records requiring specific handling.',
        citation='ISO27002:2022 §5.32 + §5.33',
        role='records_categorisation',
    ),
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='A.5.35', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Independent review (A.5.35) covers records-protection program operation.',
        citation='ISO27002:2022 §5.35 scope; curation batch 19',
    ),
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Compliance review (A.5.36) verifies records-protection adherence.',
        citation='ISO27002:2022 §5.36 scope; curation batch 19',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='A.5.35', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Independent review covers PII protection program operation.',
        citation='ISO27002:2022 §5.35 scope',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Compliance review verifies PII protection adherence.',
        citation='ISO27002:2022 §5.36 scope',
    ),
    RelationshipEdge(
        source_ref='A.5.35', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Independent review and compliance review programs share '
                  'finding registers and can coordinate scope.',
        citation='ISO27002:2022 §5.35 + §5.36; curation batch 19',
        role='review_coordination',
    ),

    # ── 5. Classification cascade ─────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='A.5.12', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Asset inventory must exist before assets can be classified.',
        citation='ISO27002:2022 §5.12 implies §5.9',
    ),
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='A.5.13', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Classification scheme must exist before labels can be applied.',
        citation='ISO27002:2022 §5.13 references §5.12',
    ),
    RelationshipEdge(
        source_ref='A.5.13', source_standard_id='ISO27001:2022',
        target_ref='A.5.12', target_standard_id='ISO27001:2022',
        edge_type='CASCADES_FROM',
        rationale='Labelling review cadence + scope inherits from parent '
                  'classification scheme — changes to scheme propagate to labels.',
        citation='Curation batch 10',
        role='cadence_inheritance',
    ),
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='A.5.10', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Acceptable-use rules (A.5.10) reference classification levels — '
                  'must know the scheme before authoring AUP differentials.',
        citation='ISO27002:2022 §5.10 references classification',
    ),
    RelationshipEdge(
        source_ref='A.5.13', source_standard_id='ISO27001:2022',
        target_ref='A.7.10', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Media handling rules depend on label being applied — '
                  'unlabelled media cannot be handled per its sensitivity.',
        citation='ISO27002:2022 §7.10 + §5.13',
    ),
    RelationshipEdge(
        source_ref='A.7.10', source_standard_id='ISO27001:2022',
        target_ref='A.7.14', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Media handling rules feed disposal procedures — disposal '
                  'requires knowing what was on the media.',
        citation='ISO27002:2022 §7.14 references §7.10',
    ),
    RelationshipEdge(
        source_ref='A.7.14', source_standard_id='ISO27001:2022',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Equipment disposal events update the asset register.',
        citation='ISO27002:2022 §7.14 + §5.9; curation batch 22',
    ),

    # ── 6. People controls contractual layer ──────────────────────────
    RelationshipEdge(
        source_ref='A.6.1', source_standard_id='ISO27001:2022',
        target_ref='A.6.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Screening (A.6.1) precedes terms of employment (A.6.2) — '
                  'screening outcome informs offer + contract.',
        citation='ISO27002:2022 §6.1 + §6.2',
    ),
    RelationshipEdge(
        source_ref='A.6.2', source_standard_id='ISO27001:2022',
        target_ref='A.6.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Terms-of-employment signing precedes information-security '
                  'training (training framing typically tied to onboarding contract).',
        citation='ISO27002:2022 §6.2 + §6.3; curation batch 21',
    ),
    RelationshipEdge(
        source_ref='A.6.2', source_standard_id='ISO27001:2022',
        target_ref='A.6.6', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Terms of employment and confidentiality NDA (A.6.6) are '
                  'co-signed as the personnel info-security contract package.',
        citation='ISO27002:2022 §6.2 + §6.6; curation batch 21',
        role='employment_contract',
    ),
    RelationshipEdge(
        source_ref='A.6.8', source_standard_id='ISO27001:2022',
        target_ref='A.5.25', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Information security event reporting (A.6.8) feeds incident triage.',
        citation='ISO27002:2022 §6.8 + §5.25; curation batch 21',
    ),

    # ── 7. Physical-to-cyber bridges ──────────────────────────────────
    RelationshipEdge(
        source_ref='A.7.4', source_standard_id='ISO27001:2022',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Physical-entry monitoring outputs feed the SIEM / incident register.',
        citation='ISO27002:2022 §7.4 + §5.26; curation batch 22',
    ),
    RelationshipEdge(
        source_ref='A.7.4', source_standard_id='ISO27001:2022',
        target_ref='A.5.25', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Physical-entry alarms feed incident triage decisions.',
        citation='ISO27002:2022 §7.4 + §5.25',
    ),
    RelationshipEdge(
        source_ref='A.7.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Protection against physical and environmental threats (A.7.5) '
                  'feeds ICT readiness assumptions about facility hazards.',
        citation='ISO27002:2022 §7.5 + §5.30; curation batch 22',
    ),
    RelationshipEdge(
        source_ref='A.7.11', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Supporting utilities monitoring feeds ICT readiness BIA.',
        citation='ISO27002:2022 §7.11 + §5.30; curation batch 22',
    ),

    # ── 8. Supplier chain ─────────────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.19', source_standard_id='ISO27001:2022',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Supplier-relationship policy frames the contractual terms '
                  'authored in A.5.20 supplier agreements.',
        citation='ISO27002:2022 §5.19 + §5.20',
    ),
    RelationshipEdge(
        source_ref='A.5.20', source_standard_id='ISO27001:2022',
        target_ref='A.5.21', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Supplier agreements enable ICT supply-chain risk management.',
        citation='ISO27002:2022 §5.20 + §5.21',
    ),
    RelationshipEdge(
        source_ref='A.5.21', source_standard_id='ISO27001:2022',
        target_ref='A.5.22', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='ICT supplier register enables periodic monitoring/review.',
        citation='ISO27002:2022 §5.21 + §5.22',
    ),
    RelationshipEdge(
        source_ref='A.5.22', source_standard_id='ISO27001:2022',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Supplier review outputs feed future agreement renegotiations.',
        citation='ISO27002:2022 §5.22 + §5.20',
    ),
    RelationshipEdge(
        source_ref='A.5.23', source_standard_id='ISO27001:2022',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Cloud-services security (A.5.23) is a sub-class of supplier '
                  'relationship — shares policy framework but adds cloud-specific terms.',
        citation='ISO27002:2022 §5.23 + §5.19',
        role='cloud_specialisation',
    ),

    # ── 9. Information transfer ───────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.14', source_standard_id='ISO27001:2022',
        target_ref='A.5.13', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Information transfer rules depend on classification labels '
                  'being applied — unlabelled info cannot be transferred per sensitivity.',
        citation='ISO27002:2022 §5.14 + §5.13; curation batch 11',
    ),

    # ── 10. Project security ──────────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.8', source_standard_id='ISO27001:2022',
        target_ref='A.8.25', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Project-security gates feed secure SDLC requirements.',
        citation='ISO27002:2022 §5.8 + §8.25; curation batch 8',
    ),
    RelationshipEdge(
        source_ref='A.5.8', source_standard_id='ISO27001:2022',
        target_ref='A.8.26', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Project-security requirements drive application-security architecture.',
        citation='ISO27002:2022 §5.8 + §8.26; curation batch 8',
    ),
    RelationshipEdge(
        source_ref='A.5.8', source_standard_id='ISO27001:2022',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Project-security requirements drive supplier engagement when '
                  'projects involve third parties.',
        citation='ISO27002:2022 §5.8 + §5.20; curation batch 8',
    ),

    # ── 11. ISMS clause chain ─────────────────────────────────────────
    RelationshipEdge(
        source_ref='4.1', source_standard_id='ISO27001:2022',
        target_ref='4.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Understanding context (4.1) and interested parties (4.2) '
                  'must precede ISMS scope determination (4.3).',
        citation='ISO27001:2022 cl. 4.3 references 4.1 + 4.2',
        role='isms_scope_chain',
    ),
    RelationshipEdge(
        source_ref='4.2', source_standard_id='ISO27001:2022',
        target_ref='4.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Interested-party expectations inform ISMS scope.',
        citation='ISO27001:2022 cl. 4.3 references 4.2',
        role='isms_scope_chain',
    ),
    RelationshipEdge(
        source_ref='4.3', source_standard_id='ISO27001:2022',
        target_ref='4.4', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='ISMS scope determination precedes the ISMS itself.',
        citation='ISO27001:2022 cl. 4.4 builds on 4.3',
    ),
    RelationshipEdge(
        source_ref='5.1', source_standard_id='ISO27001:2022',
        target_ref='5.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Leadership commitment frames the information-security policy.',
        citation='ISO27001:2022 cl. 5.2 ("top management shall establish")',
    ),
    RelationshipEdge(
        source_ref='5.2', source_standard_id='ISO27001:2022',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Information-security policy frames the risk-assessment approach.',
        citation='ISO27001:2022 cl. 5.2 + 6.1.2',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='6.1.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Risk assessment outputs drive risk treatment selection.',
        citation='ISO27001:2022 cl. 6.1.3 references 6.1.2',
        role='risk_chain',
    ),
    RelationshipEdge(
        source_ref='9.2', source_standard_id='ISO27001:2022',
        target_ref='10.1', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Internal audit findings drive nonconformity identification.',
        citation='ISO27001:2022 cl. 9.2 + 10.1',
    ),
    RelationshipEdge(
        source_ref='10.1', source_standard_id='ISO27001:2022',
        target_ref='10.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Nonconformity identification precedes continual improvement actions.',
        citation='ISO27001:2022 cl. 10.2 builds on 10.1',
    ),
    RelationshipEdge(
        source_ref='9.3', source_standard_id='ISO27001:2022',
        target_ref='10.2', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Management review outputs feed continual improvement.',
        citation='ISO27001:2022 cl. 9.3 + 10.2',
    ),
    RelationshipEdge(
        source_ref='9.1', source_standard_id='ISO27001:2022',
        target_ref='9.3', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Monitoring/measurement outputs feed management review.',
        citation='ISO27001:2022 cl. 9.3 inputs from 9.1',
    ),

    # ── 12. Compliance review (A.5.36 audits policy controls) ─────────
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Policy framework adherence verified via compliance review.',
        citation='ISO27002:2022 §5.36 scope',
    ),
    RelationshipEdge(
        source_ref='A.5.4', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Management responsibility / segregation verified via compliance review.',
        citation='ISO27002:2022 §5.36 scope',
    ),
    RelationshipEdge(
        source_ref='9.2', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Internal audit scope often relies on the compliance-review '
                  'program findings as audit-evidence input.',
        citation='ISO27001:2022 cl. 9.2 + ISO27002:2022 §5.36',
    ),

    # ── S6 batch 2: secondary clusters ────────────────────────────────
    # Policy framework downstream, governance cluster, lessons-learned
    # outflow, technological neighbourhoods (network, app sec, logging,
    # backup, crypto), training/discipline links.

    # ── 13. Policy framework (A.5.1) downstream ───────────────────────
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.10', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='AUP (A.5.10) derives from the parent information-security policy framework.',
        citation='ISO27002:2022 §5.10 ("based on the information security policy")',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.12', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Classification scheme is one of the topic-specific policies the framework authorises.',
        citation='ISO27002:2022 §5.1 + §5.12',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Supplier-relationship policy sits under the parent framework.',
        citation='ISO27002:2022 §5.1 + §5.19',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Information-transfer policy sits under the parent framework.',
        citation='ISO27002:2022 §5.1 + §5.14',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.15', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Access control policy is a topic-specific policy under the framework.',
        citation='ISO27002:2022 §5.15 (topic-specific access control policy)',
    ),

    # ── 14. Governance cluster (A.5.2-6) ──────────────────────────────
    RelationshipEdge(
        source_ref='A.5.2', source_standard_id='ISO27001:2022',
        target_ref='A.5.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Information-security roles & responsibilities define who '
                  'segregates from whom — segregation depends on assigned roles.',
        citation='ISO27002:2022 §5.2 + §5.3',
    ),
    RelationshipEdge(
        source_ref='A.5.3', source_standard_id='ISO27001:2022',
        target_ref='A.8.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Segregation of duties (A.5.3) is operationalised in privileged-access '
                  'design (A.8.2) — no admin pair, no two-person controls.',
        citation='ISO27002:2022 §5.3 + §8.2',
    ),
    RelationshipEdge(
        source_ref='A.5.2', source_standard_id='ISO27001:2022',
        target_ref='A.5.4', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Roles & responsibilities precede management commitment to '
                  'enforcing them.',
        citation='ISO27002:2022 §5.2 + §5.4',
    ),
    RelationshipEdge(
        source_ref='A.5.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.6', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Contacts with authorities + contacts with special-interest groups — '
                  'parallel external-relationship registers maintained together.',
        citation='ISO27002:2022 §5.5 + §5.6',
        role='external_contacts',
    ),
    RelationshipEdge(
        source_ref='A.5.5', source_standard_id='ISO27001:2022',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Authority contacts are needed for incident response — '
                  'register feeds incident escalation paths.',
        citation='ISO27002:2022 §5.5 + §5.26',
    ),

    # ── 15. Lessons-learned outflow (A.5.27) ──────────────────────────
    RelationshipEdge(
        source_ref='A.5.27', source_standard_id='ISO27001:2022',
        target_ref='A.5.7', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Lessons-learned outputs feed threat-intel signal updates.',
        citation='ISO27002:2022 §5.27 + §5.7',
    ),
    RelationshipEdge(
        source_ref='A.5.27', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Lessons-learned findings inform compliance-review program scope.',
        citation='ISO27002:2022 §5.27 + §5.36',
    ),
    RelationshipEdge(
        source_ref='A.5.27', source_standard_id='ISO27001:2022',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Lessons-learned inputs feed risk-assessment updates (new threats, '
                  'new vulnerabilities surfaced).',
        citation='ISO27001:2022 cl. 6.1.2 + ISO27002:2022 §5.27',
    ),

    # ── 16. Legal/regulatory cascade (A.5.31) ─────────────────────────
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Legal register feeds PII-protection obligations — privacy law '
                  'scope drives A.5.34 program design.',
        citation='ISO27002:2022 §5.31 + §5.34',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Legal-register obligations cascade into supplier agreement clauses.',
        citation='ISO27002:2022 §5.31 + §5.20',
    ),

    # ── 17. Network controls (A.8.20-23) ──────────────────────────────
    RelationshipEdge(
        source_ref='A.8.20', source_standard_id='ISO27001:2022',
        target_ref='A.8.21', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Network security baseline frames per-service hardening.',
        citation='ISO27002:2022 §8.20 + §8.21',
    ),
    RelationshipEdge(
        source_ref='A.8.20', source_standard_id='ISO27001:2022',
        target_ref='A.8.22', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Network-security baseline frames the segmentation strategy.',
        citation='ISO27002:2022 §8.20 + §8.22',
    ),
    RelationshipEdge(
        source_ref='A.8.20', source_standard_id='ISO27001:2022',
        target_ref='A.8.23', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Network-security baseline frames web-filtering policy.',
        citation='ISO27002:2022 §8.20 + §8.23',
    ),

    # ── 18. Application security (A.8.25-29) ──────────────────────────
    RelationshipEdge(
        source_ref='A.8.25', source_standard_id='ISO27001:2022',
        target_ref='A.8.26', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Secure-development lifecycle frames application-security requirements.',
        citation='ISO27002:2022 §8.25 + §8.26',
    ),
    RelationshipEdge(
        source_ref='A.8.25', source_standard_id='ISO27001:2022',
        target_ref='A.8.27', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Secure-development lifecycle establishes the security-architecture principles.',
        citation='ISO27002:2022 §8.25 + §8.27',
    ),
    RelationshipEdge(
        source_ref='A.8.25', source_standard_id='ISO27001:2022',
        target_ref='A.8.28', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='SDLC mandates secure-coding standards.',
        citation='ISO27002:2022 §8.25 + §8.28',
    ),
    RelationshipEdge(
        source_ref='A.8.25', source_standard_id='ISO27001:2022',
        target_ref='A.8.29', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='SDLC mandates security testing within development.',
        citation='ISO27002:2022 §8.25 + §8.29',
    ),
    RelationshipEdge(
        source_ref='A.8.31', source_standard_id='ISO27001:2022',
        target_ref='A.8.25', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Separation of development/test/production environments is '
                  'an SDLC enabler — no separated environments, no controlled lifecycle.',
        citation='ISO27002:2022 §8.31 + §8.25',
    ),
    RelationshipEdge(
        source_ref='A.8.32', source_standard_id='ISO27001:2022',
        target_ref='A.8.25', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Change management (A.8.32) and secure development are sibling '
                  'controls; major changes go through SDLC, SDLC changes go through CM.',
        citation='ISO27002:2022 §8.32 + §8.25',
        role='change_lifecycle',
    ),
    RelationshipEdge(
        source_ref='A.8.33', source_standard_id='ISO27001:2022',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Test information protection requires the information-deletion '
                  'mechanism — test data must be deletable per lifecycle rules.',
        citation='ISO27002:2022 §8.33 + §8.10',
    ),

    # ── 19. Logging + monitoring (A.8.15-17) ──────────────────────────
    RelationshipEdge(
        source_ref='A.8.15', source_standard_id='ISO27001:2022',
        target_ref='A.8.16', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Logging is the prerequisite for monitoring — no logs, no monitoring.',
        citation='ISO27002:2022 §8.15 + §8.16',
    ),
    RelationshipEdge(
        source_ref='A.8.17', source_standard_id='ISO27001:2022',
        target_ref='A.8.15', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Clock synchronisation underpins log integrity for cross-system correlation.',
        citation='ISO27002:2022 §8.17 + §8.15',
    ),
    RelationshipEdge(
        source_ref='A.8.16', source_standard_id='ISO27001:2022',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Monitoring outputs feed the incident register.',
        citation='ISO27002:2022 §8.16 + §5.26',
    ),
    RelationshipEdge(
        source_ref='A.8.15', source_standard_id='ISO27001:2022',
        target_ref='A.5.27', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Logs are evidence input for lessons-learned reviews.',
        citation='ISO27002:2022 §8.15 + §5.27',
    ),

    # ── 20. Backup + redundancy (A.8.13-14) ───────────────────────────
    RelationshipEdge(
        source_ref='A.8.13', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Backup capability feeds ICT-readiness RTO/RPO commitments.',
        citation='ISO27002:2022 §8.13 + §5.30',
    ),
    RelationshipEdge(
        source_ref='A.8.14', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Redundancy capacity feeds ICT-readiness continuity scenarios.',
        citation='ISO27002:2022 §8.14 + §5.30',
    ),
    RelationshipEdge(
        source_ref='A.8.13', source_standard_id='ISO27001:2022',
        target_ref='A.8.14', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Backup + redundancy together compose the resilience baseline.',
        citation='ISO27002:2022 §8.13 + §8.14',
        role='resilience',
    ),

    # ── 21. Cryptography (A.8.24) ─────────────────────────────────────
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Classification levels drive cryptographic-protection requirements.',
        citation='ISO27002:2022 §5.12 + §8.24',
    ),
    RelationshipEdge(
        source_ref='A.8.24', source_standard_id='ISO27001:2022',
        target_ref='A.5.10', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Cryptography rules feed AUP — what users may/may-not do '
                  'with keys and crypto-enabled assets.',
        citation='ISO27002:2022 §8.24 + §5.10',
    ),

    # ── 22. Vulnerability + patch + configuration (A.8.7-9) ───────────
    RelationshipEdge(
        source_ref='A.8.8', source_standard_id='ISO27001:2022',
        target_ref='A.5.7', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Vulnerability management consumes threat intelligence; threat '
                  'intelligence consumes vulnerability landscape — bidirectional.',
        citation='ISO27002:2022 §8.8 + §5.7',
        role='vuln_intel',
    ),
    RelationshipEdge(
        source_ref='A.8.8', source_standard_id='ISO27001:2022',
        target_ref='A.8.32', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Vulnerability findings trigger change-management remediation flow.',
        citation='ISO27002:2022 §8.8 + §8.32',
    ),
    RelationshipEdge(
        source_ref='A.8.9', source_standard_id='ISO27001:2022',
        target_ref='A.8.8', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Configuration baselines enable meaningful vulnerability assessment.',
        citation='ISO27002:2022 §8.9 + §8.8',
    ),

    # ── 23. Training + discipline + AUP links ─────────────────────────
    RelationshipEdge(
        source_ref='A.6.3', source_standard_id='ISO27001:2022',
        target_ref='A.5.10', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Training reinforces AUP rules — AUP frames the training content.',
        citation='ISO27002:2022 §6.3 + §5.10',
        role='awareness_pair',
    ),
    RelationshipEdge(
        source_ref='A.6.3', source_standard_id='ISO27001:2022',
        target_ref='A.6.8', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Training equips personnel to recognise + report events; '
                  'training-content authors use real reports as scenarios.',
        citation='ISO27002:2022 §6.3 + §6.8',
        role='awareness_pair',
    ),
    RelationshipEdge(
        source_ref='A.6.3', source_standard_id='ISO27001:2022',
        target_ref='A.5.13', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Training covers labelling practice; ensures correct application.',
        citation='ISO27002:2022 §6.3 + §5.13',
    ),
    RelationshipEdge(
        source_ref='A.5.36', source_standard_id='ISO27001:2022',
        target_ref='A.6.4', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Compliance-review findings can trigger the A.6.4 disciplinary process.',
        citation='ISO27002:2022 §5.36 + §6.4',
    ),

    # ── 24. Evidence handling outflow (A.5.28) ────────────────────────
    RelationshipEdge(
        source_ref='A.5.28', source_standard_id='ISO27001:2022',
        target_ref='9.2', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Internal audit (9.2) needs evidence retained per A.5.28 chain-of-custody.',
        citation='ISO27001:2022 cl. 9.2 + ISO27002:2022 §5.28',
    ),
    RelationshipEdge(
        source_ref='A.5.28', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Compliance review draws on evidence preserved per A.5.28.',
        citation='ISO27002:2022 §5.28 + §5.36',
    ),

    # ── 25. Access controls (A.5.15 → A.5.18 + A.8.2/3/4/5) ──────────
    RelationshipEdge(
        source_ref='A.5.15', source_standard_id='ISO27001:2022',
        target_ref='A.5.18', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Access-control policy frames the access-rights mechanism — '
                  'no policy, no scoped grants.',
        citation='ISO27002:2022 §5.15 + §5.18',
    ),
    RelationshipEdge(
        source_ref='A.5.15', source_standard_id='ISO27001:2022',
        target_ref='A.8.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Access-control policy frames the privileged-access model.',
        citation='ISO27002:2022 §5.15 + §8.2',
    ),
    RelationshipEdge(
        source_ref='A.5.15', source_standard_id='ISO27001:2022',
        target_ref='A.8.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Access-control policy frames the information-access restriction model.',
        citation='ISO27002:2022 §5.15 + §8.3',
    ),
    RelationshipEdge(
        source_ref='A.5.17', source_standard_id='ISO27001:2022',
        target_ref='A.8.5', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Authentication-info rules drive the secure-authentication technical control.',
        citation='ISO27002:2022 §5.17 + §8.5',
    ),
    RelationshipEdge(
        source_ref='A.5.18', source_standard_id='ISO27001:2022',
        target_ref='A.8.2', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Access-rights mgmt and privileged-access mgmt are siblings — '
                  'privileged grants are a subset of access rights with extra controls.',
        citation='ISO27002:2022 §5.18 + §8.2',
        role='access_pair',
    ),
    RelationshipEdge(
        source_ref='A.5.18', source_standard_id='ISO27001:2022',
        target_ref='A.8.3', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Access rights (who can access) and information-access restriction '
                  '(what they can do once in) are complementary.',
        citation='ISO27002:2022 §5.18 + §8.3',
        role='access_pair',
    ),

    # ── 26. Cross-control link from A.8.16 monitoring + A.8.10 deletion
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Records retention (A.5.33) drives the information-deletion '
                  '(A.8.10) execution when retention period expires.',
        citation='ISO27002:2022 §5.33 + §8.10',
        role='retention_deletion',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='PII retention drives deletion timing — A.5.34 + A.8.10 paired.',
        citation='ISO27002:2022 §5.34 + §8.10',
        role='retention_deletion',
    ),

    # ── 27. Acquisition + maintenance bridges ─────────────────────────
    RelationshipEdge(
        source_ref='A.5.20', source_standard_id='ISO27001:2022',
        target_ref='A.8.30', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Supplier agreements frame outsourced-development security clauses.',
        citation='ISO27002:2022 §5.20 + §8.30',
    ),
    RelationshipEdge(
        source_ref='A.8.30', source_standard_id='ISO27001:2022',
        target_ref='A.8.25', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Outsourced-development controls extend the SDLC into supplier scope.',
        citation='ISO27002:2022 §8.30 + §8.25',
    ),

    # ── S6 batch 3: physical internal + A.8 gaps + ISMS 7-9 ───────────

    # ── 28. A.7 physical internal structure ───────────────────────────
    RelationshipEdge(
        source_ref='A.7.1', source_standard_id='ISO27001:2022',
        target_ref='A.7.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Security perimeter must be defined before entry controls can be authored.',
        citation='ISO27002:2022 §7.1 + §7.2',
    ),
    RelationshipEdge(
        source_ref='A.7.1', source_standard_id='ISO27001:2022',
        target_ref='A.7.4', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Perimeter scope frames physical-monitoring coverage.',
        citation='ISO27002:2022 §7.1 + §7.4',
    ),
    RelationshipEdge(
        source_ref='A.7.2', source_standard_id='ISO27001:2022',
        target_ref='A.7.4', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Entry controls and physical monitoring are co-deployed — '
                  'every entry point monitored, every monitor at an entry.',
        citation='ISO27002:2022 §7.2 + §7.4',
        role='physical_access',
    ),
    RelationshipEdge(
        source_ref='A.7.3', source_standard_id='ISO27001:2022',
        target_ref='A.7.6', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Secured offices (A.7.3) and working in secure areas (A.7.6) — '
                  'the room and the work-conduct rules are co-authored.',
        citation='ISO27002:2022 §7.3 + §7.6',
        role='secure_area',
    ),
    RelationshipEdge(
        source_ref='A.7.6', source_standard_id='ISO27001:2022',
        target_ref='A.7.8', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Working in secure areas and equipment siting — same room, '
                  'paired controls for personnel-+-asset protection.',
        citation='ISO27002:2022 §7.6 + §7.8',
        role='secure_area',
    ),
    RelationshipEdge(
        source_ref='A.7.8', source_standard_id='ISO27001:2022',
        target_ref='A.7.5', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Equipment-siting decisions feed environmental-threat protections.',
        citation='ISO27002:2022 §7.8 + §7.5',
    ),
    RelationshipEdge(
        source_ref='A.7.9', source_standard_id='ISO27001:2022',
        target_ref='A.6.7', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Off-premises equipment + remote working — same risk surface; '
                  'the equipment-protection rules pair with the working-conduct rules.',
        citation='ISO27002:2022 §7.9 + §6.7',
        role='remote_pair',
    ),
    RelationshipEdge(
        source_ref='A.7.12', source_standard_id='ISO27001:2022',
        target_ref='A.7.8', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Cabling-security planning is part of equipment-siting design.',
        citation='ISO27002:2022 §7.12 + §7.8',
    ),
    RelationshipEdge(
        source_ref='A.7.13', source_standard_id='ISO27001:2022',
        target_ref='A.8.32', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Equipment-maintenance events feed change-management tracking.',
        citation='ISO27002:2022 §7.13 + §8.32',
    ),

    # ── 29. A.6.7 remote-working network ──────────────────────────────
    RelationshipEdge(
        source_ref='A.6.7', source_standard_id='ISO27001:2022',
        target_ref='A.8.1', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Remote working + user-endpoint device controls — same '
                  'remote-worker scope on both sides.',
        citation='ISO27002:2022 §6.7 + §8.1',
        role='remote_pair',
    ),
    RelationshipEdge(
        source_ref='A.6.7', source_standard_id='ISO27001:2022',
        target_ref='A.7.7', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Remote working + clear-desk/clear-screen — same '
                  'home-office hygiene rules.',
        citation='ISO27002:2022 §6.7 + §7.7',
        role='remote_pair',
    ),
    RelationshipEdge(
        source_ref='A.6.7', source_standard_id='ISO27001:2022',
        target_ref='A.5.10', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Remote-working specifics feed AUP differentiation.',
        citation='ISO27002:2022 §6.7 + §5.10',
    ),

    # ── 30. A.8.1 endpoint devices ────────────────────────────────────
    RelationshipEdge(
        source_ref='A.8.1', source_standard_id='ISO27001:2022',
        target_ref='A.5.10', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Endpoint-device technical controls drive AUP user rules.',
        citation='ISO27002:2022 §8.1 + §5.10',
    ),
    RelationshipEdge(
        source_ref='A.8.1', source_standard_id='ISO27001:2022',
        target_ref='A.8.7', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Endpoint security + anti-malware — every endpoint covered '
                  'by anti-malware as part of its baseline.',
        citation='ISO27002:2022 §8.1 + §8.7',
        role='endpoint_pair',
    ),

    # ── 31. A.8.4 source code + A.8.18 utility programs → A.8.2 ───────
    RelationshipEdge(
        source_ref='A.8.4', source_standard_id='ISO27001:2022',
        target_ref='A.8.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Source-code access is a privileged grant; A.8.2 privileged-access '
                  'model frames it.',
        citation='ISO27002:2022 §8.4 + §8.2',
    ),
    RelationshipEdge(
        source_ref='A.8.18', source_standard_id='ISO27001:2022',
        target_ref='A.8.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Privileged-utility-program use is a privileged grant; A.8.2 frames it.',
        citation='ISO27002:2022 §8.18 + §8.2',
    ),
    RelationshipEdge(
        source_ref='A.8.19', source_standard_id='ISO27001:2022',
        target_ref='A.8.32', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Software-installation rules are operationalised via change management.',
        citation='ISO27002:2022 §8.19 + §8.32',
    ),

    # ── 32. A.8.6 capacity management → A.5.30 BCP ────────────────────
    RelationshipEdge(
        source_ref='A.8.6', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Capacity baselines feed ICT-readiness RTO/RPO planning.',
        citation='ISO27002:2022 §8.6 + §5.30',
    ),
    RelationshipEdge(
        source_ref='A.8.6', source_standard_id='ISO27001:2022',
        target_ref='A.8.16', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Capacity monitoring metrics surface in operational monitoring.',
        citation='ISO27002:2022 §8.6 + §8.16',
    ),

    # ── 33. A.8.7 anti-malware ↔ A.5.7 threat intel ───────────────────
    RelationshipEdge(
        source_ref='A.8.7', source_standard_id='ISO27001:2022',
        target_ref='A.5.7', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Anti-malware detections feed threat-intelligence signal updates.',
        citation='ISO27002:2022 §8.7 + §5.7',
    ),

    # ── 34. A.8.11 data masking / A.8.12 DLP ──────────────────────────
    RelationshipEdge(
        source_ref='A.8.11', source_standard_id='ISO27001:2022',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Data masking is a PII-protection technical control that '
                  'operationalises A.5.34 minimisation obligations.',
        citation='ISO27002:2022 §8.11 + §5.34',
    ),
    RelationshipEdge(
        source_ref='A.8.11', source_standard_id='ISO27001:2022',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Data masking and information deletion are sibling minimisation '
                  'mechanisms — mask when need to retain shape, delete when no need.',
        citation='ISO27002:2022 §8.11 + §8.10',
        role='minimisation',
    ),
    RelationshipEdge(
        source_ref='A.8.12', source_standard_id='ISO27001:2022',
        target_ref='A.5.13', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='DLP rules depend on classification labels being applied — '
                  'labels are the matching criteria DLP enforces.',
        citation='ISO27002:2022 §8.12 + §5.13',
    ),
    RelationshipEdge(
        source_ref='A.8.12', source_standard_id='ISO27001:2022',
        target_ref='A.5.18', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='DLP and access-rights are complementary outbound-control mechanisms.',
        citation='ISO27002:2022 §8.12 + §5.18',
        role='data_control',
    ),

    # ── 35. A.8.34 audit-testing protection ───────────────────────────
    RelationshipEdge(
        source_ref='A.8.34', source_standard_id='ISO27001:2022',
        target_ref='9.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Audit-testing protections enable safe operation of internal-audit activities.',
        citation='ISO27002:2022 §8.34 + ISO27001:2022 cl. 9.2',
    ),

    # ── 36. ISMS clauses 7.x competence + awareness + communication ──
    RelationshipEdge(
        source_ref='7.1', source_standard_id='ISO27001:2022',
        target_ref='7.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Resources provision precedes competence determination.',
        citation='ISO27001:2022 cl. 7.1 + 7.2',
    ),
    RelationshipEdge(
        source_ref='7.2', source_standard_id='ISO27001:2022',
        target_ref='7.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Competence requirements frame the awareness-program scope.',
        citation='ISO27001:2022 cl. 7.2 + 7.3',
    ),
    RelationshipEdge(
        source_ref='7.2', source_standard_id='ISO27001:2022',
        target_ref='A.6.3', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='ISMS competence requirements and the A.6.3 information-security '
                  'awareness/education/training are paired surfaces.',
        citation='ISO27001:2022 cl. 7.2 + ISO27002:2022 §6.3',
        role='competence',
    ),
    RelationshipEdge(
        source_ref='7.3', source_standard_id='ISO27001:2022',
        target_ref='A.6.3', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='ISMS awareness clause and A.6.3 awareness-training control are paired.',
        citation='ISO27001:2022 cl. 7.3 + ISO27002:2022 §6.3',
        role='awareness',
    ),
    RelationshipEdge(
        source_ref='7.4', source_standard_id='ISO27001:2022',
        target_ref='A.5.5', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='ISMS communication clause and A.5.5 contact-with-authorities control are paired.',
        citation='ISO27001:2022 cl. 7.4 + ISO27002:2022 §5.5',
        role='communication',
    ),
    RelationshipEdge(
        source_ref='7.5', source_standard_id='ISO27001:2022',
        target_ref='4.4', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Documented-information requirements operationalise the ISMS itself.',
        citation='ISO27001:2022 cl. 7.5 + 4.4',
    ),

    # ── 37. ISMS clauses 8.x operational risk-management chain ────────
    RelationshipEdge(
        source_ref='8.1', source_standard_id='ISO27001:2022',
        target_ref='8.2', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Operational planning frames the risk-assessment review activities.',
        citation='ISO27001:2022 cl. 8.1 + 8.2',
    ),
    RelationshipEdge(
        source_ref='8.2', source_standard_id='ISO27001:2022',
        target_ref='8.3', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Updated risk-assessment outputs drive treatment-plan updates.',
        citation='ISO27001:2022 cl. 8.2 + 8.3',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='8.2', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Initial (6.1.2) and operational (8.2) risk assessment are the same '
                  'process at different lifecycle phases.',
        citation='ISO27001:2022 cl. 6.1.2 + 8.2',
        role='risk_lifecycle',
    ),
    RelationshipEdge(
        source_ref='6.1.3', source_standard_id='ISO27001:2022',
        target_ref='8.3', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Initial (6.1.3) and operational (8.3) risk treatment are the same '
                  'process at different lifecycle phases.',
        citation='ISO27001:2022 cl. 6.1.3 + 8.3',
        role='risk_lifecycle',
    ),

    # ── 38. ISMS clause 9.x evaluation chain ──────────────────────────
    RelationshipEdge(
        source_ref='9.1', source_standard_id='ISO27001:2022',
        target_ref='9.2', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Monitoring/measurement results feed internal-audit scope.',
        citation='ISO27001:2022 cl. 9.1 + 9.2',
    ),
    RelationshipEdge(
        source_ref='9.2', source_standard_id='ISO27001:2022',
        target_ref='9.3', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Internal-audit outputs feed management review.',
        citation='ISO27001:2022 cl. 9.2 + 9.3',
    ),

    # ── 39. A.5.6 special-interest groups → A.5.7 threat intel ────────
    RelationshipEdge(
        source_ref='A.5.6', source_standard_id='ISO27001:2022',
        target_ref='A.5.7', target_standard_id='ISO27001:2022',
        edge_type='FEEDS_INTO',
        rationale='Special-interest-group membership produces threat-intel signals.',
        citation='ISO27002:2022 §5.6 + §5.7',
    ),

    # ── 40. A.5.37 operating procedures ───────────────────────────────
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='PREREQUISITE_OF',
        rationale='Operating procedures depend on the asset register identifying '
                  'the applicable scope.',
        citation='ISO27002:2022 §5.37 + §5.9; curation batch 19',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='AUDITED_BY',
        rationale='Operating procedures are within scope of compliance review.',
        citation='ISO27002:2022 §5.37 + §5.36',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='A.8.32', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Operating procedures reference change-management process; '
                  'changes update procedures.',
        citation='ISO27002:2022 §5.37 + §8.32',
        role='operations',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='A.5.24', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Operating procedures include the IR procedures that A.5.24 frames.',
        citation='ISO27002:2022 §5.37 + §5.24',
        role='operations',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='A.5.29', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Operating procedures include the disruption-response procedures.',
        citation='ISO27002:2022 §5.37 + §5.29',
        role='operations',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='PAIRS_WITH',
        rationale='Operating procedures include the ICT-readiness procedures.',
        citation='ISO27002:2022 §5.37 + §5.30',
        role='operations',
    ),
]

# ── Intra-GDPR edges (S5) ─────────────────────────────────────────────
# Authored from GDPR text + EDPB Guidelines. Both public.
# Granularity: top-level Articles unless a citation specifically
# targets a sub-article. PAIRS_WITH is symmetric (author once;
# loader writes both directions). All others directional.
#
# Edge-type discipline:
#   PAIRS_WITH       — both move together; one's evidence informs the other
#   PREREQUISITE_OF  — A must exist before B is meaningful (A -> B)
#   ESCALATES_TO     — A's threshold exceeded -> B fires (A -> B)
#   AUDITED_BY       — B independently verifies A's operation (A -> B)
#   FEEDS_INTO       — A's output is input to B's operation (A -> B)
#
# Citations point to GDPR Art.X.Y phrase or EDPB Guideline reference.
# Note where DerivedSpec already encodes the relationship — those are
# NOT duplicated here (DerivedSpec composition is a separate edge type).

INTRA_GDPR_EDGES: list[RelationshipEdge] = [

    # ── Chapter II: Principles + lawful basis chain ───────────────────
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.7 (consent) only applies when Art.6.1.a is the chosen lawful basis.',
        citation='GDPR Art.6.1.a referenced by Art.7',
        role='lawful_basis',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='Art.8', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.8 (children\'s consent) specialises Art.6.1.a when an information-society service is offered directly to a child.',
        citation='GDPR Art.8.1',
        role='lawful_basis',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.9 (special categories) requires both a Art.6 lawful basis AND an Art.9.2 exemption.',
        citation='GDPR Art.9.1-9.2 (two-step test)',
        role='lawful_basis',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='Art.10', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.10 (criminal convictions) requires Art.6 lawful basis plus Union/MS law authorisation.',
        citation='GDPR Art.10',
        role='lawful_basis',
    ),
    RelationshipEdge(
        source_ref='Art.7', source_standard_id='GDPR:2016/679',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Withdrawal of consent under Art.7.3 is one of the explicit Art.17.1.b grounds for erasure.',
        citation='GDPR Art.17.1.b ("data subject withdraws consent on which the processing is based according to point (a) of Article 6(1) or point (a) of Article 9(2)")',
    ),
    RelationshipEdge(
        source_ref='Art.9', source_standard_id='GDPR:2016/679',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='ESCALATES_TO',
        rationale='Large-scale processing of Art.9 special-category data is an explicit Art.35.3.b DPIA trigger.',
        citation='GDPR Art.35.3.b',
    ),
    RelationshipEdge(
        source_ref='Art.10', source_standard_id='GDPR:2016/679',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='ESCALATES_TO',
        rationale='Processing of Art.10 criminal-conviction data on a large scale triggers DPIA likelihood under EDPB Guidelines 4/2017 criteria.',
        citation='EDPB Guidelines 4/2017 on DPIA (criterion #4)',
    ),

    # ── Chapter III: Rights of the data subject ───────────────────────
    RelationshipEdge(
        source_ref='Art.12', source_standard_id='GDPR:2016/679',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.12.1 governs HOW Art.13 information must be provided (concise, transparent, intelligible, accessible).',
        citation='GDPR Art.12.1 referencing Arts. 13 and 14',
    ),
    RelationshipEdge(
        source_ref='Art.12', source_standard_id='GDPR:2016/679',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.12.1 governs HOW Art.14 information must be provided (same transparency requirements as Art.13).',
        citation='GDPR Art.12.1',
    ),
    RelationshipEdge(
        source_ref='Art.12', source_standard_id='GDPR:2016/679',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.12.3 sets the 1-month response deadline + extension rules for Art.15 access requests.',
        citation='GDPR Art.12.3 referencing Arts. 15 to 22',
    ),
    RelationshipEdge(
        source_ref='Art.13', source_standard_id='GDPR:2016/679',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Two collection-path variants of the same transparency obligation — Art.13 for direct collection, Art.14 for indirect.',
        citation='GDPR Art.14 mirrors Art.13 content; EDPB Guidelines on Transparency Annex',
        role='collection_path',
    ),
    RelationshipEdge(
        source_ref='Art.15', source_standard_id='GDPR:2016/679',
        target_ref='Art.16', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Inaccuracies surfaced via Art.15 access are routinely followed by Art.16 rectification requests.',
        citation='EDPB Guidelines 01/2022 on data subject rights — access',
    ),
    RelationshipEdge(
        source_ref='Art.16', source_standard_id='GDPR:2016/679',
        target_ref='Art.19', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Each Art.16 rectification triggers an Art.19 notification obligation to recipients.',
        citation='GDPR Art.19 explicitly references Arts. 16, 17(1), and 18',
        role='notification',
    ),
    RelationshipEdge(
        source_ref='Art.17', source_standard_id='GDPR:2016/679',
        target_ref='Art.19', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Each Art.17 erasure triggers an Art.19 notification obligation to recipients.',
        citation='GDPR Art.19 explicitly references Arts. 16, 17(1), and 18',
        role='notification',
    ),
    RelationshipEdge(
        source_ref='Art.18', source_standard_id='GDPR:2016/679',
        target_ref='Art.19', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Each Art.18 restriction triggers an Art.19 notification obligation to recipients.',
        citation='GDPR Art.19 explicitly references Arts. 16, 17(1), and 18',
        role='notification',
    ),
    RelationshipEdge(
        source_ref='Art.21', source_standard_id='GDPR:2016/679',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.21.2 objection to direct marketing is an Art.17.1.c ground for erasure.',
        citation='GDPR Art.17.1.c ("data subject objects to the processing pursuant to Article 21(1)")',
    ),
    RelationshipEdge(
        source_ref='Art.20', source_standard_id='GDPR:2016/679',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.20 portability applies only when processing is based on Art.6.1.a consent or Art.6.1.b contract.',
        citation='GDPR Art.20.1.a',
    ),
    RelationshipEdge(
        source_ref='Art.22', source_standard_id='GDPR:2016/679',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='ESCALATES_TO',
        rationale='Art.22 automated decision-making with legal/significant effect is an explicit Art.35.3.a DPIA trigger.',
        citation='GDPR Art.35.3.a',
    ),

    # ── Chapter IV: Controller / processor obligations ────────────────
    RelationshipEdge(
        source_ref='Art.30', source_standard_id='GDPR:2016/679',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.32 "appropriate security measures for processing" requires the Art.30 RoPA enumeration of processing activities to scope.',
        citation='GDPR Art.32.1 ("the security of processing") read with Art.30',
    ),
    RelationshipEdge(
        source_ref='Art.30', source_standard_id='GDPR:2016/679',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.30 RoPA entries are the candidate set scoped against Art.35.1 likelihood criteria to determine DPIA need.',
        citation='EDPB Guidelines 4/2017 on DPIA §III.B',
    ),
    RelationshipEdge(
        source_ref='Art.30', source_standard_id='GDPR:2016/679',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.30.1.e RoPA must record transfers to third countries — feeds Art.46 safeguard selection.',
        citation='GDPR Art.30.1.e',
    ),
    RelationshipEdge(
        source_ref='Art.24', source_standard_id='GDPR:2016/679',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='AUDITED_BY',
        rationale='Art.24 controller responsibility is to implement measures that demonstrate compliance with Art.5 principles — Art.5.2 makes Art.5 the auditor of Art.24 measures.',
        citation='GDPR Art.24.1 + Art.5.2',
    ),
    RelationshipEdge(
        source_ref='Art.26', source_standard_id='GDPR:2016/679',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Joint-controller arrangements must be reflected in each controller\'s Art.30 RoPA.',
        citation='GDPR Art.30.1 (controllers maintain RoPA "of processing activities under its responsibility")',
        role='governance',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='Art.29', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.29 processor-instruction binding presupposes the Art.28 controller-processor agreement establishing those instructions.',
        citation='GDPR Art.29 ("on instructions from the controller")',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Art.28.3.c requires the processor to take all Art.32 measures — DPA security clauses mirror Art.32 obligations.',
        citation='GDPR Art.28.3.c',
        role='security_flowdown',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.33.2 requires the processor to notify the controller of breaches without undue delay — DPA breach-notification clauses set this up.',
        citation='GDPR Art.33.2 + Art.28.3.f',
    ),
    RelationshipEdge(
        source_ref='Art.31', source_standard_id='GDPR:2016/679',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Art.31 SA cooperation includes the Art.33 breach-reporting channel — same SA contact protocol.',
        citation='GDPR Art.31 + Art.33',
        role='sa_interaction',
    ),
    RelationshipEdge(
        source_ref='Art.32', source_standard_id='GDPR:2016/679',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Art.25 DPbD design-time controls and Art.32 operational security are complementary — DPbD provides the baseline that Art.32 sustains.',
        citation='EDPB Guidelines 4/2019 on Art.25 §1.3',
        role='security_architecture',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='Art.34', target_standard_id='GDPR:2016/679',
        edge_type='ESCALATES_TO',
        rationale='Art.34 escalates Art.33 to direct-subject communication when breach is likely to result in high risk to rights.',
        citation='GDPR Art.34.1 ("when the personal data breach is likely to result in a high risk")',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='Art.36', target_standard_id='GDPR:2016/679',
        edge_type='ESCALATES_TO',
        rationale='Art.36 prior consultation fires when Art.35 DPIA shows residual high risk that controller cannot mitigate.',
        citation='GDPR Art.36.1',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.35.7.d-d DPIA outputs (the measures, safeguards and security mechanisms) become Art.32 controls.',
        citation='GDPR Art.35.7.d',
    ),
    RelationshipEdge(
        source_ref='Art.37', source_standard_id='GDPR:2016/679',
        target_ref='Art.38', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.38 position-of-DPO duties only apply once Art.37 designation has happened.',
        citation='GDPR Art.37 then Art.38 ordering',
        role='dpo_lifecycle',
    ),
    RelationshipEdge(
        source_ref='Art.38', source_standard_id='GDPR:2016/679',
        target_ref='Art.39', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.39 DPO tasks presuppose the Art.38 conditions (independence, resources, no conflicts) are in place.',
        citation='GDPR Art.38.3 + Art.39',
        role='dpo_lifecycle',
    ),
    RelationshipEdge(
        source_ref='Art.40', source_standard_id='GDPR:2016/679',
        target_ref='Art.41', target_standard_id='GDPR:2016/679',
        edge_type='AUDITED_BY',
        rationale='Art.41 monitoring bodies verify adherence to Art.40 codes of conduct.',
        citation='GDPR Art.41.1 ("monitoring of compliance with a code of conduct")',
    ),
    RelationshipEdge(
        source_ref='Art.42', source_standard_id='GDPR:2016/679',
        target_ref='Art.43', target_standard_id='GDPR:2016/679',
        edge_type='AUDITED_BY',
        rationale='Art.43 certification bodies issue and renew the Art.42 certifications and seals.',
        citation='GDPR Art.43.1',
    ),

    # ── Chapter V: International transfers ────────────────────────────
    RelationshipEdge(
        source_ref='Art.44', source_standard_id='GDPR:2016/679',
        target_ref='Art.45', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.44 general principle ("transferred only if conditions in this Chapter are complied with") gates Art.45 adequacy reliance.',
        citation='GDPR Art.44',
        role='transfer_mechanism',
    ),
    RelationshipEdge(
        source_ref='Art.44', source_standard_id='GDPR:2016/679',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.44 gates Art.46 appropriate-safeguards reliance.',
        citation='GDPR Art.44',
        role='transfer_mechanism',
    ),
    RelationshipEdge(
        source_ref='Art.44', source_standard_id='GDPR:2016/679',
        target_ref='Art.49', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.44 gates Art.49 derogation reliance.',
        citation='GDPR Art.44',
        role='transfer_mechanism',
    ),
    RelationshipEdge(
        source_ref='Art.46', source_standard_id='GDPR:2016/679',
        target_ref='Art.47', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='BCRs in Art.47 are a specific Art.46.2.b safeguard mechanism — same body of obligations specialised for intra-group.',
        citation='GDPR Art.46.2.b + Art.47',
        role='safeguard_specialisation',
    ),
    RelationshipEdge(
        source_ref='Art.45', source_standard_id='GDPR:2016/679',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='PAIRS_WITH',
        rationale='Adequacy + appropriate safeguards are the two equal-rank Art.44 transfer paths; failure of adequacy moves the activity to Art.46.',
        citation='Schrems II (CJEU C-311/18) read with GDPR Arts. 45/46',
        role='transfer_mechanism',
    ),
    RelationshipEdge(
        source_ref='Art.46', source_standard_id='GDPR:2016/679',
        target_ref='Art.49', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='EDPB strict-construction doctrine: Art.49 derogations are only available where Arts. 45 and 46 cannot be relied upon.',
        citation='EDPB Guidelines 2/2018 on Art.49 §II.2',
        role='transfer_mechanism',
    ),
    RelationshipEdge(
        source_ref='Art.48', source_standard_id='GDPR:2016/679',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.48 foreign authority requests must be analysed against Art.46 safeguards — TIA workflow.',
        citation='Schrems II (CJEU C-311/18); EDPB Recommendations 01/2020',
    ),

    # ── Cross-chapter accountability + transparency anchors ───────────
    RelationshipEdge(
        source_ref='Art.5', source_standard_id='GDPR:2016/679',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='AUDITED_BY',
        rationale='Art.5.2 demonstrability of the Art.5 principles is operationalised in part through the Art.30 records of processing.',
        citation='GDPR Art.5.2 + Art.30',
        role='accountability',
    ),
    RelationshipEdge(
        source_ref='Art.5.2', source_standard_id='GDPR:2016/679',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='AUDITED_BY',
        rationale='Art.5.2 accountability principle is concretely operationalised by the Art.30 RoPA — primary evidence of demonstrability.',
        citation='GDPR Art.5.2 read with Art.30',
        role='accountability',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.e', source_standard_id='GDPR:2016/679',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Storage-limitation reviews mature data toward retention end, at which Art.17 erasure mechanisms execute.',
        citation='GDPR Art.5.1.e + Art.17',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.d', source_standard_id='GDPR:2016/679',
        target_ref='Art.16', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Accuracy obligations under Art.5.1.d are operationalised through Art.16 rectification mechanisms.',
        citation='GDPR Art.5.1.d + Art.16',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.a', source_standard_id='GDPR:2016/679',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Transparency principle (Art.5.1.a) is operationally delivered via Art.13 information at collection.',
        citation='GDPR Art.5.1.a + Art.13 (transparency thread)',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.a', source_standard_id='GDPR:2016/679',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Transparency principle (Art.5.1.a) is operationally delivered via Art.14 information when not from data subject.',
        citation='GDPR Art.5.1.a + Art.14',
    ),
    RelationshipEdge(
        source_ref='Art.24', source_standard_id='GDPR:2016/679',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.24 frames the controller-responsibility obligation that Art.32 implements through specific security measures.',
        citation='GDPR Art.24.1 ("appropriate technical and organisational measures") reflected in Art.32.1',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.25 DPbD design-time decisions establish the security architecture that Art.32 measures sustain.',
        citation='EDPB Guidelines 4/2019 §1.3',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='Art.31', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.33 breach reporting is the most frequent triggering of Art.31 SA cooperation channels.',
        citation='GDPR Art.31 + Art.33',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='FEEDS_INTO',
        rationale='Art.35 DPIA recommended mitigations are implemented as Art.25 DPbD measures in subsequent design iterations.',
        citation='EDPB Guidelines 4/2017 §IV',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.13.1.c-d requires the lawful basis (and legitimate interests pursued where applicable) to be communicated — that lawful basis is the Art.6 selection.',
        citation='GDPR Art.13.1.c-d',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='PREREQUISITE_OF',
        rationale='Art.14.1.c-d requires the lawful basis to be communicated — that lawful basis is the Art.6 selection.',
        citation='GDPR Art.14.1.c-d',
    ),
]


# ── BLOCKS_WHEN edges (S3i — negative cascade) ────────────────────────
# Each edge marks the SOURCE control's implications as suppressible
# when the applies_when expression evaluates true against the cascade
# metadata. Engine consults these before writing an implication on
# the source control; matched blockers go to cascade_suppression_log
# with suppression_kind='blocks_when'.
#
# The TARGET control is the state-bearing control that conceptually
# manages the blocker condition (e.g., A.5.31 legal register is where
# legal holds are recorded). The relationship is informational —
# the engine evaluates applies_when against the cascade metadata, not
# against the target control's own state. The target is a curation
# anchor for "where would the auditor look to confirm the blocker?".

BLOCKS_WHEN_EDGES: list[RelationshipEdge] = [
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='BLOCKS_WHEN',
        applies_when='legal_hold == true',
        rationale='Retention-period-reached deletion is suppressed when '
                  'a legal hold is active on the affected records. Auditor '
                  'verifies hold via A.5.31 legal/regulatory register.',
        citation='ISO27002:2022 §5.33 + §5.31 (legal-hold exception to retention)',
        role='legal_hold',
    ),
    RelationshipEdge(
        source_ref='A.8.10', source_standard_id='ISO27001:2022',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='BLOCKS_WHEN',
        applies_when='legal_hold == true',
        rationale='Information deletion (A.8.10) is suppressed when a legal '
                  'hold is active. Same blocker as A.5.33 retention path.',
        citation='ISO27002:2022 §8.10 + §5.31',
        role='legal_hold',
    ),
    RelationshipEdge(
        source_ref='Art.17', source_standard_id='GDPR:2016/679',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='BLOCKS_WHEN',
        applies_when='legal_obligation_to_retain == true',
        rationale='GDPR Art.17.3.b: erasure is suppressed when processing '
                  'is necessary for compliance with a legal obligation '
                  '(Art.6.1.c lawful basis). Auditor verifies the legal-'
                  'obligation basis in the Art.6 lawful-basis register.',
        citation='GDPR Art.17.3.b read with Art.6.1.c',
        role='legal_obligation',
    ),
    RelationshipEdge(
        source_ref='A.5.18', source_standard_id='ISO27001:2022',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='BLOCKS_WHEN',
        applies_when='investigation_in_progress == true',
        rationale='Access-rights revocation may be deferred when an '
                  'incident investigation needs the subject to retain '
                  'access for forensic continuity. Suppressed until '
                  'investigation closes. Auditor verifies in A.5.26 '
                  'incident register.',
        citation='ISO27002:2022 §5.18 + §5.26 (investigation continuity)',
        role='active_investigation',
    ),
    RelationshipEdge(
        source_ref='A.5.30', source_standard_id='ISO27001:2022',
        target_ref='A.5.24', target_standard_id='ISO27001:2022',
        edge_type='BLOCKS_WHEN',
        applies_when='active_incident == true',
        rationale='Scheduled ICT-readiness tests are suppressed while a '
                  'real incident is in progress (avoid resource conflict). '
                  'Auditor verifies via A.5.24 incident-response framework.',
        citation='ISO27002:2022 §5.30 + §5.24',
        role='active_incident',
    ),
]


# S4: cross-framework edges migrated from iso_nodes_phase1.json + gdpr_nodes_phase2.json
# (cross_framework_summary fields).
# Edge types: IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE.
# Re-generate via scripts/extract_xfw_to_catalog.py — do not
# edit by hand; the next regeneration overwrites local edits.

XFW_EDGES: list[RelationshipEdge] = [
    RelationshipEdge(
        source_ref='Art.10', source_standard_id='GDPR:2016/679',
        target_ref='A.5.12', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information classification must flag criminal convictions data as a special restricted category requiring explicit legal basis and heightened access controls.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.10', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control must identify the specific legal basis permitting processing of criminal data — only official authorities or specific legal derogations apply.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.10', source_standard_id='GDPR:2016/679',
        target_ref='A.8.3', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction must limit access to criminal convictions data to only those with an explicit legal basis to process it — most restrictive access tier.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.13', source_standard_id='GDPR:2016/679',
        target_ref='A.5.37', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Documented operating procedures must define the privacy notice process — what information is provided, when, and in what format.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.14', source_standard_id='GDPR:2016/679',
        target_ref='A.5.37', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Documented procedures must cover indirect data collection scenarios and the obligation to notify data subjects within one month.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.15', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes subject access request procedures — the primary control for fulfilling DSAR identification, search, and response.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.16', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes rectification procedures for maintaining accuracy of personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.17', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes erasure procedures — the procedural side of right-to-be-forgotten alongside A.8.10 information deletion.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.17', source_standard_id='GDPR:2016/679',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information deletion is the primary technical control for the right to be forgotten — secure, verifiable, complete erasure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.18', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes processing-restriction procedures triggered by subject requests.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.19', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes recipient-notification procedures when data is rectified, erased, or restricted.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.19', source_standard_id='GDPR:2016/679',
        target_ref='A.5.37', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Documented operating procedures must include the process for notifying recipients when rectification, erasure or restriction has been applied to personal data shared with them.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.20', source_standard_id='GDPR:2016/679',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information transfer controls must cover secure provision of portable personal data — format, encryption, integrity verification.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.20', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes data-portability procedures (structured machine-readable export).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.20', source_standard_id='GDPR:2016/679',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Cryptography must protect portable personal data in transit — the exported dataset must be encrypted for transmission.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.21', source_standard_id='GDPR:2016/679',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes objection-handling procedures including opt-out flags for direct marketing/profiling.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.22', source_standard_id='GDPR:2016/679',
        target_ref='A.5.37', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Documented operating procedures must define the process for human review of automated decisions when requested by data subjects.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.24', source_standard_id='GDPR:2016/679',
        target_ref='A.5.1', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security policies demonstrate the controller\'s commitment to data protection — foundational accountability document.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.24', source_standard_id='GDPR:2016/679',
        target_ref='A.5.2', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security roles and responsibilities must include GDPR-specific roles (DPO, controller, processor designations).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.24', source_standard_id='GDPR:2016/679',
        target_ref='A.5.4', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Management responsibilities control ensures top management takes accountability for GDPR compliance — Art.24 is a governance obligation.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information deletion with automated retention enforcement implements privacy by default — data deleted automatically when no longer needed.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='A.8.11', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Data masking is a key privacy-by-default technical control — using masked/pseudonymised data by default reduces exposure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='A.8.25', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Secure development lifecycle is the ISO mechanism for embedding privacy by design — security and privacy requirements built in from the start of development, not bolted on afterwards.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='A.8.26', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Application security requirements must include data minimisation, purpose limitation and subject rights as functional requirements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='A.8.27', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Secure system architecture and engineering principles implement privacy by design at the architectural level.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.26', source_standard_id='GDPR:2016/679',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security in supplier relationships covers joint controller arrangements — security requirements and responsibilities must be defined in joint controller agreements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.26', source_standard_id='GDPR:2016/679',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Supplier agreements must include joint controller arrangements with explicit data protection obligations for each party.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security in supplier relationships is the primary ISO control for managing data processor relationships — security requirements imposed on all processors by contract.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Addressing information security within supplier agreements directly implements Art.28 — processor contracts must contain specific GDPR-mandated clauses (subject matter, duration, nature, purpose).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='A.5.22', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Monitoring, review and change management of supplier services implements the Art.28 requirement to audit processors and ensure ongoing compliance with contractual obligations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.29', source_standard_id='GDPR:2016/679',
        target_ref='A.6.2', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Terms and conditions of employment must include data processing obligations — staff process personal data only on controller instructions, as required by Art.29.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.30', source_standard_id='GDPR:2016/679',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Protection of records must cover the ROPA itself as a compliance record — must be maintained, protected and available to the DPA.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.30', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Inventory of information and associated assets is the ISO equivalent of the ROPA — must be extended to include all GDPR mandatory fields (purpose, lawful basis, retention, recipients).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.a', source_standard_id='GDPR:2016/679',
        target_ref='A.8.11', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Data masking implements pseudonymisation — transforming personal data so it cannot be attributed to a data subject without additional information held separately.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.a', source_standard_id='GDPR:2016/679',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Use of cryptography is the direct implementation of the encryption requirement — must cover personal data at rest and in transit, with a documented key management procedure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.5.15', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Access control implements confidentiality — ensures only authorised persons can access personal data processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.5.29', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security during disruption ensures personal data remains protected and available even during crisis situations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.8.14', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Redundancy of information processing facilities implements resilience — processing systems must withstand and recover from failures without loss of data availability.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.8.20', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Network security implements confidentiality and integrity in transit — personal data traversing networks must be protected.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.8.3', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction implements confidentiality at the data level — users access only the personal data they need.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.8.7', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Protection against malware directly implements integrity and availability of personal data processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.c', source_standard_id='GDPR:2016/679',
        target_ref='A.5.30', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='ICT readiness for business continuity implements the ability to restore personal data processing in a timely manner after incidents.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.c', source_standard_id='GDPR:2016/679',
        target_ref='A.8.13', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information backup is the primary technical control for restoring personal data availability — must be tested, offsite, and cover recovery time objectives appropriate to the risk.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.d', source_standard_id='GDPR:2016/679',
        target_ref='A.5.35', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Independent review of information security provides the formal evaluation and effectiveness assessment required by Art.32(1)(d).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.d', source_standard_id='GDPR:2016/679',
        target_ref='A.8.29', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Security testing in development and acceptance implements systematic testing of technical measures protecting personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.d', source_standard_id='GDPR:2016/679',
        target_ref='A.8.8', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Management of technical vulnerabilities requires regular assessment of security weaknesses — directly implements testing requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.d', source_standard_id='GDPR:2016/679',
        target_ref='9.1', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Monitoring, measurement, analysis and evaluation is the ISO management system mechanism for ongoing effectiveness testing.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.2', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security risk assessment is the direct implementation of Art.32(2)\'s requirement to assess risks to rights and freedoms when determining appropriate security measures.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.4', source_standard_id='GDPR:2016/679',
        target_ref='A.6.3', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security awareness, education and training ensures staff processing personal data understand their obligations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='A.5.24', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Incident management planning and preparation is the foundation for Art.33 compliance — 72-hour notification requires a pre-planned, rehearsed incident response process.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='A.5.25', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Assessment and decision on information security events implements the triage process that determines whether a breach has occurred and whether it must be notified.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Response to information security incidents implements the breach containment and notification workflow — includes DPA notification.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='A.5.28', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Collection of evidence supports the breach documentation requirements — Art.33(5) requires all breaches to be documented including those not notified to the DPA.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.34', source_standard_id='GDPR:2016/679',
        target_ref='A.5.26', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Incident response must include the data subject communication workflow — Art.34 requires notification without undue delay when breach is likely to result in high risk to subjects.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='A.5.8', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security in project management must include DPIA as a required gate for projects involving high-risk processing.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security risk assessment is the ISO framework that most closely aligns with DPIA methodology — Art.35 requires systematic assessment of risks to rights and freedoms, which ISO 6.1.2 structures. DPIA extends this to privacy specifically.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.37', source_standard_id='GDPR:2016/679',
        target_ref='A.5.2', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information security roles and responsibilities must include the DPO role — designation, independence, tasks and reporting line should be documented here.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.38', source_standard_id='GDPR:2016/679',
        target_ref='A.5.4', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Management responsibilities include ensuring the DPO has access to top management and the resources to perform their tasks.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.44', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Legal, statutory and regulatory requirements must include the transfer restrictions under Chapter V — adequacy decisions, standard contractual clauses, binding corporate rules.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.45', source_standard_id='GDPR:2016/679',
        target_ref='A.5.22', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Monitoring and review of supplier services must include adequacy status of third-country recipients — a previously adequate country losing adequacy (as with US Privacy Shield) requires immediate action.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.45', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control must track adequacy decisions — the list of adequate countries changes; compliance requires monitoring Commission decisions and adjusting transfer practices.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.46', source_standard_id='GDPR:2016/679',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information transfer controls must address international transfers specifically — encryption, lawful basis verification, adequacy confirmation before transfer.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.46', source_standard_id='GDPR:2016/679',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Addressing security in supplier agreements must cover international transfer safeguards — SCCs, BCRs or other Art.46 mechanisms must be reflected in data processing agreements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.a', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Legal, statutory, regulatory and contractual requirements control directly addresses identifying and complying with GDPR lawfulness obligations as a legal requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.5.12', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Classification of information must include purpose-limitation labels; data classified by purpose prevents secondary use violations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.c', source_standard_id='GDPR:2016/679',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information deletion control ensures data no longer adequate, relevant or limited is deleted — direct technical implementation of minimisation.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.e', source_standard_id='GDPR:2016/679',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Protection of records control includes retention schedules — must define and enforce GDPR-compliant retention periods.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.e', source_standard_id='GDPR:2016/679',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information deletion is the primary technical control for storage limitation — data must be deleted when retention period expires.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.f', source_standard_id='GDPR:2016/679',
        target_ref='A.5.15', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Access control ensures personal data is only accessible to authorised persons — core confidentiality control.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.f', source_standard_id='GDPR:2016/679',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Cryptography is the primary technical control for integrity and confidentiality of personal data — encryption at rest and in transit.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.f', source_standard_id='GDPR:2016/679',
        target_ref='A.8.3', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction implements need-to-know principle for personal data — direct confidentiality control.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.f', source_standard_id='GDPR:2016/679',
        target_ref='A.8.5', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Secure authentication prevents unauthorised access to personal data processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.f', source_standard_id='GDPR:2016/679',
        target_ref='A.8.7', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Protection against malware prevents integrity violations and confidentiality breaches affecting personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.2', source_standard_id='GDPR:2016/679',
        target_ref='A.5.35', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Independent review of information security is the primary ISO mechanism for demonstrating accountability — documented, auditable.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.2', source_standard_id='GDPR:2016/679',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Compliance with policies and standards requires documented evidence of compliance — the accountability paper trail.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.2', source_standard_id='GDPR:2016/679',
        target_ref='9.1', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Monitoring, measurement, analysis and evaluation produces the metrics and records that demonstrate accountability to regulators.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control is the direct ISO mechanism for identifying and documenting the lawful basis for each processing activity — a mandatory GDPR requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.7', source_standard_id='GDPR:2016/679',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Protection of records must cover consent records — the controller must be able to demonstrate consent was freely given and specific.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.85', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control must identify where national law derogations under Art.85 apply — journalistic, academic, artistic or literary purposes may override standard GDPR requirements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.9', source_standard_id='GDPR:2016/679',
        target_ref='A.5.12', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information classification must identify special category data and apply heightened classification — explicit GDPR requirement for additional protection of sensitive categories.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.9', source_standard_id='GDPR:2016/679',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Cryptography applies with heightened urgency to special category data — encryption at rest and in transit is effectively mandatory.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.9', source_standard_id='GDPR:2016/679',
        target_ref='A.8.3', target_standard_id='ISO27001:2022',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction must enforce stricter access controls for special category data — need-to-know at highest level.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.32.2', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security risk assessment is the direct implementation of Art.32(2)\'s requirement to assess risks to rights and freedoms when determining appropriate security measures.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security risk assessment is the ISO framework that most closely aligns with DPIA methodology — Art.35 requires systematic assessment of risks to rights and freedoms, which ISO 6.1.2 structures. DPIA extends this to privacy specifically.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='9.1', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.d', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Monitoring, measurement, analysis and evaluation is the ISO management system mechanism for ongoing effectiveness testing.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='9.1', source_standard_id='ISO27001:2022',
        target_ref='Art.5.2', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Monitoring, measurement, analysis and evaluation produces the metrics and records that demonstrate accountability to regulators.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='Art.24', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security policies demonstrate the controller\'s commitment to data protection — foundational accountability document.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security policies underpin Art.5 data protection principles - the foundational organisational measure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='Art.10', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information classification must flag criminal convictions data as a special restricted category requiring explicit legal basis and heightened access controls.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Classification of information must include purpose-limitation labels; data classified by purpose prevents secondary use violations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information classification must identify special category data and apply heightened classification — explicit GDPR requirement for additional protection of sensitive categories.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.14', source_standard_id='ISO27001:2022',
        target_ref='Art.20', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information transfer controls must cover secure provision of portable personal data — format, encryption, integrity verification.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.14', source_standard_id='ISO27001:2022',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information transfer controls must address international transfers specifically — encryption, lawful basis verification, adequacy confirmation before transfer.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.15', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Access control implements confidentiality — ensures only authorised persons can access personal data processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.15', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.f', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Access control ensures personal data is only accessible to authorised persons — core confidentiality control.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.18', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Access rights management implements Art.32.1.b ongoing confidentiality of processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.18', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Access rights management directly implements Art.5.1.f integrity and confidentiality principle.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.19', source_standard_id='ISO27001:2022',
        target_ref='Art.26', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security in supplier relationships covers joint controller arrangements — security requirements and responsibilities must be defined in joint controller agreements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.19', source_standard_id='ISO27001:2022',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security in supplier relationships is the primary ISO control for managing data processor relationships — security requirements imposed on all processors by contract.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.2', source_standard_id='ISO27001:2022',
        target_ref='Art.24', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security roles and responsibilities must include GDPR-specific roles (DPO, controller, processor designations).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.2', source_standard_id='ISO27001:2022',
        target_ref='Art.37', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security roles and responsibilities must include the DPO role — designation, independence, tasks and reporting line should be documented here.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.20', source_standard_id='ISO27001:2022',
        target_ref='Art.26', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Supplier agreements must include joint controller arrangements with explicit data protection obligations for each party.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.20', source_standard_id='ISO27001:2022',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Addressing information security within supplier agreements directly implements Art.28 — processor contracts must contain specific GDPR-mandated clauses (subject matter, duration, nature, purpose).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.20', source_standard_id='ISO27001:2022',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Addressing security in supplier agreements must cover international transfer safeguards — SCCs, BCRs or other Art.46 mechanisms must be reflected in data processing agreements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.22', source_standard_id='ISO27001:2022',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Monitoring, review and change management of supplier services implements the Art.28 requirement to audit processors and ensure ongoing compliance with contractual obligations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.22', source_standard_id='ISO27001:2022',
        target_ref='Art.45', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Monitoring and review of supplier services must include adequacy status of third-country recipients — a previously adequate country losing adequacy (as with US Privacy Shield) requires immediate action.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.23', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Cloud service security controls implement Art.32 appropriate technical measures for personal data in cloud environments.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.24', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Incident management planning implements Art.32.1.d ability to restore availability - a named Art.32 requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.24', source_standard_id='ISO27001:2022',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Incident management planning and preparation is the foundation for Art.33 compliance — 72-hour notification requires a pre-planned, rehearsed incident response process.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.25', source_standard_id='ISO27001:2022',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Assessment and decision on information security events implements the triage process that determines whether a breach has occurred and whether it must be notified.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.26', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Incident response directly implements Art.32.1.d resilience and restoration of processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.26', source_standard_id='ISO27001:2022',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Response to information security incidents implements the breach containment and notification workflow — includes DPA notification.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.26', source_standard_id='ISO27001:2022',
        target_ref='Art.34', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Incident response must include the data subject communication workflow — Art.34 requires notification without undue delay when breach is likely to result in high risk to subjects.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.28', source_standard_id='ISO27001:2022',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Collection of evidence supports the breach documentation requirements — Art.33(5) requires all breaches to be documented including those not notified to the DPA.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.29', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security during disruption ensures personal data remains protected and available even during crisis situations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.30', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.c', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='ICT readiness for business continuity implements the ability to restore personal data processing in a timely manner after incidents.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.10', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control must identify the specific legal basis permitting processing of criminal data — only official authorities or specific legal derogations apply.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.44', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Legal, statutory and regulatory requirements must include the transfer restrictions under Chapter V — adequacy decisions, standard contractual clauses, binding corporate rules.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.45', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control must track adequacy decisions — the list of adequate countries changes; compliance requires monitoring Commission decisions and adjusting transfer practices.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.a', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Legal, statutory, regulatory and contractual requirements control directly addresses identifying and complying with GDPR lawfulness obligations as a legal requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control is the direct ISO mechanism for identifying and documenting the lawful basis for each processing activity — a mandatory GDPR requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.85', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Legal requirements control must identify where national law derogations under Art.85 apply — journalistic, academic, artistic or literary purposes may override standard GDPR requirements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Protection of records must cover the ROPA itself as a compliance record — must be maintained, protected and available to the DPA.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.e', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Protection of records control includes retention schedules — must define and enforce GDPR-compliant retention periods.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Protection of records must cover consent records — the controller must be able to demonstrate consent was freely given and specific.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes subject access request procedures — the primary control for fulfilling DSAR identification, search, and response.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.16', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes rectification procedures for maintaining accuracy of personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes erasure procedures — the procedural side of right-to-be-forgotten alongside A.8.10 information deletion.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.18', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes processing-restriction procedures triggered by subject requests.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.19', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes recipient-notification procedures when data is rectified, erased, or restricted.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.20', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes data-portability procedures (structured machine-readable export).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.34', source_standard_id='ISO27001:2022',
        target_ref='Art.21', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='PII protection includes objection-handling procedures including opt-out flags for direct marketing/profiling.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.35', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.d', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Independent review of information security provides the formal evaluation and effectiveness assessment required by Art.32(1)(d).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.35', source_standard_id='ISO27001:2022',
        target_ref='Art.5.2', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Independent review of information security is the primary ISO mechanism for demonstrating accountability — documented, auditable.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.36', source_standard_id='ISO27001:2022',
        target_ref='Art.5.2', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Compliance with policies and standards requires documented evidence of compliance — the accountability paper trail.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Documented operating procedures must define the privacy notice process — what information is provided, when, and in what format.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Documented procedures must cover indirect data collection scenarios and the obligation to notify data subjects within one month.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='Art.19', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Documented operating procedures must include the process for notifying recipients when rectification, erasure or restriction has been applied to personal data shared with them.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='Art.22', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Documented operating procedures must define the process for human review of automated decisions when requested by data subjects.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.4', source_standard_id='ISO27001:2022',
        target_ref='Art.24', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Management responsibilities control ensures top management takes accountability for GDPR compliance — Art.24 is a governance obligation.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.4', source_standard_id='ISO27001:2022',
        target_ref='Art.38', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Management responsibilities include ensuring the DPO has access to top management and the resources to perform their tasks.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.8', source_standard_id='ISO27001:2022',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security in project management must include DPIA as a required gate for projects involving high-risk processing.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Inventory of information and associated assets is the ISO equivalent of the ROPA — must be extended to include all GDPR mandatory fields (purpose, lawful basis, retention, recipients).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.6.2', source_standard_id='ISO27001:2022',
        target_ref='Art.29', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Terms and conditions of employment must include data processing obligations — staff process personal data only on controller instructions, as required by Art.29.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.6.3', source_standard_id='ISO27001:2022',
        target_ref='Art.32.4', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information security awareness, education and training ensures staff processing personal data understand their obligations.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.10', source_standard_id='ISO27001:2022',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information deletion is the primary technical control for the right to be forgotten — secure, verifiable, complete erasure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.10', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information deletion with automated retention enforcement implements privacy by default — data deleted automatically when no longer needed.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.10', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.c', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information deletion control ensures data no longer adequate, relevant or limited is deleted — direct technical implementation of minimisation.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.10', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.e', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information deletion is the primary technical control for storage limitation — data must be deleted when retention period expires.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.11', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Data masking is a key privacy-by-default technical control — using masked/pseudonymised data by default reduces exposure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.11', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.a', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Data masking implements pseudonymisation — transforming personal data so it cannot be attributed to a data subject without additional information held separately.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.13', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.c', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information backup is the primary technical control for restoring personal data availability — must be tested, offsite, and cover recovery time objectives appropriate to the risk.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.14', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Redundancy of information processing facilities implements resilience — processing systems must withstand and recover from failures without loss of data availability.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.2', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Privileged access rights management implements Art.5.1.f integrity and confidentiality of processing.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.20', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Network security implements confidentiality and integrity in transit — personal data traversing networks must be protected.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.24', source_standard_id='ISO27001:2022',
        target_ref='Art.20', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Cryptography must protect portable personal data in transit — the exported dataset must be encrypted for transmission.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.24', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.a', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Use of cryptography is the direct implementation of the encryption requirement — must cover personal data at rest and in transit, with a documented key management procedure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.24', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.f', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Cryptography is the primary technical control for integrity and confidentiality of personal data — encryption at rest and in transit.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.24', source_standard_id='ISO27001:2022',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Cryptography applies with heightened urgency to special category data — encryption at rest and in transit is effectively mandatory.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.25', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Secure development lifecycle is the ISO mechanism for embedding privacy by design — security and privacy requirements built in from the start of development, not bolted on afterwards.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.26', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Application security requirements must include data minimisation, purpose limitation and subject rights as functional requirements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.27', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Secure system architecture and engineering principles implement privacy by design at the architectural level.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.29', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.d', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Security testing in development and acceptance implements systematic testing of technical measures protecting personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.3', source_standard_id='ISO27001:2022',
        target_ref='Art.10', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction must limit access to criminal convictions data to only those with an explicit legal basis to process it — most restrictive access tier.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.3', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction implements confidentiality at the data level — users access only the personal data they need.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.3', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.f', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction implements need-to-know principle for personal data — direct confidentiality control.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.3', source_standard_id='ISO27001:2022',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Information access restriction must enforce stricter access controls for special category data — need-to-know at highest level.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.5', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Secure authentication is an explicit technical measure for Art.32 security of processing.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.5', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.f', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Secure authentication prevents unauthorised access to personal data processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.7', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.b', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Protection against malware directly implements integrity and availability of personal data processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.7', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.f', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Protection against malware prevents integrity violations and confidentiality breaches affecting personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.8', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.d', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='Management of technical vulnerabilities requires regular assessment of security weaknesses — directly implements testing requirement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.12', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Legal requirements include GDPR\'s transparency obligations and prescribed response timeframes (one month, extendable to three).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.12', source_standard_id='GDPR:2016/679',
        target_ref='A.5.37', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Documented operating procedures must cover data subject communication processes — timely, clear responses to subject requests.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.15', source_standard_id='GDPR:2016/679',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Records of processing activities (Art.30) provide the structured information required to respond to subject access requests.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.16', source_standard_id='GDPR:2016/679',
        target_ref='A.8.13', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Backup systems must accommodate rectification requests — corrections should propagate to backup copies where technically feasible.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.16', source_standard_id='GDPR:2016/679',
        target_ref='A.8.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Configuration management of data processing systems must support amendment of personal data records on subject request.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.17', source_standard_id='GDPR:2016/679',
        target_ref='A.7.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Secure disposal of equipment must ensure deleted personal data is not recoverable from decommissioned storage media.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.17', source_standard_id='GDPR:2016/679',
        target_ref='A.8.13', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Backup management must address erasure requests — controller must consider whether backup copies must also be erased or overwritten.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.22', source_standard_id='GDPR:2016/679',
        target_ref='A.8.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Configuration management of automated decision systems must document the logic used for profiling and automated decisions.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.24', source_standard_id='GDPR:2016/679',
        target_ref='9.3', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Management review produces documented evidence of top management\'s ongoing accountability for information security and data protection.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.25', source_standard_id='GDPR:2016/679',
        target_ref='A.5.8', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Information security in project management ensures privacy requirements are considered for every project involving personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.28', source_standard_id='GDPR:2016/679',
        target_ref='A.5.21', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Managing security in the ICT supply chain extends processor oversight to sub-processors — Art.28 requires controller approval for sub-processor engagements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.29', source_standard_id='GDPR:2016/679',
        target_ref='A.5.2', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Defined information security roles and responsibilities implement the chain of authority required by Art.29.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.29', source_standard_id='GDPR:2016/679',
        target_ref='A.6.3', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Information security awareness and training must cover Art.29 obligations — staff must understand they process data only on documented controller instructions.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.30', source_standard_id='GDPR:2016/679',
        target_ref='A.5.37', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Documented operating procedures must include the ROPA maintenance process — how often reviewed, who updates it, change control.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.32', source_standard_id='GDPR:2016/679',
        target_ref='A.5.1', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Information security policies provide the documented framework for \'appropriate technical and organisational measures\'.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.c', source_standard_id='GDPR:2016/679',
        target_ref='A.8.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Redundancy prevents the need for restoration in many failure scenarios — a complement to backup/recovery.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.1.d', source_standard_id='GDPR:2016/679',
        target_ref='A.8.16', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Monitoring activities provides continuous testing of security measures — anomaly detection and security event monitoring.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.4', source_standard_id='GDPR:2016/679',
        target_ref='A.6.2', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Terms and conditions of employment embed data processing obligations contractually — staff bound to process only on instructions.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32.4', source_standard_id='GDPR:2016/679',
        target_ref='A.6.4', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Disciplinary process applies where staff violate personal data processing obligations — deterrence and accountability.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.34', source_standard_id='GDPR:2016/679',
        target_ref='A.5.24', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Incident management planning must pre-define the criteria and process for data subject notification — cannot be improvised during a live breach response.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Legal requirements control must include DPIA obligations — identifying when a DPIA is legally required (profiling, systematic monitoring, large-scale special category processing).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.35', source_standard_id='GDPR:2016/679',
        target_ref='A.8.25', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Secure development lifecycle must integrate DPIA as a mandatory step for new systems processing personal data at high risk.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.37', source_standard_id='GDPR:2016/679',
        target_ref='A.5.4', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Management responsibilities must include the DPO in governance structures — top management must ensure DPO has resources and access required by Arts.37-39.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.38', source_standard_id='GDPR:2016/679',
        target_ref='A.5.3', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Segregation of duties supports DPO independence — the DPO must not be in a position that creates a conflict of interest with their data protection oversight role.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.45', source_standard_id='GDPR:2016/679',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Supplier relationship security must assess transfer destinations for adequacy before personal data is shared internationally.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.46', source_standard_id='GDPR:2016/679',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Supplier relationship security must assess third-country processors for GDPR transfer compliance — adequacy or safeguards in place.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.a', source_standard_id='GDPR:2016/679',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Compliance with policies, rules and standards ensures lawfulness obligations are embedded in operational procedures.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.b', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Asset inventory must record processing purposes for each personal data asset — foundational requirement for purpose limitation.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.c', source_standard_id='GDPR:2016/679',
        target_ref='A.8.11', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Data masking reduces personal data exposure in non-production environments, supporting minimisation in test/dev contexts.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.d', source_standard_id='GDPR:2016/679',
        target_ref='A.8.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Configuration management principles apply to data quality controls in processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='low',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.e', source_standard_id='GDPR:2016/679',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Legal requirements control encompasses retention obligations under GDPR and intersecting national retention laws.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.f', source_standard_id='GDPR:2016/679',
        target_ref='A.8.15', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Logging provides audit trail demonstrating integrity of personal data processing and detecting confidentiality breaches.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.2', source_standard_id='GDPR:2016/679',
        target_ref='9.3', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Management review demonstrates top management accountability for GDPR compliance at governance level.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.7', source_standard_id='GDPR:2016/679',
        target_ref='A.8.15', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Logging of consent capture events creates the audit trail demonstrating consent was obtained at the right time.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.83', source_standard_id='GDPR:2016/679',
        target_ref='A.5.35', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Independent review produces the documented evidence that demonstrates compliance — the audit trail that mitigates regulatory enforcement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.83', source_standard_id='GDPR:2016/679',
        target_ref='A.5.36', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Compliance with policies and standards is what Art.83 ultimately rewards — demonstrated compliance reduces administrative fines under the \'effectiveness of measures taken\' assessment.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.9', source_standard_id='GDPR:2016/679',
        target_ref='A.8.11', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Data masking is particularly important for special category data in test, analytics and reporting environments.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='9.3', source_standard_id='ISO27001:2022',
        target_ref='Art.24', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Management review produces documented evidence of top management\'s ongoing accountability for information security and data protection.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='9.3', source_standard_id='ISO27001:2022',
        target_ref='Art.5.2', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Management review demonstrates top management accountability for GDPR compliance at governance level.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.1', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Information security policies provide the documented framework for \'appropriate technical and organisational measures\'.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.12', source_standard_id='ISO27001:2022',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Information classification identifies categories of personal data, supporting Art.30 records of processing activities.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.18', source_standard_id='ISO27001:2022',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Access revocation processes support implementation of Art.17 right to erasure.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.19', source_standard_id='ISO27001:2022',
        target_ref='Art.45', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Supplier relationship security must assess transfer destinations for adequacy before personal data is shared internationally.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.19', source_standard_id='ISO27001:2022',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Supplier relationship security must assess third-country processors for GDPR transfer compliance — adequacy or safeguards in place.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.2', source_standard_id='ISO27001:2022',
        target_ref='Art.29', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Defined information security roles and responsibilities implement the chain of authority required by Art.29.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.21', source_standard_id='ISO27001:2022',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Managing security in the ICT supply chain extends processor oversight to sub-processors — Art.28 requires controller approval for sub-processor engagements.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.24', source_standard_id='ISO27001:2022',
        target_ref='Art.34', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Incident management planning must pre-define the criteria and process for data subject notification — cannot be improvised during a live breach response.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.3', source_standard_id='ISO27001:2022',
        target_ref='Art.38', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Segregation of duties supports DPO independence — the DPO must not be in a position that creates a conflict of interest with their data protection oversight role.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.12', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Legal requirements include GDPR\'s transparency obligations and prescribed response timeframes (one month, extendable to three).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Legal requirements control must include DPIA obligations — identifying when a DPIA is legally required (profiling, systematic monitoring, large-scale special category processing).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.e', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Legal requirements control encompasses retention obligations under GDPR and intersecting national retention laws.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.31', source_standard_id='ISO27001:2022',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Compliance with legal requirements includes maintaining consent records and processes required by Art.7.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.33', source_standard_id='ISO27001:2022',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Records of processing activities (Art.30) provide the structured information required to respond to subject access requests.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.35', source_standard_id='ISO27001:2022',
        target_ref='Art.83', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Independent review produces the documented evidence that demonstrates compliance — the audit trail that mitigates regulatory enforcement.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.36', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.a', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Compliance with policies, rules and standards ensures lawfulness obligations are embedded in operational procedures.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.36', source_standard_id='ISO27001:2022',
        target_ref='Art.83', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Compliance with policies and standards is what Art.83 ultimately rewards — demonstrated compliance reduces administrative fines under the \'effectiveness of measures taken\' assessment.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='Art.12', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Documented operating procedures must cover data subject communication processes — timely, clear responses to subject requests.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.37', source_standard_id='ISO27001:2022',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Documented operating procedures must include the ROPA maintenance process — how often reviewed, who updates it, change control.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.4', source_standard_id='ISO27001:2022',
        target_ref='Art.37', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Management responsibilities must include the DPO in governance structures — top management must ensure DPO has resources and access required by Arts.37-39.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.8', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Information security in project management ensures privacy requirements are considered for every project involving personal data.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.b', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Asset inventory must record processing purposes for each personal data asset — foundational requirement for purpose limitation.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.6.2', source_standard_id='ISO27001:2022',
        target_ref='Art.32.4', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Terms and conditions of employment embed data processing obligations contractually — staff bound to process only on instructions.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.6.3', source_standard_id='ISO27001:2022',
        target_ref='Art.29', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Information security awareness and training must cover Art.29 obligations — staff must understand they process data only on documented controller instructions.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.6.4', source_standard_id='ISO27001:2022',
        target_ref='Art.32.4', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Disciplinary process applies where staff violate personal data processing obligations — deterrence and accountability.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.14', source_standard_id='ISO27001:2022',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Secure disposal of equipment must ensure deleted personal data is not recoverable from decommissioned storage media.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.11', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.c', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Data masking reduces personal data exposure in non-production environments, supporting minimisation in test/dev contexts.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.11', source_standard_id='ISO27001:2022',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Data masking is particularly important for special category data in test, analytics and reporting environments.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.12', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Data masking implements Art.5.1.c data minimisation and Art.5.1.e storage limitation principles.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.13', source_standard_id='ISO27001:2022',
        target_ref='Art.16', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Backup systems must accommodate rectification requests — corrections should propagate to backup copies where technically feasible.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.13', source_standard_id='ISO27001:2022',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Backup management must address erasure requests — controller must consider whether backup copies must also be erased or overwritten.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.14', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.c', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Redundancy prevents the need for restoration in many failure scenarios — a complement to backup/recovery.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.15', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.f', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Logging provides audit trail demonstrating integrity of personal data processing and detecting confidentiality breaches.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.15', source_standard_id='ISO27001:2022',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Logging of consent capture events creates the audit trail demonstrating consent was obtained at the right time.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.16', source_standard_id='ISO27001:2022',
        target_ref='Art.32.1.d', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Monitoring activities provides continuous testing of security measures — anomaly detection and security event monitoring.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.25', source_standard_id='ISO27001:2022',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Secure development lifecycle must integrate DPIA as a mandatory step for new systems processing personal data at high risk.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.9', source_standard_id='ISO27001:2022',
        target_ref='Art.16', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Configuration management of data processing systems must support amendment of personal data records on subject request.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.9', source_standard_id='ISO27001:2022',
        target_ref='Art.22', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Configuration management of automated decision systems must document the logic used for profiling and automated decisions.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.9', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.d', target_standard_id='GDPR:2016/679',
        edge_type='SUPPORTS',
        rationale='Configuration management principles apply to data quality controls in processing systems.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='low',
    ),
    RelationshipEdge(
        source_ref='Art.10', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory must specifically flag criminal convictions data assets to ensure additional controls are applied.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.13', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory of personal data processing activities is the source from which privacy notice content is derived.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.14', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory must capture sources of indirectly obtained data to identify where Art.14 notification obligations apply.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='A.6.8', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Information security event reporting by staff is the detection mechanism — staff must report potential breaches immediately to enable the 72-hour clock to start from awareness, not occurrence.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.33', source_standard_id='GDPR:2016/679',
        target_ref='A.8.15', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Logging provides the forensic trail needed to characterise a breach for the mandatory notification content (categories affected, approximate number of records, likely consequences).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.c', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory identifies all personal data holdings — prerequisite to assessing adequacy, relevance and necessity of each dataset.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5.1.d', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory with data quality metadata supports accuracy obligations by tracking data sources and update frequency.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory must record the lawful basis for each personal data asset — foundational for demonstrating Art.6 compliance.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.7', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory must track consent status per data subject and processing activity — prerequisite for consent management.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.7', source_standard_id='GDPR:2016/679',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Information deletion enables withdrawal of consent — when consent is withdrawn, personal data must be deletable on request.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.9', source_standard_id='GDPR:2016/679',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='ENABLES',
        rationale='Asset inventory must specifically flag special category data assets for additional controls and oversight.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.10', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory must specifically flag criminal convictions data assets to ensure additional controls are applied.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory of personal data processing activities is the source from which privacy notice content is derived.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory must capture sources of indirectly obtained data to identify where Art.14 notification obligations apply.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.c', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory identifies all personal data holdings — prerequisite to assessing adequacy, relevance and necessity of each dataset.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.5.1.d', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory with data quality metadata supports accuracy obligations by tracking data sources and update frequency.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory must record the lawful basis for each personal data asset — foundational for demonstrating Art.6 compliance.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory must track consent status per data subject and processing activity — prerequisite for consent management.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.5.9', source_standard_id='ISO27001:2022',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Asset inventory must specifically flag special category data assets for additional controls and oversight.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.6.8', source_standard_id='ISO27001:2022',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Information security event reporting by staff is the detection mechanism — staff must report potential breaches immediately to enable the 72-hour clock to start from awareness, not occurrence.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.10', source_standard_id='ISO27001:2022',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Information deletion enables withdrawal of consent — when consent is withdrawn, personal data must be deletable on request.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.15', source_standard_id='ISO27001:2022',
        target_ref='Art.33', target_standard_id='GDPR:2016/679',
        edge_type='ENABLES',
        rationale='Logging provides the forensic trail needed to characterise a breach for the mandatory notification content (categories affected, approximate number of records, likely consequences).',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.22', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Risk assessment must evaluate risks of automated decision-making including profiling — Art.22 requires DPIA in many cases.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.32', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Risk assessment is the explicit mechanism Art.32 requires — \'appropriate to the risk\' means a documented risk assessment must justify the measures chosen. ISO 6.1.2 is the framework.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5', source_standard_id='GDPR:2016/679',
        target_ref='4.1', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Understanding the organisation\'s context is the foundation for determining how GDPR principles apply to the business.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5', source_standard_id='GDPR:2016/679',
        target_ref='A.5.2', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Information security policy must encompass data protection principles; accountability under Art.5(2) requires documented policy commitment.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.5', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Risk assessment process identifies and addresses risks to personal data principles — the ISO mechanism for systematic GDPR compliance.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.6', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Risk assessment must consider lawfulness risks — processing without a legal basis is a high-probability, high-impact risk.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='Art.85', source_standard_id='GDPR:2016/679',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='GOVERNANCE',
        rationale='Risk assessment should consider Art.85 scenarios where the organisation\'s activities involve expression or information rights that may conflict with data subject rights.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='low',
    ),
    RelationshipEdge(
        source_ref='4.1', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Understanding the organisation\'s context is the foundation for determining how GDPR principles apply to the business.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.22', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Risk assessment must evaluate risks of automated decision-making including profiling — Art.22 requires DPIA in many cases.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Risk assessment is the explicit mechanism Art.32 requires — \'appropriate to the risk\' means a documented risk assessment must justify the measures chosen. ISO 6.1.2 is the framework.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Risk assessment process identifies and addresses risks to personal data principles — the ISO mechanism for systematic GDPR compliance.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Risk assessment must consider lawfulness risks — processing without a legal basis is a high-probability, high-impact risk.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='6.1.2', source_standard_id='ISO27001:2022',
        target_ref='Art.85', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Risk assessment should consider Art.85 scenarios where the organisation\'s activities involve expression or information rights that may conflict with data subject rights.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='low',
    ),
    RelationshipEdge(
        source_ref='A.5.2', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='GOVERNANCE',
        rationale='Information security policy must encompass data protection principles; accountability under Art.5(2) requires documented policy commitment.',
        citation='iso_nodes_phase1.json + gdpr_nodes_phase2.json (cross_framework_summary)',
        role='high',
    ),
]


# ── ISO 27701:2019 Batch 1 bridges — Conditions for collection + processing ──
# Two edge sets:
#   SUPPORTS   27701 → 27001 parent controls (where 27701 augments an existing
#              ISO 27001 control — mainly supplier/contract territory for
#              A.7.2.6 + B.8.2.1)
#   IMPLEMENTS 27701 → GDPR Article per Annex D Table D.1 (article-level
#              bridges; Annex D cites subclauses like (28)(3)(a) but the
#              current catalog uses Article-level nodes)
# Author: 2026-07-03. Batch 1 = §A.7.2.x controller side + §B.8.2.x processor
# side. Subsequent batches extend the edge set.

ISO27701_BATCH1_EDGES: list[RelationshipEdge] = [
    # ── SUPPORTS 27701 → 27001 ────────────────────────────────────────────────
    # A.7.2.6 contracts with PII processors ↔ ISO 27001 A.5.19-23 supplier controls
    RelationshipEdge(
        source_ref='A.7.2.6', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.6 privacy-augments the general supplier information-security policy at 27001 A.5.19 with the additional Art.28-alignment terms + Annex B implementation requirement.',
        citation='ISO/IEC 27701:2019 §7.2.6 + ISO/IEC 27002:2022 §5.19',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.6', source_standard_id='ISO27701:2019',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.6 privacy-augments 27001 A.5.20 addressing information security within supplier agreements — adds the Art.28 processor-specific contract terms.',
        citation='ISO/IEC 27701:2019 §7.2.6 + ISO/IEC 27002:2022 §5.20',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.6', source_standard_id='ISO27701:2019',
        target_ref='A.5.22', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.6 supports 27001 A.5.22 monitoring, review and change management of supplier services — processor contracts are the vehicle for the review + audit rights.',
        citation='ISO/IEC 27701:2019 §7.2.6 + ISO/IEC 27002:2022 §5.22',
        role='medium',
    ),
    # B.8.2.1 customer agreement ↔ 27001 A.5.19-23 supplier controls (processor's mirror)
    RelationshipEdge(
        source_ref='B.8.2.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.2.1 mirrors 27001 A.5.19 from the processor side — the customer agreement is the supplier-relationship equivalent for the processor.',
        citation='ISO/IEC 27701:2019 §8.2.1 + ISO/IEC 27002:2022 §5.19',
        role='high',
    ),
    # A.7.2.8 records of processing ↔ 27001 A.5.9 asset register (records program)
    RelationshipEdge(
        source_ref='A.7.2.8', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.8 RoPA is a records-program artefact analogous to 27001 A.5.9 asset register — same records-program spine, differs by scope (PII processing activities vs information/associated assets).',
        citation='ISO/IEC 27701:2019 §7.2.8 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),
    # B.8.2.6 processor RoPA ↔ 27001 A.5.9
    RelationshipEdge(
        source_ref='B.8.2.6', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.2.6 processor RoPA is the processor-side records-program artefact analogous to 27001 A.5.9 asset register.',
        citation='ISO/IEC 27701:2019 §8.2.6 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),

    # ── IMPLEMENTS 27701 → GDPR (per Annex D Table D.1) ───────────────────────
    # A.7.2.1 Identify and document purpose → Art.5 (purpose limitation) + Art.32.4 (processor instructions)
    RelationshipEdge(
        source_ref='A.7.2.1', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.1 operationalises GDPR Art.5.1.b purpose limitation — the specific purposes principle must be documented before processing begins.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.1 → (5)(1)(b), (32)(4)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.1', source_standard_id='ISO27701:2019',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.1 supports GDPR Art.32.4 — processors act only on documented instructions from the controller including on stated purposes.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.1 → (32)(4)',
        role='medium',
    ),
    # A.7.2.2 Identify lawful basis → Art.5, Art.6, Art.9, Art.10 (extensive per Annex D)
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.2 operationalises GDPR Art.5.1.a lawfulness principle — every processing activity must have a documented lawful basis.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.2 → (5)(1)(a), (10)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.2 is the certifiable operationalisation of GDPR Art.6 lawfulness of processing — determining + documenting the Art.6.1.a-f basis per activity.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.2 → (6)(1)(a-f), (6)(2), (6)(3), (6)(4)(a-e)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.8', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.2 covers Art.8.3 — Member State children-consent age variations factor into the basis catalog.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.2 → (8)(3)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.2 covers special-category dual-basis requirement — Art.9.2.a-j basis in addition to Art.6.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.2 → (9)(1), (9)(2)(a-j), (9)(3), (9)(4)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.22', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.2 covers Art.22.2 — automated decision-making requires specific basis (contract necessity / MS law / explicit consent) as part of the lawful basis catalog.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.2 → (22)(2)(a-c), (22)(4)',
        role='medium',
    ),
    # A.7.2.3 Determine consent process → Art.8 (children)
    RelationshipEdge(
        source_ref='A.7.2.3', source_standard_id='ISO27701:2019',
        target_ref='Art.8', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.3 operationalises GDPR Art.8 — determining when child-consent (with parental authorisation where applicable) is required.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.3 → (8)(1), (8)(2)',
        role='high',
    ),
    # A.7.2.4 Obtain + record consent → Art.7 (conditions for consent) + Art.9 (explicit consent for Art.9 data)
    RelationshipEdge(
        source_ref='A.7.2.4', source_standard_id='ISO27701:2019',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.4 is the certifiable operationalisation of GDPR Art.7 conditions for consent — demonstrable, freely given, specific, unambiguous.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.4 → (7)(1), (7)(2)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.4', source_standard_id='ISO27701:2019',
        target_ref='Art.9', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.4 covers Art.9.2.a explicit consent for special-category data.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.4 → (9)(2)(a)',
        role='medium',
    ),
    # A.7.2.5 PIA/DPIA → Art.35 (DPIA) + Art.36 (Prior consultation)
    RelationshipEdge(
        source_ref='A.7.2.5', source_standard_id='ISO27701:2019',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.5 is the certifiable operationalisation of GDPR Art.35 Data Protection Impact Assessment — triggers, assessment scope, mitigations, DPO opinion.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.5 → (35)(1-11)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.5', source_standard_id='ISO27701:2019',
        target_ref='Art.36', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.5 operationalises GDPR Art.36 prior consultation — where residual high risk remains after DPIA, SA is consulted.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.5 → (36)(1), (36)(3)(a-f), (36)(5)',
        role='high',
    ),
    # A.7.2.6 Contracts with PII processors → Art.5 (Art.5.2 accountability) + Art.28 (processor)
    RelationshipEdge(
        source_ref='A.7.2.6', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.6 supports GDPR Art.5.2 accountability — the written contract is a demonstration artefact.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.6 → (5)(2)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.2.6', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.6 is the certifiable operationalisation of GDPR Art.28 processor — mandatory Art.28.3 contract terms + Art.28.9 written form.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.6 → (28)(3)(e), (28)(9)',
        role='high',
    ),
    # A.7.2.7 Joint PII controller → Art.26
    RelationshipEdge(
        source_ref='A.7.2.7', source_standard_id='ISO27701:2019',
        target_ref='Art.26', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.7 is the certifiable operationalisation of GDPR Art.26 joint controllers — arrangement + essence publication + subject rights against either party.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.7 → (26)(1), (26)(2), (26)(3)',
        role='high',
    ),
    # A.7.2.8 Records of processing → Art.5 (Art.5.2 accountability) + Art.24 (controller responsibility) + Art.30 (records)
    RelationshipEdge(
        source_ref='A.7.2.8', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.8 supports GDPR Art.5.2 accountability — RoPA is a core accountability demonstration artefact.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.8 → (5)(2)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.2.8', source_standard_id='ISO27701:2019',
        target_ref='Art.24', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.8 supports GDPR Art.24.1 — RoPA demonstrates controller has implemented appropriate technical + organizational measures.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.8 → (24)(1)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.2.8', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.2.8 is the certifiable operationalisation of GDPR Art.30.1 controller Records of Processing Activities.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 7.2.8 → (30)(1)(a-g), (30)(3), (30)(4), (30)(5)',
        role='high',
    ),
    # B.8.2.1 Customer agreement → Art.28 + Art.35 (customer DPIA support)
    RelationshipEdge(
        source_ref='B.8.2.1', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.1 operationalises GDPR Art.28.3.e + Art.28.3.f + Art.28.9 — processor contract addressing assistance with subject rights + security of processing, in writing.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.1 → (28)(3)(e), (28)(3)(f), (28)(9)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.2.1', source_standard_id='ISO27701:2019',
        target_ref='Art.35', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.1 covers Art.35.1 processor DPIA support obligation.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.1 → (35)(1)',
        role='medium',
    ),
    # B.8.2.2 Organization's purposes → Art.5 + Art.28 + Art.29 + Art.32
    RelationshipEdge(
        source_ref='B.8.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.2 operationalises GDPR Art.5.1.a lawfulness + Art.5.1.b purpose limitation from processor side.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.2 → (5)(1)(a), (5)(1)(b)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.2 is the certifiable operationalisation of GDPR Art.28.3.a — processor acts only on documented instructions.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.2 → (28)(3)(a)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.29', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.2 operationalises GDPR Art.29 — processor + anyone acting under its authority processes PII only on controller instructions.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.2 → (29)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.2.2', source_standard_id='ISO27701:2019',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.2 supports Art.32.4 — processor + persons acting under its authority only process on instructions.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.2 → (32)(4)',
        role='medium',
    ),
    # B.8.2.3 Marketing/advertising use → Art.7
    RelationshipEdge(
        source_ref='B.8.2.3', source_standard_id='ISO27701:2019',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.3 operationalises GDPR Art.7.4 — consent for processing not freely given if service is conditional on consent for unrelated processing.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.3 → (7)(4)',
        role='high',
    ),
    # B.8.2.4 Infringing instruction → Art.28
    RelationshipEdge(
        source_ref='B.8.2.4', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.4 operationalises GDPR Art.28.3.h — processor immediately informs controller if an instruction infringes GDPR or applicable law.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.4 → (28)(3)(h)',
        role='high',
    ),
    # B.8.2.5 Customer obligations → Art.28
    RelationshipEdge(
        source_ref='B.8.2.5', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.5 operationalises GDPR Art.28.3.h — processor makes available information necessary to demonstrate controller compliance + contributes to audits.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.5 → (28)(3)(h)',
        role='high',
    ),
    # B.8.2.6 Records related to processing → Art.30 (Art.30.2 processor RoPA)
    RelationshipEdge(
        source_ref='B.8.2.6', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.2.6 is the certifiable operationalisation of GDPR Art.30.2 processor Records of Processing Activities.',
        citation='ISO/IEC 27701:2019 Annex D Table D.1 — 8.2.6 → (30)(3), (30)(4), (30)(5), (30)(2)(a), (30)(2)(b)',
        role='high',
    ),
]


# ── ISO 27701:2019 Batch 2 bridges — Obligations to PII principals + PbD ────
# 23 anchors: §A.7.3.1-10 subject rights + §A.7.4.1-9 privacy by design +
# §B.8.3.1 processor obligations support + §B.8.4.1-3 processor PbD.
# Bridges per Annex D Table D.1 (Article-level, since catalog uses Article
# nodes not subclause nodes).
# Author: 2026-07-04.

ISO27701_BATCH2_EDGES: list[RelationshipEdge] = [
    # ── SUPPORTS 27701 → 27001 (privacy augments existing security control) ──
    # A.7.3.6 access/correction/erasure ↔ A.8.10 information deletion (erasure implementation)
    RelationshipEdge(
        source_ref='A.7.3.6', source_standard_id='ISO27701:2019',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.6 erasure right rides on top of 27001 A.8.10 information deletion — the operational deletion capability is the technical implementation of the privacy right.',
        citation='ISO/IEC 27701:2019 §7.3.6 + ISO/IEC 27002:2022 §8.10',
        role='high',
    ),
    # A.7.4.5 end-of-processing ↔ A.8.10 information deletion + A.5.9 asset register
    RelationshipEdge(
        source_ref='A.7.4.5', source_standard_id='ISO27701:2019',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.5 delete-or-deidentify at end of processing uses 27001 A.8.10 information deletion as the operational vehicle.',
        citation='ISO/IEC 27701:2019 §7.4.5 + ISO/IEC 27002:2022 §8.10',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.5', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.5 requires reconciling with the asset/data inventory to ensure all copies deleted — asset register (27001 A.5.9) is the reconciliation source.',
        citation='ISO/IEC 27701:2019 §7.4.5 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),
    # A.7.4.7 retention ↔ A.5.33 records retention (both are storage-limitation controls)
    RelationshipEdge(
        source_ref='A.7.4.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.33', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.7 PII retention schedules coexist with 27001 A.5.33 records protection retention — cross-frame coherence required.',
        citation='ISO/IEC 27701:2019 §7.4.7 + ISO/IEC 27002:2022 §5.33',
        role='high',
    ),
    # A.7.4.8 disposal ↔ A.5.28 information handling + A.7.14 secure disposal of equipment
    RelationshipEdge(
        source_ref='A.7.4.8', source_standard_id='ISO27701:2019',
        target_ref='A.5.28', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.8 PII disposal reuses 27001 A.5.28 evidence-handling disposal_record shape.',
        citation='ISO/IEC 27701:2019 §7.4.8 + ISO/IEC 27002:2022 §5.28',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.8', source_standard_id='ISO27701:2019',
        target_ref='A.7.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.8 physical media disposal covered by 27001 A.7.14 secure disposal/reuse of equipment.',
        citation='ISO/IEC 27701:2019 §7.4.8 + ISO/IEC 27002:2022 §7.14',
        role='medium',
    ),
    # A.7.4.9 transmission controls ↔ A.5.14 information transfer + A.8.24 cryptography
    RelationshipEdge(
        source_ref='A.7.4.9', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.9 PII transmission augments 27001 A.5.14 information transfer with privacy-specific controls (audit logs of PII transmissions).',
        citation='ISO/IEC 27701:2019 §7.4.9 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.9', source_standard_id='ISO27701:2019',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.9 encryption-in-transit uses 27001 A.8.24 cryptography as the implementation vehicle.',
        citation='ISO/IEC 27701:2019 §7.4.9 + ISO/IEC 27002:2022 §8.24',
        role='high',
    ),
    # B.8.4.2 return/transfer/disposal (processor side) ↔ A.5.19 supplier + A.5.28 disposal
    RelationshipEdge(
        source_ref='B.8.4.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.4.2 end-of-service PII handling operates within 27001 A.5.19 supplier relationships policy (processor-side).',
        citation='ISO/IEC 27701:2019 §8.4.2 + ISO/IEC 27002:2022 §5.19',
        role='medium',
    ),
    # B.8.4.3 transmission (processor side) ↔ A.5.14 + A.8.24
    RelationshipEdge(
        source_ref='B.8.4.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.4.3 processor-side transmission mirrors A.7.4.9 controller-side — augments 27001 A.5.14 information transfer.',
        citation='ISO/IEC 27701:2019 §8.4.3 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.4.3', source_standard_id='ISO27701:2019',
        target_ref='A.8.24', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.4.3 encryption-in-transit uses 27001 A.8.24 cryptography.',
        citation='ISO/IEC 27701:2019 §8.4.3 + ISO/IEC 27002:2022 §8.24',
        role='high',
    ),

    # ── IMPLEMENTS 27701 → GDPR (per Annex D Table D.1) ────────────────────
    # §A.7.3.x subject rights → Art.11-22
    RelationshipEdge(
        source_ref='A.7.3.1', source_standard_id='ISO27701:2019',
        target_ref='Art.12', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.1 operationalises GDPR Art.12 — transparent information provision, communication + modalities for exercise of rights.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.1 → (12)(2)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.2', source_standard_id='ISO27701:2019',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.2 determines the information provided to subjects — direct-collection Art.13 fields.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.2 → (13)(1)(a-f), (13)(2)(c-e), (13)(3)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.2', source_standard_id='ISO27701:2019',
        target_ref='Art.14', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.2 also covers Art.14 indirect-collection additional fields (source of PII).',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.2 → (14)(1)(a-f), (14)(2)(b-f), (14)(3-5)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.3', source_standard_id='ISO27701:2019',
        target_ref='Art.12', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.3 delivery of notice operationalises Art.12.1 concise, transparent, intelligible + easily accessible form.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.3 → (12)(1), (12)(7)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.3', source_standard_id='ISO27701:2019',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.3 timing of provision — at time of collection per Art.13.3.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.3 → (13)(3)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.3.4', source_standard_id='ISO27701:2019',
        target_ref='Art.7', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.4 consent withdrawal mechanism operationalises Art.7.3 — as easy to withdraw as to give consent.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.4 → (7)(3)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.4', source_standard_id='ISO27701:2019',
        target_ref='Art.18', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.4 modification of consent covers Art.18 restriction of processing scenarios.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.4 → (18)(1)(a-d)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.3.5', source_standard_id='ISO27701:2019',
        target_ref='Art.21', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.5 objection mechanism is the certifiable operationalisation of Art.21 right to object.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.5 → (21)(1-6)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.6', source_standard_id='ISO27701:2019',
        target_ref='Art.16', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.6 correction operationalises Art.16 rectification.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.6 → (16)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.6', source_standard_id='ISO27701:2019',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.6 erasure operationalises Art.17 right to erasure.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.6 → (17)(1)(a-f), (17)(2)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.6', source_standard_id='ISO27701:2019',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.6 access operationalises Art.15 right of access.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.6 → (15)(1)(a-h), (15)(2), (18)(3)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.7', source_standard_id='ISO27701:2019',
        target_ref='Art.19', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.7 is the certifiable operationalisation of Art.19 notification obligation regarding rectification/erasure/restriction.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.7 → (19)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.8', source_standard_id='ISO27701:2019',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.8 provides copy of PII per Art.15.3.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.8 → (15)(3), (15)(4)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.8', source_standard_id='ISO27701:2019',
        target_ref='Art.20', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.8 structured commonly-used machine-readable format aligns with Art.20 portability.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.8 → (20)(1-4)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.9', source_standard_id='ISO27701:2019',
        target_ref='Art.12', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.9 request handling operationalises Art.12 modalities for exercise of rights + response-time obligations.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.9 → (12)(3-6)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.10', source_standard_id='ISO27701:2019',
        target_ref='Art.22', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.10 covers subject-facing obligations for automated decision-making — Art.22.1 + Art.22.3 human intervention + Art.22.4 explicit consent for Art.9 data.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.10 → (22)(1), (22)(3)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.10', source_standard_id='ISO27701:2019',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.3.10 notification of existence — Art.13.2.f + Art.14.2.g automated-decision disclosure at collection.',
        citation='ISO/IEC 27701:2019 Annex D — 7.3.10 → (13)(2)(f)',
        role='medium',
    ),

    # §A.7.4.x privacy by design + default → Art.5 + Art.25 + Art.32
    RelationshipEdge(
        source_ref='A.7.4.1', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.1 collection limitation operationalises Art.5.1.b purpose limitation + Art.5.1.c data minimisation.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.1 → (5)(1)(b), (5)(1)(c)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.2', source_standard_id='ISO27701:2019',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.2 processing limitation implements Art.25.2 privacy by default — only PII necessary for each specific purpose processed by default.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.2 → (25)(2)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.3', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.3 accuracy operationalises Art.5.1.d accuracy principle.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.3 → (5)(1)(d)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.4', source_standard_id='ISO27701:2019',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.4 minimisation objectives operationalise Art.25.1 privacy by design — pseudonymisation + data minimisation techniques.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.4 → (25)(1)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.4', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.4 minimisation operationalises Art.5.1.c data minimisation + Art.5.1.e storage limitation.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.4 → (5)(1)(c), (5)(1)(e)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.4.5', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.5 end-of-processing deletion / de-identification operationalises Art.5.1.c minimisation + Art.5.1.e storage limitation.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.5 → (5)(1)(c), (5)(1)(e)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.5', source_standard_id='ISO27701:2019',
        target_ref='Art.6', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.5 supports Art.6.4.e — compatibility test via de-identification for further processing.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.5 → (6)(4)(e)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.4.5', source_standard_id='ISO27701:2019',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.5 de-identification operationalises Art.32.1.a pseudonymisation as a security measure.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.5 → (32)(1)(a)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.4.6', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.6 temp file disposal supports Art.5.1.c minimisation applied to transient PII.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.6 → (5)(1)(c)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.4.7', source_standard_id='ISO27701:2019',
        target_ref='Art.13', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.7 retention schedules underpin Art.13.2.a storage period disclosure.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.7 → (13)(2)(a), (14)(2)(a)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.8', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.8 disposal operationalises Art.5.1.f integrity + confidentiality — secure destruction eliminates residual risk.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.8 → (5)(1)(f)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.9', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.9 transmission controls operationalise Art.5.1.f integrity + confidentiality.',
        citation='ISO/IEC 27701:2019 Annex D — 7.4.9 → (5)(1)(f)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.9', source_standard_id='ISO27701:2019',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.4.9 encryption-in-transit operationalises Art.32.1.a security of processing pseudonymisation + encryption.',
        citation='ISO/IEC 27701:2019 Annex D + Art.32.1.a',
        role='high',
    ),

    # §B.8.3.1 processor obligations support → Art.28 + Art.15 + Art.17
    RelationshipEdge(
        source_ref='B.8.3.1', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.3.1 is the certifiable operationalisation of Art.28.3.e — processor assists controller with subject rights.',
        citation='ISO/IEC 27701:2019 Annex D — 8.3.1 → (28)(3)(e)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.3.1', source_standard_id='ISO27701:2019',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.3.1 supports customer Art.15 fulfilment — processor makes processing information available.',
        citation='ISO/IEC 27701:2019 Annex D — 8.3.1 → (15)(3)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.3.1', source_standard_id='ISO27701:2019',
        target_ref='Art.17', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.3.1 supports customer Art.17 fulfilment — processor executes erasure on customer instruction.',
        citation='ISO/IEC 27701:2019 Annex D — 8.3.1 → (17)(2)',
        role='medium',
    ),

    # §B.8.4.x processor PbD → Art.5 + Art.28 + Art.30
    RelationshipEdge(
        source_ref='B.8.4.1', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.4.1 processor temp file disposal supports Art.5.1.c minimisation.',
        citation='ISO/IEC 27701:2019 Annex D — 8.4.1 → (5)(1)(c)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.4.2', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.4.2 is the certifiable operationalisation of Art.28.3.g — processor returns or deletes PII at end of service.',
        citation='ISO/IEC 27701:2019 Annex D — 8.4.2 → (28)(3)(g)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.4.2', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.4.2 end-of-service records support Art.30.1.f retention records.',
        citation='ISO/IEC 27701:2019 Annex D — 8.4.2 → (30)(1)(f)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.4.3', source_standard_id='ISO27701:2019',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.4.3 processor transmission controls operationalise Art.5.1.f integrity + confidentiality.',
        citation='ISO/IEC 27701:2019 Annex D — 8.4.3 → (5)(1)(f)',
        role='high',
    ),
]


# ── ISO 27701:2019 Batch 3 bridges — Transfers + Sharing + Disclosure ───────
# 12 anchors: §A.7.5.1-4 controller + §B.8.5.1-8 processor. Heavy bridge to
# GDPR Chapter V (Art.44-49) + Art.28.2/3.a/3.d/4 subprocessor terms.
# Author: 2026-07-04.

ISO27701_BATCH3_EDGES: list[RelationshipEdge] = [
    # ── SUPPORTS 27701 → 27001 ─────────────────────────────────────────────
    # Cross-jurisdiction transfer basis ↔ A.5.14 information transfer
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.5.1 cross-jurisdiction transfer basis augments 27001 A.5.14 information transfer with the privacy-specific Chap V + Schrems II TIA overlay.',
        citation='ISO/IEC 27701:2019 §7.5.1 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.5.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.5.2 destinations register operationalises 27001 A.5.14 information transfer at the country-map level.',
        citation='ISO/IEC 27701:2019 §7.5.2 + ISO/IEC 27002:2022 §5.14',
        role='medium',
    ),
    # A.7.5.3 + A.7.5.4 records ↔ A.5.9 asset register
    RelationshipEdge(
        source_ref='A.7.5.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.5.3 transfer records are a records-programme artefact — analogous to 27001 A.5.9 asset register discipline for PII transfer events.',
        citation='ISO/IEC 27701:2019 §7.5.3 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.5.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.5.4 disclosure records — same records-programme pattern as A.5.9.',
        citation='ISO/IEC 27701:2019 §7.5.4 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),
    # B.8.5.1 processor transfer basis ↔ A.5.14
    RelationshipEdge(
        source_ref='B.8.5.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.1 processor-side cross-jurisdiction transfers mirror A.7.5.1 — augment 27001 A.5.14.',
        citation='ISO/IEC 27701:2019 §8.5.1 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    # B.8.5.6/7/8 subcontractor chain ↔ A.5.19 + A.5.21 + A.5.22 supplier
    RelationshipEdge(
        source_ref='B.8.5.6', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.6 subcontractor disclosure operates within 27001 A.5.19 supplier relationships (subprocessor is a supplier).',
        citation='ISO/IEC 27701:2019 §8.5.6 + ISO/IEC 27002:2022 §5.19',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.7 subcontractor engagement — same policy family as 27001 A.5.19 supplier policy + specialisation for privacy subprocessors.',
        citation='ISO/IEC 27701:2019 §8.5.7 + ISO/IEC 27002:2022 §5.19',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.21', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.7 subcontractor written-contract flow-down aligns with 27001 A.5.21 managing ICT supply chain security.',
        citation='ISO/IEC 27701:2019 §8.5.7 + ISO/IEC 27002:2022 §5.21',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.5.8', source_standard_id='ISO27701:2019',
        target_ref='A.5.22', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.8 subcontractor-change monitoring aligns with 27001 A.5.22 monitoring, review + change management of supplier services.',
        citation='ISO/IEC 27701:2019 §8.5.8 + ISO/IEC 27002:2022 §5.22',
        role='high',
    ),

    # ── IMPLEMENTS 27701 → GDPR (per Annex D + Chap V) ─────────────────────
    # A.7.5.1 transfer basis → Chapter V (Art.44 + Art.45 + Art.46 + Art.47 + Art.48 + Art.49)
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.44', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.1 operationalises GDPR Art.44 general principle for transfers.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.1 → (44)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.45', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.1 covers Art.45 adequacy-decision transfers.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.1 → (45)(1-9)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.1 covers Art.46 appropriate safeguards (SCCs, BCRs, codes, certification).',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.1 → (46)(1-5)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.47', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.1 covers Art.47 binding corporate rules basis.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.1 → (47)(1-3)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.48', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.1 addresses Art.48 transfers not authorised by Union law (foreign court orders).',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.1 → (48)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.49', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.1 covers Art.49 derogations for specific situations as last-resort transfer basis.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.1 → (49)(1-6)',
        role='high',
    ),
    # A.7.5.2 destinations → Art.15.2 (subject-facing disclosure) + Art.30.1.e
    RelationshipEdge(
        source_ref='A.7.5.2', source_standard_id='ISO27701:2019',
        target_ref='Art.15', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.2 destinations disclosure feeds Art.15.2 — subject-right to know transfer destinations.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.2 → (15)(2)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.5.2', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.2 destinations feed Art.30.1.e recipient records.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.2 → (30)(1)(e)',
        role='medium',
    ),
    # A.7.5.3 transfer records → Art.30.1.e
    RelationshipEdge(
        source_ref='A.7.5.3', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.3 transfer records support Art.30.1.e transfer-recipient recording.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.3 → (30)(1)(e)',
        role='high',
    ),
    # A.7.5.4 disclosure records → Art.30.1.d
    RelationshipEdge(
        source_ref='A.7.5.4', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 A.7.5.4 disclosure records support Art.30.1.d recipient recording.',
        citation='ISO/IEC 27701:2019 Annex D — 7.5.4 → (30)(1)(d)',
        role='high',
    ),
    # B.8.5.1 processor transfer basis → Chap V + Art.28
    RelationshipEdge(
        source_ref='B.8.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.44', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.1 processor-side Chap V compliance + Art.28 processor-instruction flow.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.1 → (44), (46), (48), (49)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.46', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.1 processor transfers under Art.46 safeguards.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.1 → (46)(1-5)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.48', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.1 handles Art.48 processor-side.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.1 → (48)',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.5.1', source_standard_id='ISO27701:2019',
        target_ref='Art.49', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.1 processor Art.49 derogation invocation.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.1 → (49)(1-6)',
        role='medium',
    ),
    # B.8.5.2 destinations → Art.30.2.c
    RelationshipEdge(
        source_ref='B.8.5.2', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.2 processor destinations support Art.30.2.c transfer records.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.2 → (30)(2)(c)',
        role='medium',
    ),
    # B.8.5.3 disclosure records → Art.30.1.d
    RelationshipEdge(
        source_ref='B.8.5.3', source_standard_id='ISO27701:2019',
        target_ref='Art.30', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.3 processor disclosure records — same records-programme discipline as Art.30.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.3 → (30)(1)(d)',
        role='medium',
    ),
    # B.8.5.4 notification → Art.28.3.a documented instructions
    RelationshipEdge(
        source_ref='B.8.5.4', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.4 legally-binding request notification operationalises Art.28.3.a documented-instructions principle — processor doesn''t act on non-controller instructions without proper channel.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.4 → (28)(3)(a)',
        role='high',
    ),
    # B.8.5.5 disclosure decision → Art.48 Union-law authorisation gate
    RelationshipEdge(
        source_ref='B.8.5.5', source_standard_id='ISO27701:2019',
        target_ref='Art.48', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.5 reject-if-not-legally-binding operationalises Art.48 protection against foreign disclosure requests without Union-law basis.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.5 → (48)',
        role='high',
    ),
    # B.8.5.6/7/8 subcontractor chain → Art.28.2 + Art.28.4
    RelationshipEdge(
        source_ref='B.8.5.6', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.6 pre-use subcontractor disclosure operationalises Art.28.2 general/specific authorisation + Art.28.4 subprocessor obligations.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.6 → (28)(2), (28)(4)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.7', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.7 subcontractor engagement operationalises Art.28.2 + Art.28.3.d flow-down of contract terms.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.7 → (28)(2), (28)(3)(d)',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.8', source_standard_id='ISO27701:2019',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='IMPLEMENTS',
        rationale='27701 B.8.5.8 subcontractor-change notification operationalises Art.28.2 second sentence — inform controller of intended changes + opportunity to object.',
        citation='ISO/IEC 27701:2019 Annex D — 8.5.8 → (28)(2)',
        role='high',
    ),
]


# ── ISO 27701:2019 Batch 4 — Parent-program SUPPORTS backfill (Ship 23'.b) ───
# Surfaced by scripts/audit_cross_role_edges.py — 30 ISO 27701 extension
# controls had no SUPPORTS → ISO 27001 parent edge, blocking the role-aware
# chat surface's "extension query → surface parent programs" path.
#
# Mapping strategy:
#   * Controller-side (A.7.2.x, A.7.3.x, A.7.4.x): SUPPORTS A.5.34 as the
#     ISO 27001 privacy anchor. Where a specific supporting ISO control is
#     obvious from ISO/IEC 27002:2022 §5.34 or the 27701 clause text, add
#     it as a secondary edge.
#   * Processor-side (B.8.x): SUPPORTS A.5.19/A.5.20 supplier controls,
#     since processor obligations are supplier-contract-shaped.
# High-confidence mappings only; secondary edges added where the ISO 27002
# or 27701 clause text makes the relationship explicit.
# Author: 2026-07-24. See ship_23_prime_a_audit_2026_07_24 memo.

ISO27701_BATCH4_PARENT_EDGES: list[RelationshipEdge] = [
    # ── A.7.2.x — Controller conditions for collection + processing ─────────
    RelationshipEdge(
        source_ref='A.7.2.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.1 identify and document purpose of PII processing implements 27001 A.5.34 privacy protection through purpose specification — the foundational scoping decision.',
        citation='ISO/IEC 27701:2019 §7.2.1 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.2 identifying lawful basis implements 27001 A.5.34 by grounding processing legitimacy in law.',
        citation='ISO/IEC 27701:2019 §7.2.2 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Lawful-basis identification depends on legal / statutory / regulatory requirements catalogued under 27001 A.5.31.',
        citation='ISO/IEC 27701:2019 §7.2.2 + ISO/IEC 27002:2022 §5.31',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.2.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.3 determining when consent is required is a scoping decision that implements 27001 A.5.34 privacy protection.',
        citation='ISO/IEC 27701:2019 §7.2.3 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.4 obtaining + recording consent operationalises 27001 A.5.34 through evidence of lawful basis.',
        citation='ISO/IEC 27701:2019 §7.2.4 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Consent records are a class of information whose retention + management falls under 27001 A.5.9 inventory / asset lifecycle controls.',
        citation='ISO/IEC 27701:2019 §7.2.4 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.2.5', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.5 privacy impact assessment operationalises 27001 A.5.34 by identifying + treating PII-specific risks.',
        citation='ISO/IEC 27701:2019 §7.2.5 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.5', source_standard_id='ISO27701:2019',
        target_ref='6.1.2', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Privacy impact assessment is a specialised form of 27001 6.1.2 information security risk assessment applied to PII scope.',
        citation='ISO/IEC 27701:2019 §7.2.5 + ISO/IEC 27001:2022 §6.1.2',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.2.7 joint PII controller arrangements are a supplier-relationship instance covered by 27001 A.5.19 information security in supplier relationships.',
        citation='ISO/IEC 27701:2019 §7.2.7 + ISO/IEC 27002:2022 §5.19',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.2.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Joint controllership is a PII-specific arrangement type under 27001 A.5.34 privacy protection.',
        citation='ISO/IEC 27701:2019 §7.2.7 + ISO/IEC 27002:2022 §5.34',
        role='medium',
    ),

    # ── A.7.3.x — Obligations to PII principals (subject rights) ────────────
    RelationshipEdge(
        source_ref='A.7.3.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.1 determining + fulfilling PII principal obligations operationalises 27001 A.5.34 privacy protection.',
        citation='ISO/IEC 27701:2019 §7.3.1 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='PII principal rights are grounded in legal/regulatory requirements catalogued under 27001 A.5.31.',
        citation='ISO/IEC 27701:2019 §7.3.1 + ISO/IEC 27002:2022 §5.31',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.3.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.2 determining information for PII principals scopes the transparency artefacts required by 27001 A.5.34.',
        citation='ISO/IEC 27701:2019 §7.3.2 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.3 providing information to PII principals delivers the transparency artefacts required by 27001 A.5.34.',
        citation='ISO/IEC 27701:2019 §7.3.3 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.4 providing consent modification / withdrawal mechanisms operationalises 27001 A.5.34 respect for principal choice.',
        citation='ISO/IEC 27701:2019 §7.3.4 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.5', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.5 objection-to-processing mechanism operationalises 27001 A.5.34 respect for principal choice.',
        citation='ISO/IEC 27701:2019 §7.3.5 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.7 informing third parties of principal-initiated changes propagates 27001 A.5.34 protection downstream.',
        citation='ISO/IEC 27701:2019 §7.3.7 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.7', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Third-party propagation depends on the supplier-relationship management framework under 27001 A.5.19.',
        citation='ISO/IEC 27701:2019 §7.3.7 + ISO/IEC 27002:2022 §5.19',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.7.3.8', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.8 providing PII copies to principals operationalises 27001 A.5.34 access-to-own-data protection.',
        citation='ISO/IEC 27701:2019 §7.3.8 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.9', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.9 handling PII principal requests is the operational surface of 27001 A.5.34 privacy protection.',
        citation='ISO/IEC 27701:2019 §7.3.9 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.3.10', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.3.10 automated decision-making controls are a PII-specific application of 27001 A.5.34 protection.',
        citation='ISO/IEC 27701:2019 §7.3.10 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),

    # ── A.7.4.x — Privacy by design / minimisation ──────────────────────────
    RelationshipEdge(
        source_ref='A.7.4.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.1 limit collection operationalises 27001 A.5.34 minimisation principle at the collection interface.',
        citation='ISO/IEC 27701:2019 §7.4.1 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.2 limit processing operationalises 27001 A.5.34 minimisation principle at the processing layer.',
        citation='ISO/IEC 27701:2019 §7.4.2 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.3 accuracy and quality of PII operationalises 27001 A.5.34 data-integrity aspect of privacy protection.',
        citation='ISO/IEC 27701:2019 §7.4.3 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.4 PII minimisation objectives directly implement 27001 A.5.34 minimisation principle at the policy layer.',
        citation='ISO/IEC 27701:2019 §7.4.4 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.6', source_standard_id='ISO27701:2019',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 A.7.4.6 temporary files handling operationalises 27001 A.8.10 information deletion for transient PII copies.',
        citation='ISO/IEC 27701:2019 §7.4.6 + ISO/IEC 27002:2022 §8.10',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.7.4.6', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Temporary-file discipline is a privacy-protection concern under 27001 A.5.34 — transient PII must be cleaned up.',
        citation='ISO/IEC 27701:2019 §7.4.6 + ISO/IEC 27002:2022 §5.34',
        role='medium',
    ),

    # ── B.8.2.x — Processor conditions for collection + processing ──────────
    RelationshipEdge(
        source_ref='B.8.2.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.2.2 processing only for organisation-authorised purposes is a supplier-agreement term covered by 27001 A.5.20.',
        citation='ISO/IEC 27701:2019 §8.2.2 + ISO/IEC 27002:2022 §5.20',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.2.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.2.3 marketing/advertising use restriction is a supplier-agreement term under 27001 A.5.20.',
        citation='ISO/IEC 27701:2019 §8.2.3 + ISO/IEC 27002:2022 §5.20',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.2.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.20', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.2.4 handling of infringing controller instructions is a supplier-agreement clause under 27001 A.5.20.',
        citation='ISO/IEC 27701:2019 §8.2.4 + ISO/IEC 27002:2022 §5.20',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.2.5', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.2.5 customer obligations to the processor is a supplier-relationship term under 27001 A.5.19.',
        citation='ISO/IEC 27701:2019 §8.2.5 + ISO/IEC 27002:2022 §5.19',
        role='high',
    ),

    # ── B.8.3.x — Processor obligations to PII principals ───────────────────
    RelationshipEdge(
        source_ref='B.8.3.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.34', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.3.1 processor obligations to PII principals operationalises 27001 A.5.34 downstream when the processor receives principal requests.',
        citation='ISO/IEC 27701:2019 §8.3.1 + ISO/IEC 27002:2022 §5.34',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.3.1', source_standard_id='ISO27701:2019',
        target_ref='A.5.19', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Processor-side handling of principal requests is bounded by the supplier-relationship framework at 27001 A.5.19.',
        citation='ISO/IEC 27701:2019 §8.3.1 + ISO/IEC 27002:2022 §5.19',
        role='medium',
    ),

    # ── B.8.4.x — Processor privacy by design ───────────────────────────────
    RelationshipEdge(
        source_ref='B.8.4.1', source_standard_id='ISO27701:2019',
        target_ref='A.8.10', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.4.1 processor temporary files handling operationalises 27001 A.8.10 information deletion for transient PII copies.',
        citation='ISO/IEC 27701:2019 §8.4.1 + ISO/IEC 27002:2022 §8.10',
        role='high',
    ),

    # ── B.8.5.x — Processor transfers + disclosure ──────────────────────────
    RelationshipEdge(
        source_ref='B.8.5.2', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.2 disclosure of countries + international organisations receiving PII operationalises 27001 A.5.14 information transfer controls for processor-side transparency.',
        citation='ISO/IEC 27701:2019 §8.5.2 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.3 records of PII disclosure to third parties are the audit trail for 27001 A.5.14 information transfers.',
        citation='ISO/IEC 27701:2019 §8.5.3 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.3', source_standard_id='ISO27701:2019',
        target_ref='A.5.9', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Disclosure records are a class of information asset under 27001 A.5.9 inventory / lifecycle controls.',
        citation='ISO/IEC 27701:2019 §8.5.3 + ISO/IEC 27002:2022 §5.9',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='B.8.5.4', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.4 notification of PII disclosure requests operationalises the transparency wrapper on 27001 A.5.14 information transfers.',
        citation='ISO/IEC 27701:2019 §8.5.4 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.5', source_standard_id='ISO27701:2019',
        target_ref='A.5.14', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='27701 B.8.5.5 legally binding PII disclosure handling is the special-case pathway for 27001 A.5.14 transfers under legal compulsion.',
        citation='ISO/IEC 27701:2019 §8.5.5 + ISO/IEC 27002:2022 §5.14',
        role='high',
    ),
    RelationshipEdge(
        source_ref='B.8.5.5', source_standard_id='ISO27701:2019',
        target_ref='A.5.31', target_standard_id='ISO27001:2022',
        edge_type='SUPPORTS',
        rationale='Legally binding disclosure requests fall under 27001 A.5.31 legal / statutory / regulatory requirements framework.',
        citation='ISO/IEC 27701:2019 §8.5.5 + ISO/IEC 27002:2022 §5.31',
        role='medium',
    ),
]


# ── Ship 23'.b Gap 3 — A.8 Technological → GDPR bridges ─────────────────────
# Surfaced by audit_cross_role_edges.py — 15 of 34 A.8.x controls (44%)
# had no GDPR relationship despite being technical-security controls that
# naturally demonstrate Art.32 (Security of processing) or Art.25 (Privacy
# by design). Every A.8 tech control DEMONSTRATES at least Art.32; a few
# also demonstrate Art.25 (SDLC-adjacent) or Art.28 (outsourced work).
# High-confidence mappings only.

A8_TECH_GDPR_BRIDGE_EDGES: list[RelationshipEdge] = [
    RelationshipEdge(
        source_ref='A.8.1', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.1 user endpoint device security is a technical measure for GDPR Art.32 security of processing, particularly for PII accessed from endpoints.',
        citation='ISO/IEC 27002:2022 §8.1 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.4', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.4 source-code access controls prevent unauthorised alteration of PII-processing systems, an Art.32 confidentiality + integrity measure.',
        citation='ISO/IEC 27002:2022 §8.4 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.6', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.6 capacity management demonstrates the availability leg of GDPR Art.32.1.b resilience of processing systems.',
        citation='ISO/IEC 27002:2022 §8.6 + GDPR Art.32.1.b',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.17', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.17 clock synchronization preserves log-timeline integrity required to demonstrate Art.32 security controls to auditors + Art.33 breach-notification timing.',
        citation='ISO/IEC 27002:2022 §8.17 + GDPR Art.32.1.d',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.18', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.18 privileged utility program controls limit high-power access to PII systems, a direct Art.32.1.b integrity + confidentiality measure.',
        citation='ISO/IEC 27002:2022 §8.18 + GDPR Art.32.1.b',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.19', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.19 software installation controls prevent unauthorised code introduction into PII-processing systems, an Art.32 integrity measure.',
        citation='ISO/IEC 27002:2022 §8.19 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.21', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.21 security of network services demonstrates the network-layer confidentiality + availability of GDPR Art.32.1 security of processing.',
        citation='ISO/IEC 27002:2022 §8.21 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.22', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.22 network segregation limits lateral movement between PII processing zones, an Art.32.1 confidentiality + integrity measure.',
        citation='ISO/IEC 27002:2022 §8.22 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.23', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.23 web filtering restricts outbound exfiltration of PII + inbound compromise routes, an Art.32.1 confidentiality measure.',
        citation='ISO/IEC 27002:2022 §8.23 + GDPR Art.32.1',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.28', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.28 secure coding practices embed security into PII-processing applications, an Art.32.1 integrity + confidentiality measure.',
        citation='ISO/IEC 27002:2022 §8.28 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.28', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='Secure coding is a foundational practice for GDPR Art.25 data protection by design — security baked in at build time.',
        citation='ISO/IEC 27002:2022 §8.28 + GDPR Art.25.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.30', source_standard_id='ISO27001:2022',
        target_ref='Art.28', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.30 outsourced-development controls establish the security expectations for external processors of PII-processing systems, aligning with Art.28 processor contract terms.',
        citation='ISO/IEC 27002:2022 §8.30 + GDPR Art.28.3',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.30', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.30 outsourced-development security posture propagates Art.32.1 requirements down to development suppliers.',
        citation='ISO/IEC 27002:2022 §8.30 + GDPR Art.32.1',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.31', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.31 separation of development, test, and production environments isolates PII in production from development-time risks, an Art.32.1 integrity + confidentiality measure.',
        citation='ISO/IEC 27002:2022 §8.31 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.31', source_standard_id='ISO27001:2022',
        target_ref='Art.25', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='Environment separation is a Art.25 privacy-by-design measure preventing test-time PII exposure in production.',
        citation='ISO/IEC 27002:2022 §8.31 + GDPR Art.25.1',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.32', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.32 change management preserves the integrity of PII-processing systems across modifications, an Art.32.1.b measure.',
        citation='ISO/IEC 27002:2022 §8.32 + GDPR Art.32.1.b',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.33', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.33 protection of test information prevents PII leakage through non-production test datasets, an Art.32.1 confidentiality measure.',
        citation='ISO/IEC 27002:2022 §8.33 + GDPR Art.32.1',
        role='high',
    ),
    RelationshipEdge(
        source_ref='A.8.33', source_standard_id='ISO27001:2022',
        target_ref='Art.5', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='Test information controls demonstrate purpose limitation (Art.5.1.b) — PII may not leak into test datasets for purposes outside the collection basis.',
        citation='ISO/IEC 27002:2022 §8.33 + GDPR Art.5.1.b',
        role='medium',
    ),
    RelationshipEdge(
        source_ref='A.8.34', source_standard_id='ISO27001:2022',
        target_ref='Art.32', target_standard_id='GDPR:2016/679',
        edge_type='DEMONSTRATES',
        rationale='A.8.34 protection of information systems during audit testing prevents audit-driven disruption to PII availability, an Art.32.1.b measure.',
        citation='ISO/IEC 27002:2022 §8.34 + GDPR Art.32.1.b',
        role='high',
    ),
]


ALL_EDGES: list[RelationshipEdge] = (
    INTRA_ISO_EDGES
    + INTRA_GDPR_EDGES
    + BLOCKS_WHEN_EDGES
    + XFW_EDGES
    + ISO27701_BATCH1_EDGES
    + ISO27701_BATCH2_EDGES
    + ISO27701_BATCH3_EDGES
    + ISO27701_BATCH4_PARENT_EDGES
    + A8_TECH_GDPR_BRIDGE_EDGES
)
