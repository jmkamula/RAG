"""ArionComply — leaf evaluators.

Each evaluator returns a LeafVerdict for one EvidenceRequirement leaf, given
a tenant. The evaluator's job is to:
  1. Look up the leaf's MUST checklist items from Neo4j (item_id + text).
  2. Query Postgres for *current* artifacts of the leaf's evidence_type that
     the LLM extractor reported as having those items 'present'.
  3. Determine which MUST items are recognised and which are unrecognised.
  4. Check freshness if the leaf has freshness_days set (latest upload of a
     matching artifact must be within the window).

Per [[the completeness principle]]: we report what we *recognised*; we do
not judge whether the artifact is "correct". Unrecognised items become
gap-list entries the user can acknowledge or address.

Per [[rls_tenant_context_for_app_user]]: every Postgres read runs after
SELECT set_config('app.tenant_id', %s, TRUE) on the same transaction —
mandatory for arioncomply_app role which has no BYPASSRLS.

GenericLeafEvaluator handles every evidence_type the same way at Phase 1:
match-by-type + checklist-coverage. Per-type specialisations (e.g.
register_entry that counts rows within an artifact, attestation_record
that requires a signatory) are future work — the shared shape stays.

PolicyLeafEvaluator is preserved as a thin alias for backwards-compat with
the commit-3 tests.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from rag.posture.applies_when import EvalContext
from rag.posture.fulfilment_engine import LeafSpec, LeafVerdict


class GenericLeafEvaluator:
    """Evaluator handling any evidence_type with the same generic shape:
    Neo4j → MUST item ids, Postgres → present-status findings on those ids
    for current artifacts of the leaf's type, returns a LeafVerdict.

    Bound to a (pg_conn, neo4j_driver, tenant_id) triple at construction;
    call the instance with (leaf, eval_ctx) to get a LeafVerdict.
    """

    def __init__(self, pg_conn, neo4j_driver, tenant_id: str):
        self._pg        = pg_conn
        self._neo4j     = neo4j_driver
        self._tenant_id = tenant_id

    def __call__(self, leaf: LeafSpec, ctx: EvalContext) -> LeafVerdict:
        # 1. Get MUST checklist item ids (id + text) from Neo4j
        must_items = self._fetch_must_items(leaf.leaf_id)
        if not must_items:
            # Curated leaf with no MUST items — defensible Comply (curator may
            # have only filled SHOULDs). Engine treats satisfied+fresh as
            # Comply.
            return LeafVerdict(
                leaf_id       = leaf.leaf_id,
                role          = "",
                evidence_type = leaf.evidence_type,
                satisfied     = True,
                fresh         = True,
                reason        = "leaf has no MUST items defined",
            )

        must_item_ids   = [it[0] for it in must_items]
        must_item_texts = {it[0]: it[1] for it in must_items}

        # 2. Postgres: which items are 'present' for current artifacts of this type?
        recognised_ids, latest_uploaded_at = self._fetch_recognised_items(
            evidence_type   = leaf.evidence_type,
            must_item_ids   = must_item_ids,
            control_ref     = leaf.control_ref,
            standard_id     = leaf.standard_id,
        )

        # 3. Determine satisfied + freshness
        items_recognised   = [must_item_texts[i] for i in must_item_ids if i in recognised_ids]
        items_unrecognised = [must_item_texts[i] for i in must_item_ids if i not in recognised_ids]
        # Parallel ID arrays — same order as the text arrays so consumers
        # can pair (id, text) safely. Used by per-MUST advisory form to
        # bind tenant inputs to specific checklist_item_ids.
        item_ids_recognised   = [i for i in must_item_ids if i in recognised_ids]
        item_ids_unrecognised = [i for i in must_item_ids if i not in recognised_ids]
        satisfied          = len(items_unrecognised) == 0

        fresh, freshness_reason = self._check_freshness(
            freshness_days     = leaf.freshness_days,
            latest_uploaded_at = latest_uploaded_at,
            have_any_artifact  = latest_uploaded_at is not None,
        )

        reason = self._build_reason(satisfied, fresh, items_recognised, items_unrecognised, freshness_reason)

        return LeafVerdict(
            leaf_id            = leaf.leaf_id,
            role               = "",
            evidence_type      = leaf.evidence_type,
            satisfied          = satisfied,
            fresh              = fresh,
            reason             = reason,
            items_recognised   = items_recognised,
            items_unrecognised = items_unrecognised,
            item_ids_recognised   = item_ids_recognised,
            item_ids_unrecognised = item_ids_unrecognised,
        )

    # ── Neo4j: fetch MUST checklist items for a leaf ──────────────────────────

    def _fetch_must_items(self, leaf_id: str) -> list[tuple[str, str]]:
        """Returns [(item_id, item_text), ...] for the leaf's MUST_CONTAIN items."""
        with self._neo4j.session() as s:
            result = s.run("""
                MATCH (er:EvidenceRequirement {id: $leaf_id})-[:MUST_CONTAIN]->(item:ChecklistItem)
                RETURN item.id AS id, item.text AS text
                ORDER BY item.id
            """, leaf_id=leaf_id)
            return [(row["id"], row["text"]) for row in result]

    # ── Postgres: recognised items + latest upload date ──────────────────────

    def _fetch_recognised_items(
        self,
        evidence_type: str,
        must_item_ids: list[str],
        control_ref:   str,
        standard_id:   str,
    ) -> tuple[set[str], datetime | None]:
        """Returns (set of recognised item_ids, latest matching upload datetime).

        Per-MUST recognition: a leaf MUST is recognised only when an approved,
        active finding is bound to its checklist_item_id with status='present'.
        The earlier Phase-1 fallback — coarse (control_ref, evidence_type)
        match that called ALL of a leaf's MUSTs satisfied when any doc of the
        right type existed — was retired 2026-06-13 after it was found to
        systematically overstate coverage and mask per-MUST gaps that
        workbook intake / leaf-scan / doc curation later exposed (see
        [[feedback-phase-1-fallback-masks-gaps]]).

        Findings without checklist_item_id no longer feed the engine. The
        intake paths (workbook YAML, doc curation, leaf-scan back-binding)
        are responsible for setting checklist_item_id; LLM-extracted findings
        carry it natively when the extractor is given the per-MUST candidate
        list.

        `evidence_type` and `control_ref` remain in the signature for caller
        symmetry but are unused.

        RLS-scoped via set_config; querying as arioncomply_app means we MUST
        set app.tenant_id, even though we also filter by tenant_id explicitly.
        """
        if not must_item_ids:
            return set(), None

        with self._pg.cursor() as cur:
            cur.execute(
                "SELECT set_config('app.tenant_id', %s, TRUE)",
                (self._tenant_id,),
            )

            # Per-checklist-item findings. df.review_status='approved'
            # enforces the HITL Stage-1 gate (commit 4): findings that
            # haven't been user-approved don't feed the engine.
            #
            # No cd.evidence_type filter: checklist_item_id is leaf-scoped —
            # every item id is bound to exactly one leaf, so any approved
            # per-item finding by definition belongs to that leaf regardless
            # of how the source document is tagged. With workbook intake,
            # one source document legitimately satisfies many leaves of
            # different evidence_types (one .xlsm feeds asset_register /
            # register / risk_register / revocation_record leaves
            # simultaneously).
            cur.execute("""
                SELECT df.checklist_item_id,
                       cd.uploaded_at
                FROM document_findings df
                JOIN client_documents cd
                  ON cd.id = df.document_id
                WHERE cd.tenant_id        = %s
                  AND cd.is_active        = TRUE
                  AND cd.is_current       = TRUE
                  AND df.checklist_item_id = ANY(%s)
                  AND df.status           = 'present'
                  AND df.is_active        = TRUE
                  AND df.review_status    = 'approved'
            """, (self._tenant_id, list(must_item_ids)))
            per_item_rows = cur.fetchall()

            if not per_item_rows:
                return set(), None

            recognised: set[str] = set()
            latest: datetime | None = None
            for item_id, uploaded_at in per_item_rows:
                recognised.add(item_id)
                if uploaded_at is not None and (latest is None or uploaded_at > latest):
                    latest = uploaded_at
            return recognised, latest

    # ── Freshness check ──────────────────────────────────────────────────────

    def _check_freshness(
        self,
        freshness_days:     int | None,
        latest_uploaded_at: datetime | None,
        have_any_artifact:  bool,
    ) -> tuple[bool, str]:
        """No freshness_days set ⇒ always fresh.
        No matching artifact at all ⇒ vacuously fresh (the gap is satisfied=False,
        not staleness; the gap-list builder distinguishes the two)."""
        if freshness_days is None or not have_any_artifact:
            return True, ""
        cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)
        if latest_uploaded_at is None:
            return True, ""
        if latest_uploaded_at >= cutoff:
            return True, ""
        return False, f"latest matching artifact older than {freshness_days} days"

    # ── Reason string ────────────────────────────────────────────────────────

    @staticmethod
    def _build_reason(
        satisfied:          bool,
        fresh:              bool,
        items_recognised:   Iterable[str],
        items_unrecognised: Iterable[str],
        freshness_reason:   str,
    ) -> str:
        nrec = len(list(items_recognised))
        nunrec = len(list(items_unrecognised))
        total = nrec + nunrec
        if satisfied and fresh:
            return f"all {total} MUST items recognised in current evidence"
        if not satisfied and fresh:
            return f"{nrec}/{total} MUST items recognised; {nunrec} unrecognised"
        if satisfied and not fresh:
            return f"all {total} MUST items recognised but {freshness_reason}"
        return f"{nrec}/{total} MUST items recognised; {freshness_reason}"


# Backwards-compat alias for the commit-3 tests
PolicyLeafEvaluator = GenericLeafEvaluator
