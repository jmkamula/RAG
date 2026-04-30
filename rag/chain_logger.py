"""
ArionComply — Chain Logger
Logs every LLM call in the pipeline with inputs, outputs, and timing.
Writes to /tmp/arioncomply_chain.log and optionally prints to console.

Usage:
    from rag.chain_logger import ChainLogger
    logger = ChainLogger(verbose=True)
    logger.log_call(...)

Or monkey-patch into the pipeline:
    python3 chat.py --chain-log
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# ── ANSI colours for console output ──────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    BLUE   = "\033[34m"
    MAGENTA= "\033[35m"


@dataclass
class ChainCall:
    step:       str        # e.g. "classify", "clarify", "answer", "verify", "correct"
    model:      str
    system:     str
    user:       str
    response:   str
    latency_ms: int
    metadata:   dict = field(default_factory=dict)


class ChainLogger:
    """
    Logs every LLM call in the compliance pipeline.

    Log file: /tmp/arioncomply_chain_{timestamp}.log (JSON lines)
    Console:  colourised summary when verbose=True
    """

    def __init__(
        self,
        verbose:  bool = True,
        log_dir:  str  = "/tmp",
        max_context_chars: int = 800,   # truncate long contexts in console
    ):
        self.verbose           = verbose
        self.max_context_chars = max_context_chars
        self._calls: list[ChainCall] = []
        self._query_start      = None
        self._query_text       = None

        # Log file
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = Path(log_dir) / f"arioncomply_chain_{ts}.log"

    # ── Public API ─────────────────────────────────────────────────────────

    def start_query(self, query: str) -> None:
        """Call at the start of each user query."""
        self._calls       = []
        self._query_start = time.time()
        self._query_text  = query

        if self.verbose:
            print(f"\n{C.BOLD}{C.CYAN}{'═'*65}{C.RESET}")
            print(f"{C.BOLD}{C.CYAN}  CHAIN LOG — {query[:60]}{C.RESET}")
            print(f"{C.BOLD}{C.CYAN}{'═'*65}{C.RESET}")

    def log_call(
        self,
        step:       str,
        model:      str,
        system:     str,
        user:       str,
        response:   str,
        latency_ms: int,
        metadata:   dict = None,
    ) -> None:
        """Log a single LLM call."""
        call = ChainCall(
            step       = step,
            model      = model,
            system     = system,
            user       = user,
            response   = response,
            latency_ms = latency_ms,
            metadata   = metadata or {},
        )
        self._calls.append(call)
        self._write_to_file(call)

        if self.verbose:
            self._print_call(call)

    def log_verification(
        self,
        verdict:     str,
        confidence:  float,
        issues:      list[str],
        corrections: list[str],
        reasoning:   str,
        latency_ms:  int,
        model:       str,
    ) -> None:
        """Specialised logger for verification results."""
        colour = C.GREEN if verdict == "pass" else C.RED
        meta = {
            "verdict":     verdict,
            "confidence":  confidence,
            "issues":      issues,
            "corrections": corrections,
            "reasoning":   reasoning,
        }
        self.log_call(
            step       = "verify",
            model      = model,
            system     = "(verification prompt)",
            user       = "(context + answer)",
            response   = json.dumps(meta, indent=2),
            latency_ms = latency_ms,
            metadata   = meta,
        )

        if self.verbose:
            print(f"\n  {colour}{C.BOLD}VERIFICATION: {verdict.upper()}{C.RESET}"
                  f"  confidence={confidence:.0%}")
            print(f"  Reasoning: {C.DIM}{reasoning}{C.RESET}")
            if issues:
                print(f"  {C.RED}Issues flagged:{C.RESET}")
                for i in issues:
                    print(f"    • {i}")
            if corrections:
                print(f"  {C.YELLOW}Corrections suggested:{C.RESET}")
                for c in corrections:
                    print(f"    → {c}")
            if verdict == "pass" and not issues:
                print(f"  {C.GREEN}No issues found — answer accepted{C.RESET}")

    def end_query(self, total_ms: int) -> None:
        """Call at the end of each query with total latency."""
        if self.verbose:
            n_calls = len(self._calls)
            steps   = [c.step for c in self._calls]
            total_llm = sum(c.latency_ms for c in self._calls)
            print(f"\n{C.DIM}{'─'*65}{C.RESET}")
            print(f"{C.DIM}  Chain: {' → '.join(steps)}{C.RESET}")
            print(f"{C.DIM}  LLM calls: {n_calls}  "
                  f"LLM time: {total_llm/1000:.1f}s  "
                  f"Total: {total_ms/1000:.1f}s{C.RESET}")
            print(f"{C.DIM}  Log: {self.log_path}{C.RESET}")
            print(f"{C.DIM}{'─'*65}{C.RESET}\n")

    # ── Internal ────────────────────────────────────────────────────────────

    def _print_call(self, call: ChainCall) -> None:
        STEP_COLOURS = {
            "classify": C.BLUE,
            "clarify":  C.YELLOW,
            "answer":   C.GREEN,
            "verify":   C.MAGENTA,
            "correct":  C.RED,
        }
        colour = STEP_COLOURS.get(call.step, C.CYAN)

        print(f"\n{colour}{C.BOLD}── {call.step.upper()} "
              f"({call.model}, {call.latency_ms}ms) ──{C.RESET}")

        # System prompt — first 200 chars
        if call.system and call.system != "(verification prompt)":
            sys_preview = call.system.replace('\n', ' ')[:200]
            print(f"  {C.DIM}System: {sys_preview}...{C.RESET}")

        # User message — truncated
        if call.user and call.user != "(context + answer)":
            user_preview = call.user.replace('\n', ' ')[:self.max_context_chars]
            print(f"  {C.DIM}User:   {user_preview}"
                  f"{'...' if len(call.user) > self.max_context_chars else ''}{C.RESET}")

        # Response — full for classify/verify, truncated for answer
        if call.step in ("classify", "verify"):
            print(f"  {colour}Response: {call.response[:600]}{C.RESET}")
        else:
            resp_preview = call.response.replace('\n', ' ')[:300]
            print(f"  {colour}Response: {resp_preview}...{C.RESET}")

    def _write_to_file(self, call: ChainCall) -> None:
        """Append call to JSONL log file."""
        record = {
            "timestamp":  datetime.now().isoformat(),
            "query":      self._query_text,
            "step":       call.step,
            "model":      call.model,
            "latency_ms": call.latency_ms,
            "system":     call.system[:500],
            "user":       call.user[:1000],
            "response":   call.response[:2000],
            "metadata":   call.metadata,
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")


# ── Global singleton — used by pipeline components ────────────────────────────

_chain_logger: ChainLogger | None = None


def get_logger() -> ChainLogger | None:
    return _chain_logger


def enable_chain_logging(verbose: bool = True, log_dir: str = "/tmp") -> ChainLogger:
    global _chain_logger
    _chain_logger = ChainLogger(verbose=verbose, log_dir=log_dir)
    return _chain_logger


def disable_chain_logging() -> None:
    global _chain_logger
    _chain_logger = None
