"""
rag/tenant_standards.py — tenant framework enrollment.

Ship 104'.c/d (2026-09-02).

Extracts the framework enrollment logic from scripts/dev/create_tenant.py
into a reusable module so both the CLI (create_tenant.py --frameworks
...) and the UI (Get Started picker + Profile add-framework surface)
route through the same code. Ensures posture_controls seeding stays
consistent across both entry points.

Public functions:
    list_enrollable(pg_conn) -> list[dict]
        All standards that a tenant CAN enrol in (loaded_in_graph=TRUE
        entries in the standards catalog: ISO 27001, ISO 27701, GDPR
        as of Ship 102'). Includes id / name / short_name / standard_type
        / role / description / recommended flag.

    list_enrolled(pg_conn, tenant_id) -> list[dict]
        Standards the tenant is currently enrolled in, with control
        counts for the enrolled-vs-total display.

    enroll(pg_conn, neo_driver, tenant_id, standard_ids) -> dict
        Enrols the tenant in one or more standards. For each:
          - INSERT INTO tenant_standards (idempotent on conflict)
          - Query Neo4j for curated RequirementNodes in that standard
          - INSERT posture_controls rows (finding='Not assessed')
        Returns per-standard result: enrolled ✓ / already_enrolled /
        error, with posture-rows-seeded count.

Both endpoints connect via the runtime pool (arioncomply_app) with
app.tenant_id set by the caller. Neo4j uses whatever driver the
caller provides (typically fresh for the request).
"""
from __future__ import annotations
import os
import sys

from neo4j import GraphDatabase


# Standards that ship in the golden catalog per Ship 102'.
# Order matters — this is the display order in the picker.
# `recommended` gets a badge in the UI.
_ENROLLABLE_ORDER = [
    "ISO27001:2022",   # recommended anchor for most SMEs
    "GDPR:2016/679",   # if EU or UK data subjects
    "ISO27701:2019",   # privacy extension on top of 27001
]

_RECOMMENDED_ID = "ISO27001:2022"


def _new_neo4j_driver():
    """Fresh Neo4j driver from environment. Caller must .close()."""
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687"),
        auth = (
            os.getenv("NEO4J_USER",     "neo4j"),
            os.getenv("NEO4J_PASSWORD", ""),
        ),
    )


def _curated_controls_for(std_id: str, neo_driver) -> list[dict]:
    """Every curated control for a standard (RequirementNode with a
    SATISFIED_BY FulfilmentSpec). Same query as create_tenant.py's
    _curated_controls_for."""
    with neo_driver.session() as s:
        rows = s.run("""
            MATCH (rn:RequirementNode {standard_id: $s})
                  -[:SATISFIED_BY]->(:FulfilmentSpec)
            RETURN DISTINCT rn.ref AS ref, rn.title AS title
            ORDER BY rn.ref
        """, s=std_id).data()
    return rows


def list_enrollable(pg_conn) -> list[dict]:
    """Return the catalog of standards a tenant can enrol in, in
    display order, with a `recommended` flag for the anchor standard.
    """
    with pg_conn.cursor() as cur:
        # standards catalog has more entries (guidance / extensions
        # / frameworks not yet implemented). Filter to the ones our
        # golden catalog actually populates in Neo4j.
        placeholders = ",".join("%s" for _ in _ENROLLABLE_ORDER)
        cur.execute(f"""
            SELECT id, full_name, short_name, standard_type, role,
                   description, jurisdiction
              FROM standards
             WHERE id IN ({placeholders})
        """, tuple(_ENROLLABLE_ORDER))
        by_id = {r[0]: r for r in cur.fetchall()}

    out = []
    for sid in _ENROLLABLE_ORDER:
        r = by_id.get(sid)
        if not r:
            continue
        out.append({
            "id":             r[0],
            "full_name":      r[1],
            "short_name":     r[2],
            "standard_type":  r[3],
            "role":           r[4],
            "description":    r[5],
            "jurisdiction":   r[6],
            "recommended":    (r[0] == _RECOMMENDED_ID),
        })
    return out


def list_enrolled(pg_conn, tenant_id: str) -> list[dict]:
    """Return the tenant's enrolled standards with control counts.
    Caller has set app.tenant_id via set_config.
    """
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT ts.standard_id,
                   s.full_name, s.short_name,
                   ts.status,
                   ts.enrolled_at,
                   (SELECT COUNT(*) FROM posture_controls pc
                     WHERE pc.tenant_id = ts.tenant_id
                       AND pc.standard_id = ts.standard_id
                       AND pc.is_active = TRUE) AS control_count
              FROM tenant_standards ts
              JOIN standards s ON s.id = ts.standard_id
             WHERE ts.tenant_id = %s
               AND ts.is_active = TRUE
             ORDER BY ts.enrolled_at
        """, (tenant_id,))
        rows = cur.fetchall()

    return [
        {
            "standard_id":   r[0],
            "full_name":     r[1],
            "short_name":    r[2],
            "status":        r[3],
            "enrolled_at":   r[4].isoformat() if r[4] else None,
            "control_count": r[5],
        }
        for r in rows
    ]


def enrolled_standard_ids(pg_conn, tenant_id: str) -> list[str]:
    """Return the tenant's enrolled standard_ids (active only). Small
    helper for Ship 104'.e scoping across topics + get-started +
    dashboard so surfaces that fan out beyond the enrolment can grey/
    filter accordingly."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT standard_id FROM tenant_standards
             WHERE tenant_id = %s AND is_active = TRUE
        """, (tenant_id,))
        return [r[0] for r in cur.fetchall()]


def enroll(
    pg_conn,
    neo_driver,
    tenant_id: str,
    standard_ids: list[str],
) -> dict:
    """Enrol the tenant in one or more standards. For each:
      - INSERT INTO tenant_standards (idempotent — ON CONFLICT DO NOTHING)
      - Query Neo4j for the standard's curated controls
      - INSERT posture_controls rows with finding='Not assessed'

    Returns per-standard result:
        {"ISO27001:2022": {"status": "enrolled" | "already_enrolled" | "error",
                            "seeded": N,
                            "error": str | None}}
    """
    # Validate every id is one we support
    unknown = [s for s in standard_ids if s not in _ENROLLABLE_ORDER]
    if unknown:
        raise ValueError(f"Unknown standard_id(s): {unknown}. Allowed: {_ENROLLABLE_ORDER}")

    results: dict[str, dict] = {}

    with pg_conn.cursor() as cur:
        # RLS: caller must have set app.tenant_id already.
        for std_id in standard_ids:
            try:
                # Was this tenant already enrolled?
                cur.execute("""
                    SELECT 1 FROM tenant_standards
                     WHERE tenant_id = %s AND standard_id = %s AND is_active = TRUE
                """, (tenant_id, std_id))
                already = cur.fetchone() is not None

                if already:
                    results[std_id] = {
                        "status": "already_enrolled",
                        "seeded": 0,
                        "error":  None,
                    }
                    continue

                # Insert tenant_standards row (status='implementing' is the
                # convention from create_tenant.py).
                cur.execute("""
                    INSERT INTO tenant_standards (tenant_id, standard_id, status)
                    VALUES (%s, %s, 'implementing')
                    ON CONFLICT (tenant_id, standard_id) DO UPDATE
                        SET is_active = TRUE, deleted_at = NULL
                """, (tenant_id, std_id))

                # Seed posture_controls from Neo4j.
                ctrls = _curated_controls_for(std_id, neo_driver)
                seeded = 0
                for c in ctrls:
                    node_id = f"{std_id}:{c['ref']}"
                    cur.execute("""
                        INSERT INTO posture_controls (
                            tenant_id, standard_id, control_ref, node_id,
                            finding, source
                        ) VALUES (%s, %s, %s, %s, 'Not assessed', 'Not assessed')
                        ON CONFLICT DO NOTHING
                    """, (tenant_id, std_id, c["ref"], node_id))
                    seeded += 1

                results[std_id] = {
                    "status": "enrolled",
                    "seeded": seeded,
                    "error":  None,
                }
            except Exception as e:
                # Isolate per-standard failures — don't abort the whole
                # enrolment on one bad standard.
                results[std_id] = {
                    "status": "error",
                    "seeded": 0,
                    "error":  str(e),
                }

    pg_conn.commit()
    return results
