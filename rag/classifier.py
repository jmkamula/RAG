"""
QueryClassifier — ArionComply RAG Orchestration

Handles the full conversation flow from session intake through
to a resolved QueryIntent ready for retrieval.

Three-state design:
  CLEAR      → intent unambiguous, proceed to retrieval
  AMBIGUOUS  → multiple plausible clusters, LLM writes clarification
  NO_MATCH   → no confident results, LLM writes redirect question

LLM usage:
  Classification  → gpt-4o-mini  (structured JSON, cheap)
  Clarification   → gpt-4o-mini  (natural language writing, cheap)
  No LLM needed for CLEAR explicit-ref queries (pattern match)

All LLM calls use OpenAI (OPENAI_API_KEY).
"""
from __future__ import annotations

import re
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ── Enums ──────────────────────────────────────────────────────────────────────

class QuestionType(Enum):
    DEFINITION         = "definition"           # what does X mean / say
    IMPLEMENTATION     = "implementation"       # how do I implement X
    GAP_ANALYSIS       = "gap_analysis"         # what are my gaps for X
    POSTURE_CHECK      = "posture_check"        # am I compliant with X
    CROSS_FRAMEWORK    = "cross_framework"      # how does X relate to Y
    FREE_ASSESSMENT    = "free_assessment"      # broad overview / where do I stand
    DOCUMENT_INVENTORY = "document_inventory"   # what documents do we need?
    DOCUMENT_CONTENT   = "document_content"     # what must a document contain?
    UNKNOWN            = "unknown"              # could not classify

class IntakeState(Enum):
    CLEAR     = "clear"      # proceed to retrieval
    AMBIGUOUS = "ambiguous"  # ask clarification
    NO_MATCH  = "no_match"   # nothing found, redirect
    EXPLICIT  = "explicit"   # explicit ref/action detected, skip intake

# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class TenantProfile:
    tenant_id:            str
    name:                 str
    applicable_standards: list[str]  # ["ISO27001:2022", "GDPR:2016/679"]
    role:                 list[str]  # ["controller", "processor"]
    sector:               str        # "technology", "healthcare", etc.
    jurisdiction:         list[str]  # ["EU", "UK"]
    has_posture_data:     bool = False
    posture_summary:      dict  = field(default_factory=dict)
    facts:                object = None   # ClientFacts instance — drives obligation implication
    posture_data:         dict  = field(default_factory=dict)   # full posture for clarifier context
    document_alerts:      list  = field(default_factory=list)   # missing doc alerts for clarifier


@dataclass
class SessionContext:
    """Established at conversation start. Persists for session lifetime."""
    tenant_profile:   TenantProfile
    standards:        list[str]           # resolved from intake
    role:             str | None          # "controller" / "processor" / "both"
    intent_type:      QuestionType | None # broad intent from intake
    active_refs:      list[str]           # most recently discussed refs
    active_cluster:   str | None          # current topic cluster label
    # Vocabulary the user has used (builds during session)
    user_vocabulary:  list[str] = field(default_factory=list)

    def update_refs(self, refs: list[str]) -> None:
        """Update active refs after each query — keep last 5."""
        for r in refs:
            if r not in self.active_refs:
                self.active_refs.insert(0, r)
        self.active_refs = self.active_refs[:5]


@dataclass
class QueryIntent:
    """Fully resolved intent for a single query."""
    question_type:    QuestionType
    standards_scope:  list[str]
    role_filter:      str | None
    needs_posture:    bool
    cited_refs:       list[str]       # explicit refs in the query
    resolved_refs:    list[str]       # cited + inherited from session
    confidence:       float
    raw_query:        str
    # Query dimensions — what layers to fetch
    dimensions:         "QueryDimensions" = field(
                            default_factory=lambda: QueryDimensions())
    # Detected runtime events e.g. "personal_data_breach", "dsar"
    detected_events:    list[str] = field(default_factory=list)
    # Document topic when question_type is DOCUMENT_INVENTORY/CONTENT
    document_topic_ref: str | None = None   # e.g. "A.8.24" for "encryption policy"
    # Set if confidence below threshold
    clarification_question: str | None = None
    clarification_options:  list[str] = field(default_factory=list)


@dataclass
class QueryDimensions:
    """
    Three orthogonal dimensions of a compliance query.
    A query can activate any combination simultaneously.

    needs_obligation:    fetch control obligation text + guidance
                         always True for compliance queries
    needs_posture:       fetch tenant posture findings for context
                         True when query references OUR status
    needs_documentation: fetch DocumentRequirement + ChecklistItems
                         True when query references documents/evidence

    Examples:
      "what does Art.32 require?"
        → obligation=True, posture=False, documentation=False

      "what are our encryption gaps?"
        → obligation=True, posture=True, documentation=False

      "what must our encryption policy contain?"
        → obligation=True, posture=False, documentation=True

      "what is our encryption obligation and required documentation?"
        → obligation=True, posture=True, documentation=True
    """
    needs_obligation:    bool = True    # almost always True
    needs_posture:       bool = False
    needs_documentation: bool = False


@dataclass
class ClusterSummary:
    """One candidate topic cluster from vector search."""
    label:         str           # human-readable cluster name
    standard:      str           # "GDPR:2016/679" or "ISO27001:2022"
    top_refs:      list[str]     # top 3 node refs in this cluster
    avg_score:     float
    description:   str           # from business_description of top node
    chapter:       str


@dataclass
class IntakeResult:
    """Result of processing the initial 'what are you working on' response."""
    state:           IntakeState
    session:         SessionContext | None       # set if CLEAR or EXPLICIT
    clarification:   str | None                  # set if AMBIGUOUS or NO_MATCH
    clusters:        list[ClusterSummary]        # candidate clusters found
    raw_input:       str
    # Maps option letter → taxonomy type_id for clarification responses
    # e.g. {"a": "REMEDIATION_GUIDE", "b": "DOCUMENT_CONTENT", "c": "POSTURE_STATUS"}
    # Set when state=AMBIGUOUS so process_clarification resolves directly
    taxonomy_options_map: dict = None


# ── Prompts ────────────────────────────────────────────────────────────────────

CLARIFICATION_WRITER_PROMPT = """You are a compliance advisor at {tenant_name}.

A user asked: "{user_input}"

What the system knows about the client right now:
{client_context}

The query could relate to multiple compliance intents. Your job is to clarify
WHAT THE USER WANTS TO DO — not which topic they mean. The topic is likely clear;
the intent (the type of answer they need) is what's ambiguous.

Taxonomy options to present (pick 2-3 most relevant):
{taxonomy_options}

Guidelines:
- Lead with any specific client fact that's directly relevant (document not uploaded,
  open finding, etc.) — this shows the system knows their situation
- Frame each option as a concrete action the user might want to take
- Each option should map to exactly one taxonomy type shown in [brackets]
- Use plain business language — no ISO clause numbers in the question itself
- Maximum 5 lines total
- Format: one opening sentence + lettered options (a), (b), (c)

Return ONLY the clarification question text. Do not explain your reasoning."""


NO_MATCH_WRITER_PROMPT = """You are a compliance advisor at {tenant_name}.

A user described what they are working on: "{user_input}"

You searched the compliance knowledge base covering {standards} and could not
find a strong match for what they described.

Write a short, natural response that:
- Acknowledges what they said without being dismissive
- Briefly explains what the system covers
- Asks one specific question to help redirect to something useful
- Does not apologise excessively

Maximum 3 sentences. Tone: helpful colleague."""


# ── Document query phrase detection ───────────────────────────────────────────

DOCUMENTATION_PHRASES: list[str] = [
    "document", "policy", "procedure", "evidence",
    "what do we need to have", "required documentation",
    "what should our", "what must", "checklist",
    "what goes in", "prove compliance", "audit evidence",
    "what policies", "what procedures", "documentation requirements",
    "mandatory documents", "required documents", "what documents",
    "document checklist", "documents we need",
    "what should be in", "what items", "what sections",
    "policy template", "policy contain", "procedure contain",
    "dpa contain", "contract contain",
]

DOCUMENT_INVENTORY_PHRASES: list[str] = [
    "mandatory documents", "required documents", "what documents do we need",
    "document checklist", "documents we need", "what policies do we need",
    "what procedures do we need", "documentation requirements",
    "what do we need to have in place",
]

DOCUMENT_CONTENT_PHRASES: list[str] = [
    "what should our policy include", "what must a",
    "what should be in our", "what goes in", "policy template",
    "what must our", "what should our procedure", "what items",
    "what sections", "checklist for", "policy contain", "must contain",
]

# Topic → control_ref map for document queries
# "what documents do we need for encryption?" → A.8.24
DOCUMENT_TOPIC_MAP: dict[str, str] = {
    "cryptography":        "A.8.24",
    "encryption":          "A.8.24",
    "data masking":        "A.8.11",
    "masking":             "A.8.11",
    "incident":            "A.5.24",
    "incident response":   "A.5.24",
    "breach":              "Art.33",
    "data breach":         "Art.33",
    "cloud":               "A.5.23",
    "cloud services":      "A.5.23",
    "cloud storage":       "A.5.23",
    "processor":           "Art.28",
    "dpa":                 "Art.28",
    "data processing":     "Art.28",
    "privacy notice":      "Art.13",
    "privacy policy":      "Art.13",
    "access rights":       "A.5.18",
    "access control":      "A.5.15",
    "risk assessment":     "6.1.2",
    "risk":                "6.1.2",
    "remote working":      "A.6.7",
    "remote work":         "A.6.7",
    "software development":"A.8.25",
    "secure development":  "A.8.25",
    "internal audit":      "9.2",
    "audit":               "9.2",
    "management review":   "9.3",
    "isms policy":         "5.2",
    "information security policy": "5.2",
    "isms scope":          "4.3",
    "dsar":                "Art.15",
    "data subject":        "Art.15",
    "ropa":                "Art.30",
    "records of processing": "Art.30",
}


def _detect_document_dimensions(query: str) -> tuple[bool, str | None]:
    """
    Detect if query is asking about documents/evidence.
    Returns (needs_documentation, document_topic_ref).
    """
    q = query.lower()
    needs_doc = any(phrase in q for phrase in DOCUMENTATION_PHRASES)

    # Try to resolve a topic ref from the query
    topic_ref = None
    for topic, ref in DOCUMENT_TOPIC_MAP.items():
        if topic in q:
            topic_ref = ref
            break

    return needs_doc, topic_ref


def _detect_document_question_type(query: str) -> QuestionType | None:
    """
    Detect if query is specifically a document inventory or content query.
    Returns the specific QuestionType or None if not a pure document query.
    """
    q = query.lower()
    if any(phrase in q for phrase in DOCUMENT_CONTENT_PHRASES):
        return QuestionType.DOCUMENT_CONTENT
    if any(phrase in q for phrase in DOCUMENT_INVENTORY_PHRASES):
        return QuestionType.DOCUMENT_INVENTORY
    return None


CLASSIFIER_PROMPT = """You are classifying a compliance query for a precise RAG pipeline.

Tenant: {tenant_name}
Standards in scope: {standards}
Role: {role}
Has posture data: {has_posture}
Active topic from session: {active_refs}

Query: "{query}"

Classify this query and return JSON only, no other text:
{{
  "question_type": "definition|implementation|gap_analysis|posture_check|cross_framework|free_assessment|document_inventory|document_content|unknown",
  "standards_scope": ["list of relevant standard IDs from: {standards}"],
  "role_filter": "controller|processor|both|null",
  "needs_posture": true|false,
  "needs_documentation": true|false,
  "cited_refs": ["any explicit refs like Art.32 or A.8.24 mentioned in query"],
  "detected_events": ["any runtime events detected: personal_data_breach|data_subject_access_request|data_subject_erasure_request|new_processor_engaged|new_processing_activity|significant_system_change|audit_nonconformity|certification_audit|supervisory_authority_inquiry"],
  "document_topic": "control ref if query is about a specific document e.g. A.8.24 for encryption policy, or null",
  "confidence": 0.0-1.0,
  "reasoning": "one sentence"
}}

Classification rules (apply strictly):
- "definition":          asking what something means, says, or requires in the abstract
- "implementation":      asking how to build, create, or set something up
- "gap_analysis":        asking what is missing, what gaps exist, what needs fixing
- "posture_check":       asking about OUR/WE compliance status — "do WE need to", "are WE covered"
- "cross_framework":     asking how one standard relates to another
- "free_assessment":     asking for an overall picture or overview
- "document_inventory":  asking what documents are required — "what documents do we need?"
- "document_content":    asking what a document must contain — "what should our policy include?"

Dimension rules:
- needs_posture=true when question_type is posture_check or gap_analysis OR query uses "our/we"
- needs_documentation=true when query mentions documents, policies, procedures, evidence, checklist

Event detection — set detected_events when query describes a runtime occurrence:
- "we had a breach / data was leaked / unauthorised access" → personal_data_breach
- "DSAR / data subject access request / someone asked for their data" → data_subject_access_request
- "erasure request / right to be forgotten" → data_subject_erasure_request
- "new processor / new cloud provider / new supplier" → new_processor_engaged
- "new processing activity / starting to process" → new_processing_activity
- "system change / new system / go-live" → significant_system_change
- "audit finding / nonconformity / corrective action" → audit_nonconformity
- "certification audit / stage 1 / stage 2" → certification_audit
- "ICO / supervisory authority contacted us" → supervisory_authority_inquiry

Key distinction — posture_check vs implementation:
  "Do we need to notify customers?" → posture_check
  "How do I notify customers?"      → implementation

- cited_refs: extract article numbers (Art.X, Art.X.Y.Z) and ISO refs (A.X.XX, X.X.X)
- confidence < 0.7 if genuinely ambiguous
- If active_refs are set in session, the query almost certainly relates to them"""


# ── Document query phrase detection ───────────────────────────────────────────

DOCUMENTATION_PHRASES: list[str] = [
    "document", "policy", "procedure", "evidence",
    "what do we need to have", "required documentation",
    "what should our", "what must", "checklist",
    "what goes in", "prove compliance", "audit evidence",
    "what policies", "what procedures", "documentation requirements",
    "mandatory documents", "required documents", "what documents",
    "document checklist", "documents we need",
    "what should be in", "what items", "what sections",
    "policy template", "policy contain", "procedure contain",
    "dpa contain", "contract contain",
]

DOCUMENT_INVENTORY_PHRASES: list[str] = [
    "mandatory documents", "required documents", "what documents do we need",
    "document checklist", "documents we need", "what policies do we need",
    "what procedures do we need", "documentation requirements",
    "what do we need to have in place",
]

DOCUMENT_CONTENT_PHRASES: list[str] = [
    "what should our policy include", "what must a",
    "what should be in our", "what goes in", "policy template",
    "what must our", "what should our procedure", "what items",
    "what sections", "checklist for", "policy contain", "must contain",
]

# Topic → control_ref map for document queries
# "what documents do we need for encryption?" → A.8.24
DOCUMENT_TOPIC_MAP: dict[str, str] = {
    "cryptography":        "A.8.24",
    "encryption":          "A.8.24",
    "data masking":        "A.8.11",
    "masking":             "A.8.11",
    "incident":            "A.5.24",
    "incident response":   "A.5.24",
    "breach":              "Art.33",
    "data breach":         "Art.33",
    "cloud":               "A.5.23",
    "cloud services":      "A.5.23",
    "cloud storage":       "A.5.23",
    "processor":           "Art.28",
    "dpa":                 "Art.28",
    "data processing":     "Art.28",
    "privacy notice":      "Art.13",
    "privacy policy":      "Art.13",
    "access rights":       "A.5.18",
    "access control":      "A.5.15",
    "risk assessment":     "6.1.2",
    "risk":                "6.1.2",
    "remote working":      "A.6.7",
    "remote work":         "A.6.7",
    "software development":"A.8.25",
    "secure development":  "A.8.25",
    "internal audit":      "9.2",
    "audit":               "9.2",
    "management review":   "9.3",
    "isms policy":         "5.2",
    "information security policy": "5.2",
    "isms scope":          "4.3",
    "dsar":                "Art.15",
    "data subject":        "Art.15",
    "ropa":                "Art.30",
    "records of processing": "Art.30",
}


def _detect_document_dimensions(query: str) -> tuple[bool, str | None]:
    """
    Detect if query is asking about documents/evidence.
    Returns (needs_documentation, document_topic_ref).
    """
    q = query.lower()
    needs_doc = any(phrase in q for phrase in DOCUMENTATION_PHRASES)

    # Try to resolve a topic ref from the query
    topic_ref = None
    for topic, ref in DOCUMENT_TOPIC_MAP.items():
        if topic in q:
            topic_ref = ref
            break

    return needs_doc, topic_ref


def _detect_document_question_type(query: str) -> QuestionType | None:
    """
    Detect if query is specifically a document inventory or content query.
    Returns the specific QuestionType or None if not a pure document query.
    """
    q = query.lower()
    if any(phrase in q for phrase in DOCUMENT_CONTENT_PHRASES):
        return QuestionType.DOCUMENT_CONTENT
    if any(phrase in q for phrase in DOCUMENT_INVENTORY_PHRASES):
        return QuestionType.DOCUMENT_INVENTORY
    return None


INTAKE_CLASSIFIER_PROMPT = """You are classifying an initial user description of what they are working on.

Tenant: {tenant_name}
Standards available: {standards}
Role: {role}

User said: "{user_input}"

The semantic search found these candidate topic clusters:
{cluster_summaries}

Based on the user's description and the clusters found, classify their intent.
Return JSON only:
{{
  "question_type": "definition|implementation|gap_analysis|posture_check|cross_framework|free_assessment|unknown",
  "standards_scope": ["relevant standard IDs"],
  "role_filter": "controller|processor|both|null",
  "needs_posture": true|false,
  "primary_cluster": "label of the most relevant cluster or null",
  "confidence": 0.0-1.0
}}"""


# ── Explicit intent patterns ───────────────────────────────────────────────────
# These patterns allow skip-LLM fast classification for unambiguous queries.

EXPLICIT_REF_PATTERN   = re.compile(
    r'\b(Art\.\d+(\.\d+)*(\.[a-z])?|A\.\d+\.\d+|\d+\.\d+(\.\d+)?)\b'
)
DEFINITION_VERBS       = re.compile(
    r'\b(what does|what is|explain|define|describe|tell me about|'
    r'what does .* say|what does .* mean|what does .* require|'
    r'what are the implications|implications of|what happens if|'
    r'understand|understanding)\b',
    re.IGNORECASE
)
GAP_VERBS              = re.compile(
    r'\b(gaps?|missing|what.*need|not compliant|failing|fix|remediat|'
    r'what.*wrong|issues?|problems?|what to do|actions?)\b',
    re.IGNORECASE
)
POSTURE_VERBS          = re.compile(
    r'\b(compliant|compliance|status|covered|our (posture|gaps?|status)|'
    r'are we|do we|have we|where (are|do) we)\b',
    re.IGNORECASE
)
IMPLEMENTATION_VERBS   = re.compile(
    r'\b(implement|build|create|set up|how to|how do|steps?|procedure|'
    r'what should we build|how should we|ensure|how can we|'
    r'what do we need for|requirements for|what.*need.*product|'
    r'collecting personal data|process personal data)\b',
    re.IGNORECASE
)

# High-confidence practitioner phrases that map directly to a control cluster
# without needing full vector cluster disambiguation.
# Format: (pattern, question_type, primary_refs)
CLEAR_INTENT_PHRASES = [
    # Encryption / cryptography gaps
    (re.compile(r'\bencryption\s+gaps?\b', re.IGNORECASE),
     "gap_analysis", ["A.8.24", "Art.32"]),
    (re.compile(r'\bcryptograph\w*\s+(?:gaps?|issues?|problems?)\b', re.IGNORECASE),
     "gap_analysis", ["A.8.24"]),
    (re.compile(r'\bencryption\s+policy\s+gap\b', re.IGNORECASE),
     "gap_analysis", ["A.8.24"]),

    # Audit preparation
    (re.compile(r'\b(?:preparing|prepare)\s+for\s+(?:our\s+)?(?:ISO\s*27001|ISMS)\s+audit\b', re.IGNORECASE),
     "implementation", ["9.2", "9.3"]),
    (re.compile(r'\bISO\s*27001\s+audit\s+(?:prep|preparation|readiness)\b', re.IGNORECASE),
     "implementation", ["9.2"]),
    (re.compile(r'\baudit\s+(?:next\s+month|coming\s+up|readiness)\b', re.IGNORECASE),
     "implementation", ["9.2"]),

    # Cloud storage obligations
    (re.compile(r'\bcloud\s+storage\s+(?:for\s+)?(?:data\s+privacy|personal\s+data|obligations?)\b', re.IGNORECASE),
     "implementation", ["A.5.23", "Art.28"]),
    (re.compile(r'\bobligations?\s+(?:for|on)\s+cloud\s+(?:storage|services?)\b', re.IGNORECASE),
     "implementation", ["A.5.23", "Art.28"]),
    (re.compile(r'\bcloud\s+(?:security\s+requirements?|provider\s+obligations?)\b', re.IGNORECASE),
     "implementation", ["A.5.23"]),

    # Data masking gaps
    (re.compile(r'\bdata\s+masking\s+(?:gaps?|missing|policy)\b', re.IGNORECASE),
     "gap_analysis", ["A.8.11"]),

    # Access rights / access control gaps
    (re.compile(r'\baccess\s+rights?\s+(?:gaps?|issues?|problems?|status)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.18"]),
    (re.compile(r'\baccess\s+(?:control|review)\s+(?:gaps?|issues?|status)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.18", "A.5.15"]),
    (re.compile(r'\bwhat\s+are\s+our\s+access\s+(?:rights?|control)\s+(?:gaps?|issues?)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.18"]),

    # Supplier / vendor gaps
    (re.compile(r'\bsupplier\s+(?:gaps?|assessment|review)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.19", "A.5.20"]),
    (re.compile(r'\bvendor\s+(?:gaps?|assessment|review|compliance)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.19"]),
    (re.compile(r'\bbusiness\s+partner\s+(?:gaps?|assessment)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.19"]),

    # Software / ChatGPT / AI tools
    (re.compile(r'\bsoftware\s+(?:allow|deny|list|policy|installation\s+gaps?)\b', re.IGNORECASE),
     "gap_analysis", ["A.8.19"]),
    (re.compile(r'\b(?:chatgpt|ai\s+tools?|shadow\s+it)\s+(?:policy|gaps?|control)\b', re.IGNORECASE),
     "gap_analysis", ["A.8.19"]),

    # Incident response gaps
    (re.compile(r'\bincident\s+response\s+(?:gaps?|issues?|drill|test)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.26", "A.5.24"]),
    (re.compile(r'\bIR\s+(?:drill|test|gaps?)\b', re.IGNORECASE),
     "gap_analysis", ["A.5.26"]),

    # General "our gaps" queries — route to gap_analysis
    (re.compile(r'\bwhat\s+are\s+our\s+(?:main\s+)?(?:compliance\s+)?gaps?\b', re.IGNORECASE),
     "gap_analysis", []),

    # Posture overview — unambiguous "what is our posture/status" phrases
    # These go to gap_analysis (closest current type; posture_check is future)
    (re.compile(r'\bwhat\s+is\s+our\s+(?:iso\s*2700\d|compliance|isms?)\s+posture\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bwhat\s+is\s+our\s+(?:overall\s+)?compliance\s+(?:status|posture|picture)\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bsummar(?:ise|ize)\s+our\s+(?:iso\s*2700\d|compliance|isms?)\s+(?:status|posture)\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bare\s+we\s+(?:iso\s*2700\d\s+)?certified\b', re.IGNORECASE),
     "posture_check", []),

    # Implementation / remediation queries — unambiguous "what should we do" phrases
    (re.compile(r'\bwhat\s+should\s+we\s+do\s+(?:to\s+)?(?:close|address|fix|remediat)\b', re.IGNORECASE),
     "implementation", []),
    (re.compile(r'\bhow\s+(?:do|should|can)\s+we\s+(?:close|fix|address|remediat)\b', re.IGNORECASE),
     "implementation", []),
    (re.compile(r'\bhow\s+should\s+we\s+prepare\s+for\s+(?:our|the|an?)\s+(?:\w+\s+){1,4}audit\b', re.IGNORECASE),
     "implementation", []),
    (re.compile(r'\bhow\s+(?:do|should)\s+we\s+implement\b', re.IGNORECASE),
     "implementation", []),

    # Document content queries — "what must/should our X contain/include"
    (re.compile(r'\bwhat\s+(?:must|should)\s+(?:our|the|a)\s+[\w\s]+(?:policy|procedure|plan|playbook)\s+contain\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\bwhat\s+(?:must|should)\s+be\s+in\s+(?:our|a|the)\s+[\w\s]+(?:policy|procedure|plan)\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\brequired\s+(?:elements?|contents?|sections?)\s+of\s+(?:our|a|the)\s+[\w\s]+(?:policy|procedure)\b', re.IGNORECASE),
     "document_content", []),

    # Scope N/A queries — physical security and dev controls not applicable to Arion
    # These should answer directly "N/A for our scope" rather than firing clarification
    (re.compile(r'\bphysical\s+security\s+(?:gaps?|findings?|controls?|posture)\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bsoftware\s+(?:development|dev)\s+security\s+(?:gaps?|findings?|controls?)\b', re.IGNORECASE),
     "gap_analysis", []),

    # Document upload status queries — narrow phrases only
    # Deliberately narrow to avoid over-triggering on training/process questions
    # "have we uploaded" is unambiguous — always about file upload
    # Broader questions like "what is missing to evidence X" go through LLM classifier
    # to preserve context-aware routing for complex questions
    (re.compile(r'\bhave\s+we\s+uploaded\s+(?:our|the)\b', re.IGNORECASE),
     "document_inventory", []),
    (re.compile(r'\b(?:is|are)\s+(?:our|the)\s+[\w\s]{3,40}(?:policy|procedure|plan|playbook)\s+(?:uploaded|in\s+the\s+system|on\s+the\s+platform)\b', re.IGNORECASE),
     "document_inventory", []),
    (re.compile(r'\bwhich\s+documents?\s+(?:have\s+(?:not|yet)\s+been|are\s+(?:not|still)?)\s+uploaded\b', re.IGNORECASE),
     "document_inventory", []),
    (re.compile(r'\bshow\s+(?:me\s+)?(?:all\s+)?(?:missing|unuploaded)\s+documents?\b', re.IGNORECASE),
     "document_inventory", []),

    # GDPR fulfilment via ISO 27701 — cross_framework query
    (re.compile(r'\b(?:are\s+we|is\s+arion)\s+(?:gdpr\s+)?compliant\b', re.IGNORECASE),
     "cross_framework", []),
    (re.compile(r'\bGDPR\s+(?:complian|fulfilm|coverage|status|evaluation|assessment)\w*\b', re.IGNORECASE),
     "cross_framework", []),
    (re.compile(r'\bhow\s+(?:do\s+we|does\s+arion)\s+(?:meet|satisfy|cover)\s+GDPR\b', re.IGNORECASE),
     "cross_framework", []),
    (re.compile(r'\bwhat\s+(?:GDPR|privacy)\s+obligations?\s+(?:do\s+we|apply|are\s+we)\b', re.IGNORECASE),
     "cross_framework", []),
    (re.compile(r'\bGDPR\s+Art(?:icle|\.)?\s*\d+\b', re.IGNORECASE),
     "cross_framework", []),
    (re.compile(r'\bour\s+(?:top|main|biggest|current)\s+(?:compliance\s+)?gaps?\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bshow\s+(?:me\s+)?(?:all\s+)?our\s+(?:NC|OFI|findings?|gaps?)\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bwhat\s+(?:NC|OFI)\s+(?:do\s+we\s+have|findings?\s+do\s+we)\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bwhat\s+are\s+our\s+(?:NC|OFI)\s+findings?\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\bour\s+(?:NC|OFI)\s+findings?\b', re.IGNORECASE),
     "gap_analysis", []),
    (re.compile(r'\blist\s+(?:our\s+)?(?:NC|OFI|non.conformit|non-conformit)\b', re.IGNORECASE),
     "gap_analysis", []),

    # Glossary / definition queries — bypass clarification, answer directly
    (re.compile(r'\bwhat\s+(?:is|are)\s+(?:an?\s+)?(?:NC|OFI|ISMS|DPIA|DPA|RoPA|DSR|DSAR)\b', re.IGNORECASE),
     "definition", []),
    (re.compile(r'\bwhat\s+(?:does\s+)?(?:NC|OFI|ISMS|DPIA|DPA|RoPA|DSR|DSAR)\s+(?:mean|stand for)\b', re.IGNORECASE),
     "definition", []),
    (re.compile(r'\bwhat\s+is\s+a(?:n)?\s+(?:control|article|clause|annex|standard|obligation|requirement)\b', re.IGNORECASE),
     "definition", []),
    (re.compile(r'\bwhat\s+(?:is|are)\s+(?:ISO\s*27001|ISO\s*27002|GDPR|the\s+ISMS)\b', re.IGNORECASE),
     "definition", []),
    (re.compile(r'\bexplain\s+(?:what\s+)?(?:NC|OFI|ISMS|DPIA|DPA|a\s+control|an\s+article)\b', re.IGNORECASE),
     "definition", []),

    # Evidence / record-keeping queries — map to document_content
    (re.compile(r'\bevidence\s+(?:do\s+(?:i|we)\s+need|to\s+keep|required|needed)\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\bwhat\s+records?\s+(?:do\s+(?:i|we)\s+need|(?:must|should)\s+(?:i|we)\s+keep|are\s+required)\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\bwhat\s+(?:audit\s+)?evidence\s+(?:is\s+required|do\s+we\s+need|should\s+we\s+have)\b', re.IGNORECASE),
     "document_content", []),

    # Document content queries — bypass clarification, go direct
    (re.compile(r'\bwhat\s+(?:must|should)\s+our\s+\w+\s+policy\s+(?:include|contain)\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\bwhat\s+(?:must|should)\s+(?:a|an|our)\s+\w+\s+(?:policy|procedure|dpa)\s+contain\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\bpolicy\s+(?:checklist|template|requirements?)\b', re.IGNORECASE),
     "document_content", []),
    (re.compile(r'\bwhat\s+(?:items?|sections?|clauses?)\s+(?:does|should|must)\s+\w+\s+(?:policy|procedure)\b', re.IGNORECASE),
     "document_content", []),

    # Document inventory queries
    (re.compile(r'\bwhat\s+(?:mandatory\s+)?documents?\s+(?:do\s+we\s+need|are\s+required)\b', re.IGNORECASE),
     "document_inventory", []),
    (re.compile(r'\bdocument(?:ation)?\s+(?:checklist|requirements?|inventory)\b', re.IGNORECASE),
     "document_inventory", []),
    (re.compile(r'\bwhat\s+policies?\s+(?:do\s+we\s+need|are\s+required)\b', re.IGNORECASE),
     "document_inventory", []),
]


# ── QueryClassifier ────────────────────────────────────────────────────────────

class QueryClassifier:
    """
    Full conversation flow manager — intake, clarification, intent resolution.

    Usage:
        classifier = QueryClassifier(tenant_profile, retriever)

        # First message — intake
        result = classifier.process_intake(user_text)
        if result.state == IntakeState.AMBIGUOUS:
            # Show result.clarification to user, wait for response
            result = classifier.process_clarification(user_choice, result)

        # Subsequent queries within the session
        intent = classifier.classify_query(query, session, history)
    """

    # Confidence thresholds — calibrated for text-embedding-3-large
    # ChromaDB cosine similarity with this model:
    #   Strong match  0.35–0.60
    #   Good match    0.25–0.45
    #   Weak/no match < 0.20
    CLEAR_THRESHOLD     = 0.42   # top cluster score to proceed without asking
    DOMINANT_GAP        = 0.08   # min gap between top and second cluster
    MIN_MATCH_SCORE     = 0.22   # below this = no_match

    def __init__(
        self,
        tenant_profile: TenantProfile,
        retriever,                          # VectorRetriever instance
        classify_model:     str = "gpt-4o-mini",
        clarify_model:      str = "gpt-4o-mini",
        temperature:        float = 0.1,    # low — we want consistency
    ):
        # Read LOCAL_LLM_MODEL at init — overrides defaults when set
        local_model = os.getenv("LOCAL_LLM_MODEL")
        if local_model:
            classify_model = local_model
            clarify_model  = local_model

        self.tenant      = tenant_profile
        self.retriever   = retriever
        self.clf_model   = classify_model
        self.clr_model   = clarify_model
        self.temperature = temperature
        self._openai     = None

    # ── Public API ─────────────────────────────────────────────────────────

    def opening_message(self) -> str:
        """Returns the opening intake prompt shown to new users."""
        standards_str = " and ".join(
            s.split(":")[0].replace("ISO27001", "ISO 27001")
                           .replace("GDPR", "GDPR")
            for s in self.tenant.applicable_standards
        )
        return (
            f"Hi — I'm your {standards_str} compliance advisor for "
            f"{self.tenant.name}.\n\n"
            f"What are you working on today? You can describe it in your "
            f"own words, for example:\n\n"
            f"  • 'We had a data breach last week and need to know what "
            f"to report'\n"
            f"  • 'We're preparing for our ISO 27001 audit next month'\n"
            f"  • 'I want to understand what we need for our new product'\n"
            f"  • 'Give me an overview of where we stand'\n\n"
            f"Or ask me a specific question directly."
        )

    def process_intake(self, user_input: str) -> IntakeResult:
        """
        Process the initial 'what are you working on' response.

        Returns IntakeResult with state:
          EXPLICIT  → explicit ref/action detected, session set, proceed
          CLEAR     → single dominant cluster, session set, proceed
          AMBIGUOUS → multiple clusters, clarification question generated
          NO_MATCH  → no confident results, redirect question generated
        """
        # 1. Check for explicit refs / clear action verbs — skip intake if found
        explicit_result = self._check_explicit(user_input)
        if explicit_result:
            return explicit_result

        # 2. Vector search on the full description
        results = self.retriever.search(
            user_input,
            n=20,
            standards=self.tenant.applicable_standards,
        )

        if not results.results:
            return self._handle_no_match(user_input, [])

        # 3. Group into clusters
        clusters = self._build_clusters(results.results)

        # 4. Score and decide state
        top    = clusters[0] if clusters else None
        second = clusters[1] if len(clusters) > 1 else None

        if not top or top.avg_score < self.MIN_MATCH_SCORE:
            return self._handle_no_match(user_input, clusters)

        if (top.avg_score >= self.CLEAR_THRESHOLD and
                (second is None or
                 top.avg_score - second.avg_score >= self.DOMINANT_GAP)):
            # Single dominant cluster — classify and proceed
            return self._handle_clear(user_input, clusters)

        # Multiple comparable clusters — ask for clarification
        return self._handle_ambiguous(user_input, clusters)

    def process_clarification(
        self,
        user_choice:     str,
        prior_result:    IntakeResult,
    ) -> IntakeResult:
        """
        Process the user's response to a clarification question.
        Maps their choice back to the matching cluster and builds session.
        """
        choice_lower = user_choice.lower().strip()
        clusters     = prior_result.clusters

        # Try to match choice to a cluster
        selected = None
        if choice_lower.startswith("a") and clusters:
            selected = clusters[0]
        elif choice_lower.startswith("b") and len(clusters) > 1:
            selected = clusters[1]
        elif choice_lower.startswith("c") and len(clusters) > 2:
            selected = clusters[2]
        else:
            # Let the LLM figure out what they meant
            selected = self._match_choice_to_cluster(user_choice, clusters)

        if selected is None:
            # Still unclear — one more attempt
            return self._handle_ambiguous(user_choice, clusters)

        # Resolve taxonomy type directly from the user's option selection
        # This avoids re-running classification and gives deterministic routing
        resolved_taxonomy = None
        tmap = getattr(prior_result, 'taxonomy_options_map', None) or {}
        if choice_lower and tmap:
            # Match first letter of response to taxonomy map
            for letter, taxonomy_id in tmap.items():
                if choice_lower.startswith(letter):
                    resolved_taxonomy = taxonomy_id
                    break

        # Map taxonomy_id back to question_type string for the session
        # (classifier uses legacy strings internally; taxonomy is the richer layer)
        from rag.taxonomy import CLASSIFIER_TO_TAXONOMY
        TAXONOMY_TO_CLASSIFIER = {v: k for k, v in CLASSIFIER_TO_TAXONOMY.items()}
        if resolved_taxonomy:
            qtype_str = TAXONOMY_TO_CLASSIFIER.get(resolved_taxonomy, 'gap_analysis')
        else:
            qtype_str = self._infer_question_type(prior_result.raw_input)

        session = self._build_session(
            user_input     = prior_result.raw_input,
            primary_cluster= selected,
            question_type  = qtype_str,
        )
        return IntakeResult(
            state                = IntakeState.CLEAR,
            session              = session,
            clarification        = None,
            clusters             = [selected],
            raw_input            = user_choice,
            taxonomy_options_map = None,
        )

    def classify_query(
        self,
        query:   str,
        session: SessionContext,
        history: list[dict],
    ) -> QueryIntent:
        """
        Classify a specific query within an established session.

        Fast path: explicit refs → pattern match, no LLM.
        Standard path: LLM classification with session context.
        Low confidence: return QueryIntent with clarification_question set.
        """
        # Fast path — explicit ref with clear verb
        fast = self._fast_classify(query, session)
        if fast:
            return fast

        # Standard path — LLM classification
        return self._llm_classify(query, session, history)


    # ── Best-effort answer ────────────────────────────────────────────────────

    def answer_best_effort(
        self,
        node_ids:       list[str],
        session:        SessionContext,
        original_query: str = "",
    ) -> QueryIntent:
        """
        Build a QueryIntent from available node IDs without clarification.

        Called by the orchestrator when the clarification limit is reached
        or the user explicitly overrides with "just answer" / "skip".

        Returns a QueryIntent at confidence 0.5 (best-effort) so the
        pipeline generates a broad answer rather than a precise posture check.
        """
        # Extract explicit refs from the original query if any
        explicit_refs = [r[0] for r in EXPLICIT_REF_PATTERN.findall(
            original_query
        )]

        # Infer question type from verbs in the query
        qtype = self._infer_question_type(original_query)
        if qtype == QuestionType.UNKNOWN:
            qtype = QuestionType.DEFINITION   # safest default

        # Derive refs from node IDs (format: "STANDARD:REF" or "STD:VER:REF")
        resolved_refs = []
        for nid in node_ids[:5]:
            parts = nid.split(":")
            ref   = parts[-1]
            if ref and ref not in resolved_refs:
                resolved_refs.append(ref)

        # Merge with explicit refs and active session refs
        all_refs = list(dict.fromkeys(
            explicit_refs + resolved_refs + session.active_refs
        ))[:8]

        needs_posture = qtype in (
            QuestionType.GAP_ANALYSIS, QuestionType.POSTURE_CHECK
        )
        _, doc_topic = _detect_document_dimensions(original_query)
        needs_doc    = bool(_detect_document_question_type(original_query))
        try:
            from enrichment.events.event_nodes import detect_events
            events = detect_events(original_query)
        except ImportError:
            events = []

        return QueryIntent(
            question_type      = qtype,
            standards_scope    = session.standards or self.tenant.applicable_standards,
            role_filter        = session.role,
            needs_posture      = needs_posture,
            cited_refs         = explicit_refs,
            resolved_refs      = all_refs,
            confidence         = 0.5,
            raw_query          = original_query,
            dimensions         = QueryDimensions(
                needs_obligation    = True,
                needs_posture       = needs_posture,
                needs_documentation = needs_doc,
            ),
            detected_events    = events,
            document_topic_ref = doc_topic,
        )

    # ── Intake handlers ────────────────────────────────────────────────────

    def _check_explicit(self, user_input: str) -> IntakeResult | None:
        """
        Detect explicit refs (Art.32, A.8.24) or very clear action verbs
        or high-confidence practitioner phrases.
        If found, skip the full intake and build a minimal session.
        """
        # Check high-confidence practitioner phrases first
        for pattern, qtype_str, primary_refs in CLEAR_INTENT_PHRASES:
            if pattern.search(user_input):
                qtype_map = {
                    "gap_analysis":       QuestionType.GAP_ANALYSIS,
                    "implementation":     QuestionType.IMPLEMENTATION,
                    "definition":         QuestionType.DEFINITION,
                    "posture_check":      QuestionType.POSTURE_CHECK,
                    "document_content":   QuestionType.DOCUMENT_CONTENT,
                    "document_inventory": QuestionType.DOCUMENT_INVENTORY,
                    "cross_framework":    QuestionType.CROSS_FRAMEWORK,
                }
                qtype = qtype_map.get(qtype_str, QuestionType.GAP_ANALYSIS)
                session = SessionContext(
                    tenant_profile = self.tenant,
                    standards      = self.tenant.applicable_standards,
                    role           = None,
                    intent_type    = qtype,
                    active_refs    = primary_refs,
                    active_cluster = primary_refs[0] if primary_refs else None,
                )
                return IntakeResult(
                    state         = IntakeState.CLEAR,
                    session       = session,
                    clusters      = [],
                    clarification = None,
                    raw_input     = user_input,
                )

        refs = EXPLICIT_REF_PATTERN.findall(user_input)
        refs = [r[0] for r in refs]   # extract just the ref string

        if not refs:
            return None

        # Has explicit ref — determine question type from verbs
        qtype = self._infer_question_type(user_input)

        session = SessionContext(
            tenant_profile = self.tenant,
            standards      = self.tenant.applicable_standards,
            role           = self.tenant.role[0] if self.tenant.role else None,
            intent_type    = qtype,
            active_refs    = refs,
            active_cluster = None,
        )
        return IntakeResult(
            state        = IntakeState.EXPLICIT,
            session      = session,
            clarification = None,
            clusters     = [],
            raw_input    = user_input,
        )

    def _handle_clear(
        self,
        user_input: str,
        clusters:   list[ClusterSummary],
    ) -> IntakeResult:
        """Single dominant cluster — classify and build session."""
        top   = clusters[0]
        qtype = self._infer_question_type(user_input)

        # If still unclear from verbs alone, use LLM classifier on intake
        if qtype == QuestionType.UNKNOWN:
            qtype = self._llm_classify_intake(user_input, clusters)

        session = self._build_session(user_input, top, qtype)
        return IntakeResult(
            state        = IntakeState.CLEAR,
            session      = session,
            clarification = None,
            clusters     = clusters,
            raw_input    = user_input,
        )

    def _handle_ambiguous(
        self,
        user_input: str,
        clusters:   list[ClusterSummary],
    ) -> IntakeResult:
        """Multiple clusters — LLM writes natural clarification question.

        Builds client context from document_alerts and posture so the
        clarifier can cite specific known facts rather than abstract options.
        """
        client_context   = self._build_client_context_for_clarification(
            user_input, clusters
        )
        taxonomy_options = self._default_taxonomy_options(clusters)
        question = self._write_clarification(
            user_input,
            clusters[:3],
            client_context   = client_context,
            taxonomy_options = taxonomy_options,
        )
        # Build taxonomy map so process_clarification can resolve directly
        letters = "abc"
        tmap = {}
        for i, cluster in enumerate(clusters[:3]):
            qtype = getattr(cluster, 'question_type', None) or 'gap_analysis'
            try:
                from rag.taxonomy import get_taxonomy_type
                entry = get_taxonomy_type(qtype)
                tmap[letters[i]] = entry.type_id
            except Exception:
                tmap[letters[i]] = qtype
        # Ensure REMEDIATION_GUIDE is always an option if not present
        if 'REMEDIATION_GUIDE' not in tmap.values() and len(tmap) < 3:
            tmap[letters[len(tmap)]] = 'REMEDIATION_GUIDE'

        return IntakeResult(
            state                = IntakeState.AMBIGUOUS,
            session              = None,
            clarification        = question,
            clusters             = clusters[:3],
            raw_input            = user_input,
            taxonomy_options_map = tmap,
        )

    def _build_client_context_for_clarification(
        self,
        user_input: str,
        clusters:   list[ClusterSummary],
    ) -> str:
        """
        Build a brief factual context string from what the system knows.
        Looks at document_alerts and posture data on the tenant profile
        to find facts relevant to the user's query.
        """
        lines = []

        # Document alerts — check if query mentions any registered document names
        doc_alerts = getattr(self.tenant, "document_alerts", None) or []
        if doc_alerts:
            query_lower = user_input.lower()
            relevant_docs = []
            for alert in doc_alerts:
                title = (alert.get("document_title") or "").lower()
                ref   = (alert.get("external_ref") or "").lower()
                # Check if any significant words from the document title appear in the query
                title_words = [w for w in title.split() if len(w) > 4]
                if any(w in query_lower for w in title_words):
                    relevant_docs.append(alert)

            if relevant_docs:
                for doc in relevant_docs[:3]:
                    alert_type = doc.get("alert_type", "INFO")
                    lines.append(
                        f"- {doc['document_title']} ({doc['external_ref']}) is registered "
                        f"but NOT yet uploaded (status: {alert_type.lower()}, "
                        f"linked to: {doc.get('linked_controls', 'no linked controls')})"
                    )
            elif doc_alerts:
                # No specific match — give a summary
                critical = sum(1 for a in doc_alerts if a.get("alert_type") == "CRITICAL")
                if critical:
                    lines.append(
                        f"- {critical} document(s) are registered but not uploaded "
                        f"and linked to open NC findings"
                    )

        # Posture — find NC/OFI findings relevant to query clusters
        posture = getattr(self.tenant, "posture_data", None) or {}
        if posture:
            nc_refs  = [r.split(":")[-1] for r, v in posture.items()
                       if v.get("finding") == "NC"]
            ofi_refs = [r.split(":")[-1] for r, v in posture.items()
                       if v.get("finding") == "OFI"]
            if nc_refs:
                lines.append(f"- Open NC findings: {', '.join(nc_refs)}")
            if ofi_refs:
                lines.append(f"- Open OFI findings: {', '.join(ofi_refs)}")

        return "\n".join(lines) if lines else ""

    def _handle_no_match(
        self,
        user_input: str,
        clusters:   list[ClusterSummary],
    ) -> IntakeResult:
        """No confident match — LLM writes a helpful redirect."""
        message = self._write_no_match(user_input)
        return IntakeResult(
            state         = IntakeState.NO_MATCH,
            session       = None,
            clarification = message,
            clusters      = clusters,
            raw_input     = user_input,
        )

    # ── Cluster building ───────────────────────────────────────────────────

    def _build_clusters(
        self,
        results: list,                    # list[VectorResult]
    ) -> list[ClusterSummary]:
        """
        Group vector results into topic clusters.

        Clustering strategy:
          - GDPR: group by article root (Art.32.1.a → Art.32 cluster)
          - ISO:  group by control group prefix (A.5.15 → A.5.1x cluster)
          - Management clauses: group by clause number (5.x, 6.x)
          - Score each cluster by average similarity of its members
          - Sort by score descending
        """
        import re
        cluster_map: dict[str, list] = {}

        for r in results:
            if r.is_informational:
                continue

            ref = r.ref
            if r.is_gdpr:
                # Group by article root: Art.32.1.a → "gdpr:Art.32"
                m = re.match(r'(Art\.\d+)', ref)
                key = f"gdpr:{m.group(1)}" if m else f"gdpr:{ref}"
            elif ref.startswith('A.'):
                # Group by control family: A.5.15 → "iso:A.5.1x"
                m = re.match(r'(A\.\d+\.\d)', ref)
                key = f"iso:{m.group(1)}x" if m else f"iso:{ref}"
            else:
                # Management clauses: 5.1, 6.1.2 → group by major clause
                m = re.match(r'(\d+)', ref)
                key = f"iso:clause{m.group(1)}" if m else f"iso:{ref}"

            cluster_map.setdefault(key, []).append(r)

        summaries = []
        for key, members in cluster_map.items():
            if not members:
                continue

            members.sort(key=lambda x: x.score, reverse=True)
            top = members[0]
            description = self._extract_description(top)

            summaries.append(ClusterSummary(
                label       = self._cluster_label(top, members),
                standard    = top.standard_id,
                top_refs    = [m.ref for m in members[:3]],
                avg_score   = sum(m.score for m in members) / len(members),
                description = description,
                chapter     = top.metadata.get("chapter", ""),
            ))

        summaries.sort(key=lambda x: x.avg_score, reverse=True)
        return summaries

    def _cluster_label(self, top_node, members: list) -> str:
        """Human-readable cluster label from top node."""
        std   = "GDPR" if top_node.is_gdpr else "ISO 27001"
        title = top_node.title or ""
        # Use root article/control title, not the specific point title
        # e.g. "Security of processing — 1(a)" → "Security of processing"
        root_title = title.split(" — ")[0].strip()
        refs       = ", ".join(m.ref for m in members[:2])
        return f"{std} — {root_title} ({refs})"

    def _extract_description(self, result) -> str:
        """
        Extract the business description from the vector document.
        The document is layered — description is the second paragraph.
        """
        doc    = result.document or ""
        lines  = [l.strip() for l in doc.split('\n') if l.strip()]
        # Line 0 is header (ref: title), line 1+ is business description
        if len(lines) > 1:
            # Return up to first 180 chars of description
            desc = lines[1]
            return desc[:180] + ("..." if len(desc) > 180 else "")
        return result.title

    # ── LLM calls ─────────────────────────────────────────────────────────

    def _write_clarification(
        self,
        user_input:      str,
        clusters:        list[ClusterSummary],
        client_context:  str = "",
        taxonomy_options: str = "",
    ) -> str:
        """
        Write a taxonomy-led clarification question.

        Each option maps to a specific taxonomy type so the user's answer
        directly resolves the routing — not just the topic.

        client_context:   what the system knows (document alerts, open findings)
        taxonomy_options: formatted list of taxonomy types with descriptions
        """
        prompt = CLARIFICATION_WRITER_PROMPT.format(
            tenant_name      = self.tenant.name,
            user_input       = user_input,
            client_context   = client_context or "No specific client context available.",
            taxonomy_options = taxonomy_options or self._default_taxonomy_options(clusters),
        )
        return self._call_llm(prompt, self.clr_model, max_tokens=200, step='clarify')

    def _default_taxonomy_options(self, clusters: list) -> str:
        """
        Build taxonomy options from clusters.
        Maps cluster question_types to TaxonomyEntry descriptions.
        """
        try:
            from rag.taxonomy import get_taxonomy_type
        except ImportError:
            return "(a) Check your compliance status\n(b) Get guidance on what to do\n(c) Understand what a document needs to contain"

        seen = set()
        lines = []
        letters = "abcdefg"

        for i, cluster in enumerate(clusters[:3]):
            qtype = getattr(cluster, 'question_type', None) or 'gap_analysis'
            if qtype in seen:
                continue
            seen.add(qtype)
            try:
                entry = get_taxonomy_type(qtype)
                lines.append(
                    f"({letters[i]}) {entry.display_name} [{entry.type_id}]: "
                    f"{entry.description}"
                )
            except Exception:
                lines.append(f"({letters[i]}) {qtype}")

        # Always include REMEDIATION_GUIDE as an option if not already present
        if 'REMEDIATION_GUIDE' not in seen and len(lines) < 3:
            try:
                from rag.taxonomy import QUERY_TAXONOMY
                entry = QUERY_TAXONOMY['REMEDIATION_GUIDE']
                lines.append(
                    f"({letters[len(lines)]}) {entry.display_name} [{entry.type_id}]: "
                    f"{entry.description}"
                )
            except Exception:
                pass

        return "\n".join(lines) if lines else             "(a) POSTURE_STATUS: Check your compliance status\n"             "(b) REMEDIATION_GUIDE: Get step-by-step guidance on what to do\n"             "(c) DOCUMENT_CONTENT: Understand what a document needs to contain"

    def _write_no_match(self, user_input: str) -> str:
        """Use gpt-4o-mini to write a helpful redirect message."""
        standards_str = ", ".join(
            s.split(":")[0] for s in self.tenant.applicable_standards
        )
        prompt = NO_MATCH_WRITER_PROMPT.format(
            tenant_name = self.tenant.name,
            user_input  = user_input,
            standards   = standards_str,
        )
        return self._call_llm(prompt, self.clr_model, max_tokens=120, step='clarify')

    def _llm_classify_intake(
        self,
        user_input: str,
        clusters:   list[ClusterSummary],
    ) -> QuestionType:
        """Use LLM to classify question type from intake description."""
        cluster_text = self._format_clusters_for_prompt(clusters)
        prompt = INTAKE_CLASSIFIER_PROMPT.format(
            tenant_name      = self.tenant.name,
            standards        = ", ".join(self.tenant.applicable_standards),
            role             = ", ".join(self.tenant.role),
            user_input       = user_input,
            cluster_summaries = cluster_text,
        )
        raw    = self._call_llm(prompt, self.clf_model, max_tokens=200)
        parsed = self._parse_json(raw)
        if parsed:
            try:
                return QuestionType(parsed.get("question_type", "unknown"))
            except ValueError:
                pass
        return QuestionType.UNKNOWN

    def _llm_classify(
        self,
        query:   str,
        session: SessionContext,
        history: list[dict],
    ) -> QueryIntent:
        """Full LLM-based query classification."""
        # Summarise recent history for context
        recent = history[-3:] if history else []
        history_str = "\n".join(
            f"  {m['role']}: {m['content'][:100]}" for m in recent
        ) if recent else "none"

        prompt = CLASSIFIER_PROMPT.format(
            tenant_name  = self.tenant.name,
            standards    = ", ".join(session.standards),
            role         = session.role or "not specified",
            has_posture  = self.tenant.has_posture_data,
            active_refs  = ", ".join(session.active_refs) if session.active_refs else "none",
            query        = query,
        )
        raw    = self._call_llm(prompt, self.clf_model, max_tokens=250)
        parsed = self._parse_json(raw)

        if not parsed:
            # Fallback — return low-confidence unknown
            return QueryIntent(
                question_type   = QuestionType.UNKNOWN,
                standards_scope = session.standards,
                role_filter     = session.role,
                needs_posture   = False,
                cited_refs      = [],
                resolved_refs   = session.active_refs,
                confidence      = 0.3,
                raw_query       = query,
                clarification_question = (
                    "I'm not quite sure what you're asking. "
                    "Could you rephrase — for example, are you asking what "
                    "a specific requirement means, or what you need to do?"
                ),
            )

        cited = parsed.get("cited_refs", [])
        resolved = list(dict.fromkeys(
            cited if cited else session.active_refs[:3]
        ))[:8]

        try:
            qtype = QuestionType(parsed.get("question_type", "unknown"))
        except ValueError:
            qtype = QuestionType.UNKNOWN

        # ── Dimensions ────────────────────────────────────────────────────
        # LLM provides needs_documentation — augment with phrase detection
        llm_needs_doc = bool(parsed.get("needs_documentation", False))
        phrase_needs_doc, phrase_topic = _detect_document_dimensions(query)
        needs_documentation = llm_needs_doc or phrase_needs_doc

        # Refine question_type for pure document queries
        if qtype == QuestionType.UNKNOWN or qtype == QuestionType.DEFINITION:
            doc_qtype = _detect_document_question_type(query)
            if doc_qtype:
                qtype = doc_qtype

        # Document topic ref — LLM or phrase detection
        doc_topic = parsed.get("document_topic") or phrase_topic

        # ── Events ────────────────────────────────────────────────────────
        # LLM detection + phrase detection from event_nodes
        llm_events = parsed.get("detected_events", []) or []
        try:
            from enrichment.events.event_nodes import detect_events
            phrase_events = detect_events(query)
        except ImportError:
            phrase_events = []
        detected_events = list(dict.fromkeys(llm_events + phrase_events))

        # ── Build dimensions dataclass ─────────────────────────────────────
        llm_needs_posture = bool(parsed.get("needs_posture", False))
        needs_posture = (
            llm_needs_posture or
            qtype in (QuestionType.GAP_ANALYSIS, QuestionType.POSTURE_CHECK)
        )
        dimensions = QueryDimensions(
            needs_obligation    = True,                 # always
            needs_posture       = needs_posture,
            needs_documentation = needs_documentation,
        )

        confidence = float(parsed.get("confidence", 0.5))
        intent = QueryIntent(
            question_type       = qtype,
            standards_scope     = parsed.get("standards_scope", session.standards),
            role_filter         = parsed.get("role_filter") or session.role,
            needs_posture       = needs_posture,
            cited_refs          = cited,
            resolved_refs       = resolved,
            confidence          = confidence,
            raw_query           = query,
            dimensions          = dimensions,
            detected_events     = detected_events,
            document_topic_ref  = doc_topic,
        )

        if confidence < 0.7:
            intent.clarification_question = self._write_low_conf_clarification(
                query, session, parsed.get("reasoning", "")
            )

        return intent

    def _write_low_conf_clarification(
        self,
        query:     str,
        session:   SessionContext,
        reasoning: str,
    ) -> str:
        """
        Write a single targeted clarification question for a low-confidence
        classification. Runs a quick vector search to find the ambiguous
        candidates and generates options from them.
        """
        results = self.retriever.search(
            query, n=12, standards=session.standards
        )
        clusters = self._build_clusters(results.results)[:3]
        if len(clusters) >= 2:
            return self._write_clarification(query, clusters)
        # Single cluster but still uncertain — ask simply
        return (
            "Could you clarify what you're looking for? For example, "
            "are you asking what a requirement means, whether you comply "
            "with it, or what steps to take to meet it?"
        )

    def _match_choice_to_cluster(
        self,
        user_choice: str,
        clusters:    list[ClusterSummary],
    ) -> ClusterSummary | None:
        """Use a simple LLM call to match free-text choice to a cluster."""
        if not clusters:
            return None
        options = "\n".join(
            f"({chr(97+i)}) {c.label}: {c.description[:80]}"
            for i, c in enumerate(clusters)
        )
        prompt = (
            f"A user was asked to choose between these options:\n{options}\n\n"
            f"They responded: \"{user_choice}\"\n\n"
            f"Which option did they choose? Reply with just the letter a, b, or c."
        )
        raw    = self._call_llm(prompt, self.clf_model, max_tokens=5)
        letter = raw.strip().lower()[:1]
        idx    = ord(letter) - ord('a')
        if 0 <= idx < len(clusters):
            return clusters[idx]
        return None

    # ── Fast path ──────────────────────────────────────────────────────────

    def _fast_classify(
        self,
        query:   str,
        session: SessionContext,
    ) -> QueryIntent | None:
        """
        Pattern-match fast path for explicit, unambiguous queries.
        Also catches high-confidence practitioner phrases.
        Returns None if fast classification is not possible.
        """
        # Check practitioner phrases first — these are unambiguous
        for pattern, qtype_str, primary_refs in CLEAR_INTENT_PHRASES:
            if pattern.search(query):
                qtype_map = {
                    "gap_analysis":       QuestionType.GAP_ANALYSIS,
                    "implementation":     QuestionType.IMPLEMENTATION,
                    "definition":         QuestionType.DEFINITION,
                    "posture_check":      QuestionType.POSTURE_CHECK,
                    "document_content":   QuestionType.DOCUMENT_CONTENT,
                    "document_inventory": QuestionType.DOCUMENT_INVENTORY,
                    "cross_framework":    QuestionType.CROSS_FRAMEWORK,
                }
                qtype = qtype_map.get(qtype_str, QuestionType.GAP_ANALYSIS)
                needs_posture = qtype in (
                    QuestionType.GAP_ANALYSIS,
                    QuestionType.POSTURE_CHECK,
                )
                # Phrase match is precise — use only the matched refs
                # Never append stale session.active_refs here
                resolved = list(dict.fromkeys(primary_refs))[:8]
                return QueryIntent(
                    question_type   = qtype,
                    standards_scope = session.standards,
                    role_filter     = session.role,
                    needs_posture   = needs_posture,
                    cited_refs      = primary_refs,
                    resolved_refs   = resolved,
                    confidence      = 0.88,
                    raw_query       = query,
                )

        refs = [r[0] for r in EXPLICIT_REF_PATTERN.findall(query)]
        if not refs:
            return None

        # Determine question type from verbs
        qtype = self._infer_question_type(query)
        if qtype == QuestionType.UNKNOWN:
            return None   # has refs but unclear intent — use LLM

        needs_posture = qtype in (
            QuestionType.GAP_ANALYSIS,
            QuestionType.POSTURE_CHECK,
        )
        # cited_refs (explicit refs in query) dominate — don't dilute with stale session refs
        resolved = list(dict.fromkeys(refs))[:8]

        return QueryIntent(
            question_type   = qtype,
            standards_scope = session.standards,
            role_filter     = session.role,
            needs_posture   = needs_posture,
            cited_refs      = refs,
            resolved_refs   = resolved,
            confidence      = 0.95,
            raw_query       = query,
        )

    def _infer_question_type(self, text: str) -> QuestionType:
        """Infer question type from verb patterns — no LLM."""
        if DEFINITION_VERBS.search(text):
            return QuestionType.DEFINITION
        if GAP_VERBS.search(text):
            return QuestionType.GAP_ANALYSIS
        if POSTURE_VERBS.search(text):
            return QuestionType.POSTURE_CHECK
        if IMPLEMENTATION_VERBS.search(text):
            return QuestionType.IMPLEMENTATION
        return QuestionType.UNKNOWN

    # ── Session builder ────────────────────────────────────────────────────

    def _build_session(
        self,
        user_input:       str,
        primary_cluster:  ClusterSummary,
        question_type:    QuestionType,
    ) -> SessionContext:
        """Build a SessionContext from a resolved cluster."""
        # Extract vocabulary from user input
        words = [w.lower() for w in re.findall(r'\b\w{4,}\b', user_input)]

        return SessionContext(
            tenant_profile  = self.tenant,
            standards       = [primary_cluster.standard],
            role            = self.tenant.role[0] if self.tenant.role else None,
            intent_type     = question_type,
            active_refs     = primary_cluster.top_refs[:3],
            active_cluster  = primary_cluster.label,
            user_vocabulary = words[:20],
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _format_clusters_for_prompt(
        self,
        clusters: list[ClusterSummary],
    ) -> str:
        """Format cluster summaries for LLM prompt injection."""
        lines = []
        for i, c in enumerate(clusters):
            lines.append(
                f"Topic {chr(65+i)} — {c.label} (relevance: {c.avg_score:.2f})\n"
                f"  Covers: {', '.join(c.top_refs[:3])}\n"
                f"  About: {c.description}"
            )
        return "\n\n".join(lines)

    def _call_llm(
        self,
        prompt:     str,
        model:      str,
        max_tokens: int = 200,
        step:       str = "classify",
    ) -> str:
        """Call OpenAI with a single user message. Returns raw text."""
        import time as _time
        client = self._get_openai()
        _t0 = _time.time()
        try:
            response = client.chat.completions.create(
                model       = model,
                temperature = self.temperature,
                max_tokens  = max_tokens,
                messages    = [{"role": "user", "content": prompt}],
            )
            result = response.choices[0].message.content.strip()
            _logger = get_logger()
            if _logger:
                _logger.log_call(
                    step       = step,
                    model      = model,
                    system     = "",
                    user       = prompt[:600],
                    response   = result,
                    latency_ms = round((_time.time() - _t0) * 1000),
                )
            return result
        except Exception as e:
            return f"[LLM error: {e}]"

    def _parse_json(self, raw: str) -> dict | None:
        """Parse JSON from LLM response, stripping markdown fences."""
        clean = re.sub(r'```(?:json)?\s*', '', raw).strip().rstrip('`').strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Try extracting a JSON object
            m = re.search(r'\{.*\}', clean, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        return None

    def _get_openai(self):
        """Lazy-load OpenAI-compatible client (local Mistral or cloud GPT)."""
        if self._openai is None:
            import openai
            local_url = os.getenv("LOCAL_LLM_BASE_URL")
            if local_url:
                # Local Mistral via vLLM/llama.cpp
                self._openai = openai.OpenAI(
                    base_url = local_url.rstrip("/"),
                    api_key  = "local",
                )
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise RuntimeError(
                        "Neither LOCAL_LLM_BASE_URL nor OPENAI_API_KEY is set.\n"
                        "  For local Mistral: export LOCAL_LLM_BASE_URL=http://localhost:9000/v1\n"
                        "  For cloud:         export OPENAI_API_KEY=sk-..."
                    )
                self._openai = openai.OpenAI(api_key=api_key)
        return self._openai
from rag.chain_logger    import get_logger
