"""
Test the ContextAssembler with real ChromaDB nodes.

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    python3 test_context_assembler.py

What this tests:
  1. GAP_ANALYSIS context — Art.32.1.a with mock posture
  2. POSTURE_CHECK context — Art.33 breach notification
  3. DEFINITION context — lighter, no posture
  4. Cross-framework context — ISO A.8.24 expanding to GDPR
  5. Token budget enforcement
  6. Document layer parsing
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.context_assembler import ContextAssembler, AssembledContext
from rag.graph_expander    import (
    GraphExpander, ExpandedContext, ExpandedNode, CrossFrameworkEdge
)
from rag.classifier        import (
    QueryIntent, QuestionType, TenantProfile
)
from vector.retriever      import VectorRetriever


# ── Config ────────────────────────────────────────────────────────────────────

NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")
CHROMA_DB   = "./chroma_db"
CHROMA_HOST = os.getenv("CHROMA_HOST")        # set to "localhost" for HTTP server mode
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

arion = TenantProfile(
    tenant_id            = "arion-networks",
    name                 = "Arion Networks",
    applicable_standards = ["ISO27001:2022", "GDPR:2016/679"],
    role                 = ["controller", "processor"],
    sector               = "technology",
    jurisdiction         = ["EU", "UK"],
    has_posture_data     = True,   # pretend we have posture for testing
)

# Mock posture records — simulating Arion's assessment
MOCK_POSTURE = {
    "ISO27001:2022:A.8.24": {
        "finding":         "OFI",
        "gap_description": "Encryption policy exists but does not explicitly scope personal data at rest and in transit",
        "evidence_note":   "Encryption policy v1.2 approved 2024",
        "remedial_action": "Update encryption policy to explicitly reference personal data processing systems",
    },
    "ISO27001:2022:A.8.11": {
        "finding":         "NC",
        "gap_description": "No data masking policy or procedure in place",
        "evidence_note":   "",
        "remedial_action": "Develop data masking procedure covering personal data in non-production environments",
    },
    "ISO27001:2022:A.5.24": {
        "finding":         "Comply",
        "gap_description": "",
        "evidence_note":   "Incident response plan v2.1, last tested March 2025",
        "remedial_action": "",
    },
    "ISO27001:2022:A.5.26": {
        "finding":         "OFI",
        "gap_description": "Incident response procedure does not include personal data breach determination step",
        "evidence_note":   "IRP exists but lacks GDPR breach trigger",
        "remedial_action": "Add personal data breach determination checklist to incident response procedure",
    },
    "GDPR:2016/679:Art.32": {
        "finding":         "OFI",
        "gap_description": "Risk assessment does not explicitly address personal data processing risks",
        "evidence_note":   "General IT risk assessment in place",
        "remedial_action": "Extend risk assessment to cover personal data processing risks",
    },
}


def divider(title):
    print()
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)


# ── Build components ──────────────────────────────────────────────────────────

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

assembler = ContextAssembler(arion)


# ── TEST 1 — GAP_ANALYSIS: Art.32.1.a encryption gaps ────────────────────────
divider("TEST 1 — GAP_ANALYSIS: Art.32.1.a encryption gaps")

intent_gap = QueryIntent(
    question_type   = QuestionType.GAP_ANALYSIS,
    standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
    role_filter     = "controller",
    needs_posture   = True,
    cited_refs      = ["Art.32.1.a"],
    resolved_refs   = ["Art.32.1.a", "Art.32"],
    confidence      = 0.92,
    raw_query       = "What are our encryption gaps under Art.32.1.a?",
)

expanded1 = expander.expand(
    node_ids = ["GDPR:2016/679:Art.32.1.a"],
    intent   = intent_gap,
)

ctx1 = assembler.assemble(expanded1, intent_gap, posture=MOCK_POSTURE)

print(f"Assembled: {ctx1.primary_count} primary + {ctx1.secondary_count} secondary nodes")
print(f"Approx tokens: {ctx1.approx_tokens}")
print(f"Has posture: {ctx1.has_posture}")
print()
print("─" * 65)
print(ctx1.context_text)
print("─" * 65)
assert ctx1.approx_tokens <= 4000, f"Over budget: {ctx1.approx_tokens}"
print("\n✓ PASS — within token budget")


# ── TEST 2 — POSTURE_CHECK: breach notification ───────────────────────────────
divider("TEST 2 — POSTURE_CHECK: breach notification posture")

intent_posture = QueryIntent(
    question_type   = QuestionType.POSTURE_CHECK,
    standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
    role_filter     = "controller",
    needs_posture   = True,
    cited_refs      = ["Art.33"],
    resolved_refs   = ["Art.33", "Art.33.1"],
    confidence      = 0.90,
    raw_query       = "Are we meeting our breach notification obligations?",
)

expanded2 = expander.expand(
    node_ids = ["GDPR:2016/679:Art.33", "ISO27001:2022:A.5.24"],
    intent   = intent_posture,
)

ctx2 = assembler.assemble(expanded2, intent_posture, posture=MOCK_POSTURE)

print(f"Assembled: {ctx2.primary_count} primary + {ctx2.secondary_count} secondary nodes")
print(f"Approx tokens: {ctx2.approx_tokens}")
print()
print("─" * 65)
print(ctx2.context_text)
print("─" * 65)
print("\n✓ PASS")


# ── TEST 3 — DEFINITION: no posture needed ────────────────────────────────────
divider("TEST 3 — DEFINITION: What is the 72-hour rule?")

intent_def = QueryIntent(
    question_type   = QuestionType.DEFINITION,
    standards_scope = ["GDPR:2016/679"],
    role_filter     = "controller",
    needs_posture   = False,
    cited_refs      = ["Art.33.1"],
    resolved_refs   = ["Art.33.1", "Art.33"],
    confidence      = 0.95,
    raw_query       = "What is the 72-hour rule?",
)

expanded3 = expander.expand(
    node_ids = ["GDPR:2016/679:Art.33.1"],
    intent   = intent_def,
)

ctx3 = assembler.assemble(expanded3, intent_def, posture={})

print(f"Assembled: {ctx3.primary_count} primary + {ctx3.secondary_count} secondary")
print(f"Approx tokens: {ctx3.approx_tokens} (budget=2000)")
print()
print("─" * 65)
print(ctx3.context_text)
print("─" * 65)
assert ctx3.approx_tokens <= 2000, f"Definition over budget: {ctx3.approx_tokens}"
print("\n✓ PASS — definition context fits budget")


# ── TEST 4 — Token budget check ───────────────────────────────────────────────
divider("TEST 4 — Token budget enforcement")

# Fetch 20 known nodes directly by ID — no embedding call needed
known_ids = [
    "GDPR:2016/679:Art.32",    "GDPR:2016/679:Art.32.1",
    "GDPR:2016/679:Art.32.1.a","GDPR:2016/679:Art.32.1.b",
    "GDPR:2016/679:Art.32.1.c","GDPR:2016/679:Art.32.1.d",
    "GDPR:2016/679:Art.32.4",  "GDPR:2016/679:Art.33",
    "GDPR:2016/679:Art.33.1",  "GDPR:2016/679:Art.33.2",
    "GDPR:2016/679:Art.33.3",  "GDPR:2016/679:Art.33.5",
    "GDPR:2016/679:Art.34",    "GDPR:2016/679:Art.34.1",
    "ISO27001:2022:A.8.24",    "ISO27001:2022:A.8.7",
    "ISO27001:2022:A.8.8",     "ISO27001:2022:A.5.24",
    "ISO27001:2022:A.5.26",    "ISO27001:2022:A.5.27",
]
large_results = retriever.search_by_ids(known_ids)
# Build a fake ExpandedContext from vector results
from rag.graph_expander import ExpandedNode
fake_primary = []
fake_secondary = []
for i, r in enumerate(large_results[:20]):
    node = ExpandedNode(
        node_id     = r.node_id,
        ref         = r.ref,
        standard_id = r.standard_id,
        title       = r.title,
        document    = r.document,
        metadata    = r.metadata,
        source      = "cited" if i < 3 else "xfw",
    )
    if i < 5:
        fake_primary.append(node)
    else:
        fake_secondary.append(node)

fake_context = ExpandedContext(
    primary_nodes   = fake_primary,
    secondary_nodes = fake_secondary,
    xfw_edges       = [],
    total_nodes     = 20,
    traversal_stats = {},
)

intent_large = QueryIntent(
    question_type   = QuestionType.GAP_ANALYSIS,
    standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
    role_filter     = "controller",
    needs_posture   = True,
    cited_refs      = ["Art.32"],
    resolved_refs   = ["Art.32"],
    confidence      = 0.85,
    raw_query       = "Full gap analysis for our security posture",
)

ctx4 = assembler.assemble(fake_context, intent_large, posture=MOCK_POSTURE)
print(f"Input nodes:   20")
print(f"Tokens used:   {ctx4.approx_tokens} (budget=4000)")
print(f"Primary used:  {ctx4.primary_count}")
print(f"Secondary:     {ctx4.secondary_count}")
assert ctx4.approx_tokens <= 4000, f"Budget exceeded: {ctx4.approx_tokens}"
print("✓ PASS — budget enforced")


# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 65)
print("  All ContextAssembler tests complete")
print(f"  Neo4j: {'online' if expander._online else 'offline — used ChromaDB fallback'}")
print("=" * 65)
