"""ArionComply — engine runner.

Top-level orchestrator: for one tenant, evaluate every curated FulfilmentSpec
and return a dict of {control_id: ControlVerdict}. Used by posture_loader
to overlay engine verdicts on top of posture_controls for curated controls.

Error-tolerant: any failure (Neo4j down, Postgres timeout, malformed spec)
returns an empty dict — callers fall back to the unmodified posture_controls
values per the layered design.
"""
from __future__ import annotations

import logging
from typing import Optional

from rag.posture.applies_when import EvalContext
from rag.posture.fulfilment_engine import ControlVerdict, evaluate_control
from rag.posture.leaf_evaluators import GenericLeafEvaluator
from rag.posture.spec_builder import (
    build_spec_descriptor,
    list_curated_control_ids,
)

logger = logging.getLogger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def compute_engine_verdicts(
    pg_conn,
    neo4j_driver,
    tenant_id: str,
) -> dict[str, ControlVerdict]:
    """Run the engine for every curated control and return {control_id: verdict}.

    On any unexpected exception, logs a warning and returns the partial
    results so far. Posture_loader uses an empty/partial dict as "leave the
    unaffected controls' posture_controls values alone" — never blocks the
    primary read.
    """
    try:
        control_ids = list_curated_control_ids(neo4j_driver)
    except Exception as e:
        logger.warning("engine_runner: list_curated_control_ids failed: %s", e)
        return {}

    if not control_ids:
        return {}

    try:
        eval_ctx = _build_eval_context(pg_conn, neo4j_driver, tenant_id)
    except Exception as e:
        logger.warning("engine_runner: building EvalContext failed: %s", e)
        return {}

    evaluator = GenericLeafEvaluator(pg_conn, neo4j_driver, tenant_id)
    verdicts: dict[str, ControlVerdict] = {}

    with neo4j_driver.session() as s:
        for cid in control_ids:
            try:
                spec = build_spec_descriptor(s, cid)
                if spec is None:
                    continue
                verdicts[cid] = evaluate_control(spec, evaluator, eval_ctx)
            except Exception as e:
                logger.warning(
                    "engine_runner: evaluating %s failed: %s", cid, e
                )
                # Skip; caller falls back to posture_controls for this one.
                continue

    return verdicts


# ── EvalContext assembly ──────────────────────────────────────────────────────

def _build_eval_context(pg_conn, neo4j_driver, tenant_id: str) -> EvalContext:
    facts = _load_facts(pg_conn, tenant_id)
    se = _make_supply_exists_fn(pg_conn, tenant_id)
    sc = _make_supply_count_fn(pg_conn, tenant_id)
    return EvalContext(
        facts=facts,
        supply_exists_fn=se,
        supply_count_fn=sc,
    )


def _load_facts(pg_conn, tenant_id: str) -> dict[str, object]:
    """Load the tenant's client_facts row as a slug→value dict."""
    with pg_conn.cursor() as cur:
        cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
        cur.execute(
            "SELECT * FROM client_facts WHERE tenant_id = %s AND is_active = TRUE LIMIT 1",
            (tenant_id,),
        )
        row = cur.fetchone()
        if row is None:
            return {}
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))


def _make_supply_exists_fn(pg_conn, tenant_id: str):
    """Returns a callable supply_exists(target) -> bool.

    target is either:
      - 'ER:<leaf_id>' (strict prefix per the locked grammar) — resolved to
        the leaf's evidence_type via Neo4j (single hop), then queried as
        "any current artifact of that evidence_type uploaded?"
      - any other slug — treated as an evidence_type / role tag directly,
        since the commit-1 backfill set edge.role = leaf.evidence_type.

    Phase 2 will sharpen this with proper checklist-coverage semantics; for
    Phase 1 the coarse "any artifact of this type" suffices for applies_when
    gating.
    """
    def fn(target: str) -> bool:
        evidence_type = _resolve_target_to_evidence_type(target)
        if evidence_type is None:
            return False
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT 1 FROM client_documents
                WHERE tenant_id     = %s
                  AND evidence_type = %s
                  AND is_active     = TRUE
                  AND is_current    = TRUE
                LIMIT 1
            """, (tenant_id, evidence_type))
            return cur.fetchone() is not None
    return fn


def _make_supply_count_fn(pg_conn, tenant_id: str):
    """Returns supply_count(target) -> int. Counts current artifacts."""
    def fn(target: str) -> int:
        evidence_type = _resolve_target_to_evidence_type(target)
        if evidence_type is None:
            return 0
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT COUNT(*) FROM client_documents
                WHERE tenant_id     = %s
                  AND evidence_type = %s
                  AND is_active     = TRUE
                  AND is_current    = TRUE
            """, (tenant_id, evidence_type))
            row = cur.fetchone()
            return int(row[0]) if row else 0
    return fn


def _resolve_target_to_evidence_type(target: str) -> Optional[str]:
    """For Phase 1 the target string IS the evidence_type/role; the
    commit-1 backfill set edge.role = leaf.evidence_type so they match.
    The 'ER:' prefix path is reserved for when curators want to point at a
    specific leaf id — we strip the prefix and call it a leaf id, but
    leaf-id-based supply lookups are Phase 2 work (need the matcher's
    checklist-coverage layer). For now, return the string as-is for the
    role/type path, and the prefix-stripped portion for ER: ids (caller
    sees `False`/`0` either way if no artifact of that type exists, which
    is the conservative answer)."""
    if target.startswith("ER:"):
        # Phase 1: we'd need a Neo4j hop to resolve leaf id → evidence_type.
        # Cheap enough but only valuable once curators write ER:-prefixed
        # applies_when expressions, which none do today. Return None for
        # now — caller treats it as "no supply", which keeps any such gate
        # safely closed until we wire the resolution.
        return None
    return target
