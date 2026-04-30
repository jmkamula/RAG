"""
ArionComply — Terminal Chat Interface

Run from the ingestion directory:
    cd ingestion
    export OPENAI_API_KEY=sk-proj-...
    export CHROMA_HOST=localhost
    export NEO4J_PASSWORD=arionneo4j@2026
    python3 chat.py

Controls:
    /quit or /exit  — exit
    /reset          — start a new session
    /debug          — toggle analytics panel
    /history        — show conversation history
    /posture        — show loaded posture data
"""
from __future__ import annotations

import sys
import os
import textwrap

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env before any other imports that need env vars
try:
    from dotenv import load_dotenv
    from pathlib import Path
    _env_file = Path(__file__).parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass  # dotenv not installed — rely on shell environment

from rag.orchestrator import RAGOrchestrator, OrchestratorConfig, OrchestratorResponse
from rag.chain_logger import enable_chain_logging, get_logger
from rag.classifier       import TenantProfile, SessionContext, IntakeResult
from enrichment.obligations.client_facts import ARION_FACTS
from rag.posture_loader   import load_tenant_context, build_pg_conn


# ── Tenant config ──────────────────────────────────────────────────────────────

ARION_TENANT_ID = "00000000-0000-0000-0000-000000000001"

# ── Tenant context loaded from Postgres at startup ───────────────────────────
# Posture, ClientFacts, and evaluation scope all come from Postgres.
# applicable_standards is derived automatically from tenant_standards table
# + standard_relationships — expands automatically as standards are added.
# ── Tenant context cache ─────────────────────────────────────────────────────
# Replaces direct Postgres calls and module-level globals.
# TenantContextCache is process-level; each request calls cache.load(tenant_id).
# TTL=60s: fresh enough for real-time updates, cheap enough for concurrent users.
from rag.tenant_context import TenantContextCache

_tenant_cache = TenantContextCache.from_env(ttl_seconds=60)

_ctx = None
try:
    _ctx              = _tenant_cache.load(ARION_TENANT_ID)
    ARION_POSTURE     = _ctx.posture
    ARION_FACTS_DB    = _ctx.facts
    ARION_SCOPE       = _ctx.scope
    ARION_DOC_ALERTS  = _ctx.document_alerts
    ARION             = _ctx.profile
except Exception as _e:
    import warnings
    warnings.warn(f"Could not load tenant context from Postgres: {_e} — using fallback")
    ARION_POSTURE     = {}
    ARION_FACTS_DB    = ARION_FACTS
    ARION_SCOPE       = None
    ARION_DOC_ALERTS  = []
    _tenant_cache     = None
    # Fallback: build TenantProfile manually
    ARION = TenantProfile(
        tenant_id            = "arion-networks",
        name                 = "Arion Networks",
        applicable_standards = ["ISO27001:2022"],
        role                 = ["controller", "processor"],
        sector               = "technology",
        jurisdiction         = ["EU", "UK"],
        has_posture_data     = False,
        facts                = ARION_FACTS,
        posture_data         = {},
        document_alerts      = [],
    )

# Arion Networks posture data
# Replace with real posture loader once Excel files are available


# ── Colours ────────────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    BLUE   = "\033[34m"
    WHITE  = "\033[37m"
    GREY   = "\033[90m"


# ── Analytics panel ────────────────────────────────────────────────────────────

def render_analytics(response: OrchestratorResponse) -> str:
    """Render the performance analytics panel."""
    lines = [
        f"\n{C.GREY}{'─' * 55}",
        f"  ANALYTICS",
        f"{'─' * 55}{C.RESET}",
    ]

    # Question type and confidence
    qtype = response.question_type.value if response.question_type else "unknown"
    conf  = response.confidence
    conf_colour = (C.GREEN if conf >= 0.85
                   else C.YELLOW if conf >= 0.70
                   else C.RED)

    lines.append(
        f"  {C.DIM}Type:{C.RESET}        "
        f"{C.BOLD}{qtype}{C.RESET}"
    )
    lines.append(
        f"  {C.DIM}Confidence:{C.RESET}  "
        f"{conf_colour}{conf:.0%}{C.RESET}"
    )

    # Nodes
    if response.node_count:
        lines.append(
            f"  {C.DIM}Nodes:{C.RESET}       "
            f"{response.node_count} total "
            f"({response.primary_node_count} primary)"
        )

    # Timing
    neo4j_str = f"Neo4j {response.neo4j_ms}ms  " if response.neo4j_ms else ""
    lines.append(
        f"  {C.DIM}Latency:{C.RESET}     "
        f"{neo4j_str}Total {response.total_ms}ms"
    )

    # Verification
    if response.answer_text:
        v_icon  = f"{C.GREEN}✓ verified{C.RESET}" if response.verified \
                  else f"{C.YELLOW}△ unverified{C.RESET}"
        corr    = f"  {C.DIM}(corrected){C.RESET}" if response.was_corrected else ""
        lines.append(f"  {C.DIM}Answer:{C.RESET}      {v_icon}{corr}")

    # Cited refs
    if response.cited_refs:
        refs_str = "  ".join(response.cited_refs[:8])
        lines.append(f"  {C.DIM}Refs:{C.RESET}        {C.CYAN}{refs_str}{C.RESET}")

    # Posture summary
    if response.posture_findings:
        findings = response.posture_findings
        nc      = [r.split(":")[-1] for r, v in findings.items()
                   if v.get("finding") == "NC"]
        ofi     = [r.split(":")[-1] for r, v in findings.items()
                   if v.get("finding") == "OFI"]
        comply  = [r.split(":")[-1] for r, v in findings.items()
                   if v.get("finding") == "Comply"]
        if nc:
            lines.append(
                f"  {C.DIM}Posture NC:{C.RESET}  {C.RED}{', '.join(nc)}{C.RESET}"
            )
        if ofi:
            lines.append(
                f"  {C.DIM}Posture OFI:{C.RESET} {C.YELLOW}{', '.join(ofi)}{C.RESET}"
            )
        if comply:
            lines.append(
                f"  {C.DIM}Comply:{C.RESET}      {C.GREEN}{', '.join(comply)}{C.RESET}"
            )

    # Neo4j mode
    if response.expanded:
        mode = "offline" if response.expanded.offline_mode else "graph"
        lines.append(f"  {C.DIM}Graph:{C.RESET}       {mode}")

    lines.append(f"{C.GREY}{'─' * 55}{C.RESET}\n")
    return "\n".join(lines)


# ── Chat loop ──────────────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════╗
║           ArionComply — Compliance Advisor           ║
║        Arion Networks  ·  ISO 27001 + ISO 27701       ║
╚══════════════════════════════════════════════════════╝{C.RESET}
{C.DIM}Commands: /quit  /reset  /debug  /history  /posture{C.RESET}
""")


def wrap_answer(text: str, width: int = 72) -> str:
    """Wrap answer text preserving markdown structure."""
    lines   = text.split('\n')
    wrapped = []
    for line in lines:
        if line.startswith('#') or line.startswith('-') or \
           line.startswith('*') or line.strip() == '':
            wrapped.append(line)
        else:
            wrapped.extend(textwrap.wrap(line, width=width) or [''])
    return '\n'.join(wrapped)


def main():
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--chain-log", action="store_true",
                        help="Log full LLM chain to console and /tmp/")
    parser.add_argument("--log-dir", default="/tmp",
                        help="Directory for chain log files")
    args, _ = parser.parse_known_args()

    if args.chain_log:
        enable_chain_logging(verbose=True, log_dir=args.log_dir)
        print(f"\033[33m[chain-log enabled — logging all LLM calls]\033[0m\n")

    print_banner()

    # Build config from env
    config = OrchestratorConfig()

    print(f"{C.DIM}Connecting to services...{C.RESET}")
    orchestrator = RAGOrchestrator(
        tenant_profile  = ARION,
        config          = config,
        posture_data    = ARION_POSTURE,
        document_alerts = ARION_DOC_ALERTS,
    )

    # Check Neo4j
    neo4j_status = (
        f"{C.GREEN}online{C.RESET}"
        if orchestrator._expander.test_connection()
        else f"{C.YELLOW}offline (vector-only mode){C.RESET}"
    )
    chroma_status = (
        f"{C.GREEN}HTTP server{C.RESET}"
        if config.chroma_host
        else f"{C.GREEN}local{C.RESET}"
    )

    # Show which LLM is active
    if config.using_local_llm:
        llm_status = (
            f"{C.GREEN}{config.local_llm_model or 'local'}{C.RESET} "
            f"{C.DIM}via {config.local_llm_base_url}{C.RESET}"
        )
    else:
        llm_status = f"{C.GREEN}gpt-4o{C.RESET} {C.DIM}(cloud){C.RESET}"

    print(f"  Neo4j:    {neo4j_status}")
    print(f"  ChromaDB: {chroma_status}")
    print(f"  LLM:      {llm_status}")
    print(f"  Posture:  {C.GREEN}{len(ARION_POSTURE)} controls loaded{C.RESET}")
    if ARION_SCOPE:
        print(f"  Standards:{C.GREEN} {ARION_SCOPE.queryable_standards}{C.RESET}")
        if ARION_SCOPE.can_evaluate_gdpr:
            print(f"  GDPR:     {C.GREEN}evaluable via {ARION_SCOPE.gdpr_bridge}{C.RESET}")
    if ARION_DOC_ALERTS:
        critical = sum(1 for a in ARION_DOC_ALERTS if a.get("alert_type") == "CRITICAL")
        warning  = sum(1 for a in ARION_DOC_ALERTS if a.get("alert_type") == "WARNING")
        info     = sum(1 for a in ARION_DOC_ALERTS if a.get("alert_type") == "INFO")
        print(f"  Docs:     {C.RED}{critical} critical{C.RESET}  "
              f"{C.YELLOW}{warning} warning{C.RESET}  "
              f"{info} info  (missing uploads)")
    print()

    # State
    session:             SessionContext | None  = None
    history:             list[dict]             = []
    debug:               bool                   = True
    pending_intake:      dict | None            = None
    clarification_state: object | None          = None   # ClarificationState

    # Opening message
    print(f"{C.BOLD}{C.CYAN}ArionComply:{C.RESET}")
    print(f"{orchestrator.opening_message()}\n")

    # Chat loop
    while True:
        try:
            user_input = input(f"{C.BOLD}You:{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.DIM}Goodbye.{C.RESET}")
            break

        if not user_input:
            continue

        # Commands
        if user_input.lower() in ("/quit", "/exit", "quit", "exit"):
            print(f"{C.DIM}Goodbye.{C.RESET}")
            break

        if user_input.lower() == "/reset":
            session        = None
            history        = []
            pending_intake = None
            print(f"{C.DIM}Session reset.{C.RESET}\n")
            print(f"{C.BOLD}{C.CYAN}ArionComply:{C.RESET}")
            print(f"{orchestrator.opening_message()}\n")
            continue

        if user_input.lower() == "/debug":
            debug = not debug
            print(f"{C.DIM}Analytics panel: {'on' if debug else 'off'}{C.RESET}\n")
            continue

        if user_input.lower() == "/history":
            if not history:
                print(f"{C.DIM}No history yet.{C.RESET}\n")
            else:
                print(f"\n{C.DIM}--- Conversation history ---")
                for msg in history[-6:]:
                    role = msg['role'].upper()
                    print(f"  {role}: {msg['content'][:80]}...")
                print(f"---{C.RESET}\n")
            continue

        if user_input.lower() == "/posture":
            print(f"\n{C.DIM}--- Posture data ---")
            for node_id, rec in ARION_POSTURE.items():
                ref     = node_id.split(":")[-1]
                finding = rec.get("finding","?")
                icon    = {"Comply":"✓","OFI":"△","NC":"✗"}.get(finding,"?")
                print(f"  {icon} {finding:7s} {ref}")
            print(f"---{C.RESET}\n")
            continue

        # ── Pipeline call ──────────────────────────────────────────────────
        print(f"\n{C.DIM}Thinking...{C.RESET}", end="\r")

        # If we have a pending clarification — combine original + user choice
        if pending_intake is not None:
            original_msg = pending_intake.get('original_message', '')
            # If user says an override phrase, pass it directly
            if user_input.lower().strip() in {
                "just answer", "skip", "go ahead", "answer anyway",
                "answer please", "just go", "proceed",
            }:
                combined = user_input
            else:
                combined = f"{original_msg} — specifically: {user_input}"
            # Keep pending_intake alive until we get a clear answer
            # (orchestrator.chat will clear it via clarification_state)
            response = orchestrator.chat(
                message             = combined,
                session             = session,
                history             = history,
                clarification_state = clarification_state,
            )
            # Clear pending_intake only when we get an actual answer
            if not response.needs_clarification:
                pending_intake = None
        else:
            response = orchestrator.chat(
                message              = user_input,
                session              = session,
                history              = history,
                clarification_state  = clarification_state,
            )

        # Clear "Thinking..." line
        print(" " * 20, end="\r")

        # Update state
        session              = response.session
        history              = response.updated_history
        clarification_state  = response.clarification_state

        # Display response
        print(f"\n{C.BOLD}{C.CYAN}ArionComply:{C.RESET}")

        if response.needs_clarification:
            print(f"{response.clarification_question}\n")
            # Store original message ONLY on the first clarification.
            # On subsequent clarifications, keep the original message
            # so the combined query stays anchored to the real topic.
            if pending_intake is None:
                pending_intake = {
                    'original_message': user_input,
                }
            # else: keep existing pending_intake.original_message intact

        elif response.error:
            print(f"{C.RED}Error: {response.error}{C.RESET}\n")

        else:
            # Format and print answer
            print(wrap_answer(response.answer_text))
            print()

            # Analytics panel
            if debug:
                print(render_analytics(response))

        # Small separator
        if not response.needs_clarification and not response.error:
            print()


if __name__ == "__main__":
    main()
