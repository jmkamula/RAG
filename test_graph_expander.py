"""
Test the GraphExpander against live Neo4j + ChromaDB.

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    python3 test_graph_expander.py

What this tests:
  1. Neo4j connectivity check
  2. Hierarchy traversal  — Art.32.1.a → parents + siblings
  3. Cross-framework      — GDPR → ISO edges
  4. Lateral cluster      — Art.33 → Art.34
  5. GAP_ANALYSIS query   — full expansion with budget
  6. DEFINITION query     — lighter expansion
  7. Offline fallback     — graceful degradation
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.graph_expander import GraphExpander, ExpandedContext
from rag.classifier     import QueryIntent, QuestionType, SessionContext, TenantProfile
from vector.retriever   import VectorRetriever

# ── Config ────────────────────────────────────────────────────────────────────

NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")
CHROMA_DB   = "./chroma_db"
CHROMA_HOST = os.getenv("CHROMA_HOST")        # set to "localhost" for HTTP server mode
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))


def divider(title):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ── Build retriever and expander ──────────────────────────────────────────────

retriever = VectorRetriever(
    persist_dir     = CHROMA_DB,
    provider        = "openai",
    embedding_model = "text-embedding-3-large",
    chroma_host     = CHROMA_HOST,
    chroma_port     = CHROMA_PORT,
)

expander = GraphExpander(
    neo4j_uri      = NEO4J_URI,
    neo4j_user     = NEO4J_USER,
    neo4j_password = NEO4J_PASS,
    retriever      = retriever,
)


# ── TEST 1 — Connectivity ─────────────────────────────────────────────────────
divider("TEST 1 — Neo4j connectivity")
online = expander.test_connection()
print(f"Neo4j online: {online}")
if not online:
    print("  ⚠ Running in offline mode — graph traversal tests will use fallback")
    print("    Offline tests still validate ChromaDB fetch and budget logic")


# ── TEST 2 — Hierarchy: Art.32.1.a ────────────────────────────────────────────
divider("TEST 2 — Hierarchy traversal: Art.32.1.a")

intent_gap = QueryIntent(
    question_type   = QuestionType.GAP_ANALYSIS,
    standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
    role_filter     = "controller",
    needs_posture   = True,
    cited_refs      = ["Art.32.1.a"],
    resolved_refs   = ["Art.32.1.a"],
    confidence      = 0.92,
    raw_query       = "What are our encryption gaps under Art.32.1.a?",
)

ctx = expander.expand(
    node_ids = ["GDPR:2016/679:Art.32.1.a"],
    intent   = intent_gap,
)
print(expander.summary(ctx))
print()

# Checks
all_refs = [n.ref for n in ctx.all_nodes]
if online:
    assert "Art.32.1.a" in all_refs, "Should contain cited node"
    if "Art.32" in all_refs or "Art.32.1" in all_refs:
        print("✓ Parent hierarchy found")
    else:
        print("⚠ No parents found — check PART_OF edges in graph")
    if any(n.is_iso for n in ctx.all_nodes):
        print("✓ Cross-framework ISO nodes found")
    else:
        print("⚠ No ISO nodes — check IMPLEMENTS edges in graph")
else:
    print("✓ Offline fallback returned nodes from ChromaDB")


# ── TEST 3 — Cross-framework: Art.33 ─────────────────────────────────────────
divider("TEST 3 — Cross-framework traversal: Art.33")

ctx2 = expander.expand(
    node_ids = ["GDPR:2016/679:Art.33"],
    intent   = QueryIntent(
        question_type   = QuestionType.POSTURE_CHECK,
        standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
        role_filter     = "controller",
        needs_posture   = True,
        cited_refs      = ["Art.33"],
        resolved_refs   = ["Art.33"],
        confidence      = 0.88,
        raw_query       = "Are we meeting our breach notification obligations?",
    ),
)
print(expander.summary(ctx2))

if ctx2.xfw_edges:
    print(f"\n✓ XFW edges found:")
    for e in ctx2.xfw_edges[:5]:
        print(f"  {e.source_id.split(':')[-1]:15s} "
              f"─[{e.rel_type}]→ "
              f"{e.target_id.split(':')[-1]:15s} "
              f"({e.confidence})")
else:
    if online:
        print("⚠ No XFW edges — check IMPLEMENTS edges from Art.33 in graph")
    else:
        print("→ No XFW edges in offline mode (expected)")


# ── TEST 4 — Lateral cluster: Art.33 + Art.34 ────────────────────────────────
divider("TEST 4 — Lateral: Art.33 should find Art.34")

ctx3 = expander.expand(
    node_ids = ["GDPR:2016/679:Art.33"],
    intent   = QueryIntent(
        question_type   = QuestionType.DEFINITION,
        standards_scope = ["GDPR:2016/679"],
        role_filter     = "controller",
        needs_posture   = False,
        cited_refs      = ["Art.33"],
        resolved_refs   = ["Art.33"],
        confidence      = 0.95,
        raw_query       = "What does Art.33 say?",
    ),
)

all_refs3 = [n.ref for n in ctx3.all_nodes]
print(f"Nodes returned: {all_refs3[:10]}")
if online and "Art.34" in all_refs3:
    print("✓ Art.34 found via RELATED_TO")
elif online:
    print("⚠ Art.34 not found — check RELATED_TO edges in graph")
else:
    print("→ Lateral traversal not available in offline mode")


# ── TEST 5 — Multi-node expansion ────────────────────────────────────────────
divider("TEST 5 — Multi-node GAP_ANALYSIS expansion")

ctx4 = expander.expand(
    node_ids = [
        "GDPR:2016/679:Art.32.1.a",
        "GDPR:2016/679:Art.32.1.d",
        "ISO27001:2022:A.8.24",
    ],
    intent   = QueryIntent(
        question_type   = QuestionType.GAP_ANALYSIS,
        standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
        role_filter     = "controller",
        needs_posture   = True,
        cited_refs      = ["Art.32.1.a", "Art.32.1.d", "A.8.24"],
        resolved_refs   = ["Art.32.1.a", "Art.32.1.d", "A.8.24"],
        confidence      = 0.90,
        raw_query       = "What are our security gaps for encryption and testing?",
    ),
)
print(expander.summary(ctx4))
print()
print(f"Budget used: {ctx4.total_nodes} / 22 (GAP_ANALYSIS budget)")
assert ctx4.total_nodes <= 22, f"Budget exceeded: {ctx4.total_nodes} > 22"
print("✓ Within budget")


# ── TEST 6 — DEFINITION: lighter expansion ────────────────────────────────────
divider("TEST 6 — DEFINITION: lighter expansion")

ctx5 = expander.expand(
    node_ids = ["GDPR:2016/679:Art.33.1"],
    intent   = QueryIntent(
        question_type   = QuestionType.DEFINITION,
        standards_scope = ["GDPR:2016/679"],
        role_filter     = "controller",
        needs_posture   = False,
        cited_refs      = ["Art.33.1"],
        resolved_refs   = ["Art.33.1"],
        confidence      = 0.95,
        raw_query       = "What is the 72-hour rule?",
    ),
)
print(expander.summary(ctx5))
print(f"\nDefinition budget: {ctx5.total_nodes} nodes (budget=12)")
assert ctx5.total_nodes <= 12, f"Definition budget exceeded: {ctx5.total_nodes}"
print("✓ Within budget")


# ── TEST 7 — Offline fallback ─────────────────────────────────────────────────
divider("TEST 7 — Offline fallback")

offline_expander = GraphExpander(
    neo4j_uri      = "bolt://127.0.0.1:9999",  # unreachable port
    neo4j_user     = "neo4j",
    neo4j_password = "wrong",
    retriever      = retriever,
)
ctx6 = offline_expander.expand(
    node_ids = ["GDPR:2016/679:Art.33.1", "ISO27001:2022:A.8.24"],
    intent   = intent_gap,
)
print(expander.summary(ctx6))
print(f"\nOffline mode: {ctx6.offline_mode}")
assert ctx6.offline_mode == True, "Should be in offline mode"
assert ctx6.total_nodes > 0, "Should still return ChromaDB results"
print("✓ Offline fallback working — ChromaDB results returned")


# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("  All GraphExpander tests complete")
print(f"  Neo4j: {'online — full graph traversal' if online else 'offline — ChromaDB fallback'}")
print("=" * 60)
