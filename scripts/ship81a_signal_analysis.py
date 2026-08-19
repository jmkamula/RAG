#!/usr/bin/env python3
"""Ship 81'.a — per-signal precision/recall contribution.

Data source: `intake_consensus_log.candidates_sample` (JSONB, up to 20
candidates per doc — sample is stratified across accept + drop verdicts
by design). Union of 5-doc baseline runs (Ship 80'.c Run F consensus
log rows, 2026-08-18 13:37).

For each candidate, join `must_id` against the doc's ground-truth
yaml verdict (satisfies / partial / not_satisfies / unknown). Then
per signal, tally:

  fired_on_accept_tp  — signal voted for accept AND GT says satisfies
                        (strict) or partial (lenient)
  fired_on_accept_fp  — signal voted for accept AND GT says
                        not_satisfies OR unknown
  fired_on_drop_tp    — signal voted but candidate dropped, though
                        GT says satisfies/partial (recall LOSS from
                        aggregator threshold, not signal fault)
  fired_on_drop_fp    — signal voted but candidate dropped, and GT
                        agrees (correct drop — the aggregator did
                        its job)

Precision-when-fired = fired_on_accept_tp / (accept_tp + accept_fp)
Recall contribution   = accept_tp with this signal / total_TP_across_all_signals
Noise contribution    = accept_fp with this signal / total_FP

The interesting insight is `precision_when_fired` per signal — signals
where accepted candidates are mostly FPs are the noise-makers. Removing
weight or tightening threshold on those is the tuning direction.
"""
from __future__ import annotations
import json
import os
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, "/data/arioncomply/scripts")
from ship77e_compare import (
    _extract_musts_from_yaml, GT_DIR, DOCS,
)


import psycopg2


def _upload_to_doc_name(conn) -> dict[str, str]:
    """Map upload_id → filename via document_uploads."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)",
            ("00000000-0000-0000-0000-000000000001",),
        )
        cur.execute(
            """
            SELECT du.id::text, du.filename
            FROM document_uploads du
            WHERE du.tenant_id = '00000000-0000-0000-0000-000000000001'::uuid
            """
        )
        return {r[0]: r[1] for r in cur.fetchall()}


def _load_gt_by_doc() -> dict[str, dict[str, str]]:
    """{doc_filename: {must_id: verdict}} — GT lookup for TP/FP assessment."""
    out: dict[str, dict[str, str]] = {}
    for dk, (yaml_file, doc_name) in DOCS.items():
        gt = _extract_musts_from_yaml(GT_DIR / yaml_file)
        out[doc_name] = {m: v for (m, v, _c) in gt}
    return out


def _fetch_candidates(conn, upload_ids: list[str]) -> list[dict]:
    """Return list of candidate dicts joined with upload_id + logged_at."""
    upload_placeholders = ",".join(f"'{u}'::uuid" for u in upload_ids)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT set_config('app.tenant_id', %s, TRUE)",
            ("00000000-0000-0000-0000-000000000001",),
        )
        cur.execute(
            f"""
            SELECT upload_id::text, logged_at, candidates_sample
            FROM intake_consensus_log
            WHERE upload_id IN ({upload_placeholders})
              AND logged_at >= '2026-08-18 13:37:00+00'::timestamptz
              AND logged_at <  '2026-08-18 13:39:30+00'::timestamptz
            ORDER BY logged_at DESC
            """
        )
        out = []
        for upload_id, logged_at, samp in cur.fetchall():
            if not samp:
                continue
            for c in samp:
                c["_upload_id"] = upload_id
                out.append(c)
        return out


UPLOAD_IDS = {
    "dpia":     "5f59f505-45a2-4e7d-ba76-c4c6f4b2e08a",
    "ropa":     "28d9086c-37a1-4dce-b129-a3afd4e5bb18",
    "consent":  "10287fa5-f757-420b-98a4-ee9e34d02d25",
    "proc_ops": "453c55b3-1863-4461-90cb-f7ad058029f2",
    "dqa":      "fbb179a2-f565-4947-9d95-d9b3d6375691",
}


def main():
    conn = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    upload_to_name = _upload_to_doc_name(conn)
    gt_by_doc = _load_gt_by_doc()
    candidates = _fetch_candidates(conn, list(UPLOAD_IDS.values()))
    conn.close()

    print(f"Fetched {len(candidates)} candidate rows from consensus log")
    print(f"  by verdict: {Counter(c['verdict'] for c in candidates)}")
    print()

    # For each candidate, resolve GT verdict + label as accept/drop × TP/FP
    # scoring modes: strict (satisfies only) + lenient (satisfies + partial)

    # (signal, scoring_mode) → {"accept_tp": int, "accept_fp": int, "drop_tp": int, "drop_fp": int}
    signal_stats: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Global totals for context
    globals_ = {
        "strict":  {"accept_tp": 0, "accept_fp": 0, "drop_tp": 0, "drop_fp": 0},
        "lenient": {"accept_tp": 0, "accept_fp": 0, "drop_tp": 0, "drop_fp": 0},
    }

    for c in candidates:
        doc_name = upload_to_name.get(c["_upload_id"])
        if not doc_name:
            continue
        gt_map = gt_by_doc.get(doc_name, {})
        must_id = c.get("must_id")
        gt_verdict = gt_map.get(must_id, "unknown")
        verdict = c.get("verdict")
        signals = c.get("signals", [])

        for scoring in ("strict", "lenient"):
            is_expected = (
                gt_verdict == "satisfies"
                if scoring == "strict"
                else gt_verdict in ("satisfies", "partial")
            )
            if verdict == "accept":
                bucket = "accept_tp" if is_expected else "accept_fp"
            else:
                bucket = "drop_tp" if is_expected else "drop_fp"

            globals_[scoring][bucket] += 1
            for sig in signals:
                signal_stats[(sig, scoring)][bucket] += 1

    for scoring in ("strict", "lenient"):
        g = globals_[scoring]
        print("=" * 68)
        print(f"AGGREGATE ({scoring})")
        print("=" * 68)
        total_accept = g["accept_tp"] + g["accept_fp"]
        total_drop   = g["drop_tp"]   + g["drop_fp"]
        p = g["accept_tp"] / total_accept if total_accept else 0.0
        r_denom = g["accept_tp"] + g["drop_tp"]   # all "should have been accepted"
        r = g["accept_tp"] / r_denom if r_denom else 0.0
        print(f"  n_candidates = {total_accept + total_drop}")
        print(f"  accept_tp={g['accept_tp']} accept_fp={g['accept_fp']} "
              f"drop_tp={g['drop_tp']} drop_fp={g['drop_fp']}")
        print(f"  aggregate precision (of accepts): {p:.1%}")
        print(f"  aggregate recall (found / should-have-found): {r:.1%}")
        print()

        # Per-signal table
        print(f"  {'signal':<24} {'fires':>6} {'p_when_fired':>13} "
              f"{'recall_contrib':>15} {'noise_contrib':>14}")
        print(f"  {'-'*24} {'-'*6} {'-'*13} {'-'*15} {'-'*14}")
        rows = []
        for (sig, sc), stats in signal_stats.items():
            if sc != scoring:
                continue
            fires_accept = stats["accept_tp"] + stats["accept_fp"]
            fires_drop   = stats["drop_tp"]   + stats["drop_fp"]
            fires_all    = fires_accept + fires_drop
            if fires_all == 0:
                continue
            p_fired = (stats["accept_tp"] / fires_accept) if fires_accept else 0.0
            recall_contrib = (stats["accept_tp"] / g["accept_tp"]) if g["accept_tp"] else 0.0
            noise_contrib  = (stats["accept_fp"] / g["accept_fp"]) if g["accept_fp"] else 0.0
            rows.append((sig, fires_all, p_fired, recall_contrib, noise_contrib))
        # Sort by noise contribution descending
        rows.sort(key=lambda r: -r[4])
        for sig, fires_all, p_fired, rc, nc in rows:
            print(f"  {sig:<24} {fires_all:>6} {p_fired:>12.1%}  {rc:>14.1%}  {nc:>13.1%}")
        print()

    # Which signals fire on drops (aggregator worked) vs accepts (contributed)?
    # If a signal fires almost equally on both, it doesn't discriminate.
    print("=" * 68)
    print("SIGNAL DISCRIMINATION (does firing predict acceptance?)")
    print("=" * 68)
    print(f"  {'signal':<24} {'fires_accept':>13} {'fires_drop':>11} {'accept_rate':>13}")
    print(f"  {'-'*24} {'-'*13} {'-'*11} {'-'*13}")
    disc_rows = []
    for (sig, sc), stats in signal_stats.items():
        if sc != "strict":
            continue
        fa = stats["accept_tp"] + stats["accept_fp"]
        fd = stats["drop_tp"]   + stats["drop_fp"]
        if fa + fd == 0:
            continue
        rate = fa / (fa + fd)
        disc_rows.append((sig, fa, fd, rate))
    disc_rows.sort(key=lambda r: -r[3])
    for sig, fa, fd, rate in disc_rows:
        print(f"  {sig:<24} {fa:>13} {fd:>11} {rate:>12.1%}")


if __name__ == "__main__":
    main()
