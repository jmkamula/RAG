#!/usr/bin/env python3
"""Ship 69'.d — create 12 GDPR sub-clause stub nodes in Neo4j.

Each of the 13 stub_needed edges from Ship 69'.a's audit points at a
narrower sub-clause the curator's rationale named (`Art.6.4.e`,
`Art.13.2.f`, `Art.28.3.e`, ...) but which doesn't exist as a
RequirementNode. Ship 69'.d adds those 12 unique nodes (Art.28.2
appears in 3 edges) with minimal metadata + verbatim obligation
text so:

  (a) Ship 69'.a's audit reclassifies the 13 edges to
      `retargetable_now`, and
  (b) Ship 69'.b's retargeter can point each catalog edge at the
      stub, and
  (c) Ship 59'.e's stub roll-down transparently resolves each
      stub's effective MUSTs from its parent article (path 2
      ref-parse fallback), so bridge_coverage still emits
      attribution rows.

Stubs written directly to Neo4j via MERGE (idempotent). Node shape
mirrors the existing paragraph-level stubs (Art.32.1, Art.28.3
etc.) — the load_neo4j.py string-key schema.

Usage:
    PYTHONPATH=/data/arioncomply python3 scripts/curation/create_gdpr_stubs_69d.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env")
except ImportError:
    pass

from neo4j import GraphDatabase


# Verbatim GDPR text for each sub-clause. Text confirmed against
# Regulation (EU) 2016/679 (canonical publication). Chapter + theme
# inherited from parent article.
STUBS = [
    {
        "ref":              "Art.6.4.e",
        "parent_ref":       "Art.6.4",
        "title":            "Lawfulness of processing — 4(e)",
        "obligation_type":  "risk_based",
        "applies_to":       ["controller"],
        "chapter":          "Principles",
        "theme":            "Principles",
        "obligation_text":  (
            "the existence of appropriate safeguards, which may include "
            "encryption or pseudonymisation."
        ),
    },
    {
        "ref":              "Art.8.3",
        "parent_ref":       "Art.8",
        "title":            "Conditions applicable to child's consent — paragraph 3",
        "obligation_type":  "absolute",
        "applies_to":       ["controller"],
        "chapter":          "Principles",
        "theme":            "Principles",
        "obligation_text":  (
            "Paragraph 1 shall not affect the general contract law of "
            "Member States such as the rules on the validity, formation "
            "or effect of a contract in relation to a child."
        ),
    },
    {
        "ref":              "Art.13.2.f",
        "parent_ref":       "Art.13.2",
        "title":            "Information to be provided where personal data collected from the data subject — 2(f)",
        "obligation_type":  "absolute",
        "applies_to":       ["controller"],
        "chapter":          "Rights of the data subject",
        "theme":            "Rights",
        "obligation_text":  (
            "the existence of automated decision-making, including profiling, "
            "referred to in Article 22(1) and (4) and, at least in those cases, "
            "meaningful information about the logic involved, as well as the "
            "significance and the envisaged consequences of such processing "
            "for the data subject."
        ),
    },
    {
        "ref":              "Art.13.3",
        "parent_ref":       "Art.13",
        "title":            "Information to be provided where personal data collected from the data subject — paragraph 3",
        "obligation_type":  "absolute",
        "applies_to":       ["controller"],
        "chapter":          "Rights of the data subject",
        "theme":            "Rights",
        "obligation_text":  (
            "Where the controller intends to further process the personal data "
            "for a purpose other than that for which the personal data were "
            "collected, the controller shall provide the data subject prior to "
            "that further processing with information on that other purpose "
            "and with any relevant further information as referred to in "
            "paragraph 2."
        ),
    },
    {
        "ref":              "Art.15.2",
        "parent_ref":       "Art.15",
        "title":            "Right of access by the data subject — paragraph 2",
        "obligation_type":  "absolute",
        "applies_to":       ["controller"],
        "chapter":          "Rights of the data subject",
        "theme":            "Rights",
        "obligation_text":  (
            "Where personal data are transferred to a third country or to an "
            "international organisation, the data subject shall have the right "
            "to be informed of the appropriate safeguards pursuant to Article "
            "46 relating to the transfer."
        ),
    },
    {
        "ref":              "Art.28.2",
        "parent_ref":       "Art.28",
        "title":            "Processor — paragraph 2",
        "obligation_type":  "absolute",
        "applies_to":       ["processor"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "The processor shall not engage another processor without prior "
            "specific or general written authorisation of the controller. In "
            "the case of general written authorisation, the processor shall "
            "inform the controller of any intended changes concerning the "
            "addition or replacement of other processors, thereby giving the "
            "controller the opportunity to object to such changes."
        ),
    },
    {
        "ref":              "Art.28.3.d",
        "parent_ref":       "Art.28.3",
        "title":            "Processor — 3(d)",
        "obligation_type":  "absolute",
        "applies_to":       ["processor"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "respects the conditions referred to in paragraphs 2 and 4 for "
            "engaging another processor;"
        ),
    },
    {
        "ref":              "Art.28.3.e",
        "parent_ref":       "Art.28.3",
        "title":            "Processor — 3(e)",
        "obligation_type":  "absolute",
        "applies_to":       ["processor"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "taking into account the nature of the processing, assists the "
            "controller by appropriate technical and organisational measures, "
            "insofar as this is possible, for the fulfilment of the "
            "controller's obligation to respond to requests for exercising "
            "the data subject's rights laid down in Chapter III;"
        ),
    },
    {
        "ref":              "Art.28.4",
        "parent_ref":       "Art.28",
        "title":            "Processor — paragraph 4",
        "obligation_type":  "absolute",
        "applies_to":       ["processor"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "Where a processor engages another processor for carrying out "
            "specific processing activities on behalf of the controller, the "
            "same data protection obligations as set out in the contract or "
            "other legal act between the controller and the processor as "
            "referred to in paragraph 3 shall be imposed on that other "
            "processor by way of a contract or other legal act, in particular "
            "providing sufficient guarantees to implement appropriate "
            "technical and organisational measures in such a manner that the "
            "processing will meet the requirements of this Regulation. Where "
            "that other processor fails to fulfil its data protection "
            "obligations, the initial processor shall remain fully liable to "
            "the controller for the performance of that other processor's "
            "obligations."
        ),
    },
    {
        "ref":              "Art.30.1.d",
        "parent_ref":       "Art.30.1",
        "title":            "Records of processing activities — 1(d)",
        "obligation_type":  "absolute",
        "applies_to":       ["controller"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "the categories of recipients to whom the personal data have been "
            "or will be disclosed including recipients in third countries or "
            "international organisations;"
        ),
    },
    {
        "ref":              "Art.30.1.e",
        "parent_ref":       "Art.30.1",
        "title":            "Records of processing activities — 1(e)",
        "obligation_type":  "absolute",
        "applies_to":       ["controller"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "where applicable, transfers of personal data to a third country "
            "or an international organisation, including the identification "
            "of that third country or international organisation and, in the "
            "case of transfers referred to in the second subparagraph of "
            "Article 49(1), the documentation of suitable safeguards;"
        ),
    },
    {
        "ref":              "Art.30.2.c",
        "parent_ref":       "Art.30.2",
        "title":            "Records of processing activities — 2(c)",
        "obligation_type":  "absolute",
        "applies_to":       ["processor"],
        "chapter":          "Controller and Processor",
        "theme":            "Controller and Processor",
        "obligation_text":  (
            "where applicable, transfers of personal data to a third country "
            "or an international organisation, including the identification "
            "of that third country or international organisation and, in the "
            "case of transfers referred to in the second subparagraph of "
            "Article 49(1), the documentation of suitable safeguards;"
        ),
    },
]


STANDARD_ID = "GDPR:2016/679"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER",     "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD", "arionneo4j2026")
    driver = GraphDatabase.driver(uri, auth=(user, pw))

    created = 0
    skipped = 0
    with driver.session() as s:
        for stub in STUBS:
            node_id = f"{STANDARD_ID}:{stub['ref']}"
            existing = s.run(
                "MATCH (n:RequirementNode {id: $id}) RETURN count(n) AS c",
                id=node_id,
            ).single()["c"]
            if existing:
                print(f"skip  {stub['ref']:14} — node already exists")
                skipped += 1
                continue
            print(f"MERGE {stub['ref']:14} — {stub['title'][:60]}")
            if args.dry_run:
                continue
            # applies_to stored as comma-joined string (load_neo4j.py's
            # STRING_KEYS convention — property is always scalar).
            props = {
                "id":              node_id,
                "standard_id":     STANDARD_ID,
                "ref":             stub["ref"],
                "title":           stub["title"],
                "node_type":       "obligation",
                "obligation_type": stub["obligation_type"],
                "applies_to":      ",".join(stub["applies_to"]),
                "obligation_text": stub["obligation_text"],
                "parent_ref":      stub["parent_ref"],
                "chapter":         stub["chapter"],
                "theme":           stub["theme"],
            }
            s.run("""
                MERGE (n:RequirementNode {id: $id})
                SET n += $props
            """, id=node_id, props=props)
            created += 1

    print(f"\nCreated: {created}  Skipped (already existed): {skipped}  "
          f"{'(dry-run)' if args.dry_run else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
