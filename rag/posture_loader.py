"""
ArionComply — Posture Loader

Reads tenant posture from Postgres posture_controls table.
Replaces the ARION_POSTURE hardcode in chat.py.

Returns the same dict format the pipeline expects:
  {
    "ISO27001:2022:A.5.18": {
      "finding":         "NC",
      "gap_description": "Access register records from Q4 2024 incomplete",
      "action_required": "Complete and sign off Q4 2024 access register",
      "source":          "assessor",
      "source_authority":"Arion Networks Internal Audit (AUD001, April 2025)",
      "platform_ref":    "PC-ARN-0105",
      "external_ref":    "F001/F005",
      "confidence":      "high",
    },
    ...
  }

Also loads ClientFacts from Postgres client_facts table,
replacing the ARION_FACTS hardcode.

Usage:
  from rag.posture_loader import load_posture, load_client_facts

  posture = load_posture(pg_conn, tenant_id)
  facts   = load_client_facts(pg_conn, tenant_id)
"""
from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)


def _truncate_at_word(text: str, max_len: int) -> str:
    """Return text truncated at the last word boundary within `max_len`,
    with a trailing ellipsis when truncation happened. Used for
    gap_description compaction so we don't cut mid-word (e.g.
    'attaches to a…' → 'attaches to…')."""
    if not text or len(text) <= max_len:
        return text or ""
    # Prefer the last whitespace before max_len. If that lands too far
    # back (below 70% of the window), the token itself is long — hard
    # cut is unavoidable but stays readable.
    cutoff = text.rfind(" ", 0, max_len)
    if cutoff < int(max_len * 0.7):
        cutoff = max_len
    return text[:cutoff].rstrip(" ,.;:—-") + "…"


def load_posture(pg_conn, tenant_id: str) -> dict:
    """
    Load all assessed posture controls for a tenant from Postgres.

    Returns dict keyed by node_id (e.g. "ISO27001:2022:A.5.18"):
      {finding, gap_description, action_required, source,
       source_authority, platform_ref, external_ref, confidence,
       remediation_status, soa_notes, engine_gap_list?, engine_reason?,
       engine_overridden?}

    Only returns rows where finding is not 'Not assessed' —
    unassessed controls have no posture data to provide.

    N/A controls ARE included (source='workbook', finding='N/A')
    so the pipeline can correctly exclude them from obligation checks.

    Posture engine overlay (commit 4):
      After loading posture_controls, the fulfilment engine is consulted
      for every curated FulfilmentSpec. For *multi-leaf* specs only
      (composition adds new info), the engine verdict overrides the
      posture_controls finding and the gap_list is attached to the row.
      Single-leaf specs are skipped — they don't tell us anything
      posture_controls doesn't already know. Engine failure is silent
      fallback to posture_controls per the layered design.
    """
    # Ship 44'.d — OTel span. load_posture is called on every chat
    # turn AND every dashboard request; tracing helps see where time
    # goes when it's slow.
    from rag.telemetry import get_tracer
    _tracer = get_tracer(__name__)
    _span_cm = _tracer.start_as_current_span("arion.posture.load")
    _span = _span_cm.__enter__()
    try:
        _span.set_attribute("arion.tenant_id", str(tenant_id)[:64])
    except Exception:
        pass
    import time as _time
    _t0 = _time.time()

    try:
        with pg_conn.cursor() as cur:
            # Set tenant context for RLS enforcement
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    COALESCE(node_id, standard_id || ':' || control_ref) AS node_id,
                    control_ref,
                    standard_id,
                    finding,
                    confidence,
                    gap_description,
                    action_required,
                    source,
                    source_authority,
                    platform_ref,
                    external_ref,
                    soa_notes,
                    remediation_status,
                    linked_policies,
                    last_updated,
                    engine_proposal_status,
                    confirmation_status,
                    applicability_status
                FROM posture_controls
                WHERE tenant_id = %s
                  AND finding != 'Not assessed'
                  AND control_ref IS NOT NULL
                ORDER BY
                    CASE finding
                        WHEN 'NC'     THEN 1
                        WHEN 'OFI'    THEN 2
                        WHEN 'Comply' THEN 3
                        WHEN 'N/A'    THEN 4
                        ELSE 5
                    END,
                    control_ref
            """, (tenant_id,))

            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

    except Exception as e:
        logger.error(f"load_posture failed for {tenant_id}: {e}")
        if _span is not None:
            try:
                from opentelemetry import trace as _t
                _span.set_status(_t.Status(_t.StatusCode.ERROR, "load_posture failed"))
            except Exception:
                pass
            try: _span_cm.__exit__(None, None, None)
            except Exception: pass
        return {}

    posture = {}
    for row in rows:
        rec = dict(zip(cols, row))
        nid = rec.pop("node_id")
        if nid:
            posture[nid] = rec

    # Fulfilment-engine overlay: override multi-leaf curated verdicts.
    engine_overrides = _apply_engine_overlay(posture, tenant_id, pg_conn)

    # DEMONSTRATES overlay (framework role model, Phase 2b+2c, 2026-07-05):
    # For every OBLIGATION control (GDPR articles, etc.), look up which
    # PROGRAM/EXTENSION controls demonstrate it via DEMONSTRATES edges
    # in Neo4j, aggregate the sources' current findings, and attach
    # `demonstrated_by` + `propagated_finding` as metadata.
    #
    # Phase 2b: attach metadata; don't touch top-level `finding` for
    # obligations the tenant has already assessed. Their assessment
    # stands; the metadata surfaces the demonstration story.
    # Phase 2c: for obligations that are 'Not assessed' (or have no
    # posture_controls row), MATERIALISE a posture entry with
    # `finding` = the propagated aggregate. Fills gaps only — never
    # overrides an existing assessment.
    demonstrates_overlays, materialised = _apply_demonstrates_overlay(
        posture, tenant_id, pg_conn,
    )

    # S3e: cascade overlay — controls with overdue triggered_implications
    # get pending engine PAs (Stage-2 review queue). Best-effort: failure
    # here does not corrupt the live posture.
    cascade_proposals = 0
    try:
        from rag.cascade.posture_overlay import (
            compute_cascade_pressure, propose_from_cascade,
        )
        pressure = compute_cascade_pressure(pg_conn, tenant_id)
        if pressure:
            live = {nid: rec["finding"] for nid, rec in posture.items()}
            cascade_proposals = propose_from_cascade(
                pg_conn, tenant_id, pressure, live,
            )
            if cascade_proposals:
                pg_conn.commit()
    except Exception as ex:
        logger.warning("cascade posture overlay skipped: %s", ex)

    logger.info(
        f"load_posture: {len(posture)} controls loaded for {tenant_id} "
        f"({sum(1 for r in posture.values() if r['finding']=='NC')} NC, "
        f"{sum(1 for r in posture.values() if r['finding']=='OFI')} OFI, "
        f"{sum(1 for r in posture.values() if r['finding']=='Comply')} Comply, "
        f"{sum(1 for r in posture.values() if r['finding']=='N/A')} N/A; "
        f"engine_overrides={engine_overrides}; "
        f"cascade_proposals={cascade_proposals}; "
        f"demonstrates_overlays={demonstrates_overlays}; "
        f"demonstrates_materialised={materialised})"
    )

    if _span is not None:
        try:
            _span.set_attribute("arion.posture.n_controls", len(posture))
            _span.set_attribute("arion.posture.n_nc",
                                sum(1 for r in posture.values() if r['finding']=='NC'))
            _span.set_attribute("arion.posture.n_ofi",
                                sum(1 for r in posture.values() if r['finding']=='OFI'))
            _span.set_attribute("arion.posture.n_comply",
                                sum(1 for r in posture.values() if r['finding']=='Comply'))
            _span.set_attribute("arion.posture.n_na",
                                sum(1 for r in posture.values() if r['finding']=='N/A'))
            _span.set_attribute("arion.posture.engine_overrides", int(engine_overrides))
            _span.set_attribute("arion.posture.demonstrates_overlays",
                                int(demonstrates_overlays))
            _span.set_attribute("arion.posture.demonstrates_materialised",
                                int(materialised))
            _span.set_attribute("arion.posture.cascade_proposals",
                                int(cascade_proposals))
            _span.set_attribute("arion.posture.latency_ms",
                                int((_time.time() - _t0) * 1000))
        except Exception:
            pass
        try: _span_cm.__exit__(None, None, None)
        except Exception: pass

    return posture


def _apply_engine_overlay(posture: dict, tenant_id: str, pg_conn) -> int:
    """Run the fulfilment engine and apply multi-leaf verdicts on top of
    posture_controls values. Returns the number of overrides applied.

    Silent fallback: any exception (Neo4j unavailable, etc.) returns 0;
    the posture dict is unchanged. The engine is an overlay, not a hard
    dependency.
    """
    try:
        from rag.posture.engine_runner import compute_engine_verdicts
        from rag.posture.gap_writer import (
            upsert_evidence_gaps,
            get_acknowledged_leaves,
        )

        neo4j_driver = _build_engine_neo4j_driver()
        if neo4j_driver is None:
            return 0
        try:
            verdicts = compute_engine_verdicts(pg_conn, neo4j_driver, tenant_id)
        finally:
            try:
                neo4j_driver.close()
            except Exception:
                pass

        # Persist gaps before overlaying. Acknowledgements written by the
        # chat surface live on these rows; we need them in sync with the
        # engine's current view *before* we read which ones are acknowledged.
        if verdicts:
            try:
                stats = upsert_evidence_gaps(pg_conn, tenant_id, verdicts)
                logger.info(
                    "tenant_evidence_gaps: opened=%d updated=%d resolved=%d",
                    stats.opened, stats.updated, stats.resolved,
                )
            except Exception as e:
                logger.warning("gap upsert skipped: %s", e)

            # Persist engine verdicts as Stage-2 proposals on posture_controls
            # (commit 4 of the HITL rollout). Idempotent: only writes when the
            # verdict text or reason has changed since the last proposal. The
            # in-memory overlay below still applies; commit 5 will gate the
            # overlay on engine_proposal_status='approved'.
            try:
                proposed = _persist_engine_proposals(pg_conn, tenant_id, verdicts)
                if proposed:
                    logger.info(
                        "engine_proposals: wrote/refreshed %d row(s)", proposed,
                    )
            except Exception as e:
                logger.warning("engine proposal persist skipped: %s", e)

            # Persist per-MUST verdicts (schema_v94, 2026-08-10). Single
            # source of truth for consumers (template renderer, SPA leaf
            # detail, chat) — reads posture_must_verdicts instead of each
            # re-running the engine. Best-effort: any failure logged +
            # swallowed, never blocks the primary read.
            try:
                n_must_verdicts = _persist_must_verdicts(pg_conn, tenant_id, verdicts)
                if n_must_verdicts:
                    logger.info(
                        "posture_must_verdicts: wrote %d rows", n_must_verdicts,
                    )
            except Exception as e:
                logger.warning("must-verdict persist skipped: %s", e)

        overrides = 0
        for cid, verdict in verdicts.items():
            # Skip non-determinative postures; everything else (single-leaf
            # included) is eligible for overlay per Path A — see
            # _persist_engine_proposals for the rationale on removing the
            # leaves<=1 gate.
            if verdict.posture in ("UNKNOWN", "deferred", "NotApplicable"):
                continue
            row = posture.get(cid)
            if row is None:
                # Engine has a verdict but tenant has no posture_controls
                # row for it. Don't manufacture one — posture_controls is
                # still the authoritative inventory; this would be visible
                # in a later iteration when we have a richer view.
                continue

            # Ship 66'.b (2026-08-12) — N/A dominance guard.
            # Tenant's scoping decision (applicability='na') is
            # authoritative over any engine verdict. The engine can only
            # answer "how well is my evidence?"; on an out-of-scope
            # control there is no evidence question to ask.
            # Codified rule: [[feedback-engine-should-not-clobber-tenant-na]]
            # + Ship 66'.a schema split. This is the enforcement point
            # for the read path; Ship 66'.d closes the write path.
            # Ship 76'.b — migrate to shared SSoT predicate.
            from rag.posture.scope import row_in_scope
            if not row_in_scope(row):
                continue

            # Two paths trigger the in-memory overlay:
            #   (a) HITL Stage-2 gate: engine_proposal_status='approved' —
            #       Stage-2 user accepted the engine's proposed verdict
            #       (e.g. Comply→NC promotion). 'proposed' / 'rejected' /
            #       'none' otherwise keep the live posture_controls finding
            #       untouched; the persisted proposal (commit 4) still
            #       records the engine's view for the Stage-2 chat surface.
            #   (b) Engine agrees with live at NC/OFI: no Stage-2 proposal
            #       exists (suppression), but the engine's structured
            #       4-leaf reasoning is strictly more informative than the
            #       legacy PC.gap_description prose. Overlay the engine
            #       reason / gap_list so chat surfaces the auditor-grade
            #       detail. Comply==Comply still skipped — engine adds
            #       nothing. See [[engine_agreement_suppression]].
            status        = row.get("engine_proposal_status")
            agrees_on_gap = (
                verdict.posture in ("NC", "OFI")
                and row.get("finding") == verdict.posture
            )
            if status != "approved" and not agrees_on_gap:
                continue

            # Suppress acknowledged leaves from the headline. Verdict stays
            # OFI/NC (HITL: client owns posture; ack ≠ Comply) but the
            # gap_description and engine_gap_list reflect only unacknowledged
            # gaps. The full audit trail is queryable via tenant_evidence_gaps
            # directly. If a control has *all* its failing leaves acknowledged,
            # we still keep the OFI posture per the model (B in the design call).
            try:
                acked = get_acknowledged_leaves(pg_conn, tenant_id, cid)
            except Exception:
                acked = {}

            unacked_leaves = [l for l in verdict.leaves if l.leaf_id not in acked]
            acked_count = len(acked)

            row["finding"]               = verdict.posture
            row["engine_reason"]         = verdict.reason
            row["engine_overridden"]     = True
            row["engine_acked_count"]    = acked_count
            row["engine_acked_leaves"]   = sorted(acked.keys())
            row["engine_gap_list"]       = _rebuild_gap_list(unacked_leaves)

            # When the engine flips Comply→OFI/NC, the stored gap_description
            # is stale (it's the original evidence summary from the curated
            # upload). Replace it with a short auditor-facing gap line built
            # from the engine's reason + unacked gap detail so the LLM
            # presents the actual missing artifacts, not the policy summary.
            #
            # Partition unacked leaves into:
            #   fully_empty — leaf has zero items_recognised; pure miss
            #   partial     — leaf has some items_recognised but not all;
            #                 surfaces the workbook/extraction contribution
            #                 alongside the residual gap so the user sees
            #                 N/M MUSTs covered + the first specific miss
            if verdict.posture in ("OFI", "NC"):
                fully_empty: list = []
                partial: list = []
                for l in unacked_leaves:
                    if l.satisfied or not l.role:
                        continue
                    if l.items_recognised:
                        partial.append(l)
                    else:
                        fully_empty.append(l)

                ack_suffix = (
                    f" ({acked_count} acknowledged)" if acked_count else ""
                )

                parts = [f"{verdict.reason}{ack_suffix}"]

                if fully_empty:
                    missing_roles = sorted({l.role for l in fully_empty})
                    parts.append(
                        "missing artifacts of type: " + ", ".join(missing_roles)
                    )

                if partial:
                    # Lazy import — arion_graph carries the canonical
                    # snake_case → pretty label map. Prettify at compose
                    # time so ALL downstream read paths see human-
                    # readable roles.
                    try:
                        from rag.arion_graph import _pretty_role
                    except Exception:
                        def _pretty_role(r: str) -> str:
                            return r.replace("_", " ")

                    # Emit partial bits as newline-separated bullets so
                    # the LLM's final synthesis renders each leaf on
                    # its own line. Previously we concatenated with
                    # ", " which the LLM followed → wall-of-text prose
                    # that was hard to scan. Downstream truncators
                    # that limit gap_description to N chars still work
                    # (they cut at char N regardless of newline
                    # placement); rendering surfaces that preserve
                    # newlines (chat, drill-in) get the bullets.
                    partial_lines = []
                    for l in sorted(partial, key=lambda x: x.role):
                        sat = len(l.items_recognised)
                        total = sat + len(l.items_unrecognised)
                        first_miss = l.items_unrecognised[0] if l.items_unrecognised else ""
                        first_miss_short = _truncate_at_word(first_miss, 120)
                        line = f"  - {_pretty_role(l.role)}: {sat}/{total}"
                        if first_miss_short:
                            line += f" — needs {first_miss_short}"
                        partial_lines.append(line)
                    parts.append("Partial evidence:\n" + "\n".join(partial_lines))

                # Also prettify the "missing artifacts of type" list —
                # same snake_case → human treatment.
                if fully_empty:
                    try:
                        from rag.arion_graph import _pretty_role as _pr
                    except Exception:
                        def _pr(r: str) -> str:
                            return r.replace("_", " ")
                    # Replace the raw-role entry we appended earlier
                    for i, p in enumerate(parts):
                        if p.startswith("missing artifacts of type: "):
                            roles = p[len("missing artifacts of type: "):]
                            pretty = ", ".join(_pr(r.strip())
                                               for r in roles.split(",") if r.strip())
                            parts[i] = "still needed: " + pretty
                            break

                if len(parts) > 1 or verdict.reason:
                    row["gap_description"] = "; ".join(parts)
            overrides += 1
        return overrides

    except Exception as e:
        logger.warning("posture engine overlay skipped (%s: %s)", type(e).__name__, e)
        return 0


# ── Framework role model overlays (Phase 2b, 2026-07-05) ─────────────

# Rank of finding strengths, lowest = strongest. Used when aggregating
# multiple PROGRAM/EXTENSION demonstrators pointing at the same
# OBLIGATION control.
_FINDING_STRENGTH = {"Comply": 0, "OFI": 1, "NC": 2, "N/A": 3}


def _fetch_demonstrates_map() -> dict[str, list[dict]]:
    """Load the DEMONSTRATES edge map from Neo4j, keyed by target
    (obligation) node id. Returns {} on any failure — this is an
    overlay, not a hard dependency.

    Shape:
      {
        "GDPR:2016/679:Art.28": [
          {"src_id": "ISO27001:2022:A.5.19", "src_std": "ISO27001:2022",
           "via_edge": "IMPLEMENTS", "rationale": "...", "strength": "high"},
          {"src_id": "ISO27701:2019:B.8.5.6", ...},
        ],
        ...
      }
    """
    try:
        driver = _build_engine_neo4j_driver()
        if driver is None:
            return {}
        try:
            with driver.session() as s:
                out: dict[str, list[dict]] = {}
                for r in s.run(
                    """
                    MATCH (src:RequirementNode)-[d:DEMONSTRATES]->(tgt:RequirementNode)
                    RETURN
                      tgt.id          AS tgt_id,
                      src.id          AS src_id,
                      src.standard_id AS src_std,
                      d.via_edge      AS via_edge,
                      d.rationale     AS rationale,
                      d.strength      AS strength
                    """
                ):
                    out.setdefault(r["tgt_id"], []).append({
                        "src_id":    r["src_id"],
                        "src_std":   r["src_std"],
                        "via_edge":  r["via_edge"],
                        "rationale": r["rationale"],
                        "strength":  r["strength"],
                    })
                return out
        finally:
            try:
                driver.close()
            except Exception:
                pass
    except Exception as e:
        logger.warning("_fetch_demonstrates_map failed: %s", e)
        return {}


def _fetch_not_assessed_obligation_rows(
    pg_conn, tenant_id: str, target_ids: set[str],
) -> dict[str, dict]:
    """Fetch posture_controls rows with finding='Not assessed' for the
    given obligation node_ids. Load-time filter excludes these from
    the main posture dict; Phase 2c needs them so DEMONSTRATES can
    materialise a propagated finding.

    Silent failure returns {} — Phase 2c is an overlay, not a hard
    dependency.
    """
    if not target_ids:
        return {}
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute(
                """
                SELECT
                    COALESCE(node_id, standard_id||':'||control_ref) AS node_id,
                    control_ref, standard_id, finding, confidence,
                    gap_description, action_required, source, source_authority,
                    platform_ref, external_ref, soa_notes, remediation_status,
                    linked_policies, last_updated, engine_proposal_status,
                    confirmation_status
                FROM posture_controls
                WHERE tenant_id = %s
                  AND finding = 'Not assessed'
                  AND control_ref IS NOT NULL
                  AND COALESCE(node_id, standard_id||':'||control_ref) = ANY(%s)
                """,
                (tenant_id, list(target_ids)),
            )
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        out: dict[str, dict] = {}
        for row in rows:
            rec = dict(zip(cols, row))
            nid = rec.pop("node_id")
            if nid:
                out[nid] = rec
        return out
    except Exception as e:
        logger.warning("_fetch_not_assessed_obligation_rows failed: %s", e)
        return {}


def _apply_demonstrates_overlay(
    posture: dict, tenant_id: str, pg_conn,
) -> tuple[int, int]:
    """Attach demonstrated_by + propagated_finding to obligation posture
    records, and materialise Not-assessed obligation rows where
    demonstration exists.

    Aggregation rule for `propagated_finding`:
      - If every contributing source is Comply  → 'Comply'
      - Else if any source is Comply or OFI     → 'OFI'  (partial)
      - Else (all sources NC / N/A / missing)   → not set

    Behaviour by target state:
      - target has finding != 'Not assessed' → attach demonstrated_by +
        propagated_finding as METADATA; DO NOT touch `finding`
        (tenant's assessment stands). Phase 2b behavior.
      - target has finding == 'Not assessed' (not in main posture
        dict because SQL filters them out) → fetch the row from DB,
        materialise into posture, and set `finding` = propagated_finding
        with source='demonstrates_propagation'. Phase 2c behavior.
      - target has no posture_controls row at all → skipped (we do not
        invent postures from thin air).

    Returns (overlays, materialised).
    """
    demo_map = _fetch_demonstrates_map()
    if not demo_map:
        return (0, 0)

    # Phase 2c: fetch Not-assessed obligation rows for the DEMONSTRATES
    # target set. These are candidates for finding materialisation.
    not_assessed = _fetch_not_assessed_obligation_rows(
        pg_conn, tenant_id, set(demo_map.keys()) - set(posture.keys()),
    )

    overlays = 0
    materialised = 0
    for tgt_id, sources in demo_map.items():
        tgt_rec = posture.get(tgt_id)
        materialising = False
        if tgt_rec is None:
            tgt_rec = not_assessed.get(tgt_id)
            if tgt_rec is None:
                continue
            materialising = True

        contributing: list[dict] = []
        for src in sources:
            src_rec = posture.get(src["src_id"])
            if src_rec is None:
                continue
            src_finding = src_rec.get("finding")
            if src_finding not in _FINDING_STRENGTH:
                continue
            contributing.append({
                "src_id":   src["src_id"],
                "src_std":  src["src_std"],
                "via_edge": src["via_edge"],
                "finding":  src_finding,
                "strength": src.get("strength"),
            })

        if not contributing:
            # No demonstration to base propagation on. If we pulled this
            # row for materialisation, drop it — Not-assessed with no
            # positive demonstration stays out of posture, same as
            # before Phase 2c.
            continue

        tgt_rec["demonstrated_by"] = contributing
        findings = {c["finding"] for c in contributing}
        propagated: str | None = None
        if findings and findings <= {"Comply"}:
            propagated = "Comply"
        elif findings & {"Comply", "OFI"}:
            propagated = "OFI"

        if propagated:
            tgt_rec["propagated_finding"] = propagated

        if materialising:
            # Only materialise if we have a positive propagation.
            # Otherwise Not-assessed stays Not-assessed (unchanged).
            if not propagated:
                continue
            tgt_rec["finding"]          = propagated
            tgt_rec["source"]           = "demonstrates_propagation"
            tgt_rec["gap_description"]  = (
                f"Propagated from {len(contributing)} demonstrator(s) "
                f"across PROGRAM/EXTENSION postures. See demonstrated_by."
            )
            tgt_rec["remediation_status"] = None
            posture[tgt_id] = tgt_rec
            materialised += 1

        overlays += 1

    return (overlays, materialised)


def kick_posture_refresh(tenant_id: str, reason: str = "") -> None:
    """Best-effort posture refresh for use at write endpoints.

    Ship 58'.s (2026-08-10) — mutations at write endpoints (cite verify,
    Stage-2 approve/reject, external system delete) change what the
    engine computes for per-MUST recognition, but only load_posture()
    writes the refreshed truth into posture_must_verdicts. Every such
    endpoint should call this after its commit so the SSoT table stays
    fresh.

    Opens a fresh connection to avoid entangling with the caller's
    transaction (mirrors the doc_pipeline Stage 4.7 pattern). Best-effort:
    any failure is logged and swallowed — never blocks the user's write.
    A later sweep or user action will resync if this fails.
    """
    import os
    try:
        import psycopg2
        db_url = os.getenv("POSTGRES_URL",
                           "postgresql://arioncomply@127.0.0.1/arioncomply_compliance")
        _eng_conn = psycopg2.connect(db_url)
        try:
            with _eng_conn.cursor() as _cur:
                _cur.execute(
                    "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
                )
            load_posture(_eng_conn, tenant_id)
        finally:
            _eng_conn.close()
        logger.info(
            "kick_posture_refresh: tenant=%s reason=%s ok",
            str(tenant_id)[:8], reason,
        )
    except Exception as e:
        logger.warning(
            "kick_posture_refresh: tenant=%s reason=%s failed — %s: %s",
            str(tenant_id)[:8], reason, type(e).__name__, e,
        )


def _persist_must_verdicts(pg_conn, tenant_id: str, verdicts: dict) -> int:
    """Write per-MUST engine verdicts to posture_must_verdicts (schema_v94).

    Iterates each ControlVerdict's leaves and emits one row per MUST id
    in the leaf's item_ids_{recognised, unrecognised, partial, stale}
    arrays. Upsert by (tenant_id, must_id). Returns rows written.

    Facets:
      satisfied = must_id in item_ids_recognised (present-status finding
                  OR fresh cite covers it; also N/A-excluded MUSTs are
                  NOT emitted at all — see rationale below)
      stale     = must_id in item_ids_stale (has evidence but past
                  freshness_days)
      partial   = must_id in item_ids_partial (partial-status finding,
                  no present)

    N/A-excluded MUSTs: dropped from the leaf's must_item_ids inside
    GenericLeafEvaluator._fetch_na_must_ids BEFORE the recognition scan,
    so they never appear in any of the four arrays. Consumers reading
    posture_must_verdicts see absence-of-row for N/A MUSTs, which is
    the correct signal (the tenant has scoped them out).

    Best-effort: writes are wrapped in a transaction. Any failure rolls
    back this table's writes but does not affect posture_controls or
    posture_assertions writes that happen earlier in the flow.
    """
    if not verdicts:
        return 0

    # Ship 66'.b — N/A dominance. Fetch the set of control node_ids that
    # the tenant declared out of scope (applicability='na'); skip these
    # from SSoT persistence entirely. Consumers reading
    # posture_must_verdicts see absence-of-row for out-of-scope
    # controls, matching the existing "absence-of-row as valid N/A"
    # discipline (Ship 58 codified lesson).
    na_node_ids: set[str] = set()
    try:
        with pg_conn.cursor() as _cur_na:
            _cur_na.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            _cur_na.execute("""
                SELECT COALESCE(node_id, standard_id || ':' || control_ref)
                  FROM posture_controls
                 WHERE tenant_id = %s::uuid
                   AND applicability_status = 'na'
            """, (tenant_id,))
            na_node_ids = {r[0] for r in _cur_na.fetchall()}
    except Exception as e:
        # Fallback: proceed with the full set. The overlay's guard
        # (Ship 66'.b earlier in this file) still protects the primary
        # posture dict; SSoT rows for N/A controls will silently
        # accumulate but readers via read_must_verdicts_by_control get
        # tenant-consistent data via posture_controls.finding.
        logger.warning("_persist_must_verdicts: N/A filter fetch failed: %s", e)

    # A small number of MUST ids are shared across multiple leaves (e.g.
    # Ship 12'.a's item:A.5.18:rev_identity_pair which pairs identity +
    # authentication lifecycles). When one MUST surfaces from two
    # LeafVerdict arrays with divergent statuses we take the "best"
    # verdict per MUST — the evidence itself is shared, so the more
    # positive category is the honest reading. Rank:
    #   recognised (non-stale) > recognised (stale) > partial > unrecognised
    _rank = {"recognised": 3, "stale": 2, "partial": 1, "unrecognised": 0}

    def _framework_role(standard_id: str) -> str:
        """Ship 59'.b — denormalize the P/E/O role for fast filtering."""
        if standard_id == "ISO27001:2022": return "PROGRAM"
        if standard_id == "ISO27701:2019": return "EXTENSION"
        if standard_id == "GDPR:2016/679": return "OBLIGATION"
        return "OTHER"

    best: dict[str, tuple[str, str, str, bool, bool, bool, str]] = {}
    for cid, verdict in verdicts.items():
        # Ship 66'.b — N/A dominance. Skip out-of-scope controls.
        if cid in na_node_ids:
            continue
        parts = cid.rsplit(":", 1)
        if len(parts) != 2:
            continue
        standard_id, control_ref = parts[0], parts[1]
        role = _framework_role(standard_id)

        for lv in verdict.leaves:
            rec_ids     = set(lv.item_ids_recognised or ())
            partial_ids = set(lv.item_ids_partial or ())
            unrec_ids   = set(lv.item_ids_unrecognised or ())
            stale_ids   = set(lv.item_ids_stale or ())

            for mid in rec_ids:
                cat = "stale" if mid in stale_ids else "recognised"
                row = (control_ref, standard_id, role, True, mid in stale_ids, False, cat)
                if mid not in best or _rank[cat] > _rank[best[mid][6]]:
                    best[mid] = row
            for mid in partial_ids:
                row = (control_ref, standard_id, role, False, False, True, "partial")
                if mid not in best or _rank["partial"] > _rank[best[mid][6]]:
                    best[mid] = row
            for mid in unrec_ids:
                row = (control_ref, standard_id, role, False, False, False, "unrecognised")
                if mid not in best or _rank["unrecognised"] > _rank[best[mid][6]]:
                    best[mid] = row

    rows: list[tuple[str, str, str, str, str, bool, bool, bool, str]] = [
        (tenant_id, mid, cr, std, role, sat, stl, prt, cat)
        for mid, (cr, std, role, sat, stl, prt, cat) in best.items()
    ]

    if not rows:
        return 0

    # Ship 59'.e — pre-load stub_effective. Re-used below for stub
    # verdict rows AND handed to _persist_bridge_coverage to avoid a
    # second Neo4j round-trip. Silent-fail on Neo4j issues: stubs
    # remain uncovered in SSoT but the direct pass still lands.
    stub_effective: dict[str, tuple[str, list[str]]] = {}
    _drv = _build_engine_neo4j_driver()
    if _drv is not None:
        try:
            with _drv.session() as _s:
                stub_effective = _load_stub_effective_musts(_s)
        except Exception as e:
            logger.warning("stub_effective load skipped: %s", e)
        finally:
            try: _drv.close()
            except Exception: pass

    # Ship 59'.e — synthesize stub-context verdict rows. Same must_id
    # appears twice: once under its canonical owner control (e.g.
    # item:Art.32:purposes @ control_ref='Art.32') and once per stub
    # borrowing it (e.g. same MUST @ control_ref='Art.32.1.b'). Both
    # rows carry identical satisfied/stale/partial facts — the stub
    # row's `reason` is tagged 'stub_rollup:<stub_ref>' so consumers
    # (and the reader's must_ids scope filter) can distinguish.
    stub_rows: list[tuple] = []
    for stub_ref, (stub_std, must_ids) in stub_effective.items():
        stub_role = _framework_role(stub_std)
        for mid in must_ids:
            if mid in best:
                _cr, _std, _role, sat, stl, prt, _cat = best[mid]
                stub_rows.append((
                    tenant_id, mid, stub_ref, stub_std, stub_role,
                    sat, stl, prt, f"stub_rollup:{stub_ref}",
                ))
            else:
                # Canonical MUST unsatisfied (or its control had no
                # engine verdict this run) — emit an unsatisfied stub
                # row so consumers still see the MUST under the stub.
                stub_rows.append((
                    tenant_id, mid, stub_ref, stub_std, stub_role,
                    False, False, False, f"stub_rollup:{stub_ref}",
                ))

    all_rows = rows + stub_rows

    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            # Wipe stale rows for this tenant first (a MUST that was
            # recognised last run but is now N/A-excluded must NOT keep
            # its old satisfied=TRUE row). Deleting + re-inserting is
            # cheaper than tracking supersession per MUST.
            cur.execute(
                "DELETE FROM posture_must_verdicts WHERE tenant_id = %s::uuid",
                (tenant_id,),
            )
            cur.executemany("""
                INSERT INTO posture_must_verdicts
                    (tenant_id, must_id, control_ref, standard_id,
                     framework_role, satisfied, stale, partial, reason, computed_at)
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, now())
            """, all_rows)
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise

    # Ship 59'.b — bridge coverage pass. Walk Neo4j IMPLEMENTS/SUPPORTS/
    # ENABLES/GOVERNANCE edges and emit one bridge_coverage row per
    # (target_must, source_must, edge_type) triple where source is
    # direct-satisfied. Best-effort; never blocks the direct pass.
    try:
        satisfied_by_control = _index_satisfied_musts(rows)
        n_bridges = _persist_bridge_coverage(
            pg_conn, tenant_id, satisfied_by_control, _framework_role,
            stub_effective, na_node_ids,
        )
        if n_bridges:
            logger.info(
                "posture_must_bridge_coverage: wrote %d rows", n_bridges,
            )
    except Exception as e:
        logger.warning("bridge coverage persist skipped: %s", e)

    return len(all_rows)


def _index_satisfied_musts(rows: list[tuple]) -> dict[str, set[str]]:
    """From the flat row list, build {control_ref -> {satisfied_must_id}}.
    Used by _persist_bridge_coverage to enumerate source MUSTs per control
    without re-querying posture_must_verdicts."""
    out: dict[str, set[str]] = {}
    for r in rows:
        # Row shape: (tenant_id, must_id, cr, std, role, satisfied, stale, partial, cat)
        _, mid, cr, _std, _role, sat, _stl, _prt, _cat = r
        if sat:
            out.setdefault(cr, set()).add(mid)
    return out


def _persist_bridge_coverage(
    pg_conn,
    tenant_id: str,
    satisfied_by_control: dict[str, set[str]],
    framework_role_fn,
    stub_effective: dict[str, tuple[str, list[str]]] | None = None,
    na_node_ids:    set[str] | None = None,
) -> int:
    """Walk xfw bridges (IMPLEMENTS/SUPPORTS/ENABLES/GOVERNANCE) in Neo4j
    and emit bridge coverage rows for direct-satisfied source MUSTs.

    One-hop only — matches auditor discipline (Ship 58 audit Gap 1 +
    2026-08-11 design discussion). Bridge edges lack scope_items in the
    current graph (audited 2026-08-11), so all target-control MUSTs are
    considered in-scope per bridge.

    Ship 59'.b. Ship 59'.e adds stub_effective parameter (pre-loaded by
    the caller in _persist_must_verdicts) so we don't re-open Neo4j.
    Best-effort — silently no-ops if Neo4j is unavailable. Overwrites
    the tenant's rows atomically inside a delete+insert.
    """
    if not satisfied_by_control:
        return 0

    stub_effective = stub_effective or {}
    na_node_ids    = na_node_ids or set()

    # _build_engine_neo4j_driver is defined in this same module.
    drv = _build_engine_neo4j_driver()
    if drv is None:
        return 0

    edge_types = ("IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE")
    bridge_rows: list[tuple] = []
    try:
        with drv.session() as s:
            for et in edge_types:
                # Ship 68'.a — pull the optional scope_items property.
                # Shape: list of {"sr": source_must_id, "tg": target_must_id}
                # (short field names to keep the JSON compact). When the
                # curator has authored specific per-MUST-pair scope, we
                # emit bridge_coverage rows only for those pairs; when
                # absent (default on unauthored edges), fall back to the
                # cross-product model (each satisfied source MUST × each
                # target MUST) — preserves pre-Ship-68 behavior on
                # unauthored bridges so migration is opportunistic.
                q = f"""
                    MATCH (src:RequirementNode)-[e:{et}]->(dst:RequirementNode)
                    OPTIONAL MATCH (dst)-[:SATISFIED_BY]->(:FulfilmentSpec)
                               -[:REQUIRES_EVIDENCE]->(dst_er:EvidenceRequirement)
                               -[:MUST_CONTAIN]->(dst_ci:ChecklistItem)
                    RETURN src.ref AS src_ref, src.id AS src_id,
                           dst.ref AS dst_ref, dst.id AS dst_id,
                           collect(DISTINCT dst_ci.id) AS dst_musts,
                           e.scope_items AS scope_items
                """
                for row in s.run(q).data():
                    src_ref = row["src_ref"]
                    if src_ref not in satisfied_by_control:
                        continue
                    source_musts_satisfied = satisfied_by_control[src_ref]
                    if not source_musts_satisfied:
                        continue
                    src_std = _extract_std(row["src_id"])
                    dst_std = _extract_std(row["dst_id"])
                    dst_ref = row["dst_ref"] or ""
                    # Ship 66'.b — N/A target dominance. Skip bridges
                    # pointing to out-of-scope controls so the reader
                    # can't accidentally surface attribution to N/A
                    # controls via direct bridge_coverage queries.
                    # Source side is already filtered by Ship 66'.b's
                    # SSoT writer (satisfied_by_control doesn't contain
                    # N/A source controls' MUSTs).
                    if row["dst_id"] and row["dst_id"] in na_node_ids:
                        continue
                    dst_musts = [m for m in (row["dst_musts"] or []) if m]
                    # Ship 59'.e — if target is a stub (0 direct MUSTs),
                    # use the pre-computed effective MUSTs (via derivation
                    # or ref-parsing to parent). Attribution rows still
                    # tagged with the stub's dst_ref so consumers can
                    # query the stub directly.
                    if not dst_musts:
                        _stub_std, dst_musts = stub_effective.get(dst_ref, (None, []))
                        if not dst_musts:
                            continue  # legitimately unresolvable (e.g. Art.83)
                    src_role = framework_role_fn(src_std)
                    dst_role = framework_role_fn(dst_std)

                    # Ship 68'.a — authored per-pair mode. Neo4j returns
                    # scope_items as a list of JSON strings (property
                    # arrays are homogeneous). Parse defensively; any
                    # malformed entry falls through to cross-product on
                    # this edge so a bad edge doesn't lose attribution.
                    scope_pairs = _parse_scope_items(row.get("scope_items"))
                    if scope_pairs:
                        # Emit only authored pairs whose source MUST is
                        # satisfied AND whose target MUST is in scope.
                        _dst_must_set = set(dst_musts)
                        for pair in scope_pairs:
                            sr = pair.get("sr")
                            tg = pair.get("tg")
                            if not (sr and tg):
                                continue
                            if sr not in source_musts_satisfied:
                                continue
                            if tg not in _dst_must_set:
                                continue
                            bridge_rows.append((
                                tenant_id, tg, dst_ref, dst_std, dst_role,
                                sr, src_ref, src_std, src_role, et,
                            ))
                    else:
                        # Cross-product fallback (unauthored edges).
                        # Each satisfied source MUST bridges to each
                        # target MUST via this edge.
                        for src_must in source_musts_satisfied:
                            for dst_must in dst_musts:
                                bridge_rows.append((
                                    tenant_id, dst_must, dst_ref, dst_std, dst_role,
                                    src_must, src_ref, src_std, src_role, et,
                                ))
    finally:
        try: drv.close()
        except Exception: pass

    if not bridge_rows:
        return 0

    # Dedupe on UNIQUE key (target_must, target_control_ref, source_must,
    # edge_type). Ship 59'.e — target_control_ref is part of the key so
    # stub attribution rows (target_control_ref='Art.32.1.b') coexist
    # with parent attribution rows (target_control_ref='Art.32') even
    # when they share target_must_id (both borrow parent's MUSTs).
    unique_rows: dict[tuple, tuple] = {}
    for r in bridge_rows:
        key = (r[1], r[2], r[5], r[9])
        unique_rows[key] = r
    rows = list(unique_rows.values())

    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute(
                "DELETE FROM posture_must_bridge_coverage WHERE tenant_id = %s::uuid",
                (tenant_id,),
            )
            cur.executemany("""
                INSERT INTO posture_must_bridge_coverage
                    (tenant_id, target_must_id, target_control_ref, target_standard_id, target_role,
                     source_must_id, source_control_ref, source_standard_id, source_role, edge_type,
                     computed_at)
                VALUES (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            """, rows)
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise

    return len(rows)


def _parse_scope_items(raw) -> list[dict]:
    """Ship 68'.a — normalize the optional scope_items edge property.

    Neo4j homogeneously-typed arrays only allow primitive elements, so
    curator-authored per-pair scope is stored as a list of JSON strings
    (each string encoding one {"sr": source_must_id, "tg": target_must_id}
    object). This helper accepts:

      - list[str]       (Neo4j-native — each element a JSON blob)
      - list[dict]      (already deserialized — accept as-is)
      - JSON string     (single-string encoding of the whole list)
      - None / empty    (returns [])

    Any malformed element is silently skipped so a single bad entry
    doesn't take down the whole edge's scope — the writer will still
    emit rows for the valid pairs; if none parse, it falls back to
    cross-product (Ship 68'.a bridge writer contract).
    """
    if not raw:
        return []
    import json as _json
    out: list[dict] = []
    if isinstance(raw, str):
        try:
            parsed = _json.loads(raw)
        except Exception:
            return []
        raw = parsed if isinstance(parsed, list) else []
    if not isinstance(raw, list):
        return []
    for elem in raw:
        if isinstance(elem, dict):
            out.append(elem)
            continue
        if isinstance(elem, str):
            try:
                obj = _json.loads(elem)
            except Exception:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out


def _extract_std(node_id: str) -> str:
    """'GDPR:2016/679:Art.46' → 'GDPR:2016/679'."""
    parts = (node_id or "").rsplit(":", 1)
    return parts[0] if len(parts) == 2 else (node_id or "")


def _load_stub_effective_musts(neo_session) -> dict[str, tuple[str, list[str]]]:
    """Ship 59'.e (2026-08-11) — resolve effective MUSTs for stub nodes.

    A "stub" RequirementNode has zero MUST_CONTAIN items of its own but
    is referenced by xfw bridges (auditors + curators need to be able to
    query "how is Art.32.1.b covered?" directly, not "you have to
    manually check Art.32's coverage instead"). Ship 59'.e resolves
    each stub's effective MUSTs so the bridge writer can emit
    self-contained attribution rows targeting the stub's control_ref.

    Two resolution paths, in order:
      1. Follow DERIVES_FROM edges from the stub's FulfilmentSpec to
         source controls, transitively (up to depth 3). If any resolves
         to a node with MUST items, use those. Graph-native — this is
         the mechanism curators use to model "Art.5.1.f's compliance IS
         Art.32's compliance" (definitional derivation).
      2. Ref-parse fallback: `Art.X.Y.Z` → `Art.X`. Used for stubs like
         Art.32.1.b that have IMPLEMENTS bridges from curators but no
         explicit DERIVES_FROM. GDPR-specific pattern; not applicable
         to ISO controls (their refs don't have this sub-clause shape).
      3. If neither path resolves (like Art.83 — a penalties article
         with no compliance MUSTs anywhere), return empty. SSoT
         legitimately has no attribution to emit for these.

    Returns {stub_ref: (standard_id, [must_id, ...])}. Only stubs with
    resolvable effective MUSTs appear as keys. The standard_id is the
    stub's own standard (not the parent's — bridges + verdict rows are
    scoped by the stub's framework).
    """
    # Find all stubs (RequirementNodes with 0 direct MUSTs) + capture
    # their node id so we can extract the standard_id.
    stubs = neo_session.run("""
        MATCH (rn:RequirementNode)
        OPTIONAL MATCH (rn)-[:SATISFIED_BY]->(:FulfilmentSpec)
                       -[:REQUIRES_EVIDENCE]->(:EvidenceRequirement)
                       -[:MUST_CONTAIN]->(ci:ChecklistItem)
        WITH rn, count(DISTINCT ci) AS n_musts
        WHERE n_musts = 0
        RETURN rn.ref AS ref, rn.id AS node_id
    """).data()

    import re as _re
    out: dict[str, tuple[str, list[str]]] = {}
    for stub in stubs:
        ref = stub["ref"]
        if not ref:
            continue
        stub_std = _extract_std(stub["node_id"] or "")

        # Path 1: transitive DERIVES_FROM (up to depth 3)
        r = neo_session.run("""
            MATCH (stub:RequirementNode {ref: $ref})
                  -[:SATISFIED_BY]->(:FulfilmentSpec)
                  -[:DERIVES_FROM*1..3]->(dep:RequirementNode)
                  -[:SATISFIED_BY]->(:FulfilmentSpec)
                  -[:REQUIRES_EVIDENCE]->(:EvidenceRequirement)
                  -[:MUST_CONTAIN]->(ci:ChecklistItem)
            RETURN collect(DISTINCT ci.id) AS musts
        """, ref=ref).single()
        if r and r["musts"]:
            out[ref] = (stub_std, r["musts"])
            continue

        # Path 2: ref parsing (GDPR Art.X.Y.Z → Art.X)
        m = _re.match(r"^(Art\.\d+)(\.\d+.*)?$", ref)
        if m and m.group(2):
            parent_ref = m.group(1)
            rp = neo_session.run("""
                MATCH (parent:RequirementNode {ref: $parent_ref})
                      -[:SATISFIED_BY]->(:FulfilmentSpec)
                      -[:REQUIRES_EVIDENCE]->(:EvidenceRequirement)
                      -[:MUST_CONTAIN]->(ci:ChecklistItem)
                RETURN collect(DISTINCT ci.id) AS musts
            """, parent_ref=parent_ref).single()
            if rp and rp["musts"]:
                out[ref] = (stub_std, rp["musts"])
                continue

        # Path 3: no resolution — leave out of map. Consumers get empty
        # attribution for this stub, which is the honest signal.

    return out


def _persist_engine_proposals(pg_conn, tenant_id: str, verdicts: dict) -> int:
    """Write engine verdicts as Stage-2 proposals. Returns rows written.

    Phase 1c: the verdict (finding + reason) is written to `posture_assertions`
    via set_assertion(source='engine', status='pending', ...). The lifecycle
    marker (engine_proposal_status='proposed', engine_proposed_at=NOW()) is
    bumped on posture_controls because the Stage-2 approve/reject flow toggles
    that column to track decided state; the assertion supersession model owns
    only the verdict, not the lifecycle. Reverse-sync trigger does not fire on
    engine_proposal_status/at changes — it only watches finding/source/
    gap_description/confidence — so no trigger loop.

    Scope: only determinative postures (NC/OFI/Comply/N/A) are proposed;
    indeterminate verdicts (UNKNOWN/deferred/NotApplicable) are skipped.

    Idempotency: the skip-no-op check compares the proposed (finding, reason)
    against the LATEST engine PA row for the control (any status). If they
    match exactly, the proposal is treated as a no-op and skipped — pending
    rows skip churn; approved/rejected rows skip the re-propose.

    Concurrence path ([[engine_agreement_suppression]] fix): when the engine
    agrees with the live finding at NC or OFI, write the engine PA at
    status='active' (no Stage-2 queue entry) so chat / LLM context can pick
    up the engine's structured 4-leaf reason via PA. Comply / N/A
    concurrence is still skipped — engine adds nothing on top.

    Writes commit at the end. On exception, rolls back and re-raises; caller
    treats persistence as best-effort.
    """
    if not verdicts:
        return 0

    from rag.posture.assertions import set_assertion, get_latest_engine_assertion

    proposable: list[tuple[str, str, str]] = []  # (cid, posture, reason)
    for cid, verdict in verdicts.items():
        if verdict.posture in ("UNKNOWN", "deferred", "NotApplicable"):
            continue
        proposable.append((cid, verdict.posture, verdict.reason or ""))

    if not proposable:
        return 0

    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            written = 0
            for cid, posture, reason in proposable:
                if ":" in cid:
                    standard_id_full = cid.rsplit(":", 1)[0]
                    control_ref      = cid.rsplit(":", 1)[1]
                else:
                    continue

                cur.execute(
                    """
                    SELECT finding, engine_proposal_status
                      FROM posture_controls
                     WHERE tenant_id   = %s
                       AND standard_id = %s
                       AND control_ref = %s
                       AND is_active   = TRUE
                     LIMIT 1
                    """,
                    (tenant_id, standard_id_full, control_ref),
                )
                cur_row = cur.fetchone()
                if cur_row is None:
                    continue
                live_finding, cur_status = cur_row

                # PA history is the sole source of prior-proposal truth.
                # Latest engine-authored assertion (any status) determines
                # whether this verdict is a no-op repeat. Trigger- and
                # backfill-written rows are excluded because their
                # gap_description is sourced from posture_controls.
                # gap_description (the LIVE narrative) rather than the
                # engine's verdict reason — same finding but different text
                # would look like a fresh proposal and cause an approved
                # control to flip back to 'proposed' on every restart.
                latest = get_latest_engine_assertion(
                    cur,
                    tenant_id            = tenant_id,
                    control_ref          = control_ref,
                    standard_id          = standard_id_full,
                    engine_authored_only = True,
                )

                # NC/OFI concurrence: engine and live both say the same
                # gap-bearing verdict. The live decision stands; the engine
                # attaches its structured 4-leaf reason at status='active'
                # so chat / LLM context can surface auditor-grade detail.
                # No Stage-2 entry needed — there's nothing to decide.
                # See [[engine_agreement_suppression]].
                agrees_nc_ofi_concur = (
                    posture in ("NC", "OFI") and live_finding == posture
                )

                # If the engine view has shifted to concurrence with live but
                # a stale pending proposal still sits in the queue, supersede
                # it: the engine no longer holds the divergent view, so the
                # Stage-2 entry is obsolete. PC.engine_proposal_status is
                # reset so list_queue / approve no longer surfaces it.
                if (agrees_nc_ofi_concur
                        and latest is not None
                        and latest.get("status") == "pending"):
                    cur.execute(
                        "UPDATE posture_assertions "
                        "   SET status='superseded', superseded_at=NOW() "
                        " WHERE id=%s",
                        (latest["id"],),
                    )
                    cur.execute(
                        "UPDATE posture_controls "
                        "   SET engine_proposal_status='none', "
                        "       engine_proposed_at     =NULL "
                        " WHERE tenant_id=%s AND standard_id=%s "
                        "   AND control_ref=%s AND is_active=TRUE",
                        (tenant_id, standard_id_full, control_ref),
                    )
                    latest = None  # rerun the no-op gate against a clean slate

                if latest is not None:
                    if latest["finding"] == posture and (latest["gap_description"] or "") == reason:
                        continue
                else:
                    # No engine PA history yet. Skip when engine concurs with
                    # live at Comply / N/A — engine adds nothing on top of a
                    # clean posture. NC / OFI concurrence falls through to
                    # write an 'active' engine PA (above).
                    if live_finding == posture and not agrees_nc_ofi_concur:
                        continue

                write_status = "active" if agrees_nc_ofi_concur else "pending"

                set_assertion(
                    cur,
                    tenant_id       = tenant_id,
                    control_ref     = control_ref,
                    standard_id     = standard_id_full,
                    source          = "engine",
                    status          = write_status,
                    finding         = posture,
                    gap_description = reason,
                    set_by          = "engine",
                )
                # Lifecycle marker only fires for proposals awaiting a Stage-2
                # decision. 'active' concurrences need no queue entry — the
                # live finding already matches.
                if write_status == "pending":
                    cur.execute(
                        """
                        UPDATE posture_controls
                           SET engine_proposal_status = 'proposed',
                               engine_proposed_at     = NOW()
                         WHERE tenant_id   = %s
                           AND standard_id = %s
                           AND control_ref = %s
                           AND is_active   = TRUE
                        """,
                        (tenant_id, standard_id_full, control_ref),
                    )
                    # Ship 3'.e producer: notify tenant of the new pending
                    # Stage-2 verdict. related_entity_id is the posture row
                    # id so ON CONFLICT dedup collapses re-runs against the
                    # same control. Severity 'high' when engine proposes NC
                    # over a live Comply (the auditor-critical case); else
                    # 'medium'. Best-effort — notify() swallows exceptions.
                    try:
                        cur.execute(
                            """
                            SELECT id::text
                              FROM posture_controls
                             WHERE tenant_id   = %s
                               AND standard_id = %s
                               AND control_ref = %s
                               AND is_active   = TRUE
                             LIMIT 1
                            """,
                            (tenant_id, standard_id_full, control_ref),
                        )
                        row = cur.fetchone()
                        posture_row_id = row[0] if row else None
                        if posture_row_id:
                            from rag.cascade.notify import notify as _notify
                            _sev = "high" if (
                                posture == "NC" and live_finding == "Comply"
                            ) else "medium"
                            _notify(
                                cur,
                                tenant_id           = tenant_id,
                                kind                = "stage2_proposal_ready",
                                title               = f"Review engine proposal for {control_ref}",
                                body                = (
                                    f"Engine proposes {posture} "
                                    f"(live is {live_finding or 'Not assessed'}). "
                                    f"Open Stage-2 to accept or reject."
                                ),
                                severity            = _sev,
                                related_entity_kind = "posture_control",
                                related_entity_id   = posture_row_id,
                                related_control_ref = control_ref,
                                related_event_type  = "stage2_proposal_ready",
                            )
                    except Exception:
                        pass
                written += 1
        pg_conn.commit()
        return written
    except Exception:
        try:
            pg_conn.rollback()
        except Exception:
            pass
        raise


def _rebuild_gap_list(unacked_leaves) -> list:
    """Per-leaf gap text for callers wanting the full list (e.g. detailed
    explainer surface). Same format as ControlVerdict.gap_list but filtered
    to non-acknowledged leaves.

    Delegates to the engine's _build_gaps so the polite Phase-C copy applies
    uniformly — never branch the wording on caller, only on classification."""
    from rag.posture.fulfilment_engine import _build_gaps
    our_g, tenant_g = _build_gaps(list(unacked_leaves), None)
    return our_g + tenant_g


def _build_engine_neo4j_driver():
    """Lazy import + build a Neo4j driver from .env, or None if unavailable.

    Module-level import would couple posture_loader to neo4j availability;
    lazy import keeps the engine an opt-in overlay."""
    try:
        from neo4j import GraphDatabase
        uri  = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        pwd  = os.getenv("NEO4J_PASSWORD")
        if not (uri and user and pwd):
            return None
        # Phase-1 specs/edges carry NULL applies_when (see [[applies-when-phase1-regression-tests]]);
        # silence the UNRECOGNIZED-property notification spec_builder.py would otherwise emit
        # on every engine sweep. Remove once any FulfilmentSpec actually populates the key.
        return GraphDatabase.driver(
            uri,
            auth=(user, pwd),
            notifications_disabled_classifications=["UNRECOGNIZED"],
        )
    except Exception as e:
        logger.warning("Neo4j driver for posture engine unavailable: %s", e)
        return None


def load_client_facts(pg_conn, tenant_id: str):
    """
    Load ClientFacts for a tenant from Postgres client_facts table.
    Returns a ClientFacts dataclass instance.
    Falls back to safe defaults if row not found.
    """
    from enrichment.obligations.client_facts import ClientFacts

    defaults = {
        "sector":                    "technology",
        "processes_personal_data":   True,
        "eu_data_subjects":          True,
        "uk_data_subjects":          False,
        "role_controller":           True,
        "role_processor":            False,
        "role_joint_controller":     False,
        "special_category_data":     False,
        "criminal_conviction_data":  False,
        "childrens_data":            False,
        "automated_decision_making": False,
        "profiling":                 False,
        "develops_software":         False,
        "uses_cloud_services":       True,
        "uses_processors":           True,
        "has_remote_workers":        True,
        "has_physical_premises":     False,
        "large_scale_processing":    False,
        "systematic_monitoring":     False,
        "high_risk_processing":      False,
        "employee_count_250_plus":   False,
        "public_authority":          False,
        "transfers_data_outside_eu": False,
        "collected_via":             "workbook",
    }

    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    sector,
                    processes_personal_data,
                    eu_data_subjects,
                    uk_data_subjects,
                    role_controller,
                    role_processor,
                    role_joint_controller,
                    special_category_data,
                    criminal_conviction_data,
                    childrens_data,
                    automated_decision_making,
                    profiling,
                    develops_software,
                    uses_cloud_services,
                    uses_processors,
                    has_remote_workers,
                    has_physical_premises,
                    large_scale_processing,
                    systematic_monitoring,
                    high_risk_processing,
                    employee_count_250_plus,
                    public_authority,
                    transfers_data_outside_eu,
                    collected_via
                FROM client_facts
                WHERE tenant_id = %s
                LIMIT 1
            """, (tenant_id,))
            row = cur.fetchone()

            if row:
                cols = [d[0] for d in cur.description]
                db_facts = dict(zip(cols, row))
                # Merge DB values over defaults (DB wins for non-None values)
                for k, v in db_facts.items():
                    if v is not None and k in defaults:
                        defaults[k] = v

    except Exception as e:
        logger.warning(f"load_client_facts failed for {tenant_id}: {e} — using defaults")
        try:
            pg_conn.rollback()  # Reset transaction so subsequent queries work
        except Exception:
            pass

    # Map DB column names to ClientFacts field names
    field_map = {
        "processes_personal_data":  "processes_pii",
        "childrens_data":           "processes_children_data",
        "role_controller":          None,   # handled below
        "role_processor":           None,   # handled below
    }

    # Derive role string from boolean flags
    if defaults.get("role_controller") and defaults.get("role_processor"):
        role = "both"
    elif defaults.get("role_processor"):
        role = "processor"
    else:
        role = "controller"

    # Build kwargs for ClientFacts — only include known fields
    kwargs = {"role": role}
    skip = {"role_controller", "role_processor", "collected_via"}
    for k, v in defaults.items():
        if k in skip:
            continue
        mapped = field_map.get(k, k)
        if mapped is None:
            continue
        if mapped in ClientFacts.__dataclass_fields__:
            kwargs[mapped] = v
        elif k in ClientFacts.__dataclass_fields__:
            kwargs[k] = v

    return ClientFacts(**{k: v for k, v in kwargs.items()
                         if k in ClientFacts.__dataclass_fields__})


def _load_db_url() -> str:
    """Load DATABASE_URL from env or .env file."""
    from pathlib import Path
    if not os.getenv("DATABASE_URL"):
        try:
            from dotenv import load_dotenv
            here = Path(__file__).resolve().parent
            for candidate in [here, here.parent, here.parent.parent]:
                env_file = candidate / ".env"
                if env_file.exists():
                    load_dotenv(env_file)
                    logger.info(f"Loaded .env from {env_file}")
                    break
        except ImportError:
            pass
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL not set. Add to .env:\n"
            "  DATABASE_URL=postgresql://arioncomply_app:password"
            "@localhost/arioncomply_compliance"
        )
    return url


def build_pg_conn():
    """
    Build a single Postgres connection. Use for one-off operations.
    For concurrent/multi-request use, prefer build_pg_pool().
    """
    import psycopg2
    return psycopg2.connect(_load_db_url())


def build_pg_pool(minconn: int = 2, maxconn: int = 10):
    """
    Build a psycopg2 connection pool for concurrent use.
    Suitable for multi-tenant SaaS with concurrent users.

    Usage:
        pool = build_pg_pool()
        conn = pool.getconn()
        try:
            # use conn
        finally:
            pool.putconn(conn)

    Or use as context manager with the helper:
        with pool_conn(pool) as conn:
            # use conn
    """
    from psycopg2 import pool as pg_pool
    return pg_pool.SimpleConnectionPool(
        minconn = minconn,
        maxconn = maxconn,
        dsn     = _load_db_url(),
    )


class pool_conn:
    """
    Context manager for clean connection pool usage.

    with pool_conn(pool) as conn:
        do_something(conn)
    """
    def __init__(self, pool):
        self._pool = pool
        self._conn = None

    def __enter__(self):
        self._conn = self._pool.getconn()
        return self._conn

    def __exit__(self, *_):
        if self._conn:
            self._pool.putconn(self._conn)
            self._conn = None


def load_document_alerts(pg_conn, tenant_id: str) -> list[dict]:
    """
    Load document alerts for the tenant — missing files, overdue reviews.
    Used by the pipeline to surface document gaps in answers.
    Returns list of alert dicts ordered by severity.
    """
    try:
        with pg_conn.cursor() as cur:
            # Set RLS context — view enforces isolation via base table RLS
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    platform_ref, external_ref, document_title,
                    document_status, alert_type, alert_message,
                    linked_controls, linked_control_refs,
                    linked_findings, worst_finding_score
                FROM document_alerts
                WHERE alert_type IN ('CRITICAL', 'WARNING', 'INFO')
                ORDER BY worst_finding_score NULLS LAST, document_title
            """)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.warning(f"load_document_alerts failed: {e}")
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return []


def load_uploaded_documents(pg_conn, tenant_id: str) -> list[dict]:
    """
    Load documents the tenant has actually delivered, from client_documents.
    Source of truth is client_documents.document_status — the intake pipeline
    transitions it to 'uploaded' once a file is processed against a registered
    entry. document_uploads is an audit log; document_status is the state.

    Used to answer "which documents have we uploaded / submitted" (positive
    polarity); contrast with load_document_alerts which lists registered-but-
    missing docs (document_status='registered').
    """
    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            # control_refs is read LIVE from document_findings rather than the
            # cached client_documents.control_refs column. Reason: as new
            # extractors (ISO 27701, GDPR) start writing findings against
            # already-uploaded docs, those new frameworks must surface
            # automatically without re-running intake. The cached column is
            # still populated by intake as a fast-path / fallback.
            cur.execute("""
                SELECT
                    cd.id::text          AS doc_id,
                    cd.platform_ref,
                    cd.external_ref,
                    cd.document_title,
                    cd.filename,
                    cd.evidence_type     AS doc_type,
                    cd.document_status,
                    cd.uploaded_at::text,
                    cd.page_count,
                    cd.file_size_bytes,
                    cd.mime_type,
                    COALESCE(
                        (
                            SELECT array_agg(s_ref ORDER BY s_ref)
                            FROM (
                                SELECT DISTINCT
                                    df.standard_id || ':' || df.control_ref AS s_ref
                                FROM document_findings df
                                WHERE df.document_id = cd.id
                                  AND df.tenant_id   = cd.tenant_id
                                  AND df.is_active   = TRUE
                            ) sub
                        ),
                        -- Fallback: if findings haven't been written yet,
                        -- the cached column already holds fully-qualified
                        -- STANDARD:VERSION:REF entries (intake writes them
                        -- that way). No framework guesswork here.
                        cd.control_refs
                    ) AS framework_refs
                FROM client_documents cd
                WHERE cd.tenant_id       = %s::uuid
                  AND cd.is_active       = TRUE
                  AND cd.document_status IN ('uploaded', 'processing', 'active')
                ORDER BY cd.uploaded_at DESC NULLS LAST, cd.document_title NULLS LAST
            """, (tenant_id,))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
    except Exception as e:
        logger.warning(f"load_uploaded_documents failed: {e}")
        try:
            pg_conn.rollback()
        except Exception:
            pass
        return []


def load_per_control_implications(pg_conn, tenant_id: str) -> dict:
    """S3k: per-control summary of pending/overdue triggered_implications.

    Returns dict keyed by node_id (e.g. 'ISO27001:2022:A.6.3') with:
      {
        "pending":      int,
        "overdue":      int,
        "examples":     [
          {"source_event_type": str, "expected_action": str,
           "rationale": str, "due_date": iso str|None, "overdue": bool}
        ],   # up to 3 sample rows for LLM context
      }

    The dict is sparse — only controls with at least one pending impl
    have keys. Tenant context GUC must already be set by caller; this
    function does its own set_config for safety.
    """
    from datetime import datetime, timezone
    out: dict[str, dict] = {}
    try:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,),
            )
            cur.execute(
                """
                SELECT target_requirement_id,
                       sum(CASE WHEN status = 'pending'
                                  AND (due_date IS NULL OR due_date >= now())
                                THEN 1 ELSE 0 END) AS pending,
                       sum(CASE WHEN status = 'pending'
                                  AND due_date IS NOT NULL
                                  AND due_date < now()
                                THEN 1 ELSE 0 END) AS overdue
                  FROM triggered_implication
                 WHERE tenant_id = %s::uuid
                   AND status = 'pending'
                 GROUP BY target_requirement_id
                """,
                (tenant_id,),
            )
            for req_id, pending, overdue in cur.fetchall():
                if not (pending or overdue):
                    continue
                out[req_id] = {
                    "pending":  int(pending or 0),
                    "overdue":  int(overdue or 0),
                    "examples": [],
                }

            if not out:
                return out

            # Pull up to 3 example rows per control for LLM context
            cur.execute(
                """
                SELECT target_requirement_id, source_event_type,
                       expected_action, rationale, due_date
                  FROM triggered_implication
                 WHERE tenant_id = %s::uuid
                   AND status = 'pending'
                 ORDER BY due_date NULLS LAST, fired_at DESC
                """,
                (tenant_id,),
            )
            now = datetime.now(timezone.utc)
            for req_id, src_evt, action, rationale, due in cur.fetchall():
                rec = out.get(req_id)
                if rec is None or len(rec["examples"]) >= 3:
                    continue
                rec["examples"].append({
                    "source_event_type": src_evt,
                    "expected_action":   action,
                    "rationale":         (rationale or "")[:160],
                    "due_date":          due.isoformat() if due else None,
                    "overdue":           bool(due and due < now),
                })
    except Exception as e:
        logger.warning("load_per_control_implications failed: %s", e)
        return {}
    return out


def load_tenant_context(pg_conn, tenant_id: str) -> dict:
    """
    Load all tenant context in one call:
      posture            — dict of assessed controls
      facts              — ClientFacts dataclass
      scope              — TenantScope (standards + relationships)
      document_alerts    — list of missing/overdue document alerts
      uploaded_documents — list of files actually uploaded to the platform
      implications       — S3k: per-control summary of pending/overdue
                           triggered_implications

    Used by chat.py on startup to replace all hardcodes.
    """
    from rag.scope_loader import load_tenant_scope

    posture            = load_posture(pg_conn, tenant_id)
    facts              = load_client_facts(pg_conn, tenant_id)
    scope              = load_tenant_scope(pg_conn, tenant_id)
    document_alerts    = load_document_alerts(pg_conn, tenant_id)
    uploaded_documents = load_uploaded_documents(pg_conn, tenant_id)
    implications       = load_per_control_implications(pg_conn, tenant_id)

    critical = sum(1 for a in document_alerts if a.get("alert_type") == "CRITICAL")
    warning  = sum(1 for a in document_alerts if a.get("alert_type") == "WARNING")

    logger.info(
        f"Tenant context loaded: {len(posture)} posture controls, "
        f"queryable={scope.queryable_standards}, "
        f"gdpr_evaluable={scope.can_evaluate_gdpr}, "
        f"doc_alerts={len(document_alerts)} ({critical} critical, {warning} warning), "
        f"uploaded={len(uploaded_documents)}, "
        f"impls_per_control={len(implications)}"
    )
    return {
        "posture":            posture,
        "facts":              facts,
        "scope":              scope,
        "document_alerts":    document_alerts,
        "uploaded_documents": uploaded_documents,
        "implications":       implications,
    }
