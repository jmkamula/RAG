#!/usr/bin/env python3
"""Ship 73'.a — GDPR bridge-coverage gap audit.

Enumerates every whole-article GDPR node with no inbound ISO
bridge edge (IMPLEMENTS / SUPPORTS / ENABLES / GOVERNANCE) and
classifies each into one of three buckets:

  A. **regulatory_internal**  — supervisory authorities, EDPB
     operational rules, dispute resolution, preamble/definitions.
     Not tenant-facing; no bridge possible.

  B. **tenant_facing_unbridgeable** — remedies, fines, penalties,
     data-subject-vs-controller judicial remedies. Tenant-facing
     but the article describes a regulatory *outcome* or a
     data-subject *right of action* rather than an
     organizational control that an ISO system could implement.

  C. **tenant_facing_bridgeable** — the target set for Ship 73'.b.
     For each, propose the ISO control(s) + confidence.

Output: `results/gdpr_bridge_gap_audit.csv` + console summary.

Run:
    PYTHONPATH=/data/arioncomply python3 scripts/curation/audit_gdpr_bridge_gap_73a.py
"""
from __future__ import annotations

import csv
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


# Classification: ref → (bucket, proposed_iso_targets, rationale, confidence)
# Empty target list means no bridge proposed. Confidence values follow
# the existing catalog convention (high / medium / low).
#
# The three buckets:
#   A regulatory_internal
#   B tenant_facing_unbridgeable
#   C tenant_facing_bridgeable
#
# For bucket C the proposed targets are drafts for Ship 73'.b to
# refine + author.

CLASSIFICATIONS: dict[str, tuple[str, list[dict]]] = {
    # ── Chapter I — General provisions (definitions/scope) ──────
    "Art.1":  ("regulatory_internal", []),
    "Art.2":  ("regulatory_internal", []),
    "Art.3":  ("regulatory_internal", []),
    "Art.4":  ("regulatory_internal", []),

    # ── Chapter II — Principles (mostly bridged; Art.11 not) ────
    "Art.11": ("tenant_facing_bridgeable", [
        {"iso": "A.8.11", "std": "ISO27001:2022", "edge": "IMPLEMENTS",
         "rationale": "Data masking implements Art.11's provision that "
                     "controllers should not maintain identifying data solely "
                     "for compliance purposes — pseudonymization/masking of "
                     "PII in analytics/test environments removes the "
                     "identification requirement.",
         "confidence": "medium"},
        {"iso": "A.5.34", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Privacy protection of PII policy defines when "
                     "identification is needed vs when de-identified data "
                     "suffices — the org-level position that scopes Art.11.",
         "confidence": "medium"},
    ]),

    # ── Chapter III — Rights (mostly bridged; Art.23 not) ───────
    "Art.23": ("tenant_facing_bridgeable", [
        {"iso": "A.5.31", "std": "ISO27001:2022", "edge": "GOVERNANCE",
         "rationale": "Legal, statutory, regulatory and contractual "
                     "requirements is the ISO control that identifies when "
                     "Member State law restricts data subject rights — the "
                     "org must track those restrictions per jurisdiction.",
         "confidence": "high"},
    ]),

    # ── Chapter IV — Controller and processor ──────────────────
    "Art.27": ("tenant_facing_bridgeable", [
        {"iso": "A.5.19", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Information security in supplier relationships covers "
                     "the org's engagement of an Art.27 representative — the "
                     "representative is a contracted third party with defined "
                     "scope + accountability requirements.",
         "confidence": "medium"},
        {"iso": "A.5.31", "std": "ISO27001:2022", "edge": "GOVERNANCE",
         "rationale": "Legal requirements register captures the org's "
                     "obligation to designate a representative when not "
                     "established in the EU — jurisdictional applicability "
                     "determined by the register.",
         "confidence": "high"},
    ]),

    "Art.31": ("tenant_facing_bridgeable", [
        {"iso": "A.5.24", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Information security incident management planning "
                     "explicitly covers cooperation with authorities — SA "
                     "notification workflow + evidence provision channels "
                     "are part of the org's IR framework.",
         "confidence": "high"},
        {"iso": "A.5.26", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Response to information security incidents operationalizes "
                     "Art.31 during breach response — the incident handler "
                     "produces cooperation-ready evidence for the SA.",
         "confidence": "medium"},
    ]),

    "Art.39": ("tenant_facing_bridgeable", [
        {"iso": "A.5.2", "std": "ISO27001:2022", "edge": "IMPLEMENTS",
         "rationale": "Information security roles and responsibilities defines "
                     "the DPO's operational tasks — advising the controller "
                     "on Art.39.1 obligations, monitoring compliance, "
                     "cooperating with the SA. The DPO's role definition "
                     "lives here.",
         "confidence": "high"},
        {"iso": "A.5.4", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Management responsibilities ensures top management "
                     "supports DPO independence + resource allocation for "
                     "the Art.39 tasks.",
         "confidence": "medium"},
    ]),

    # Art.40-43 — Codes of conduct + certification
    "Art.40": ("tenant_facing_bridgeable", [
        {"iso": "A.5.31", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Legal / regulatory requirements — an approved code of "
                     "conduct is a documented commitment the org adheres to; "
                     "the register tracks the org's participation.",
         "confidence": "medium"},
    ]),
    "Art.41": ("tenant_facing_bridgeable", [
        {"iso": "A.5.35", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Independent review of information security — code-"
                     "of-conduct monitoring body oversight is an independent "
                     "review mechanism analogous to A.5.35's audit function.",
         "confidence": "low"},
    ]),
    "Art.42": ("tenant_facing_bridgeable", [
        {"iso": "A.5.36", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Compliance with policies, rules and standards — GDPR "
                     "certification is an external attestation of the org's "
                     "compliance posture, tracked alongside internal ISMS "
                     "conformity.",
         "confidence": "medium"},
        {"iso": "A.5.1", "std": "ISO27001:2022", "edge": "GOVERNANCE",
         "rationale": "Information security policies — certification claims "
                     "must be reflected in the org's policy framework.",
         "confidence": "low"},
    ]),
    "Art.43": ("tenant_facing_bridgeable", [
        {"iso": "A.5.19", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Supplier relationships — the certification body is a "
                     "third party engaged with defined scope + independence "
                     "requirements per Art.43. Bridge via supplier "
                     "assessment.",
         "confidence": "low"},
    ]),

    # ── Chapter VI — Independent supervisory authorities ────────
    # ALL supervisory authority articles are regulatory-internal.
    "Art.50": ("regulatory_internal", []),  # International cooperation
    "Art.51": ("regulatory_internal", []),
    "Art.52": ("regulatory_internal", []),
    "Art.53": ("regulatory_internal", []),
    "Art.54": ("regulatory_internal", []),
    "Art.55": ("regulatory_internal", []),
    "Art.56": ("regulatory_internal", []),
    "Art.57": ("regulatory_internal", []),
    "Art.58": ("regulatory_internal", []),
    "Art.59": ("regulatory_internal", []),

    # ── Chapter VII — Cooperation and consistency ──────────────
    # All internal to supervisory authorities + EDPB.
    "Art.60": ("regulatory_internal", []),
    "Art.61": ("regulatory_internal", []),
    "Art.62": ("regulatory_internal", []),
    "Art.63": ("regulatory_internal", []),
    "Art.64": ("regulatory_internal", []),
    "Art.65": ("regulatory_internal", []),
    "Art.66": ("regulatory_internal", []),
    "Art.67": ("regulatory_internal", []),
    "Art.68": ("regulatory_internal", []),
    "Art.69": ("regulatory_internal", []),
    "Art.70": ("regulatory_internal", []),
    "Art.71": ("regulatory_internal", []),
    "Art.72": ("regulatory_internal", []),
    "Art.73": ("regulatory_internal", []),
    "Art.74": ("regulatory_internal", []),
    "Art.75": ("regulatory_internal", []),
    "Art.76": ("regulatory_internal", []),

    # ── Chapter VIII — Remedies, liability and penalties ────────
    "Art.77": ("tenant_facing_unbridgeable", []),  # right to lodge complaint
    "Art.78": ("tenant_facing_unbridgeable", []),  # judicial remedy vs SA
    "Art.79": ("tenant_facing_unbridgeable", []),  # judicial remedy vs controller
    "Art.80": ("tenant_facing_unbridgeable", []),  # representation of subjects
    "Art.81": ("regulatory_internal", []),         # suspension of proceedings
    "Art.82": ("tenant_facing_bridgeable", [
        {"iso": "A.5.28", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Collection of evidence during incident response — "
                     "compensation claims under Art.82 require the "
                     "controller/processor to produce evidence of their "
                     "compliance efforts. Chain-of-custody records defend "
                     "the org.",
         "confidence": "medium"},
        {"iso": "A.5.33", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Protection of records — legal-hold retention of "
                     "processing activity records enables the org to "
                     "demonstrate compliance defence per Art.82.3.",
         "confidence": "medium"},
    ]),
    "Art.84": ("tenant_facing_unbridgeable", []),  # penalties (Member State law)

    # ── Chapter IX — Specific processing situations ────────────
    "Art.86": ("tenant_facing_unbridgeable", []),  # public access — mostly N/A private orgs
    "Art.87": ("tenant_facing_bridgeable", [
        {"iso": "A.8.11", "std": "ISO27001:2022", "edge": "IMPLEMENTS",
         "rationale": "Data masking — national ID numbers are the exact use "
                     "case for pseudonymization/masking Art.87 references.",
         "confidence": "medium"},
    ]),
    "Art.88": ("tenant_facing_bridgeable", [
        {"iso": "A.6.6", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Confidentiality or non-disclosure agreements — "
                     "employment-context processing per Art.88 is governed "
                     "by NDA + employment contract data protection clauses.",
         "confidence": "medium"},
        {"iso": "A.6.5", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Responsibilities after termination — Art.88 requires "
                     "specific safeguards including post-employment access "
                     "revocation.",
         "confidence": "medium"},
    ]),
    "Art.89": ("tenant_facing_bridgeable", [
        {"iso": "A.5.33", "std": "ISO27001:2022", "edge": "IMPLEMENTS",
         "rationale": "Protection of records — archiving purposes per "
                     "Art.89 require documented safeguards + retention "
                     "controls, which is A.5.33's core scope.",
         "confidence": "high"},
        {"iso": "A.8.11", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Data masking — the technical safeguard Art.89.1 "
                     "names explicitly (pseudonymisation) for research + "
                     "statistical purposes.",
         "confidence": "high"},
    ]),
    "Art.90": ("tenant_facing_bridgeable", [
        {"iso": "A.6.6", "std": "ISO27001:2022", "edge": "SUPPORTS",
         "rationale": "Confidentiality / non-disclosure agreements — "
                     "professional secrecy per Art.90 is a formalized "
                     "confidentiality obligation, the org's NDA framework "
                     "covers it.",
         "confidence": "medium"},
    ]),
    "Art.91": ("tenant_facing_unbridgeable", []),  # church-affiliated — narrow, no general ISO
}


def main() -> int:
    uri  = os.getenv("NEO4J_URI",     "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER",    "neo4j")
    pw   = os.getenv("NEO4J_PASSWORD","arionneo4j2026")
    d = GraphDatabase.driver(uri, auth=(user, pw))

    # Pull every whole-article GDPR node + inbound ISO bridge count.
    with d.session() as s:
        rows = s.run(r"""
            MATCH (a:RequirementNode {standard_id:"GDPR:2016/679"})
            WHERE a.ref =~ 'Art\.[0-9]+' AND toInteger(replace(a.ref, 'Art.', '')) <= 91
            OPTIONAL MATCH (src:RequirementNode)-[e:IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE]->(a)
            WHERE src.standard_id STARTS WITH 'ISO'
            WITH a, count(e) AS n_iso_edges
            RETURN a.ref AS ref, coalesce(a.title, '') AS title, n_iso_edges
            ORDER BY toInteger(replace(a.ref, 'Art.', ''))
        """).data()

    # Emit audit CSV
    out_dir = _ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "gdpr_bridge_gap_audit.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "ref", "title", "n_iso_edges", "classification",
            "proposed_iso_ref", "edge_type", "confidence", "rationale",
        ])
        for r in rows:
            ref = r["ref"]
            title = r["title"]
            n = r["n_iso_edges"]
            if n > 0:
                w.writerow([ref, title, n, "already_bridged", "", "", "", ""])
                continue
            classification, proposals = CLASSIFICATIONS.get(
                ref, ("uncertain", [])
            )
            if not proposals:
                w.writerow([ref, title, 0, classification, "", "", "", ""])
                continue
            for p in proposals:
                w.writerow([
                    ref, title, 0, classification,
                    p["iso"], p["edge"], p["confidence"], p["rationale"],
                ])

    # Console summary
    from collections import Counter
    bucket_counts = Counter()
    ref_bucket: dict[str, str] = {}
    for r in rows:
        ref = r["ref"]
        if r["n_iso_edges"] > 0:
            bucket_counts["already_bridged"] += 1
            ref_bucket[ref] = "already_bridged"
        else:
            bucket, _ = CLASSIFICATIONS.get(ref, ("uncertain", []))
            bucket_counts[bucket] += 1
            ref_bucket[ref] = bucket

    total = sum(bucket_counts.values())
    print(f"GDPR whole-article bridge audit — {total} articles\n")
    print("─── Distribution ───")
    for bucket in (
        "already_bridged", "tenant_facing_bridgeable",
        "tenant_facing_unbridgeable", "regulatory_internal", "uncertain",
    ):
        n = bucket_counts.get(bucket, 0)
        pct = 100 * n / total if total else 0
        print(f"  {bucket:32} {n:3}  ({pct:5.1f}%)")

    n_bridgeable = bucket_counts["tenant_facing_bridgeable"]
    n_bridgeable_edges = sum(
        len(proposals) for ref, (bucket, proposals) in CLASSIFICATIONS.items()
        if bucket == "tenant_facing_bridgeable"
    )
    print(f"\nShip 73'.b target: {n_bridgeable} articles / {n_bridgeable_edges} proposed bridge edges.")
    print(f"\nCSV: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
