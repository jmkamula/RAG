"""
Test LLMAnswer end-to-end against the full RAG pipeline.

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    export CHROMA_HOST=localhost
    export NEO4J_PASSWORD=arionneo4j@2026
    python3 test_llm_answer.py

What this tests:
  1. GAP_ANALYSIS  — encryption gaps with posture data
  2. POSTURE_CHECK — breach notification posture
  3. DEFINITION    — 72-hour rule explanation
  4. IMPLEMENTATION — how to implement Art.25 privacy by design
  5. Verification pass — catches a deliberately wrong answer
"""
from __future__ import annotations

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.llm_answer        import LLMAnswer, ComplianceAnswer
from rag.context_assembler import ContextAssembler
from rag.graph_expander    import GraphExpander
from rag.classifier        import (
    QueryIntent, QuestionType, TenantProfile, SessionContext
)
from vector.retriever      import VectorRetriever

# ── Config ────────────────────────────────────────────────────────────────────

NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "arionneo4j@2026")
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

arion = TenantProfile(
    tenant_id            = "arion-networks",
    name                 = "Arion Networks",
    applicable_standards = ["ISO27001:2022", "GDPR:2016/679"],
    role                 = ["controller", "processor"],
    sector               = "technology",
    jurisdiction         = ["EU", "UK"],
    has_posture_data     = True,
)

# Mock posture — Arion Networks assessment
MOCK_POSTURE = {
    "ISO27001:2022:A.8.24": {
        "finding":         "OFI",
        "gap_description": "Encryption policy exists but does not explicitly "
                           "scope personal data at rest and in transit",
        "evidence_note":   "Encryption policy v1.2 approved 2024",
        "remedial_action": "Update encryption policy to explicitly reference "
                           "personal data processing systems",
    },
    "ISO27001:2022:A.8.11": {
        "finding":         "NC",
        "gap_description": "No data masking policy or procedure in place",
        "evidence_note":   "",
        "remedial_action": "Develop data masking procedure covering personal "
                           "data in non-production environments",
    },
    "ISO27001:2022:A.5.24": {
        "finding":         "Comply",
        "gap_description": "",
        "evidence_note":   "Incident response plan v2.1, last tested March 2025",
        "remedial_action": "",
    },
    "ISO27001:2022:A.5.26": {
        "finding":         "OFI",
        "gap_description": "Incident response procedure does not include "
                           "personal data breach determination step",
        "evidence_note":   "IRP exists but lacks GDPR breach trigger",
        "remedial_action": "Add personal data breach determination checklist "
                           "to incident response procedure",
    },
    "GDPR:2016/679:Art.32": {
        "finding":         "OFI",
        "gap_description": "Risk assessment does not explicitly address "
                           "personal data processing risks",
        "evidence_note":   "General IT risk assessment in place",
        "remedial_action": "Extend risk assessment to cover personal data "
                           "processing risks",
    },
}


def divider(title):
    print()
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)


def print_answer(answer: ComplianceAnswer):
    print(f"\nModel:    {answer.model_used}  ({answer.latency_ms}ms)")
    print(f"Verified: {'✓ pass' if answer.verified else '✗ fail'}", end="")
    if answer.was_corrected:
        print(f"  (corrected: {answer.correction_note[:60]})", end="")
    print()
    print(f"Refs:     {', '.join(answer.cited_refs[:8])}")
    print()
    print("─" * 65)
    print(answer.answer_text)
    print("─" * 65)
    if answer.verification and answer.verification.issues:
        print(f"\n⚠ Verification issues: {answer.verification.issues}")


# ── Build components ──────────────────────────────────────────────────────────

retriever = VectorRetriever(
    persist_dir     = "./chroma_db",
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
llm       = LLMAnswer(
    answer_model = "gpt-4o",
    verify_model = "gpt-4o-mini",
    verify       = True,
)


# ── TEST 1 — GAP_ANALYSIS: encryption ─────────────────────────────────────────
divider("TEST 1 — GAP_ANALYSIS: What are our encryption gaps?")

intent1 = QueryIntent(
    question_type   = QuestionType.GAP_ANALYSIS,
    standards_scope = ["GDPR:2016/679", "ISO27001:2022"],
    role_filter     = "controller",
    needs_posture   = True,
    cited_refs      = ["Art.32.1.a"],
    resolved_refs   = ["Art.32.1.a", "Art.32"],
    confidence      = 0.92,
    raw_query       = "What are our encryption gaps?",
)

expanded1  = expander.expand(["GDPR:2016/679:Art.32.1.a"], intent1)
context1   = assembler.assemble(expanded1, intent1, posture=MOCK_POSTURE)
answer1    = llm.answer("What are our encryption gaps?", context1)

print_answer(answer1)
print("\n✓ TEST 1 complete")


# ── TEST 2 — POSTURE_CHECK: breach notification ────────────────────────────────
divider("TEST 2 — POSTURE_CHECK: Are we meeting breach notification obligations?")

intent2 = QueryIntent(
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
    ["GDPR:2016/679:Art.33", "ISO27001:2022:A.5.24"],
    intent2
)
context2  = assembler.assemble(expanded2, intent2, posture=MOCK_POSTURE)
answer2   = llm.answer(
    "Are we meeting our breach notification obligations?", context2
)

print_answer(answer2)
print("\n✓ TEST 2 complete")


# ── TEST 3 — DEFINITION: 72-hour rule ────────────────────────────────────────
divider("TEST 3 — DEFINITION: What is the 72-hour rule?")

intent3 = QueryIntent(
    question_type   = QuestionType.DEFINITION,
    standards_scope = ["GDPR:2016/679"],
    role_filter     = "controller",
    needs_posture   = False,
    cited_refs      = ["Art.33.1"],
    resolved_refs   = ["Art.33.1", "Art.33"],
    confidence      = 0.95,
    raw_query       = "What is the 72-hour rule?",
)

expanded3 = expander.expand(["GDPR:2016/679:Art.33.1"], intent3)
context3  = assembler.assemble(expanded3, intent3, posture={})
answer3   = llm.answer("What is the 72-hour rule?", context3)

print_answer(answer3)
print("\n✓ TEST 3 complete")


# ── TEST 4 — IMPLEMENTATION: privacy by design ────────────────────────────────
divider("TEST 4 — IMPLEMENTATION: How do we implement privacy by design?")

intent4 = QueryIntent(
    question_type   = QuestionType.IMPLEMENTATION,
    standards_scope = ["GDPR:2016/679"],
    role_filter     = "controller",
    needs_posture   = False,
    cited_refs      = ["Art.25"],
    resolved_refs   = ["Art.25", "Art.25.1", "Art.25.2"],
    confidence      = 0.88,
    raw_query       = "How do we implement privacy by design for our new product?",
)

expanded4 = expander.expand(["GDPR:2016/679:Art.25"], intent4)
context4  = assembler.assemble(expanded4, intent4, posture={})
answer4   = llm.answer(
    "How do we implement privacy by design for our new product?", context4
)

print_answer(answer4)
print("\n✓ TEST 4 complete")


# ── TEST 5 — Verification catches wrong answer ────────────────────────────────
divider("TEST 5 — Verification: catches fabricated claim")

# Inject a deliberately wrong answer into the verification pass
from rag.context_assembler import AssembledContext
from rag.classifier import QueryIntent

fake_context = AssembledContext(
    context_text    = context3.context_text,  # real 72-hour rule context
    intent          = intent3,
    tenant_name     = "Arion Networks",
    question_type   = QuestionType.DEFINITION,
    node_ids_used   = [],
    has_posture     = False,
    posture_summary = {},
    primary_count   = 1,
    secondary_count = 0,
    approx_tokens   = 500,
)

# Deliberately wrong answer — says 48 hours instead of 72
wrong_answer = (
    "Under Art.33.1, you must notify the supervisory authority within "
    "48 hours of becoming aware of a personal data breach. This is "
    "mandatory with no exceptions."
)

print("Testing with deliberately wrong answer (48h instead of 72h):")
print(f"  Wrong answer: '{wrong_answer[:80]}...'")

verification = llm._verify(
    context_text = fake_context.context_text,
    answer_text  = wrong_answer,
)
print(f"\nVerification verdict: {verification.verdict}")
print(f"Confidence: {verification.confidence}")
if verification.issues:
    print(f"Issues found:")
    for issue in verification.issues:
        print(f"  - {issue}")
if verification.corrections:
    print(f"Corrections:")
    for corr in verification.corrections:
        print(f"  → {corr}")

assert verification.verdict == "fail", \
    "Verification should catch the 48h claim"
print("\n✓ TEST 5 — Verification correctly caught the fabricated claim")


# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 65)
print("  All LLMAnswer tests complete")
print(f"  Neo4j: {'online' if expander._online else 'offline'}")
print(f"  ChromaDB: {'HTTP server' if CHROMA_HOST else 'local files'}")
print("=" * 65)
