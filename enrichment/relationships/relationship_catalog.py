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


ALL_EDGES: list[RelationshipEdge] = (
    INTRA_ISO_EDGES
    + INTRA_GDPR_EDGES
)
