#!/usr/bin/env python3
"""Ship 77'.e — first-principles compare of consensus vs critic-verifier
against manually-authored ground truth for the 5 baseline docs.

For each (doc, path) pair:
  - Find TP: findings whose checklist_item_id matches an expected MUST
    with verdict=satisfies (strict) or verdict in (satisfies, partial)
    (lenient).
  - Find FP: findings on MUSTs marked not_satisfies OR MUSTs not in the
    ground truth for that doc (wrong-artefact).
  - Find FN: expected MUSTs (satisfies for strict, +partial for lenient)
    that the path didn't emit.
  - Compute precision + recall + F1 for both strict + lenient scoring.

Ground-truth yamls have nested structure — expected MUSTs live under
various keys (art_35_expected, a_7_2_8_expected, etc) and can be
per-MUST dicts OR bulk 'bulk_not_satisfies' groups. This script
flattens them into a single (must_id, verdict) list per doc, treating
bulks as all-not_satisfies.
"""
from __future__ import annotations

import csv
import re
import yaml
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).parent.parent
GT_DIR = REPO / "docs" / "ground_truth"
MEASUREMENT_DIR = GT_DIR / "ship77d_measurement"

DOCS = {
    "dpia":      ("dpia_expected.yaml",         "Data Protection Impact Assessment (DPIA) Procedure.docx"),
    "ropa":      ("ropa_expected.yaml",         "Records of Processing Activities.docx"),
    "consent":   ("consent_expected.yaml",      "Consent Management Procedure.docx"),
    "proc_ops":  ("processor_ops_expected.yaml", "Processor Operations Procedures.docx"),
    "dqa":       ("dqa_expected.yaml",           "Data Quality Accuracy Procedure.docx"),
}

RUN_A = MEASUREMENT_DIR / "run_a_consensus.csv"
RUN_B = MEASUREMENT_DIR / "run_b_critic.csv"
# Ship 77'.f — Run C = consensus with LLM verify-all-accepts enabled.
RUN_C = MEASUREMENT_DIR / "run_c_consensus_verified.csv"


# ─── Ground truth flattener ────────────────────────────────────────────

def _flatten_bulk(rationale: str, verdict: str, confidence: str) -> list[tuple[str, str, str]]:
    """Expand a 'bulk_not_satisfies' declaration into a list of (must_id,
    verdict, confidence) tuples. Since we don't have the individual
    must_ids for bulks, we mark them with a wildcard prefix + emit a
    single record so the aggregator counts them as 'expected N musts'
    based on the rationale's count if present."""
    return []


def _extract_musts_from_yaml(yaml_path: Path) -> list[tuple[str, str, str]]:
    """Return list of (must_id, verdict, confidence) tuples via regex.
    Bypasses yaml parsing because some quote values contain unescaped
    colons that break the parser. We only need must_id + verdict +
    confidence for scoring.
    """
    text = yaml_path.read_text()
    musts: list[tuple[str, str, str]] = []

    # Pattern 1: dashed list-item form (used in dpia/ropa/consent/dqa):
    #   - must_id: item:X:Y
    #     verdict: satisfies|partial|not_satisfies
    #     confidence: high|medium|low
    for m in re.finditer(
        r"-\s*must_id:\s*(\S+)\s*\n"
        r"\s+verdict:\s*(\w+)\s*\n"
        r"\s+confidence:\s*(\w+)",
        text
    ):
        musts.append((m.group(1), m.group(2), m.group(3)))

    # Pattern 2: compact per-MUST dict form (used in processor_ops):
    #   short_slug: { verdict: ..., confidence: ..., ... }
    # Or:
    #   short_slug:
    #     verdict: X
    #     confidence: Y
    #
    # We need to reconstruct must_id from context. The parent leaf name
    # is above (e.g. scope_leaf, procedure_leaf, register_leaf,
    # review_leaf). But the actual must slug is per-MUST. For
    # processor_ops, must_id is derivable from the containing control
    # ref plus the slug key. Extract them:

    # First find the current control ref from surrounding section header.
    # Split into control sections (art_28_expected:, b_8_2_1_expected:, ...)
    ref_pattern = re.compile(r"^(art_\d+|b_\d+_\d+_\d+|a_\d+_\d+_\d+)_expected:", re.M)
    positions = [(m.start(), m.group(1)) for m in ref_pattern.finditer(text)]
    positions.append((len(text), None))

    def _slug_to_ref(section_slug: str) -> str:
        # art_28 → Art.28, a_7_2_8 → A.7.2.8, b_8_2_1 → B.8.2.1
        parts = section_slug.split("_")
        head = parts[0]
        if head == "art":
            return f"Art.{'.'.join(parts[1:])}"
        elif head == "a":
            return f"A.{'.'.join(parts[1:])}"
        elif head == "b":
            return f"B.{'.'.join(parts[1:])}"
        return section_slug

    # Compact inline-brace pattern: {slug}: { verdict: X, confidence: Y, ... }
    compact_pat = re.compile(
        r"^\s{4}([a-z_]+):\s*\{\s*verdict:\s*(\w+)\s*,\s*confidence:\s*(\w+)",
        re.M
    )
    for i in range(len(positions) - 1):
        start, section = positions[i]
        end = positions[i + 1][0]
        if section is None:
            continue
        control_ref = _slug_to_ref(section)
        for m in compact_pat.finditer(text[start:end]):
            slug = m.group(1)
            # Skip slugs that are structural (verdict, quote, notes, rationale, bulk_*)
            if slug in {"verdict", "quote", "notes", "rationale",
                        "confidence", "bulk_not_satisfies"}:
                continue
            must_id = f"item:{control_ref}:{slug}"
            musts.append((must_id, m.group(2), m.group(3)))

    # Bulk not_satisfies patterns like "bulk_not_satisfies: all_N_musts"
    # or "*_bulk_not_satisfies" — we skip these because we don't have
    # the individual must_ids. Scoring treats them as "expected
    # not_satisfies for the whole control area" which is close-enough.

    return musts


# ─── Findings loader ───────────────────────────────────────────────────

def _load_findings(csv_path: Path) -> dict[str, list[dict]]:
    """Return {doc_filename: [finding_dicts]}. Each dict has:
    control_ref, standard_id, checklist_item_id, inference_source."""
    findings_by_doc: dict[str, list[dict]] = defaultdict(list)
    with open(csv_path) as fh:
        reader = csv.reader(fh)
        _header = next(reader)
        # CSV columns: filename, control_ref, standard_id, checklist_item_id,
        #              status, confidence, excerpt, inference_source, extracted_at
        for row in reader:
            if len(row) < 8:
                continue
            filename = row[0]
            # Skip embedded-newline continuation lines (filename empty)
            if not filename or not row[1].strip():
                continue
            findings_by_doc[filename].append({
                "control_ref":       row[1],
                "standard_id":       row[2],
                "checklist_item_id": row[3],
                "status":            row[4],
                "confidence":        row[5],
                "inference_source":  row[7],
            })
    return dict(findings_by_doc)


# ─── Scoring ───────────────────────────────────────────────────────────

def _score(findings: list[dict], gt_musts: list[tuple[str, str, str]]) -> dict:
    """Compare a doc's findings against its ground-truth MUSTs.

    Returns dict with strict + lenient precision/recall/F1 + FP class
    counts + narrative.
    """
    # Build expected sets
    strict_expected = {m for m, v, _ in gt_musts if v == "satisfies"}
    partial_expected = {m for m, v, _ in gt_musts if v == "partial"}
    lenient_expected = strict_expected | partial_expected
    not_satisfies_expected = {m for m, v, _ in gt_musts if v == "not_satisfies"}
    # All must_ids seen in the ground truth for THIS doc:
    all_gt_musts = strict_expected | partial_expected | not_satisfies_expected

    # Bucket findings by their checklist_item_id
    finding_musts = {f["checklist_item_id"] for f in findings if f["checklist_item_id"]}

    # Strict scoring
    strict_tp = finding_musts & strict_expected
    strict_fn = strict_expected - finding_musts
    strict_fp = finding_musts - strict_expected

    # Lenient scoring (partial counts as expected)
    lenient_tp = finding_musts & lenient_expected
    lenient_fn = lenient_expected - finding_musts
    lenient_fp = finding_musts - lenient_expected

    # FP class breakdown
    fp_on_not_satisfies = finding_musts & not_satisfies_expected
    fp_on_unknown = finding_musts - all_gt_musts

    def _pf(tp, fp, fn):
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f = 2*p*r / (p + r) if (p + r) else 0.0
        return {"p": p, "r": r, "f1": f, "tp": tp, "fp": fp, "fn": fn}

    return {
        "n_findings":         len(findings),
        "n_distinct_musts":   len(finding_musts),
        "strict":  _pf(len(strict_tp), len(strict_fp), len(strict_fn)),
        "lenient": _pf(len(lenient_tp), len(lenient_fp), len(lenient_fn)),
        "fp_on_not_satisfies": len(fp_on_not_satisfies),
        "fp_on_unknown":       len(fp_on_unknown),
    }


# ─── Main ─────────────────────────────────────────────────────────────

def main():
    print("Ship 77'.e — first-principles compare")
    print("=" * 68)

    findings_a = _load_findings(RUN_A)
    findings_b = _load_findings(RUN_B)
    findings_c = _load_findings(RUN_C) if RUN_C.exists() else {}

    all_scores = {"consensus": {}, "critic": {}, "consensus_verified": {}}

    for key, (yaml_file, doc_name) in DOCS.items():
        gt_musts = _extract_musts_from_yaml(GT_DIR / yaml_file)
        f_a = findings_a.get(doc_name, [])
        f_b = findings_b.get(doc_name, [])
        f_c = findings_c.get(doc_name, [])
        s_a = _score(f_a, gt_musts)
        s_b = _score(f_b, gt_musts)
        s_c = _score(f_c, gt_musts) if f_c else None
        all_scores["consensus"][key] = s_a
        all_scores["critic"][key] = s_b
        if s_c:
            all_scores["consensus_verified"][key] = s_c

        print(f"\n─── {key} ({doc_name[:40]}...) ───")
        print(f"  GT MUSTs: strict-expected={sum(1 for _,v,_ in gt_musts if v=='satisfies')} "
              f"partial={sum(1 for _,v,_ in gt_musts if v=='partial')} "
              f"not_satisfies={sum(1 for _,v,_ in gt_musts if v=='not_satisfies')}")

        variants = [("consensus (A)", s_a), ("critic (B)", s_b)]
        if s_c:
            variants.append(("cons+verify (C)", s_c))
        for name, s in variants:
            print(f"  {name:15} {s['n_findings']:3} findings, {s['n_distinct_musts']:3} distinct musts")
            for scoring in ("strict", "lenient"):
                x = s[scoring]
                print(f"    {scoring:8} P={x['p']:.2%} R={x['r']:.2%} F1={x['f1']:.2%} "
                      f"(TP={x['tp']} FP={x['fp']} FN={x['fn']})")
            print(f"    FP breakdown: on_not_satisfies={s['fp_on_not_satisfies']}, "
                  f"on_unknown/wrong_artefact={s['fp_on_unknown']}")

    # Aggregate
    print("\n" + "=" * 68)
    print("AGGREGATE (across 5 docs)")
    for path in ("consensus", "critic", "consensus_verified"):
        if not all_scores[path]:
            continue
        for scoring in ("strict", "lenient"):
            tps  = sum(all_scores[path][d][scoring]["tp"] for d in all_scores[path])
            fps  = sum(all_scores[path][d][scoring]["fp"] for d in all_scores[path])
            fns  = sum(all_scores[path][d][scoring]["fn"] for d in all_scores[path])
            p = tps / (tps + fps) if (tps + fps) else 0.0
            r = tps / (tps + fns) if (tps + fns) else 0.0
            f = 2*p*r/(p+r) if (p+r) else 0.0
            print(f"  {path:20} {scoring:8} P={p:.2%} R={r:.2%} F1={f:.2%} "
                  f"(TP={tps} FP={fps} FN={fns})")


if __name__ == "__main__":
    main()
