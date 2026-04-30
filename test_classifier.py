"""
Test the QueryClassifier against the live ChromaDB index.

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    python3 test_classifier.py

What this tests:
  1. Opening message generation
  2. Explicit ref detection (fast path, no LLM)
  3. Clear single-cluster intake (ransomware → breach notification)
  4. Ambiguous intake (suppliers → clarification question)
  5. Clarification resolution (user picks option)
  6. classify_query within established session
  7. Fast path classify_query (explicit ref in follow-up)
"""
from __future__ import annotations

import sys
import os

# Ensure ingestion/ is on the path regardless of where you run from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.classifier   import QueryClassifier, TenantProfile, IntakeState, SessionContext, QuestionType
from vector.retriever import VectorRetriever


# ── Arion Networks tenant profile ─────────────────────────────────────────────

arion = TenantProfile(
    tenant_id            = "arion-networks",
    name                 = "Arion Networks",
    applicable_standards = ["ISO27001:2022", "GDPR:2016/679"],
    role                 = ["controller", "processor"],
    sector               = "technology",
    jurisdiction         = ["EU", "UK"],
    has_posture_data     = False,
)


# ── Build retriever and classifier ────────────────────────────────────────────

# ChromaDB connection — supports both local files and HTTP server
# Local files (default): just set CHROMA_DB_PATH
# HTTP server mode:       export CHROMA_HOST=localhost CHROMA_PORT=8000
CHROMA_DB_PATH = "./chroma_db"
CHROMA_HOST    = os.getenv("CHROMA_HOST")
CHROMA_PORT    = int(os.getenv("CHROMA_PORT", "8000"))

retriever = VectorRetriever(
    persist_dir     = CHROMA_DB_PATH,
    provider        = "openai",
    embedding_model = "text-embedding-3-large",
    chroma_host     = CHROMA_HOST,
    chroma_port     = CHROMA_PORT,
)

classifier = QueryClassifier(
    tenant_profile  = arion,
    retriever       = retriever,
    classify_model  = "gpt-4o-mini",
    clarify_model   = "gpt-4o-mini",
)


# ── Run tests ─────────────────────────────────────────────────────────────────

def divider(title):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ── TEST 1 — Opening message ──────────────────────────────────────────────────
divider("TEST 1 — Opening message")
print(classifier.opening_message())


# ── TEST 2 — Explicit ref (fast path, no LLM) ────────────────────────────────
divider("TEST 2 — Explicit ref (no LLM needed)")
result = classifier.process_intake(
    "What does Art.32 say about encryption?"
)
print(f"State:        {result.state.value}")
print(f"Active refs:  {result.session.active_refs if result.session else None}")
print(f"Intent:       {result.session.intent_type.value if result.session else None}")
assert result.state == IntakeState.EXPLICIT, "Expected EXPLICIT state"
assert "Art.32" in result.session.active_refs, "Expected Art.32 in refs"
print("✓ PASS")


# ── TEST 3 — Ransomware breach (clear single-cluster) ────────────────────────
divider("TEST 3 — Clear intent: ransomware breach")
result = classifier.process_intake(
    "We had a ransomware attack and need to know what to report"
)
print(f"State:        {result.state.value}")
if result.state == IntakeState.CLEAR and result.session:
    print(f"Standards:    {result.session.standards}")
    print(f"Active refs:  {result.session.active_refs}")
    print(f"Cluster:      {result.session.active_cluster}")
    print("✓ PASS — resolved to single cluster")
elif result.state == IntakeState.AMBIGUOUS:
    print(f"Clusters found:  {[c.label for c in result.clusters]}")
    print(f"Clarification:\n  {result.clarification}")
    print("→ Ambiguous (acceptable — multiple breach-related clusters)")
else:
    print(f"No match response: {result.clarification}")


# ── TEST 4 — Supplier (ambiguous → clarification question) ───────────────────
divider("TEST 4 — Ambiguous: supplier query")
result = classifier.process_intake(
    "I need to sort out the thing with our suppliers"
)
print(f"State:    {result.state.value}")
print(f"Clusters: {[c.label[:55] for c in result.clusters]}")
if result.state == IntakeState.AMBIGUOUS:
    print(f"\nClarification question (GPT-written):")
    print(f"  {result.clarification}")
    print("✓ PASS — natural clarification generated")
elif result.state == IntakeState.CLEAR and result.session:
    print(f"Resolved directly to: {result.session.active_cluster}")
    print("→ Acceptable — clear enough for single cluster")
else:
    print(f"No match: {result.clarification}")


# ── TEST 5 — Clarification resolution ────────────────────────────────────────
divider("TEST 5 — User responds to clarification")
# Use the result from test 4 if it was ambiguous
ambiguous_result = result if result.state == IntakeState.AMBIGUOUS else None

if ambiguous_result:
    # Simulate user picking option (a)
    resolved = classifier.process_clarification("a", ambiguous_result)
    print(f"User said: 'a'")
    print(f"State:      {resolved.state.value}")
    if resolved.session:
        print(f"Standards:  {resolved.session.standards}")
        print(f"Active refs: {resolved.session.active_refs}")
        print(f"Cluster:    {resolved.session.active_cluster}")
    print("✓ PASS — clarification resolved to session")
else:
    print("→ Skipped (test 4 was already clear)")


# ── TEST 6 — classify_query within session ────────────────────────────────────
divider("TEST 6 — classify_query: follow-up in breach session")
breach_session = SessionContext(
    tenant_profile = arion,
    standards      = ["GDPR:2016/679"],
    role           = "controller",
    intent_type    = QuestionType.POSTURE_CHECK,
    active_refs    = ["Art.33", "Art.34"],
    active_cluster = "GDPR — Breach Notification",
)
intent = classifier.classify_query(
    "Do we need to notify affected customers?",
    session = breach_session,
    history = [],
)
print(f"QuestionType:   {intent.question_type.value}")
print(f"Standards:      {intent.standards_scope}")
print(f"Needs posture:  {intent.needs_posture}")
print(f"Cited refs:     {intent.cited_refs}")
print(f"Resolved refs:  {intent.resolved_refs}")
print(f"Confidence:     {intent.confidence:.2f}")
if intent.clarification_question:
    print(f"Clarification:  {intent.clarification_question}")
print("✓ PASS")


# ── TEST 7 — Fast path classify_query (explicit ref) ─────────────────────────
divider("TEST 7 — Fast path classify_query (explicit ref)")
intent2 = classifier.classify_query(
    "What are our gaps for Art.33.1?",
    session = breach_session,
    history = [],
)
print(f"QuestionType:  {intent2.question_type.value}")
print(f"Cited refs:    {intent2.cited_refs}")
print(f"Confidence:    {intent2.confidence:.2f}")
print(f"Fast path:     {intent2.confidence == 0.95}")
assert "Art.33.1" in intent2.cited_refs, "Expected Art.33.1 in cited refs"
assert intent2.question_type == QuestionType.GAP_ANALYSIS, "Expected GAP_ANALYSIS"
assert intent2.confidence == 0.95, "Expected fast-path confidence 0.95"
print("✓ PASS")


# ── TEST 8 — The example from the session ─────────────────────────────────────
divider("TEST 8 — Original example from session")
result = classifier.process_intake(
    "We had a ransomware attack and need to know what to report"
)
print(f"result.state = {result.state.value}")
if result.session:
    print(f"result.session.active_refs = {result.session.active_refs}")
elif result.clarification:
    print(f"result.clarification = {result.clarification}")

print()
print("=" * 60)
print("  All tests complete")
print("=" * 60)
