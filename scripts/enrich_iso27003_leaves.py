"""
Ship 13'.c (2026-07-22) — enrich `business_description` on the 26
ISMS clause leaves with authority-cited paragraphs sourced from
ISO 27003:2017.

Per Ship 13'.a design memo: prose enrichment only, no new MUSTs
(guidance is non-normative). Each paragraph paraphrases the
27003 guidance in the leaf's specific clause and cites the
same §X.Y number verified against the source text at
`/data/arioncomply/private/iso27003_2017.txt`. 27003 mirrors
ISO 27001 clause numbering 1:1, so §X.Y in 27003 aligns to
clause X.Y in 27001.

Appends AFTER any existing Ship 12'.c citation footer + any
Ship 13'.b 27005 enrichment paragraph. Order for leaves that
carry both is: raw obligation → footer → 27005 paragraph →
27003 paragraph. Reading order is honest curation order; the
footer summary lists the guidance families alphabetically.

Idempotent — checks for a per-leaf `Per ISO 27003:2017` marker
before appending. Safe to re-run.

Usage:
    PYTHONPATH=/data/arioncomply python3 \
        scripts/enrich_iso27003_leaves.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("/data/arioncomply/.env")


_MARKER = "Per ISO 27003:2017"


_ENRICHMENTS: dict[str, str] = {

    "4.1": (
        "Per ISO 27003:2017 §4.1: understanding the organization's "
        "context is a continuous ISMS function. External issues include "
        "social, cultural, political, legal, financial, technological, "
        "natural, and competitive aspects; internal issues span culture, "
        "policy, governance, contractual relationships, capabilities, "
        "physical infrastructure, information systems, and prior audit "
        "results. Analysis serves three purposes — scoping the ISMS, "
        "determining risks and opportunities, and ensuring the ISMS "
        "adapts to change. Reviews should be regular; outputs feed "
        "§4.3 (scope), §6.1 (risk actions), and §9.3 (management review)."
    ),

    "4.2": (
        "Per ISO 27003:2017 §4.2: interested parties can be external "
        "(regulators, shareholders, suppliers, industry associations, "
        "customers, competitors, activist groups) or internal (top "
        "management, process/system/information owners, HR, IT, "
        "employees, security professionals). The organization should "
        "identify each party's information-security-relevant needs and "
        "expectations, and review these regularly as they evolve. "
        "Results feed §4.3 (scope determination) and §6.1 (risk actions)."
    ),

    "4.3": (
        "Per ISO 27003:2017 §4.3: scope determination is a multi-step "
        "process — preliminary scope (small management group), refined "
        "scope (review functional units for boundary simplification), "
        "final scope (adjusted + precisely described), and formal top-"
        "management approval. Documented scope should include "
        "organizational, ICT, and physical boundaries with interfaces. "
        "Scoping decisions should account for external/internal issues "
        "(§4.1), interested-parties requirements (§4.2), business-"
        "activity readiness, support functions, and outsourced "
        "dependencies. Later scope modifications are costly."
    ),

    "4.4": (
        "Per ISO 27003:2017 §4.4: this clause is the central "
        "establish/implement/maintain/improve mandate. Where §4.1-§4.3 "
        "define context and boundaries, §4.4 requires the organization "
        "to ensure that all elements of the ISMS across §5-§10 are "
        "actually in place and coherent — an umbrella requirement over "
        "the entire management system."
    ),

    "5.1": (
        "Per ISO 27003:2017 §5.1: top management demonstrates "
        "leadership by (a) ensuring policy and objectives align with "
        "strategic direction, (b) integrating ISMS requirements into "
        "organizational processes, (c) providing adequate resources — "
        "financial, personnel, facilities, technical, (d) communicating "
        "the need for information-security management, (e) supporting "
        "security processes and reviewing effectiveness reports, (f) "
        "directing and supporting personnel in ISMS roles, (g) assessing "
        "resource needs during management review, and (h) enabling those "
        "assigned ISMS responsibilities. Where the organization is part "
        "of a larger entity, engagement with the parent's leadership "
        "improves commitment."
    ),

    "5.2": (
        "Per ISO 27003:2017 §5.2: the information security policy "
        "contains brief, high-level statements of intent and direction, "
        "either including objectives or providing a framework for setting "
        "them. It should reflect business context, align to organizational "
        "culture, contain explicit commitment to satisfy security "
        "requirements and support continual improvement, and be "
        "communicated to all persons within ISMS scope in an easily-"
        "understandable form. Top management decides which external "
        "interested parties see the policy; externally-shared policies "
        "should exclude confidential content."
    ),

    "5.3": (
        "Per ISO 27003:2017 §5.3: top management ensures ISMS "
        "responsibilities and authorities are assigned and "
        "communicated. Activities requiring assignment: ISMS "
        "coordination, risk assessment/treatment advice, security "
        "process/system design, control standard-setting, incident "
        "management, and ISMS audit. Beyond dedicated security roles, "
        "information-security responsibilities should be embedded in "
        "information owners, process/asset/risk owners, security "
        "coordinators, project managers, line managers, and end users. "
        "Top management approves major role definitions; day-to-day "
        "delegation is permitted."
    ),

    "6.1": (
        "Per ISO 27003:2017 §6.1: risk-and-opportunity planning "
        "subdivides into two categories — ISMS-outcome risks (e.g., "
        "unclear processes, poor management engagement) handled under "
        "§6.1.1, and information-security risks (loss of C/I/A) handled "
        "under §6.1.2-§6.1.3. The organization may address them "
        "separately or together, but must define and apply complete "
        "processes for both. The words 'determine' and 'address' in "
        "ISO 27001 6.1.1 are equivalent to 'assess' (6.1.2) and "
        "'treat' (6.1.3)."
    ),

    "6.1.1": (
        "Per ISO 27003:2017 §6.1.1: for ISMS-outcome risks (planning, "
        "implementation, operation), the organization determines risks "
        "based on §4.1 issues and §4.2 requirements, then plans to "
        "(a) ensure intended outcomes are delivered, (b) prevent or "
        "reduce undesired effects, and (c) achieve continual "
        "improvement. Actions are integrated into ISMS processes with "
        "a method for evaluating effectiveness. Approaches can be "
        "strategical, tactical, or operational per site/service/"
        "system. If an existing management system covers this, verify "
        "it meets all §6.1.1 requirements."
    ),

    "6.1.2": (
        "Per ISO 27003:2017 §6.1.2: the organization defines a risk "
        "assessment process that (a) establishes risk acceptance "
        "criteria and criteria for consequence, likelihood, and level "
        "of risk, (b) ensures repeated assessments produce consistent, "
        "valid, comparable results, (c) identifies risks against loss "
        "of C/I/A and their risk owners, (d) analyses consequences and "
        "likelihood to determine risk levels, and (e) evaluates "
        "against criteria to prioritise for treatment. Detailed "
        "methodology is in ISO 27005:2022 §7."
    ),

    "6.1.3": (
        "Per ISO 27003:2017 §6.1.3: risk treatment (a) selects "
        "appropriate options based on assessment results, (b) "
        "determines all necessary controls, (c) compares determined "
        "controls against ISO 27001 Annex A to verify no necessary "
        "control is omitted, (d) produces the Statement of "
        "Applicability documenting each Annex A control's "
        "applicability and justification, (e) formulates the risk "
        "treatment plan, and (f) obtains risk-owner approval and "
        "residual-risk acceptance. Detailed methodology is in ISO "
        "27005:2022 §8."
    ),

    "6.2": (
        "Per ISO 27003:2017 §6.2: information security objectives "
        "operationalize the policy at relevant functions and levels. "
        "Objectives must be (a) consistent with the policy, (b) "
        "measurable where practicable, (c) connected to security "
        "requirements and risk assessment/treatment results, (d) "
        "communicated, (e) updated as appropriate. Plans for "
        "achieving objectives specify what will be done, resources "
        "required, responsible parties, completion timelines, and "
        "evaluation methods. Documented information on objectives is "
        "required."
    ),

    # NOTE: ISO 27001:2022 §6.3 (Planning of changes) is new in the
    # 2022 revision. ISO 27003:2017 has no direct §6.3; the closest
    # guidance is in §8.1, which covers planned and unintended
    # changes during operation.
    "6.3": (
        "Per ISO 27003:2017 §8.1 (the closest guidance — 27003:2017 "
        "predates ISO 27001:2022 §6.3): planned changes should be "
        "planned with tasks, responsibilities, deadlines, and "
        "resources; implementation should be monitored and documented "
        "information retained. For unintended changes, review "
        "consequences, determine whether adverse effects have "
        "occurred or can occur, plan and implement mitigating "
        "actions, and retain documentation. The change should also "
        "be considered against risk-acceptance criteria in the "
        "treatment plan."
    ),

    "7.1": (
        "Per ISO 27003:2017 §7.1: resource categories include persons "
        "(drive and operate activities), time, financial resources, "
        "information (for decisions and performance measurement), and "
        "infrastructure (technology, tools, materials). The "
        "organization should estimate resource needs in quantity and "
        "quality, acquire what's needed, provide the resources, "
        "maintain across all ISMS processes, and review against ISMS "
        "needs — adjusting as required."
    ),

    "7.2": (
        "Per ISO 27003:2017 §7.2: for each ISMS role, the organization "
        "determines expected competence (documented if necessary via "
        "job description) and assigns roles to competent persons — "
        "either by identifying qualified existing staff, developing "
        "competence through training/mentoring/reassignment, or "
        "engaging new persons through hiring or contracting. "
        "Effectiveness of competence-development actions should be "
        "evaluated. Competence covers both employees and other "
        "persons working under organizational control (e.g., "
        "contractors)."
    ),

    "7.3": (
        "Per ISO 27003:2017 §7.3: awareness programmes should target "
        "each audience (internal and external) with specific messages, "
        "include information-security context within awareness/"
        "training on other topics, communicate at planned intervals, "
        "and verify knowledge — both at session-end and randomly "
        "between sessions. Behavioural verification (whether persons "
        "act on communicated messages), with 'good' vs 'bad' examples, "
        "reinforces the message."
    ),

    "7.4": (
        "Per ISO 27003:2017 §7.4: the organization determines what "
        "to communicate (policies, objectives, risks, incidents, ISMS "
        "changes, results), when to communicate, who is authorised "
        "to initiate/receive/respond, and which processes drive or "
        "receive the communications. External communication should "
        "have specific authorised roles (e.g., PR officer for "
        "external, security officer for internal), pre-approved "
        "messages for key scenarios, defined channels with "
        "confidentiality and integrity protections, and verification "
        "that messages are correctly received and understood."
    ),

    "7.5": (
        "Per ISO 27003:2017 §7.5: documented information includes both "
        "the mandatory items required by ISO 27001 clauses and "
        "organization-determined items necessary for ISMS "
        "effectiveness. Documented information should be factual and "
        "'to the point'. The amount typically scales with "
        "organizational size. Creation, updating, and control "
        "(identification, protection, distribution, retrieval, "
        "retention, disposition) should be governed by documented "
        "procedures per §7.5.2-§7.5.3. Documented information should "
        "be available for performance evaluation activities in §9."
    ),

    "8.1": (
        "Per ISO 27003:2017 §8.1: the organization plans, implements, "
        "and controls processes to meet information-security "
        "requirements — including ISMS processes (management review, "
        "internal audit) and processes for the risk treatment plan. "
        "Planned changes should be planned with tasks, deadlines, and "
        "resources; unintended changes should have consequences "
        "reviewed and mitigation applied. For outsourced processes, "
        "the organization determines outsourcing scope, ensures "
        "control through interfaces, addresses information-security "
        "in supplier agreements, monitors service delivery against "
        "risk-acceptance criteria, and manages supplier-service "
        "changes."
    ),

    "8.2": (
        "Per ISO 27003:2017 §8.2: risk assessment during operation "
        "follows the §6.1.2 process, executed on a scheduled cadence "
        "and in response to significant changes or incidents. Results "
        "are retained as documented information. Assessments should "
        "be broad at least annually. Level of detail is refined step-"
        "by-step across iterations, as part of continual improvement "
        "of the ISMS. When significant change or incident occurs, "
        "determine which triggers require an additional out-of-cycle "
        "assessment."
    ),

    "8.3": (
        "Per ISO 27003:2017 §8.3: risk treatment during operation "
        "follows the §6.1.3 process — after each iteration of §8.2 "
        "assessment, or when the treatment plan (or parts of it) "
        "fails. Treatment progress should be driven and monitored by "
        "this operational activity. Results are retained as "
        "documented information demonstrating the §6.1.3 process has "
        "been executed."
    ),

    "9.1": (
        "Per ISO 27003:2017 §9.1: the organization determines (a) "
        "what to monitor and measure, (b) who does the monitoring and "
        "measurement and when, (c) methods producing valid, "
        "comparable, reproducible results, (d) who analyses and "
        "evaluates, (e) evaluation methods. Two aspects of "
        "evaluation: information-security performance (are we doing "
        "as expected?) and ISMS effectiveness (are we doing the "
        "right things?). If methods for monitoring, measurement, "
        "analysis, or evaluation can be determined, they must be "
        "determined."
    ),

    "9.2": (
        "Per ISO 27003:2017 §9.2: the audit programme defines "
        "structure and responsibilities for planning, conducting, "
        "reporting, and follow-up. Should ensure audits are "
        "appropriate in scope, minimize operational impact, maintain "
        "quality, ensure auditor competence, retain audit records, "
        "and cover the ISMS within a specified timeframe. Frequency "
        "and extent are risk-based. Effectiveness of implemented "
        "controls should be examined; key controls should be in "
        "every audit. Auditors should be competent, independent, "
        "and adequately trained. Nonconformities feed §10.1; risks "
        "and opportunities feed §4.1 and §6.1."
    ),

    "9.3": (
        "Per ISO 27003:2017 §9.3: management review provides top "
        "management assurance of ISMS continuing suitability, "
        "adequacy, and effectiveness. Should be at least annually — "
        "new or less-mature ISMSes more frequently. Agenda should "
        "cover: status of prior review actions, changes in external/"
        "internal issues, security performance feedback "
        "(nonconformities, monitoring/measurement, audit results, "
        "objective fulfilment), interested-parties feedback, risk "
        "assessment/treatment status, and improvement opportunities. "
        "Outputs include decisions on policy/objective changes, "
        "risk-criteria changes, resource/budget changes, and SoA "
        "updates. Documented information retention is mandatory."
    ),

    # NOTE: ISO 27001:2013 → :2022 renumbered clauses 10.1 and 10.2.
    # 27003:2017 uses the :2013 numbering (10.1=Nonconformity,
    # 10.2=Continual improvement). We cite 27003 §s but map them to
    # the corresponding :2022 clause on the Neo4j side. This avoids
    # publishing 27003 §10.1 content under 27001:2022 §10.1 (which
    # is now Continual improvement, not Nonconformity).

    "10.1": (
        "Per ISO 27003:2017 §10.2 (renumbered to §10.1 in ISO "
        "27001:2022): the ISMS is evaluated for continual improvement "
        "across suitability (do external/internal issues, interested-"
        "parties requirements, objectives, and risks remain properly "
        "addressed?), adequacy (are ISMS processes and controls "
        "compatible with organizational purposes and activities?), "
        "and effectiveness (are intended outcomes achieved, risks "
        "managed to meet objectives, and resources commensurate with "
        "results?). Improvement opportunities can also emerge from "
        "managing nonconformities. Actions to address improvement "
        "opportunities should be treated as a subset of §6.1.1 risk-"
        "and-opportunity actions."
    ),

    "10.2": (
        "Per ISO 27003:2017 §10.1 (renumbered to §10.2 in ISO "
        "27001:2022): a nonconformity is a non-fulfilment of an ISMS "
        "requirement. Corrections address the nonconformity "
        "immediately; corrective actions eliminate the cause to "
        "prevent recurrence. The handling process should identify "
        "extent and impact, decide on corrections, analyse root "
        "cause, determine corrective action, plan and implement, "
        "verify effectiveness. Sources of nonconformities include "
        "audits, complaints, incidents, monitoring results, unmet "
        "objectives. Documented information on nonconformities and "
        "actions must be retained."
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

    print(f"Ship 13'.c — enrich {len(_ENRICHMENTS)} leaves with 27003 prose")
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
