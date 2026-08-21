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

    Ship 72'.c (2026-08-16) — validates each must_id against the
    canonical catalog (`FindingContract.catalog_recognises`). Mapping
    YAMLs with a typo in a MUST id used to silently insert a bad
    `checklist_item_id`; the SSoT reader would then drop the row on
    lookup, leaving evidence unbound with no trail. Now the workbook
    path logs + skips, same defensive posture as the templated path.
    """
    from rag.intake.finding_contract import catalog_recognises
    import logging as _logging
    _log = _logging.getLogger(__name__)

    rows: list[tuple] = []

    def _row(must_id: str, status: str, confidence: str) -> tuple | None:
        if not catalog_recognises(must_id):
            _log.warning(
                "workbook _findings_for_pass: skipping unknown must_id %r "
                "on sheet %r (not in ALL_EVIDENCE_REQUIREMENTS ∪ DerivedSpec "
                "direct_evidence — likely a mapping YAML typo)",
                must_id, sheet_name,
            )
            return None
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
        row = _row(must_id, "present", "high")
        if row is not None:
            rows.append(row)
    for must_id in pass_prop.partial:
        row = _row(must_id, "partial", "medium")
        if row is not None:
            rows.append(row)

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
                    # Track finding_id per MUST so cite emission can attribute back.
                    finding_id_by_must: dict[str, str] = {}
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
                            RETURNING id
                            """,
                            (
                                tenant_str, doc_str,
                                control_ref, std_id, checklist_item_id,
                                status, confidence, excerpt,
                                inf_source, proposal_id,
                            ),
                        )
                        finding_id_by_must[checklist_item_id] = cur.fetchone()[0]
                        findings_written += 1

                    # Ship 89'.b — emit cite-mode rows for cite_bindings.
                    # One external_evidence_source per (tenant, must_id,
                    # system_id) — the table's UNIQUE constraint collapses
                    # duplicate cites naturally. Attributed back via
                    # origin_finding_id when the workbook produced a
                    # finding for that MUST; otherwise NULL (cite without
                    # corresponding finding — rare, but legal).
                    for must_id, cite_meta in pp.cite_bindings.items():
                        system_id = _ensure_external_system(
                            cur, tenant_str, cite_meta,
                        )
                        origin_finding = finding_id_by_must.get(must_id)
                        _upsert_cite(
                            cur,
                            tenant_id       = tenant_str,
                            must_id         = must_id,
                            leaf_id         = pp.target_evidence_requirement,
                            system_id       = system_id,
                            cadence_days    = int(
                                cite_meta.get("verification_days") or 365
                            ),
                            origin_finding_id = origin_finding,
                            per_must_note   = (
                                f"workbook cite: sheet {p.sheet!r} "
                                f"column {cite_meta.get('header')!r}"
                            ),
                            hyperlink_url = cite_meta.get("hyperlink_url"),
                        )

        pg.commit()
    except Exception:
        pg.rollback()
        raise

    return run_uuid, findings_written


# ── Ship 89'.b — cite-mode helpers ────────────────────────────────────

def _ensure_external_system(cur, tenant_id: str, cite_meta: dict) -> str:
    """Find-or-create a tenant_external_system row for this cite.

    Maps YAML `cite_kind` to a canonical system_name. Same-name systems
    are reused (idempotent per tenant). Workbook cites typically live in
    an "Internal Documents" system (SharePoint / filesystem / etc.);
    tenant can rename via the profile UI afterward.
    """
    kind = (cite_meta.get("cite_kind") or "internal_document").strip()
    system_name = {
        "internal_document": cite_meta.get("system_hint") or "Internal Documents",
        "url":               cite_meta.get("system_hint") or "External URLs",
        "external_system":   cite_meta.get("system_hint") or "External System",
    }.get(kind, kind)
    cadence = int(cite_meta.get("verification_days") or 365)
    cur.execute(
        """
        SELECT id::text FROM tenant_external_system
         WHERE tenant_id = %s::uuid AND system_name = %s AND is_active = TRUE
         LIMIT 1
        """,
        (tenant_id, system_name),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        """
        INSERT INTO tenant_external_system (
            tenant_id, system_name, default_cadence_days,
            covers_evidence_types, is_active
        ) VALUES (%s::uuid, %s, %s, ARRAY[]::text[], TRUE)
        RETURNING id::text
        """,
        (tenant_id, system_name, cadence),
    )
    return cur.fetchone()[0]


def _upsert_cite(
    cur,
    *,
    tenant_id:         str,
    must_id:           str,
    leaf_id:           str,
    system_id:         str,
    cadence_days:      int,
    origin_finding_id: str | None,
    per_must_note:     str,
    hyperlink_url:     str | None = None,
) -> None:
    """Insert or reactivate an external_evidence_source row for this cite.

    The table's UNIQUE(tenant_id, must_id, system_id) WHERE is_active
    means duplicate workbook cites collapse (e.g. all 149 SoA hyperlinks
    binding item:6.1.3:soa_reference → 1 cite). Existing rows get their
    origin_finding_id + per_must_note refreshed.

    Ship 92'.a.ii — hyperlink_url stored on emission for the auto-verify
    resolver. Multi-URL columns collapse to one cite; this stores the
    first non-mailto URL (deterministic on first-cell-in-column order).
    """
    cur.execute(
        """
        SELECT id::text FROM external_evidence_source
         WHERE tenant_id = %s::uuid
           AND must_id   = %s
           AND system_id = %s::uuid
           AND is_active = TRUE
         LIMIT 1
        """,
        (tenant_id, must_id, system_id),
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            """
            UPDATE external_evidence_source
               SET cadence_days      = %s,
                   per_must_note     = %s,
                   origin_finding_id = COALESCE(%s::uuid, origin_finding_id),
                   hyperlink_url     = COALESCE(%s, hyperlink_url),
                   updated_at        = now()
             WHERE id = %s::uuid
            """,
            (cadence_days, per_must_note, origin_finding_id, hyperlink_url, row[0]),
        )
        return
    cur.execute(
        """
        INSERT INTO external_evidence_source (
            tenant_id, must_id, leaf_id, system_id,
            cadence_days, per_must_note, origin_finding_id, hyperlink_url
        ) VALUES (
            %s::uuid, %s, %s, %s::uuid,
            %s, %s, %s::uuid, %s
        )
        """,
        (tenant_id, must_id, leaf_id, system_id,
         cadence_days, per_must_note, origin_finding_id, hyperlink_url),
    )
