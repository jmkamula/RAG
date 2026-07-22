"""
Ship 13'.e (2026-07-22) — enrich `business_description` on the 7
monitoring leaves with authority-cited paragraphs sourced from
ISO 27004:2016 (second edition).

Context:
  * Ship 12'.b enrolled 27004:2016 in the standards registry.
  * Ship 12'.c appended `[Related guidance: ISO 27004:2016]`
    citation footers to 9.1 + 6 monitoring Annex A leaves.
  * Ship 13'.a discovered the available PDF was 27004:2009
    first edition (edition mismatch); unenrolled + scrubbed the
    27004 mention from all 7 footers.
  * Today (2026-07-22) the user landed the actual 2016 second
    edition PDF; Ship 13'.e re-enrolls + curates from real text.

Per the Ship 13'.a design memo: prose enrichment only, no new
MUSTs (guidance is non-normative). Each paragraph paraphrases
the 27004:2016 guidance in the leaf's specific area and cites
a specific § pointer verified against the source text at
`/data/arioncomply/private/iso27004_2016.txt`.

This script does two things per leaf:

1. Restore the citation footer that Ship 13'.a scrubbed:
   * 9.1: swap `[Related guidance: ISO 27003:2017]` →
     `[Related guidance: ISO 27003:2017 · ISO 27004:2016]`
   * 6 monitoring leaves (A.5.22 / A.5.36 / A.5.37 / A.7.4 /
     A.8.15 / A.8.16): re-append the
     `[Related guidance: ISO 27004:2016]` footer

2. Append the 27004:2016 enrichment paragraph AFTER the footer
   (and after any prior Ship 13'.c 27003 paragraph on 9.1)

Idempotent — footer-restore is a no-op if the citation already
present; enrichment append is a no-op if `Per ISO 27004:2016`
already present. Safe to re-run.

Usage:
    PYTHONPATH=/data/arioncomply python3 \
        scripts/enrich_iso27004_leaves.py [--dry-run]
"""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv("/data/arioncomply/.env")


_MARKER = "Per ISO 27004:2016"


# ── Footer-restore patterns ───────────────────────────────────

_FOOTER_9_1_OLD = "[Related guidance: ISO 27003:2017]"
_FOOTER_9_1_NEW = "[Related guidance: ISO 27003:2017 · ISO 27004:2016]"

# Standalone 27004 footer for the 6 monitoring Annex A leaves
_FOOTER_27004_ONLY = "\n\n[Related guidance: ISO 27004:2016]"

_MONITORING_LEAVES = [
    "A.5.22", "A.5.36", "A.5.37",
    "A.7.4", "A.8.15", "A.8.16",
]


# ── Per-leaf enrichment paragraphs ────────────────────────────

_ENRICHMENTS: dict[str, str] = {

    "9.1": (
        "Per ISO 27004:2016 §6-§8: the monitoring, measurement, "
        "analysis and evaluation process starts with an "
        "information-need identification (§8.2) — what the "
        "organization wants to learn about ISMS performance or "
        "effectiveness — and works through a six-step lifecycle: "
        "identify information needs, create + maintain measures, "
        "establish procedures, monitor + measure, analyse results, "
        "and evaluate ISMS performance and effectiveness (§8.1). "
        "§7 splits measures into two types: performance measures "
        "(are planned activities being carried out?) and "
        "effectiveness measures (are they achieving the intended "
        "security outcomes?). §6.4 sets timeframes to match "
        "information-need lifecycles; §6.5 defines seven "
        "measurement roles (client, planner, reviewer, information "
        "owner, collector, analyst, communicator) that a single "
        "organization may combine but should not omit."
    ),

    "A.5.22": (
        "Per ISO 27004:2016 §6.2 + §7.2: supplier monitoring should "
        "produce measures aligned to a specific information need "
        "about third-party service delivery — the standard lists "
        "\"third party risk management\" as one of the recommended "
        "monitoring domains. Performance measures (§7.2) track "
        "whether the supplier is doing what was contracted; "
        "effectiveness measures (§7.3) track whether the "
        "monitoring itself is catching issues in time. Measures "
        "should be selected against the risks the supplier "
        "relationship carries, not the ease of data collection."
    ),

    "A.5.36": (
        "Per ISO 27004:2016 §7.2 + §7.3: compliance monitoring "
        "combines performance measures (are policies actually "
        "being followed at planned intervals?) with effectiveness "
        "measures (are compliance reviews catching real "
        "non-conformity and driving corrective action?). §5.2 "
        "explicitly frames compliance monitoring as fulfilling "
        "the ISO 27001 clause 9.1 obligation to evaluate ISMS "
        "effectiveness. Metrics should be defined against the "
        "specific policies and standards under review, not "
        "against generic compliance-percentage indicators."
    ),

    "A.5.37": (
        "Per ISO 27004:2016 §7.3: operating-procedure "
        "effectiveness measures should quantify whether the "
        "documented procedure is achieving its intended security "
        "outcome — not merely whether the procedure exists or is "
        "being followed. §6.3 identifies procedure execution "
        "quality as a candidate measurement subject, with "
        "attributes such as time-to-execute, error rates, and "
        "downstream incident correlation. Effectiveness measures "
        "here feed the ISMS-improvement loop (§8.7-§8.8)."
    ),

    "A.7.4": (
        "Per ISO 27004:2016 §6.2 + §7.2: physical security "
        "monitoring produces measures against explicit "
        "information needs (access-anomaly detection rate, "
        "monitored-perimeter coverage, response-time to alerts). "
        "Where monitoring is automated (badge readers, CCTV "
        "analytics, environmental sensors), §6.4 requires "
        "specifying data-collection cadence + retention lifecycle. "
        "Performance measures show whether monitoring is running "
        "as designed; effectiveness measures show whether it "
        "actually detects the incidents it was deployed to catch."
    ),

    "A.8.15": (
        "Per ISO 27004:2016 §8.6: log-analysis effectiveness "
        "should be measured — not just log-volume or coverage. "
        "§7.3 provides examples: exploitation-of-known-"
        "vulnerabilities correlations, mean-time-to-detect, "
        "false-positive rates. Log data feeds multiple downstream "
        "measures (§6.2 lists 'audit', 'incident management', and "
        "'access control, firewall and other event logging' as "
        "monitoring domains that share log-derived inputs). "
        "Measures should be tied to specific security decisions "
        "the analysis is meant to inform (§8.7)."
    ),

    "A.8.16": (
        "Per ISO 27004:2016 §8.5: monitoring activities should be "
        "operationalised through documented procedures (§8.4) "
        "that specify what is monitored, when, by whom, and how "
        "the resulting data is validated (§8.5 covers data "
        "integrity of the measurement pipeline itself). §6.4 "
        "requires timeframes matched to information-need "
        "lifecycles — real-time detection needs continuous "
        "monitoring; strategic trend analysis can tolerate slower "
        "cadence. Effectiveness measures (§7.3) close the loop "
        "by verifying that monitoring outputs actually drive "
        "action (§8.7)."
    ),
}


def _restore_footer(bd: str, ref: str) -> str:
    """Restore the citation footer that Ship 13'.a scrubbed."""
    if "ISO 27004:2016" in bd:
        return bd  # already restored
    if ref == "9.1":
        return bd.replace(_FOOTER_9_1_OLD, _FOOTER_9_1_NEW, 1)
    if ref in _MONITORING_LEAVES:
        # Append the standalone footer BEFORE any 27003 or 27005
        # paragraph. Since Ship 13'.a scrubbed the whole footer
        # from the 6 monitoring leaves, and no other guidance
        # standard cites them, we can just append at the end of
        # the existing prose.
        return bd.rstrip() + _FOOTER_27004_ONLY
    return bd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    driver = GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
        auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
    )

    print(f"Ship 13'.e — 27004:2016 re-enrollment + enrichment on {len(_ENRICHMENTS)} leaves")
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

            # Step 1: restore the citation footer
            bd_with_footer = _restore_footer(current_bd, ref)
            # Step 2: append the enrichment paragraph
            new_bd = (bd_with_footer.rstrip() + "\n\n" + paragraph).strip()

            if args.dry_run:
                stats["updated"] += 1
                delta = len(new_bd) - len(current_bd)
                print(f"  + {ref:8}  \"{title[:44]}\"  +{delta}c")
                continue

            s.run(
                "MATCH (n:RequirementNode {id: $id}) "
                "SET n.business_description = $bd",
                id=node_id, bd=new_bd,
            )
            stats["updated"] += 1
            delta = len(new_bd) - len(current_bd)
            print(f"  + {ref:8}  \"{title[:44]}\"  restored footer + paragraph (+{delta}c)")

    print()
    print(f"Updated:        {stats['updated']}")
    print(f"Already marked: {stats['already_marked']}")
    print(f"Missing:        {stats['missing']}")
    return 0 if stats["missing"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
