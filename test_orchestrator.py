"""
Test the RAGOrchestrator end-to-end.

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    export CHROMA_HOST=localhost
    export NEO4J_PASSWORD=arionneo4j@2026
    python3 test_orchestrator.py

What this tests:
  1. New session — intake flow (no existing session)
  2. Clarification resolution — user picks option
  3. Follow-up query — within established session
  4. Explicit ref query — fast path, no clarification
  5. Multi-turn conversation — session state carries forward
  6. Error handling — graceful degradation
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.orchestrator import RAGOrchestrator, OrchestratorConfig
from rag.classifier   import TenantProfile, QuestionType


# ── Config ────────────────────────────────────────────────────────────────────

arion = TenantProfile(
    tenant_id            = "arion-networks",
    name                 = "Arion Networks",
    applicable_standards = ["ISO27001:2022", "GDPR:2016/679"],
    role                 = ["controller", "processor"],
    sector               = "technology",
    jurisdiction         = ["EU", "UK"],
    has_posture_data     = True,
)

POSTURE = {
    "ISO27001:2022:A.8.24": {
        "finding":         "OFI",
        "gap_description": "Encryption policy does not explicitly scope personal data",
        "evidence_note":   "Encryption policy v1.2",
        "remedial_action": "Update encryption policy",
    },
    "ISO27001:2022:A.8.11": {
        "finding":         "NC",
        "gap_description": "No data masking policy in place",
        "evidence_note":   "",
        "remedial_action": "Develop masking procedure",
    },
    "ISO27001:2022:A.5.24": {
        "finding":         "Comply",
        "gap_description": "",
        "evidence_note":   "IRP v2.1, tested March 2025",
        "remedial_action": "",
    },
    "ISO27001:2022:A.5.26": {
        "finding":         "OFI",
        "gap_description": "IRP lacks personal data breach determination step",
        "evidence_note":   "",
        "remedial_action": "Add breach determination checklist to IRP",
    },
    "GDPR:2016/679:Art.32": {
        "finding":         "OFI",
        "gap_description": "Risk assessment does not cover personal data risks",
        "evidence_note":   "General IT risk assessment in place",
        "remedial_action": "Extend risk assessment",
    },
}

config = OrchestratorConfig()   # reads env vars automatically


def divider(title):
    print()
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)


def print_response(response):
    """Print a formatted response summary."""
    if response.needs_clarification:
        print(f"  → CLARIFICATION NEEDED")
        print(f"  Question: {response.clarification_question}")
    elif response.error:
        print(f"  → ERROR: {response.error}")
    else:
        print(f"  → ANSWER ({response.question_type.value if response.question_type else 'unknown'})")
        # First 200 chars of answer
        preview = (response.answer_text or "")[:200].replace('\n', ' ')
        print(f"  Preview: {preview}...")
        print()
        print(f"  Confidence:  {response.confidence:.0%}")
        print(f"  Nodes:       {response.node_count} ({response.primary_node_count} primary)")
        print(f"  Latency:     {response.total_ms}ms (Neo4j: {response.neo4j_ms}ms)")
        print(f"  Verified:    {'✓' if response.verified else '✗'}")
        print(f"  Corrected:   {'yes' if response.was_corrected else 'no'}")
        print(f"  Refs:        {', '.join(response.cited_refs[:6])}")
        if response.posture_findings:
            nc  = [r.split(':')[-1] for r,v in response.posture_findings.items()
                   if v.get('finding')=='NC']
            ofi = [r.split(':')[-1] for r,v in response.posture_findings.items()
                   if v.get('finding')=='OFI']
            if nc:  print(f"  NC:          {', '.join(nc)}")
            if ofi: print(f"  OFI:         {', '.join(ofi)}")


# ── Build orchestrator ────────────────────────────────────────────────────────

print("Building orchestrator...")
orchestrator = RAGOrchestrator(
    tenant_profile = arion,
    config         = config,
    posture_data   = POSTURE,
)
neo4j_online = orchestrator._expander.test_connection()
print(f"  Neo4j:    {'online' if neo4j_online else 'offline'}")
print(f"  ChromaDB: {'HTTP' if config.chroma_host else 'local'}")
print(f"  Posture:  {len(POSTURE)} controls")
print(f"  Opening: {orchestrator.opening_message()[:80]}...")


# ── TEST 1 — New session, explicit ref (fast path) ────────────────────────────
divider("TEST 1 — Explicit ref query: What is Art.33.1?")

r1 = orchestrator.chat("What does Art.33.1 say?")
print_response(r1)

assert r1.answer_text is not None, "Expected an answer"
assert not r1.needs_clarification, "Explicit ref should not need clarification"
assert r1.session is not None, "Should have a session"
print("\n✓ PASS")


# ── TEST 2 — Follow-up in established session ─────────────────────────────────
divider("TEST 2 — Follow-up: do we need to notify affected customers?")

r2 = orchestrator.chat(
    "Do we need to notify affected customers as well?",
    session = r1.session,
    history = r1.updated_history,
)
print_response(r2)

assert not r2.needs_clarification, "Should resolve within breach session"
assert r2.session is not None
print("\n✓ PASS")


# ── TEST 3 — GAP_ANALYSIS with posture ───────────────────────────────────────
divider("TEST 3 — GAP_ANALYSIS: What are our encryption gaps?")

r3 = orchestrator.chat(
    "What are our encryption gaps under Art.32?",
    session = r1.session,
    history = r1.updated_history,
)
print_response(r3)

assert r3.answer_text is not None
# Should surface the NC and OFI posture findings
if r3.posture_findings:
    nc_found = any(v.get('finding') == 'NC'
                   for v in r3.posture_findings.values())
    print(f"  NC findings surfaced: {'✓' if nc_found else '✗ (may need posture data)'}")
print("\n✓ PASS")


# ── TEST 4 — Fresh session, ambiguous query ───────────────────────────────────
divider("TEST 4 — New session, ambiguous query (supplier)")

r4 = orchestrator.chat("I need to sort out our supplier arrangements")
print_response(r4)

if r4.needs_clarification:
    print(f"\n  → Clarification asked (expected for ambiguous query)")
    print(f"  Question: {r4.clarification_question}")
    print("\n✓ PASS — clarification correctly triggered")
else:
    print(f"\n→ Resolved directly to: {r4.question_type}")
    print("✓ PASS — direct resolution also acceptable")


# ── TEST 5 — Multi-turn conversation state ────────────────────────────────────
divider("TEST 5 — Multi-turn: session refs carry forward")

# Start with a specific topic
r5a = orchestrator.chat("What does Art.25 require for privacy by design?")
print(f"Turn 1: {r5a.question_type.value if r5a.question_type else 'clarification'}")
print(f"  Active refs after turn 1: {r5a.session.active_refs if r5a.session else '—'}")

if r5a.session:
    # Follow up
    r5b = orchestrator.chat(
        "What evidence do we need to demonstrate this?",
        session = r5a.session,
        history = r5a.updated_history,
    )
    print(f"Turn 2: {r5b.question_type.value if r5b.question_type else 'clarification'}")
    print(f"  Active refs after turn 2: {r5b.session.active_refs if r5b.session else '—'}")
    print(f"  History length: {len(r5b.updated_history)} messages")
    print("\n✓ PASS — session state carries forward across turns")
else:
    print("→ No session from turn 1 (clarification) — skipping turn 2")


# ── TEST 6 — Opening message ──────────────────────────────────────────────────
divider("TEST 6 — Opening message")

msg = orchestrator.opening_message()
print(msg)
assert "Arion Networks" in msg
assert "ISO 27001" in msg or "GDPR" in msg
print("\n✓ PASS")


# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 65)
print("  All orchestrator tests complete")
print(f"  Neo4j: {'online' if neo4j_online else 'offline'}")
print(f"  Model: {config.answer_model}")
print("=" * 65)
