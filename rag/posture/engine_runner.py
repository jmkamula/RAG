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

from rag.posture.applies_when import EvalContext, EvalError
from rag.posture.fulfilment_engine import ControlVerdict, evaluate_control
from rag.posture.leaf_evaluators import GenericLeafEvaluator
from rag.posture.spec_builder import (
    build_spec_descriptor,
    build_spec_resolver,
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
        # spec_resolver is built once per session — its internal memo dedupes
        # repeat lookups when several derived specs share a dependency (e.g.
        # GDPR Art.32 and Art.5.1.f both deriving from ISO A.8.24).
        resolver = build_spec_resolver(s)
        for cid in control_ids:
            try:
                spec = build_spec_descriptor(s, cid)
                if spec is None:
                    continue
                verdicts[cid] = evaluate_control(spec, evaluator, eval_ctx,
                                                 spec_resolver=resolver)
            except Exception as e:
                logger.warning(
                    "engine_runner: evaluating %s failed: %s", cid, e
                )
                # Skip; caller falls back to posture_controls for this one.
                continue

    return verdicts


def evaluate_one_control(
    pg_conn,
    neo4j_driver,
    tenant_id: str,
    control_id: str,
) -> Optional[ControlVerdict]:
    """Evaluate a single control without iterating the full curated set.

    Used by the Stage-2 detail UI to render the derived_from tree for one
    proposal without paying the full compute_engine_verdicts cost. Same
    error-tolerant contract: returns None on any failure rather than
    raising.
    """
    try:
        eval_ctx = _build_eval_context(pg_conn, neo4j_driver, tenant_id)
    except Exception as e:
        logger.warning("evaluate_one_control: building EvalContext failed: %s", e)
        return None

    evaluator = GenericLeafEvaluator(pg_conn, neo4j_driver, tenant_id)
    try:
        with neo4j_driver.session() as s:
            resolver = build_spec_resolver(s)
            spec = build_spec_descriptor(s, control_id)
            if spec is None:
                return None
            return evaluate_control(spec, evaluator, eval_ctx, spec_resolver=resolver)
    except Exception as e:
        logger.warning("evaluate_one_control(%s) failed: %s", control_id, e)
        return None


# ── EvalContext assembly ──────────────────────────────────────────────────────

def _build_eval_context(pg_conn, neo4j_driver, tenant_id: str) -> EvalContext:
    facts = _load_facts(pg_conn, tenant_id)
    er_evidence_types = _load_er_evidence_types(neo4j_driver)
    se = _make_supply_exists_fn(pg_conn, tenant_id, er_evidence_types)
    sc = _make_supply_count_fn(pg_conn, tenant_id, er_evidence_types)
    return EvalContext(
        facts=facts,
        supply_exists_fn=se,
        supply_count_fn=sc,
    )


def _load_er_evidence_types(neo4j_driver) -> dict[str, str | None]:
    """Map every EvidenceRequirement.id to its evidence_type.

    Used by `_resolve_target_to_evidence_type` so that applies_when
    expressions of the form `supply_exists("ER:<leaf_id>")` resolve to the
    leaf's evidence_type before the Postgres lookup. Built once per
    `compute_engine_verdicts` call; today the graph has ~22 leaves so the
    full load is trivial.
    """
    with neo4j_driver.session() as s:
        result = s.run(
            "MATCH (er:EvidenceRequirement) "
            "RETURN er.id AS id, er.evidence_type AS evidence_type"
        )
        return {row["id"]: row["evidence_type"] for row in result}


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


def _make_supply_exists_fn(pg_conn, tenant_id: str, er_evidence_types: dict[str, str | None]):
    """Returns a callable supply_exists(target) -> bool.

    target is either:
      - 'ER:<leaf_id>' (strict prefix per the locked grammar) — resolved to
        the leaf's evidence_type via the pre-loaded EvidenceRequirement map,
        then queried as "any current artifact of that evidence_type
        uploaded?"
      - any other slug — treated as an evidence_type / role tag directly,
        since the commit-1 backfill set edge.role = leaf.evidence_type.

    Phase 2 will sharpen this with proper checklist-coverage semantics; for
    Phase 1 the coarse "any artifact of this type" suffices for applies_when
    gating.
    """
    def fn(target: str) -> bool:
        evidence_type = _resolve_target_to_evidence_type(target, er_evidence_types)
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


def _make_supply_count_fn(pg_conn, tenant_id: str, er_evidence_types: dict[str, str | None]):
    """Returns supply_count(target) -> int. Counts current artifacts."""
    def fn(target: str) -> int:
        evidence_type = _resolve_target_to_evidence_type(target, er_evidence_types)
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


def _resolve_target_to_evidence_type(
    target: str,
    er_evidence_types: dict[str, str | None],
) -> str:
    """Resolve an applies_when target string to a concrete evidence_type.

    Non-ER targets pass through unchanged — the commit-1 backfill set
    edge.role = leaf.evidence_type, so a role tag IS its evidence_type.

    'ER:<leaf_id>' targets look up the leaf in the pre-loaded
    EvidenceRequirement map. An unknown leaf id, or a leaf with no
    evidence_type set, raises EvalError so the calling control fails loudly
    rather than silently evaluating to False — which would invert any
    curator's "narrow on supply" intent.
    """
    if not target.startswith("ER:"):
        return target
    leaf_id = target[3:]
    if leaf_id not in er_evidence_types:
        raise EvalError(
            f"applies_when references unknown leaf id {target!r} — "
            f"no EvidenceRequirement with id {leaf_id!r} in Neo4j"
        )
    evidence_type = er_evidence_types[leaf_id]
    if not evidence_type:
        raise EvalError(
            f"applies_when references leaf {target!r} which has no "
            f"evidence_type set on the EvidenceRequirement node"
        )
    return evidence_type
