"""
ISO 27701 RequirementNode seeder.

Existing 27001 + GDPR RequirementNodes were loaded from enrichment source
JSONs (iso_nodes_phase1.json, gdpr_nodes_phase2.json). No such JSON exists
for 27701 (the standard is copyrighted; we can't check it in).

This script seeds the RequirementNode shell (id, standard_id, ref, title,
obligation_text, node_type, obligation_type, applies_to,
business_description) directly from the ISO/IEC 27701:2019 clause text so
that `enrichment/documents/load_to_neo4j.py` can then MATCH each node when
attaching the FulfilmentSpec + EvidenceRequirement children.

Batch-scoped — run per-batch as new controls are curated. Idempotent
(MERGE by id).
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(str(Path(__file__).parent.parent / ".env"))


@dataclass(frozen=True)
class Seed:
    ref:         str
    title:       str
    obligation:  str   # normative shall/should statement from control column
    business:    str   # business_description — implementation guidance summary
    role:        str   # "controller" | "processor"


# ── Batch 1 seeds — 14 controls (from ISO/IEC 27701:2019 §A.7.2.x + §B.8.2.x)
BATCH1_SEEDS: list[Seed] = [
    Seed(
        ref="A.7.2.1",
        title="Identify and document purpose",
        obligation="The organization shall identify and document the specific purposes for which the PII will be processed.",
        business="PII principals should understand the purposes for which their PII is processed. The organization documents each processing purpose sufficiently clearly and in enough detail to be usable in the required information provided to PII principals (see §7.3.2), in consent processes (see §7.2.3), and in the records of processing (see §7.2.8).",
        role="controller",
    ),
    Seed(
        ref="A.7.2.2",
        title="Identify lawful basis",
        obligation="The organization shall determine, document and comply with the relevant lawful basis for the processing of PII for the identified purposes.",
        business="Some jurisdictions require the organization to demonstrate lawfulness of processing was duly established before processing began. Legal bases include consent, contract performance, legal obligation, vital interests, public interest, or legitimate interests of the controller. The organization documents this basis for each PII processing activity.",
        role="controller",
    ),
    Seed(
        ref="A.7.2.3",
        title="Determine when and how consent is to be obtained",
        obligation="The organization shall determine and document a process by which it can demonstrate if, when and how consent for the processing of PII was obtained from PII principals.",
        business="Consent can be required unless other lawful grounds apply. The organization documents when consent is needed and the requirements for obtaining it. Some jurisdictions have specific requirements (e.g. not bundled with other agreements). Certain data collection contexts (e.g. children, research) can be subject to additional requirements.",
        role="controller",
    ),
    Seed(
        ref="A.7.2.4",
        title="Obtain and record consent",
        obligation="The organization shall obtain and record consent from PII principals according to the documented processes.",
        business="Consent should be recorded such that details can be provided on request (time consent was provided, identification of the PII principal, consent statement). Consent should be freely given, specific to the purpose, unambiguous, and explicit.",
        role="controller",
    ),
    Seed(
        ref="A.7.2.5",
        title="Privacy impact assessment",
        obligation="The organization shall assess the need for, and implement where appropriate, a privacy impact assessment whenever new processing of PII or changes to existing processing of PII is planned.",
        business="PII processing generates risks for PII principals which should be assessed through a privacy impact assessment. Some jurisdictions mandate PIAs in specific cases (e.g. automated decisions with legal effects, large-scale processing of special categories, systematic monitoring of public spaces). ISO/IEC 29134 provides guidance.",
        role="controller",
    ),
    Seed(
        ref="A.7.2.6",
        title="Contracts with PII processors",
        obligation="The organization shall have a written contract with any PII processor that it uses, and shall ensure their contracts with PII processors address the implementation of the appropriate controls in Annex B.",
        business="The contract should require the PII processor to implement the appropriate controls specified in Annex B, taking account of the risk assessment (see §5.4.1.2) and scope of processing (see §6.12). By default all Annex B controls should be assumed relevant; exclusion requires justification (see §5.4.1.3).",
        role="controller",
    ),
    Seed(
        ref="A.7.2.7",
        title="Joint PII controller",
        obligation="The organization shall determine respective roles and responsibilities for the processing of PII (including PII protection and security requirements) with any joint PII controller.",
        business="Roles and responsibilities should be determined transparently and documented in a contract or similar binding document (sometimes called a data sharing agreement) covering purpose, categories of PII, roles, security responsibilities, breach handling, retention, liability, and how obligations to PII principals are met.",
        role="controller",
    ),
    Seed(
        ref="A.7.2.8",
        title="Records related to processing PII",
        obligation="The organization shall determine and securely maintain the necessary records in support of its obligations for the processing of PII.",
        business="Maintain an inventory or list of PII processing activities including type of processing, purposes, categories of PII and PII principals, categories of recipients (including third countries), general description of technical and organizational security measures, and a Privacy Impact Assessment report. The inventory should have a designated owner responsible for accuracy and completeness.",
        role="controller",
    ),
    Seed(
        ref="B.8.2.1",
        title="Customer agreement",
        obligation="The organization shall ensure, where relevant, that the contract to process PII addresses the organization's role in providing assistance with the customer's obligations, taking into account the nature of processing and the information available to the organization.",
        business="The processor contract should cover privacy by design and default, security of processing, notification of PII breaches to supervisory authority and to customers and PII principals, PIA conduct, and assistance with prior consultations to PII protection authorities. Some jurisdictions require subject matter, duration, nature, purpose, PII types, and PII principal categories.",
        role="processor",
    ),
    Seed(
        ref="B.8.2.2",
        title="Organization's purposes",
        obligation="The organization shall ensure that PII processed on behalf of a customer are only processed for the purposes expressed in the documented instructions of the customer.",
        business="The customer contract should include objective and time frame. The processor may need to determine method of processing consistent with customer instructions (e.g. capacity allocation) but without additional purposes. The organization should allow the customer to verify compliance with the purpose specification and limitation principles.",
        role="processor",
    ),
    Seed(
        ref="B.8.2.3",
        title="Marketing and advertising use",
        obligation="The organization shall not use PII processed under a contract for the purposes of marketing and advertising without establishing that prior consent was obtained from the appropriate PII principal, and shall not make providing such consent a condition for receiving the service.",
        business="Compliance with customer contractual marketing/advertising requirements should be documented. Organizations should not insist on marketing/advertising inclusion where express consent has not been fairly obtained.",
        role="processor",
    ),
    Seed(
        ref="B.8.2.4",
        title="Infringing instruction",
        obligation="The organization shall inform the customer if, in its opinion, a processing instruction infringes applicable legislation and/or regulation.",
        business="The processor's ability to verify infringement depends on the technological context, the instruction, and the contract between the organization and the customer.",
        role="processor",
    ),
    Seed(
        ref="B.8.2.5",
        title="Customer obligations",
        obligation="The organization shall provide the customer with the appropriate information such that the customer can demonstrate compliance with their obligations.",
        business="Information can include whether the organization allows for and contributes to audits conducted by the customer or another auditor mandated or otherwise agreed by the customer.",
        role="processor",
    ),
    Seed(
        ref="B.8.2.6",
        title="Records related to processing PII",
        obligation="The organization shall determine and maintain the necessary records in support of demonstrating compliance with its obligations (as specified in the applicable contract) for the processing of PII carried out on behalf of a customer.",
        business="Records can include categories of processing carried out on behalf of each customer, transfers to third countries or international organizations, and a general description of the technical and organizational security measures.",
        role="processor",
    ),
    # ── Batch 2 seeds (23 controls) — §A.7.3.x + §A.7.4.x + §B.8.3.1 + §B.8.4.x
    Seed(ref="A.7.3.1", title="Determining and fulfilling obligations to PII principals",
         obligation="The organization shall determine and document their legal, regulatory and business obligations to PII principals related to the processing of their PII and provide the means to meet these obligations.",
         business="Obligations vary by jurisdiction. Provide the appropriate means to meet obligations in an accessible and timely manner with clear documentation of the extent to which obligations are fulfilled and an up-to-date contact point provided via the same medium used to collect PII and consent.",
         role="controller"),
    Seed(ref="A.7.3.2", title="Determining information for PII principals",
         obligation="The organization shall determine and document the information to be provided to PII principals regarding the processing of their PII and the timing of such a provision.",
         business="Determine legal, regulatory and business requirements for when and what information is provided. Typical content includes purpose, controller identity, lawful basis, sources, statutory/contractual nature of provision, subject rights, withdrawal mechanism, transfers, recipients, retention, automated decision making, right to complain, and frequency of provision.",
         role="controller"),
    Seed(ref="A.7.3.3", title="Providing information to PII principals",
         obligation="The organization shall provide PII principals with clear and easily accessible information identifying the PII controller and describing the processing of their PII.",
         business="Provide the information determined in 7.3.2 in a timely, concise, complete, transparent, intelligible and easily accessible form using clear plain language. Present at time of collection where appropriate; also make permanently accessible. Icons and images can help.",
         role="controller"),
    Seed(ref="A.7.3.4", title="Providing mechanism to modify or withdraw consent",
         obligation="The organization shall provide a mechanism for PII principals to modify or withdraw their consent.",
         business="Inform principals of withdrawal rights. Withdrawal mechanism should be consistent with the collection medium (email/website etc.). Record any modification or withdrawal similarly to consent itself. Disseminate changes to systems and third parties. Define response time. Prior processing remains valid; results not used for new processing.",
         role="controller"),
    Seed(ref="A.7.3.5", title="Providing mechanism to object to PII processing",
         obligation="The organization shall provide a mechanism for PII principals to object to the processing of their PII.",
         business="Document legal and regulatory objection requirements (e.g. direct marketing objection). Provide information about objection rights. Mechanisms should be consistent with the type of service (online services provide online objection).",
         role="controller"),
    Seed(ref="A.7.3.6", title="Access, correction and/or erasure",
         obligation="The organization shall implement policies, procedures and/or mechanisms to meet their obligations to PII principals to access, correct and/or erase their PII.",
         business="Enable access, correction and erasure without undue delay. Define response times. Disseminate corrections/erasures through systems and to third parties (see 7.3.7). Include dispute-handling procedures. Records generated by 7.5.3 can help. Track jurisdiction-specific restrictions.",
         role="controller"),
    Seed(ref="A.7.3.7", title="PII controllers' obligations to inform third parties",
         obligation="The organization shall inform third parties with whom PII has been shared of any modification, withdrawal or objections pertaining to the shared PII, and implement appropriate policies, procedures and/or mechanisms to do so.",
         business="Bearing in mind available technology, take appropriate steps to inform third parties of subject-initiated modifications, withdrawals or objections. Maintain active communication channels with third parties. Monitor acknowledgement of receipt.",
         role="controller"),
    Seed(ref="A.7.3.8", title="Providing copy of PII processed",
         obligation="The organization shall be able to provide a copy of the PII that is processed when requested by the PII principal.",
         business="Provide in structured, commonly used, accessible format. Some jurisdictions require machine-readable format for portability. Copies must relate specifically to the requesting subject. Where PII already deleted per retention policy, inform the subject. Do not re-identify solely to fulfil this control. Where feasible, transfer directly to another organization at subject request.",
         role="controller"),
    Seed(ref="A.7.3.9", title="Handling requests",
         obligation="The organization shall define and document policies and procedures for handling and responding to legitimate requests from PII principals.",
         business="Legitimate requests include requests for a copy of PII or complaints. Some jurisdictions permit fees for excessive/repetitive requests. Handle within defined response times. Some jurisdictions define response times and delay-notification requirements. Response times should be documented in the privacy policy.",
         role="controller"),
    Seed(ref="A.7.3.10", title="Automated decision making",
         obligation="The organization shall identify and address obligations, including legal obligations, to the PII principals resulting from decisions made by the organization which are related to the PII principal based solely on automated processing of PII.",
         business="Some jurisdictions define specific obligations for solely-automated decisions significantly affecting subjects, such as notifying existence of automated decision making, allowing objection, and/or obtaining human intervention. Some jurisdictions prohibit full automation for certain processing.",
         role="controller"),
    Seed(ref="A.7.4.1", title="Limit collection",
         obligation="The organization shall limit the collection of PII to the minimum that is relevant, proportional and necessary for the identified purposes.",
         business="Limit PII collection to what is adequate, relevant and necessary — including indirect collection (web logs, system logs). Privacy by default: where optionality exists, each option should be disabled by default and only enabled by explicit subject choice.",
         role="controller"),
    Seed(ref="A.7.4.2", title="Limit processing",
         obligation="The organization shall limit the processing of PII to that which is adequate, relevant and necessary for the identified purposes.",
         business="Manage processing limits through information security and privacy policies and documented procedures. Limit disclosure, storage period, and who can access PII by default to the minimum necessary for identified purposes.",
         role="controller"),
    Seed(ref="A.7.4.3", title="Accuracy and quality",
         obligation="The organization shall ensure and document that PII is as accurate, complete and up-to-date as is necessary for the purposes for which it is processed, throughout the life-cycle of the PII.",
         business="Implement policies/procedures/mechanisms to minimize inaccuracies and to respond to inaccurate PII. Apply throughout the PII lifecycle. See ISO/IEC 29101:2018, 6.2 for lifecycle information.",
         role="controller"),
    Seed(ref="A.7.4.4", title="PII minimization objectives",
         obligation="The organization shall define and document data minimization objectives and what mechanisms (such as de-identification) are used to meet those objectives.",
         business="Identify how PII quantity and identifiability is limited relative to purposes. Use de-identification or other minimization techniques where full PII isn't required. Document technical configurations. See ISO/IEC 20889 for de-identification techniques and ISO/IEC 19944 for cloud identification qualifiers.",
         role="controller"),
    Seed(ref="A.7.4.5", title="PII de-identification and deletion at the end of processing",
         obligation="The organization shall either delete PII or render it in a form which does not permit identification or re-identification of PII principals, as soon as the original PII is no longer necessary for the identified purpose(s).",
         business="Have mechanisms to erase PII when no further processing is anticipated. Alternatively use de-identification techniques such that resulting data cannot reasonably permit re-identification.",
         role="controller"),
    Seed(ref="A.7.4.6", title="Temporary files",
         obligation="The organization shall ensure that temporary files created as a result of the processing of PII are disposed of following documented procedures within a specified, documented period.",
         business="Periodic checks that unused temporary files are deleted. Temp files include filesystem roll-back journals, database transient files, application temp files. A garbage-collection procedure identifies relevant files and determines time since last use.",
         role="controller"),
    Seed(ref="A.7.4.7", title="Retention",
         obligation="The organization shall not retain PII for longer than is necessary for the purposes for which the PII is processed.",
         business="Develop and maintain retention schedules taking into account legal, regulatory and business requirements. Where requirements conflict, make a documented risk-based business decision.",
         role="controller"),
    Seed(ref="A.7.4.8", title="Disposal",
         obligation="The organization shall have documented policies, procedures and/or mechanisms for the disposal of PII.",
         business="Choice of disposal technique depends on nature and extent of PII, associated metadata, and physical characteristics of the media on which PII is stored.",
         role="controller"),
    Seed(ref="A.7.4.9", title="PII transmission controls",
         obligation="The organization shall subject PII transmitted over a data-transmission network to appropriate controls designed to ensure that the data reaches its intended destination.",
         business="Control transmission by ensuring only authorized individuals have access to transmission systems and by following appropriate processes including retention of audit logs to ensure PII is transmitted without compromise to correct recipients.",
         role="controller"),
    Seed(ref="B.8.3.1", title="Obligations to PII principals",
         obligation="The organization shall provide the customer with the means to comply with its obligations related to PII principals.",
         business="A controller's obligations can be defined by legislation, regulation and/or contract, including matters where the customer uses the organization's services (e.g. correction or deletion of PII in a timely fashion). Where the customer depends on the organization for information or technical measures, these should be specified in a contract.",
         role="processor"),
    Seed(ref="B.8.4.1", title="Temporary files",
         obligation="The organization shall ensure that temporary files created as a result of the processing of PII are disposed of following documented procedures within a specified, documented period.",
         business="Periodic verification that unused temporary files are deleted within the identified time period. Temp files include filesystem journals, roll-back files and application temp files. A garbage-collection procedure identifies relevant files and determines time since last use.",
         role="processor"),
    Seed(ref="B.8.4.2", title="Return, transfer or disposal of PII",
         obligation="The organization shall provide the ability to return, transfer and/or disposal of PII in a secure manner. It should also make its policy available to the customer.",
         business="Provide the assurance necessary to allow the customer to ensure that PII processed under a contract is erased (by the organization and any subcontractors) from wherever stored — including backups and business continuity — as soon as no longer necessary. Retention period after termination should protect customer from accidental lapse. See 7.4.7 retention principle.",
         role="processor"),
    Seed(ref="B.8.4.3", title="PII transmission controls",
         obligation="The organization shall subject PII transmitted over a data-transmission network to appropriate controls designed to ensure that the data reaches its intended destination.",
         business="Ensure only authorized individuals have access to transmission systems and follow appropriate processes including retention of audit data. Transmission requirements can be included in the processor-customer contract. Where contractual requirements are silent, take advice from the customer prior to transmission.",
         role="processor"),
]


CYPHER = """
MERGE (n:RequirementNode {id: $id})
SET   n.standard_id            = $standard_id,
      n.ref                    = $ref,
      n.title                  = $title,
      n.obligation_text        = $obligation_text,
      n.node_type              = 'control',
      n.obligation_type        = 'risk_based',
      n.applies_to             = $applies_to,
      n.business_description   = $business_description
RETURN n.id AS id
"""


def main():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    pwd = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))

    standard_id = "ISO27701:2019"
    seeded = 0
    with driver.session() as s:
        for seed in BATCH1_SEEDS:
            params = {
                "id":                    f"{standard_id}:{seed.ref}",
                "standard_id":           standard_id,
                "ref":                   seed.ref,
                "title":                 seed.title,
                "obligation_text":       seed.obligation,
                "applies_to":            f"['{seed.role}']",
                "business_description":  seed.business,
            }
            r = s.run(CYPHER, params)
            _ = r.single()
            seeded += 1
            print(f"  ✓ MERGE {params['id']} — {seed.title}")

    print()
    print(f"Seeded {seeded} ISO 27701 RequirementNodes.")
    driver.close()


if __name__ == "__main__":
    main()
