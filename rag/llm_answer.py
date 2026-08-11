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
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

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

POSTURE FINDING DISCIPLINE — STRICT (must not violate)
- The tag IS the verdict. A control's formal posture section is fixed
  by its [NC] / [OFI] / [Comply] / [N/A] tag in the context. Never
  re-categorize a control based on prose in its gap, evidence, or
  remedial-action text. "X is in place but needs ongoing review" is
  Comply if tagged Comply — it is NOT an OFI.
- Each control appears in EXACTLY ONE formal finding section per
  answer. Never list the same control under two different finding
  headings (e.g. once under "OFI" and again under "Comply"). If you
  catch yourself listing a control twice, drop the duplicate and keep
  only the section that matches its tag.
- For Comply controls, do not call them "gaps", "issues", "concerns",
  or "areas for improvement" — those words belong to OFI/NC controls.

ADVISORY COMMENTARY — QUARANTINED
You MAY add useful best-practice advice that isn't anchored to a posture
tag (e.g. "ongoing monitoring would help confirm A.5.30 stays effective
under change"). When you do:
  - Put it under a SEPARATE "Recommendations" or "Suggested
    improvements" section, clearly labelled as advisory.
  - Never place such commentary under "Opportunities for Improvement
    (OFI)" — that heading is reserved for controls explicitly tagged
    [OFI] in the context.
  - It's fine to reference a Comply control in the Recommendations
    section as long as the Comply listing above is unchanged. Same
    control, two roles: formal Comply finding above, advisory note
    below — never both labelled as findings.

WORKED EXAMPLE — DO NOT WRITE THIS:
  **Opportunities for Improvement (OFI):**
  - A.5.30: ICT readiness is in place but needs ongoing monitoring.

  **Comply:**
  - A.5.30: ICT readiness for business continuity is in place.

Why this is wrong: A.5.30 is tagged Comply in the context. It appears
under Comply ONLY. The "needs ongoing monitoring" remark is advisory and
must not borrow the OFI heading.

WORKED EXAMPLE — WRITE IT LIKE THIS:
  **Comply:**
  - A.5.30: ICT readiness for business continuity is in place.

  **Recommendations (advisory, not formal findings):**
  - A.5.30: regular review and testing of BC measures would help confirm
    ongoing effectiveness as services evolve.

Notice: A.5.30 appears in exactly one finding section (Comply). The
advisory note about monitoring lives under Recommendations and is
clearly labelled as not-a-formal-finding.

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
Context: ISO 27001 is the security-controls foundation; ISO 27701 extends it with a Privacy Information Management System (PIMS); GDPR is EU privacy law. ISO 27701 Annex D maps every 27701 Annex A + Annex B control to specific GDPR Articles.

When a cross-framework query is asked, cite posture from ALL enrolled + curated standards that address the topic — 27001, 27701, and GDPR are all first-class. A 27701 control finding is not a stand-in for a GDPR finding; both may be relevant.

1. Opening: one sentence naming which frameworks are being cited for this query
2. NC findings: each NC with the specific framework + ref
3. OFI findings: each OFI with the accountability/security risk framed against the specific framework
4. Cross-framework links: where the same topic surfaces in multiple frameworks, explain the bridge relationship (e.g. "27701 A.7.2.6 operationalises GDPR Art.28 for processor contracts")
5. Summary: priority actions across frameworks""",

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
    # References cited in the answer (union of primary + xfw — kept flat
    # for backward compatibility with state["cited_refs"] consumers)
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
    # Layered selection — refs chosen from each layer. Lets downstream
    # consumers (UI badges, trace, multi-framework drill-down) tell
    # primary-framework citations apart from cross-framework citations
    # without re-parsing the answer text.
    primary_refs:     list[str] = field(default_factory=list)
    xfw_refs:         list[str] = field(default_factory=list)
    # Tier-4 structured templates block (see rag/templates/answer_footer.py
    # :build_templates_block). Populated by arion_graph.py after
    # rank_and_answer returns, when the query is action-oriented and
    # cited refs include NC/OFI controls. The chat UI renders this as a
    # per-leaf card block below the answer bubble; API consumers get the
    # same data as JSON on the response.
    templates_block:  dict | None = None
    # Ship 18'.b — structured answer payload (intro + actions[] + related[]).
    # None when structured path failed (LLM emitted malformed JSON) — the
    # prose `answer_text` remains the source of truth in that case.
    answer_structured: dict | None = None



# ── Rank-and-answer prompt ──────────────────────────────────────────────────────
# Single-pass: Mistral selects + ranks + answers in one call.
# Replaces the separate context assembly → answer flow in the graph pipeline.
# Eliminates position bias — all nodes are presented equally as a numbered list.

RANK_AND_ANSWER_SYSTEM = """You are a compliance advisor for {tenant_name}, \
specialising in {standards}. You give precise, actionable compliance guidance.

You will receive numbered compliance nodes grouped into two layers:
  LAYER 1 — primary obligation nodes for the framework the query targets.
            Posture comes directly from the [NC] / [OFI] / [Comply] /
            [Not yet assessed] tag on the node.
  LAYER 2 — cross-framework (XFW) nodes from other frameworks that map
            to a Layer 1 node. Each carries:
              * an [XFW→ ref] tag listing the linked Layer 1 refs
              * an [Addressed via ref, ref, ...] posture tag when any of
                those linked primaries have been assessed
              * a "Posture from linked primaries:" block enumerating the
                finding (NC/OFI/Comply/Not yet assessed) for each linked
                ref. THIS IS THE ONLY SOURCE OF POSTURE FOR A LAYER 2
                NODE. Never assign NC/OFI/Comply to a Layer 2 node from
                its obligation text alone.

STEP 1 — output exactly TWO lines, in this order, even if one is empty:
SELECTED_PRIMARY: 3, 1, 7
SELECTED_XFW: 11, 12

Rules for these two lines:
- SELECTED_PRIMARY contains ONLY numbers from LAYER 1. Best first.
- SELECTED_XFW contains ONLY numbers from LAYER 2. Each entry must
  directly relate to one of your SELECTED_PRIMARY refs — read the
  [XFW→ ref] tag on the node to confirm. Drop xfw nodes whose linked
  ref isn't in SELECTED_PRIMARY.
- If no Layer 2 nodes were presented, OR none directly support your
  answer, output "SELECTED_XFW:" with nothing after the colon.
- Never put a Layer 1 number in SELECTED_XFW or vice versa.

Selection guidance (applies to SELECTED_PRIMARY) — completeness over brevity:
- Select every primary node materially relevant to the query. Do not impose
  an artificial count cap. The two-list design (PRIMARY for completeness,
  XFW for focused cross-framework support) exists so that primary coverage
  can be exhaustive.
- For "list all X" / "show me our X" / "what are our X" queries (e.g.
  "show me our OFI findings", "what NCs do we have?"), include EVERY
  finding of the requested type in posture data — never truncate. This
  means EVERY node tagged [NC] or [OFI] in LAYER 1, including ISO clauses
  in the N.M format (e.g. 9.2 internal audit, 6.1 risk assessment) — NOT
  just Annex A controls. Clause-level findings count and must be listed.
- For topic-scoped queries (e.g. "access rights gaps", "encryption posture"),
  include all NC/OFI findings whose obligation directly addresses the topic.
  Omit findings unrelated to the topic rather than capping by count.
- Definition queries: keep tight focus — only the node(s) being defined and
  immediate ancestors/children that clarify the definition.

SELECTED_XFW count: 0-3 is typical. Only include xfw nodes that add a
materially different obligation (e.g. GDPR Art.32 added alongside ISO
A.5.18 for an access-control answer). Padding the xfw line with weakly-
related nodes is worse than leaving it empty.

STEP 2 — write your compliance answer.
Rules for your answer:
- Use ONLY the nodes you selected. Never add obligations from your training knowledge.
- Refer to controls by their ref code only: A.8.24, Art.32, 9.2 — never by node number.
- Report posture ONLY from the node data: NC / OFI / Comply / Not yet assessed.
  Never infer or assume compliance status. If a node has no posture tag, do not state one.
- Lead with NC findings, then OFI, then Comply. Never list unassessed controls as gaps.
- Be direct and actionable. State what is missing and what to do.
- END WHEN THE ACTIONABLE CONTENT ENDS. For action-oriented queries
  where cited controls are NC or OFI, a STRUCTURED "starter kit"
  block will render automatically below your answer with per-control
  download buttons + progress-aware lines ("5 of 7 elements still to
  fill in") + cite-mode alternatives. You do NOT need to enumerate
  templates or add a closing paragraph like "To achieve compliance,
  focus on completing the missing artifacts" — that's exactly what
  the block below shows. Stop when the last finding is described.
  Optional single-sentence bridge like "The starter templates below
  cover each of these" is fine; a full closing paragraph is not.
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
- STANDARDS SCOPE — only frameworks listed in the SCOPE block below are
  citable. Frameworks outside this list are NOT implemented by the tenant
  and must NEVER appear in your answer, even as an "indirect" bridge or
  example. If the user asks about a framework that isn't in scope, say
  plainly that it isn't currently in scope and offer to address the
  closest framework that IS in scope.
{scope_block}
- Always use full readable citations: "ISO 27001 A.8.24" not "A.8.24", "GDPR Art. 32" not "Art.32".

GLOSSARY RULE:
Use formal audit terms throughout — NC, OFI, Comply. They match the client's audit records.
When a term appears for the first time in an answer, define it briefly inline:
  NC (Non-Conformity) — a required control or obligation is absent or not effectively implemented
  OFI (Opportunity for Improvement) — a control or obligation exists but has gaps to address
  Comply — the control or obligation is in place with evidence of effectiveness
If the user asks what a term means, explain it fully and show which controls carry that finding.
After defining a term once in an answer, use it without re-defining it.

CONTROLS vs CLAUSES vs ARTICLES — always be precise about the source:
  ISO 27001:2022 has TWO distinct numbering systems — DO NOT mix them:
    1. ANNEX A CONTROLS — refs always start with "A." and use groups 5-8
       only: A.5.x (organizational), A.6.x (people), A.7.x (physical),
       A.8.x (technological). Cite as "ISO 27001 control A.8.24".
    2. BODY CLAUSES (management system requirements) — refs are bare
       N.M format with NO "A." prefix: 4.x context, 5.x leadership,
       6.x planning, 7.x support, 8.x operation, 9.x performance
       evaluation (incl. 9.2 internal audit, 9.3 management review),
       10.x improvement. Cite as "ISO 27001 clause 9.2" — NEVER as
       "A.9.2" or "Annex A 9.2". There is no Annex A group 9 or 10.
    ANTI-PATTERN to avoid: writing "A.9.2", "A.10.1", "A.4.1" — these
       refs are clauses, not Annex A items. The leading "A." is wrong.
    Never call an ISO 27001 item an "article".
  ISO 27701 uses CONTROLS — refer to them as "ISO 27701 A.7.2.4" for controller
    controls in Annex A, or "ISO 27701 B.8.5.6" for processor controls in Annex B.
    ISO 27701 §5.x + §6.x are 27001/27002 mappings — cite as "ISO 27701 clause 5.4.1.3"
    when relevant. Never call an ISO 27701 item an "article".
    ISO 27701 extends ISO 27001 with a Privacy Information Management System (PIMS).
    It is a certifiable standard, and its Annex D maps every 27701 control to
    specific GDPR Articles.
  GDPR uses ARTICLES — refer to them as "GDPR Art. 32" or "GDPR article 32".
    GDPR is EU law, not a certifiable standard.
  NIS2 / DORA / eIDAS use ARTICLES — refer to them as "NIS2 Art.21" etc.

SELECTION ORDER:
1. NC nodes relevant to the query (always include)
2. OFI nodes relevant to the query
3. Nodes whose obligation directly addresses the query
4. Cross-framework nodes that implement the same obligation (GDPR, ISO 27701, NIS2 etc) — include these alongside primary nodes, not as an afterthought
5. Comply nodes with relevant evidence

CROSS-FRAMEWORK RULE: When a query topic has nodes from multiple standards (e.g. ISO 27001 A.5.15 AND GDPR Art.32 both address access control security), select nodes from ALL relevant standards. A complete answer addresses the full regulatory picture.
For Arion Networks: ISO 27001 is the security-controls foundation. ISO 27701 is enrolled as a PIMS certification path, extending 27001 with controller-side (§A.7.x) and processor-side (§B.8.x) privacy controls that map to GDPR Chap V + Art.28 + Art.35 via Annex D. All three are first-class citable frameworks — always include relevant cross-framework nodes when they exist in the node list.

CROSS-FRAMEWORK GUARDRAILS:
- Only cite a GDPR article if it has a direct, material relationship to the query topic. Do not cite GDPR articles merely because they appear in the node list.
- A direct relationship means: the ISO control explicitly implements or supports that GDPR obligation (e.g. A.5.18 access rights → Art.32.1.b confidentiality of processing).
- An indirect or tangential relationship (e.g. Art.5 general principles appearing because of a distant graph traversal) should NOT be cited unless the query explicitly asks about it.
- FOCUS RULE: For document_content and gap_analysis queries, select ISO posture nodes first (NC, OFI), then add GDPR nodes only where the relationship is direct. Do not pad with loosely related nodes from either standard.
- SUPPLIER DRIFT: Do not include supplier controls (A.5.19, A.5.20) in access control evidence answers unless the query explicitly mentions suppliers or third parties.

CRITICAL: A node's posture status comes ONLY from its [NC], [OFI], [Comply], or
[Not yet assessed] tag. If a node has no posture tag, it is unassessed — never
call it NC or OFI based on the obligation text alone.

XFW POSTURE INHERITANCE: Layer 2 nodes never carry a direct [NC]/[OFI]/[Comply]
tag of their own — they carry [Addressed via A.5.x, ...] and a "Posture from
linked primaries" block. To describe a Layer 2 node's posture, summarise the
findings of its linked primaries (e.g. "GDPR Art.32 is addressed via A.5.15
[Comply] and A.5.18 [NC — register incomplete] — the access-register gap is the
residual Art.32 risk to close"). NEVER state that a Layer 2 article is NC, OFI
or Comply by itself — always attribute the finding to the linked primary
control. If [Addressed via ...] is absent, the Layer 2 node is unassessed.

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

# ── Utility: UUID-shape detector ──────────────────────────────────────────────
#
# Adapter over rag.id_types.is_uuid, kept as defence-in-depth on the
# log-writer path (chat_casefile_log requires a UUID-shaped tenant_id
# for the ::uuid cast; anything else silently skips).
from rag.id_types import is_uuid as _is_uuid_shape


# Ship 2'.n (2026-07-16): retired the legacy `rank_and_answer` body
# and its inline `_infer_primary_std`. The layer split (primary/xfw)
# is gone — the digest structures by role per framework-role-model-arc.
# `_pick_primary_std` at file scope was also retired in this arc.


# ── Standard label helpers ────────────────────────────────────────────────────

# ────────────────────────────────────────────────────────────────────────
# Post-compose hallucination guard (L1).
#
# Catches the failure mode where the LLM duplicates a control across NC/OFI
# sections, or fabricates a status the engine never emitted (e.g. listing
# A.5.18 as "NC - All children unassessed" when posture says OFI). The
# truth source is posture_by_ref (built in rank_and_answer); each line in
# the composed answer is parsed for (ref, claimed_status) pairs and dropped
# when the claim contradicts truth.
#
# Scope:
#   - Only inspects refs where we have a definitive finding (NC/OFI/Comply).
#   - Refs the tenant hasn't assessed are left alone (LLM may legitimately
#     reference unassessed controls in xfw narrative).
#   - "Addressed via A.X [NC], A.Y [OFI]" lines validate each ref/status
#     pair independently — the per-ref window stops at the next ref.
#   - The bullet/line containing a contradicted claim is dropped wholesale;
#     numbered-list gaps are tolerated (markdown renderers auto-renumber).
# ────────────────────────────────────────────────────────────────────────
_VERIFIER_REF_RE = re.compile(
    r"\b(?:A\.\d+(?:\.\d+){0,2}|Art\.\d+(?:\.\d+)?|\d+\.\d+(?:\.\d+){0,2})\b"
)
_VERIFIER_STATUS_RE = re.compile(r"\b(NC|OFI|Comply)\b", re.IGNORECASE)
_BULLET_LINE_RE = re.compile(r"^\s*(?:[-*•]|\d+\.)\s")


def _classify_section_header(line: str) -> str | None:
    """
    Returns 'NC' / 'OFI' / 'COMPLY' for posture-section headers, 'RESET'
    for sections that shouldn't inherit status (cross-framework, not yet
    assessed), and None for non-headers. Bullets are explicitly excluded
    even if they contain section keywords.
    """
    s = line.strip()
    if not s or len(s) > 120:
        return None
    if _BULLET_LINE_RE.match(s):
        return None
    if "**" not in s and not s.startswith("#"):
        return None
    plain = re.sub(r"[*#]", "", s).strip().rstrip(":").strip().lower()
    if not plain:
        return None
    if "cross" in plain and "framework" in plain:
        return "RESET"
    if "not yet assessed" in plain or "unassessed" in plain:
        return "RESET"
    if re.search(r"\bnon[- ]?conform", plain) or "(nc)" in plain:
        return "NC"
    if "opportunit" in plain or "(ofi)" in plain:
        return "OFI"
    if re.search(r"\bcompl(y|iant)\b", plain) and "noncompliant" not in plain:
        return "COMPLY"
    return None


def _verify_posture_status_claims(
    answer_text:    str,
    posture_by_ref: dict,
) -> tuple[str, list[str]]:
    """
    Drop lines whose (ref, claimed_status) pair contradicts the posture
    truth in posture_by_ref. Returns (cleaned_text, violations).
    """
    if not answer_text or not posture_by_ref:
        return answer_text, []

    truth: dict[str, str] = {}
    for _ref, _rec in posture_by_ref.items():
        _f = (_rec.get("finding") or "").strip().upper()
        if _f in ("NC", "OFI", "COMPLY"):
            truth[_ref] = "COMPLY" if _f == "COMPLY" else _f

    if not truth:
        return answer_text, []

    violations:      list[str] = []
    out_lines:       list[str] = []
    current_section: str | None = None     # NC / OFI / COMPLY / None

    for line in answer_text.splitlines():
        header = _classify_section_header(line)
        if header is not None:
            current_section = None if header == "RESET" else header
            out_lines.append(line)
            continue

        refs = list(_VERIFIER_REF_RE.finditer(line))
        if not refs:
            out_lines.append(line)
            continue

        bad = False
        for i, ref_m in enumerate(refs):
            ref = ref_m.group(0)
            expected = truth.get(ref)
            if not expected:
                continue
            # Window from this ref to the next ref (or end of line)
            win_start = ref_m.end()
            win_end   = refs[i + 1].start() if i + 1 < len(refs) else len(line)
            window    = line[win_start:win_end]
            sm = _VERIFIER_STATUS_RE.search(window)
            if sm:
                claimed = sm.group(1).upper()
            elif current_section:
                # No inline status; inherit from section header
                claimed = current_section
            else:
                continue
            if claimed != expected:
                violations.append(f"{ref}: claimed={claimed} actual={expected}")
                bad = True
                break

        if not bad:
            out_lines.append(line)

    cleaned = "\n".join(out_lines)
    if violations:
        cleaned = _renumber_numbered_lists(cleaned)
    return cleaned, violations


_NUMBERED_BULLET_RE = re.compile(r"^(\s*)(\d+)\.(\s+)")


def _renumber_numbered_lists(text: str) -> str:
    """
    Rewrite contiguous blocks of `^N. ` bullets to monotonic 1, 2, 3...
    so drops above don't leave a `1. 3. 5.` visual artifact. A block
    breaks on any line that isn't a numbered bullet.
    """
    out: list[str] = []
    counter = 0
    for line in text.splitlines():
        m = _NUMBERED_BULLET_RE.match(line)
        if m:
            counter += 1
            out.append(_NUMBERED_BULLET_RE.sub(
                lambda mm: f"{mm.group(1)}{counter}.{mm.group(3)}", line, count=1,
            ))
        else:
            out.append(line)
            counter = 0
    return "\n".join(out)


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
        # Model defaults come from rag.llm_models (Ship 5'.d config
        # module). Callers can still override per-instance; env vars
        # MODEL_CHAT_ANSWER / MODEL_CHAT_VERIFY / VERIFY_MODEL /
        # LOCAL_LLM_MODEL take precedence in that order.
        answer_model:       str   = None,
        verify_model:       str   = None,
        temperature:        float = 0.1,
        max_tokens:         int   = 1500,
        verify:             bool  = True,     # run verification pass
        max_corrections:    int   = 1,        # max regeneration attempts
    ):
        from rag.llm_models import MODEL_CHAT_ANSWER, MODEL_CHAT_VERIFY
        if answer_model is None: answer_model = MODEL_CHAT_ANSWER
        if verify_model is None: verify_model = MODEL_CHAT_VERIFY
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

        # Skip verify+correct for implementation/guidance queries — they
        # produce long-form advice with many refs that trip the verifier
        # into false-positive "fail" verdicts, and the corrective pass
        # frequently truncates at max_tokens leaving a malformed answer.
        # Verifier is designed for factual posture claims, not guidance.
        _qt = getattr(context, "question_type", None)
        _qt_str = getattr(_qt, "value", str(_qt or "")).lower()
        _skip_verify = _qt_str in {"implementation", "gap_analysis"}

        if self.run_verify and not _skip_verify:
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
        """Build the system prompt for this question type and tenant.

        Layer 2 of the scope filter (2026-07-12): append the tenant's
        scope facts + N/A control list to the prompt. Tells the LLM
        which controls are structurally out-of-scope so it doesn't
        enumerate them in answers regardless of query."""
        standards_str = " + ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
            for s in context.intent.standards_scope
        )
        structure = ANSWER_STRUCTURES.get(
            context.question_type,
            ANSWER_STRUCTURES[QuestionType.UNKNOWN],
        )
        base = SYSTEM_PROMPT.format(
            tenant_name      = context.tenant_name,
            standards        = standards_str,
            answer_structure = structure,
        )
        # Scope block — appended when we have tenant_id in context.
        try:
            from rag.scope_filter import (
                get_tenant_na_scope, get_tenant_scope_facts,
                build_scope_instruction,
            )
            tenant_id = getattr(context, "tenant_id", None)
            if tenant_id:
                import psycopg2, os as _os
                _conn = psycopg2.connect(
                    host    = _os.getenv("PGHOST",    "127.0.0.1"),
                    dbname  = _os.getenv("PGDATABASE","arioncomply_compliance"),
                    user    = _os.getenv("PGUSER",    "arioncomply_app"),
                    password= _os.getenv("PGPASSWORD",""),
                )
                try:
                    na_refs = get_tenant_na_scope(tenant_id, _conn)
                    facts   = get_tenant_scope_facts(tenant_id, _conn)
                    instr   = build_scope_instruction(na_refs, facts)
                    if instr:
                        base = base + "\n\n" + instr
                finally:
                    _conn.close()
        except Exception as _e:
            # Silent fallback — scope block is a safety net, not
            # required for the prompt to function.
            pass
        return base

    def _build_user_message(
        self,
        query:   str,
        context: AssembledContext,
    ) -> str:
        """Build the user message: context block + question."""
        posture_note = ""
        if context.has_posture:
            from rag.id_types import ref_of
            findings = context.posture_summary
            nc_refs  = [ref_of(r) for r, v in findings.items()
                        if v.get("finding") == "NC"]
            ofi_refs = [ref_of(r) for r, v in findings.items()
                        if v.get("finding") == "OFI"]
            comply_refs = [ref_of(r) for r, v in findings.items()
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
            from rag.id_types import ref_of
            controls_in_scope = set()
            for nid in context.node_ids_used:
                controls_in_scope.add(ref_of(nid))
            # Also include posture refs
            for ref in context.posture_summary:
                controls_in_scope.add(ref_of(ref))

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
                from rag.framework_refs import render_framework_refs as _render_framework_refs
                def _ctl(a):
                    return _render_framework_refs(a.get("linked_control_refs")) or a.get("linked_controls") or ""
                alert_lines = []
                for a in show_critical[:5]:
                    alert_lines.append(
                        f"  CRITICAL — {a['document_title']} ({a['external_ref']}) "
                        f"is registered but NOT uploaded. "
                        f"Linked to NC on: {_ctl(a)}"
                    )
                for a in show_warning[:3]:
                    alert_lines.append(
                        f"  WARNING — {a['document_title']} ({a['external_ref']}) "
                        f"is registered but NOT uploaded. "
                        f"Linked to OFI on: {_ctl(a)}"
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

    # ── Compose (prose polish over a verified deterministic answer) ───────────

    _COMPOSE_SYSTEM = (
        "You rewrite a deterministic compliance status report into a brief, "
        "conversational answer for a compliance practitioner. The audience "
        "is an auditor or compliance owner who needs every control reference "
        "the report contains — these refs are the answer's audit trail, not "
        "metadata, and dropping any is a compliance failure.\n"
        "\n"
        "Rules - these are absolute:\n"
        "1. Restate only the facts in the report. Never invent document refs "
        "(DOC###, CD-###-####), control refs (e.g. A.5.18, Art.32), upload "
        "dates, or finding severities.\n"
        "2. PRESERVE EVERY REFERENCE EXACTLY AS WRITTEN. This includes every "
        "DOC###, CD-###-####, ISO clause (A.x.y), and Article (Art.X / Art.32) "
        "that appears in the report. If the report lists 14 control refs, your "
        "rewrite must include all 14. Refs are NEVER optional, NEVER trimmed "
        "for brevity, NEVER summarised as 'multiple controls'.\n"
        "3. If the report ends with an action / instruction line (one that "
        "tells the user to do something), keep that line verbatim at the end "
        "of your rewrite. If the report has no such line, do NOT invent one.\n"
        "4. Keep the prose tight, but never at the cost of dropping a ref. "
        "A specific-doc yes/no answer is 1-2 sentences PLUS its refs. A "
        "list-style answer stays tight in framing but lists every entry.\n"
        "5. Use plain prose. Bullet lists are fine when the report has bullets, "
        "but do not add Markdown headings.\n"
        "6. Do not add caveats, disclaimers, suggestions, or 'next steps' "
        "beyond what the report says.\n"
        "7. Never write a placeholder like '...' or 'TODO' - if a fact is "
        "incomplete in the report, restate it as-is.\n"
        "8. Never apologise. Never say 'as an AI'. Never speculate."
    )

    # Ref shapes the composer must not invent
    _COMPOSE_REF_PATTERN = re.compile(
        r'\b(?:DOC\d{3}|CD-[A-Z]{2,4}-\d{3,4}|'
        r'A\.\d+(?:\.\d+)*|Art\.\d+(?:\(\d+\))?)\b'
    )

    def rank_and_answer(
        self,
        query:             str,
        nodes:             list,
        posture:           dict | None,
        intent,
        tenant_name:       str  = "",
        standards:         str  = "ISO 27001 + GDPR",   # kept for signature compat; unused post-Ship 2'.n
        doc_contexts:      dict | None = None,
        incident_contexts: list | None = None,
        scope_standards:   list[str] | None = None,
        last_entity:       dict | None = None,
        tenant_id:         str  = "",
    ) -> "ComplianceAnswer":
        """
        Case-file rank + answer in a single LLM call.

        Ship 2'.n (2026-07-16): retired the ~900-LOC legacy body and
        the CASEFILE_ENABLED gate. The case-file flow (previously
        `_casefile_flow`) is now the only path — baseline held clean
        across three consecutive full evals (Ship 2'.j / .k / .m at
        207/208) with the flag on. See framework-role-model-arc for
        the model.

        Flow:
          1. Build a CaseFile wrapping the resolver's outputs.
          2. Render (system, user) via build_prompt_pair(cf) — ~2k tokens.
          3. Call LLM with the digest — no rank rubric, direct answer.
          4. Extract PreservationSpec from the CaseFile.
          5. check_and_repair the LLM output — deterministic footers
             for any dropped refs/verdicts/bridges.
          6. Log to chat_casefile_log (schema_v68) — silent-fail.
          7. Return ComplianceAnswer with repaired text.

        Verification / correction passes are SKIPPED — the
        preservation-check IS our verification. Regressions surface
        as repair events + eval-suite drops.

        The `standards` kwarg is a display string kept for signature
        backward-compat with the existing caller in arion_graph.py;
        it's unused in the body (scope_standards carries the actual
        list). Safe to remove in a follow-up cleanup.
        """
        from rag.casefile import CaseFile
        from rag.casefile.digest import (
            build_prompt_pair, build_structured_prompt_pair, approx_tokens,
        )
        from rag.casefile.preservation import extract_preservation_spec
        from rag.casefile.repair import check_and_repair
        from rag.casefile.answer_augment import (
            parse_structured_answer, augment_and_repair,
            structured_to_prose,
        )

        t0 = time.time()

        # ── Build a CaseFile ───────────────────────────────────────────
        # Ship 2'.i (2026-07-16): NO primary/xfw split. Every enrolled
        # standard's obligations are first-class citizens per the
        # framework-role-model-arc. All resolver nodes go into a single
        # pool; the digest structures its layout by role
        # (program/extension/obligation) instead of by layer identity.
        # Bridges become a relationship view, not a node classification.
        _nodes = list(nodes or [])
        _all_nodes = [n for n in _nodes if not getattr(n, "is_informational", False)]

        # Duck-typed resolver-shaped view. CaseFile only reads
        # posture_nodes + graph_nodes.
        # Ship 2'.i: all obligations go into primary_nodes — the
        # legacy split is retired. secondary_nodes / xfw_nodes are
        # kept empty for backward-compat with CaseFile's legacy
        # accessors (they'll be removed when the legacy
        # rank_and_answer path is retired, retire-by 2026-08-15).
        from types import SimpleNamespace
        _graph = SimpleNamespace(
            primary_nodes   = _all_nodes,
            secondary_nodes = [],
            xfw_nodes       = [],
            doc_contexts    = dict(doc_contexts or {}),
            xfw_edges       = [],
        )
        _resolved = SimpleNamespace(
            posture_nodes = dict(posture or {}),
            graph_nodes   = _graph,
        )

        # Duck-typed tenant view — CaseFile only needs .tenant_name +
        # .scope.queryable_standards + .tenant_id.
        # Ship 2'.i: the explicit tenant_id kwarg is the canonical UUID.
        # The tenant_name fallback path handled the pre-Ship-2'.i case
        # where state["tenant_id"] was a display name; that state is
        # now cleaned up, but the shape guard remains as defence-in-depth.
        if tenant_id and _is_uuid_shape(tenant_id):
            _tid = tenant_id
        elif _is_uuid_shape(tenant_name):
            _tid = tenant_name       # legacy path — pre-2'.i callers
        else:
            _tid = ""
        _tenant = SimpleNamespace(
            tenant_name = tenant_name or "",
            tenant_id   = _tid,
            scope       = SimpleNamespace(
                queryable_standards = list(scope_standards or []),
            ),
        )

        cf = CaseFile(
            query        = query,
            intent       = intent,
            resolved     = _resolved,
            session      = None,      # session ships in a later Ship 2' phase
            tenant       = _tenant,
            last_entity  = last_entity,
            incidents    = list(incident_contexts or []),
        )

        # Ship 14'.e — populate cf.risks when the classifier routes to
        # POSTURE_RISK. Fail-loud discipline (Ship 2'.n): the fetch
        # helper is defensive internally but we don't swallow
        # unexpected exceptions here. Only fires on posture_risk to
        # avoid a per-turn DB hit on other queries.
        if cf.question_type == "posture_risk" and _tid:
            from rag.risk.queries import fetch_risks_for_casefile
            cf.risks = fetch_risks_for_casefile(_tid, top_n=8)

        # Ship 60'.j — precompute bridge-coverage counts per xfw
        # obligation ref so the digest's XFW BRIDGES section can
        # append "(N/M MUSTs bridge-covered)" without a re-query in
        # the rendering path. Scope bounded to refs that already
        # appear in cf.xfw_bridges() — no per-obligation SSoT scan
        # beyond what the digest already surfaces. Best-effort; any
        # failure leaves bridge_counts empty and the section renders
        # unchanged.
        if _tid:
            try:
                _bridge_refs = list(cf.xfw_bridges().keys())
            except Exception:
                _bridge_refs = []
            if _bridge_refs:
                try:
                    import os as _os_bc, psycopg2 as _pg_bc
                    _bc_conn = _pg_bc.connect(
                        host     = _os_bc.getenv("PGHOST",     "127.0.0.1"),
                        dbname   = _os_bc.getenv("PGDATABASE", "arioncomply_compliance"),
                        user     = _os_bc.getenv("PGUSER",     "arioncomply_app"),
                        password = _os_bc.getenv("PGPASSWORD", ""),
                    )
                    try:
                        with _bc_conn.cursor() as _bc_cur:
                            _bc_cur.execute(
                                "SELECT set_config('app.tenant_id', %s, TRUE)",
                                (_tid,),
                            )
                            # One aggregated query per section (up to ~5
                            # refs typically). n_total = distinct MUSTs
                            # for the ref in SSoT; n_bridged = distinct
                            # target_must_ids in bridge_coverage for
                            # unmet MUSTs. Using two aggregates so a
                            # ref with no direct rows still shows a
                            # count for its stub coverage.
                            _bc_cur.execute("""
                                SELECT control_ref,
                                       COUNT(*)                       AS n_total,
                                       COUNT(*) FILTER (WHERE satisfied) AS n_satisfied
                                  FROM posture_must_verdicts
                                 WHERE tenant_id = %s::uuid
                                   AND control_ref = ANY(%s)
                                 GROUP BY control_ref
                            """, (_tid, _bridge_refs))
                            _totals = {r[0]: (int(r[1]), int(r[2]))
                                       for r in _bc_cur.fetchall()}
                            _bc_cur.execute("""
                                SELECT target_control_ref,
                                       COUNT(DISTINCT target_must_id) AS n_targets_bridged
                                  FROM posture_must_bridge_coverage
                                 WHERE tenant_id = %s::uuid
                                   AND target_control_ref = ANY(%s)
                                 GROUP BY target_control_ref
                            """, (_tid, _bridge_refs))
                            _brg_targets = {r[0]: int(r[1])
                                            for r in _bc_cur.fetchall()}
                        cf.bridge_counts = {}
                        for _ref in _bridge_refs:
                            n_total, n_sat = _totals.get(_ref, (0, 0))
                            n_brg_targets  = _brg_targets.get(_ref, 0)
                            if not n_total:
                                continue
                            # "Bridge-covered" = unmet-direct MUSTs
                            # that have at least one bridge attribution
                            # row (cap by n_total - n_satisfied so an
                            # over-counted target set can't exceed the
                            # unmet population).
                            n_bridged_unmet = min(
                                n_brg_targets, n_total - n_sat,
                            )
                            cf.bridge_counts[_ref] = (n_bridged_unmet, n_total)
                        logging.getLogger("rag.llm_answer").info(
                            "bridge_counts: %d refs populated (of %d xfw refs)",
                            len(cf.bridge_counts), len(_bridge_refs),
                        )
                    finally:
                        _bc_conn.close()
                except Exception as _bc_e:
                    logging.getLogger("rag.llm_answer").warning(
                        "bridge_counts precompute skipped: %s", _bc_e,
                    )

        # ── Render digest ─────────────────────────────────────────────
        # Ship 18'.b: attempt the structured (JSON) path first; fall
        # back to prose on any parse failure. Both paths share the same
        # digest — only the system prompt differs.
        t_dig = time.time()
        system_prompt, user_digest = build_structured_prompt_pair(cf)
        digest_ms = int((time.time() - t_dig) * 1000)

        sys_tokens  = approx_tokens(system_prompt)
        user_tokens = approx_tokens(user_digest)

        # ── LLM call (structured) ─────────────────────────────────────
        raw = self._call_llm(
            system          = system_prompt,
            user            = user_digest,
            model           = self.answer_model,
            max_tokens      = self.max_tokens,
            step            = "rank_answer",
            response_format = {"type": "json_object"},
        )

        # ── Try structured parse ──────────────────────────────────────
        structured_payload: dict | None = None
        structured_events: list[dict]   = []
        spec = extract_preservation_spec(cf)
        structured = parse_structured_answer(raw)

        if structured is not None:
            # Deterministic augmentation — build related cards + repair
            # missing required_refs via card insertion (APPEND-ONLY).
            # Open a short-lived pg connection for advisory data
            # (evidence_summary / still_needed). Best-effort — augment
            # runs with pg_conn=None on connect failure.
            _aug_conn = None
            try:
                import os as _os, psycopg2 as _pg2
                _aug_conn = _pg2.connect(
                    host     = _os.getenv("PGHOST",     "127.0.0.1"),
                    dbname   = _os.getenv("PGDATABASE", "arioncomply_compliance"),
                    user     = _os.getenv("PGUSER",     "arioncomply_app"),
                    password = _os.getenv("PGPASSWORD", ""),
                )
                if _tid:
                    with _aug_conn.cursor() as _cur:
                        _cur.execute(
                            "SELECT set_config('app.tenant_id', %s, TRUE)",
                            (_tid,),
                        )
            except Exception as _ce:
                logging.getLogger("rag.llm_answer").debug(
                    "augment pg connect failed (evidence detail skipped): %s", _ce,
                )
                _aug_conn = None

            try:
                structured, structured_events = augment_and_repair(
                    structured,
                    cf,
                    spec,
                    pg_conn   = _aug_conn,
                    tenant_id = _tid,
                )
                structured_payload = structured.model_dump()
            finally:
                if _aug_conn is not None:
                    try: _aug_conn.close()
                    except Exception: pass

            # Compose a prose answer_text from the structured payload
            # for backward compat + preservation-check parity.
            # Ship 21'.b: use structured_to_prose which emits clean
            # markdown (## action headings + related-controls section)
            # instead of the old `title: body` inline format. Related
            # section carries what the retired ↳ Compliance facts:
            # footer used to render.
            answer_text = self._normalize_clause_refs(
                structured_to_prose(structured)
            )
        else:
            # Fail-open: LLM emitted malformed JSON. Log to
            # repair_events and use the raw text as prose.
            structured_events.append({
                "kind":   "structured_parse_failed",
                "ref":    None,
                "detail": "LLM output not parseable as StructuredAnswer JSON — "
                          "falling back to prose path",
            })
            answer_text = self._normalize_clause_refs(raw)

        # ── Preservation check + repair (prose path) ──────────────────
        t_rep = time.time()
        repair_result = check_and_repair(answer_text, spec, cf)
        answer_text = repair_result.text
        # Merge in structured-path events so the log captures both.
        if structured_events:
            from rag.casefile.repair import RepairEvent as _RE
            for ev in structured_events:
                repair_result.events.append(_RE(
                    kind   = ev.get("kind", "structured"),
                    ref    = ev.get("ref"),
                    detail = ev.get("detail", ""),
                ))
        repair_ms = int((time.time() - t_rep) * 1000)

        # ── Log to chat_casefile_log (silent-fail) ────────────────────
        try:
            self._log_casefile_turn(
                cf                    = cf,
                system_prompt_tokens  = sys_tokens,
                user_digest_tokens    = user_tokens,
                repair_result         = repair_result,
                answer_text           = answer_text,
                digest_latency_ms     = digest_ms,
                repair_latency_ms     = repair_ms,
                total_latency_ms      = int((time.time() - t0) * 1000),
                casefile_enabled      = True,
                shadow_mode           = False,
            )
        except Exception as _le:
            logging.getLogger("rag.llm_answer").debug(
                "casefile log write skipped: %s", _le,
            )

        # ── Build ComplianceAnswer ───────────────────────────────────
        cited_refs = self._extract_refs(answer_text)

        # posture_findings shape: {ref → finding} for whatever the
        # answer cited that we have posture on.
        posture_by_ref = cf.posture_by_ref()
        posture_findings = {
            r: posture_by_ref[r].get("finding", "")
            for r in cited_refs
            if r in posture_by_ref
        }
        # Response envelope's primary_refs / xfw_refs fields — legacy
        # bookkeeping for downstream UI consumers that still expect the
        # split. Ship 2'.i: with no layer split, we classify by role:
        # program+extension nodes → primary_refs; obligation nodes →
        # xfw_refs (auditor navigation direction). Retire this split
        # once downstream consumers no longer need the shape.
        _role_by_ref: dict[str, str | None] = {}
        for n in _all_nodes:
            _role_by_ref[n.ref] = cf.role_of(n.ref)
        primary_refs = [
            r for r in cited_refs
            if _role_by_ref.get(r) in ("program", "extension")
        ]
        xfw_refs = [
            r for r in cited_refs
            if _role_by_ref.get(r) == "obligation"
        ]

        latency_ms = int((time.time() - t0) * 1000)
        return ComplianceAnswer(
            answer_text       = answer_text,
            question_type     = intent.question_type if intent else None,
            tenant_name       = tenant_name,
            cited_refs        = cited_refs,
            posture_findings  = posture_findings,
            verification      = None,
            verified          = True,       # preservation check IS verification
            model_used        = self.answer_model,
            latency_ms        = latency_ms,
            was_corrected     = repair_result.repaired,
            primary_refs      = primary_refs,
            xfw_refs          = xfw_refs,
            answer_structured = structured_payload,
        )

    def _log_casefile_turn(
        self,
        cf,
        system_prompt_tokens: int,
        user_digest_tokens:   int,
        repair_result,
        digest_latency_ms:    int,
        repair_latency_ms:    int,
        total_latency_ms:     int,
        casefile_enabled:     bool,
        shadow_mode:          bool,
        answer_text:          str | None = None,
    ) -> None:
        """Write one row to chat_casefile_log — best-effort, silent-fail.

        Uses a fresh connection so the log write doesn't sit in the
        session's psycopg2 pool (Ship 1 consensus_log pattern).
        """
        import psycopg2, os as _os
        tenant_id = cf.tenant_id
        if not tenant_id:
            return  # nothing to log against
        # Defence-in-depth: post-Ship-2'.i, cf.tenant_id is always
        # UUID-shaped (validated via TenantUUID at state construction).
        # This guard catches any caller path that bypassed the state
        # machinery and handed us a slug or display name directly —
        # log-writes cast to ::uuid, and a silent InvalidTextRepresentation
        # is exactly the failure mode Ship 2'.i was built to prevent.
        if not _is_uuid_shape(tenant_id):
            import logging as _lg
            _lg.getLogger("rag.llm_answer").warning(
                "casefile_log skipped: tenant_id %r is not UUID-shaped "
                "(state should have validated this — investigate caller)",
                tenant_id,
            )
            return
        try:
            conn = psycopg2.connect(
                host     = _os.getenv("PGHOST",     "127.0.0.1"),
                dbname   = _os.getenv("PGDATABASE", "arioncomply_compliance"),
                user     = _os.getenv("PGUSER",     "arioncomply_app"),
                password = _os.getenv("PGPASSWORD", ""),
            )
        except Exception as _ce:
            # Ship 2'.k: fail-loud on the connect step. Silent-fail here
            # was masking config errors that would otherwise be caught
            # in dev. Best-effort principle preserved (we return), but
            # the failure surfaces in the log at WARNING.
            import logging as _lg
            _lg.getLogger("rag.llm_answer").warning(
                "casefile_log connect failed (best-effort skip): %s", _ce,
            )
            return
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT set_config('app.tenant_id', %s, FALSE)",
                    (tenant_id,),
                )
            from rag.casefile.log import log_casefile
            log_casefile(
                pg_conn              = conn,
                tenant_id            = tenant_id,
                case_file            = cf,
                system_prompt_tokens = system_prompt_tokens,
                user_digest_tokens   = user_digest_tokens,
                repair_result        = repair_result,
                answer_text          = answer_text,
                digest_latency_ms    = digest_latency_ms,
                repair_latency_ms    = repair_latency_ms,
                total_latency_ms     = total_latency_ms,
                casefile_enabled     = casefile_enabled,
                shadow_mode          = shadow_mode,
            )
        finally:
            try: conn.close()
            except Exception: pass

    def compose(
        self,
        query:                str,
        deterministic_text:   str,
        *,
        required_refs:        list[str] | None = None,
        action_hint:          str | None       = None,
        model:                str | None       = None,
        max_tokens:           int              = 400,
    ) -> str:
        """
        Polish a verified deterministic answer into conversational prose.

        The deterministic text is the source of truth: we send it to the
        small/fast model as a fact sheet and ask for a tight rewrite. The
        rewrite is validated three ways before being returned:
          1. Every entry in `required_refs` survived verbatim
          2. The action_hint (if given) survived or is re-attached
          3. No NEW refs appeared (no DOC###, CD-###, A.x.y or Art.X that
             wasn't already in the deterministic input)

        On any failure (LLM error, empty output, missing required refs,
        invented refs) we return `deterministic_text` unchanged — never
        silently regress.

        Args:
            query:              the user's original question
            deterministic_text: the verified answer to polish
            required_refs:      refs that MUST appear verbatim in the output
                                (e.g. ["DOC006", "A.5.18"]); empty list to
                                skip required-ref enforcement
            action_hint:        a single line (e.g. "Upload: python3 …")
                                re-attached if the rewrite drops it
            model:              override model (default: verify_model)
            max_tokens:         cap on rewrite size

        Returns:
            Prose rewrite on success; `deterministic_text` on any failure.
        """
        if not deterministic_text:
            return deterministic_text

        required_refs = [r for r in (required_refs or []) if r]

        # Snapshot every ref shape in the deterministic input — the composer
        # is not allowed to introduce a ref that's not in this set.
        allowed_refs = set(self._COMPOSE_REF_PATTERN.findall(deterministic_text))

        user_message = (
            f"User question:\n{query.strip()}\n\n"
            f"Deterministic status report (the truth — restate only this):\n"
            f"\"\"\"\n{deterministic_text.strip()}\n\"\"\"\n\n"
            f"Rewrite the report as a brief conversational answer to the "
            f"user's question. Preserve every document and control reference "
            f"exactly as written. Do NOT mention any document or control "
            f"reference that does not appear in the report above. If the "
            f"report says '37 additional doc(s)' or similar summary, keep "
            f"that summary as-is — do not expand it by listing extra docs."
        )

        try:
            composed = self._call_llm(
                system     = self._COMPOSE_SYSTEM,
                user       = user_message,
                model      = model or self.verify_model,
                max_tokens = max_tokens,
                step       = "compose",
            )
        except Exception:
            return deterministic_text

        composed = (composed or "").strip()
        if not composed:
            return deterministic_text

        # 1. Required refs must survive
        for ref in required_refs:
            if ref not in composed:
                return deterministic_text

        # 2. No invented refs — every ref in the rewrite must have been in
        # the deterministic input
        seen_refs = set(self._COMPOSE_REF_PATTERN.findall(composed))
        invented  = seen_refs - allowed_refs
        if invented:
            return deterministic_text

        # 3. No invented action / instruction lines — the LLM sometimes
        # volunteers "Upload: …" or similar placeholders. Any "Upload:" /
        # tool reference in the rewrite must have been in the input.
        determ_lower = deterministic_text.lower()
        for line in composed.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            looks_like_action = (
                stripped.lower().startswith("upload:") or
                "tools/doc_uploader.py" in stripped.lower() or
                stripped.endswith("…") or
                stripped.endswith("...")
            )
            if looks_like_action and stripped.lower() not in determ_lower:
                return deterministic_text

        # 4. Re-attach action hint if dropped
        if action_hint and action_hint not in composed:
            composed = composed.rstrip() + "\n\n" + action_hint

        return composed

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
                f"\n{ctx.control_ref}: {ctx.title}"
            )
            checklist_lines.append(f"Type: {(ctx.evidence_type or '').replace('_', ' ')}")
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
        primary_nums: set[int] | None = None,
        xfw_nums:     set[int] | None = None,
    ) -> tuple[list[int], list[int], str]:
        """
        Parse SELECTED_PRIMARY: and SELECTED_XFW: lines (and the answer)
        from rank_and_answer output.

        Returns (selected_primary, selected_xfw, answer_text).

        primary_nums / xfw_nums (when provided) are the valid node-number
        sets for each layer. Used to police misrouted selections — e.g. if
        the LLM puts a Layer 2 number in SELECTED_PRIMARY, we move it.
        Without them, parser trusts the LLM's grouping.

        Fallback chain:
          1. SELECTED_PRIMARY: / SELECTED_XFW: — preferred two-line format
          2. Legacy SELECTED: — treated as all-primary
          3. Neither — every node is selected as primary (preserves the
             pre-layered behavior so the pipeline never blocks on a parse)
        """
        primary  : list[int] = []
        xfw      : list[int] = []
        answer   : str       = raw.strip()
        consumed : list[tuple[int, int]] = []  # (start, end) of lines to strip

        def _parse_ints(s: str, valid: set[int] | None) -> list[int]:
            out: list[int] = []
            for part in s.split(","):
                part = part.strip()
                if part.isdigit():
                    n = int(part)
                    if n in num_to_node and (valid is None or n in valid):
                        out.append(n)
            return out

        # Preferred format
        m_primary = re.search(
            r"SELECTED[_\s]PRIMARY\s*:\s*([\d,\s]*)", raw, re.IGNORECASE
        )
        m_xfw = re.search(
            r"SELECTED[_\s]XFW\s*:\s*([\d,\s]*)", raw, re.IGNORECASE
        )
        if m_primary:
            primary = _parse_ints(m_primary.group(1), primary_nums)
            consumed.append((m_primary.start(), m_primary.end()))
        if m_xfw:
            xfw = _parse_ints(m_xfw.group(1), xfw_nums)
            consumed.append((m_xfw.start(), m_xfw.end()))

        # Legacy fallback — only if neither preferred line was present
        if not m_primary and not m_xfw:
            m_legacy = re.search(r"SELECTED\s*:\s*([\d,\s]+)", raw, re.IGNORECASE)
            if m_legacy:
                # Treat legacy SELECTED as primary; route any Layer 2 numbers
                # to xfw if we know the layer membership.
                all_nums = _parse_ints(m_legacy.group(1), None)
                if xfw_nums is not None:
                    primary = [n for n in all_nums if n not in xfw_nums]
                    xfw     = [n for n in all_nums if n in xfw_nums]
                else:
                    primary = all_nums
                consumed.append((m_legacy.start(), m_legacy.end()))

        # Strip the consumed SELECTED lines (and any leading whitespace
        # they leave behind) from the answer text. Strip back-to-front so
        # earlier offsets stay valid.
        if consumed:
            answer = raw
            for start, end in sorted(consumed, key=lambda t: t[0], reverse=True):
                answer = answer[:start] + answer[end:]
            answer = answer.strip()
            # Strip a label-only first line (e.g. "**COMPLIANCE ANSWER:**")
            answer = re.sub(
                r"^(?:\*{0,2}(?:COMPLIANCE\s+ANSWER|ANSWER|PART\s*\d|STEP\s*\d)\*{0,2}[:\s—-]*\n+)",
                "", answer, flags=re.IGNORECASE
            ).strip()

        # Last-resort fallback — preserve historical "use everything" behavior
        if not primary and not xfw:
            if primary_nums is not None:
                primary = [n for n in num_to_node if n in primary_nums]
                xfw     = [n for n in num_to_node if xfw_nums and n in xfw_nums]
            else:
                primary = list(num_to_node.keys())

        return primary, xfw, answer

    def _call_llm(
        self,
        system:     str,
        user:       str,
        model:      str,
        max_tokens: int = 1500,
        step:       str = "answer",
        response_format: Optional[dict] = None,
    ) -> str:
        """Single LLM call via the provider-neutral client."""
        from rag.llm_client import call as llm_call
        # 180s — implementation/audit-prep answers can legitimately
        # run 40-60s of token generation on gpt-4o-mini. Default 60s
        # is too tight (case #21 caught this).
        response = llm_call(
            system      = system,
            user        = user,
            model       = model,
            purpose     = "chat" if step in ("answer","compose") else (step or "chat"),
            max_tokens  = max_tokens,
            temperature = self.temperature,
            timeout_s   = 180.0,
            metadata    = {"step": step},
            response_format = response_format,
        )
        if not response.ok:
            raise RuntimeError(f"LLM call failed ({model}): {response.error}")
        result = response.text.strip()
        logger = get_logger()
        if logger:
            logger.log_call(
                step       = step,
                model      = model,
                system     = system[:300],
                user       = user[:800],
                response   = result,
                latency_ms = response.latency_ms,
            )
        return result

    def _verify(
        self,
        context_text:  str,
        answer_text:   str,
        posture:       dict | None = None,
        question_type: str | None  = None,  # e.g. "definition", "gap_analysis"
    ) -> VerificationResult:
        """Run verification pass using verify_model."""
        t0 = time.time()

        # Build posture preamble so verifier knows findings are factual inputs
        posture_preamble = ""
        if posture:
            from rag.id_types import ref_of
            lines = ["FACTUAL POSTURE FINDINGS (these are pre-assessed facts, "
                     "not claims to verify against legal text):"]
            for node_id, rec in posture.items():
                ref     = ref_of(node_id)
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
        from rag.llm_client import call as llm_call
        response = llm_call(
            system      = VERIFICATION_PROMPT,
            user        = prompt,
            model       = self.verify_model,
            purpose     = "chat",
            max_tokens  = 400,
            temperature = 0.0,
            metadata    = {"step": "verify", "question_type": question_type},
        )
        if response.ok:
            raw    = response.text.strip()
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
                        latency_ms  = response.latency_ms,
                        model       = self.verify_model,
                    )
                return result

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
        from rag.llm_client import call as llm_call
        response = llm_call(
            system      = system,
            user        = "",  # overridden by messages
            model       = self.answer_model,
            purpose     = "chat",
            max_tokens  = self.max_tokens,
            temperature = self.temperature,
            metadata    = {"step": "correct"},
            messages    = [
                {"role": "system",    "content": system},
                {"role": "user",      "content": self._build_user_message(query, context)},
                {"role": "assistant", "content": original},
                {"role": "user",      "content": correction_prompt},
            ],
        )
        if not response.ok:
            return original, False, f"Correction failed: {response.error}"

        corrected = response.text.strip()
        # Strip any preamble the model adds despite instructions
        corrected = self._strip_correction_preamble(corrected)

        note = f"Corrected after verification: {'; '.join(issues[:2])}"
        return corrected, True, note

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

    # ISO 27001 body clauses (groups 4-10) have no "A." prefix.
    # The LLM occasionally hallucinates "A.9.2", "A.10.1", etc.
    # Strip the erroneous "A." before these clause groups programmatically.
    _SPURIOUS_ANNEX_RE = re.compile(r'\bA\.((?:4|9|10)\.\d+)\b')

    def _normalize_clause_refs(self, text: str) -> str:
        return self._SPURIOUS_ANNEX_RE.sub(r'\1', text)

    def _extract_refs(self, text: str) -> list[str]:
        """Extract article and control references from answer text."""
        # GDPR: Art.32, Art.32.1, Art.32.1.a
        gdpr      = re.findall(r'\bArt\.\d+(?:\.\d+)*(?:\.[a-z])?\b', text)
        # ISO Annex A: A.5.15 (27001), A.7.2.5 (27701 3-part), B.8.5.6 (27701 processor)
        iso_annex = re.findall(r'\b[AB]\.\d+(?:\.\d+){1,2}\b', text)
        # ISO Management clauses: 6.1.2, 5.1
        # Exclude numbers that are substrings of already-matched refs
        iso_mgmt  = re.findall(
            r'(?<!Art\.)(?<![AB]\.)\b\d+\.\d+(?:\.\d+)?\b', text
        )

        # Build set of numeric suffixes already claimed
        claimed = set()
        for ref in gdpr:
            m = re.match(r'Art\.(\d+(?:\.\d+)*)', ref)
            if m:
                claimed.add(m.group(1))
        for ref in iso_annex:
            m = re.match(r'[AB]\.(\d+(?:\.\d+){1,2})', ref)
            if m:
                claimed.add(m.group(1))

        # Filter iso_mgmt matches that are trailing substrings of any
        # already-claimed ref (e.g. "2.5" appearing inside "A.7.2.5" —
        # the lookbehind guard can't cover multi-char prefixes without
        # variable-length lookbehind, so substring-check post-facto).
        def _is_substring_of_claim(candidate: str) -> bool:
            for c in claimed:
                if c == candidate:
                    return True
                # trailing substring, dot-bounded (e.g. "2.5" in "7.2.5")
                if c.endswith("." + candidate):
                    return True
            return False
        iso_mgmt = [r for r in iso_mgmt if not _is_substring_of_claim(r)]

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

