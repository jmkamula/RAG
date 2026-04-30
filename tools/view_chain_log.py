#!/usr/bin/env python3
"""
ArionComply — Chain Log Viewer

Usage:
    python3 tools/view_chain_log.py                  # latest log
    python3 tools/view_chain_log.py --query 1        # only turn 1
    python3 tools/view_chain_log.py --step verify    # only verify steps
    python3 tools/view_chain_log.py --step selected  # see what Mistral selected
    python3 tools/view_chain_log.py --full           # no truncation
"""
import sys, json, glob, argparse

class C:
    RESET="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"
    CYAN="\033[36m"; GREEN="\033[32m"; YELLOW="\033[33m"
    RED="\033[31m"; BLUE="\033[34m"; MAGENTA="\033[35m"

STEP_COLOURS = {
    "classify": C.BLUE, "clarify": C.YELLOW,
    "answer": C.GREEN, "rank_answer": C.GREEN,
    "rank_raw": C.CYAN, "selected": C.MAGENTA,
    "verify": C.MAGENTA, "correct": C.RED,
}

def find_latest():
    logs = sorted(glob.glob("/tmp/arioncomply_chain_*.log"), reverse=True)
    return logs[0] if logs else None

def load(path):
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try: records.append(json.loads(line))
                except: pass
    return records

def render(r, full=False):
    step    = r.get("step", "?")
    model   = r.get("model", "")
    latency = r.get("latency_ms", 0)
    colour  = STEP_COLOURS.get(step, C.CYAN)
    out     = []

    header = f"{colour}{C.BOLD}── {step.upper()}"
    if latency: header += f" ({model}, {latency}ms)"
    elif model: header += f" ({model})"
    out.append(header + f" ──{C.RESET}")

    system = r.get("system", "")
    if system and "(verification" not in system and "(context" not in system:
        out.append(f"  {C.DIM}System: {system[:200]}{C.RESET}")

    user = r.get("user", "")
    if user and "(context" not in user:
        limit = None if full else 300
        out.append(f"  {C.DIM}User:   {user[:limit]}{C.RESET}")

    response = r.get("response", "")
    if response:
        limit = None if full else (1500 if step in ("verify","rank_raw","selected") else 300)
        out.append(f"  {colour}Response:\n{response[:limit]}{C.RESET}")

    meta = r.get("metadata", {})
    if meta and step == "verify":
        verdict = meta.get("verdict","")
        vc = C.GREEN if verdict == "pass" else C.RED
        out.append(f"\n  {vc}{C.BOLD}VERDICT: {verdict.upper()}  {meta.get('confidence',0):.0%}{C.RESET}")
        if meta.get("reasoning"): out.append(f"  {C.DIM}{meta['reasoning']}{C.RESET}")
        for i in meta.get("issues",[]): out.append(f"  {C.RED}  Issue: {i}{C.RESET}")
        for c in meta.get("corrections",[]): out.append(f"  {C.YELLOW}  Fix:   {c}{C.RESET}")

    return "\n".join(out)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", nargs="?")
    parser.add_argument("--query", "-q")
    parser.add_argument("--step", "-s")
    parser.add_argument("--full", "-f", action="store_true")
    args = parser.parse_args()

    path = args.log_file or find_latest()
    if not path:
        print("No log found. Run: python3 chat_graph.py --chain-log")
        sys.exit(1)

    print(f"{C.DIM}Log: {path}{C.RESET}")
    records = load(path)
    if not records:
        print("Empty."); sys.exit(0)

    if args.step:
        records = [r for r in records if r.get("step") == args.step]

    # Group by query
    groups = {}
    for r in records:
        q = r.get("query", "?")
        groups.setdefault(q, []).append(r)
    queries = list(groups.keys())

    if args.query:
        try:
            idx = int(args.query) - 1
            queries = [queries[idx]] if 0 <= idx < len(queries) else []
        except ValueError:
            queries = [q for q in queries if args.query.lower() in q.lower()]

    for i, q in enumerate(queries, 1):
        recs = groups[q]
        print(f"\n{C.BOLD}{C.CYAN}{'═'*60}{C.RESET}")
        print(f"{C.BOLD}{C.CYAN}  QUERY {i}: {q[:55]}{C.RESET}")
        print(f"{C.DIM}  Chain: {' → '.join(r.get('step','?') for r in recs)}{C.RESET}")
        print(f"{C.BOLD}{C.CYAN}{'═'*60}{C.RESET}")
        for r in recs:
            print(render(r, full=args.full))

    print(f"\n{C.DIM}Records: {len(records)}  Queries: {len(queries)}{C.RESET}\n")

if __name__ == "__main__":
    main()
