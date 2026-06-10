#!/usr/bin/env python3
"""
Smoke test for conversational context routing in the chat surface.

Exercises five two/three-turn conversation patterns to verify whether
each turn has access to prior-turn context. Each test runs against the
live API with a fresh session_id, sends the turns in sequence, and
reports per-test PASS/FAIL based on simple heuristics on the
responses.

Run:
  PYTHONPATH=/data/arioncomply python3 scripts/test_conversational_context.py

Patterns covered:
  1. Named-doc upload-status follow-up (the canonical fix case)
  2. Sequential single-doc (does Q3 deictic resolve to most recent?)
  3. "Tell me more" deep-dive after a doc match
  4. "Is it compliant?" status query about prior entity
  5. Inventory query → deictic follow-up (last_entity should be empty)

Exit 0 if all PASS or all explained; 1 on any unexpected failure shape.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid

import requests

DEFAULT_API_KEY  = "arion_dev_key_2026"
DEFAULT_BASE_URL = "http://localhost:8080"

# Phrases that signal the conversational-context routing is BROKEN.
BAD_FALLBACK_MARKERS = (
    "does not provide any primary compliance nodes",
    "please provide the relevant compliance nodes",
)


def _chat(base_url: str, api_key: str, session_id: str, question: str) -> str:
    t0 = time.time()
    print(f"  → [{session_id[-8:]}] {question[:70]}", flush=True)
    r = requests.post(
        f"{base_url}/api/v1/chat",
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        json={"question": question, "session_id": session_id},
        timeout=180,
    )
    r.raise_for_status()
    ans = r.json().get("answer", "")
    print(f"    ← {len(ans)} chars in {time.time()-t0:.1f}s", flush=True)
    return ans


def _has_bad_fallback(answer: str) -> bool:
    al = answer.lower()
    return any(marker in al for marker in BAD_FALLBACK_MARKERS)


def _verdict(passed: bool, reason: str) -> str:
    return f"{'PASS' if passed else 'FAIL'}: {reason}"


def _run(base_url: str, api_key: str) -> list[dict]:
    results: list[dict] = []

    # ── Pattern 1: named-doc upload + deictic follow-up ────────────────────
    sid = f"smoke_{uuid.uuid4().hex[:8]}"
    q1 = "have we uploaded our business continuity policy?"
    q2 = "this is the plan, what about the policy document?"
    a1 = _chat(base_url, api_key, sid, q1)
    a2 = _chat(base_url, api_key, sid, q2)
    # Pass: Q2 doesn't fall into the empty-retrieval template.
    # Extra credit: Q2 mentions BC Policy / DOC007 / something contextual.
    p1_pass = not _has_bad_fallback(a2)
    p1_ctx = any(s in a2 for s in ("Business Continuity", "DOC007", "policy"))
    results.append({
        "name":   "1. named-doc upload + deictic follow-up",
        "verdict": _verdict(p1_pass, "Q2 avoids generic empty-retrieval template" + (" and references prior context" if p1_ctx else "")),
        "q1":     q1, "q2": q2,
        "a1":     a1[:200],
        "a2":     a2[:300],
    })

    # ── Pattern 2: sequential single-doc, then deictic ────────────────────
    sid = f"smoke_{uuid.uuid4().hex[:8]}"
    q1 = "have we uploaded our business continuity policy?"
    q2 = "have we uploaded our access control policy?"
    q3 = "is it approved?"
    a1 = _chat(base_url, api_key, sid, q1)
    a2 = _chat(base_url, api_key, sid, q2)
    a3 = _chat(base_url, api_key, sid, q3)
    # Pass: Q3 references SOME prior doc (last_entity is one-slot, so it'll
    # resolve to Q2's Access Control Policy). Fail: Q3 falls into empty
    # template OR confuses both docs.
    p2_pass = not _has_bad_fallback(a3)
    p2_refs_acp = any(s in a3 for s in ("Access Control", "DOC006"))
    p2_refs_bcp = any(s in a3 for s in ("Business Continuity", "DOC007"))
    p2_note = ""
    if p2_refs_acp and not p2_refs_bcp:
        p2_note = "Q3 resolved 'it' to most recent (ACP) — one-slot behaviour"
    elif p2_refs_bcp and not p2_refs_acp:
        p2_note = "Q3 resolved 'it' to FIRST doc (BCP) — unexpected"
    elif p2_refs_acp and p2_refs_bcp:
        p2_note = "Q3 mentions BOTH — ambiguous"
    else:
        p2_note = "Q3 references neither doc"
    results.append({
        "name":   "2. sequential docs + 'is it approved?'",
        "verdict": _verdict(p2_pass, p2_note),
        "q1":     q1, "q2": q2, "q3": q3,
        "a1":     a1[:150],
        "a2":     a2[:150],
        "a3":     a3[:300],
    })

    # ── Pattern 3: doc match + 'tell me more' ─────────────────────────────
    sid = f"smoke_{uuid.uuid4().hex[:8]}"
    q1 = "have we uploaded our access control policy?"
    q2 = "tell me more about it"
    a1 = _chat(base_url, api_key, sid, q1)
    a2 = _chat(base_url, api_key, sid, q2)
    p3_pass = not _has_bad_fallback(a2)
    p3_ctx  = any(s in a2 for s in ("Access Control", "DOC006", "A.5.15", "A.5.18"))
    results.append({
        "name":   "3. doc match + 'tell me more about it'",
        "verdict": _verdict(p3_pass, "Q2 avoids generic template" + (" and includes ACP-related content" if p3_ctx else " but doesn't visibly reference ACP")),
        "q1":     q1, "q2": q2,
        "a1":     a1[:150],
        "a2":     a2[:300],
    })

    # ── Pattern 4: doc match + 'is it compliant?' ─────────────────────────
    sid = f"smoke_{uuid.uuid4().hex[:8]}"
    q1 = "have we uploaded our access control policy?"
    q2 = "is it compliant?"
    a1 = _chat(base_url, api_key, sid, q1)
    a2 = _chat(base_url, api_key, sid, q2)
    p4_pass = not _has_bad_fallback(a2)
    p4_ctx  = any(s in a2 for s in ("Access Control", "DOC006", "A.5.15", "A.5.18", "OFI", "NC", "Comply"))
    results.append({
        "name":   "4. doc match + 'is it compliant?'",
        "verdict": _verdict(p4_pass, "Q2 avoids generic template" + (" and includes ACP/posture content" if p4_ctx else " but doesn't visibly reference ACP")),
        "q1":     q1, "q2": q2,
        "a1":     a1[:150],
        "a2":     a2[:300],
    })

    # ── Pattern 5: inventory query (no single entity) + deictic ───────────
    sid = f"smoke_{uuid.uuid4().hex[:8]}"
    q1 = "what documents have we uploaded?"
    q2 = "what about the policy?"
    a1 = _chat(base_url, api_key, sid, q1)
    a2 = _chat(base_url, api_key, sid, q2)
    # Pass: Q2 doesn't fall into the generic template. Q1 returns a list
    # without a single entity (last_entity should be empty for inventory
    # queries). Q2 is more open to falling through — this is the worst-case
    # for the MVP fix because there's no prior entity to lean on.
    p5_pass = not _has_bad_fallback(a2)
    results.append({
        "name":   "5. inventory query + 'what about the policy?'",
        "verdict": _verdict(p5_pass, "Q2 avoids generic empty-retrieval template" + ("" if p5_pass else " — last_entity was empty so Q2 had no prior context")),
        "q1":     q1, "q2": q2,
        "a1":     a1[:120] + "...",
        "a2":     a2[:300],
    })

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--api-key",  default=DEFAULT_API_KEY)
    ap.add_argument("--json",     action="store_true", help="Emit full JSON results")
    args = ap.parse_args()

    print(f"=== Conversational context smoke test ===")
    print(f"target: {args.base_url}")
    print()

    t0 = time.time()
    try:
        results = _run(args.base_url, args.api_key)
    except requests.exceptions.RequestException as e:
        print(f"FAIL: HTTP error — {e}")
        return 1

    pass_count = sum(1 for r in results if r["verdict"].startswith("PASS"))
    fail_count = len(results) - pass_count
    elapsed = time.time() - t0

    for r in results:
        print(f"[{r['verdict']}] {r['name']}")
        print(f"    Q1: {r['q1']}")
        print(f"    A1: {r['a1']}")
        print(f"    Q2: {r['q2']}")
        print(f"    A2: {r['a2']}")
        if "q3" in r:
            print(f"    Q3: {r['q3']}")
            print(f"    A3: {r['a3']}")
        print()

    print(f"=== {pass_count}/{len(results)} PASS in {elapsed:.1f}s ===")

    if args.json:
        print()
        print(json.dumps(results, indent=2))

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
