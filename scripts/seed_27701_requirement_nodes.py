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
