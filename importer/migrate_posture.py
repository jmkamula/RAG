"""
Migrate verified posture findings from real audit evidence into Postgres.

Sources:
  A — URS external audit report 2025/214427/OA1 (Martin Kubiš, April-May 2025)
      Section 7.0 OFI comments — 4 OFI findings, 0 NCs raised
      Arion Networks PASSED — certification recommended

  B — Internal audit (AUD001, April 2025)
      2 internal NC findings (F001, F002)

  C — SoA self-assessment (version 1.0, 11.04.2025)
      73 Implemented (Comply), 20 N/A — already in Postgres from workbook import

DISCARD: seed data (A.8.24, A.8.11, A.5.26 OFI, 6.1.2, Art.32)
  These were invented at project start — no real evidence basis.
"""
import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

import psycopg2

TENANT_ID    = "00000000-0000-0000-0000-000000000001"
TENANT_SHORT = "ARN"

URS   = "URS Certification s.r.o. (auditor: Martin Kubiš)"
ARION = "Arion Networks Internal Audit (AUD001, April 2025)"

VERIFIED_FINDINGS = [
    # External audit OFIs — URS 2025/214427/OA1 Section 7.0
    {
        "node_id":          "ISO27001:2022:A.5.19",
        "standard_id":      "ISO27001:2022",
        "control_ref":      "A.5.19",
        "finding":          "OFI",
        "confidence":       "high",
        "gap_description":  "Business partners not evaluated as part of supplier "
                            "assessment process",
        "action_required":  "Extend supplier assessment to cover business partners",
        "source":           "assessor",
        "source_authority": URS,
        "external_ref":     "F004",
        "audit_ref":        "URS 2025/214427/OA1 OFI #1",
    },
    {
        "node_id":          "ISO27001:2022:A.5.18",
        "standard_id":      "ISO27001:2022",
        "control_ref":      "A.5.18",
        "finding":          "OFI",
        "confidence":       "high",
        "gap_description":  "No formal review of user access rights implemented",
        "action_required":  "Implement formal periodic access rights review process",
        "source":           "assessor",
        "source_authority": URS,
        "external_ref":     "F005",
        "audit_ref":        "URS 2025/214427/OA1 OFI #2",
    },
    {
        "node_id":          "ISO27001:2022:A.8.19",
        "standard_id":      "ISO27001:2022",
        "control_ref":      "A.8.19",
        "finding":          "OFI",
        "confidence":       "high",
        "gap_description":  "No allow/deny list for software; ChatGPT used without policy",
        "action_required":  "Define approved software list; create AI tools policy",
        "source":           "assessor",
        "source_authority": URS,
        "external_ref":     "F006",
        "audit_ref":        "URS 2025/214427/OA1 OFI #3",
    },
    {
        "node_id":          "ISO27001:2022:9.2",
        "standard_id":      "ISO27001:2022",
        "control_ref":      "9.2",
        "finding":          "OFI",
        "confidence":       "high",
        "gap_description":  "Audit reports do not list controls/clauses audited",
        "action_required":  "Update audit report template to include control coverage",
        "source":           "assessor",
        "source_authority": URS,
        "external_ref":     "F007",
        "audit_ref":        "URS 2025/214427/OA1 OFI #4",
    },
    # Internal audit NCs — AUD001 April 2025
    {
        "node_id":          "ISO27001:2022:A.5.18",
        "standard_id":      "ISO27001:2022",
        "control_ref":      "A.5.18",
        "finding":          "NC",
        "confidence":       "high",
        "gap_description":  "Access register records from Q4 2024 incomplete",
        "action_required":  "Complete and sign off Q4 2024 access register by 30 May 2025",
        "source":           "assessor",
        "source_authority": ARION,
        "external_ref":     "F001",
        "audit_ref":        "AUD001 internal audit",
    },
    {
        "node_id":          "ISO27001:2022:A.5.26",
        "standard_id":      "ISO27001:2022",
        "control_ref":      "A.5.26",
        "finding":          "NC",
        "confidence":       "high",
        "gap_description":  "Incident response drill planned for Q1 2025 not conducted",
        "action_required":  "Schedule and conduct IR drill; document outcome",
        "source":           "assessor",
        "source_authority": ARION,
        "external_ref":     "F002",
        "audit_ref":        "AUD001 internal audit",
    },
]

PRIORITY = {"NC": 3, "OFI": 2, "Comply": 1, "N/A": 0, "Not assessed": -1}


def main():
    pg = psycopg2.connect(os.getenv("DATABASE_URL"))
    updated = inserted = skipped = 0

    print("=== POSTURE MIGRATION (verified findings only) ===\n")
    print("Discarding seed data — not from real evidence:")
    for ref in ["A.8.24 OFI", "A.8.11 NC", "6.1.2 OFI", "Art.32 OFI"]:
        print(f"  {ref}")
    print()

    with pg.cursor() as cur:
        for rec in VERIFIED_FINDINGS:
            cur.execute("""
                SELECT id, finding, external_ref
                FROM posture_controls
                WHERE tenant_id  = %s
                  AND standard_id = %s
                  AND control_ref = %s
            """, (TENANT_ID, rec["standard_id"], rec["control_ref"]))
            rows = cur.fetchall()

            new_prio = PRIORITY.get(rec["finding"], 0)

            if rows:
                # Prefer SoA row (no external_ref) for updating
                soa_row = next((r for r in rows if not r[2]), rows[0])
                row_id, current_finding, _ = soa_row
                cur_prio = PRIORITY.get(current_finding, 0)

                if new_prio >= cur_prio:
                    cur.execute("""
                        UPDATE posture_controls SET
                            finding          = %s,
                            confidence       = %s,
                            gap_description  = %s,
                            action_required  = %s,
                            source           = %s,
                            source_authority = %s,
                            soa_notes        = %s,
                            last_updated     = NOW()
                        WHERE id = %s
                    """, (
                        rec["finding"], rec["confidence"],
                        rec["gap_description"], rec["action_required"],
                        rec["source"], rec.get("source_authority"),
                        rec.get("audit_ref"), row_id,
                    ))
                    print(f"  ✓ UPDATE {rec['control_ref']:8s} "
                          f"{current_finding} → {rec['finding']:5s} "
                          f"[{rec['external_ref']}]")
                    updated += 1
                else:
                    print(f"  - SKIP  {rec['control_ref']:8s} "
                          f"keeping {current_finding} [{rec['external_ref']}]")
                    skipped += 1
            else:
                cur.execute("""
                    INSERT INTO posture_controls (
                        tenant_id, standard_id, control_ref, node_id,
                        finding, confidence, gap_description, action_required,
                        source, source_authority, soa_notes, workbook_imported
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,FALSE)
                    RETURNING id
                """, (
                    TENANT_ID, rec["standard_id"], rec["control_ref"], rec["node_id"],
                    rec["finding"], rec["confidence"],
                    rec["gap_description"], rec["action_required"],
                    rec["source"], rec.get("source_authority"), rec.get("audit_ref"),
                ))
                new_id = cur.fetchone()[0]
                cur.execute("SELECT next_platform_ref(%s,'PC',%s)",
                            (TENANT_ID, TENANT_SHORT))
                platform_ref = cur.fetchone()[0]
                cur.execute("UPDATE posture_controls SET platform_ref=%s WHERE id=%s",
                            (platform_ref, new_id))
                print(f"  ✓ INSERT {rec['control_ref']:8s} {rec['finding']:5s} "
                      f"[{platform_ref}] [{rec['external_ref']}]")
                inserted += 1

    pg.commit()
    pg.close()
    print(f"\n✓ {updated} updated, {inserted} inserted, {skipped} skipped")
    print("""
Verify:
  SELECT platform_ref, control_ref, finding, source, soa_notes
  FROM posture_controls
  WHERE tenant_id='00000000-0000-0000-0000-000000000001'
    AND finding IN ('NC','OFI')
  ORDER BY finding DESC, control_ref;""")


if __name__ == "__main__":
    main()
