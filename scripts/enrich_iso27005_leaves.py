"""
Ship 13'.b (2026-07-21) — enrich `business_description` on the 14
risk-adjacent leaves with authority-cited paragraphs sourced from
ISO 27005:2022.

Per Ship 13'.a design memo: prose enrichment only, no new MUSTs
(guidance is non-normative). Each paragraph paraphrases the
27005 guidance in the leaf's specific area and cites a specific
§ pointer verified against the source text at
`/data/arioncomply/private/iso27005_2022.txt`.

Appends AFTER the existing Ship 12'.c citation footer:
    business_description
    ...existing prose...
    [Related guidance: ISO 27003:2017 · ISO 27005:2022]
    Per ISO 27005:2022 §X.Y: ...paraphrased guidance...

Idempotent — checks for a per-leaf `Per ISO 27005:2022` marker
before appending. Safe to re-run.

Usage:
    PYTHONPATH=/data/arioncomply python3 \
        scripts/enrich_iso27005_leaves.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("/data/arioncomply/.env")


_MARKER = "Per ISO 27005:2022"


_ENRICHMENTS: dict[str, str] = {

    "6.1": (
        "Per ISO 27005:2022 §5-§6: the information security risk management "
        "process combines context establishment (organizational scope, "
        "interested-parties requirements, risk criteria) with iterative risk "
        "assessment and risk treatment cycles. Two cycles operate in parallel "
        "— a strategic cycle triggered by major changes to business context "
        "or objectives, and an operational cycle for ongoing scenario review. "
        "The organization should define both cycles' cadence and ensure risk "
        "owners have accountability and authority for the risks they own."
    ),

    "6.1.1": (
        "Per ISO 27005:2022 §5.1: the risk management process is iterative. "
        "Where a risk assessment produces enough information to determine "
        "appropriate treatment, the assessment closes; otherwise another "
        "iteration is performed with revised scope or additional expertise. "
        "Risk treatment itself iterates through selecting options, planning, "
        "implementing, assessing effectiveness, and deciding whether "
        "residual risk is acceptable — two 'risk decision points' that "
        "should be documented and revisited each cycle."
    ),

    "6.1.2": (
        "Per ISO 27005:2022 §7: risk assessment comprises three activities "
        "— identification, analysis, and evaluation. Identification produces "
        "a list of risks that could prevent, affect, or delay achievement "
        "of information security objectives; two approaches are commonly "
        "used (event-based scenarios or asset-threat-vulnerability "
        "enumeration). Analysis determines the level of risk from "
        "consequence and likelihood assessments. Evaluation compares "
        "analysed risks against risk criteria (§6.4) to determine "
        "acceptability and prioritise for treatment. Every identified risk "
        "should have an assigned risk owner with the authority and "
        "accountability to make treatment decisions. Risk acceptance "
        "criteria (§6.4.2) should be approved by the authorised management "
        "level, reflect the organization's risk appetite, and be reviewed "
        "regularly."
    ),

    "6.1.3": (
        "Per ISO 27005:2022 §8: risk treatment selects one or more options "
        "— avoidance, modification, retention, or sharing — and determines "
        "the controls necessary to implement the chosen options. Sources of "
        "controls include ISO/IEC 27001:2022 Annex A, sector-specific codes "
        "of practice, and custom controls where the existing sets do not "
        "fit. Controls should be classified as preventive, detective, or "
        "corrective, with a resilient mix providing defence-in-depth against "
        "control failures. Custom control wording should describe ownership, "
        "monitoring, evidence, frequency, and tolerance. The output feeds "
        "the Statement of Applicability (§8.5) and the risk treatment plan "
        "(§8.6), both of which require risk-owner approval along with "
        "explicit acceptance of residual risks (§8.6.3)."
    ),

    "6.3": (
        "Per ISO 27005:2022 §5.2: risk management operates through a "
        "strategic cycle (major changes to business context, risk sources, "
        "or objectives) and an operational cycle (shorter cadence, driven "
        "by detailed risk-scenario updates). When significant changes "
        "occur to the ISMS scope, the threat landscape, or the business "
        "environment, the organization should determine whether an "
        "additional out-of-cycle risk assessment is required (§9.1). Change "
        "planning should specify what qualifies as 'significant' and which "
        "cycle a given change triggers."
    ),

    "8.1": (
        "Per ISO 27005:2022 §9: operational risk management performs the "
        "risk assessment and treatment processes at planned intervals and "
        "when significant changes occur. Risk assessments should be "
        "scheduled against organizational budget and procurement cycles — "
        "the assessment must produce treatment recommendations in time for "
        "funding requests, then be reassessed after budget allocations. "
        "When the ISMS scope, threat landscape, or business context "
        "changes materially, the organization should determine whether an "
        "additional out-of-cycle assessment is warranted."
    ),

    "8.2": (
        "Per ISO 27005:2022 §7 + §9.1: operational execution of the risk "
        "assessment applies the process defined in ISO 27001 clause 6.1.2 "
        "— identify, analyse, evaluate — using the criteria established at "
        "ISMS setup. Assessment cadence should reflect the ISMS lifecycle: "
        "planned intervals plus event-triggered ad-hoc rounds when "
        "significant change occurs (§9.1). Results feed the risk treatment "
        "execution in ISO 27001 clause 8.3."
    ),

    "8.3": (
        "Per ISO 27005:2022 §8.6 + §9.2: risk treatment execution "
        "formulates plans that specify, for each treated risk: the "
        "selected treatment option and rationale, the accountable owner, "
        "proposed actions, resources required, performance indicators, "
        "constraints, reporting cadence, timeline, and implementation "
        "status. Plans should be approved by risk owners; residual risks "
        "should be explicitly accepted by risk owners against defined "
        "acceptance criteria (§6.4.2). Where residual risk exceeds "
        "acceptance criteria, the risk owner should justify the override "
        "in writing, with escalation to a higher management level."
    ),

    "A.5.5": (
        "Per ISO 27005:2022 §7.2: risk identification benefits from "
        "external threat sensing beyond the organization's own visibility. "
        "Contact with law-enforcement, sector-specific regulators, and "
        "interested parties acts as a threat-intelligence source that "
        "feeds both event-based scenario identification and asset-"
        "vulnerability discovery. Regular authority contact closes the "
        "gap between emerging threats and the organization's risk "
        "register — treating late-detected threats as a risk in itself."
    ),

    "A.5.7": (
        "Per ISO 27005:2022 §7.2: threat intelligence directly feeds the "
        "risk-identification activity. In the event-based approach, "
        "threat sources and their capabilities shape strategic scenarios; "
        "in the asset-based approach, threats enumerate against each "
        "asset-vulnerability pair. Threat intelligence should identify "
        "not only known threats but also drive discovery of previously-"
        "unrecognised risk sources. Coverage should include strategic, "
        "operational, and tactical intelligence; the tempo of intake "
        "should match the operational risk-assessment cycle (§5.2)."
    ),

    "A.5.24": (
        "Per ISO 27005:2022 §8.6: information security incident planning "
        "is a corrective/detective treatment plan for identified risks. "
        "The IR framework should specify — for each risk class where "
        "incidents can occur — the accountable owner, detection method, "
        "response procedure, evidence handling, communication chain, and "
        "post-incident review. IR readiness (drills, exercises) should "
        "appear as a monitored performance indicator in the risk "
        "treatment plan (§8.6.1). The residual-risk acceptance decision "
        "(§8.6.3) should include an explicit stance on IR effectiveness."
    ),

    "A.5.29": (
        "Per ISO 27005:2022 §8.2 + §8.6: business-disruption risk should "
        "be treated through a combination of modification (redundant "
        "infrastructure, geographic distribution), sharing (insurance, "
        "third-party recovery arrangements) and, where necessary, "
        "avoidance. The disruption treatment plan should specify "
        "continuity RTOs, degradation levels acceptable during recovery, "
        "activation triggers, and residual-continuity-risk ownership. "
        "Testing frequency and success criteria should be included as "
        "performance indicators (§8.6.1)."
    ),

    "A.5.30": (
        "Per ISO 27005:2022 §8.6: ICT readiness for continuity is a "
        "specific treatment plan for information-processing "
        "infrastructure risk. The BIA driving the plan should identify "
        "recovery point objectives (RPOs) and recovery time objectives "
        "(RTOs) for each critical process, and the plan should specify "
        "the technical measures — replication, backups, failover, "
        "redundant capacity — with their status, ownership, and testing "
        "cadence. Success criteria (§8.6.1 performance indicators) "
        "should include documented RTO-met flags per exercise."
    ),

    "A.7.5": (
        "Per ISO 27005:2022 §7.2: physical and environmental threats — "
        "flood, fire, power failure, physical intrusion, HVAC failure — "
        "should be identified as risks against physical assets "
        "(facilities, data centres, media stores) with location-specific "
        "likelihood. The event-based approach handles jurisdictional "
        "and geographic hazards well; the asset-based approach catches "
        "facility-specific vulnerabilities. Treatment planning (§8.6) "
        "should combine preventive physical controls, detective "
        "monitoring (A.7.4), and corrective response — with continuity "
        "linkages to A.5.29 disruption security and A.5.30 ICT readiness."
    ),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    print(f"Ship 13'.b — enrich {len(_ENRICHMENTS)} leaves with 27005 prose")
    if args.dry_run:
        print("(dry-run: no writes)")
    print()

    stats = {"updated": 0, "already_marked": 0, "missing": 0}
    with driver.session() as s:
        for ref in sorted(_ENRICHMENTS.keys()):
            paragraph = _ENRICHMENTS[ref]
            node_id = f"ISO27001:2022:{ref}"
            row = s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "RETURN coalesce(n.business_description, '') AS bd, n.title AS title",
                id=node_id,
            ).single()
            if row is None:
                stats["missing"] += 1
                print(f"  ! {ref:8}  NODE NOT FOUND")
                continue

            current_bd: str = row["bd"] or ""
            title: str = row["title"] or ""

            if _MARKER in current_bd:
                stats["already_marked"] += 1
                print(f"  · {ref:8}  already enriched")
                continue

            new_bd = (current_bd.rstrip() + "\n\n" + paragraph).strip()

            if args.dry_run:
                stats["updated"] += 1
                print(f"  + {ref:8}  \"{title[:44]}\"  +{len(paragraph)}c")
                continue

            s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "SET n.business_description = $bd",
                id=node_id, bd=new_bd,
            )
            stats["updated"] += 1
            print(f"  + {ref:8}  \"{title[:44]}\"  appended +{len(paragraph)}c")

    print()
    print(f"Updated:        {stats['updated']}")
    print(f"Already marked: {stats['already_marked']}")
    print(f"Missing:        {stats['missing']}")
    return 0 if stats["missing"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
