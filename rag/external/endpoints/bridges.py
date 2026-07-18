"""
Cross-framework bridge endpoint —
    GET /api/external/v1/bridges?control_ref=X&standard_id=Y

Ship 4'.f — external systems can query the framework graph
directly for cross-framework relationships. Useful for:

  * Compliance-platform integrations building their own
    cross-mapping views ("what does A.5.18 satisfy in GDPR?")
  * Reverse lookups ("what ISO controls implement Art.32?")
  * Cross-standard evidence rollups (evidence for A.5.18 also
    counts for its GDPR bridges)

Bridges are PURE metadata about the framework graph — no tenant
state. But we still gate this behind `external:xfw:read` scope so
partner permissions can be granular.

Data comes from Neo4j RequirementNode graph:
  * `IMPLEMENTS`  — hardest bridge (this control implements that)
  * `SUPPORTS`    — supports/partially satisfies
  * `ENABLES`     — makes possible
  * `GOVERNANCE`  — governance-level relationship

Outbound edges: (self) → other framework's control
Inbound edges:  other framework's control → (self)
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from rag.external.auth import external_key_with_scope

logger = logging.getLogger(__name__)

router = APIRouter()


_ALLOWED_RELS = ("IMPLEMENTS", "SUPPORTS", "ENABLES", "GOVERNANCE")


class Bridge(BaseModel):
    id:          str            = Field(..., description="Neo4j node id, e.g. `ISO27001:2022:A.5.18`.")
    ref:         Optional[str]  = Field(None, description="Bare control ref, e.g. `A.5.18`.")
    standard_id: Optional[str]  = Field(None, description="Framework id.")
    title:       Optional[str]  = Field(None, description="Control title.")
    rel:         str            = Field(..., description="Relationship type: `IMPLEMENTS` / `SUPPORTS` / `ENABLES` / `GOVERNANCE`.")


class BridgesResponse(BaseModel):
    source_id:   str        = Field(..., description="Neo4j node id we queried, e.g. `ISO27001:2022:A.5.18`.")
    control_ref: str
    standard_id: str
    outbound:    list[Bridge] = Field(..., description="Edges FROM this control TO other controls.")
    inbound:     list[Bridge] = Field(..., description="Edges FROM other controls TO this control.")


def _neo_driver():
    """Lazy-load the Neo4j driver from env vars. Keeps this module
    importable even when Neo4j is unreachable at test time —
    endpoints will just return 503 in that case."""
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI",      "bolt://127.0.0.1:7687")
    user = os.getenv("NEO4J_USER",     "neo4j")
    pwd  = os.getenv("NEO4J_PASSWORD", "")
    return GraphDatabase.driver(uri, auth=(user, pwd))


_CYPHER = """
MATCH (n:RequirementNode {id: $node_id})

OPTIONAL MATCH (n)-[r_out:IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE]->(xfw_out:RequirementNode)
WITH n,
     collect(DISTINCT {
        id:          xfw_out.id,
        ref:         xfw_out.ref,
        standard_id: xfw_out.standard_id,
        title:       xfw_out.title,
        rel:         type(r_out)
     }) AS outbound

OPTIONAL MATCH (n)<-[r_in:IMPLEMENTS|SUPPORTS|ENABLES|GOVERNANCE]-(xfw_in:RequirementNode)
RETURN
    n.id AS source_id,
    outbound,
    collect(DISTINCT {
        id:          xfw_in.id,
        ref:         xfw_in.ref,
        standard_id: xfw_in.standard_id,
        title:       xfw_in.title,
        rel:         type(r_in)
    }) AS inbound
"""


@router.get("/bridges",
            response_model = BridgesResponse,
            summary        = "Cross-framework bridges for a control")
async def get_bridges(
    request:     Request,
    key          = Depends(external_key_with_scope("external:xfw:read")),
    control_ref: str = Query(..., description="Control ref, e.g. `A.5.18`."),
    standard_id: str = Query(..., description="Framework id, e.g. `ISO27001:2022`."),
):
    """Return outbound + inbound cross-framework edges for a control.
    Reads directly from the framework graph in Neo4j.

    Returns 404 if the control doesn't exist in the graph."""
    node_id = f"{standard_id}:{control_ref}"

    try:
        driver = _neo_driver()
    except Exception as e:
        logger.warning("Neo4j driver init failed: %s", e)
        raise HTTPException(
            status_code = 503,
            detail      = "Framework graph unavailable. Please try again in a moment.",
        )

    try:
        with driver.session() as session:
            try:
                result = session.run(_CYPHER, node_id=node_id).single()
            except Exception as e:
                logger.warning("Neo4j bridges query failed for %r: %s", node_id, e)
                raise HTTPException(
                    status_code = 503,
                    detail      = "Framework graph query failed. Please try again in a moment.",
                )
    finally:
        try: driver.close()
        except Exception: pass

    if result is None:
        raise HTTPException(
            status_code = 404,
            detail      = f"No control {node_id!r} in the framework graph.",
        )

    def _clean(items):
        # collect(DISTINCT ...) may emit a row with null fields when
        # the OPTIONAL MATCH had no matches — filter those out.
        out = []
        for it in items or []:
            if not it or not it.get("id") or not it.get("rel"):
                continue
            out.append(Bridge(
                id          = it["id"],
                ref         = it.get("ref"),
                standard_id = it.get("standard_id"),
                title       = it.get("title"),
                rel         = it["rel"],
            ))
        return out

    return BridgesResponse(
        source_id   = result["source_id"] or node_id,
        control_ref = control_ref,
        standard_id = standard_id,
        outbound    = _clean(result["outbound"]),
        inbound     = _clean(result["inbound"]),
    )
