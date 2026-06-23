"""Writer module — persist Stage I proposals + per-MUST document_findings.

Single transaction:
  1. INSERT workbook_intake_proposal row (sheet-level breadcrumb).
  2. INSERT one document_findings row per (pass, satisfied-or-partial MUST).
     - satisfied → status='present', confidence='high'
     - partial   → status='partial', confidence='medium'
     - missing   → no row written (gaps surface via curated MUST list, not
                   via document_findings)
     - review_status defaults to 'pending' → lands in posture Stage 1 queue.
     - inference_source='workbook', checklist_item_id populated, document_id
       points at the source upload, workbook_proposal_id links back to (1).

This is the merge point: posture Stage 1 (existing chat surface) reviews
both LLM-extracted and workbook-fingerprinted findings through one queue.

RLS: every connection must `SELECT set_config('app.tenant_id', ..., TRUE)`
before reads/writes. arioncomply_app has no BYPASSRLS.
See [[rls-tenant-context-for-app-user]].
"""
from __future__ import annotations

import json
from dataclasses import asdict
from uuid import UUID, uuid4

from enrichment.documents import document_requirements as DR

from .workbook_discovery import PassProposal, SheetProposal


# Build a {req_id: standard_id} index once at module load. Covers
# ALL_EVIDENCE_REQUIREMENTS plus every DerivedSpec.direct_evidence so
# workbook passes that target DerivedSpec direct leaves resolve cleanly.
def _build_req_standard_index() -> dict[str, str]:
    idx: dict[str, str] = {}
    for r in DR.ALL_EVIDENCE_REQUIREMENTS:
        idx[r.id] = r.standard_id
    for name in dir(DR):
        obj = getattr(DR, name)
        if isinstance(obj, DR.DerivedSpec):
            for r in obj.direct_evidence or []:
                idx[r.id] = r.standard_id
    return idx


_REQ_STANDARD: dict[str, str] = _build_req_standard_index()


def _standard_for(req_id: str) -> str:
    """Resolve target_evidence_requirement → standard_id."""
    try:
        return _REQ_STANDARD[req_id]
    except KeyError as e:
        raise ValueError(
            f"target_evidence_requirement {req_id!r} not in curated "
            f"ALL_EVIDENCE_REQUIREMENTS or any DerivedSpec.direct_evidence. "
            f"Run scripts/validate_workbook_mappings.py before persisting."
        ) from e


def _findings_for_pass(
    pass_prop: PassProposal,
    sheet_name: str,
    standard_id: str,
) -> list[tuple]:
    """One row per satisfied/partial MUST. Returns tuples ready for execute().

    Tuple shape mirrors the INSERT below.
    """
    rows: list[tuple] = []

    def _row(must_id: str, status: str, confidence: str) -> tuple:
        column = pass_prop.matched_columns.get(must_id, "?")
        excerpt = f"sheet {sheet_name!r} col {column!r}"
        # Cap at 500 like the LLM extractor's policy.
        return (
            pass_prop.target_control,
            standard_id,
            must_id,
            status,
            confidence,
            excerpt[:500],
            "workbook",
        )

    for must_id in pass_prop.satisfied:
        rows.append(_row(must_id, "present", "high"))
    for must_id in pass_prop.partial:
        rows.append(_row(must_id, "partial", "medium"))

    return rows


def persist_proposals(
    pg,
    tenant_id: UUID | str,
    workbook_uri: str,
    client_document_id: UUID | str,
    proposals: list[SheetProposal],
    *,
    run_id: UUID | None = None,
) -> tuple[UUID, int]:
    """Insert proposals + per-MUST findings as a single discovery run.

    Returns (run_id, findings_count). Single transaction; commits on success,
    rolls back + re-raises on error.
    """
    run_uuid = run_id or uuid4()
    tenant_str = str(tenant_id)
    doc_str = str(client_document_id)

    findings_written = 0
    try:
        with pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (tenant_str,),
            )

            # Supersede prior extract batches for this document before writing
            # the new one. Same transaction — if writes fail, rollback restores
            # the prior batch. Without this, re-extracts pile up duplicate
            # findings (see multipath_data_cleanup_2026_06_23 retrospective).
            if proposals:
                cur.execute(
                    """
                    UPDATE workbook_intake_proposal
                    SET status = 'superseded',
                        superseded_at = now()
                    WHERE client_document_id = %s
                      AND status = 'pending'
                    """,
                    (doc_str,),
                )
                cur.execute(
                    """
                    UPDATE document_findings
                    SET is_active = FALSE,
                        review_status = 'rejected',
                        rejection_reason = %s,
                        reviewed_at = COALESCE(reviewed_at, now())
                    WHERE document_id = %s
                      AND inference_source = 'workbook'
                      AND is_active = TRUE
                    """,
                    (f"superseded_by_extract_run:{run_uuid}", doc_str),
                )

            for p in proposals:
                cur.execute(
                    """
                    INSERT INTO workbook_intake_proposal (
                        tenant_id, discovery_run_id, workbook_uri, sheet_name,
                        mapping_id, mapping_path, confidence, header_row,
                        row_count, proposal, status, client_document_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', %s
                    )
                    RETURNING id
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
                        doc_str,
                    ),
                )
                proposal_id = cur.fetchone()[0]

                for pp in p.passes:
                    standard_id = _standard_for(pp.target_evidence_requirement)
                    for (
                        control_ref,
                        std_id,
                        checklist_item_id,
                        status,
                        confidence,
                        excerpt,
                        inf_source,
                    ) in _findings_for_pass(pp, p.sheet, standard_id):
                        cur.execute(
                            """
                            INSERT INTO document_findings (
                                tenant_id, document_id,
                                control_ref, standard_id, checklist_item_id,
                                status, confidence, excerpt,
                                inference_source, workbook_proposal_id,
                                is_active, retention_class
                            ) VALUES (
                                %s, %s,
                                %s, %s, %s,
                                %s, %s, %s,
                                %s, %s,
                                TRUE, 'compliance'
                            )
                            """,
                            (
                                tenant_str, doc_str,
                                control_ref, std_id, checklist_item_id,
                                status, confidence, excerpt,
                                inf_source, proposal_id,
                            ),
                        )
                        findings_written += 1

        pg.commit()
    except Exception:
        pg.rollback()
        raise

    return run_uuid, findings_written
