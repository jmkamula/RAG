"""
ArionComply — LangGraph chat interface.

Runs alongside chat.py during migration. Use --graph flag or this file
directly to test the LangGraph pipeline vs the orchestrator.

Usage:
    python3 chat_graph.py
    python3 chat_graph.py --chain-log
"""
from __future__ import annotations

import os
import sys
import time
import textwrap

sys.path.insert(0, os.path.dirname(__file__))

from rag.arion_graph        import build_arion_graph, get_checkpointer
from rag.arion_state        import make_initial_state, ArionState
from rag.orchestrator       import OrchestratorConfig
from rag.llm_answer         import LLMAnswer
from rag.context_assembler  import ContextAssembler
from rag.graph_expander     import GraphExpander
from rag.classifier         import QueryClassifier
from rag.chain_logger       import enable_chain_logging
from vector.retriever       import VectorRetriever
from chat                   import ARION as tenant, ARION_POSTURE, ARION_SCOPE, ARION_DOC_ALERTS


# ── ANSI colours ─────────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[36m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"


def print_banner():
    print(f"\n{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║       ArionComply — Compliance Advisor  [graph]      ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}║           Arion Networks  ·  ISO 27001 + GDPR        ║{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}╚══════════════════════════════════════════════════════╝{C.RESET}")
    print(f"{C.DIM}Commands: /quit  /reset  /debug  /posture{C.RESET}\n")


def print_analytics(result: ArionState, total_ms: int):
    print(f"\n{C.DIM}{'─'*55}{C.RESET}")
    print(f"{C.DIM}  ANALYTICS  (graph){C.RESET}")
    print(f"{C.DIM}{'─'*55}{C.RESET}")
    print(f"{C.DIM}  Type:        {result.get('intent_type','?')}{C.RESET}")
    print(f"{C.DIM}  Confidence:  {result.get('confidence', 0):.0%}{C.RESET}")
    print(f"{C.DIM}  Nodes:       {result.get('node_count', 0)} primary{C.RESET}")
    neo4j_ms = result.get('neo4j_ms', 0)
    print(f"{C.DIM}  Latency:     Neo4j {neo4j_ms}ms  Total {total_ms}ms{C.RESET}")

    verified      = result.get('verified', False)
    was_corrected = result.get('was_corrected', False)
    answer_source = result.get('answer_source', '')
    if answer_source == 'postgres':
        v_str = f"{C.GREEN}✓ direct (Postgres){C.RESET}"
    elif verified and not was_corrected:
        v_str = f"{C.GREEN}✓ verified{C.RESET}"
    elif verified and was_corrected:
        v_str = f"{C.YELLOW}✓ verified  (corrected){C.RESET}"
    else:
        v_str = f"{C.YELLOW}△ unverified{C.RESET}"
    print(f"  Answer:      {v_str}")

    cited = result.get('cited_refs', [])
    if cited:
        print(f"{C.DIM}  Refs:        {('  '.join(cited[:8]))}{C.RESET}")

    pf = result.get('posture_findings', {})
    nc  = [r for r, f in pf.items() if f == 'NC']
    ofi = [r for r, f in pf.items() if f == 'OFI']
    comply = [r for r, f in pf.items() if f == 'Comply']
    if nc:
        print(f"{C.DIM}  Posture NC:  {', '.join(nc)}{C.RESET}")
    if ofi:
        print(f"{C.DIM}  Posture OFI: {', '.join(ofi)}{C.RESET}")
    if comply:
        print(f"{C.DIM}  Comply:      {', '.join(comply)}{C.RESET}")

    print(f"{C.DIM}  Turn:        {result.get('turn_count', 0)}{C.RESET}")
    print(f"{C.DIM}{'─'*55}{C.RESET}\n")


def check_neo4j(config: OrchestratorConfig) -> tuple[bool, str]:
    """Explicit Neo4j connectivity check with clear status message."""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password),
            connection_timeout=5,
        )
        with driver.session() as s:
            count = s.run("MATCH (n) RETURN count(n) as c").single()["c"]
        driver.close()
        return True, f"{C.GREEN}online ({count} nodes){C.RESET}"
    except Exception as e:
        short = str(e)[:60]
        return False, f"{C.RED}OFFLINE{C.RESET} {C.DIM}— {short}{C.RESET}"


def main():
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--chain-log", action="store_true")
    parser.add_argument("--log-dir", default="/tmp")
    args, _ = parser.parse_known_args()

    if args.chain_log:
        enable_chain_logging(verbose=True, log_dir=args.log_dir)
        print(f"{C.YELLOW}[chain-log enabled]{C.RESET}\n")

    print_banner()

    config = OrchestratorConfig()

    print(f"{C.DIM}Building graph...{C.RESET}")

    # ── Explicit Neo4j check ───────────────────────────────────────────────
    neo4j_online, neo4j_status = check_neo4j(config)
    print(f"  Neo4j:    {neo4j_status}")
    if not neo4j_online:
        print(f"\n  {C.YELLOW}⚠ Neo4j is offline.{C.RESET}")
        print(f"  {C.DIM}Graph expansion disabled — answers will use vector-only context.{C.RESET}")
        print(f"  {C.DIM}Start Neo4j Desktop and restart to enable full graph traversal.{C.RESET}\n")

    # ── Build pipeline components ──────────────────────────────────────────
    retriever  = VectorRetriever(
        chroma_host=config.chroma_host,
        chroma_port=config.chroma_port,
    )
    expander   = GraphExpander(
        neo4j_uri      = config.neo4j_uri,
        neo4j_user     = config.neo4j_user,
        neo4j_password = config.neo4j_password,
        retriever      = retriever,
    )

    # Pre-warm Neo4j connection — sets _online=True before graph runs
    if neo4j_online:
        expander._is_online()

    assembler  = ContextAssembler(tenant_profile=tenant)
    llm        = LLMAnswer()
    classifier = QueryClassifier(tenant_profile=tenant, retriever=retriever)

    chroma_status = (
        f"{C.GREEN}HTTP server{C.RESET}"
        if config.chroma_host
        else f"{C.GREEN}local{C.RESET}"
    )
    print(f"  ChromaDB: {chroma_status}")

    llm_model = os.getenv("LOCAL_LLM_MODEL", "gpt-4o")
    llm_url   = os.getenv("LOCAL_LLM_BASE_URL", "OpenAI")
    print(f"  LLM:      {C.GREEN}{llm_model}{C.RESET} via {llm_url}")
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
    print(f"  Pipeline: {C.GREEN}LangGraph StateGraph{C.RESET}")

    if not neo4j_online:
        print(f"  Mode:     {C.YELLOW}vector-only (Neo4j offline){C.RESET}")

    with get_checkpointer() as cp:
        graph = build_arion_graph(
            tenant       = tenant,
            retriever    = retriever,
            expander     = expander,
            assembler    = assembler,
            llm          = llm,
            classifier   = classifier,
            posture      = ARION_POSTURE,
            checkpointer = cp,
        )

        session_id = f"arion_{int(time.time())}"
        cfg        = {"configurable": {"thread_id": session_id}}
        init_state = make_initial_state(tenant)

        print(f"\n{C.BOLD}ArionComply:{C.RESET}")
        print("Hello! I'm your ArionComply advisor for ISO 27001 and GDPR. "
              "What would you like to explore?\n")

        while True:
            try:
                user_input = input(f"{C.BOLD}You:{C.RESET} ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break

            if not user_input:
                continue

            # Commands
            if user_input.lower() in ("/quit", "/exit", "exit", "quit"):
                print("Goodbye.")
                break

            if user_input.lower() == "/reset":
                session_id = f"arion_{int(time.time())}"
                cfg        = {"configurable": {"thread_id": session_id}}
                init_state = make_initial_state(tenant)
                print(f"{C.DIM}Session reset.{C.RESET}\n")
                continue

            if user_input.lower() == "/posture":
                print(f"\n{C.DIM}Posture data ({len(ARION_POSTURE)} controls):{C.RESET}")
                for node_id, rec in ARION_POSTURE.items():
                    ref = node_id.split(":")[-1]
                    finding = rec.get("finding", "?")
                    colour = C.RED if finding == "NC" else C.YELLOW if finding == "OFI" else C.GREEN
                    gap = rec.get("gap_description", "")[:60]
                    print(f"  {colour}{finding:7s}{C.RESET} {ref:15s} {C.DIM}{gap}{C.RESET}")
                print()
                continue

            if user_input.lower() == "/neo4j":
                online, status = check_neo4j(config)
                print(f"  Neo4j: {status}\n")
                continue

            if user_input.lower() == "/debug":
                print(f"  Session:  {session_id}")
                print(f"  Neo4j:    {'online' if neo4j_online else 'OFFLINE'}")
                print(f"  Thread:   {cfg['configurable']['thread_id']}\n")
                continue

            # Run graph
            t0 = time.time()
            print(f"{C.DIM}Thinking...{C.RESET}")

            try:
                result = graph.invoke(
                    {**init_state, "query": user_input},
                    cfg,
                )
            except Exception as e:
                print(f"{C.RED}Error: {e}{C.RESET}\n")
                import traceback
                traceback.print_exc()
                continue

            total_ms = round((time.time() - t0) * 1000)

            # Handle clarification
            if result.get("needs_clarif") and result.get("clarif_question"):
                print(f"\n{C.BOLD}ArionComply:{C.RESET}")
                print(result["clarif_question"])
                print(f"\n{C.DIM}(Say 'just answer' to skip clarification){C.RESET}\n")
                continue

            # Print answer
            answer = result.get("answer_text", "")
            if answer:
                print(f"\n{C.BOLD}ArionComply:{C.RESET}")
                for line in answer.split("\n"):
                    if line.strip():
                        print(textwrap.fill(line, width=65,
                                            subsequent_indent="   ")
                              if len(line) > 65 else line)
                    else:
                        print()

            print_analytics(result, total_ms)


if __name__ == "__main__":
    main()
