#!/usr/bin/env python3
"""Ship 79'.a — spot-check the union-added "unknown" MUSTs on DPIA + DQA.

Isolates the 20 MUSTs (15 DPIA + 5 DQA) that union+tuned found but neither
consensus nor critic found and ground truth doesn't enumerate. For each,
show the finding's excerpt so I can judge: legitimate coverage vs
wrong-artefact.
"""
import sys
sys.path.insert(0, "/data/arioncomply/scripts")
from ship77e_compare import _load_findings, RUN_A, RUN_B, RUN_D


def _finding_by_must(findings):
    out = {}
    for f in findings:
        k = (f["control_ref"], f["checklist_item_id"] or "")
        out[k] = f
    return out


def spotcheck(doc_key, doc_name):
    print(f"\n{'='*70}")
    print(f"  {doc_key}: {doc_name}")
    print(f"{'='*70}")
    a = _finding_by_must(_load_findings(RUN_A).get(doc_name, []))
    b = _finding_by_must(_load_findings(RUN_B).get(doc_name, []))
    d = _finding_by_must(_load_findings(RUN_D).get(doc_name, []))

    union_added = set(d.keys()) - set(a.keys()) - set(b.keys())
    print(f"\n{len(union_added)} MUSTs union+tuned added that neither A nor B found:\n")
    for (ref, mid) in sorted(union_added):
        f = d[(ref, mid)]
        excerpt = (f.get("excerpt") or "").strip()[:180]
        print(f"  [{ref}] {mid}")
        print(f"    inference_source: {f.get('inference_source')}")
        print(f"    excerpt: {excerpt}")
        print()


for doc_key, doc_name in [
    ("DPIA", "Data Protection Impact Assessment (DPIA) Procedure.docx"),
    ("DQA",  "Data Quality Accuracy Procedure.docx"),
]:
    spotcheck(doc_key, doc_name)
