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
                    engine_proposal_status
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
                    partial_bits = []
                    for l in sorted(partial, key=lambda x: x.role):
                        sat = len(l.items_recognised)
                        total = sat + len(l.items_unrecognised)
                        first_miss = l.items_unrecognised[0] if l.items_unrecognised else ""
                        # Cap the item description so the gap_description
                        # stays compact (one line per partial leaf).
                        first_miss_short = (first_miss[:80] + "…") if len(first_miss) > 80 else first_miss
                        bit = f"{l.role} ({sat}/{total}"
                        if first_miss_short:
                            bit += f" — missing: {first_miss_short}"
                        bit += ")"
                        partial_bits.append(bit)
                    parts.append("partial: " + ", ".join(partial_bits))

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
                    linked_policies, last_updated, engine_proposal_status
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
        "sector":                   "technology",
        "processes_personal_data":  True,
        "eu_data_subjects":         True,
        "role_controller":          True,
        "role_processor":           False,
        "special_category_data":    False,
        "childrens_data":           False,
        "develops_software":        False,
        "uses_cloud_services":      True,
        "uses_processors":          True,
        "has_remote_workers":       True,
        "has_physical_premises":    False,
        "large_scale_processing":   False,
        "high_risk_processing":     False,
        "transfers_data_outside_eu":False,
        "collected_via":            "workbook",
    }

    try:
        with pg_conn.cursor() as cur:
            cur.execute("SELECT set_config('app.tenant_id', %s, TRUE)", (tenant_id,))
            cur.execute("""
                SELECT
                    sector,
                    processes_personal_data,
                    eu_data_subjects,
                    role_controller,
                    role_processor,
                    special_category_data,
                    childrens_data,
                    develops_software,
                    uses_cloud_services,
                    uses_processors,
                    has_remote_workers,
                    has_physical_premises,
                    large_scale_processing,
                    high_risk_processing,
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
