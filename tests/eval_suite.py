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

    # ── Phase B batch 24 (2026-06-02) — chapters 4 + 5 close-out 7-pack ────
    # First ISMS management-system clauses promoted to 4-leaf. Spine mix:
    # 2×records_program (4.1/4.2 register-as-primary) + 5×policy_program
    # (4.3/4.4/5.1/5.2/5.3 — scope/manual/directive/policy/matrix as primary).
    # Required posture seed: workbook didn't import rows for 4.1-4.4; rows for
    # 5.1-5.3 existed but inactive. Live posture set to OFI on all 7 (matches
    # Arion's pre-ISMS narrative). Engine NC 0/4 surfaces for all 7 in Stage-2.

    EvalCase(
        id=139,
        query="pending engine verdict for 4.1",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "isms_context"],
        expected_refs=["4.1"], expected_type="posture_check",
        must_contain=["4.1", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 4.1 (Understanding context) — records_program 4-leaf: issues_register + identification_framework + applicable_domains_scope + program_review (365d). First ISMS clause of batch 24 (chapters 4+5 close-out 7-pack).",
    ),

    EvalCase(
        id=138,
        query="pending engine verdict for 4.2",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "isms_parties"],
        expected_refs=["4.2"], expected_type="posture_check",
        must_contain=["4.2", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 4.2 (Interested parties) — records_program 4-leaf: parties_register + identification_framework + applicable_domains_scope + program_review (365d). Parallel structure to 4.1.",
    ),

    EvalCase(
        id=137,
        query="pending engine verdict for 4.3",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "isms_scope"],
        expected_refs=["4.3"], expected_type="posture_check",
        must_contain=["4.3", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 4.3 (ISMS scope) — policy_program 4-leaf: isms_scope (primary, id preserved) + scope_methodology + scope_change_record + scope_program_review (365d). Primary-leaf id preserved: req:4.3:isms_scope.",
    ),

    EvalCase(
        id=136,
        query="pending engine verdict for 4.4",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "isms_manual"],
        expected_refs=["4.4"], expected_type="posture_check",
        must_contain=["4.4", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 4.4 (ISMS itself) — policy_program 4-leaf: isms_manual + process_map + manual_change_record + program_review (365d). Process map is a distinct second leaf (not just a should_contain item).",
    ),

    EvalCase(
        id=135,
        query="pending engine verdict for 5.1",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "leadership"],
        expected_refs=["5.1"], expected_type="posture_check",
        must_contain=["5.1", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 5.1 (Leadership commitment) — policy_program 4-leaf: leadership_directive + engagement_framework + reaffirmation_record + program_review (365d). Reaffirmation_record is the lifecycle-end variant — covers turnover and currency.",
    ),

    EvalCase(
        id=134,
        query="pending engine verdict for 5.2",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "isp"],
        expected_refs=["5.2"], expected_type="posture_check",
        must_contain=["5.2", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 5.2 (InfoSec policy) — policy_program 4-leaf: information_security_policy (primary, id preserved) + approval_record + communication_evidence + program_review (365d). Primary-leaf id preserved: req:5.2:information_security_policy. Communication evidence is a distinct leaf (not a should_contain item) — 'approved but not communicated' is a common audit finding.",
    ),

    EvalCase(
        id=133,
        query="pending engine verdict for 5.3",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "isms_roles"],
        expected_refs=["5.3"], expected_type="posture_check",
        must_contain=["5.3", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks clause 5.3 (ISMS roles & authorities) — policy_program 4-leaf: roles_matrix + raci_framework + roles_change_record + program_review (365d). A.5.2 cross-check baked into the matrix and the review (5.3 = management-system roles; A.5.2 = operational roles).",
    ),

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
        # The 3 "outlier" OFIs: A.5.19 (suppliers), A.8.19 (software install),
        # 9.2 (a clause, not Annex A). Pre-fix llm_answer.py:307 capped
        # gap_analysis at 5-7 nodes; the LLM included 2 NCs first (per
        # selection-order rule) then 5 OFIs from the 8, silently dropping
        # the outliers ~50% of runs. Fix: removed the cap and added an
        # explicit "include clause format" rule to the prompt.
        expected_refs=["A.5.19", "A.8.19", "9.2"],
        forbidden_refs=["A.7.5", "A.6.7"],
        expected_type="gap_analysis",
        must_contain=["OFI"],
        # "A.9.2" / "A.10." / "A.4." are anti-patterns: clauses 4-10 are
        # body clauses, not Annex A — Annex A only has groups 5-8. The LLM
        # used to label clause 9.2 as "A.9.2"; the prompt now forbids this.
        must_not_contain=["A.7.5", "A.6.7", "A.9.2", "A.10.", "A.4."],
        min_findings=3,
        notes=(
            "Locks in exhaustive-list rule for gap_analysis (no count cap) "
            "AND the clause-vs-Annex-A labeling rule (no 'A.' prefix on "
            "body clauses 4-10)."
        ),
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

    EvalCase(
        id=29,
        query="show me the timeline for A.6.4",
        tags=["posture", "timeline", "short_circuit", "history"],
        expected_refs=["A.6.4"],
        expected_type="posture_check",
        # Stage 3 lock: the posture_status_log short-circuit reads the
        # demo-seeded timeline rows for A.6.4 (NULL→OFI on 2026-03-15,
        # OFI→Comply on 2026-05-06). A regression would either lose the
        # dates, drop the transition arrow, or fall through to a generic
        # posture answer that doesn't reference the prior state.
        must_contain=["A.6.4", "2026-03-15", "2026-05-06", "OFI", "Comply"],
        notes="Stage 3: posture timeline short-circuit (schema_v21).",
    ),

    EvalCase(
        id=30,
        query="have we uploaded our business continuity policy?",
        tags=["documents", "short_circuit", "upload_inventory", "registry_link"],
        expected_type="document_inventory",
        # API uploads save the file as {upload_id}.{ext} on disk. Before the
        # readers.read_document(original_filename=…) plumbing fix, that UUID
        # name leaked through to Finding.document_name, so posture_writer's
        # registry matcher (_match_registered_document) missed DOC007 on
        # every BCP upload and created an orphan client_documents row —
        # leaving DOC007 stuck at document_status='registered'. The bot then
        # told users their BCP "has not yet been uploaded" even though the
        # findings had landed. This case locks in the linkage: uploading
        # "Business Continuity Policy.docx" must surface DOC007 as uploaded.
        must_contain=["Business Continuity Policy", "uploaded"],
        must_not_contain=["not yet been uploaded", "not uploaded"],
        notes="BCP registry linkage: original_filename must reach the matcher.",
    ),

    EvalCase(
        id=31,
        query="what must our ISMS scope statement contain?",
        tags=["documents", "rename", "evidence_model", "document_content"],
        expected_refs=["4.3"],
        expected_type="document_content",
        # Commit 1 of the evidence-model rename. The chat path now traverses
        #   RequirementNode -[:SATISFIED_BY]-> FulfilmentSpec
        #                     -[:REQUIRES_EVIDENCE]-> EvidenceRequirement
        # instead of the old direct (n)-[:REQUIRES_DOCUMENT]->(:DocumentRequirement)
        # edge. The 4.3 ISMS Scope Statement is one of the 18 hand-curated
        # leaves; a regression on the FulfilmentSpec hop would drop its
        # checklist entirely (no must-items returned).
        must_contain=["Boundaries", "ISMS", "must"],
        must_not_contain=["FulfilmentSpec", "REQUIRES_EVIDENCE", "EvidenceRequirement"],
        notes=(
            "Locks in REQUIRES_DOCUMENT->REQUIRES_EVIDENCE rename and the "
            "FulfilmentSpec traversal hop in graph_expander."
        ),
    ),

    # ── Stage-2 engine-verdict approval (HITL two-stage commit 5) ──
    # MUST run before case 33: commit 5 gates the in-memory overlay on
    # engine_proposal_status='approved'. Without prior Stage-2 approval,
    # A.5.1's live finding stays at the document-confirmed value and case
    # 33 would no longer see the engine's OFI overlay. id=38 (approve)
    # therefore precedes id=33 in eval execution order — same trick the
    # acknowledge case (id=34) and Stage-1 approve case (id=36) use to
    # keep state idempotent across runs.
    EvalCase(
        id=37,
        query="what engine verdicts need review?",
        tags=["posture", "hitl", "stage2", "engine_proposals"],
        expected_type="posture_check",
        # Stage-2 review-queue chat surface: read-only. Idempotent anchors
        # "engine" + "review" match both the populated list and the
        # post-approval "No engine verdicts are pending review" path.
        must_contain=["engine", "review"],
        must_not_contain=[
            "FulfilmentSpec", "REQUIRES_EVIDENCE", "EvidenceRequirement",
            "I need more information",
        ],
        notes=(
            "Locks the Stage-2 engine-verdict review-queue chat surface "
            "(parse_stage2_intent + list_pending_proposals). Read-only."
        ),
    ),

    EvalCase(
        id=38,
        query="approve engine verdict for A.5.1",
        tags=["posture", "hitl", "stage2", "approve"],
        expected_refs=["A.5.1"],
        expected_type="posture_check",
        # Stage-2 batch-approval chat surface: promotes the persisted engine
        # proposal (commit 4) to live finding and flips
        # confirmation_status='engine_confirmed'.
        #
        # Idempotent anchor "approved" matches both the first-write success
        # ("Approved engine verdict for A.5.1: 'Comply' → 'OFI'. A.5.1 is now
        # engine_confirmed.") and the already-approved repeat path ("Engine
        # verdict for A.5.1 is already approved.").
        must_contain=["approved", "A.5.1"],
        must_not_contain=[
            "FulfilmentSpec", "REQUIRES_EVIDENCE", "EvidenceRequirement",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks the Stage-2 engine-verdict approval surface. Pairs with "
            "id=37 (list). Position-critical: must precede id=33 so the "
            "live finding is flipped before the 'A.5.1 compliant?' check."
        ),
    ),

    EvalCase(
        id=33,
        query="are we ISO 27001 A.5.1 compliant?",
        tags=["posture", "engine", "fulfilment_spec", "multi_leaf"],
        expected_refs=["A.5.1"],
        expected_type="posture_check",
        # Pre-commit-4: posture_controls.finding for A.5.1 was 'Comply' because
        # the tenant uploaded a policy and the extractor only checked policy
        # presence — auditors, however, expect four artifacts (policy, approval,
        # communication record, review record). Commit 4 wires the fulfilment
        # engine into load_posture: A.5.1's 4-leaf FulfilmentSpec evaluates
        # 1/4 satisfied → OFI, with the missing 3 leaves surfaced in the chat
        # answer's gap list. This case locks in:
        #   - engine overrides posture_controls for multi-leaf curated specs
        #   - chat surface exposes the engine's gap_list (specific missing items)
        #   - 'Comply' is forbidden for A.5.1 — the headline anti-regression.
        must_contain=["A.5.1", "OFI"],
        # Forbid A.5.1-specific Comply tags. The plain word "Comply" can't be
        # forbidden — it appears in the cross-framework rendering of other
        # ISO controls that address GDPR Art.32 (e.g. A.5.24 [Comply]).
        must_not_contain=[
            "A.5.1 [Comply]",
            "A.5.1 is Comply",
            "A.5.1 currently rated as Comply",
            "A.5.1 currently rated as a Comply",
        ],
        notes=(
            "Headline lock-in for the fulfilment engine. Would have failed "
            "pre-commit-4 (answered Comply); passes post-commit-4 (OFI with "
            "review/approval/communication gaps surfaced)."
        ),
    ),

    EvalCase(
        id=34,
        query=("acknowledge the A.5.1 communication record gap because we "
               "post the policy on the intranet and email new versions to "
               "all staff"),
        tags=["posture", "engine", "acknowledge", "tenant_evidence_gaps"],
        expected_refs=["A.5.1"],
        expected_type="posture_check",
        # Commit 5 (chat surface): the acknowledge short-circuit recognises
        # the ack-trigger verb + control ref + role + optional rationale, then
        # writes status='acknowledged' on the matching tenant_evidence_gaps
        # row. Idempotent: first run produces "Acknowledged: A.5.1
        # [communication_record]…", subsequent runs produce "already
        # acknowledged" — both confirm the surface is wired.
        #
        # Per [[human_in_the_loop_positioning]]: acknowledging suppresses the
        # gap from the headline list but the verdict STAYS OFI/NC. The forbid
        # below catches a regression where ack flips the posture to Comply.
        must_contain=["acknowledged", "A.5.1"],
        must_not_contain=[
            "flipped to Comply", "posture is now Comply",
            "A.5.1 [Comply]", "A.5.1 is Comply",
        ],
        notes=(
            "Locks in the acknowledge-gap chat surface (commit 5). "
            "Idempotent assertion via 'acknowledged' substring matches both "
            "the first-write and the already-acknowledged repeat paths."
        ),
    ),

    EvalCase(
        id=32,
        query="what documents do we need for A.5.29?",
        tags=["documents", "rename", "evidence_model", "uncurated"],
        expected_refs=["A.5.29"],
        # After commit 1, A.5.29 has a FulfilmentSpec with
        # curation_status='uncurated' and zero REQUIRES_EVIDENCE edges (no
        # hand-curated leaves). The chat path must return a graceful answer
        # that mentions A.5.29 and does NOT (a) hallucinate a checklist of
        # made-up requirements, or (b) leak internal model names. Forbidden
        # phrases catch the two regression modes.
        must_contain=["A.5.29"],
        must_not_contain=[
            "FulfilmentSpec", "REQUIRES_EVIDENCE", "EvidenceRequirement",
            "curation_status", "uncurated",
        ],
        notes=(
            "Locks in graceful empty-curation handling for the 408 controls "
            "with curation_status='uncurated' post-migration."
        ),
    ),

    EvalCase(
        id=35,
        query="what findings need review?",
        tags=["posture", "hitl", "stage1", "review_queue"],
        expected_type="posture_check",
        # Stage-1 review queue surface (HITL two-stage commit 3): the
        # short-circuit recognises the list verb and renders the per-control
        # pending counts directly from document_findings, bypassing the LLM
        # and the normal posture/standard pipeline.
        #
        # Idempotent assertion: with pending rows the render starts
        # "Pending review (N control(s)):"; with an empty queue it returns
        # "No pending findings to review." Both contain "pending" + "review"
        # — so the case passes regardless of whether the approve case below
        # has already drained the queue on a prior run.
        must_contain=["pending", "review"],
        must_not_contain=[
            "FulfilmentSpec", "REQUIRES_EVIDENCE", "EvidenceRequirement",
            "I need more information",
        ],
        notes=(
            "Locks the Stage-1 review-queue chat surface "
            "(parse_stage1_intent + list_queue). Read-only — does not "
            "mutate document_findings or posture_controls. Idempotent "
            "anchors handle both populated and drained queue states."
        ),
    ),

    EvalCase(
        id=36,
        query="approve findings for A.5.1",
        tags=["posture", "hitl", "stage1", "approve"],
        expected_refs=["A.5.1"],
        expected_type="posture_check",
        # Stage-1 batch approval surface (HITL two-stage commit 3): the
        # short-circuit recognises the approve verb + "findings" object +
        # control ref, promotes all pending document_findings rows for
        # A.5.1 to review_status='approved', and flips the live
        # posture_controls row to confirmation_status='document_confirmed'.
        #
        # Idempotent assertion via "approved" substring: matches both the
        # first-write success path ("Approved N extracted finding(s)…")
        # and the no_pending repeat path ("…already been approved or
        # rejected"). Pattern mirrors the acknowledge EvalCase (id=34).
        #
        # Per [[human_in_the_loop_positioning]]: the client owns posture.
        # The forbid below catches a regression where the surface fails
        # to fire and the normal LLM pipeline answers a posture lookup
        # for A.5.1 instead.
        must_contain=["approved", "A.5.1"],
        must_not_contain=[
            "FulfilmentSpec", "REQUIRES_EVIDENCE", "EvidenceRequirement",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks the Stage-1 batch-approval chat surface "
            "(approve_findings_for_control + posture promotion). "
            "Idempotent anchor 'approved' matches both first-write and "
            "no_pending repeat paths. Pairs with id=35 (list)."
        ),
    ),

    EvalCase(
        id=39,
        query="what is our posture on A.5.1?",
        tags=["posture", "confirmation_label", "document_confirmed"],
        expected_refs=["A.5.1"],
        # expected_type intentionally omitted — the classifier routes
        # "what is our posture on X?" to `definition` rather than
        # `posture_check`. The label-fix contract is type-agnostic;
        # locking expected_type here would WARN on a tangential signal.
        # Confirmation-label regression: A.5.1 carries
        # confirmation_status='document_confirmed' (Stage-1 approved).
        # Pre-fix llm_answer.py treated only {confirmed, overridden} as
        # non-draft and tagged the prompt context with [<finding> DRAFT].
        # The CONFIRMATION RULE in SYSTEM_PROMPT then forces the LLM to
        # hedge ("Our records suggest…" / "A preliminary assessment
        # indicates…") instead of stating the posture as fact.
        # Post-fix the tuple includes {document_confirmed, engine_confirmed}
        # so the [DRAFT] tag is dropped and the LLM states the finding
        # directly. Finding kept loose (Comply vs engine-driven OFI per
        # case 33) — the regression signal is the hedging phrases, not
        # the verdict text.
        must_contain=["A.5.1"],
        must_not_contain=[
            "preliminary assessment",
            "Our records suggest",
            "could you clarify",
            "I need more information",
        ],
        notes=(
            "Locks the [DRAFT] label fix: document_confirmed rows must "
            "be presented as facts, not hedged via the CONFIRMATION RULE. "
            "Depends on id=36 having previously flipped A.5.1 to "
            "document_confirmed (or the existing seeded state)."
        ),
    ),

    EvalCase(
        id=40,
        query="what is our posture on Art.5?",
        tags=["posture", "engine", "engine_nc"],
        expected_refs=["Art.5"],
        # Engine NC contract: _compose_posture emits NC when 0/N of an
        # applies/curated control's children are satisfied (was OFI for
        # any non-Comply pre-change). The Arion tenant's GDPR Art.5 is
        # the canonical 0/N case — none of its 2 paragraphs are satisfied
        # — and the consultant approved the engine's NC proposal during
        # initial UI rollout, so the live finding is now NC.
        #
        # Pre-change (engine emitted OFI for any non-Comply): the live
        # finding would have been OFI at best, never NC. This assertion
        # would have failed because no NC verdict ever reached Art.5.
        # Post-change: engine proposed NC, reviewer approved, live
        # finding is NC and stable.
        must_contain=["NC", "Art.5"],
        must_not_contain=[
            "FulfilmentSpec", "REQUIRES_EVIDENCE",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks engine 0/N → NC behaviour end-to-end (was 0/N → OFI). "
            "Tests the live-finding path post engine approval — depends "
            "on the seeded Arion tenant state where Art.5's NC proposal "
            "is engine_confirmed. Resilient to queue churn because it "
            "asserts on the applied finding, not the pending list."
        ),
    ),

    # ── Multi-leaf calibrations #2-#5 (commit 13e44ad) ──────────────────────
    # Each calibration promoted a control from single-leaf to a 4-leaf spine.
    # The Stage-2 list_one short-circuit (parse_stage2_intent → list_one) is
    # the surface that surfaces the engine_proposal_reason verbatim — the
    # phrase "0/4 children satisfied" PROVES the multi-leaf evaluation:
    # pre-promotion each control was single-leaf and the engine would have
    # emitted "0/1 children satisfied". Post-promotion it's "0/4".
    # LLM-free path (~30ms per case), template-rendered, deterministic.

    EvalCase(
        id=42,
        query="pending engine verdict for A.8.2",
        tags=["posture", "engine", "stage2", "multi_leaf", "calibration"],
        expected_refs=["A.8.2"],
        expected_type="posture_check",
        must_contain=["A.8.2", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            # Pre-promotion the single-leaf spec would have produced this:
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.8.2 calibration #2 (technical_control 4-leaf spine: "
            "configuration_baseline + procedure + monitoring_record + "
            "recertification). Stage-2 list_one short-circuit exposes the "
            "snapshotted reason — '0/4 children satisfied' is the multi-leaf "
            "signature. Pre-promotion single-leaf would have read '0/1'."
        ),
    ),

    EvalCase(
        id=43,
        query="pending engine verdict for A.5.2",
        tags=["posture", "engine", "stage2", "multi_leaf", "calibration"],
        expected_refs=["A.5.2"],
        expected_type="posture_check",
        must_contain=["A.5.2", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.2 calibration #3 (policy_program 4-leaf spine, "
            "governance-wrapper variant — primary artifact is the "
            "responsibility_matrix, not a policy doc; siblings are "
            "approval + communication_record + review_record). Same "
            "Stage-2 list_one surface; '0/4' is the multi-leaf signature."
        ),
    ),

    EvalCase(
        id=44,
        query="pending engine verdict for Art.30",
        tags=["posture", "engine", "stage2", "multi_leaf", "calibration", "gdpr"],
        expected_refs=["Art.30"],
        expected_type="posture_check",
        must_contain=["Art.30", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks Art.30 calibration #4 (records_program 4-leaf spine — "
            "the new sixth spine candidate from this batch: RoPA register + "
            "maintenance procedure + data_flow_inventory + annual review). "
            "Stage-2 list_one surface; '0/4' is the multi-leaf signature."
        ),
    ),

    EvalCase(
        id=45,
        query="pending engine verdict for Art.15",
        tags=["posture", "engine", "stage2", "multi_leaf", "calibration", "gdpr"],
        expected_refs=["Art.15"],
        expected_type="posture_check",
        must_contain=["Art.15", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks Art.15 calibration #5 (gdpr_rights 4-leaf spine: DSAR "
            "handling procedure + register + per-request response leaf "
            "[operational] + annual process review). Stage-2 list_one "
            "surface; '0/4' is the multi-leaf signature. Pre-promotion "
            "the single dsar_response operational leaf would have been "
            "the lone child."
        ),
    ),

    # ── Phase B records_program family (commit pending 2026-05-29) ──────────
    # First Phase B bulk batch: 5 ISO A.5 register-style controls promoted to
    # the records_program 4-leaf spine in one pass. A.5.32 is the adapted
    # variant (procedure leaf retained alongside the inventory). Same Stage-2
    # list_one surface + '0/4' signature as cases 42-45.

    EvalCase(
        id=46,
        query="pending engine verdict for A.5.5",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program"],
        expected_refs=["A.5.5"],
        expected_type="posture_check",
        must_contain=["A.5.5", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.5 (Authority contacts) Phase B promotion to "
            "records_program 4-leaf: authority_contact_register + "
            "maintenance_procedure + applicable_authorities_scope + "
            "periodic review. '0/4' is the multi-leaf signature; the "
            "single-leaf predecessor would have read '0/1'."
        ),
    ),

    EvalCase(
        id=47,
        query="pending engine verdict for A.5.6",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program"],
        expected_refs=["A.5.6"],
        expected_type="posture_check",
        must_contain=["A.5.6", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.6 (Contact with special interest groups) Phase B "
            "promotion to records_program 4-leaf: SIG register + "
            "engagement_procedure + risk_topic_scope + periodic review."
        ),
    ),

    EvalCase(
        id=48,
        query="pending engine verdict for A.5.9",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program"],
        expected_refs=["A.5.9"],
        expected_type="posture_check",
        must_contain=["A.5.9", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.9 (Inventory of information and associated assets) "
            "Phase B promotion to records_program 4-leaf with the stricter "
            "freshness model: register + lifecycle_procedure + "
            "discovery_upstream + reconciliation review. Both the register "
            "and the review carry freshness=90 (asset drift is daily — "
            "annual review would be insufficient). '0/4' is the multi-leaf "
            "signature."
        ),
    ),

    EvalCase(
        id=49,
        query="pending engine verdict for A.5.31",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program"],
        expected_refs=["A.5.31"],
        expected_type="posture_check",
        must_contain=["A.5.31", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.31 (Legal, statutory, regulatory and contractual "
            "requirements) Phase B promotion to records_program 4-leaf: "
            "obligations_register + maintenance_procedure + "
            "applicable_obligations_scope + periodic review with "
            "freshness=180 (semi-annual cadence preserved from the "
            "single-leaf predecessor's freshness signal)."
        ),
    ),

    EvalCase(
        id=50,
        query="pending engine verdict for A.5.32",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "adapted"],
        expected_refs=["A.5.32"],
        expected_type="posture_check",
        must_contain=["A.5.32", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.32 (Intellectual property rights) Phase B promotion "
            "to records_program *adapted* 4-leaf — IPR has both procedural "
            "and inventory aspects, so the procedure leaf (existing id) is "
            "retained alongside the new licensed_software_ipr_inventory "
            "register, the acquired_works_upstream intake, and a periodic "
            "IPR audit. The licensed_inventory + renewal_tracking items "
            "moved from the procedure leaf to the new inventory leaf; the "
            "audit_cadence item moved to the new review leaf. '0/4' is the "
            "multi-leaf signature."
        ),
    ),

    # ── Phase B policy_program family (commit pending 2026-05-29) ──────────
    # Second Phase B bulk batch: 5 ISO A.5 policy/governance controls promoted
    # to the policy_program 4-leaf spine (primary artefact + approval +
    # communication_record + periodic review). A.5.3 uses a segregation_matrix
    # primary leaf; A.5.4 uses a management_directive; A.5.10/A.5.12/A.5.15
    # use the conventional policy/scheme artefact. A.5.15 already has the
    # access control policy uploaded, so its engine signature is OFI at 1/4
    # rather than NC at 0/4 — locks that distinction.

    EvalCase(
        id=51,
        query="pending engine verdict for A.5.3",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program"],
        expected_refs=["A.5.3"],
        expected_type="posture_check",
        must_contain=["A.5.3", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.3 (Segregation of duties) Phase B promotion to "
            "policy_program 4-leaf with the matrix variant: segregation_matrix "
            "+ approval + communication_record + periodic review. '0/4' is "
            "the multi-leaf signature; the single-leaf predecessor would have "
            "read '0/1'."
        ),
    ),

    EvalCase(
        id=52,
        query="pending engine verdict for A.5.4",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program"],
        expected_refs=["A.5.4"],
        expected_type="posture_check",
        must_contain=["A.5.4", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.4 (Management responsibilities) Phase B promotion to "
            "policy_program 4-leaf with the directive variant: "
            "management_directive + approval + communication_record + "
            "periodic review."
        ),
    ),

    EvalCase(
        id=53,
        query="pending engine verdict for A.5.10",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program"],
        expected_refs=["A.5.10"],
        expected_type="posture_check",
        must_contain=["A.5.10", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.10 (Acceptable use) Phase B promotion to policy_program "
            "4-leaf: acceptable_use_policy + approval + communication_record + "
            "periodic review. AUPs are enforceability-sensitive — the "
            "communication leaf carries an explicit user-acknowledgement item."
        ),
    ),

    EvalCase(
        id=54,
        query="pending engine verdict for A.5.12",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program"],
        expected_refs=["A.5.12"],
        expected_type="posture_check",
        must_contain=["A.5.12", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.12 (Information classification) Phase B promotion to "
            "policy_program 4-leaf: classification_scheme + approval + "
            "communication_record + periodic review. Classification feeds "
            "A.5.13 / A.5.10 / A.5.14 downstream so the communication leaf "
            "targets all information creators, not just data owners."
        ),
    ),

    EvalCase(
        id=55,
        query="pending engine verdict for A.5.15",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "partial_evidence"],
        expected_refs=["A.5.15"],
        expected_type="posture_check",
        # A.5.15 differs from the other 4 in this batch: the access control
        # policy is already uploaded on Arion (legacy single-leaf evidence
        # carried forward), so 1 of the 4 leaves is satisfied. Engine output
        # is therefore 'OFI' at '1/4', not 'NC' at '0/4'. This locks the
        # partial-evidence multi-leaf path — a useful complement to the
        # 0/N-NC default the other Phase B cases exercise.
        must_contain=["A.5.15", "engine proposes", "'OFI'", "1/4 children satisfied"],
        must_not_contain=[
            "0/4 children satisfied",
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.15 (Access control policy) Phase B promotion to "
            "policy_program 4-leaf with the partial-evidence shape: the "
            "policy leaf is satisfied (legacy upload) but approval, "
            "communication and review leaves are not, so engine proposes "
            "'OFI' at '1/4 children satisfied'. Companion to cases 46-50 "
            "which all sit at 0/4."
        ),
    ),

    # ── Phase B operational_process supplier+cloud 5-pack (commit 2026-05-31) ──
    # Third Phase B bulk batch: A.5.19, A.5.20, A.5.21, A.5.22, A.5.23 all
    # promoted to the operational_process 4-leaf spine. The four supplier
    # controls (A.5.19-22) form the supplier lifecycle (select → agree →
    # operate → review/exit); A.5.23 extends the same shape to cloud services.
    # Per-control primary-leaf variants:
    #   A.5.19  procedure       + supplier_register     + portfolio_review     + offboarding
    #   A.5.20  agreement_tpl   + coverage_register     + template_review      + deviations
    #   A.5.21  procedure       + ict_component_register + supply_chain_review + eol_replacement
    #   A.5.22  review_record   + schedule_register     + program_meta_review  + change_response_log
    #   A.5.23  policy          + cloud_service_register + cloud_posture_review + exit_migration
    # A.5.23 is profile_fact-triggered (only fires for cloud-using tenants) AND
    # already had its policy leaf uploaded on Arion, so engine sits at OFI 1/4
    # — same partial-evidence path locked by case 55 for A.5.15.

    EvalCase(
        id=56,
        query="pending engine verdict for A.5.19",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process"],
        expected_refs=["A.5.19"],
        expected_type="posture_check",
        must_contain=["A.5.19", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.19 (InfoSec in supplier relationships) Phase B "
            "promotion to operational_process 4-leaf: supplier_risk_procedure "
            "+ supplier_register + portfolio_review + offboarding_record. "
            "Procedure leaf id preserved from single-leaf predecessor. '0/4' "
            "is the multi-leaf signature; pre-promotion would have read '0/1'."
        ),
    ),

    EvalCase(
        id=57,
        query="pending engine verdict for A.5.20",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process"],
        expected_refs=["A.5.20"],
        expected_type="posture_check",
        must_contain=["A.5.20", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.20 (Security in supplier agreements) Phase B promotion "
            "to operational_process 4-leaf with the agreement-template "
            "variant: agreement_template + coverage_register + template_review "
            "+ deviation_register. Lifecycle-end slot is realised as the "
            "deviation register — each softened or omitted clause is the "
            "supplier 'exiting' the standard template path."
        ),
    ),

    EvalCase(
        id=58,
        query="pending engine verdict for A.5.21",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process"],
        expected_refs=["A.5.21"],
        expected_type="posture_check",
        must_contain=["A.5.21", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.21 (ICT supply chain) Phase B promotion to "
            "operational_process 4-leaf: ict_supply_chain_procedure + "
            "ict_component_register + supply_chain_review (freshness 180d) + "
            "eol_replacement_record. Review freshness tightened from default "
            "365d to 180d because ICT supply chain volatility (M&A, EOL "
            "pipelines, vuln disclosures) outpaces an annual cadence."
        ),
    ),

    EvalCase(
        id=59,
        query="pending engine verdict for A.5.22",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process"],
        expected_refs=["A.5.22"],
        expected_type="posture_check",
        must_contain=["A.5.22", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.22 (Monitoring + change mgmt of supplier services) "
            "Phase B promotion to operational_process 4-leaf with the "
            "review-record-shaped variant: supplier_review_record + "
            "review_schedule_register + program_meta_review + "
            "change_response_log. Lifecycle-end slot is the change-response "
            "log — each supplier-side change (network/tech/location/sub-"
            "contractor/re-tendering) is the lifecycle event requiring "
            "documented response."
        ),
    ),

    EvalCase(
        id=60,
        query="pending engine verdict for A.5.23",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "partial_evidence", "profile_fact"],
        expected_refs=["A.5.23"],
        expected_type="posture_check",
        # A.5.23 differs from the other 4 in this batch: the cloud services
        # policy leaf is already uploaded on Arion (legacy single-leaf
        # evidence carried forward), so 1 of the 4 leaves is satisfied.
        # Engine output is therefore 'OFI' at '1/4', not 'NC' at '0/4'.
        # This re-exercises the partial-evidence multi-leaf path that case
        # 55 first introduced for A.5.15. A.5.23 is also profile_fact-
        # triggered (only fires for cloud-using tenants), so this case
        # additionally locks the profile_fact + partial-evidence combination.
        must_contain=["A.5.23", "engine proposes", "'OFI'", "1/4 children satisfied"],
        must_not_contain=[
            "0/4 children satisfied",
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.23 (InfoSec for use of cloud services) Phase B "
            "promotion to operational_process 4-leaf adapted: "
            "cloud_services_policy + cloud_service_register + "
            "cloud_posture_review + exit_migration_record. Partial-evidence "
            "shape (engine OFI 1/4, not NC 0/4) because the policy leaf was "
            "already satisfied via legacy upload. Companion to case 55 — "
            "second partial-evidence case in the suite, and the first one "
            "that combines partial evidence with profile_fact triggering."
        ),
    ),

    # ── Phase B operational_process incident triage 3-pack (commit 2026-05-31) ──
    # Fourth Phase B bulk batch: A.5.25 (event triage), A.5.26 (incident
    # response), A.5.27 (lessons learned) promoted to operational_process
    # 4-leaf. All three controls are clean procedure-shaped, so the spine
    # applies without primary-leaf variant — only the lifecycle-end slot
    # adapts per control: triage_decision_record / incident_closure_record /
    # improvement_action_record. Cross-control linkages: A.5.25 closure
    # (=incident) feeds A.5.26 register; A.5.26 closure feeds A.5.27 register.
    #
    # Eval coverage: cases 61 + 62 for A.5.25 + A.5.27 via the standard
    # Stage-2 list_one surface. A.5.26 is NOT in the eval suite — its engine
    # verdict ('NC' at '0/4 children satisfied') is verified via direct
    # compute_engine_verdicts() invocation but does not surface through
    # Stage-2 because the engine agrees with the tenant's live finding
    # (both NC). posture_loader.py:343 intentionally suppresses no-op
    # proposals to keep the Stage-2 queue clean. If the tenant ever flips
    # A.5.26 to OFI/Comply, the engine proposal will reappear and a future
    # eval case could cover it.

    EvalCase(
        id=61,
        query="pending engine verdict for A.5.25",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "incident_family"],
        expected_refs=["A.5.25"],
        expected_type="posture_check",
        must_contain=["A.5.25", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.25 (Event assessment + triage) Phase B promotion to "
            "operational_process 4-leaf: event_assessment_procedure + "
            "event_triage_log + triage_program_review (freshness 180d) + "
            "triage_decision_record. Live posture flips from Comply to "
            "engine-proposed NC at 0/4 — engine sees no evidence on any of "
            "the 4 sibling leaves. Review freshness 180d because event "
            "landscape volatility (new detection sources, attack pattern "
            "shifts, false-positive calibration) outpaces annual cadence."
        ),
    ),

    EvalCase(
        id=62,
        query="pending engine verdict for A.5.27",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "incident_family"],
        expected_refs=["A.5.27"],
        expected_type="posture_check",
        must_contain=["A.5.27", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.27 (Learning from incidents) Phase B promotion to "
            "operational_process 4-leaf: lessons_learned_procedure + "
            "lessons_register + lessons_program_review + "
            "improvement_action_record. Live posture flips from Comply to "
            "engine-proposed NC at 0/4. The improvement_action_record "
            "lifecycle-end leaf is the loop-closure evidence: per-lesson, "
            "the actual control / training / procedure change that strengthens"
            " the org (per ISO 27002 § 5.27a)."
        ),
    ),

    # ── Phase B operational_process threat intelligence (commit 2026-05-31) ──
    # Fifth Phase B bulk batch (single-control): A.5.7 promoted to
    # operational_process 4-leaf — threat_intelligence_procedure +
    # threat_intel_feed_register + threat_intel_program_review (180d) +
    # intel_product_record. The lifecycle-end slot is the per-product
    # intelligence record (each IOC list / advisory / briefing delivered to
    # a named consumer). Review freshness 180d for the same detection-
    # landscape rationale as A.5.25 + A.5.26. Cross-control: feed register
    # captures internal sources from A.5.6 SIG outputs; program review
    # checks consumer feedback from A.5.21 / A.5.25 / A.5.27.

    EvalCase(
        id=63,
        query="pending engine verdict for A.5.7",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "threat_intel"],
        expected_refs=["A.5.7"],
        expected_type="posture_check",
        must_contain=["A.5.7", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.7 (Threat intelligence) Phase B promotion to "
            "operational_process 4-leaf: threat_intelligence_procedure + "
            "threat_intel_feed_register + threat_intel_program_review "
            "(freshness 180d) + intel_product_record. Live posture flips "
            "from Comply (PIMS-tagged hand-entered finding) to engine-"
            "proposed NC at 0/4 — engine sees no per-leaf evidence on any "
            "of the 4 siblings. Review freshness 180d because threat "
            "landscape volatility (feed quality shifts, IOC libraries age "
            "within weeks, new TTPs emerge inside a quarter) outpaces "
            "annual cadence — same rationale as A.5.25 + A.5.26 in batch 4."
        ),
    ),

    # ── Phase B operational_process evidence handling (commit 2026-05-31) ──
    # Sixth Phase B bulk batch (single-control): A.5.28 promoted to
    # operational_process 4-leaf — evidence_collection_procedure +
    # evidence_custody_register + evidence_program_review (365d) +
    # evidence_disposal_record. Closes the incident-evidence triangle
    # alongside A.5.25-27 already shipped in batch 4. A.5.26's evidence-
    # archive SHOULD now resolves to the A.5.28 custody register entry;
    # the disposal_record proves chain-of-custody was maintained to
    # legitimate end (external handover OR retention-driven destruction).
    # Review freshness 365d — evidence-handling discipline is forensically
    # stable (does NOT churn like threat-intel or detection landscape).
    #
    # Batch 7 (A.5.1 Style v1 → v2 alignment, commit 2026-05-31) was
    # alignment-only with no new eval case — existing cases 33/34/36/38
    # already lock A.5.1's OFI verdict.

    EvalCase(
        id=64,
        query="pending engine verdict for A.5.28",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "evidence_handling"],
        expected_refs=["A.5.28"],
        expected_type="posture_check",
        must_contain=["A.5.28", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.28 (Collection of evidence) Phase B promotion to "
            "operational_process 4-leaf: evidence_collection_procedure + "
            "evidence_custody_register + evidence_program_review (freshness "
            "365d) + evidence_disposal_record. Live posture flips from "
            "Comply (hand-entered Audit Log / Incident Log finding) to "
            "engine-proposed NC at 0/4. The disposal_record lifecycle-end "
            "leaf is the *end* of the chain of custody — proves the program "
            "actually closes the loop on every evidence package (external "
            "handover with receipt OR retention-driven destruction with "
            "witness + final hash). Review freshness 365d because evidence-"
            "handling discipline is forensically stable (legal admissibility "
            "rules, retention obligations and forensic methodology don't "
            "churn the way threat-intel or detection landscape does)."
        ),
    ),

    # ── Phase B operational_process project security (commit 2026-05-31) ──
    # Eighth Phase B bulk batch (single-control): A.5.8 promoted to
    # operational_process 4-leaf — project_management_security_integration
    # procedure + project_security_register + project_security_program_review
    # (365d) + project_security_closure_record. The lifecycle-end is per-
    # project closure signoff (three-way: sponsor + InfoSec + operational
    # owner). Cross-control linkages to A.8.25/A.8.26 SDLC + A.5.20 supplier
    # agreements + A.5.23 cloud register + A.5.27 lessons capture.

    EvalCase(
        id=65,
        query="pending engine verdict for A.5.8",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "project_security"],
        expected_refs=["A.5.8"],
        expected_type="posture_check",
        must_contain=["A.5.8", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.8 (Information security in project management) Phase "
            "B promotion to operational_process 4-leaf: "
            "project_management_security_integration procedure + "
            "project_security_register + project_security_program_review "
            "(freshness 365d) + project_security_closure_record. Live "
            "posture flips from Comply (hand-entered finding citing 'default "
            "integration with ISMS Manager consultation') to engine-proposed "
            "NC at 0/4 — engine sees no per-leaf evidence on any of the 4 "
            "siblings. The closure_record lifecycle-end leaf is the three-way "
            "signoff (sponsor + InfoSec + operational owner) that proves "
            "each project actually closed out security accountability rather "
            "than just dissolved the team. Review freshness 365d because "
            "project-management methodologies are structurally stable, unlike "
            "detection landscape (180d) or threat-intel feeds (180d)."
        ),
    ),

    # ── Phase B operational_process return-of-assets (commit 2026-05-31) ──
    # Ninth Phase B bulk batch (single-control): A.5.11 promoted to
    # operational_process 4-leaf — return_of_assets_procedure +
    # leaver_return_register + return_program_review (365d) + per-leaver
    # return_record. Cross-control linkages to A.5.9 asset register
    # (which assets the leaver had) + A.8.10 information deletion (data
    # wipe path). Review freshness 365d (HR methodology stable).

    EvalCase(
        id=66,
        query="pending engine verdict for A.5.11",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "return_of_assets"],
        expected_refs=["A.5.11"],
        expected_type="posture_check",
        must_contain=["A.5.11", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.11 (Return of assets) Phase B promotion to "
            "operational_process 4-leaf: return_of_assets_procedure + "
            "leaver_return_register + return_program_review (freshness 365d) "
            "+ per-leaver return_record. Live posture flips from Comply "
            "(hand-entered BYOD-justified finding) to engine-proposed NC at "
            "0/4. The return_record lifecycle-end leaf is the per-leaver "
            "closure event with dual signoff (returning party + receiving "
            "role) — captures BOTH confirmed returns AND documented non-"
            "returns with risk-accepted write-off, so the leaver is closed "
            "out either way. Review freshness 365d because HR offboarding "
            "methodology is stable (changes only when workforce model "
            "shifts — remote-vs-onsite, contractor mix, BYOD policy)."
        ),
    ),

    # ── Phase B operational_process information-labelling (commit 2026-05-31) ──
    # Tenth Phase B bulk batch (single-control): A.5.13 promoted to
    # operational_process 4-leaf — information_labelling_procedure +
    # labelling_coverage_register + labelling_program_review (365d) +
    # per-platform labelling_application_record. Cascade pair with A.5.12
    # classification (already 4-leaf policy_program from batch 2): the
    # scheme lives in A.5.12, application of the scheme lives here.

    EvalCase(
        id=67,
        query="pending engine verdict for A.5.13",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "labelling"],
        expected_refs=["A.5.13"],
        expected_type="posture_check",
        must_contain=["A.5.13", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.13 (Labelling of information) Phase B promotion to "
            "operational_process 4-leaf: information_labelling_procedure + "
            "labelling_coverage_register + labelling_program_review "
            "(freshness 365d) + per-platform labelling_application_record. "
            "Live posture flips from Comply (hand-entered Purview-based "
            "finding) to engine-proposed NC at 0/4. The application_record "
            "lifecycle-end leaf is the per-platform enablement proof — "
            "every system that came online had labelling extended to it, "
            "not just the platforms IT remembered to configure first. "
            "Review freshness 365d because labelling cascades from A.5.12 "
            "classification (parent scheme; reviewing labelling out of "
            "sync produces misaligned controls)."
        ),
    ),

    # ── Phase B policy_program information-transfer (commit 2026-05-31) ──
    # Eleventh Phase B bulk batch (single-control): A.5.14 promoted to
    # policy_program 4-leaf — information_transfer_policy + management_
    # approval + communication_record + periodic_review (365d). Same shape
    # as A.5.10/A.5.12/A.5.15 from batch 2. Cascade from A.5.12
    # classification scheme via scheme_alignment MUST. Cross-link to A.5.20
    # supplier agreements for the transfer-agreements SHOULD path. New
    # legal_jurisdiction MUST explicitly aligns with GDPR Chap V (Art.44-49)
    # international-transfer mechanisms — first batch where ISO + GDPR
    # alignment is encoded directly in a MUST citation rationale.

    EvalCase(
        id=68,
        query="pending engine verdict for A.5.14",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "information_transfer"],
        expected_refs=["A.5.14"],
        expected_type="posture_check",
        must_contain=["A.5.14", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.14 (Information transfer) Phase B promotion to "
            "policy_program 4-leaf: information_transfer_policy + "
            "management_approval + communication_record + periodic_review "
            "(freshness 365d). Live posture flips from Comply (hand-entered "
            "finding citing Microsoft 365 + SSPA + GDPR coverage) to engine-"
            "proposed NC at 0/4 — engine sees no per-leaf evidence on any "
            "of the 4 siblings. First policy_program batch since batch 2 "
            "(A.5.10/A.5.12/A.5.15) — re-validates the spine consistency. "
            "New legal_jurisdiction MUST explicitly aligns with GDPR Chap V "
            "(Art.44-49) international-transfer mechanisms — codifies the "
            "ISO × GDPR alignment at the spec level, following pii_overlay "
            "in batch 10."
        ),
    ),

    # ── Phase B operational_process identity-management (commit 2026-05-31) ──
    # Twelfth Phase B bulk batch (single-control): A.5.16 promoted to
    # operational_process 4-leaf — identity_management_procedure +
    # identity_register + identity_program_review (180d) +
    # per-identity revocation_record. Review freshness 180d because
    # identity drift is high-volume (matches A.5.25/A.5.26 detection-
    # landscape volatility family). Cross-control links to A.5.11 leaver
    # register (joiner/leaver cascade), A.5.17 authentication
    # information (paired credential lifecycle), A.5.18 access rights
    # review (attestation cadence). service_accounts MUST is the key
    # promotion — was a SHOULD, now MUST because service-account hygiene
    # is the weakest spot in most orgs' identity programs.

    EvalCase(
        id=69,
        query="pending engine verdict for A.5.16",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "identity_management"],
        expected_refs=["A.5.16"],
        expected_type="posture_check",
        must_contain=["A.5.16", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.16 (Identity management) Phase B promotion to "
            "operational_process 4-leaf: identity_management_procedure + "
            "identity_register + identity_program_review (freshness 180d) "
            "+ per-identity revocation_record. Live posture flips from "
            "Comply (empty gap_description hand-entered) to engine-proposed "
            "NC at 0/4. The revocation_record lifecycle-end leaf is the "
            "per-identity disable proof with an auditor-critical SLA-met "
            "flag — proves not just THAT each identity was disabled but "
            "that the disable timestamp was within the stated SLA "
            "(e.g. 'X was disabled within 24h of last day'). Review "
            "freshness 180d because identity drift is high-volume; matches "
            "A.5.25/A.5.26 detection-landscape velocity family. "
            "service_accounts MUST (was SHOULD pre-promotion) makes the "
            "auditor-critical weakest-spot governance a first-class "
            "requirement."
        ),
    ),

    # ── Phase B operational_process authentication-info (commit 2026-05-31) ──
    # Thirteenth Phase B bulk batch (single-control): A.5.17 promoted to
    # operational_process 4-leaf — authentication_information_procedure +
    # credential_register + authentication_program_review (180d) +
    # per-credential revocation_record. Naturally PAIRED with A.5.16
    # identity management (batch 12). Each identity event in A.5.16
    # typically has a paired credential event in A.5.17 — pairing
    # enforced via authn_link (A.5.16) and identity_link (A.5.17) MUSTs.
    # MFA promoted SHOULD → MUST (modern baseline, no longer optional).

    # ── Phase B A.8 Technological Controls 33-pack (commit 2026-06-01) ──
    # Twenty-third Phase B bulk batch (THIRTY-THREE controls): all of A.8.1 +
    # A.8.3 through A.8.34 promoted to 4-leaf — LARGEST batch yet by 2.4×
    # (previous: A.7 14-pack). 132 new evidence requirements. A.8.2 was
    # already 4-leaf from 2026-05-26 calibration; Style v2 aligned in this
    # batch (locked by existing case #42; no new case here). Closes A.8 block.
    #
    # Spine mix: 8×policy_program (A.8.1/18/20/23/24/25/27/34) +
    # 20×op_process (A.8.3/7/8/9/10/11/13/15/16/17/19/21/22/26/28/29/30/31/32/33) +
    # 5×technical_control (A.8.4/5/6/12/14). A.8.10 + A.8.13 + A.8.32 carry
    # lifecycle-end record variants (disposal / restore-test / change record).
    #
    # Tombstone consolidation: A.8.11/A.8.24/A.8.25 were single-leaf entries
    # at upstream locations in document_requirements.py; tombstoned to stub
    # comments and rebuilt in the consolidated A.8 block. Item-id preservation
    # (referenced by SPECs): SPEC_ART_32 → A.8.24 (personal_data, pii_keys,
    # at_rest, in_transit); SPEC_ART_25 → A.8.11 (scope, techniques,
    # personal_data); SPEC_ART_25 comment → A.8.10 (scope_systems).
    #
    # Live postures across the 33 promotions: predominantly Comply (~28),
    # with A.8.25 N/A (Arion does not develop external-facing software, A.8.25
    # is profile_fact triggered, currently N/A) and a handful of OFI (A.8.1
    # endpoints, A.8.19 software install). All 33 engine verdicts: NC 0/4
    # (or 0/5 for A.8.24/34 if loader didn't prune orphan EvidenceRequirement
    # nodes — see [[loader-er-orphan-cleanup-followup]] for the cleanup
    # performed in this batch). All surface in Stage-2 (engine NC ≠ live
    # Comply AND ≠ live OFI AND ≠ live N/A — only NC==NC suppresses).

    EvalCase(
        id=132,
        query="pending engine verdict for A.8.1",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "endpoints"],
        expected_refs=["A.8.1"], expected_type="posture_check",
        must_contain=["A.8.1", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.1 (User endpoint devices) — policy_program 4-leaf: policy + endpoint_register + applicable_endpoint_scope + program_review (365d). FIRST control of A.8 33-pack (batch 23).",
    ),

    EvalCase(
        id=131,
        query="pending engine verdict for A.8.3",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "access_restriction"],
        expected_refs=["A.8.3"], expected_type="posture_check",
        must_contain=["A.8.3", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.3 (Information access restriction) — op_process 4-leaf: procedure + access_matrix_register + applicable_systems_scope + program_review (365d).",
    ),

    EvalCase(
        id=130,
        query="pending engine verdict for A.8.4",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "technical_control", "source_code", "profile_fact"],
        expected_refs=["A.8.4"], expected_type="posture_check",
        must_contain=["A.8.4", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.4 (Source code access) — technical_control 4-leaf: baseline + procedure + monitoring_log + review (180d). profile_fact trigger (org develops software).",
    ),

    EvalCase(
        id=129,
        query="pending engine verdict for A.8.5",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "technical_control", "secure_auth"],
        expected_refs=["A.8.5"], expected_type="posture_check",
        must_contain=["A.8.5", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.5 (Secure authentication) — technical_control 4-leaf: baseline + procedure + auth_log + review (180d). MFA universal/privileged + impossible-travel detection promoted to MUST.",
    ),

    EvalCase(
        id=128,
        query="pending engine verdict for A.8.6",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "technical_control", "capacity"],
        expected_refs=["A.8.6"], expected_type="posture_check",
        must_contain=["A.8.6", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.6 (Capacity management) — technical_control 4-leaf: baseline + procedure + monitoring_log + review (365d). Auto-scaling promoted to MUST.",
    ),

    EvalCase(
        id=127,
        query="pending engine verdict for A.8.7",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "malware"],
        expected_refs=["A.8.7"], expected_type="posture_check",
        must_contain=["A.8.7", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.7 (Malware protection) — op_process 4-leaf: procedure + coverage_register + applicable_scope + review (180d). Behavioural detection promoted to MUST.",
    ),

    EvalCase(
        id=126,
        query="pending engine verdict for A.8.8",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "vuln_mgmt"],
        expected_refs=["A.8.8"], expected_type="posture_check",
        must_contain=["A.8.8", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.8 (Technical vulnerabilities) — op_process 4-leaf: procedure + vulnerability_backlog_register + applicable_scope + review (180d). SLA-breach flag is auditor-critical.",
    ),

    EvalCase(
        id=125,
        query="pending engine verdict for A.8.9",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "config_mgmt"],
        expected_refs=["A.8.9"], expected_type="posture_check",
        must_contain=["A.8.9", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.9 (Configuration management) — op_process 4-leaf: procedure + baseline_register + applicable_scope + review (365d).",
    ),

    EvalCase(
        id=124,
        query="pending engine verdict for A.8.10",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "data_deletion", "lifecycle_end"],
        expected_refs=["A.8.10"], expected_type="posture_check",
        must_contain=["A.8.10", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.10 (Information deletion) — op_process 4-leaf with disposal_record lifecycle-end: procedure + disposal_register + applicable_scope + review (365d). item:A.8.10:scope_systems referenced by SPEC_ART_25 comment — preserved.",
    ),

    EvalCase(
        id=123,
        query="pending engine verdict for A.8.11",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "data_masking", "tombstone_consolidation"],
        expected_refs=["A.8.11"], expected_type="posture_check",
        must_contain=["A.8.11", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.11 (Data masking) — op_process 4-leaf, tombstone consolidation from upstream REQ_DATA_MASKING: procedure + masking_register + applicable_scope + review (365d). Items preserved for SPEC_ART_25: scope, techniques, personal_data.",
    ),

    EvalCase(
        id=122,
        query="pending engine verdict for A.8.12",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "technical_control", "dlp"],
        expected_refs=["A.8.12"], expected_type="posture_check",
        must_contain=["A.8.12", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.12 (DLP) — technical_control 4-leaf: baseline + procedure + alert_log + review (180d).",
    ),

    EvalCase(
        id=121,
        query="pending engine verdict for A.8.13",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "backup", "lifecycle_end"],
        expected_refs=["A.8.13"], expected_type="posture_check",
        must_contain=["A.8.13", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.13 (Information backup) — op_process 4-leaf with restore_test_record lifecycle-end: procedure + restore_test_register + applicable_scope + review (365d). RPO-met flag auditor-critical (parallels A.5.30).",
    ),

    EvalCase(
        id=120,
        query="pending engine verdict for A.8.14",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "technical_control", "redundancy"],
        expected_refs=["A.8.14"], expected_type="posture_check",
        must_contain=["A.8.14", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.14 (Redundancy of IPF) — technical_control 4-leaf: baseline + procedure + failover_test_register + review (365d). Cross-AZ/region promoted to MUST.",
    ),

    EvalCase(
        id=119,
        query="pending engine verdict for A.8.15",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "logging"],
        expected_refs=["A.8.15"], expected_type="posture_check",
        must_contain=["A.8.15", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.15 (Logging) — op_process 4-leaf: procedure + source_register + applicable_scope + review (180d). Log-integrity verification promoted to MUST.",
    ),

    EvalCase(
        id=118,
        query="pending engine verdict for A.8.16",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "monitoring"],
        expected_refs=["A.8.16"], expected_type="posture_check",
        must_contain=["A.8.16", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.16 (Monitoring activities) — op_process 4-leaf: procedure + detection_register + applicable_scope + review (180d). SIEM use cases + threat-hunting promoted to MUST.",
    ),

    EvalCase(
        id=117,
        query="pending engine verdict for A.8.17",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "clock_sync"],
        expected_refs=["A.8.17"], expected_type="posture_check",
        must_contain=["A.8.17", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.17 (Clock synchronisation) — op_process 4-leaf: procedure + sync_register + applicable_scope + review (365d).",
    ),

    EvalCase(
        id=116,
        query="pending engine verdict for A.8.18",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "privileged_utility"],
        expected_refs=["A.8.18"], expected_type="posture_check",
        must_contain=["A.8.18", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.18 (Privileged utility programs) — policy_program 4-leaf: policy + utility_register + applicable_scope + review (365d). Removal-where-unneeded promoted to MUST.",
    ),

    EvalCase(
        id=115,
        query="pending engine verdict for A.8.19",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "software_install"],
        expected_refs=["A.8.19"], expected_type="posture_check",
        must_contain=["A.8.19", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.19 (Software installation on operational systems) — op_process 4-leaf: procedure + installation_register + applicable_scope + review (365d). Allowlisting promoted to MUST.",
    ),

    EvalCase(
        id=114,
        query="pending engine verdict for A.8.20",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "networks"],
        expected_refs=["A.8.20"], expected_type="posture_check",
        must_contain=["A.8.20", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.20 (Networks security) — policy_program 4-leaf: policy + network_register + applicable_scope + review (365d). Zero-trust direction promoted to MUST.",
    ),

    EvalCase(
        id=113,
        query="pending engine verdict for A.8.21",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "network_services"],
        expected_refs=["A.8.21"], expected_type="posture_check",
        must_contain=["A.8.21", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.21 (Security of network services) — op_process 4-leaf: procedure + service_register + applicable_scope + review (180d). A.5.22 supplier review linkage.",
    ),

    EvalCase(
        id=112,
        query="pending engine verdict for A.8.22",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "network_segregation"],
        expected_refs=["A.8.22"], expected_type="posture_check",
        must_contain=["A.8.22", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.22 (Network segregation) — op_process 4-leaf: procedure + zone_register + applicable_scope + review (365d). Micro-segmentation direction promoted to MUST.",
    ),

    EvalCase(
        id=111,
        query="pending engine verdict for A.8.23",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "web_filtering"],
        expected_refs=["A.8.23"], expected_type="posture_check",
        must_contain=["A.8.23", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.23 (Web filtering) — policy_program 4-leaf: policy + filtering_event_register + applicable_scope + review (365d).",
    ),

    EvalCase(
        id=110,
        query="pending engine verdict for A.8.24",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "cryptography", "tombstone_consolidation", "spec_art_32"],
        expected_refs=["A.8.24"], expected_type="posture_check",
        must_contain=["A.8.24", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.24 (Use of cryptography) — policy_program 4-leaf, tombstone consolidation from upstream REQ_ENCRYPTION_POLICY: policy + key_register + applicable_scope + program_review (180d). Items preserved for SPEC_ART_32: personal_data, pii_keys, at_rest, in_transit. Key-strength + PQ direction noted.",
    ),

    EvalCase(
        id=109,
        query="pending engine verdict for A.8.25",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "secure_development", "tombstone_consolidation", "profile_fact"],
        expected_refs=["A.8.25"], expected_type="posture_check",
        must_contain=["A.8.25", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.25 (Secure development lifecycle) — policy_program 4-leaf, tombstone consolidation from upstream REQ_SECURE_DEVELOPMENT: policy + project_register + applicable_scope + review (180d). profile_fact trigger preserved (A.8.25 only applies when org develops software).",
    ),

    EvalCase(
        id=108,
        query="pending engine verdict for A.8.26",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "app_sec_req", "profile_fact"],
        expected_refs=["A.8.26"], expected_type="posture_check",
        must_contain=["A.8.26", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.26 (Application security requirements) — op_process 4-leaf: procedure + application_register + applicable_scope + review (365d). Threat-modelling promoted to MUST.",
    ),

    EvalCase(
        id=107,
        query="pending engine verdict for A.8.27",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "arch_principles", "profile_fact"],
        expected_refs=["A.8.27"], expected_type="posture_check",
        must_contain=["A.8.27", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.27 (Secure architecture/engineering principles) — policy_program 4-leaf: policy + architecture_register + applicable_scope + review (365d). Threat-modelling integration promoted to MUST.",
    ),

    EvalCase(
        id=106,
        query="pending engine verdict for A.8.28",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "secure_coding", "profile_fact"],
        expected_refs=["A.8.28"], expected_type="posture_check",
        must_contain=["A.8.28", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.28 (Secure coding) — op_process 4-leaf: procedure + finding_register + applicable_scope + review (365d). SCA/dependency scanning promoted to MUST.",
    ),

    EvalCase(
        id=105,
        query="pending engine verdict for A.8.29",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "sec_testing", "profile_fact"],
        expected_refs=["A.8.29"], expected_type="posture_check",
        must_contain=["A.8.29", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.29 (Security testing in dev/acceptance) — op_process 4-leaf: procedure + test_register + applicable_scope + review (180d). Pen-test cadence promoted to MUST.",
    ),

    EvalCase(
        id=104,
        query="pending engine verdict for A.8.30",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "outsourced_dev", "profile_fact"],
        expected_refs=["A.8.30"], expected_type="posture_check",
        must_contain=["A.8.30", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.30 (Outsourced development) — op_process 4-leaf: procedure + engagement_register + applicable_scope + review (365d). Maturity assessment promoted to MUST.",
    ),

    EvalCase(
        id=103,
        query="pending engine verdict for A.8.31",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "env_separation", "profile_fact"],
        expected_refs=["A.8.31"], expected_type="posture_check",
        must_contain=["A.8.31", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.31 (Dev/test/prod environment separation) — op_process 4-leaf: procedure + environment_register + applicable_scope + review (365d). IaC promoted to MUST. No-prod-data spot-check in review.",
    ),

    EvalCase(
        id=102,
        query="pending engine verdict for A.8.32",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "change_mgmt", "lifecycle_end"],
        expected_refs=["A.8.32"], expected_type="posture_check",
        must_contain=["A.8.32", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.32 (Change management) — op_process 4-leaf with change_record lifecycle-end: procedure + change_register + applicable_scope + review (365d). CI/CD integration promoted to MUST.",
    ),

    EvalCase(
        id=101,
        query="pending engine verdict for A.8.33",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "test_info", "profile_fact"],
        expected_refs=["A.8.33"], expected_type="posture_check",
        must_contain=["A.8.33", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.33 (Test information) — op_process 4-leaf: procedure + test_dataset_register + applicable_scope + review (365d). DPIA-consideration MUST flagged personal_data.",
    ),

    EvalCase(
        id=100,
        query="pending engine verdict for A.8.34",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "audit_testing"],
        expected_refs=["A.8.34"], expected_type="posture_check",
        must_contain=["A.8.34", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.8.34 (Audit testing protection) — policy_program 4-leaf: policy + audit_engagement_register + applicable_scope + program_review (365d). Dedicated test accounts promoted to MUST. LAST control of A.8 33-pack (batch 23).",
    ),

    # ── Phase B A.7 Physical Controls 14-pack (commit 2026-06-01) ──
    # Twenty-second Phase B bulk batch (FOURTEEN controls): all of A.7.1 through
    # A.7.14 promoted to 4-leaf — LARGEST batch yet (previous: A.6 7-pack). 56
    # new evidence requirements. Closes the A.7 Physical Controls block.
    #
    # Spine mix: 11×op_process + 3×policy_program (A.7.1 perimeter, A.7.7 clear
    # desk, A.7.9 off-premises). A.7.14 uses op_process with disposal_record
    # lifecycle-end (parallel to A.5.28 evidence-disposal pattern).
    #
    # Live postures: 8 of 14 N/A (Arion is cloud-only, no physical premises
    # beyond office). 4 Comply (A.7.7, A.7.10, A.7.13, A.7.14). 2 missing rows
    # (A.7.9 + A.7.12). All 14 engine verdicts: NC 0/4. All 14 surface in
    # Stage-2 (engine NC differs from live N/A AND from live Comply — no
    # agreement suppression). No DerivedSpec refs to A.7.x items — clean.

    EvalCase(
        id=99,
        query="pending engine verdict for A.7.1",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "physical_perimeters"],
        expected_refs=["A.7.1"], expected_type="posture_check",
        must_contain=["A.7.1", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.1 (Physical perimeters) — policy_program 4-leaf: physical_security_perimeters policy + perimeter_register + applicable_sites_scope + program_review (365d). Live N/A → engine NC 0/4. FIRST control of A.7 14-pack (batch 22).",
    ),

    EvalCase(
        id=98,
        query="pending engine verdict for A.7.2",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "physical_entry"],
        expected_refs=["A.7.2"], expected_type="posture_check",
        must_contain=["A.7.2", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.2 (Physical entry) — op_process 4-leaf: physical_entry_procedure + entry_event_register + applicable_areas_scope + program_review (365d). Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=97,
        query="pending engine verdict for A.7.3",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "offices_rooms"],
        expected_refs=["A.7.3"], expected_type="posture_check",
        must_contain=["A.7.3", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.3 (Offices/rooms/facilities) — op_process 4-leaf: offices_rooms_facilities_procedure + room_register + applicable_rooms_scope + program_review (365d). Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=96,
        query="pending engine verdict for A.7.4",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "physical_monitoring"],
        expected_refs=["A.7.4"], expected_type="posture_check",
        must_contain=["A.7.4", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.4 (Physical security monitoring) — op_process 4-leaf: physical_security_monitoring + monitoring_event_register + monitoring_scope + program_review (365d). SIEM integration MUST cross-links to A.5.26 incident response. Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=95,
        query="pending engine verdict for A.7.5",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "environmental_threats"],
        expected_refs=["A.7.5"], expected_type="posture_check",
        must_contain=["A.7.5", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.5 (Environmental threats) — op_process 4-leaf: environmental_threats_procedure + threat_register + applicable_sites_scope + program_review (365d). BCP integration MUST cross-links to A.5.29/A.5.30. Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=94,
        query="pending engine verdict for A.7.6",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "secure_areas"],
        expected_refs=["A.7.6"], expected_type="posture_check",
        must_contain=["A.7.6", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.6 (Working in secure areas) — op_process 4-leaf: working_in_secure_areas_procedure + work_session_register + applicable_areas_scope + program_review (365d). Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=93,
        query="pending engine verdict for A.7.7",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "clear_desk_screen"],
        expected_refs=["A.7.7"], expected_type="posture_check",
        must_contain=["A.7.7", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.7 (Clear desk / clear screen) — policy_program 4-leaf: clear_desk_clear_screen_policy + cd_cs_audit_register + applicable_locations_scope + program_review (365d). Live Comply → engine NC 0/4 (no partial-evidence — A.7 controls have no rich Arion uploads beyond hand-entered findings).",
    ),

    EvalCase(
        id=92,
        query="pending engine verdict for A.7.8",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "equipment_siting"],
        expected_refs=["A.7.8"], expected_type="posture_check",
        must_contain=["A.7.8", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.8 (Equipment siting) — op_process 4-leaf: equipment_siting_procedure + siting_register + applicable_equipment_scope + program_review (365d). Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=91,
        query="pending engine verdict for A.7.9",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "policy_program", "off_premises"],
        expected_refs=["A.7.9"], expected_type="posture_check",
        must_contain=["A.7.9", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.9 (Off-premises assets) — policy_program 4-leaf: off_premises_assets_policy + off_premises_register + applicable_classes_scope + program_review (365d). Cross-link to A.6.7 remote-working. No posture row pre-batch → engine NC 0/4.",
    ),

    EvalCase(
        id=90,
        query="pending engine verdict for A.7.10",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "storage_media"],
        expected_refs=["A.7.10"], expected_type="posture_check",
        must_contain=["A.7.10", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.10 (Storage media lifecycle) — op_process 4-leaf: storage_media_procedure + media_register + applicable_media_scope + program_review (365d). Live Comply → engine NC 0/4.",
    ),

    EvalCase(
        id=89,
        query="pending engine verdict for A.7.11",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "supporting_utilities"],
        expected_refs=["A.7.11"], expected_type="posture_check",
        must_contain=["A.7.11", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.11 (Supporting utilities) — op_process 4-leaf: supporting_utilities_procedure + utility_register + applicable_sites_scope + program_review (365d). BCP integration MUST cross-links to A.5.29/A.5.30. Live N/A → engine NC 0/4.",
    ),

    EvalCase(
        id=88,
        query="pending engine verdict for A.7.12",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "cabling_security"],
        expected_refs=["A.7.12"], expected_type="posture_check",
        must_contain=["A.7.12", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.12 (Cabling security) — op_process 4-leaf: cabling_security_procedure + cabling_register + applicable_runs_scope + program_review (365d). No posture row pre-batch → engine NC 0/4.",
    ),

    EvalCase(
        id=87,
        query="pending engine verdict for A.7.13",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "equipment_maintenance"],
        expected_refs=["A.7.13"], expected_type="posture_check",
        must_contain=["A.7.13", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.13 (Equipment maintenance) — op_process 4-leaf: equipment_maintenance_procedure (freshness 365d) + maintenance_event_register + applicable_equipment_scope + program_review (365d). Live Comply → engine NC 0/4.",
    ),

    EvalCase(
        id=86,
        query="pending engine verdict for A.7.14",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "secure_disposal", "lifecycle_end"],
        expected_refs=["A.7.14"], expected_type="posture_check",
        must_contain=["A.7.14", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes="Locks A.7.14 (Secure disposal) — op_process 4-leaf with disposal_record lifecycle-end: secure_disposal_procedure + disposal_scope + disposal_record (per-equipment) + program_review (365d). Parallel to A.5.28 evidence-disposal pattern. Live Comply → engine NC 0/4.",
    ),

    # ── Phase B A.6 People Controls 7-pack (commit 2026-06-01) ──
    # Twenty-first Phase B bulk batch (seven controls): A.6.1 + A.6.2 + A.6.3
    # + A.6.4 + A.6.5 + A.6.6 + A.6.8 all promoted to 4-leaf. LARGEST MULTI-
    # CONTROL BATCH YET (previous record: batch 3 with 5 controls). Closes
    # the A.6 People Controls block — A.6.7 was already curated as
    # REQ_REMOTE_WORKING (profile_fact triggered).
    #
    # Spine mix:
    #   A.6.1  op_process — screening_procedure + record_register + roles_scope + program_review
    #   A.6.2  records_program template-as-primary — terms_template + signed_register + workers_scope + template_review
    #   A.6.3  op_process programme-as-primary — awareness_programme + completion_register + audience_scope + programme_review
    #   A.6.4  op_process — disciplinary_process + case_register + jurisdictions_scope + process_review
    #   A.6.5  op_process — post_employment_procedure + leaver_briefing_register + obligations_scope + program_review
    #   A.6.6  records_program template-as-primary — nda_template + signature_register + parties_scope + template_review
    #   A.6.8  op_process — event_reporting_procedure + report_register + audience_scope + program_review
    #
    # All 7 engine verdicts: NC 0/4 children satisfied. Live postures: A.6.4
    # = OFI; rest = Comply (with various hand-entered findings). All 7 flip
    # to engine-proposed NC in Stage-2 (no engine-agreement suppression).
    # No DerivedSpec references to A.6.x items — clean item-id preservation.

    EvalCase(
        id=85,
        query="pending engine verdict for A.6.8",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "event_reporting"],
        expected_refs=["A.6.8"],
        expected_type="posture_check",
        must_contain=["A.6.8", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.8 (Event reporting) Phase B promotion to op_process "
            "4-leaf: event_reporting_procedure (preserves prior single-leaf "
            "id) + event_report_register (per-event submission tracker) + "
            "reporting_audience_scope (who can report) + reporting_"
            "program_review (freshness 365d). Live posture flips from "
            "Comply (hand-entered 'simple and accessible reporting "
            "process via email, Teams, and phone...') to engine-proposed "
            "NC at 0/4. Cross-control: handoff to A.5.25 triage on every "
            "report (closes the reporting → triage → incident pipeline)."
        ),
    ),

    EvalCase(
        id=84,
        query="pending engine verdict for A.6.6",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "nda"],
        expected_refs=["A.6.6"],
        expected_type="posture_check",
        must_contain=["A.6.6", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.6 (NDA) Phase B promotion to records_program 4-leaf "
            "template-as-primary variant (like A.6.2): nda_template "
            "(preserves prior single-leaf id, freshness 365d) + "
            "nda_signature_register (per-signatory tracking) + "
            "applicable_parties_scope (which parties need NDA before "
            "access) + nda_template_review (annual review of template "
            "vs current classification scheme + jurisdictional "
            "enforceability). Live posture flips Comply → engine NC 0/4."
        ),
    ),

    EvalCase(
        id=83,
        query="pending engine verdict for A.6.5",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "post_employment"],
        expected_refs=["A.6.5"],
        expected_type="posture_check",
        must_contain=["A.6.5", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.5 (Post-employment) Phase B promotion to op_process "
            "4-leaf: post_employment_responsibilities (preserves prior "
            "single-leaf id; contractual/HR layer) + leaver_briefing_"
            "register (per-leaver exit-briefing record with signed "
            "acknowledgment of surviving obligations) + surviving_"
            "obligations_scope (which obligations apply to which roles "
            "per jurisdictional enforceability caps) + post_employment_"
            "program_review (freshness 365d). Cross-control: A.6.5 is the "
            "contractual layer above the operational A.5.11 (return of "
            "assets) + A.5.16 (identity revocation) + A.5.17 (credential "
            "revocation) + A.5.18 (access revocation). Live posture "
            "flips Comply → engine NC 0/4."
        ),
    ),

    EvalCase(
        id=82,
        query="pending engine verdict for A.6.4",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "disciplinary"],
        expected_refs=["A.6.4"],
        expected_type="posture_check",
        must_contain=["A.6.4", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.4 (Disciplinary process) Phase B promotion to "
            "op_process 4-leaf: disciplinary_process (preserves prior "
            "single-leaf id) + disciplinary_case_register (per-case "
            "tracker with investigation outcome + action taken) + "
            "applicable_jurisdictions_scope (employment-law variants "
            "drive process step variations — at-will US vs just-cause EU "
            "vs notice-period UK) + disciplinary_process_review "
            "(freshness 365d; consistency analysis flags discriminatory "
            "patterns). Live posture flips OFI → engine NC 0/4. (Only "
            "A.6.x control with live OFI vs other 6 Comply — but engine "
            "still surfaces NC because OFI != NC.)"
        ),
    ),

    EvalCase(
        id=81,
        query="pending engine verdict for A.6.3",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "awareness"],
        expected_refs=["A.6.3"],
        expected_type="posture_check",
        must_contain=["A.6.3", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.3 (Security awareness) Phase B promotion to "
            "op_process 4-leaf programme-as-primary variant: security_"
            "awareness_programme (preserves prior single-leaf id, "
            "freshness 365d) + training_completion_register (per-person "
            "training record with score + next-due) + audience_curriculum_"
            "scope (role-to-module matrix) + awareness_programme_review "
            "(freshness 365d; effectiveness analysis with phishing-"
            "simulation + reporting-rate trend). Live posture flips "
            "Comply → engine NC 0/4."
        ),
    ),

    EvalCase(
        id=80,
        query="pending engine verdict for A.6.2",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "employment_terms"],
        expected_refs=["A.6.2"],
        expected_type="posture_check",
        must_contain=["A.6.2", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.2 (Employment terms) Phase B promotion to "
            "records_program 4-leaf template-as-primary variant: "
            "employment_terms_template (preserves prior single-leaf id; "
            "the standard contract clause set) + signed_terms_register "
            "(per-employee signed-version tracker with current-version "
            "check flag) + applicable_workers_scope (which categories "
            "use which template variant) + terms_template_review "
            "(freshness 365d; policy-drift + legal-drift checks). Live "
            "posture flips Comply → engine NC 0/4. Cross-control: "
            "A.6.2 + A.6.6 NDA together form the personnel info-"
            "security contract package."
        ),
    ),

    EvalCase(
        id=79,
        query="pending engine verdict for A.6.1",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "op_process", "screening"],
        expected_refs=["A.6.1"],
        expected_type="posture_check",
        must_contain=["A.6.1", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=["0/1 children satisfied", "no curated multi-leaf",
                          "I need more information", "could you clarify"],
        notes=(
            "Locks A.6.1 (Screening) Phase B promotion to op_process "
            "4-leaf: screening_procedure (preserves prior single-leaf "
            "id) + screening_record_register (per-candidate screening "
            "event tracker with outcome + decision-date proving "
            "screening completed BEFORE access granted per A.5.18) + "
            "applicable_roles_scope (role-tier → check-matrix; "
            "jurisdictional limits where some checks unavailable) + "
            "screening_program_review (freshness 365d). Live posture "
            "flips Comply → engine NC 0/4. FIRST control of the "
            "A.6 People Controls 7-pack (batch 21)."
        ),
    ),

    # ── Phase B A.5.3x close-out 3-pack (commit 2026-06-01) ──
    # Nineteenth Phase B bulk batch (three-control): A.5.35 + A.5.36 + A.5.37
    # promoted to 4-leaf — closes the A.5.3x review/procedure block. First
    # multi-control batch since batch 4 (incident triage 3-pack) — pattern
    # is locked in, batches can bundle conceptually-related controls.
    # All three are records_program spine variants:
    #   A.5.35  review-record-as-primary (same shape as A.5.22): independent_
    #           review_report + review_schedule_register + program_meta_review
    #           + finding_response_register
    #   A.5.36  review-record-as-primary (batch-mate of A.5.35): compliance_
    #           review_record + compliance_review_schedule + compliance_
    #           program_meta_review + nonconformity_register
    #   A.5.37  register-as-primary (same shape as A.5.9 asset register):
    #           operating_procedures_register + procedures_maintenance_
    #           procedure + applicable_facilities_scope + procedures_
    #           program_review
    # Per-record freshness=365 on A.5.35 + A.5.36 primary leaves (each report/
    # record has its own currency); A.5.37 has freshness on the review leaf
    # only (the register is operational, not annual). Cross-control links
    # locked: A.5.35 ↔ A.5.36 finding registers share infrastructure
    # (fr_cross_review_link SHOULDs on both); A.5.37 → A.5.9 asset register
    # via scope_asset_link MUST; A.5.37 cross-links to A.5.24/A.5.26/A.5.29/
    # A.5.30 incident + DR procedures via related_controls_link SHOULD.

    EvalCase(
        id=78,
        query="pending engine verdict for A.5.37",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "operating_procedures"],
        expected_refs=["A.5.37"],
        expected_type="posture_check",
        must_contain=["A.5.37", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.37 (Documented operating procedures) Phase B "
            "promotion to records_program 4-leaf register-as-primary "
            "variant — same shape as A.5.9 asset register from batch 1. "
            "Leaves: operating_procedures_register (preserves prior "
            "single-leaf id) + procedures_maintenance_procedure (how "
            "procedures are created/reviewed/updated/retired) + "
            "applicable_facilities_scope (which facilities/systems need "
            "a procedure — drives 'every facility represented' check) "
            "+ procedures_program_review (freshness=365d). Live posture "
            "flips from Comply (hand-entered finding 'Policies and "
            "process documents including privacy procedures are "
            "available and ac...') to engine-proposed NC at 0/4 — the "
            "narrative claim doesn't satisfy the four-leaf register/"
            "procedure/scope/review shape. New audience_per_procedure "
            "MUST encodes 'personnel who need them' explicitly. New "
            "emergency_flag SHOULD highlights procedures where stale = "
            "catastrophic (DR, IR). New rev_accuracy_sample MUST is "
            "the bite that prevents 'documented but wrong' drift — "
            "reviewer must actually walk through a sample procedure "
            "end-to-end. Closes the A.5.3x review/procedure block — "
            "A.5.37 is the final A.5 organisational control, ending "
            "the Phase B A.5 arc that started with case #46 batch 1."
        ),
    ),

    EvalCase(
        id=77,
        query="pending engine verdict for A.5.36",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "compliance_review"],
        expected_refs=["A.5.36"],
        expected_type="posture_check",
        must_contain=["A.5.36", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.36 (Compliance review records) Phase B promotion "
            "to records_program 4-leaf review-record-as-primary variant — "
            "batch-mate of A.5.35 (same shape, different scope: A.5.35 "
            "reviews the InfoSec FUNCTION independently; A.5.36 reviews "
            "COMPLIANCE WITH policies/rules/standards). Leaves: "
            "compliance_review_record (preserves prior single-leaf id; "
            "per-cycle review record with freshness=365) + compliance_"
            "review_schedule (full catalogue with cadence per item) + "
            "compliance_program_meta_review (annual self-check; new "
            "pgm_method_review MUST — are reviews surfacing real NCs "
            "or rubber-stamping?) + nonconformity_register (per-NC "
            "lifecycle with root cause for systemic improvement). Live "
            "posture flips from Comply (empty gap_description hand-"
            "entered) to engine-proposed NC at 0/4. Cross-control link "
            "A.5.36 ↔ A.5.35 — finding registers can be one artefact "
            "(nc_cross_review_link SHOULD + fr_cross_review_link "
            "SHOULD on A.5.35 — symmetric)."
        ),
    ),

    EvalCase(
        id=76,
        query="pending engine verdict for A.5.35",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "independent_review"],
        expected_refs=["A.5.35"],
        expected_type="posture_check",
        must_contain=["A.5.35", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.35 (Independent review of information security) "
            "Phase B promotion to records_program 4-leaf review-record-"
            "as-primary variant — SAME SHAPE as A.5.22 supplier review "
            "(commit 2026-05-31, batch 3). Leaves: independent_review_"
            "report (preserves prior single-leaf id; per-report record "
            "with freshness=365) + review_schedule_register (the "
            "calendar of upcoming reviews with cadence + reviewer "
            "selection + scope areas) + review_program_meta_review "
            "(annual self-check; new pgm_independence_check MUST audits "
            "that reviewers ACTUALLY met independence criteria — "
            "rubber-stamping fail mode) + finding_response_register "
            "(per-finding lifecycle with closure evidence; lifecycle-"
            "end slot). Live posture flips from Comply (hand-entered "
            "finding 'Independent review program implemented through "
            "annual external audits and intern...') to engine-proposed "
            "NC at 0/4 — narrative claim doesn't satisfy the four-leaf "
            "shape. New significant_change_check MUST enforces 27002 "
            "§5.35's 'or on significant change' explicit consideration. "
            "First control with a finding_response_register lifecycle-"
            "end variant (analogous to A.5.22's change_response_log + "
            "A.5.25's triage_decision + A.5.28's disposal_record)."
        ),
    ),

    # ── Phase B records_program PII-protection (commit 2026-06-01) ──
    # Eighteenth Phase B bulk batch (single-control): A.5.34 promoted to
    # records_program 4-leaf — privacy_and_pii_protection_policy (the
    # PIMS-aligned umbrella policy, preserves the prior single-leaf id) +
    # pii_processing_register (per-activity PII catalog, often shared with
    # GDPR Art.30 RoPA) + privacy_applicability_scope (which privacy laws
    # apply, jurisdictions, data subject categories, controller/processor
    # status) + privacy_program_review (365d). Natural pair with A.5.33
    # (batch 17) — A.5.33 protects the records, A.5.34 protects the PII
    # subset of those records with privacy-law overlays. Engine sits at
    # OFI 1/4 — Arion's existing privacy policy upload satisfies the
    # policy leaf via the matcher's semantic recognition; the three new
    # leaves (register + scope + review) carry no evidence yet. PARTIAL-
    # EVIDENCE shape — third such case after A.5.15 (#55) and A.5.23 (#60).
    # Item-id preservation TWO-WAY: SPEC_ART_24 + SPEC_ART_25 reference 7
    # A.5.34 items by id; all 7 preserved (six stay on the policy leaf
    # where the concepts live, :pii_inventory relocates to the register
    # leaf — its natural home as the operational catalog).

    EvalCase(
        id=75,
        query="pending engine verdict for A.5.34",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "pii_protection", "partial_evidence"],
        expected_refs=["A.5.34"],
        expected_type="posture_check",
        # Like cases 55 (A.5.15) and 60 (A.5.23), A.5.34 sits at OFI 1/4 —
        # the policy leaf is satisfied via legacy upload, the three new
        # leaves are unsatisfied. The 1/4 reason text PROVES the 4-leaf
        # promotion AND the partial-evidence path.
        must_contain=["A.5.34", "engine proposes", "'OFI'", "1/4 children satisfied"],
        must_not_contain=[
            "0/4 children satisfied",
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.34 (Privacy and PII protection) Phase B promotion to "
            "records_program 4-leaf: privacy_and_pii_protection_policy "
            "(preserves the prior single-leaf id; carries 6 of the 7 "
            "preserved item-ids — applicable_laws, lawful_basis, "
            "data_subject_rights, retention_minimisation, "
            "security_controls_ref, breach_handling) + "
            "pii_processing_register (carries the seventh preserved id, "
            ":pii_inventory; per-activity PII catalog, often shared with "
            "GDPR Art.30 RoPA — same operational artefact serves both) + "
            "privacy_applicability_scope (the upstream — applicable "
            "privacy laws, jurisdictions, data subject categories, "
            "regulated activities, controller/processor status) + "
            "privacy_program_review (freshness 365d, matches A.5.33 "
            "records-family default + A.5.35/A.5.36 annual review "
            "cadence). PARTIAL-EVIDENCE shape: Arion's existing privacy "
            "policy upload satisfies the policy leaf via semantic "
            "matching, the three new leaves are unsatisfied → engine "
            "proposes OFI at 1/4. Third partial-evidence case after "
            "A.5.15 (#55, policy_program) and A.5.23 (#60, "
            "operational_process). Natural pair with A.5.33 (batch 17). "
            "Item-id preservation TWO-WAY critical — SPEC_ART_25 "
            "(Art.25 DPbD) references 4 A.5.34 items by id, SPEC_ART_24 "
            "(Art.24 controller responsibility) references 5; combined "
            "set of 7 (overlap on :applicable_laws + "
            ":security_controls_ref) all preserved across the promotion. "
            "Fourth ISO × GDPR integration MUST family — new "
            "transfer_restrictions MUST encodes GDPR Chap V at MUST "
            "level (joins A.5.14 legal_jurisdiction, A.5.33 PII overlay, "
            "A.5.13 pii_overlay). Two new MUSTs (transfer_restrictions, "
            "owner) plus :pims_alignment SHOULD encode the ISO/IEC "
            "27701 PIMS extension where in scope."
        ),
    ),

    # ── Phase B records_program records-protection (commit 2026-06-01) ──
    # Seventeenth Phase B bulk batch (single-control): A.5.33 promoted to
    # records_program 4-leaf — records_protection_policy (procedure) +
    # records_schedule_register + records_categories_scope + records_
    # program_review (365d). Pairs naturally with the batch 1 records-
    # family A.5.5/A.5.6/A.5.9/A.5.31/A.5.32 — first records_program
    # promotion since batch 1 (2026-05-29). Spine return after 11 op_
    # process batches (batches 3-6, 8-10, 12, 13, 15, 16) + 2 policy_
    # program batches (2, 11) — re-validates records_program spine
    # consistency. Annual review cadence (365d) matches the stable-
    # doctrine records-family controls A.5.5/A.5.6 (A.5.31 is the
    # exception at 180d, driven by regulatory change cadence). Item-id
    # preservation critical — SPEC_ART_5_1_E (GDPR Art.5.1.e storage
    # limitation derivation) references four A.5.33 items by id; all
    # four preserved (records_schedule + retention_periods +
    # retention_drivers relocate to register leaf, disposal stays on
    # procedure leaf).

    EvalCase(
        id=74,
        query="pending engine verdict for A.5.33",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "records_program", "records_protection"],
        expected_refs=["A.5.33"],
        expected_type="posture_check",
        must_contain=["A.5.33", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.33 (Protection of records) Phase B promotion to "
            "records_program 4-leaf: records_protection_policy "
            "(procedure leaf — preserves the prior single-leaf id) + "
            "records_schedule_register (per-class retention/protection "
            "register) + records_categories_scope (upstream — business "
            "activities, legal drivers, data categories that determine "
            "what counts as a 'record') + records_program_review "
            "(freshness 365d). Live posture flips from Comply (hand-"
            "entered finding citing 'MSFT Azure, 365 and RBAC "
            "implementation with document access controls and labeling') "
            "to engine-proposed NC at 0/4. First records_program "
            "promotion since batch 1 (2026-05-29) — re-validates spine "
            "consistency after 11 op_process + 2 policy_program "
            "batches in between. Annual review cadence (365d) matches "
            "the stable-doctrine records-family controls A.5.5/A.5.6 "
            "(A.5.31 is the exception at 180d, regulatory-change-driven). "
            "Item-id preservation critical — SPEC_ART_5_1_E (GDPR "
            "Art.5.1.e storage limitation) references four A.5.33 items "
            "by id; all four preserved across the promotion "
            "(records_schedule + retention_periods + retention_drivers "
            "relocated to the register leaf, disposal stayed on the "
            "procedure leaf). New proc_pii_overlay SHOULD encodes the "
            "ISO × GDPR Art.5.1.e integration at spec level (third "
            "ISO × GDPR integration leaf after pii_overlay on A.5.13 "
            "and legal_jurisdiction on A.5.14)."
        ),
    ),

    # ── Phase B operational_process ICT-readiness (commit 2026-05-31) ──
    # Sixteenth Phase B bulk batch (single-control): A.5.30 promoted to
    # operational_process 4-leaf — ict_continuity_plan + ict_service_
    # register + ict_program_review (180d) + per-recovery HYBRID record.
    # Natural pair-batch with A.5.29 from batch 15 — A.5.29 is the
    # security annex to the BCP; A.5.30 is the mechanical ICT recovery
    # layer. Both batches feature the HYBRID recovery/activation record
    # pattern (real OR test via type field). Plan-leaf freshness
    # convention cleaned up: removed freshness_days=365 from the legacy
    # plan and put it on the review leaf only (consistent with all
    # other op_process batches).

    EvalCase(
        id=73,
        query="pending engine verdict for A.5.30",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "ict_readiness"],
        expected_refs=["A.5.30"],
        expected_type="posture_check",
        must_contain=["A.5.30", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.30 (ICT readiness for business continuity) Phase B "
            "promotion to operational_process 4-leaf: ict_continuity_plan "
            "(plan-as-primary, natural pair with A.5.29 plan from batch 15) "
            "+ ict_service_register + ict_program_review (freshness 180d) + "
            "per-recovery HYBRID record covering BOTH real recovery events "
            "AND scheduled tests via type field. Live posture flips from "
            "Comply (hand-entered finding citing Azure + M365 redundancy + "
            "quarterly tabletops) to engine-proposed NC at 0/4. Two new "
            "MUSTs over legacy: bia_link (RTO/RPO must trace to the BIA, "
            "not arbitrarily chosen) and bcp_alignment (this layer + A.5.29 "
            "security-annex layer must reconcile). Freshness-convention "
            "cleanup: removed freshness_days=365 from legacy plan leaf, "
            "kept on review_record only (consistent with the rest of the "
            "op_process spine — A.5.7/8/11/13/16/17/24/28/29 all have "
            "freshness on review only)."
        ),
    ),

    # ── Phase B operational_process disruption-security (commit 2026-05-31) ──
    # Fifteenth Phase B bulk batch (single-control): A.5.29 promoted to
    # operational_process 4-leaf — continuity_security_plan (plan as
    # primary, like A.5.14 used policy) + disruption_scenario_register +
    # continuity_program_review (180d) + per-activation plan record.
    # The activation_record covers BOTH real disruptions AND scheduled
    # tests — distinct from A.5.24's exercise_record (drills only).
    # Fourth consecutive SHOULD-promotion (test_schedule → MUST).

    EvalCase(
        id=72,
        query="pending engine verdict for A.5.29",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "disruption_security"],
        expected_refs=["A.5.29"],
        expected_type="posture_check",
        must_contain=["A.5.29", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.29 (Information security during disruption) Phase B "
            "promotion to operational_process 4-leaf: continuity_security_plan "
            "(plan-as-primary variant) + disruption_scenario_register + "
            "continuity_program_review (freshness 180d) + per-activation "
            "plan_activation_record. Live posture flips from Comply (hand-"
            "entered finding citing BCP + GDPR/privacy compliance during "
            "recovery) to engine-proposed NC at 0/4. The activation_record "
            "lifecycle-end leaf is a HYBRID variant — covers BOTH real "
            "disruptions AND scheduled tests, with a type field "
            "distinguishing them. Distinct from A.5.24's exercise_record "
            "(drills ONLY) and A.5.26's incident_closure_record (real "
            "incidents ONLY) — A.5.29's plan can fire either way. New "
            "degradation_levels MUST encodes 'appropriate level' = "
            "graceful degradation explicitly (one of A.5.29's most-tested "
            "auditor concerns). test_schedule promoted SHOULD → MUST "
            "(fourth consecutive SHOULD-promotion across batches 12-15)."
        ),
    ),

    # ── Phase B operational_process incident-planning (commit 2026-05-31) ──
    # Fourteenth Phase B bulk batch (single-control): A.5.24 promoted to
    # operational_process 4-leaf — incident_management_framework + IR_team_
    # register + framework_program_review (180d) + per-exercise activation
    # record. A.5.24 sits ABOVE the operational A.5.25-27 incident family
    # (batch 4) and A.5.28 evidence handling (batch 6). The exercise_record
    # lifecycle-end is distinct from A.5.26's incident_closure_record —
    # this tracks READINESS DRILLS, not real incidents. Third batch with
    # GDPR-required MUSTs (after batches 10+11). `tested` SHOULD promoted
    # to exercise_cadence MUST + lifecycle-end exercise_record (same SHOULD-
    # promotion pattern as batches 12+13).

    EvalCase(
        id=71,
        query="pending engine verdict for A.5.24",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "incident_planning"],
        expected_refs=["A.5.24"],
        expected_type="posture_check",
        must_contain=["A.5.24", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.24 (Information security incident management planning) "
            "Phase B promotion to operational_process 4-leaf: "
            "incident_management_framework + incident_response_team_register "
            "+ framework_program_review (freshness 180d) + per-exercise "
            "framework_exercise_record. Live posture flips from Comply "
            "(hand-entered finding citing GDPR 72hr notification + breach "
            "notification processes) to engine-proposed NC at 0/4. The "
            "framework sits ABOVE the operational A.5.25-27 incident "
            "family (batch 4) and A.5.28 evidence handling (batch 6) — "
            "A.5.24 is the strategic planning layer that defines roles, "
            "authorities, communication paths, exercise cadence. The "
            "exercise_record lifecycle-end is distinct from A.5.26's "
            "real-incident closure record — A.5.24 tracks READINESS "
            "DRILLS, not real incidents. Review freshness 180d because "
            "IR readiness erodes between exercises. Third batch with GDPR-"
            "required MUSTs (after pii_overlay in batch 10 and "
            "legal_jurisdiction in batch 11) — preserves the personal_data "
            "and notification MUSTs as gdpr_required=True, adds "
            "rev_gdpr_72h_feasibility as new GDPR-required review MUST."
        ),
    ),

    EvalCase(
        id=70,
        query="pending engine verdict for A.5.17",
        tags=["posture", "engine", "stage2", "multi_leaf", "phase_b", "operational_process", "authentication"],
        expected_refs=["A.5.17"],
        expected_type="posture_check",
        must_contain=["A.5.17", "engine proposes", "'NC'", "0/4 children satisfied"],
        must_not_contain=[
            "0/1 children satisfied",
            "no curated multi-leaf",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks A.5.17 (Authentication information) Phase B promotion to "
            "operational_process 4-leaf: authentication_information_procedure "
            "+ credential_register + authentication_program_review "
            "(freshness 180d) + per-credential revocation_record. Live "
            "posture flips from Comply (empty gap_description) to engine-"
            "proposed NC at 0/4. Naturally PAIRED with A.5.16 (batch 12) — "
            "identity_link MUST on procedure encodes the pairing constraint. "
            "The revocation_record's rev_identity_pair MUST closes the loop "
            "between credential-revocation events and identity-revocation "
            "events. MFA promoted SHOULD → MUST: phishable single-factor "
            "auth is no longer acceptable baseline; the previously-soft "
            "expectation is now first-class, paralleling service_accounts "
            "promotion in batch 12."
        ),
    ),

    EvalCase(
        id=41,
        query="is A.5.30 compliant?",
        tags=["posture", "posture_discipline", "no_relabel"],
        expected_refs=["A.5.30"],
        # Posture-discipline regression: A.5.30 (ICT readiness for BC) is
        # tagged Comply in posture_controls but its gap_description prose
        # mentions ongoing-monitoring concerns. Pre-fix the LLM would
        # re-categorize A.5.30 as OFI based on the prose, and sometimes
        # list it under BOTH Comply and OFI sections in the same answer
        # — a dup-label bug observed during 2026-05-26 chat testing.
        #
        # Post-fix system prompt rule: "The tag IS the verdict … each
        # control appears in exactly one formal finding section …
        # advisory commentary goes under a separate Recommendations
        # section, never under OFI/NC headings."
        #
        # Single-control query so the test isn't sensitive to multi-
        # control formatting; "Comply" must be present, OFI/NC labels
        # must NOT attach to A.5.30 in any form.
        must_contain=["A.5.30", "Comply"],
        must_not_contain=[
            "A.5.30 [OFI]",
            "A.5.30 [NC]",
            "A.5.30 is OFI",
            "A.5.30 is NC",
            "A.5.30 is a non-conformity",
            "A.5.30 is an opportunity for improvement",
            "I need more information", "could you clarify",
        ],
        notes=(
            "Locks the posture-tag-is-the-verdict rule and forbids "
            "re-labelling Comply controls as OFI based on prose. Pairs "
            "with the system-prompt POSTURE FINDING DISCIPLINE block. "
            "Single-control probe — multi-control dup-label is harder "
            "to assert via substring matching but flows from the same "
            "rule."
        ),
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
