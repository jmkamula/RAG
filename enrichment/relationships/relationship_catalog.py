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
MANAGED_EDGE_TYPES = (
    "PAIRS_WITH",
    "PREREQUISITE_OF",
    "ESCALATES_TO",
    "CASCADES_FROM",
    "FEEDS_INTO",
    "AUDITED_BY",
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

INTRA_ISO_EDGES: list[RelationshipEdge] = []

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
