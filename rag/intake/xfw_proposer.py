"""
rag/intake/xfw_proposer.py
Stage 4.5 — Cross-framework finding proposer (HITL queue).

For each source finding, walk Neo4j IMPLEMENTS edges to xfw-bridged
standards and mirror the finding into document_findings as a *pending*
proposal (confirmed_by IS NULL, inference_source='xfw_bridge'). The chat
surface lists these for review.

Two trigger modes:
  - Per-upload (propose_for_findings) — called from doc_pipeline after
    Stage 4 writes findings.
  - Backfill   (propose_backfill)     — __main__ entrypoint. Walks all
    extracted findings for a tenant. Used after a tenant enables a new
    framework (NIS2, DORA, etc.) so proposals start landing in the new
    lane without re-uploading every doc.

Idempotence:
  Pending proposals (confirmed_by IS NULL) for the affected scope are
  deleted before insert. Confirmed proposals are preserved.

Scope filter:
  IMPLEMENTS edges target any standard, but proposals are written only
  for target standards listed in tenant_evaluation_scope (direct or
  xfw_inherited). NIS2 proposals start appearing the moment the tenant
  enables NIS2 — re-run backfill to populate against existing docs.
"""
from __future__ import annotations

import argparse
import logging
import os
import uuid
from dataclasses import dataclass, field
from typing import Optional

import psycopg2
from neo4j import GraphDatabase, Driver

from .models import DocumentFinding

logger = logging.getLogger(__name__)


# ── Pipeline-vocabulary → document_findings.status mirror ─────────────────────
# The semantic being mirrored is "this document contributes evidence to the
# linked xfw control" — NOT compliance posture (that lives on posture_controls
# and is propagated separately by rank_and_answer's Layer-2 inheritance).
#
# Therefore we only propose when the source row is 'present' or 'partial' —
# the doc has at least partial content that addresses the source control.
# A 'missing' source row means the doc tried-and-failed to cover that control,
# so it carries no evidence to inherit; we skip it (caller checks
# _SOURCE_STATUSES_TO_PROPAGATE).
_PIPELINE_TO_DF_STATUS: dict[str, str] = {
    "comply":   "present",
    "ofi":      "partial",
    "n/a":      "present",
    "present":  "present",
    "partial":  "partial",
}
_SOURCE_STATUSES_TO_PROPAGATE: set[str] = {"comply", "ofi", "n/a", "present", "partial"}


@dataclass
class ProposalSummary:
    tenant_id:        str
    sources_walked:   int = 0
    edges_seen:       int = 0
    proposals_written: int = 0
    proposals_skipped: int = 0       # source had no IMPLEMENTS edge, or target out of scope
    standards_targeted: set[str] = field(default_factory=set)

    def __str__(self) -> str:
        return (
            f"xfw_proposer[{self.tenant_id[:8]}]: "
            f"sources={self.sources_walked} edges={self.edges_seen} "
            f"written={self.proposals_written} skipped={self.proposals_skipped} "
            f"targets={sorted(self.standards_targeted)}"
        )


# ── Internal helpers ──────────────────────────────────────────────────────────

def _in_scope_standards(conn, tenant_id: str) -> set[str]:
    """
    Return the set of standard_ids in scope for this tenant — either directly
    enrolled or reached via an xfw_inherited bridge. Proposals are filtered to
    these; out-of-scope targets are skipped (a tenant not enrolled in NIS2
    should not accrue NIS2 proposals).
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT standard_id
              FROM tenant_evaluation_scope
             WHERE tenant_id = %s
               AND scope_source IN ('direct', 'xfw_inherited')
            """,
            (tenant_id,),
        )
        return {row[0] for row in cur.fetchall()}


def _walk_implements(driver: Driver, source_id: str) -> list[tuple[str, str, str]]:
    """
    Walk IMPLEMENTS edges from a source control node to xfw'd target controls.
    Edges are bidirectional in Neo4j (both ISO→GDPR and GDPR→ISO exist);
    walking outbound only is sufficient because every ISO→GDPR edge has its
    reverse, so each pair is covered.

    Returns list of (target_node_id, target_standard_id, target_ref).
    """
    cypher = """
    MATCH (a {id: $src_id})-[:IMPLEMENTS]->(b)
    WHERE b.standard_id <> a.standard_id
    RETURN b.id AS tgt_id, b.standard_id AS tgt_std, b.ref AS tgt_ref
    """
    with driver.session() as s:
        return [
            (row["tgt_id"], row["tgt_std"], row["tgt_ref"])
            for row in s.run(cypher, src_id=source_id)
        ]


def _build_source_node_id(standard_id: str, control_ref: str) -> str:
    """Neo4j convention: '{standard_id}:{ref}' e.g. 'ISO27001:2022:A.5.18'."""
    return f"{standard_id}:{control_ref}"


def _clear_pending_proposals(
    conn,
    tenant_id:   str,
    document_id: Optional[str] = None,
) -> int:
    """
    Delete pending xfw_bridge proposals for idempotent re-run.

    Per-upload mode: scope to (tenant, document_id) — only that doc's
    proposals are refreshed.
    Backfill mode (document_id=None): scope to (tenant) — all unconfirmed
    xfw_bridge proposals are cleared and recomputed against the current scope.

    Confirmed proposals (confirmed_by IS NOT NULL) are never deleted.
    """
    with conn.cursor() as cur:
        if document_id is None:
            cur.execute(
                """
                DELETE FROM document_findings
                 WHERE tenant_id        = %s
                   AND inference_source = 'xfw_bridge'
                   AND confirmed_by IS NULL
                """,
                (tenant_id,),
            )
        else:
            cur.execute(
                """
                DELETE FROM document_findings
                 WHERE tenant_id        = %s
                   AND document_id      = %s
                   AND inference_source = 'xfw_bridge'
                   AND confirmed_by IS NULL
                """,
                (tenant_id, document_id),
            )
        return cur.rowcount


def _insert_proposal(
    conn,
    *,
    tenant_id:        str,
    document_id:      str,
    control_ref:      str,
    standard_id:      str,
    status:           str,
    confidence:       str,
    inferred_from_ref: str,
    inferred_from_std: str,
    excerpt:          Optional[str] = None,
) -> bool:
    """Insert one pending xfw proposal. Returns True on success."""
    with conn.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO document_findings (
                    id, tenant_id, document_id,
                    control_ref, standard_id,
                    status, confidence, excerpt,
                    extracted_at, is_active, retention_class,
                    inference_source,
                    inferred_from_control_ref, inferred_from_standard_id
                ) VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    NOW(), TRUE, 'compliance',
                    'xfw_bridge',
                    %s, %s
                )
                """,
                (
                    str(uuid.uuid4()), tenant_id, document_id,
                    control_ref, standard_id,
                    status, confidence, excerpt,
                    inferred_from_ref, inferred_from_std,
                ),
            )
            return True
        except Exception as e:
            logger.warning(
                f"xfw proposal insert failed "
                f"({standard_id}:{control_ref} ← {inferred_from_std}:{inferred_from_ref}): "
                f"{type(e).__name__}: {e}"
            )
            return False


# ── Public API ────────────────────────────────────────────────────────────────

def propose_for_findings(
    tenant_id:    str,
    document_id:  str,
    findings:     list[DocumentFinding],
    conn,
    driver:       Driver,
) -> ProposalSummary:
    """
    Per-upload mode. Called from doc_pipeline after Stage 4 commits findings.
    `findings` is the list just written for this document.

    Caller owns the DB transaction (commit/rollback); this function uses the
    given connection but does not commit on its own.
    """
    summary = ProposalSummary(tenant_id=tenant_id)
    if not findings:
        return summary

    in_scope = _in_scope_standards(conn, tenant_id)
    if not in_scope:
        logger.info(f"xfw_proposer: tenant {tenant_id[:8]} has no in-scope standards")
        return summary

    _clear_pending_proposals(conn, tenant_id, document_id=document_id)

    # Dedup within this run so duplicate source rows don't produce duplicate
    # proposals. Source-level dedup happens on (control_ref, standard_id);
    # proposal-level dedup happens on (document_id, control_ref, standard_id).
    seen_sources:   set[tuple[str, str]] = set()
    seen_proposals: set[tuple[str, str, str]] = set()

    for f in findings:
        if not f.control_ref or not f.standard_id:
            continue
        src_status = (f.finding or "").lower()
        if src_status not in _SOURCE_STATUSES_TO_PROPAGATE:
            continue
        if (f.control_ref, f.standard_id) in seen_sources:
            continue
        seen_sources.add((f.control_ref, f.standard_id))
        summary.sources_walked += 1
        src_id  = _build_source_node_id(f.standard_id, f.control_ref)
        targets = _walk_implements(driver, src_id)
        summary.edges_seen += len(targets)

        for tgt_id, tgt_std, tgt_ref in targets:
            if tgt_std not in in_scope:
                summary.proposals_skipped += 1
                continue
            key = (document_id, tgt_ref, tgt_std)
            if key in seen_proposals:
                continue
            seen_proposals.add(key)
            status = _PIPELINE_TO_DF_STATUS.get(src_status, "partial")
            ok = _insert_proposal(
                conn,
                tenant_id=tenant_id,
                document_id=document_id,
                control_ref=tgt_ref,
                standard_id=tgt_std,
                status=status,
                confidence=(f.confidence or "medium"),
                inferred_from_ref=f.control_ref,
                inferred_from_std=f.standard_id,
                excerpt=(f.evidence_text or "")[:500] or None,
            )
            if ok:
                summary.proposals_written += 1
                summary.standards_targeted.add(tgt_std)
            else:
                summary.proposals_skipped += 1

    logger.info(str(summary))
    return summary


def propose_backfill(
    tenant_id: str,
    db_url:    str,
    driver:    Driver,
) -> ProposalSummary:
    """
    Backfill mode. Reads all confirmed extracted findings from document_findings
    for the tenant and re-runs xfw proposals against the current scope.

    Use after a tenant enables a new framework (NIS2/DORA/etc.) so existing
    docs gain proposals in the new lane.

    Owns its own DB transaction.
    """
    summary = ProposalSummary(tenant_id=tenant_id)
    conn = psycopg2.connect(db_url)
    try:
        with conn.cursor() as cur:
            cur.execute("SET app.tenant_id = %s", (tenant_id,))

        in_scope = _in_scope_standards(conn, tenant_id)
        if not in_scope:
            logger.warning(f"xfw_proposer backfill: tenant {tenant_id[:8]} has no in-scope standards")
            return summary

        _clear_pending_proposals(conn, tenant_id, document_id=None)

        # DISTINCT collapses pre-existing duplicate document_findings rows
        # so each (doc_id, ref, std) source produces at most one walk and
        # one proposal per IMPLEMENTS target. Confidence/excerpt come from
        # an arbitrary representative row — fine for HITL review.
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (document_id, control_ref, standard_id)
                       document_id, control_ref, standard_id, status, confidence, excerpt
                  FROM document_findings
                 WHERE tenant_id       = %s
                   AND is_active       = TRUE
                   AND inference_source = 'extracted'
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()

        seen_proposals: set[tuple[str, str, str]] = set()
        for doc_id, ctrl_ref, std_id, status_db, conf, excerpt in rows:
            src_status = (status_db or "").lower()
            if src_status not in _SOURCE_STATUSES_TO_PROPAGATE:
                continue
            summary.sources_walked += 1
            src_id  = _build_source_node_id(std_id, ctrl_ref)
            targets = _walk_implements(driver, src_id)
            summary.edges_seen += len(targets)

            for tgt_id, tgt_std, tgt_ref in targets:
                if tgt_std not in in_scope:
                    summary.proposals_skipped += 1
                    continue
                key = (doc_id, tgt_ref, tgt_std)
                if key in seen_proposals:
                    continue
                seen_proposals.add(key)
                proposal_status = _PIPELINE_TO_DF_STATUS.get(src_status, "partial")
                ok = _insert_proposal(
                    conn,
                    tenant_id=tenant_id,
                    document_id=doc_id,
                    control_ref=tgt_ref,
                    standard_id=tgt_std,
                    status=proposal_status,
                    confidence=(conf or "medium"),
                    inferred_from_ref=ctrl_ref,
                    inferred_from_std=std_id,
                    excerpt=excerpt,
                )
                if ok:
                    summary.proposals_written += 1
                    summary.standards_targeted.add(tgt_std)
                else:
                    summary.proposals_skipped += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    logger.info(str(summary))
    return summary


# ── CLI entrypoint ────────────────────────────────────────────────────────────

def _main() -> int:
    logging.basicConfig(
        level  = logging.INFO,
        format = "%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Backfill xfw proposals for a tenant after a scope change.",
    )
    parser.add_argument("--tenant", required=True, help="Tenant UUID")
    parser.add_argument(
        "--db-url",
        default=os.environ.get("DATABASE_URL"),
        help="Postgres URL (defaults to $DATABASE_URL)",
    )
    parser.add_argument(
        "--neo4j-uri",
        default=os.environ.get("NEO4J_URI"),
        help="Neo4j bolt URI (defaults to $NEO4J_URI)",
    )
    parser.add_argument(
        "--neo4j-user",
        default=os.environ.get("NEO4J_USER"),
    )
    parser.add_argument(
        "--neo4j-password",
        default=os.environ.get("NEO4J_PASSWORD"),
    )
    args = parser.parse_args()

    if not args.db_url or not args.neo4j_uri:
        print("Set DATABASE_URL and NEO4J_URI (or pass --db-url / --neo4j-uri).")
        return 2

    driver = GraphDatabase.driver(args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password))
    try:
        summary = propose_backfill(args.tenant, args.db_url, driver)
        print(summary)
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
