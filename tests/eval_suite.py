"""
ArionComply — Semi-Automated Evaluation Suite
Run: python3 tests/eval_suite.py [--test N] [--tag X] [--verbose] [--csv path] [--pause N]
"""
from __future__ import annotations
import os, sys, re, time, argparse, csv
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

try:
    from dotenv import load_dotenv
    for _p in [_ROOT, _ROOT.parent, _ROOT.parent.parent]:
        if (_p / ".env").exists():
            load_dotenv(_p / ".env")
            print(f"[eval] Loaded .env from {_p / '.env'}")
            break
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class EvalCase:
    id:               int
    query:            str
    tags:             list = field(default_factory=list)
    expected_refs:    list = field(default_factory=list)
    forbidden_refs:   list = field(default_factory=list)
    expected_type:    Optional[str] = None
    must_contain:     list = field(default_factory=list)
    must_not_contain: list = field(default_factory=list)
    min_findings:     int  = 0
    notes:            str  = ""


@dataclass
class EvalResult:
    case:           EvalCase
    answer:         str
    refs:           list
    qtype:          str
    latency_ms:     int
    passed:         list
    warnings:       list
    failures:       list
    resolver_trace: object = None   # ResolverTrace from pipeline state

    @property
    def status(self):
        if self.failures: return "FAIL"
        if self.warnings: return "WARN"
        return "PASS"


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

EVAL_CASES = [

    EvalCase(
        id=1, query="what are our access rights gaps?",
        tags=["gap", "core", "nc"],
        expected_refs=["A.5.18"],
        forbidden_refs=["A.7.1", "A.7.2", "A.8.25", "A.8.26"],
        expected_type="gap_analysis",
        must_contain=["A.5.18", "NC"],
        must_not_contain=["not applicable", "physical"],
        min_findings=1,
        notes="A.5.18 NC. Physical/dev controls must not appear.",
    ),

    EvalCase(
        id=2, query="what are our main compliance gaps?",
        tags=["gap", "core"],
        expected_refs=["A.5.18", "A.5.26"],
        forbidden_refs=["A.7.5", "A.6.7", "A.8.25"],
        expected_type="gap_analysis",
        must_contain=["NC"],
        min_findings=2,
        notes="Both NCs must appear.",
    ),

    EvalCase(
        id=3, query="show me our OFI findings",
        tags=["gap", "core", "ofi"],
        expected_refs=["A.5.19", "A.8.19", "9.2"],
        forbidden_refs=["A.7.5", "A.6.7"],
        expected_type="gap_analysis",
        must_contain=["OFI"],
        must_not_contain=["A.7.5", "A.6.7"],
        min_findings=3,
        notes="4 real OFIs.",
    ),

    EvalCase(
        id=4, query="what NC findings do we have?",
        tags=["gap", "core", "nc"],
        expected_refs=["A.5.18", "A.5.26"],
        expected_type="gap_analysis",
        must_contain=["NC", "A.5.18", "A.5.26"],
        min_findings=2,
        notes="Exactly 2 NCs.",
    ),

    EvalCase(
        id=5, query="what should we do to close the access rights NC?",
        tags=["gap", "implementation", "nc"],
        expected_refs=["A.5.18"],
        expected_type="implementation",
        must_contain=["access", "register"],
        must_not_contain=["physical"],
        notes="Implementation query for A.5.18 NC.",
    ),

    EvalCase(
        id=6, query="supplier assessment gaps",
        tags=["gap", "ofi"],
        expected_refs=["A.5.19"],
        expected_type="gap_analysis",
        must_contain=["A.5.19", "OFI"],
        notes="A.5.19 OFI.",
    ),

    EvalCase(
        id=7, query="ChatGPT policy gaps",
        tags=["gap", "ofi", "software"],
        expected_refs=["A.8.19"],
        expected_type="gap_analysis",
        must_contain=["A.8.19"],
        notes="A.8.19 OFI.",
    ),

    EvalCase(
        id=8, query="incident response gaps",
        tags=["gap", "nc", "ir"],
        expected_refs=["A.5.26"],
        expected_type="gap_analysis",
        must_contain=["A.5.26", "NC"],
        notes="A.5.26 NC.",
    ),

    EvalCase(
        id=9, query="what is our ISO 27001 posture?",
        tags=["posture", "core"],
        expected_refs=[],           # LLM may lead with any NC/OFI — min_findings covers it
        expected_type="gap_analysis",
        must_contain=["NC", "OFI"],
        min_findings=2,
        notes="Full posture overview.",
    ),

    EvalCase(
        id=10, query="are we certified?",
        tags=["posture", "cert"],
        expected_type="posture_check",
        must_contain=["certif"],
        must_not_contain=[],        # LLM may use "not certified" contextually (e.g. "risks to certification")
        notes="Arion is certified (URS, April 2025). Checks certif is mentioned.",
    ),

    EvalCase(
        id=11, query="are we GDPR compliant?",
        tags=["gdpr", "cross_framework"],
        expected_type="cross_framework",
        must_contain=["GDPR"],
        must_not_contain=["you are not GDPR compliant"],
        min_findings=2,
        notes="Should explain ISO 27701 bridge.",
    ),

    EvalCase(
        id=12, query="GDPR Art.32 compliance status",
        tags=["gdpr", "cross_framework"],
        expected_type="cross_framework",
        min_findings=1,
        notes="Art.32 = security of processing.",
    ),

    EvalCase(
        id=13, query="what is a NC?",
        tags=["definition"],
        expected_type="definition",
        must_contain=["non-conformity", "NC"],
        notes="Definition.",
    ),

    EvalCase(
        id=14, query="what does OFI mean?",
        tags=["definition"],
        expected_type="definition",
        must_contain=["improvement", "OFI"],
        notes="Definition.",
    ),

    EvalCase(
        id=15, query="what is ISO 27001?",
        tags=["definition"],
        expected_type="definition",
        must_contain=["information security", "management"],
        notes="Standard definition.",
    ),

    EvalCase(
        id=16,
        query="what documents do we need to address the access rights NC?",
        tags=["documents", "nc"],
        expected_refs=["A.5.18"],
        expected_type="document_inventory",
        must_contain=["access"],
        notes="Document checklist for A.5.18.",
    ),

    EvalCase(
        id=17, query="what must our access control policy contain?",
        tags=["documents", "policy"],
        expected_refs=["A.5.18"],
        expected_type="document_content",
        must_contain=["access"],
        notes="Document content query.",
    ),

    EvalCase(
        id=18, query="what are our physical security gaps?",
        tags=["scope", "na"],
        # forbidden_refs empty: short-circuit answer correctly says N/A,
        # no control refs should appear as gaps
        forbidden_refs=[],
        must_contain=["not applicable"],
        notes="Physical controls N/A. Short-circuit returns N/A message.",
    ),

    EvalCase(
        id=19, query="what are our software development security gaps?",
        tags=["scope", "na"],
        # forbidden_refs empty: short-circuit answer mentions A.8.25-31 as N/A (correct)
        forbidden_refs=[],
        must_contain=["not applicable"],
        notes="Dev controls N/A. Short-circuit returns N/A message.",
    ),

    EvalCase(
        id=20, query="how do we implement a formal access rights review?",
        tags=["implementation"],
        expected_refs=["A.5.18"],
        expected_type="implementation",
        must_contain=["review", "access"],
        notes="Implementation guidance for A.5.18.",
    ),

    EvalCase(
        id=21,
        query="how should we prepare for our next ISO 27001 surveillance audit?",
        tags=["implementation", "audit"],
        expected_refs=["9.2"],
        expected_type="implementation",
        must_contain=["audit"],
        notes="9.2 OFI.",
    ),

    # ── Feature-locked cases ────────────────────────────────────────────────
    # Each case below locks in a specific commit. If the commit's behaviour
    # regresses, the named case must fail. See feedback memory
    # `feedback_eval_with_each_feature`.

    EvalCase(
        id=22,
        query="are we ISO 27001 A.6.4 compliant?",
        tags=["posture", "cited_ref"],
        expected_refs=["A.6.4"],
        expected_type="posture_check",
        must_contain=["A.6.4", "disciplinary"],
        # The pre-fix bug returned unrelated NC/OFI findings (A.5.18 etc.) and
        # never mentioned A.6.4. Forbid those refs in the answer so the case
        # fails the moment the cited-ref handling regresses.
        must_not_contain=["A.5.18", "A.5.12"],
        notes="Commit 432605c: POSTURE_STATUS handler must seed cited refs.",
    ),

    EvalCase(
        id=23,
        query="what is ISO 27001 control A.6.4?",
        tags=["definition", "cited_ref"],
        expected_refs=["A.6.4"],
        expected_type="definition",
        must_contain=["A.6.4", "disciplinary"],
        notes="Commit 0b55716: STANDARD_KNOWLEDGE handler seeds cited refs.",
    ),

    EvalCase(
        id=24,
        query="what is our GDPR Art.32 status?",
        tags=["cross_framework", "xfw_inheritance", "gdpr"],
        expected_refs=["Art.32"],
        expected_type="cross_framework",
        # Art.32 is a Layer-2 node and must NEVER carry a standalone NC/OFI
        # tag — its posture is inherited from linked ISO controls. The answer
        # must reference at least one A.5.x bridge control.
        must_contain=["Art.32", "A.5"],
        must_not_contain=["Art.32 [NC]", "Art.32 [OFI]", "Art.32 is a non-conformity"],
        notes="Commit 432605c: Art.32 posture via xfw inheritance, never direct.",
    ),

    EvalCase(
        id=25,
        query="is GDPR Art.5 a non-conformity?",
        tags=["cross_framework", "xfw_inheritance", "gdpr"],
        expected_refs=["Art.5"],
        expected_type="cross_framework",
        # Lock in xfw inheritance behavioural contract:
        #   (1) the answer mentions Art.5 (the query subject)
        #   (2) it cites at least one ISO bridge control (A.5.x)
        #   (3) it NEVER attaches an NC/OFI tag to Art.5 itself — Layer-2
        #       nodes always inherit posture from linked primaries.
        # Skip a strict "addressed via" phrasing check — the LLM uses
        # equivalent phrasings ("implemented through", "covered by") and
        # the load-bearing test is the anti-hallucination one below.
        must_contain=["Art.5", "A.5"],
        must_not_contain=["Art.5 [NC]", "Art.5 [OFI]", "Art.5 is a non-conformity"],
        notes="Commit 432605c: anti-hallucination on Layer-2 posture.",
    ),

    EvalCase(
        id=26,
        query="what documents have we uploaded?",
        tags=["documents", "short_circuit", "upload_inventory"],
        expected_type="document_inventory",
        # The short-circuit path reads client_documents.is_uploaded and lists
        # actual titles + uploaded_at dates. A regression would either fall
        # back to a generic checklist or hallucinate doc names.
        must_contain=["Access Control Policy", "uploaded"],
        notes="Commit 9998c22: uploaded-doc short-circuit names real titles.",
    ),

    # TODO id=27 incident obligations — pending. The classifications model
    # (commit 40ad607) lands the Postgres + Neo4j shape, but the chat surface
    # still routes every "incident obligations" phrasing through
    # clarification. Add once the classifier recognises the intent.

    EvalCase(
        id=27,
        query="what cross-framework findings need review?",
        tags=["xfw_proposals", "documents", "short_circuit", "hitl"],
        expected_type="document_inventory",
        # End-to-end lock for the intake xfw_proposer + chat surface:
        # - intake hook walks IMPLEMENTS and writes proposals (else DB empty)
        # - classifier CLEAR_INTENT_PHRASE routes the query
        # - resolver short-circuits with the proposals list
        # The "←" arrow is structural (proposal-line format) so a regression
        # to a generic doc-status answer would lose it.
        must_contain=["cross-framework finding", "GDPR", "Art.", "←"],
        must_not_contain=["not applicable"],
        notes="Locks in xfw_proposer + classifier+resolver short-circuit chain.",
    ),

    EvalCase(
        id=28,
        query="what NC findings do we have?",
        tags=["posture", "nc", "xfw_proposals_isolation"],
        expected_refs=["A.5.18", "A.5.26"],
        expected_type="gap_analysis",
        must_contain=["NC", "A.5.18", "A.5.26"],
        # Isolation guard: pending xfw proposals must NOT leak into a normal
        # NC-findings posture query. The HITL queue lives in its own short
        # circuit; if its phrasing appears here, the pattern matcher is
        # over-firing.
        must_not_contain=[
            "cross-framework finding(s) pending review",
            "pending review:",
        ],
        notes="Negative test: xfw proposal listing must not pollute posture answers.",
    ),
]


# ---------------------------------------------------------------------------
# Pipeline wrapper
# ---------------------------------------------------------------------------

class EvalPipeline:
    def __init__(self):
        print("Loading pipeline components...")
        from chat import ARION as tenant, ARION_POSTURE
        from rag.arion_graph import build_arion_graph
        from rag.arion_state import make_initial_state
        from rag.orchestrator import OrchestratorConfig
        from rag.context_assembler import ContextAssembler
        from rag.graph_expander import GraphExpander
        from rag.llm_answer import LLMAnswer
        from rag.classifier import QueryClassifier
        from vector.retriever import VectorRetriever
        from langgraph.checkpoint.memory import MemorySaver

        cfg = OrchestratorConfig()
        retriever = VectorRetriever(
            chroma_host=cfg.chroma_host,
            chroma_port=cfg.chroma_port,
        )
        expander = GraphExpander(
            neo4j_uri=cfg.neo4j_uri,
            neo4j_user=cfg.neo4j_user,
            neo4j_password=cfg.neo4j_password,
            retriever=retriever,
        )
        self._graph = build_arion_graph(
            tenant=tenant,
            retriever=retriever,
            expander=expander,
            assembler=ContextAssembler(tenant_profile=tenant),
            llm=LLMAnswer(),
            classifier=QueryClassifier(tenant_profile=tenant, retriever=retriever),
            posture=ARION_POSTURE,
            checkpointer=MemorySaver(),
        )
        self._tenant     = tenant
        self._make_state = make_initial_state
        print(f"  Pipeline ready. Posture: {len(ARION_POSTURE)} controls loaded.")

    def run(self, query: str) -> dict:
        import uuid
        cfg = {"configurable": {"thread_id": f"eval_{uuid.uuid4().hex[:8]}"}}
        return self._graph.invoke(
            self._make_state(self._tenant, query=query), cfg
        )


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_case(case: EvalCase, pipeline: EvalPipeline) -> EvalResult:
    t0 = time.time()
    try:
        result = pipeline.run(case.query)
    except Exception as e:
        return EvalResult(
            case=case, answer=f"ERROR: {e}", refs=[], qtype="error",
            latency_ms=int((time.time() - t0) * 1000),
            passed=[], warnings=[], failures=[f"Pipeline exception: {e}"],
        )

    latency_ms     = int((time.time() - t0) * 1000)
    answer         = result.get("answer_text",    "") or ""
    refs           = result.get("cited_refs",     []) or []
    qtype          = result.get("intent_type",    "") or ""
    resolver_trace = result.get("resolver_trace", None)
    trace  = result.get("resolver_trace")

    passed, warnings, failures = [], [], []

    for ref in case.expected_refs:
        if ref in refs or ref in answer:
            passed.append(f"ref_present: {ref}")
        else:
            failures.append(f"MISSING required ref: {ref}")

    for ref in case.forbidden_refs:
        if ref in answer:
            failures.append(f"FORBIDDEN ref present: {ref}")
        else:
            passed.append(f"ref_absent: {ref}")

    for phrase in case.must_contain:
        if re.search(re.escape(phrase), answer, re.IGNORECASE):
            passed.append(f"contains: {phrase!r}")
        else:
            failures.append(f"MISSING required phrase: {phrase!r}")

    for phrase in case.must_not_contain:
        if re.search(re.escape(phrase), answer, re.IGNORECASE):
            failures.append(f"FORBIDDEN phrase present: {phrase!r}")
        else:
            passed.append(f"absent: {phrase!r}")

    if case.expected_type and qtype != case.expected_type:
        warnings.append(
            f"type mismatch: expected {case.expected_type}, got {qtype}"
        )
    elif case.expected_type:
        passed.append(f"type: {qtype}")

    # min_findings: count distinct ISO control refs in the answer
    controls = set(re.findall(r'A\.\d+\.\d+|\d+\.\d+', answer))
    nc_n  = len(re.findall(r'\bNC\b|[Nn]on.?[Cc]onformit', answer))
    ofi_n = len(re.findall(r'\bOFI\b|[Oo]pportunity for [Ii]mprovement', answer))
    total = max(len(controls), nc_n + ofi_n)
    if case.min_findings > 0 and total < case.min_findings:
        warnings.append(
            f"findings: expected \u2265{case.min_findings}, "
            f"got {total} ({len(controls)} controls cited)"
        )
    elif case.min_findings > 0:
        passed.append(f"findings: {total} \u2265 {case.min_findings}")

    return EvalResult(
        case=case, answer=answer, refs=refs, qtype=qtype,
        latency_ms=latency_ms,
        passed=passed, warnings=warnings, failures=failures,
        resolver_trace=resolver_trace,
    )


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_results(results: list, verbose: bool = False, trace: bool = False) -> None:
    n  = len(results)
    np = sum(1 for r in results if r.status == "PASS")
    nw = sum(1 for r in results if r.status == "WARN")
    nf = sum(1 for r in results if r.status == "FAIL")
    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  EVALUATION RESULTS: {np}/{n} PASS  {nw} WARN  {nf} FAIL")
    print(f"{sep}\n")
    for r in results:
        icon = "\u2713" if r.status == "PASS" else (
               "\u26a0" if r.status == "WARN" else "\u2717")
        print(
            f"  {icon} [{r.status:4s}] #{r.case.id:2d} "
            f"{r.latency_ms:5d}ms  {r.case.query[:50]}"
        )
        for f in r.failures:  print(f"         \u2717 {f}")
        for w in r.warnings:  print(f"         \u26a0 {w}")
        if trace and r.status in ("FAIL", "WARN") and r.resolver_trace:
            if r.resolver_trace and hasattr(r.resolver_trace, "full_trace"):
                print(r.resolver_trace.full_trace())
        if verbose:
            print(f"\n         Query:  {r.case.query}")
            print(f"         Type:   {r.qtype}")
            print(f"         Refs:   {r.refs}")
            print(f"         Answer: {r.answer[:400]}...\n")
    avg = sum(r.latency_ms for r in results) // n if n else 0
    print(f"\n  Avg latency: {avg}ms")
    print(f"  Total:       {sum(r.latency_ms for r in results)}ms")


def write_csv(results: list, path: str) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "id", "status", "query", "expected_type", "actual_type",
            "expected_refs", "actual_refs", "failures", "warnings",
            "latency_ms", "notes",
        ])
        for r in results:
            w.writerow([
                r.case.id, r.status, r.case.query,
                r.case.expected_type, r.qtype,
                " ".join(r.case.expected_refs), " ".join(r.refs),
                " | ".join(r.failures), " | ".join(r.warnings),
                r.latency_ms, r.case.notes,
            ])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="ArionComply evaluation suite")
    p.add_argument("--tag")
    p.add_argument("--test",    type=int)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--trace",   action="store_true",
                   help="Print full ResolverTrace for FAIL/WARN tests")
    p.add_argument("--csv")
    p.add_argument("--dry",     action="store_true")
    p.add_argument("--pause",   type=float, default=1.0)
    args = p.parse_args()

    cases = EVAL_CASES
    if args.test:  cases = [c for c in cases if c.id == args.test]
    elif args.tag: cases = [c for c in cases if args.tag in c.tags]
    if not cases:
        print("No matching test cases.")
        return

    if args.dry:
        print(f"\n{len(cases)} test cases (dry run):\n")
        for c in cases:
            tags = ", ".join(c.tags)
            print(f"  #{c.id:2d}  [{tags:30s}]  {c.query}")
        return

    try:
        pipeline = EvalPipeline()
    except Exception as e:
        print(f"\n\u2717 Could not load pipeline: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\nRunning {len(cases)} test cases (pause={args.pause}s)...\n")
    results = []
    for i, case in enumerate(cases, 1):
        print(f"  [{i:2d}/{len(cases)}] #{case.id} {case.query[:55]}...")
        r = run_case(case, pipeline)
        results.append(r)
        icon = "\u2713" if r.status == "PASS" else (
               "\u26a0" if r.status == "WARN" else "\u2717")
        print(f"         {icon} {r.status:4s}  {r.latency_ms}ms  type={r.qtype}")
        for f in r.failures[:2]:
            print(f"         \u2717 {f}")
        # --trace: print resolver trace for FAIL/WARN
        if getattr(args, 'trace', False) and r.status in ('FAIL', 'WARN'):
            _t = getattr(r, 'resolver_trace', None)
            if _t and hasattr(_t, 'full_trace'):
                print(_t.full_trace())
            elif _t:
                print(f'         [trace] {_t}')
        if args.pause > 0 and i < len(cases):
            time.sleep(args.pause)

    print_results(results, verbose=args.verbose, trace=getattr(args,"trace",False))

    if args.csv:
        write_csv(results, args.csv)
        print(f"\nCSV written to {args.csv}")
        print(f"\nResults written to {args.csv}")


if __name__ == "__main__":
    main()
