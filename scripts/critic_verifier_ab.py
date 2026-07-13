#!/usr/bin/env python3
"""
Critic-verifier A/B runner — Phase 6 evaluation.

For each doc in the sample, run TWO re-extractions:
  Phase A: baseline (USE_CRITIC_VERIFIER_PASS=0)
  Phase B: critic-verifier (USE_CRITIC_VERIFIER_PASS=1)

For each phase capture:
  - findings_kept / findings_raw / distinct_musts_bound (from intake_trace_log)
  - Auto-approved vs pending Stage-1 count (from document_findings)
  - LLM cost + tokens + latency (from ai_call_log)
  - Yield ratio %

Prints a comparison table + a recommendation.

Usage:
  # 1. Kill the API you have running
  # 2. Run this script — it manages API restarts + flag flips
  python scripts/critic_verifier_ab.py

Note: this DOES clear existing findings on each sampled doc and
re-extract them twice. Runs on Arion by default (tenant 00000000-…-01).
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import time
import uuid

import psycopg2

TENANT_ID    = "00000000-0000-0000-0000-000000000001"
API_KEY      = "arion_dev_key_2026"
API_URL      = "http://localhost:8080"
DB_PARAMS    = dict(host="127.0.0.1", dbname="arioncomply_compliance", user="arioncomply")

# Sample — pick 6 for diversity in size + doc type
SAMPLE_DOCS = [
    ("5f59f505-45a2-4e7d-ba76-c4c6f4b2e08a", "DPIA Procedure"),
    ("fbb179a2-f565-4947-9d95-d9b3d6375691", "Data Quality Accuracy Procedure"),
    ("10287fa5-f757-420b-98a4-ee9e34d02d25", "Consent Management Procedure"),
    ("ac1294bc-8d59-4e12-b0b1-3997c7cfa130", "Purpose Limitation Procedure"),
    ("453c55b3-1863-4461-90cb-f7ad058029f2", "Processor Operations Procedures"),
    ("28d9086c-37a1-4dce-b129-a3afd4e5bb18", "Records of Processing Activities"),
]

API_SERVER_CMD = [
    "python3", "/data/arioncomply/api_server.py",
]


def _sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def kill_api():
    _sh(["pkill", "-f", "api_server.py"])
    time.sleep(2)


def start_api(critic_on: bool) -> subprocess.Popen:
    env = dict(os.environ)
    env["PYTHONPATH"] = "/data/arioncomply"
    if critic_on:
        env["USE_CRITIC_VERIFIER_PASS"] = "1"
    else:
        env.pop("USE_CRITIC_VERIFIER_PASS", None)
    proc = subprocess.Popen(
        API_SERVER_CMD,
        env=env,
        stdout=open("/tmp/api_ab.log", "a"),
        stderr=subprocess.STDOUT,
    )
    # Wait for API to be ready
    import urllib.request, urllib.error
    for _ in range(30):
        try:
            urllib.request.urlopen(f"{API_URL}/openapi.json", timeout=2)
            return proc
        except Exception:
            time.sleep(1)
    raise RuntimeError("API did not come up in 30s")


def clear_findings(upload_id: str, pg) -> None:
    with pg.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (TENANT_ID,))
        cur.execute("""
            UPDATE document_findings
               SET is_active=FALSE, deleted_at=NOW(),
                   deletion_reason='critic_ab_run'
             WHERE document_id IN (
                    SELECT id FROM client_documents
                     WHERE tenant_id = %s::uuid
                       AND is_current = TRUE
                       AND filename IN (
                             SELECT filename FROM document_uploads
                              WHERE id = %s::uuid
                           )
                   )
               AND is_active = TRUE
        """, (TENANT_ID, upload_id))
    pg.commit()


def trigger_reextract(upload_id: str) -> None:
    import urllib.request
    req = urllib.request.Request(
        f"{API_URL}/api/v1/admin/uploads/{upload_id}/reextract",
        method="POST",
        headers={"X-API-Key": API_KEY},
    )
    urllib.request.urlopen(req, timeout=10).read()


def wait_for_completion(upload_id: str, pg, max_wait_s: int = 120) -> str:
    """Poll document_uploads until extraction_status != processing."""
    deadline = time.time() + max_wait_s
    while time.time() < deadline:
        time.sleep(4)
        with pg.cursor() as cur:
            cur.execute("SELECT extraction_status FROM document_uploads WHERE id = %s::uuid", (upload_id,))
            status = (cur.fetchone() or ["?"])[0]
        if status in ("completed", "failed"):
            return status
    return "timeout"


def snapshot_metrics(upload_id: str, pg) -> dict:
    """Read the latest intake_trace_log + ai_call_log for this upload."""
    with pg.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (TENANT_ID,))
        cur.execute("""
            SELECT llm_calls, findings_raw, findings_kept, distinct_musts_bound,
                   leaf_musts_in_scope, yield_ratio_pct,
                   dropped_hallucinated, dropped_short_quote, dropped_questionnaire
              FROM intake_trace_log
             WHERE upload_id = %s AND stage = 'extract'
             ORDER BY traced_at DESC LIMIT 1
        """, (upload_id,))
        row = cur.fetchone() or (0,)*9
        trace = {
            "llm_calls":            row[0],
            "findings_raw":         row[1],
            "findings_kept":        row[2],
            "distinct_musts_bound": row[3],
            "leaf_musts_in_scope":  row[4],
            "yield_ratio_pct":      row[5],
            "dropped_hallucinated": row[6],
            "dropped_short_quote":  row[7],
            "dropped_questionnaire": row[8],
        }
        # Cost from ai_call_log — extraction calls in the last 3 minutes
        # for this upload's tenant, purpose in (extractor, extractor_pass2)
        cur.execute("""
            SELECT count(*), coalesce(sum(cost_usd), 0)::numeric(12,4),
                   coalesce(sum(tokens_in), 0), coalesce(sum(tokens_out), 0),
                   coalesce(sum(latency_ms), 0)
              FROM ai_call_log
             WHERE tenant_id = %s::uuid
               AND purpose IN ('extractor','extractor_pass2','enricher')
               AND called_at > NOW() - INTERVAL '3 minutes'
        """, (TENANT_ID,))
        c = cur.fetchone()
        trace["ai_calls"]     = int(c[0])
        trace["ai_cost_usd"]  = float(c[1])
        trace["tokens_in"]    = int(c[2])
        trace["tokens_out"]   = int(c[3])
        trace["ai_latency_ms"] = int(c[4])
        # Findings breakdown — approved vs pending
        cur.execute("""
            SELECT
              count(*) FILTER (WHERE review_status='approved'),
              count(*) FILTER (WHERE review_status='pending'),
              count(*)
              FROM document_findings df
              JOIN client_documents cd ON cd.id = df.document_id
             WHERE cd.tenant_id = %s::uuid
               AND cd.is_current = TRUE
               AND df.is_active = TRUE
               AND cd.filename IN (
                    SELECT filename FROM document_uploads WHERE id = %s::uuid
                   )
        """, (TENANT_ID, upload_id))
        f = cur.fetchone() or (0, 0, 0)
        trace["auto_approved"] = int(f[0])
        trace["pending"]       = int(f[1])
        trace["total"]         = int(f[2])
    return trace


def run_phase(critic_on: bool, pg) -> dict:
    label = "critic" if critic_on else "baseline"
    print(f"\n=== Phase: {label} (USE_CRITIC_VERIFIER_PASS={int(critic_on)}) ===")
    kill_api()
    proc = start_api(critic_on)
    time.sleep(2)  # extra warmup

    per_doc: dict[str, dict] = {}
    for uid, label_doc in SAMPLE_DOCS:
        print(f"  {label_doc} …", end=" ", flush=True)
        clear_findings(uid, pg)
        trigger_reextract(uid)
        status = wait_for_completion(uid, pg)
        if status != "completed":
            print(f"[{status}]")
            per_doc[label_doc] = {"error": status}
            continue
        # Small pause so ai_call_log rows land
        time.sleep(2)
        m = snapshot_metrics(uid, pg)
        per_doc[label_doc] = m
        print(f"kept={m['findings_kept']}, "
              f"approved={m['auto_approved']}, "
              f"cost=${m['ai_cost_usd']:.4f}, "
              f"llm_calls={m['llm_calls']}")
    return per_doc


def main():
    pg = psycopg2.connect(**DB_PARAMS)
    try:
        baseline = run_phase(critic_on=False, pg=pg)
        critic   = run_phase(critic_on=True,  pg=pg)
    finally:
        pg.close()

    # Comparison table
    print("\n" + "="*100)
    print(f"{'Doc':<40} {'B kept':>7} {'C kept':>7} {'B appr':>7} {'C appr':>7} {'B $':>8} {'C $':>8} {'B calls':>7} {'C calls':>7}")
    print("-"*100)
    tot_b_kept = tot_c_kept = tot_b_appr = tot_c_appr = 0
    tot_b_cost = tot_c_cost = 0.0
    tot_b_calls = tot_c_calls = 0
    for label in sorted(set(baseline.keys()) | set(critic.keys())):
        b = baseline.get(label, {})
        c = critic.get(label, {})
        if "error" in b or "error" in c:
            continue
        row = [label[:40],
               b.get("findings_kept", 0), c.get("findings_kept", 0),
               b.get("auto_approved", 0), c.get("auto_approved", 0),
               b.get("ai_cost_usd", 0.0), c.get("ai_cost_usd", 0.0),
               b.get("llm_calls", 0), c.get("llm_calls", 0)]
        print(f"{row[0]:<40} {row[1]:>7} {row[2]:>7} {row[3]:>7} {row[4]:>7} "
              f"{row[5]:>8.4f} {row[6]:>8.4f} {row[7]:>7} {row[8]:>7}")
        tot_b_kept += row[1]; tot_c_kept += row[2]
        tot_b_appr += row[3]; tot_c_appr += row[4]
        tot_b_cost += row[5]; tot_c_cost += row[6]
        tot_b_calls += row[7]; tot_c_calls += row[8]
    print("-"*100)
    print(f"{'TOTAL':<40} {tot_b_kept:>7} {tot_c_kept:>7} {tot_b_appr:>7} {tot_c_appr:>7} "
          f"{tot_b_cost:>8.4f} {tot_c_cost:>8.4f} {tot_b_calls:>7} {tot_c_calls:>7}")

    # Ratios
    print()
    if tot_b_kept:
        print(f"Discovery gain:     {(tot_c_kept - tot_b_kept)/tot_b_kept*100:+.1f}% "
              f"(critic {tot_c_kept} vs baseline {tot_b_kept})")
    if tot_b_appr:
        print(f"Auto-approve gain:  {(tot_c_appr - tot_b_appr)/tot_b_appr*100:+.1f}% "
              f"(critic {tot_c_appr} vs baseline {tot_b_appr})")
    if tot_b_cost:
        print(f"Cost ratio:         {tot_c_cost/tot_b_cost:.2f}× "
              f"(critic ${tot_c_cost:.4f} vs baseline ${tot_b_cost:.4f})")
    print()

    # Write full snapshot to file for later analysis
    out_path = f"/data/arioncomply/results/critic_ab_{time.strftime('%Y%m%d_%H%M')}.json"
    with open(out_path, "w") as f:
        json.dump({"baseline": baseline, "critic": critic}, f, indent=2, default=str)
    print(f"Full snapshot: {out_path}")


if __name__ == "__main__":
    main()
