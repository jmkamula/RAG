"""Writer module — persist Stage I proposals to workbook_intake_proposal.

Splits cleanly from rag/intake/workbook_discovery.py (which stays pure-
functional and DB-free). Callers (CLI, future Stage II) instantiate this
when they need durable proposals.

RLS: every connection must `SELECT set_config('app.tenant_id', ..., TRUE)`
before the INSERT. arioncomply_app has no BYPASSRLS.
See [[rls-tenant-context-for-app-user]].
"""
from __future__ import annotations

import json
from dataclasses import asdict
from uuid import UUID, uuid4

from .workbook_discovery import SheetProposal


def persist_proposals(
    pg,
    tenant_id: UUID | str,
    workbook_uri: str,
    proposals: list[SheetProposal],
    *,
    run_id: UUID | None = None,
) -> UUID:
    """Insert proposals as a single discovery run. Returns the run_id.

    `pg` is a psycopg2 connection. Caller owns commit/rollback semantics
    only insofar as we commit at the end; if any INSERT raises, the caller
    sees a rolled-back transaction (we re-raise).
    """
    run_uuid = run_id or uuid4()
    tenant_str = str(tenant_id)

    try:
        with pg.cursor() as cur:
            # Required for every read/write under arioncomply_app — RLS
            # policies pass via tenant_id column on the row, but app code
            # convention is to set this so future RLS policies that read
            # current_setting() Just Work.
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )

            for p in proposals:
                cur.execute(
                    """
                    INSERT INTO workbook_intake_proposal (
                        tenant_id, discovery_run_id, workbook_uri, sheet_name,
                        mapping_id, mapping_path, confidence, header_row,
                        row_count, proposal, status
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending'
                    )
                    """,
                    (
                        tenant_str,
                        str(run_uuid),
                        workbook_uri,
                        p.sheet,
                        p.mapping_id,
                        p.mapping_path,
                        p.confidence,
                        p.header_row,
                        p.row_count,
                        json.dumps(asdict(p)),
                    ),
                )
        pg.commit()
    except Exception:
        pg.rollback()
        raise

    return run_uuid
