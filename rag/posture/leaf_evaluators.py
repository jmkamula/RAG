"""ArionComply — per-evidence-type leaf evaluators.

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

This module ships the policy evaluator (commit 3). Per-type evaluators for
the other 23 evidence_types arrive as needed. The shared shape (the
LeafEvaluatorFn signature) means the engine doesn't care which evaluator
runs for which leaf — wiring at commit 4 builds a dispatch table by
evidence_type.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from rag.posture.applies_when import EvalContext
from rag.posture.fulfilment_engine import LeafSpec, LeafVerdict


class PolicyLeafEvaluator:
    """Evaluator for evidence_type='policy' leaves.

    Bound to a (pg_conn, neo4j_driver, tenant_id) triple at construction;
    call the instance with (leaf, eval_ctx) to get a LeafVerdict.
    """

    def __init__(self, pg_conn, neo4j_driver, tenant_id: str):
        self._pg        = pg_conn
        self._neo4j     = neo4j_driver
        self._tenant_id = tenant_id

    def __call__(self, leaf: LeafSpec, ctx: EvalContext) -> LeafVerdict:
        if leaf.evidence_type != "policy":
            return LeafVerdict(
                leaf_id            = leaf.leaf_id,
                role               = "",
                evidence_type      = leaf.evidence_type,
                satisfied          = False,
                fresh              = False,
                reason             = f"this evaluator handles 'policy' only; got {leaf.evidence_type!r}",
                items_unrecognised = list(leaf.must_items),
            )

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

        # 2. Postgres: which items are 'present' for current policy artifacts?
        recognised_ids, latest_uploaded_at = self._fetch_recognised_items(
            evidence_type   = "policy",
            must_item_ids   = must_item_ids,
        )

        # 3. Determine satisfied + freshness
        items_recognised   = [must_item_texts[i] for i in must_item_ids if i in recognised_ids]
        items_unrecognised = [must_item_texts[i] for i in must_item_ids if i not in recognised_ids]
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
    ) -> tuple[set[str], datetime | None]:
        """Returns (set of recognised item_ids, latest matching upload datetime).

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
            cur.execute("""
                SELECT df.checklist_item_id,
                       cd.uploaded_at
                FROM document_findings df
                JOIN client_documents cd
                  ON cd.id = df.document_id
                WHERE cd.tenant_id        = %s
                  AND cd.evidence_type    = %s
                  AND cd.is_active        = TRUE
                  AND cd.is_current       = TRUE
                  AND df.checklist_item_id = ANY(%s)
                  AND df.status           = 'present'
                  AND df.is_active        = TRUE
            """, (self._tenant_id, evidence_type, list(must_item_ids)))
            rows = cur.fetchall()

        recognised: set[str] = set()
        latest_uploaded_at: datetime | None = None
        for item_id, uploaded_at in rows:
            recognised.add(item_id)
            if uploaded_at is not None:
                if latest_uploaded_at is None or uploaded_at > latest_uploaded_at:
                    latest_uploaded_at = uploaded_at
        return recognised, latest_uploaded_at

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
