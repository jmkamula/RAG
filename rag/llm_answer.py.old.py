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
- Be precise about conditions. If an obligation only applies in certain
  circumstances (e.g. DPIA required only for high-risk processing, not all
  new projects), state the condition. Never drop qualifying conditions.
- Cite article numbers and control references inline: Art.32.1.a, A.8.24, Art.33.
- When posture data is available, lead with the finding. Do not bury it.
  Say: "Your encryption policy has an OFI gap — it does not explicitly scope \
personal data at rest and in transit (A.8.24)."
  Not: "A.8.24 requires an encryption policy. Your policy may need review."
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
1. How the standards address this topic
2. Where they overlap (same obligation, different framing)
3. Where they diverge (one standard goes further)
4. Practical implication: satisfying one standard's requirement \
and how far it covers the other""",

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

WHAT TO FLAG (genuine errors only):
- Wrong article numbers (answer says Art.33.2, context says Art.33.1)
- Wrong time periods (answer says 48 hours, context says 72 hours)
- Obligations invented that do not appear anywhere in the context
- Posture findings contradicted (context says Comply, answer says NC)
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

        return (
            f"COMPLIANCE CONTEXT\n"
            f"{'─' * 60}\n"
            f"{context.context_text}\n"
            f"{'─' * 60}\n"
            f"{posture_note}\n\n"
            f"QUESTION\n"
            f"{query}"
        )

    # ── LLM calls ──────────────────────────────────────────────────────────

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
        context_text: str,
        answer_text:  str,
        posture:      dict | None = None,
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

        prompt = (
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
