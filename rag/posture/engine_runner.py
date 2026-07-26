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
    # Ship 44'.d — OTel span. This is a heavy call (touches all curated
    # controls × their MUSTs); worth tracing for latency debugging.
    from rag.telemetry import get_tracer
    _tracer = get_tracer(__name__)
    _span_cm = _tracer.start_as_current_span("arion.engine.compute_verdicts")
    _span = _span_cm.__enter__()
    try:
        try:
            _span.set_attribute("arion.tenant_id", str(tenant_id)[:64])
        except Exception:
            pass
    except Exception:
        _span = None

    import time as _time
    _t0 = _time.time()

    try:
        control_ids = list_curated_control_ids(neo4j_driver)
    except Exception as e:
        logger.warning("engine_runner: list_curated_control_ids failed: %s", e)
        if _span is not None:
            try:
                from opentelemetry import trace as _t
                _span.set_status(_t.Status(_t.StatusCode.ERROR, "list_curated_control_ids failed"))
            except Exception:
                pass
            try: _span_cm.__exit__(None, None, None)
            except Exception: pass
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

    if _span is not None:
        try:
            _span.set_attribute("arion.engine.n_controls_evaluated",
                                len(control_ids))
            _span.set_attribute("arion.engine.n_verdicts_emitted",
                                len(verdicts))
            _span.set_attribute("arion.engine.latency_ms",
                                int((_time.time() - _t0) * 1000))
        except Exception:
            pass
        try: _span_cm.__exit__(None, None, None)
        except Exception: pass

    return verdicts


def evaluate_one_control(
    pg_conn,
    neo4j_driver,
    tenant_id: str,
    control_id: str,
    *,
    pre_built_ctx: Optional[EvalContext] = None,
    shared_session = None,
    shared_resolver = None,
) -> Optional[ControlVerdict]:
    """Evaluate a single control without iterating the full curated set.

    Used by the Stage-2 detail UI to render the derived_from tree for one
    proposal without paying the full compute_engine_verdicts cost. Same
    error-tolerant contract: returns None on any failure rather than
    raising.

    Ship 45'.c — batch callers (e.g. build_advisory_data_for_refs) can
    pass pre-built shared context to avoid the per-call
    `_build_eval_context` + `build_spec_resolver` + fresh Neo4j session
    overhead. Legacy callers that omit these args see identical
    behavior.
    """
    try:
        eval_ctx = pre_built_ctx or _build_eval_context(pg_conn, neo4j_driver, tenant_id)
    except Exception as e:
        logger.warning("evaluate_one_control: building EvalContext failed: %s", e)
        return None

    evaluator = GenericLeafEvaluator(pg_conn, neo4j_driver, tenant_id)
    try:
        if shared_session is not None and shared_resolver is not None:
            spec = build_spec_descriptor(shared_session, control_id)
            if spec is None:
                return None
            return evaluate_control(spec, evaluator, eval_ctx,
                                    spec_resolver=shared_resolver)

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
    # Ship 45'.c — micro-cache `_load_er_evidence_types` because the
    # Neo4j scan of all EvidenceRequirement nodes is invariant across
    # tenants + across a single chat turn's many evaluate_one_control
    # calls. TTL 30s protects against catalog reloads without paying
    # the ~50ms Neo4j scan on every ref.
    er_evidence_types = _cached_er_evidence_types(neo4j_driver)
    facts = _load_facts(pg_conn, tenant_id)
    se = _make_supply_exists_fn(pg_conn, tenant_id, er_evidence_types)
    sc = _make_supply_count_fn(pg_conn, tenant_id, er_evidence_types)
    return EvalContext(
        facts=facts,
        supply_exists_fn=se,
        supply_count_fn=sc,
    )


_ER_TYPES_CACHE: dict[str, tuple[float, dict]] = {}
_ER_TYPES_TTL_S = 30.0

def _cached_er_evidence_types(neo4j_driver) -> dict:
    """TTL cache wrapping _load_er_evidence_types. Driver id used as
    cache key; catalog is invariant across tenants."""
    import time as _t
    key = str(id(neo4j_driver))
    hit = _ER_TYPES_CACHE.get(key)
    if hit is not None:
        ts, val = hit
        if (_t.monotonic() - ts) < _ER_TYPES_TTL_S:
            return val
    val = _load_er_evidence_types(neo4j_driver)
    _ER_TYPES_CACHE[key] = (_t.monotonic(), val)
    return val


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
