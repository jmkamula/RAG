#!/usr/bin/env python3
"""Ship 81'.a addendum — is fingerprint_keyword pulling its weight?

Question: of the 26 TPs on the sample, how many would we STILL catch
if we dropped fingerprint_keyword? If the answer is 26, fingerprint is
redundant. If it's 15, fingerprint carries the tail.

Answer via signal-set analysis:
  For each TP candidate, count how many DISTINCT high-precision signals
  fire. If ≥1 of (must_semantic_topk / explicit_ref / doc_mappings_target)
  fires, fingerprint is redundant on that candidate.

Also: for each FP candidate, do the same. If fingerprint fires but no
other signal does, that FP is "fingerprint-only" — dropping fingerprint
would remove it cleanly.
"""
from __future__ import annotations
import os
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "/data/arioncomply/scripts")
from ship77e_compare import _extract_musts_from_yaml, GT_DIR, DOCS
import psycopg2


UPLOAD_IDS = {
    "dpia":     "5f59f505-45a2-4e7d-ba76-c4c6f4b2e08a",
    "ropa":     "28d9086c-37a1-4dce-b129-a3afd4e5bb18",
    "consent":  "10287fa5-f757-420b-98a4-ee9e34d02d25",
    "proc_ops": "453c55b3-1863-4461-90cb-f7ad058029f2",
    "dqa":      "fbb179a2-f565-4947-9d95-d9b3d6375691",
}

# From Ship 81'.a analysis — precision-when-fired sorted
HIGH_PRECISION = {"must_semantic_topk", "explicit_ref", "doc_mappings_target"}
LOW_PRECISION  = {"bm25_topk", "evidence_uniqueness"}
BROAD_FIRING   = {"fingerprint_keyword", "semantic_fit_gate", "per_protocol_scope"}


def main():
    conn = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)",
                    ("00000000-0000-0000-0000-000000000001",))
        cur.execute(
            f"""
            SELECT du.filename, il.candidates_sample
            FROM intake_consensus_log il
            JOIN document_uploads du ON du.id = il.upload_id
            WHERE il.upload_id IN ({",".join(f"'{u}'::uuid" for u in UPLOAD_IDS.values())})
              AND il.logged_at >= '2026-08-18 13:37:00+00'::timestamptz
              AND il.logged_at <  '2026-08-18 13:39:30+00'::timestamptz
              AND il.tenant_id = '00000000-0000-0000-0000-000000000001'::uuid
            """
        )
        rows = cur.fetchall()
    conn.close()

    # GT lookup
    gt_by_doc: dict[str, dict[str, str]] = {}
    for dk, (yaml_file, doc_name) in DOCS.items():
        gt = _extract_musts_from_yaml(GT_DIR / yaml_file)
        gt_by_doc[doc_name] = {m: v for (m, v, _c) in gt}

    # Categorise each candidate
    counters = {
        "tp_strict": {"total": 0, "fingerprint_fires": 0, "fingerprint_alone": 0,
                      "other_high_prec_also": 0, "no_high_prec": 0},
        "fp":        {"total": 0, "fingerprint_fires": 0, "fingerprint_alone": 0,
                      "other_high_prec_also": 0, "no_high_prec": 0},
    }

    for doc_name, sample in rows:
        gt_map = gt_by_doc.get(doc_name, {})
        for c in sample or []:
            if c.get("verdict") != "accept":
                continue
            must_id = c.get("must_id")
            gt_verdict = gt_map.get(must_id, "unknown")
            signals = set(c.get("signals") or [])
            is_tp_strict = gt_verdict == "satisfies"
            bucket = "tp_strict" if is_tp_strict else "fp"
            counters[bucket]["total"] += 1
            fp_fires = "fingerprint_keyword" in signals
            if fp_fires:
                counters[bucket]["fingerprint_fires"] += 1
                other_signals = signals - {"fingerprint_keyword", "semantic_fit_gate"}
                # semantic_fit_gate always co-fires with fingerprint — treat as part of the pair
                if not other_signals:
                    counters[bucket]["fingerprint_alone"] += 1
                elif other_signals & HIGH_PRECISION:
                    counters[bucket]["other_high_prec_also"] += 1
                else:
                    counters[bucket]["no_high_prec"] += 1

    print("Fingerprint keyword utility on the accept-zone sample")
    print("=" * 70)
    for cat_name, cat in [("STRICT TPs", counters["tp_strict"]), ("FPs", counters["fp"])]:
        n = cat["total"]
        if not n:
            continue
        print(f"\n{cat_name} — {n} total candidates in accept-zone")
        print(f"  fingerprint_keyword fires on: {cat['fingerprint_fires']} ({cat['fingerprint_fires']/n:.0%})")
        print(f"    of those, fingerprint + semantic_fit_gate ALONE (no other signal): "
              f"{cat['fingerprint_alone']} ({cat['fingerprint_alone']/max(cat['fingerprint_fires'],1):.0%} of fp firings)")
        print(f"    of those, another HIGH-precision signal also fires: "
              f"{cat['other_high_prec_also']} ({cat['other_high_prec_also']/max(cat['fingerprint_fires'],1):.0%})")
        print(f"    of those, only LOW/BROAD signals also fire (no high-prec corroborator): "
              f"{cat['no_high_prec']} ({cat['no_high_prec']/max(cat['fingerprint_fires'],1):.0%})")

    # Interpretation section
    tp = counters["tp_strict"]
    fp = counters["fp"]

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    tp_uniquely_from_fp = tp["fingerprint_alone"] + tp["no_high_prec"]
    fp_uniquely_from_fp = fp["fingerprint_alone"] + fp["no_high_prec"]
    print(f"\nTPs that would be LOST if we dropped fingerprint_keyword: {tp_uniquely_from_fp}")
    print(f"  (assuming semantic_fit_gate is dropped with it, and only ")
    print(f"   high-precision signals must_semantic/explicit_ref/doc_mappings remain)")
    print(f"FPs that would be REMOVED cleanly: {fp_uniquely_from_fp}")

    if tp_uniquely_from_fp == 0:
        print("\n=> Fingerprint contributes ZERO unique TPs to the accept-zone sample.")
        print("   Every TP has a high-precision signal corroborating it.")
        print("   Fingerprint's value on accept-zone: purely raising signal count.")
        print("   Verdict: could be dropped without recall loss.")
    else:
        ratio = tp_uniquely_from_fp / (fp_uniquely_from_fp or 1)
        print(f"\n=> Fingerprint carries {tp_uniquely_from_fp} unique TPs.")
        print(f"   TP:FP ratio of fingerprint-unique candidates: {ratio:.2f}")
        print(f"   If ratio < 0.20 (fingerprint-unique is >5:1 FP:TP), drop it.")
        print(f"   If ratio > 0.50, fingerprint carries tail signal — keep.")


if __name__ == "__main__":
    main()
