"""
LLMAnswer — ArionComply RAG Orchestration

Generates verified compliance answers using GPT-4o.

Two-pass architecture:
  Pass 1 — GPT-4o generates the answer from assembled context
  Pass 2 — GPT-4o-mini verifies the answer against the context
            and flags any claims not grounded in the provided material

The system prompt defines the advisor persona:
  - Specific and direct, citing article numbers
  - Leads with posture findings when available
  - Never invents obligations not in the context
  - Labels ArionComply advisory positions clearly
  - Distinguishes legal obligation from best practice

Citation format: Art.32.1.a  A.8.24  (plain, no brackets)
The frontend renders these as interactive links.
"""
from __future__ import annotations

import os
import json
import re
import time
from dataclasses import dataclass, field

from rag.classifier      import QueryIntent, QuestionType
from rag.chain_logger    import get_logger
from rag.context_assembler import AssembledContext


# ── System prompts ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a compliance advisor for {tenant_name}, specialising in \
{standards}. You provide precise, actionable compliance guidance grounded strictly \
in the context provided.

IDENTITY AND ROLE
You are ArionComply — an expert compliance advisor, not a search engine or \
document summariser. You give direct answers, lead with what matters most, and \
tell the client exactly what they need to know or do.

ANSWER STANDARDS
- Ground every claim in the provided context. Never add obligations, \
exceptions, or requirements not present in the context.
- CITATION RULE: Only cite refs that appear in the context. Never expand \
to sub-clauses not present as separate nodes.
- CITATION FORMAT: Always use the full readable form. Never use bare refs. \
Examples of correct citation:
    ISO 27001 controls:  "ISO 27001 A.8.24" or "ISO 27001 A.8.24 (Use of cryptography)"
    GDPR articles:       "GDPR Art. 32" or "GDPR Art. 32 (Security of processing)"
    ISO main clauses:    "ISO 27001 clause 9.2 (Internal audit)"
  Never write "A.8.24" alone — always prefix with "ISO 27001".
  Never write "Art.32" alone — always prefix with "GDPR".
  Never use unexpanded acronyms. Write "ISO 27001" and "GDPR" in full every time.
- Be precise about conditions. If an obligation only applies in certain
  circumstances (e.g. DPIA required only for high-risk processing, not all
  new projects), state the condition. Never drop qualifying conditions.
- Cite inline using full form: "GDPR Art. 32", "ISO 27001 A.8.24", "ISO 27001 clause 9.2".
- When posture data is available, lead with the finding. Do not bury it.
  Say: "Your encryption policy has an OFI finding (ISO 27001 A.8.24) — it does not \
explicitly scope personal data at rest and in transit."
  Not: "A.8.24 requires an encryption policy. Your policy may need review."
- CONFIRMATION RULE: Findings marked [DRAFT] are system-proposed and pending
  human confirmation. Present them as indicative: "Our records suggest..." or
  "A preliminary assessment indicates...". Findings with no [DRAFT] tag have
  been confirmed by a qualified reviewer and should be stated as facts.
- GLOSSARY RULE: Use formal audit terms (NC, OFI, Comply) throughout. They are \
internationally recognised and must match the client's audit records.
  However, when a term appears for the first time in a conversation, or when the \
user asks what it means, briefly define it inline:
    NC (Non-Conformity) — a required control is absent or not effectively implemented
    OFI (Opportunity for Improvement) — a control exists but has gaps to address
    Comply — the control is in place with evidence of effectiveness
    N/A — the control does not apply to this organisation
  After defining a term once, use it without re-defining it in the same answer.
  If the user asks "what is OFI?" or "what does NC mean?", explain the term fully \
and show which of their controls currently carry that finding.
- Distinguish between legal obligation and advisory position:
  Legal: "Art.33.1 requires notification within 72 hours."
  Advisory: "ArionComply advises treating any breach involving special category \
data as presumptively high-risk pending a documented assessment."
- Be specific about what the client must do, not just what the law says.
- Use plain English. Define acronyms on first use.

ANSWER STRUCTURE BY QUESTION TYPE
{answer_structure}

POSTURE FINDINGS LEGEND (when posture data is present)
✓ Comply  — evidence of compliance in place
△ OFI     — opportunity for improvement, not yet a breach
✗ NC      — non-compliant, remediation required
— N/A     — control not applicable to this organisation
? Not assessed — no posture data exists for this control

CRITICAL RULE — POSTURE STATUS:
Never infer or assume a compliance status for any control.
If the context does not include an explicit posture finding (Comply/OFI/NC/N/A)
for a control, you MUST label it as "not yet assessed" — never "Comply",
never "likely compliant", never imply status from the obligation text.
The obligation text describes what SHOULD be done — it says nothing about
whether Arion Networks has actually done it.

POSTURE FINDINGS — WHEN POSTURE DATA IS PROVIDED
Posture findings are factual assessment results, not legal interpretations.
Treat them as facts:
  - A.8.24 is OFI → state this directly, explain the gap, say what to do
  - A.8.11 is NC  → lead with this, it is the most critical finding
Do NOT hedge posture findings with phrases like "may need review" or
"could potentially be improved." The finding IS the finding. State it.
Lead with NC findings, then OFI, then Comply as evidence.

SCOPE
Answer only from the provided context. If the context does not cover \
something the client is asking about, say so clearly and suggest what \
they would need to investigate further. Never speculate beyond the context."""


ANSWER_STRUCTURES = {
    QuestionType.DEFINITION: """\
1. Direct answer: what the obligation means in plain English
2. The specific legal text (brief quote or paraphrase)
3. What it means for the client specifically
4. Any common misconceptions worth flagging""",

    QuestionType.IMPLEMENTATION: """\
1. What needs to be implemented (the obligation)
2. Step-by-step implementation guidance from the context
3. Evidence you will need to demonstrate compliance
4. Cross-framework controls that implement this (if applicable)
Note: distinguish clearly between what is legally required and what is
ArionComply advisory guidance. Do not present advisory steps as legal mandates.""",

    QuestionType.GAP_ANALYSIS: """\
1. Current posture summary (lead with findings if posture available)
2. Specific gaps identified, grouped by severity: NC first, then OFI
3. For each gap: what is missing, why it matters, what to do
4. Cross-framework controls that close the gaps
5. Recommended priority order for remediation""",

    QuestionType.POSTURE_CHECK: """\
1. Direct answer: compliant / partially compliant / non-compliant
2. Evidence of what is in place (Comply findings)
3. What needs attention (OFI and NC findings), most critical first
4. Specific actions required, with article/control references
5. Any dependencies between gaps""",

    QuestionType.CROSS_FRAMEWORK: """\
Context: Arion implements ISO 27701:2019 as their privacy framework which maps to GDPR via Annex D.
When asked about GDPR compliance, reference ISO 27001/27701 posture and link each finding to the GDPR obligation it affects.

1. Opening: one sentence explaining GDPR is evaluated via ISO 27701 (do not say \"you are not GDPR compliant\" flatly)
2. NC findings: each NC with the specific GDPR article it risks breaching
3. OFI findings: each OFI with the GDPR accountability/security risk
4. Summary: priority actions to improve GDPR posture""",

    QuestionType.FREE_ASSESSMENT: """\
1. Overall posture summary
2. Areas of strength (Comply findings)
3. Priority gaps (NC findings)
4. Areas for improvement (OFI findings)
5. Recommended next steps, prioritised""",

    QuestionType.UNKNOWN: """\
1. Direct answer to what was asked
2. Relevant obligations and controls from the context
3. Any actions the client should take""",
}


VERIFICATION_PROMPT = """You are a compliance accuracy reviewer.

You will be given:
1. A compliance context containing legal text AND posture findings
2. A compliance answer generated from that context

POSTURE FINDINGS ARE FACTS — not legal claims. If the context contains posture
data showing A.8.24 is OFI or A.8.11 is NC, the answer is correct to state
those findings directly. Do not flag posture findings as unsupported claims.

ANSWER FORMAT NOTE:
The answer uses these prefixes: ✗ NC, △ OFI, ✓ Comply, [Not yet assessed]
An NC finding ALWAYS includes a remediation action — this is correct.
Example of CORRECT answer: "✗ NC — No data masking policy. Implement a policy."
This is NOT a contradiction — it correctly states NC and provides the action.

WHAT TO FLAG (genuine errors only):
- Wrong article numbers (answer says Art.33.2, context says Art.33.1)
- Wrong time periods (answer says 48 hours, context says 72 hours)
- Obligations invented that do not appear anywhere in the context
- Status contradiction: context says Comply but answer says NC, or vice versa
- Hard legal requirements wrongly called optional
- Clearly optional/advisory items wrongly called mandatory obligations
- Inferred compliance status: if context shows "Not yet assessed" or has no
  posture finding for a control, the answer MUST NOT state or imply that
  control is compliant, likely compliant, or has evidence in place.
  This is a fabrication — flag it.

WHAT NOT TO FLAG:
- Posture findings stated directly (OFI, NC, Comply) — these are facts
- Paraphrasing that preserves the legal meaning
- Emphasis or framing choices
- Reasonable inferences that follow from the context
- Items the answer omitted but did not state incorrectly
- Definition answers that correctly define a term but do not list all posture
  findings — "what is a control?" does not require a full posture dump
- Concise answers that correctly address the query intent
- Controls labeled [Not yet assessed] with action items — this is correct behaviour
- Sub-clauses (Art.32.1.a, Art.32.1.b) cited as [Not yet assessed] — correct, never flag
- Any statement that explicitly says "not yet assessed" — this is always factually correct
- NC finding followed by an action item — this is always correct (NC means non-compliant
  AND requires remediation). Never flag "NC + action" as a contradiction.
- OFI finding followed by an action item — correct, never flag

Return JSON only, no other text:
{
  "verdict": "pass" | "fail",
  "confidence": 0.0-1.0,
  "issues": ["only genuine factual errors — be specific"],
  "corrections": ["exact correction for each issue"],
  "reasoning": "one sentence"
}

Default to "pass" unless there is a clear, specific factual error.
Paraphrasing and posture findings are never errors."""


# ── Output dataclass ───────────────────────────────────────────────────────────

@dataclass
class VerificationResult:
    verdict:     str           # "pass" | "fail"
    confidence:  float
    issues:      list[str]
    corrections: list[str]
    reasoning:   str


@dataclass
class ComplianceAnswer:
    """The final answer returned to the user."""
    answer_text:      str
    question_type:    QuestionType
    tenant_name:      str
    # References cited in the answer
    cited_refs:       list[str]
    # Posture findings surfaced in the answer
    posture_findings: dict        # ref → finding
    # Verification
    verification:     VerificationResult | None
    verified:         bool
    # Stats
    model_used:       str
    latency_ms:       int
    # Was the answer regenerated after verification failure?
    was_corrected:    bool = False
    correction_note:  str  = ""



# ── Rank-and-answer prompt ──────────────────────────────────────────────────────
# Single-pass: Mistral selects + ranks + answers in one call.
# Replaces the separate context assembly → answer flow in the graph pipeline.
# Eliminates position bias — all nodes are presented equally as a numbered list.

RANK_AND_ANSWER_SYSTEM = """You are a compliance advisor for {tenant_name}, \
specialising in {standards}. You give precise, actionable compliance guidance.

You will receive numbered compliance nodes and a user query.

STEP 1 — output exactly one line:
SELECTED: 3, 1, 7, 2, 5
(the node numbers most relevant to the query, best first)

Selection count guidance:
- Gap analysis queries: select 5-7 nodes (focus on NC/OFI findings)
- Implementation queries: select 7-10 nodes (broader coverage needed)
- Definition queries: select 3-5 nodes (tight focus)
- Posture check queries: select 5-8 nodes (all assessed controls)

STEP 2 — write your compliance answer.
Rules for your answer:
- Use ONLY the nodes you selected. Never add obligations from your training knowledge.
- Refer to controls by their ref code only: A.8.24, Art.32, 9.2 — never by node number.
- Report posture ONLY from the node data: NC / OFI / Comply / Not yet assessed.
  Never infer or assume compliance status. If a node has no posture tag, do not state one.
- Lead with NC findings, then OFI, then Comply. Never list unassessed controls as gaps.
- Be direct and actionable. State what is missing and what to do.
- N/A CONTROLS: finding="N/A" means out of scope — NEVER report as a gap or finding.
  Arion Networks exclusions: all 7.x physical controls, A.8.25-A.8.31 dev controls.
  Do not cite A.7.x, A.8.25, A.8.26, A.8.27, A.8.28, A.8.29, A.8.30, A.8.31 as gaps.
- SCOPE QUERIES: If the query asks specifically about physical security or software
  development security, respond with: "Physical security controls (A.7.x) are marked
  N/A for Arion Networks — your ISMS scope excludes physical premises controls. No
  physical security gaps are applicable to your organisation."
  Similarly for software development: "Software development security controls
  (A.8.25-A.8.31) are marked N/A — Arion Networks does not develop software."
  Do NOT surface unrelated findings (e.g. A.5.18) in response to a physical or dev query.
- UNASSESSED ≠ GAP: "Not yet assessed" means not evaluated, not that there is a finding.
  Only report controls explicitly marked NC or OFI from the posture data.
- STANDARDS SCOPE: Arion Networks has enrolled in:
    ISO 27001:2022 (certified, URS April 2025)
    ISO 27701:2019 (implementing — not yet certified)
  GDPR is evaluable INDIRECTLY via ISO 27701 Annex D mapping.
  When asked about GDPR compliance: reference ISO 27701 controls that map to the
  relevant GDPR articles, then state the posture on those controls.
  Example: "GDPR Art.32 is addressed by ISO 27701 6.11.1 (privacy risk assessment).
            Your current posture on 6.11.1 is [finding]."
  Never claim Arion "implements GDPR" — they implement ISO 27701 which maps to GDPR.
- Always use full readable citations: "ISO 27001 A.8.24" not "A.8.24", "GDPR Art. 32" not "Art.32".

GLOSSARY RULE:
Use formal audit terms throughout — NC, OFI, Comply. They match the client's audit records.
When a term appears for the first time in an answer, define it briefly inline:
  NC (Non-Conformity) — a required control or obligation is absent or not effectively implemented
  OFI (Opportunity for Improvement) — a control or obligation exists but has gaps to address
  Comply — the control or obligation is in place with evidence of effectiveness
If the user asks what a term means, explain it fully and show which controls carry that finding.
After defining a term once in an answer, use it without re-defining it.

CONTROLS vs ARTICLES — always be precise about the source:
  ISO 27001 uses CONTROLS — refer to them as "ISO 27001 control A.8.24" or
    "ISO 27001 clause 9.2". Never call an ISO 27001 item an "article".
  ISO 27701 uses CONTROLS — refer to them as "ISO 27701 control 6.11.1".
    ISO 27701 extends ISO 27001 with privacy management controls.
    It maps to GDPR requirements but is a certifiable standard, not a law.
  GDPR uses ARTICLES — refer to them as "GDPR Art. 32" or "GDPR article 32".
    GDPR is EU law, not a certifiable standard.
  ARION NETWORKS: implements ISO 27701 for privacy, not GDPR directly.
    Always reference ISO 27701 controls when advising on privacy obligations.
    Only reference GDPR articles when a client explicitly asks about the law.

SELECTION ORDER:
1. NC nodes relevant to the query (always include)
2. OFI nodes relevant to the query
3. Nodes whose obligation directly addresses the query
4. Cross-framework controls that implement a selected obligation
5. Comply nodes with relevant evidence

CRITICAL: A node's posture status comes ONLY from its [NC], [OFI], [Comply], or
[Not yet assessed] tag. If a node has no posture tag, it is unassessed — never
call it NC or OFI based on the obligation text alone.

DOCUMENT CHECKLIST GUIDANCE:
When DOCUMENT CHECKLISTS are provided below the nodes:
- For "what must our policy contain?" queries: lead your answer with the checklist items
- List all must-contain items, flagging GDPR-required ones explicitly
- Show ✓ for items present in uploaded document, ✗ for missing items
- For mixed queries (obligation + document): answer both dimensions
- Never invent checklist items not in the provided checklists

DOCUMENT INVENTORY GUIDANCE (question_type = document_inventory):

UPLOAD STATUS QUESTIONS ("have we uploaded X?", "is our X policy in the system?"):
  These MUST be answered from DOCUMENT UPLOAD STATUS section, not from posture findings.
  Posture findings (NC, OFI) describe compliance gaps — they do NOT describe file upload status.
  The DOCUMENT UPLOAD STATUS section is the only source of truth for whether a file exists.
  Answer format: "[Document title] ([ref]) is registered in the system but has NOT been uploaded yet."
  If the document is not in the alerts list, it has been uploaded — say so.
  NEVER use posture findings as a proxy for upload status.

When the query asks "what documents do we need for X":
- Lead with the specific document title required (e.g. "Information Security for Use
  of Cloud Services Policy"), not with NC/OFI posture findings
- State which standard/article requires the document
- Then list the key must-contain items for that document
- Only mention NC/OFI findings if they are directly related to the topic asked about
- Do NOT list unrelated posture findings just because they appear in the node list
- Structure: Document name → why required → key contents → current status
"""

# ── Standard label helpers ────────────────────────────────────────────────────

_STANDARD_LABELS = {
    "ISO27001:2022":  "ISO 27001",
    "ISO27001:2013":  "ISO 27001",
    "GDPR:2016/679":  "GDPR",
    "GDPR":           "GDPR",
    "ISO27002:2022":  "ISO 27002",
    "ISO27701:2019":  "ISO 27701",
    "ISO27701:2022":  "ISO 27701",
}

def _standard_label(standard_id: str) -> str:
    """Convert standard_id to readable label: ISO27001:2022 → ISO 27001"""
    return _STANDARD_LABELS.get(standard_id, standard_id.split(":")[0])


def _format_ref(standard_id: str, ref: str) -> str:
    """Format a full readable citation: ISO27001:2022 + A.8.24 → ISO 27001 A.8.24"""
    label = _standard_label(standard_id)
    if label == "GDPR":
        # Normalise Art.32 → Art. 32
        import re
        ref = re.sub(r'Art\.(\d)', r'Art. \1', ref)
    return f"{label} {ref}"


RANK_AND_ANSWER_NODE_TEMPLATE = """NODE {num} — {standard_label} {ref}{posture_tag}
{posture_line}{source_type}: {standard_label} {ref}: {obligation_text}
"""


# ── LLMAnswer ──────────────────────────────────────────────────────────────────

class LLMAnswer:
    """
    Generates and verifies compliance answers using OpenAI.

    Usage:
        llm = LLMAnswer()
        answer = llm.answer(
            query   = "What are our encryption gaps?",
            context = assembled_context,   # from ContextAssembler
        )
        print(answer.answer_text)
    """

    def __init__(
        self,
        answer_model:       str   = "gpt-4o",
        verify_model:       str   = "gpt-4o-mini",
        temperature:        float = 0.1,
        max_tokens:         int   = 1500,
        verify:             bool  = True,     # run verification pass
        max_corrections:    int   = 1,        # max regeneration attempts
    ):
        # Read LOCAL_LLM_MODEL at init time so all calls use local model
        local_model = os.getenv("LOCAL_LLM_MODEL")
        if local_model:
            answer_model = local_model
            verify_model = local_model

        # VERIFY_MODEL env var overrides verify independently
        # e.g. LOCAL_LLM_MODEL=gpt-4o-mini VERIFY_MODEL=gpt-4o
        override_verify = os.getenv("VERIFY_MODEL")
        if override_verify:
            verify_model = override_verify

        self.answer_model    = answer_model
        self.verify_model    = verify_model
        self.temperature     = temperature
        self.max_tokens      = max_tokens
        self.run_verify      = verify
        self.max_corrections = max_corrections
        self._client         = None

    # ── Public API ─────────────────────────────────────────────────────────

    def answer(
        self,
        query:   str,
        context: AssembledContext,
    ) -> ComplianceAnswer:
        """
        Generate a verified compliance answer.

        Args:
            query:   The user's original question
            context: AssembledContext from ContextAssembler

        Returns:
            ComplianceAnswer with answer_text, citations, and verification
        """
        t0 = time.time()

        # Build system prompt for this question type
        system = self._build_system_prompt(context)

        # Build user message: context + query
        user_message = self._build_user_message(query, context)

        # Pass 1 — Generate answer
        answer_text = self._call_llm(
            system      = system,
            user        = user_message,
            model       = self.answer_model,
            max_tokens  = self.max_tokens,
        )

        # Pass 2 — Verify
        verification  = None
        was_corrected = False
        correction_note = ""

        if self.run_verify:
            verification = self._verify(
                context_text = context.context_text,
                answer_text  = answer_text,
                posture      = context.posture_summary,
            )

            # Only attempt correction for clear, non-contradictory failures
            is_spurious = self._is_spurious_failure(verification)

            if (verification.verdict == "fail" and
                    verification.issues and
                    not is_spurious and
                    self.max_corrections > 0):
                answer_text, was_corrected, correction_note = self._correct(
                    query       = query,
                    context     = context,
                    system      = system,
                    original    = answer_text,
                    issues      = verification.issues,
                    corrections = verification.corrections,
                )
                if was_corrected:
                    verification = self._verify(
                        context_text = context.context_text,
                        answer_text  = answer_text,
                        posture      = context.posture_summary,
                    )

        latency_ms = round((time.time() - t0) * 1000)

        return ComplianceAnswer(
            answer_text      = answer_text,
            question_type    = context.question_type,
            tenant_name      = context.tenant_name,
            cited_refs       = self._extract_refs(answer_text),
            posture_findings = context.posture_summary,
            verification     = verification,
            verified         = (verification is None or
                                verification.verdict == "pass"),
            model_used       = self.answer_model,
            latency_ms       = latency_ms,
            was_corrected    = was_corrected,
            correction_note  = correction_note,
        )

    # ── Prompt builders ────────────────────────────────────────────────────

    def _build_system_prompt(self, context: AssembledContext) -> str:
        """Build the system prompt for this question type and tenant."""
        standards_str = " + ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
            for s in context.intent.standards_scope
        )
        structure = ANSWER_STRUCTURES.get(
            context.question_type,
            ANSWER_STRUCTURES[QuestionType.UNKNOWN],
        )
        return SYSTEM_PROMPT.format(
            tenant_name      = context.tenant_name,
            standards        = standards_str,
            answer_structure = structure,
        )

    def _build_user_message(
        self,
        query:   str,
        context: AssembledContext,
    ) -> str:
        """Build the user message: context block + question."""
        posture_note = ""
        if context.has_posture:
            findings = context.posture_summary
            nc_refs  = [r.split(":")[-1] for r, v in findings.items()
                        if v.get("finding") == "NC"]
            ofi_refs = [r.split(":")[-1] for r, v in findings.items()
                        if v.get("finding") == "OFI"]
            comply_refs = [r.split(":")[-1] for r, v in findings.items()
                           if v.get("finding") == "Comply"]

            parts = []
            if nc_refs:
                parts.append(f"NC (non-compliant, must fix): {', '.join(nc_refs)}")
            if ofi_refs:
                parts.append(f"OFI (improvement needed): {', '.join(ofi_refs)}")
            if comply_refs:
                parts.append(f"Comply (evidence in place): {', '.join(comply_refs)}")

            if parts:
                posture_note = (
                    f"\nARION NETWORKS POSTURE FINDINGS — state these directly, "
                    f"do not hedge:\n  " + "\n  ".join(parts) +
                    f"\nLead your answer with NC findings first, then OFI, "
                    f"then summarise Comply evidence."
                )

        # Build document alerts note
        # Strategy: inject alerts that are relevant to controls in the current context
        # This is additive — it doesn't change routing, just enriches the answer
        doc_alert_note = ""
        doc_alerts = getattr(context, "document_alerts", None) or []
        if doc_alerts:
            # Identify which controls are in scope for this query
            controls_in_scope = set()
            for nid in context.node_ids_used:
                ref = nid.split(":")[-1] if ":" in nid else nid
                controls_in_scope.add(ref)
            # Also include posture refs
            for ref in context.posture_summary:
                controls_in_scope.add(ref.split(":")[-1])

            critical = [a for a in doc_alerts if a.get("alert_type") == "CRITICAL"]
            warning  = [a for a in doc_alerts if a.get("alert_type") == "WARNING"]

            # Filter to alerts relevant to controls in scope (if we know what's in scope)
            # If no controls in scope, show all critical/warning alerts
            def is_relevant(alert):
                linked = alert.get("linked_controls", "") or ""
                if not controls_in_scope:
                    return True
                return any(ctrl.strip() in controls_in_scope
                          for ctrl in linked.split(","))

            relevant_critical = [a for a in critical if is_relevant(a)]
            relevant_warning  = [a for a in warning  if is_relevant(a)]

            # Fall back to all critical/warning if none are specifically relevant
            show_critical = relevant_critical or critical[:3]
            show_warning  = relevant_warning  or []

            if show_critical or show_warning:
                alert_lines = []
                for a in show_critical[:5]:
                    alert_lines.append(
                        f"  CRITICAL — {a['document_title']} ({a['external_ref']}) "
                        f"is registered but NOT uploaded. "
                        f"Linked to NC on: {a.get('linked_controls','')}"
                    )
                for a in show_warning[:3]:
                    alert_lines.append(
                        f"  WARNING — {a['document_title']} ({a['external_ref']}) "
                        f"is registered but NOT uploaded. "
                        f"Linked to OFI on: {a.get('linked_controls','')}"
                    )
                doc_alert_note = (
                    "\nDOCUMENT UPLOAD STATUS — files registered but not yet uploaded:\n"
                    + "\n".join(alert_lines)
                    + "\n\nIMPORTANT: If the question asks whether a document has been "
                    "uploaded, answer directly from this list. Do not say you lack information "
                    "about uploads — use this list as your source of truth for upload status.\n"
                )

        return (
            f"COMPLIANCE CONTEXT\n"
            f"{'─' * 60}\n"
            f"{context.context_text}\n"
            f"{'─' * 60}\n"
            f"{doc_alert_note}\n"   # document status BEFORE posture — LLM reads top-down
            f"{posture_note}\n"
            f"QUESTION\n"
            f"{query}"
        )

    # ── LLM calls ──────────────────────────────────────────────────────────

    # ── Rank-and-answer (combined pass for graph pipeline) ────────────────────

    def rank_and_answer(
        self,
        query:            str,
        nodes:            list,          # list[ExpandedNode]
        posture:          dict | None,   # node_id → {finding, gap_description, evidence}
        intent,                          # QueryIntent
        tenant_name:      str  = "",
        standards:        str  = "ISO 27001 + GDPR",
        doc_contexts:     dict | None = None,   # node_id → DocumentContext
        incident_contexts:list | None = None,   # list[IncidentObligationContext]
    ) -> "ComplianceAnswer":
        """
        Combined rank + answer in a single Mistral call.

        Replaces the assemble() → answer() flow in the graph pipeline.
        Eliminates position bias — all nodes presented as a numbered list.
        Mistral selects the most relevant nodes and answers from them.

        Returns ComplianceAnswer with:
          - answer_text: the compliance answer
          - cited_refs: only refs from selected nodes
          - posture_findings: posture from selected nodes
          - was_corrected: True if verification triggered a correction
        """
        t0 = time.time()

        # ── Format nodes as numbered list ─────────────────────────────────
        node_list   = [n for n in nodes if not n.is_informational]
        num_to_node = {}
        node_lines  = []

        for i, node in enumerate(node_list, 1):
            num_to_node[i] = node
            rec    = (posture or {}).get(node.node_id, {})
            finding        = rec.get("finding", "")
            gap            = rec.get("gap_description", "")
            evidence       = rec.get("evidence_text", "")
            confirm_status = rec.get("confirmation_status")  # None = legacy row

            # Confirmation label: DRAFT findings are indicative, not authoritative
            is_confirmed = confirm_status in ("confirmed", "overridden")
            is_draft     = confirm_status == "draft" or confirm_status is None
            confirm_label = "" if is_confirmed else " [DRAFT]"

            posture_tag  = f" [{finding}{confirm_label}]" if finding else " [Not yet assessed]"
            if finding == "NC":
                posture_line = f"Posture: ✗ NC{confirm_label} — {gap}\n" if gap else f"Posture: ✗ NC{confirm_label}\n"
            elif finding == "OFI":
                posture_line = f"Posture: △ OFI{confirm_label} — {gap}\n" if gap else f"Posture: △ OFI{confirm_label}\n"
            elif finding == "Comply":
                posture_line = f"Posture: ✓ Comply{confirm_label} — {evidence}\n" if evidence else f"Posture: ✓ Comply{confirm_label}\n"
            elif finding == "N/A":
                posture_line = "Posture: — N/A (excluded from scope — DO NOT REPORT AS GAP)\n"
            else:
                posture_line = ""

            # Get obligation text from metadata (stored separately from embedding)
            # Fall back to first 400 chars of document, then title
            obligation = (
                node.metadata.get("obligation_text", "")
                or node.metadata.get("business_description", "")
                or (node.document or "")[:400]
                or node.title
                or ""
            )[:400]
            node_lines.append(
                RANK_AND_ANSWER_NODE_TEMPLATE.format(
                    num            = i,
                    ref            = node.ref,
                    standard_label = _standard_label(node.standard_id),
                    source_type    = "Article" if node.standard_id.startswith("GDPR") else "Control",
                    posture_tag    = posture_tag,
                    posture_line   = posture_line,
                    obligation_text= obligation,
                )
            )

        nodes_block = "\n".join(node_lines)

        # ── Build system + user messages ──────────────────────────────────
        system = RANK_AND_ANSWER_SYSTEM.format(
            tenant_name = tenant_name or "your organisation",
            standards   = standards,
        )

        # ── Build incident context header ─────────────────────────────────
        incident_header = ""
        if incident_contexts:
            critical = [i for i in incident_contexts
                        if i.urgency in ("overdue", "critical")]
            if critical:
                inc = critical[0]
                incident_header = (
                    f"\n⚠ ACTIVE INCIDENT: {inc.incident_type.replace('_',' ').upper()} "
                    f"[{inc.severity.upper()}]"
                )
                if inc.deadline_at:
                    urgency = "OVERDUE" if inc.urgency == "overdue" else "< 12 HOURS"
                    incident_header += f" — Deadline: {urgency}\n"

        # ── Build checklist block for document queries ────────────────────
        # Inject checklist items alongside nodes so GPT can use both
        from rag.classifier import QuestionType
        checklist_block = ""
        if doc_contexts and intent.dimensions.needs_documentation:
            cl_lines = ["\nDOCUMENT CHECKLISTS (use these for document content questions):"]
            for node_id, ctx in list(doc_contexts.items())[:5]:
                # Derive standard_id from node_id e.g. "ISO27001:2022:A.8.24"
                std_id = ":".join(node_id.split(":")[:2]) if ":" in node_id else ""
                full_ref = _format_ref(std_id, ctx.control_ref) if std_id else ctx.control_ref
                cl_lines.append(
                    f"\n{full_ref} — {ctx.document_title} [{ctx.trigger_type}]"
                )
                for item in ctx.must_contain:
                    status = ""
                    if item.status == "present":
                        status = " ✓"
                    elif item.status == "missing":
                        status = " ✗"
                    elif item.status is None:
                        status = " ?"   # not yet assessed
                    gdpr    = " [GDPR required]" if item.gdpr_required else ""
                    excerpt = f" — {item.excerpt}" if item.excerpt and item.status == "missing" else ""
                    cl_lines.append(f"  -{status} {item.text}{gdpr}{excerpt}")
                if ctx.should_contain:
                    cl_lines.append("  Should also contain:")
                    for item in ctx.should_contain[:3]:
                        cl_lines.append(f"    - {item.text}")
            checklist_block = "\n".join(cl_lines)

        user = f"""QUERY: {query}{incident_header}

COMPLIANCE NODES ({len(node_list)} total):
{nodes_block}{checklist_block}

Output the SELECTED: line first, then your answer directly (no headers or labels)."""

        # ── Single Mistral call ───────────────────────────────────────────
        raw = self._call_llm(
            system     = system,
            user       = user,
            model      = self.answer_model,
            max_tokens = self.max_tokens,
            step       = "rank_answer",
        )

        # ── Log raw output for debugging ──────────────────────────────────
        logger = get_logger()
        if logger:
            logger.log_call(
                step       = "rank_raw",
                model      = self.answer_model,
                system     = f"Nodes presented: {len(node_list)}",
                user       = "\n".join(
                    f"NODE {i} — {node_list[i-1].ref}"
                    for i in range(1, min(len(node_list)+1, 25))
                ),
                response   = raw[:1000],
                latency_ms = 0,
                metadata   = {"node_count": len(node_list)},
            )

        # ── Parse SELECTED line and answer ────────────────────────────────
        selected_nums, answer_text = self._parse_rank_answer(raw, num_to_node)
        selected_nodes = [num_to_node[n] for n in selected_nums if n in num_to_node]

        # ── Log selection ─────────────────────────────────────────────────
        if logger:
            logger.log_call(
                step       = "selected",
                model      = self.answer_model,
                system     = f"Selected {len(selected_nodes)}/{len(node_list)} nodes",
                user       = "",
                response   = f"SELECTED: {selected_nums}\n" + "\n".join(
                    f"  {n.ref} [{(posture or {}).get(n.node_id, {}).get('finding', '?')}]"
                    for n in selected_nodes
                ),
                latency_ms = 0,
            )

        # ── Extract cited refs and posture findings ────────────────────────
        cited_refs      = self._extract_refs(answer_text)
        posture_findings = {}
        for node in selected_nodes:
            rec = (posture or {}).get(node.node_id, {})
            if rec.get("finding"):
                posture_findings[node.ref] = rec["finding"]

        # ── Verification against selected nodes + checklists ─────────────
        selected_context = "\n\n".join(
            f"{node.ref}: {node.metadata.get('obligation_text', '') or node.title}"
            for node in selected_nodes
        )
        # Append checklist content to verification context so verifier
        # doesn't flag GDPR-required checklist items as unsupported
        if doc_contexts:
            cl_lines = ["\nDOCUMENT CHECKLISTS (these are the authoritative requirements):"]
            for node_id, ctx in list(doc_contexts.items())[:3]:
                cl_lines.append(f"{ctx.control_ref} — {ctx.document_title}")
                for item in ctx.must_contain:
                    gdpr = " [GDPR required]" if item.gdpr_required else ""
                    cl_lines.append(f"  - {item.text}{gdpr}")
            selected_context += "\n" + "\n".join(cl_lines)
        posture_summary = {
            node.ref: (posture or {}).get(node.node_id, {})
            for node in selected_nodes
        }

        verification  = None
        was_corrected = False
        if self.run_verify and selected_nodes:
            verification = self._verify(
                context_text  = selected_context,   # only selected nodes
                answer_text   = answer_text,
                posture       = posture_summary,
                question_type = intent.question_type.value if intent else None,
            )
            is_spurious = self._is_spurious_failure(verification)
            if (verification.verdict == "fail" and
                    verification.issues and not is_spurious and
                    self.max_corrections > 0):
                corrected = self._call_llm(
                    system = system,
                    user   = (
                        f"{user}\n\nYour previous answer had these issues:\n"
                        + "\n".join(f"- {i}" for i in verification.issues)
                        + "\n\nPlease correct ONLY those specific issues. Keep all NC findings, OFI findings, and correctly-labeled [Not yet assessed] items. Start with SELECTED: line."
                    ),
                    model      = self.answer_model,
                    max_tokens = self.max_tokens,
                    step       = "correct",
                )
                _, answer_text = self._parse_rank_answer(corrected, num_to_node)
                was_corrected  = True

        latency_ms = round((time.time() - t0) * 1000)

        return ComplianceAnswer(
            answer_text      = answer_text,
            question_type    = intent.question_type,
            tenant_name      = tenant_name,
            cited_refs       = cited_refs,
            posture_findings = posture_findings,
            verification     = verification,
            verified         = verification.verdict == "pass" if verification else False,
            model_used       = self.answer_model,
            latency_ms       = latency_ms,
            was_corrected    = was_corrected,
        )

    def _answer_document_query(
        self,
        query:        str,
        intent,                     # QueryIntent
        doc_contexts: dict,         # node_id → DocumentContext
        tenant_name:  str,
        standards:    str,
    ) -> "ComplianceAnswer":
        """
        Dedicated answer path for DOCUMENT_CONTENT and DOCUMENT_INVENTORY queries.
        The checklist is the primary content — not the obligation node list.
        """
        import time
        t0 = time.time()

        from rag.classifier import QuestionType

        # ── Build checklist context ────────────────────────────────────────
        checklist_lines = []
        all_refs = []

        for node_id, ctx in doc_contexts.items():
            checklist_lines.append(
                f"\n{ctx.control_ref}: {ctx.document_title}"
            )
            checklist_lines.append(f"Type: {ctx.document_type}")
            checklist_lines.append(f"Purpose: {ctx.description}")

            if ctx.has_document_uploaded:
                pct = ctx.completeness_pct
                checklist_lines.append(f"Completeness: {pct}%")
                for item in ctx.present_must:
                    checklist_lines.append(f"  ✓ {item.text}")
                for item in ctx.missing_must:
                    gdpr = " [GDPR required]" if item.gdpr_required else ""
                    checklist_lines.append(f"  ✗ {item.text}{gdpr}")
            else:
                checklist_lines.append("Status: not yet uploaded")
                checklist_lines.append("Must contain:")
                for item in ctx.must_contain:
                    gdpr = " [GDPR required]" if item.gdpr_required else ""
                    checklist_lines.append(f"  - {item.text}{gdpr}")
                if ctx.should_contain:
                    checklist_lines.append("Should also contain:")
                    for item in ctx.should_contain[:3]:
                        checklist_lines.append(f"  - {item.text}")

            all_refs.append(ctx.control_ref)

        checklist_text = "\n".join(checklist_lines)

        # ── Build prompt ──────────────────────────────────────────────────
        system = (
            f"You are a compliance advisor for {tenant_name}, "
            f"specialising in {standards}.\n\n"
            f"Answer the query directly from the document requirements provided.\n"
            f"Be specific and actionable. List items clearly.\n"
            f"Flag GDPR-required items explicitly.\n"
            f"If a document is uploaded, highlight what is missing.\n"
            f"Never add requirements not in the checklist below."
        )

        user = f"QUERY: {query}\n\nDOCUMENT REQUIREMENTS:\n{checklist_text}"

        raw = self._call_llm(
            system     = system,
            user       = user,
            model      = self.answer_model,
            max_tokens = self.max_tokens,
            step       = "doc_answer",
        )

        # ── Simple verification for document answers ──────────────────────
        answer_text = raw.strip()

        # Run verification against checklist
        verified      = False
        was_corrected = False
        if self.run_verify:
            verify_context = (
                f"Document requirements for {', '.join(all_refs)}:\n"
                f"{checklist_text[:2000]}"
            )
            verification = self._verify(
                answer   = answer_text,
                context  = verify_context,
                query    = query,
            )
            verified = verification.verdict == "pass"

            if not verified and not self._is_spurious_failure(verification):
                corrected_raw = self._call_llm(
                    system     = system,
                    user       = (
                        user + "\n\nCorrect these issues in your answer:\n"
                        + "\n".join(f"- {i}" for i in verification.issues)
                    ),
                    model      = self.answer_model,
                    max_tokens = self.max_tokens,
                    step       = "doc_correct",
                )
                answer_text   = corrected_raw.strip()
                was_corrected = True

        latency_ms = round((time.time() - t0) * 1000)

        return ComplianceAnswer(
            answer_text      = answer_text,
            verified         = verified,
            was_corrected    = was_corrected,
            cited_refs       = all_refs,
            posture_findings = {},
            latency_ms       = latency_ms,
            model_used       = self.answer_model,
        )

    def _parse_rank_answer(
        self,
        raw:          str,
        num_to_node:  dict,
    ) -> tuple[list[int], str]:
        """
        Parse the SELECTED: line and answer from rank_and_answer output.
        Returns (selected_nums, answer_text).
        Falls back gracefully if SELECTED line is missing.
        """
        selected_nums = []
        answer_text   = raw.strip()

        # Find SELECTED: line
        m = re.search(r"SELECTED\s*:\s*([\d,\s]+)", raw, re.IGNORECASE)
        if m:
            for part in m.group(1).split(","):
                part = part.strip()
                if part.isdigit():
                    n = int(part)
                    if n in num_to_node:
                        selected_nums.append(n)
            # Remove SELECTED line from answer text
            answer_text = raw[m.end():].strip()
            # Strip leading labels including bold markdown variants
            # e.g. "COMPLIANCE ANSWER:", "**COMPLIANCE ANSWER:**", "STEP 2 —"
            # Strip label-only first line (e.g. "**COMPLIANCE ANSWER:**")
            answer_text = re.sub(
                r"^(?:\*{0,2}(?:COMPLIANCE\s+ANSWER|ANSWER|PART\s*\d|STEP\s*\d)\*{0,2}[:\s—-]*\n+)",
                "", answer_text, flags=re.IGNORECASE
            ).strip()

        # Fallback: use all nodes if SELECTED not found
        if not selected_nums:
            selected_nums = list(num_to_node.keys())

        return selected_nums, answer_text

    def _call_llm(
        self,
        system:     str,
        user:       str,
        model:      str,
        max_tokens: int = 1500,
        step:       str = "answer",
    ) -> str:
        """Single OpenAI call. Returns response text."""
        client = self._get_client()
        t0 = time.time()
        try:
            response = client.chat.completions.create(
                model       = model,
                temperature = self.temperature,
                max_tokens  = max_tokens,
                messages    = [
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
            )
            result = response.choices[0].message.content.strip()
            latency = round((time.time() - t0) * 1000)
            logger = get_logger()
            if logger:
                logger.log_call(
                    step       = step,
                    model      = model,
                    system     = system[:300],
                    user       = user[:800],
                    response   = result,
                    latency_ms = latency,
                )
            return result
        except Exception as e:
            raise RuntimeError(f"LLM call failed ({model}): {e}")

    def _verify(
        self,
        context_text:  str,
        answer_text:   str,
        posture:       dict | None = None,
        question_type: str | None  = None,  # e.g. "definition", "gap_analysis"
    ) -> VerificationResult:
        """Run verification pass using gpt-4o-mini."""
        client = self._get_client()
        t0 = time.time()

        # Build posture preamble so verifier knows findings are factual inputs
        posture_preamble = ""
        if posture:
            lines = ["FACTUAL POSTURE FINDINGS (these are pre-assessed facts, "
                     "not claims to verify against legal text):"]
            for node_id, rec in posture.items():
                ref     = node_id.split(":")[-1]
                finding = rec.get("finding", "?")
                gap     = rec.get("gap_description", "")
                lines.append(f"  {ref}: {finding}" +
                              (f" — {gap}" if gap else ""))
            posture_preamble = "\n".join(lines) + "\n\n"

        query_type_note = ""
        if question_type:
            query_type_note = (
                f"QUERY TYPE: {question_type}\n"
                f"{'Definition queries require correct definition + example only — not full posture dump.' if question_type == 'definition' else ''}"
                f"\n\n"
            )
        prompt = (
            f"{query_type_note}"
            f"{posture_preamble}"
            f"CONTEXT:\n{context_text[:5000]}\n\n"
            f"ANSWER:\n{answer_text}"
        )
        try:
            response = client.chat.completions.create(
                model       = self.verify_model,
                temperature = 0.0,
                max_tokens  = 400,
                messages    = [
                    {"role": "system", "content": VERIFICATION_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            raw    = response.choices[0].message.content.strip()
            parsed = self._parse_json(raw)

            if parsed:
                result = VerificationResult(
                    verdict     = parsed.get("verdict", "pass"),
                    confidence  = float(parsed.get("confidence", 0.8)),
                    issues      = parsed.get("issues", []),
                    corrections = parsed.get("corrections", []),
                    reasoning   = parsed.get("reasoning", ""),
                )
                logger = get_logger()
                if logger:
                    logger.log_verification(
                        verdict     = result.verdict,
                        confidence  = result.confidence,
                        issues      = result.issues,
                        corrections = result.corrections,
                        reasoning   = result.reasoning,
                        latency_ms  = round((time.time() - t0) * 1000),
                        model       = self.verify_model,
                    )
                return result
        except Exception:
            pass

        return VerificationResult(
            verdict    = "pass",
            confidence = 0.5,
            issues     = [],
            corrections = [],
            reasoning  = "Verification parse error — defaulting to pass",
        )

    def _correct(
        self,
        query:       str,
        context:     AssembledContext,
        system:      str,
        original:    str,
        issues:      list[str],
        corrections: list[str],
    ) -> tuple[str, bool, str]:
        """
        Attempt to correct a failed verification.
        Returns (corrected_answer, was_corrected, correction_note).
        """
        issues_text = "\n".join(f"- {i}" for i in issues)
        corr_text   = "\n".join(f"- {c}" for c in corrections)

        correction_prompt = (
            f"Your previous answer had the following accuracy issues:\n"
            f"{issues_text}\n\n"
            f"Suggested corrections:\n{corr_text}\n\n"
            f"Please provide a corrected answer that addresses these issues. "
            f"Start your answer directly — do not acknowledge these instructions "
            f"or say 'here is the corrected answer'. Just give the answer."
        )
        client = self._get_client()
        try:
            response = client.chat.completions.create(
                model       = self.answer_model,
                temperature = self.temperature,
                max_tokens  = self.max_tokens,
                messages    = [
                    {"role": "system",    "content": system},
                    {"role": "user",      "content":
                        self._build_user_message(query, context)},
                    {"role": "assistant", "content": original},
                    {"role": "user",      "content": correction_prompt},
                ],
            )
            corrected = response.choices[0].message.content.strip()

            # Strip any preamble the model adds despite instructions
            corrected = self._strip_correction_preamble(corrected)

            note = f"Corrected after verification: {'; '.join(issues[:2])}"
            return corrected, True, note
        except Exception as e:
            return original, False, f"Correction failed: {e}"

    # Preamble patterns the model uses when acknowledging corrections
    _PREAMBLE_PATTERNS = [
        "thank you for pointing out",
        "thank you for the feedback",
        "you're right",
        "i apologize",
        "here is the corrected answer",
        "here's the corrected answer",
        "here is a corrected version",
        "here's a corrected version",
        "here is the updated answer",
        "here's the updated answer",
        "certainly, here is",
        "certainly, here's",
        "of course, here",
        "sure, here is",
        "sure, here's",
        "based on your feedback",
        "based on the feedback",
    ]

    def _strip_correction_preamble(self, text: str) -> str:
        """
        Remove conversational preambles the model adds when correcting.
        These appear when the model treats the correction prompt as dialogue.
        """
        import re
        lines = text.split('\n')

        # Check first 1-3 lines for preamble patterns
        skip_until = 0
        for i, line in enumerate(lines[:4]):
            line_lower = line.lower().strip()
            if any(line_lower.startswith(p) for p in self._PREAMBLE_PATTERNS):
                skip_until = i + 1
            elif skip_until > 0 and line.strip() == "":
                # Skip blank line after preamble
                skip_until = i + 1
            elif skip_until > 0:
                # Hit substantive content — stop stripping
                break

        if skip_until > 0:
            return '\n'.join(lines[skip_until:]).strip()
        return text

    # ── Helpers ────────────────────────────────────────────────────────────

    def _is_spurious_failure(self, verification: VerificationResult) -> bool:
        """
        Detect self-contradictory or low-value verification failures.
        Returns True if the failure should be ignored.
        """
        if not verification.issues:
            return True

        contradiction_phrases = [
            "correctly stated",
            "is correct",
            "correctly identifies",
            "correctly references",
            "is correctly",
        ]
        for issue in verification.issues:
            issue_lower = issue.lower()
            for phrase in contradiction_phrases:
                if phrase in issue_lower:
                    return True

        # OFI ≠ non-compliant. Flagging "compliant" as wrong because of OFI is spurious.
        import re
        ofi_compliance_phrases = [
            "incorrectly states that the organization is compliant",
            "incorrectly states that the organisation is compliant",
            "incorrectly claims compliance",
            "should not be stated as compliant",
        ]
        for issue in verification.issues:
            issue_lower = issue.lower()
            for phrase in ofi_compliance_phrases:
                if phrase in issue_lower:
                    # Only spurious if there is no NC finding mentioned
                    has_nc = bool(re.search(r'\bnc\b', issue_lower)) or \
                             'non-compli' in issue_lower
                    if not has_nc:
                        return True

        # Self-contradiction: "X is incorrectly stated as Y while context states it is Y"
        import re
        for issue in verification.issues:
            m = re.search(
                r'incorrectly stated as (\w+).*?(?:while|but).*?states? (?:it )?is \1',
                issue, re.IGNORECASE
            )
            if m:
                return True

        return False

    def _extract_refs(self, text: str) -> list[str]:
        """Extract article and control references from answer text."""
        # GDPR: Art.32, Art.32.1, Art.32.1.a
        gdpr      = re.findall(r'\bArt\.\d+(?:\.\d+)*(?:\.[a-z])?\b', text)
        # ISO Annex A: A.5.15, A.8.24
        iso_annex = re.findall(r'\bA\.\d+\.\d+\b', text)
        # ISO Management clauses: 6.1.2, 5.1
        # Exclude numbers that are substrings of already-matched refs
        iso_mgmt  = re.findall(
            r'(?<!Art\.)(?<!A\.)\b\d+\.\d+(?:\.\d+)?\b', text
        )

        # Build set of numeric suffixes already claimed
        claimed = set()
        for ref in gdpr:
            m = re.match(r'Art\.(\d+(?:\.\d+)*)', ref)
            if m:
                claimed.add(m.group(1))
        for ref in iso_annex:
            m = re.match(r'A\.(\d+\.\d+)', ref)
            if m:
                claimed.add(m.group(1))

        iso_mgmt = [r for r in iso_mgmt if r not in claimed]

        # Deduplicate preserving order
        seen = set()
        refs = []
        for r in gdpr + iso_annex + iso_mgmt:
            if r not in seen:
                seen.add(r)
                refs.append(r)
        return refs

    def _parse_json(self, raw: str) -> dict | None:
        """Parse JSON from LLM response, stripping markdown fences."""
        clean = re.sub(r'```(?:json)?\s*', '', raw).strip().rstrip('`')
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        return None

    def _get_client(self):
        """
        Lazy-load OpenAI-compatible client.

        Supports two modes:
          Local LLM (Mistral via llama.cpp):
            export LOCAL_LLM_BASE_URL=http://localhost:8080/v1
            export LOCAL_LLM_MODEL=mistral-small-3.2-24b

          Cloud (GPT-4o fallback):
            export OPENAI_API_KEY=sk-proj-...
        """
        if self._client is None:
            import openai
            local_url = os.getenv("LOCAL_LLM_BASE_URL")

            if local_url:
                # Local Mistral via llama.cpp — OpenAI-compatible API
                # api_key is required by the SDK but ignored by llama.cpp
                self._client = openai.OpenAI(
                    base_url = local_url.rstrip("/"),
                    api_key  = "local",
                )
                # Override model names to use local model
                local_model = os.getenv("LOCAL_LLM_MODEL")
                if local_model:
                    self.answer_model = local_model
                    self.verify_model = local_model  # same model for verification
            else:
                # Cloud GPT-4o fallback
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError(
                        "Neither LOCAL_LLM_BASE_URL nor OPENAI_API_KEY is set.\n"
                        "  For local Mistral:  export LOCAL_LLM_BASE_URL=http://localhost:8080/v1\n"
                        "  For cloud GPT-4o:   export OPENAI_API_KEY=sk-..."
                    )
                self._client = openai.OpenAI(api_key=api_key)
        return self._client
