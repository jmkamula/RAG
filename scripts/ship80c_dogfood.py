#!/usr/bin/env python3
"""Ship 80'.c — dogfood the LLM-curated fingerprint YAMLs on the 5
baseline docs. Snapshot as run_f_vocab_curator.csv, then score against
ground truth to measure the recall lift over Ship 79'.c Run E.

Flow:
  1. Deactivate existing findings on the 5 docs.
  2. Re-extract each via /reextract (union+artefact mode, same as Ship 79'.c).
  3. Poll to completion.
  4. Snapshot findings via psql \\copy (client-side, no PostgreSQL server
     write permission required).
  5. Next: extend scripts/ship77e_compare.py to score run_f alongside.
"""
from urllib.request import Request, urlopen
import json, time, os, subprocess

API_KEY = "arion_dev_key_2026"
BASE = "http://localhost:8080"
DOCS = {
    "dpia":     "5f59f505-45a2-4e7d-ba76-c4c6f4b2e08a",
    "ropa":     "28d9086c-37a1-4dce-b129-a3afd4e5bb18",
    "consent":  "10287fa5-f757-420b-98a4-ee9e34d02d25",
    "proc_ops": "453c55b3-1863-4461-90cb-f7ad058029f2",
    "dqa":      "fbb179a2-f565-4947-9d95-d9b3d6375691",
}
OUT_CSV = "/data/arioncomply/docs/ground_truth/ship77d_measurement/run_f_vocab_curator.csv"


def deactivate_findings():
    import psycopg2
    conn = psycopg2.connect(
        host="127.0.0.1", dbname="arioncomply_compliance",
        user="arioncomply", password=os.getenv("ARION_OWNER_PW") or os.getenv("POSTGRES_PASSWORD", ""),
    )
    tid = "00000000-0000-0000-0000-000000000001"
    with conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tid,))
        cur.execute(
            """
            UPDATE document_findings df
               SET is_active = false, deletion_reason = 'ship80c_prep'
              FROM client_documents cd
             WHERE df.document_id = cd.id AND df.tenant_id = cd.tenant_id
               AND cd.filename IN (
                 'Data Quality Accuracy Procedure.docx',
                 'Data Protection Impact Assessment (DPIA) Procedure.docx',
                 'Records of Processing Activities.docx',
                 'Consent Management Procedure.docx',
                 'Processor Operations Procedures.docx')
               AND cd.tenant_id = %s::uuid
               AND df.is_active
            """, (tid,))
        n = cur.rowcount
        conn.commit()
        print(f"  deactivated {n} existing findings")
    conn.close()


def reextract_all():
    t_start = time.time()
    print(f"Run F start (union+artefact, LLM-curated fingerprints): t_start={t_start}")
    for name, upload_id in DOCS.items():
        boundary = "----ship80c_bnd"
        body = f"--{boundary}--\r\n".encode()
        try:
            r = urlopen(Request(
                f"{BASE}/api/v1/admin/uploads/{upload_id}/reextract",
                data=body, method="POST",
                headers={
                    "X-API-Key": API_KEY,
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                },
            ), timeout=10).read().decode()
            print(f"  {name}: {r[:80]}")
        except Exception as e:
            print(f"  {name}: ERROR {e}")

    print("\nPolling completion (union runs both paths, ~110s per doc)...")
    completed = set()
    for _ in range(160):
        time.sleep(15)
        for name, upload_id in DOCS.items():
            if name in completed:
                continue
            try:
                s = urlopen(Request(
                    f"{BASE}/api/v1/documents/{upload_id}/status",
                    headers={"X-API-Key": API_KEY}), timeout=5).read().decode()
                st = json.loads(s).get("status")
                if st in ("completed", "failed"):
                    completed.add(name)
                    print(f"  {name}: {st}  ({int(time.time()-t_start)}s)")
            except Exception as e:
                print(f"  {name}: poll err {e}")
        if len(completed) == 5:
            break
    print(f"\nRun F complete. elapsed={int(time.time()-t_start)}s")


def snapshot_findings():
    """Client-side \\copy via psql — no server write permission required."""
    tid = "00000000-0000-0000-0000-000000000001"
    sql = f"""
    SET LOCAL app.tenant_id = '{tid}';
    \\copy (
      SELECT cd.filename, df.control_ref, df.standard_id,
             df.checklist_item_id, df.status, df.confidence,
             LEFT(df.excerpt, 200) AS excerpt,
             df.inference_source, df.extracted_at::text
        FROM client_documents cd
        JOIN document_findings df
          ON df.document_id = cd.id AND df.tenant_id = cd.tenant_id
       WHERE cd.filename IN (
         'Data Quality Accuracy Procedure.docx',
         'Data Protection Impact Assessment (DPIA) Procedure.docx',
         'Records of Processing Activities.docx',
         'Consent Management Procedure.docx',
         'Processor Operations Procedures.docx')
         AND cd.tenant_id = '{tid}'::uuid
         AND df.is_active
         AND df.extracted_at > now() - interval '30 minutes'
    ) TO '{OUT_CSV}' WITH (FORMAT csv, HEADER);
    """
    env = os.environ.copy()
    env["PGPASSWORD"] = env.get("ARION_OWNER_PW") or env.get("POSTGRES_PASSWORD", "")
    subprocess.run(
        ["psql", "-h", "127.0.0.1", "-U", "arioncomply",
         "-d", "arioncomply_compliance", "-c", sql],
        env=env, check=True,
    )
    with open(OUT_CSV) as fh:
        n = sum(1 for _ in fh) - 1
    print(f"snapshot: {n} findings -> {OUT_CSV}")


if __name__ == "__main__":
    print("=== Ship 80'.c dogfood ===")
    deactivate_findings()
    reextract_all()
    snapshot_findings()
    print()
    print("Next: extend scripts/ship77e_compare.py to score run_f_vocab_curator.csv")
