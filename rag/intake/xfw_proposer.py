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


# ── Ship 11'.b — bridge source-quality gate ─────────────────────────
#
# The Ship 10 HITL review (2026-07-20) surfaced that ~35% of stage-1
# rejects (17 of 49) came from bridges propagated from weak source
# findings. Root cause: bridges multiply low-confidence, unbound, or
# fragment-shape source findings across 3-4 target controls each,
# amplifying noise 3-4x per weak source.
#
# This gate filters source findings BEFORE the bridge walk. Sources
# that fail the gate produce no bridges. Legitimate mediums with
# substantive content still propagate.
#
# See [[ship-11-prime-a-extractor-quality-plan-2026-07-20]] for the
# 5-pattern taxonomy this addresses (Pattern 4 — Bridge multiplier).

# Minimum substantive excerpt length. Field-labels ("Subprocessors /
# Any third parties involved") tend to be short + colon-separated;
# genuine prose is longer. 40 chars matches the extractor's
# _MIN_EVIDENCE_LEN (Ship 6'.b grounding).
_BRIDGE_MIN_EXCERPT_CHARS = 40

# Confidences that are permitted to seed bridges. `low` alone gets
# blocked; `medium`/`high` proceed subject to the other criteria.
_BRIDGE_ALLOWED_CONFIDENCES: set[str] = {"medium", "high"}


def _bridge_worthy_check(
    *,
    inference_source:   Optional[str],
    confidence:         Optional[str],
    checklist_item_id:  Optional[str],
    excerpt:            Optional[str],
) -> tuple[bool, str]:
    """Ship 11'.b gate — return (worthy, reason) for a candidate
    source finding, given its raw fields.

    A source is worthy to seed cross-framework bridges when:
      1. It's NOT itself a bridge (no bridge-of-bridges cascade).
      2. Confidence is at least `medium` (drops `low`).
      3. It's either MUST-bound (checklist_item_id set) OR has a
         substantive excerpt (≥40 chars of prose). Field-labels + bare
         section headers fail this check.

    Returns:
      (True, "ok")                  — bridges may propagate
      (False, "<specific reason>")  — bridges suppressed; caller
                                       increments sources_gated

    Takes raw fields (not a DocumentFinding) so both the per-upload
    path (DocumentFinding objects) and the backfill path (Postgres
    tuples) can reuse the same gate. See
    [[ship-11-prime-b-bridge-source-quality-gate-2026-07-20]].
    """
    # 1. No bridge-of-bridges — an xfw source can't seed another bridge.
    if inference_source == "xfw_bridge":
        return (False, "source_is_bridge")

    # 2. Confidence gate — drop `low` before it multiplies.
    conf = (confidence or "").lower()
    if conf not in _BRIDGE_ALLOWED_CONFIDENCES:
        return (False, f"low_confidence:{conf or 'unset'}")

    # 3. Substance gate — MUST-bound OR substantive excerpt.
    #    MUST-bound sources have already been vetted by the critic-
    #    verifier's MUST-binding step, so they carry a stronger prior.
    must_bound = bool(checklist_item_id)
    excerpt_s  = excerpt or ""
    if not must_bound and len(excerpt_s) < _BRIDGE_MIN_EXCERPT_CHARS:
        return (False, f"fragment_source:{len(excerpt_s)}c_no_must")

    return (True, "ok")


def _source_is_bridge_worthy(finding: "DocumentFinding") -> tuple[bool, str]:
    """Convenience wrapper around _bridge_worthy_check for the
    per-upload path that passes DocumentFinding objects."""
    return _bridge_worthy_check(
        inference_source  = getattr(finding, "inference_source", None),
        confidence        = getattr(finding, "confidence", None),
        checklist_item_id = getattr(finding, "checklist_item_id", None),
        excerpt           = getattr(finding, "evidence_text", None),
    )


@dataclass
class ProposalSummary:
    tenant_id:        str
    sources_walked:   int = 0
    sources_gated:    int = 0       # Ship 11'.b — filtered by bridge source-quality gate
    edges_seen:       int = 0
    proposals_written: int = 0
    proposals_skipped: int = 0       # source had no IMPLEMENTS edge, or target out of scope
    standards_targeted: set[str] = field(default_factory=set)

    def __str__(self) -> str:
        return (
            f"xfw_proposer[{self.tenant_id[:8]}]: "
            f"sources={self.sources_walked} gated={self.sources_gated} "
            f"edges={self.edges_seen} written={self.proposals_written} "
            f"skipped={self.proposals_skipped} "
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


def _compose_bridge_excerpt(rationale: str | None,
                            source_excerpt: str | None) -> Optional[str]:
    """S7: combine the catalog-managed bridge rationale with the source
    document excerpt. Format:
        [Bridge: <rationale>] <source_excerpt>
    The rationale answers "why does this cross-framework relationship
    apply?". The source excerpt answers "what does the original
    document say?". Auditor needs both. Length-capped at 500.
    """
    rationale = (rationale or "").strip()
    body      = (source_excerpt or "").strip()
    if rationale:
        # Trim rationale + body to fit 500-char column with delimiter.
        budget = 500 - len(rationale) - len("[Bridge: ] ")
        if budget < 50:
            # Rationale too long — keep just the rationale prefix.
            return f"[Bridge: {rationale[:480]}]"
        return f"[Bridge: {rationale}] {body[:budget]}"
    return body[:500] or None


def _walk_bridges(
    driver: Driver, source_id: str,
) -> list[tuple[str, str, str, str, str, str]]:
    """
    Walk cross-framework bridge edges from a source control node to bridged
    target controls in other standards. Walks BOTH edge types
    (IMPLEMENTS + SUPPORTS) in BOTH directions (undirected match).

    - IMPLEMENTS: A implements B (A is the certifiable operationalisation
      of B's obligation). Evidence for A → propagates to B, and vice versa.
    - SUPPORTS:   A supports B (A helps satisfy B without being identical).
      Evidence for A → still credits B (per the auditor mental model).

    Undirected walk because:
    - Old ISO 27001 ↔ GDPR bridges were loaded bidirectionally (both
      A→B and B→A edges exist).
    - Newer ISO 27701 bridges (Batch 1-3 curation 2026-07-03..07-04)
      are single-direction (A→B only). Without undirected walk, evidence
      landing on Art.28 wouldn't propagate to A.7.2.6 because there's
      no outbound edge from Art.28.

    Returns list of (target_node_id, target_standard_id, target_ref,
    rationale, src_role, tgt_role). The role columns (Phase 1
    role model) let callers filter PROGRAM/EXTENSION → OBLIGATION
    edges — those are handled deterministically by DEMONSTRATES
    propagation in posture_loader (Phase 2b/2c), so xfw proposals
    for that direction would double-write. Deduped when the same
    target is reachable via both edge types.
    """
    cypher = """
    MATCH (a {id: $src_id})-[r:IMPLEMENTS|SUPPORTS]-(b)
    WHERE b.standard_id <> a.standard_id
    RETURN DISTINCT b.id                    AS tgt_id,
                    b.standard_id           AS tgt_std,
                    b.ref                   AS tgt_ref,
                    coalesce(r.rationale, '') AS rationale,
                    coalesce(a.role_owner, '') AS src_role,
                    coalesce(b.role_owner, '') AS tgt_role
    """
    with driver.session() as s:
        return [
            (row["tgt_id"], row["tgt_std"], row["tgt_ref"],
             row["rationale"], row["src_role"], row["tgt_role"])
            for row in s.run(cypher, src_id=source_id)
        ]


# Back-compat alias — callers still using the old name during migration.
_walk_implements = _walk_bridges


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


_CANONICAL_BINDINGS_CACHE: Optional[dict[str, tuple[str, str]]] = None
_DERIVES_CHAIN_CACHE:      Optional[dict[str, list[str]]]      = None


def _load_canonical_bindings(driver: Driver) -> dict[str, tuple[str, str]]:
    """Load control_ref → (canonical_leaf_id, canonical_item_id) from Neo4j.
    Used to bind xfw_bridge findings to a target MUST item so they're
    engine-eligible post Phase-1 retirement.

    Selection heuristic:
      - Canonical leaf: prefer one whose id contains register/procedure/
        record/agreement/programme/policy; else first alphabetically
      - Canonical item: prefer one whose id contains owner/charter/
        scope_processing; else first alphabetically

    Cached per-process — Neo4j is queried once and reused.
    """
    import re
    global _CANONICAL_BINDINGS_CACHE
    if _CANONICAL_BINDINGS_CACHE is not None:
        return _CANONICAL_BINDINGS_CACHE
    by_ctrl: dict[str, list[tuple[str, list[str]]]] = {}
    with driver.session() as s:
        rows = s.run("""
            MATCH (req:EvidenceRequirement)
            OPTIONAL MATCH (req)-[:MUST_CONTAIN]->(item:ChecklistItem)
            RETURN req.id AS leaf, req.control_ref AS ctrl, collect(item.id) AS items
        """).data()
    for r in rows:
        if not r.get("items"):
            continue
        by_ctrl.setdefault(r["ctrl"], []).append((r["leaf"], r["items"]))
    CANONICAL_LEAF = re.compile(r"(register|procedure|record|agreement|programme|policy)")
    OWNER_ITEM = re.compile(r"owner|charter|scope_processing")
    out: dict[str, tuple[str, str]] = {}
    for ctrl, leaves in by_ctrl.items():
        cands = [l for l in leaves if CANONICAL_LEAF.search(l[0])]
        chosen_leaf, items = (cands[0] if cands else sorted(leaves)[0])
        owners = [i for i in items if OWNER_ITEM.search(i)]
        chosen_item = owners[0] if owners else sorted(items)[0]
        out[ctrl] = (chosen_leaf, chosen_item)
    _CANONICAL_BINDINGS_CACHE = out
    logger.info(f"xfw_proposer: loaded {len(out)} canonical bindings from Neo4j")
    return out


def _load_derives_chain() -> dict[str, list[str]]:
    """Load control_ref → [derives_from target refs] from curated
    DerivedSpec definitions. Used to resolve transitively-derived
    specs (Art.5 family etc.) — these have empty direct_evidence by
    *design* (the principle is an alias for its operational
    implementer) but their derives_from chain points to operational
    targets that DO have curated leaves.

    Examples:
      Art.5.1.f → [Art.32]      (security principle → T&O measures)
      Art.5.2   → [Art.24]      (accountability → controller responsibility)
      Art.5.1.e → [A.5.33, Art.25]  (storage limitation → retention + DPbD)
      Art.5     → [Art.5.1, Art.5.2]  (top principle → sub-principles)
    """
    global _DERIVES_CHAIN_CACHE
    if _DERIVES_CHAIN_CACHE is not None:
        return _DERIVES_CHAIN_CACHE
    out: dict[str, list[str]] = {}
    try:
        from enrichment.documents.document_requirements import ALL_DERIVED_SPECS
        for s in ALL_DERIVED_SPECS:
            targets = [d.target_control_ref for d in s.derives_from if d.target_control_ref]
            if targets:
                out[s.control_ref] = targets
    except Exception as e:
        logger.warning(
            f"xfw_proposer: failed to load derives chain: {type(e).__name__}: {e}"
        )
    _DERIVES_CHAIN_CACHE = out
    return out


def _rollup_sub_clause(ref: str) -> str:
    """Roll up GDPR sub-clause to parent: Art.32.1.b → Art.32.
    ISO refs (A.5.x or 5.x) pass through unchanged."""
    if not ref.startswith("Art."):
        return ref
    parts = ref.split(".")
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return ref


def _pick_canonical_item(
    control_ref: str,
    bindings:    dict[str, tuple[str, str]],
    *,
    _depth:      int = 0,
    _seen:       Optional[set[str]] = None,
) -> Optional[str]:
    """Find a canonical checklist_item_id for the given control_ref.

    Resolution order (each falls through to the next when no match):
      1. Direct lookup in bindings
      2. Rolled-up parent (Art.32.1.b → Art.32)
      3. derives_from chain — transitively-derived specs (Art.5 family
         etc.) resolve to their operational targets (Art.32, Art.24,
         A.5.33 etc.). Curated AS DERIVED by design; the principle
         is an alias for the operational implementer.

    Returns None when no resolution exists (truly uncurated, e.g.
    Art.85 national-law derogation). Recursion depth-bounded at 5 to
    handle chains like Art.5 → Art.5.1 → Art.5.1.a → Art.6.
    """
    if _depth > 5:
        return None
    if _seen is None:
        _seen = set()
    if control_ref in _seen:
        return None
    _seen.add(control_ref)
    # Step 1: direct
    if control_ref in bindings:
        return bindings[control_ref][1]
    # Step 2: rolled-up parent (Art.32.1.b → Art.32)
    rolled = _rollup_sub_clause(control_ref)
    if rolled != control_ref and rolled in bindings:
        return bindings[rolled][1]
    # Step 3: derives_from chain (recursive)
    chain = _load_derives_chain()
    candidates = list(chain.get(control_ref, []))
    if rolled != control_ref:
        candidates += chain.get(rolled, [])
    for next_ref in candidates:
        item = _pick_canonical_item(next_ref, bindings,
                                    _depth=_depth + 1, _seen=_seen)
        if item:
            return item
    return None


def _insert_proposal(
    conn,
    *,
    tenant_id:         str,
    document_id:       str,
    control_ref:       str,
    standard_id:       str,
    status:            str,
    confidence:        str,
    inferred_from_ref: str,
    inferred_from_std: str,
    excerpt:           Optional[str] = None,
    checklist_item_id: Optional[str] = None,
) -> bool:
    """Insert one pending xfw proposal. Returns True on success.

    checklist_item_id binds the bridge to a target-framework MUST so
    the proposal is engine-eligible once approved (Phase-1 requires
    bound findings). Caller picks the binding via
    `_pick_canonical_item`; None bridges stay unbound and surface as
    a curation gap on the target standard.
    """
    with conn.cursor() as cur:
        try:
            cur.execute(
                """
                INSERT INTO document_findings (
                    id, tenant_id, document_id,
                    control_ref, standard_id, checklist_item_id,
                    status, confidence, excerpt,
                    extracted_at, is_active, retention_class,
                    inference_source,
                    inferred_from_control_ref, inferred_from_standard_id
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    NOW(), TRUE, 'compliance',
                    'xfw_bridge',
                    %s, %s
                )
                """,
                (
                    str(uuid.uuid4()), tenant_id, document_id,
                    control_ref, standard_id, checklist_item_id,
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

    # Load canonical bindings once for this run — picks a per-control
    # (leaf, item) to bind bridges to so they're engine-eligible after
    # tenant approval. Cached per-process. Bridges to uncurated targets
    # (Art.5 family etc.) get None checklist_item_id and stay unbound.
    bindings = _load_canonical_bindings(driver)

    # Dedup within this run so duplicate source rows don't produce duplicate
    # proposals. Source-level dedup happens on (control_ref, standard_id);
    # proposal-level dedup happens on (document_id, control_ref, standard_id).
    # When multiple findings exist for the same source control, pick the one
    # with the LONGEST substantive excerpt. Prior behavior (take-first-in-
    # iteration-order) let header-only fingerprint_match findings win — the
    # doc-header block (Owner/Version/Effective Date/Classification) matches
    # single-token MUST fingerprints like `owner`, `reviewer`, and gets
    # auto-approved. When such a header-only finding coexisted with a
    # substantive one (e.g. A.8.10 with both a rev_reviewer header match
    # AND a real "Access or receive client system data..." match), the
    # bridge ended up inheriting the header-block excerpt instead of the
    # substantive one. Sort per-group descending on excerpt length so the
    # richest source drives the bridge.
    best_per_source: dict[tuple[str, str], object] = {}
    for f in findings:
        if not f.control_ref or not f.standard_id:
            continue
        src_status = (f.finding or "").lower()
        if src_status not in _SOURCE_STATUSES_TO_PROPAGATE:
            continue
        key = (f.control_ref, f.standard_id)
        prev = best_per_source.get(key)
        if prev is None or len(f.evidence_text or "") > len(prev.evidence_text or ""):
            best_per_source[key] = f

    seen_proposals: set[tuple[str, str, str]] = set()

    # Ship 11'.b — bridge source-quality gate. Skip sources that
    # would produce noisy bridges (low confidence, fragment excerpts,
    # or already-bridged rows). See [[ship-11-prime-b-...]] for the
    # per-pattern rationale.
    for f in best_per_source.values():
        worthy, reason = _source_is_bridge_worthy(f)
        if not worthy:
            logger.debug(
                "xfw_proposer: skipping bridge source %s/%s — %s "
                "(excerpt=%dc conf=%r must=%r)",
                f.standard_id, f.control_ref, reason,
                len(getattr(f, "evidence_text", "") or ""),
                getattr(f, "confidence", None),
                getattr(f, "checklist_item_id", None),
            )
            summary.sources_gated += 1
            continue
        summary.sources_walked += 1
        src_id  = _build_source_node_id(f.standard_id, f.control_ref)
        targets = _walk_bridges(driver, src_id)
        summary.edges_seen += len(targets)

        for tgt_id, tgt_std, tgt_ref, rationale, src_role, tgt_role in targets:
            if tgt_std not in in_scope:
                summary.proposals_skipped += 1
                continue
            # Phase 5 (framework role model, 2026-07-05): DEMONSTRATES
            # propagation (Phase 2b/2c) is the deterministic replacement
            # for PROGRAM/EXTENSION → OBLIGATION xfw proposals. Skip
            # that direction here to avoid double-writing an in-memory
            # posture overlay AND a Stage-1 xfw_bridge finding for the
            # same relationship. Peer directions (PROGRAM ↔ PROGRAM,
            # reverse OBLIGATION → PROGRAM navigation) stay active.
            if src_role in ("program", "extension") and tgt_role == "obligation":
                summary.proposals_skipped += 1
                continue
            key = (document_id, tgt_ref, tgt_std)
            if key in seen_proposals:
                continue
            seen_proposals.add(key)
            status = _PIPELINE_TO_DF_STATUS.get(src_status, "partial")
            chk_item = _pick_canonical_item(tgt_ref, bindings)
            # S7: prepend the catalog-managed bridge rationale (if any) so
            # the auditor sees WHY this cross-framework proposal is asserted,
            # not just THAT the source document mentions the originating
            # control. Falls back to the bare source excerpt when no
            # rationale is attached to the edge.
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
                excerpt=_compose_bridge_excerpt(rationale, f.evidence_text),
                checklist_item_id=chk_item,
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

        # Same canonical-binding cache used in propose_for_findings.
        bindings = _load_canonical_bindings(driver)

        # DISTINCT collapses pre-existing duplicate document_findings rows
        # so each (doc_id, ref, std) source produces at most one walk and
        # one proposal per IMPLEMENTS target. Confidence/excerpt come from
        # an arbitrary representative row — fine for HITL review.
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (document_id, control_ref, standard_id)
                       document_id, control_ref, standard_id, status, confidence,
                       excerpt, checklist_item_id, inference_source
                  FROM document_findings
                 WHERE tenant_id       = %s
                   AND is_active       = TRUE
                   AND inference_source = 'extracted'
                """,
                (tenant_id,),
            )
            rows = cur.fetchall()

        seen_proposals: set[tuple[str, str, str]] = set()
        for (doc_id, ctrl_ref, std_id, status_db, conf, excerpt,
             chk_item_src, inf_src) in rows:
            src_status = (status_db or "").lower()
            if src_status not in _SOURCE_STATUSES_TO_PROPAGATE:
                continue
            # Ship 11'.b — apply bridge source-quality gate.
            worthy, reason = _bridge_worthy_check(
                inference_source  = inf_src,
                confidence        = conf,
                checklist_item_id = chk_item_src,
                excerpt           = excerpt,
            )
            if not worthy:
                summary.sources_gated += 1
                continue
            summary.sources_walked += 1
            src_id  = _build_source_node_id(std_id, ctrl_ref)
            targets = _walk_bridges(driver, src_id)
            summary.edges_seen += len(targets)

            for tgt_id, tgt_std, tgt_ref, rationale, src_role, tgt_role in targets:
                if tgt_std not in in_scope:
                    summary.proposals_skipped += 1
                    continue
                # Phase 5 (framework role model, 2026-07-05): skip
                # PROGRAM/EXTENSION → OBLIGATION direction — handled
                # deterministically by DEMONSTRATES propagation.
                if src_role in ("program", "extension") and tgt_role == "obligation":
                    summary.proposals_skipped += 1
                    continue
                key = (doc_id, tgt_ref, tgt_std)
                if key in seen_proposals:
                    continue
                seen_proposals.add(key)
                proposal_status = _PIPELINE_TO_DF_STATUS.get(src_status, "partial")
                chk_item = _pick_canonical_item(tgt_ref, bindings)
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
                    excerpt=_compose_bridge_excerpt(rationale, excerpt),
                    checklist_item_id=chk_item,
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
