"""
RAGOrchestrator — ArionComply RAG Pipeline

Wires all five components into a single callable:
  1. QueryClassifier  — intake / intent resolution / clarification
  2. VectorRetriever  — semantic search over enriched ChromaDB
  3. GraphExpander    — Neo4j traversal (hierarchy + xfw + lateral)
  4. ContextAssembler — structured LLM prompt context
  5. LLMAnswer        — GPT-4o generation + verification pass

Manages:
  - Session lifecycle (first message = intake, subsequent = classify)
  - Clarification loop (returns question without running retrieval)
  - Conversation history (last N turns passed to classifier)
  - PostureLookup (injected — JSON file or future Postgres)

Usage:
    from rag.orchestrator import RAGOrchestrator, OrchestratorConfig

    config = OrchestratorConfig(
        neo4j_uri      = "bolt://127.0.0.1:7687",
        neo4j_user     = "neo4j",
        neo4j_password = "arionneo4j@2026",
        chroma_host    = "localhost",
        chroma_port    = 8000,
        openai_api_key = "sk-proj-...",
    )

    orchestrator = RAGOrchestrator(tenant_profile, config)

    # First message — intake
    response = orchestrator.chat("We had a ransomware attack last week")
    if response.needs_clarification:
        print(response.clarification_question)
    else:
        print(response.answer_text)

    # Follow-up using returned session
    response2 = orchestrator.chat(
        "What do we need to report?",
        session = response.session,
        history = response.updated_history,
    )
    print(response2.answer_text)
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Optional

from rag.classifier      import (
    QueryClassifier, QueryIntent, QuestionType,
    TenantProfile, SessionContext, IntakeState, IntakeResult,
)
from rag.graph_expander  import GraphExpander, ExpandedContext
from rag.context_assembler import ContextAssembler, AssembledContext
from rag.llm_answer      import LLMAnswer, ComplianceAnswer
from vector.retriever    import VectorRetriever


# ── Clarification state ───────────────────────────────────────────────────────

@dataclass
class ClarificationState:
    """
    Tracks clarification attempts per conversational topic.
    Passed back to the caller in OrchestratorResponse and returned
    on the next call so the orchestrator can enforce the limit.
    """
    count:         int       = 0        # clarification attempts on current topic
    topic_hash:    str       = ""       # hash of the original query (topic ID)
    last_node_ids: list[str] = field(default_factory=list)  # best candidate nodes
    MAX:           int       = 2        # max clarifications before forcing answer

    def increment(self, topic_hash: str, node_ids: list[str]) -> "ClarificationState":
        """Return new state with incremented count for same topic."""
        if topic_hash == self.topic_hash:
            return ClarificationState(
                count         = self.count + 1,
                topic_hash    = topic_hash,
                last_node_ids = node_ids or self.last_node_ids,
                MAX           = self.MAX,
            )
        # New topic — reset count
        return ClarificationState(
            count         = 1,
            topic_hash    = topic_hash,
            last_node_ids = node_ids,
            MAX           = self.MAX,
        )

    def exhausted(self) -> bool:
        return self.count >= self.MAX

    def reset(self) -> "ClarificationState":
        return ClarificationState(MAX=self.MAX)


# Override phrases — user wants to skip clarification and get an answer
OVERRIDE_PHRASES = {
    "just answer", "skip", "go ahead", "answer anyway",
    "answer please", "just go", "proceed", "never mind",
    "forget it", "just tell me", "best guess", "any answer",
}


# ── Configuration ──────────────────────────────────────────────────────────────

@dataclass
class OrchestratorConfig:
    """All connection and model configuration in one place."""
    # Neo4j
    neo4j_uri:      str = "bolt://127.0.0.1:7687"
    neo4j_user:     str = "neo4j"
    neo4j_password: str = "arionneo4j@2026"

    # ChromaDB
    chroma_host:    str | None = None        # None = local file mode
    chroma_port:    int        = 8000
    chroma_db_path: str        = "./chroma_db"

    # OpenAI
    openai_api_key:    str = ""              # falls back to OPENAI_API_KEY env
    embedding_model:   str = "text-embedding-3-large"
    answer_model:      str = "gpt-4o"
    clarify_model:     str = "gpt-4o-mini"
    classify_model:    str = "gpt-4o-mini"
    # Note: answer_model/clarify_model/classify_model are overridden
    # at runtime by LOCAL_LLM_MODEL env var in LLMAnswer and QueryClassifier

    # Pipeline behaviour
    verify_answers:    bool = True
    max_history_turns: int  = 6    # conversation turns kept in context

    # Local LLM (Mistral via llama.cpp) — overrides cloud models when set
    local_llm_base_url:  str = ""   # e.g. "http://localhost:8080/v1"
    local_llm_model:     str = ""   # e.g. "mistral-small-3.2-24b"

    def __post_init__(self):
        # Fall back to env vars
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        if not self.chroma_host:
            self.chroma_host = os.getenv("CHROMA_HOST") or None
        if not self.neo4j_password or self.neo4j_password == "arionneo4j@2026":
            env_pass = os.getenv("NEO4J_PASSWORD")
            if env_pass:
                self.neo4j_password = env_pass
        # Local LLM overrides
        if not self.local_llm_base_url:
            self.local_llm_base_url = os.getenv("LOCAL_LLM_BASE_URL", "")
        if not self.local_llm_model:
            self.local_llm_model = os.getenv("LOCAL_LLM_MODEL", "")
        # Propagate local model to answer/classify/clarify models
        if self.local_llm_model:
            self.answer_model   = self.local_llm_model
            self.clarify_model  = self.local_llm_model
            self.classify_model = self.local_llm_model

    @property
    def using_local_llm(self) -> bool:
        return bool(self.local_llm_base_url)


# ── Response dataclass ─────────────────────────────────────────────────────────

@dataclass
class OrchestratorResponse:
    """
    Everything the caller needs from one pipeline run.
    """
    # The answer (None if clarification needed)
    answer_text:           str | None
    needs_clarification:   bool
    clarification_question: str | None

    # Session state — pass back in on next call
    session:               SessionContext | None
    updated_history:       list[dict]

    # Intent and retrieval metadata
    intent:                QueryIntent | None
    question_type:         QuestionType | None
    confidence:            float

    # Pipeline performance
    node_count:            int
    primary_node_count:    int
    neo4j_ms:              int
    total_ms:              int
    model_used:            str

    # Answer quality
    verified:              bool
    was_corrected:         bool
    cited_refs:            list[str]
    posture_findings:      dict

    # Intermediate results (for analytics / debugging)
    expanded:              ExpandedContext | None  = None
    assembled:             AssembledContext | None = None
    answer_obj:            ComplianceAnswer | None = None

    # Clarification tracking — pass back in on next call
    clarification_state:   "ClarificationState | None" = None

    # Error (if pipeline failed)
    error:                 str | None = None


# ── RAGOrchestrator ────────────────────────────────────────────────────────────

class RAGOrchestrator:
    """
    Single entry point for the full ArionComply RAG pipeline.

    Instantiate once per tenant session (or once per deployment
    if PostureLookup is stateless / DB-backed).
    """

    def __init__(
        self,
        tenant_profile:  TenantProfile,
        config:          OrchestratorConfig,
        posture_data:    dict | None  = None,   # {node_id: {finding, gap, ...}}
        document_alerts: list | None  = None,   # from load_document_alerts()
    ):
        self.tenant          = tenant_profile
        self.config          = config
        self.posture         = posture_data    or {}
        self.document_alerts = document_alerts or []

        # Initialise components
        self._retriever  = self._build_retriever()
        self._expander   = self._build_expander()
        self._assembler  = ContextAssembler(tenant_profile)
        self._classifier = QueryClassifier(
            tenant_profile  = tenant_profile,
            retriever       = self._retriever,
            classify_model  = config.classify_model,
            clarify_model   = config.clarify_model,
        )
        self._llm = LLMAnswer(
            answer_model = config.answer_model,
            verify_model = config.clarify_model,
            verify       = config.verify_answers,
        )

    # ── Public API ─────────────────────────────────────────────────────────

    def opening_message(self) -> str:
        """Returns the opening intake message for new sessions."""
        return self._classifier.opening_message()

    def chat(
        self,
        message:               str,
        session:               SessionContext | None       = None,
        history:               list[dict] | None           = None,
        posture:               dict | None                 = None,
        clarification_state:   "ClarificationState | None" = None,
    ) -> OrchestratorResponse:
        """
        Process one conversational turn.

        Args:
            message:              The user's message
            session:              SessionContext from previous turn (None = new)
            history:              Conversation history from previous turns
            posture:              Posture data override (uses instance posture)
            clarification_state:  ClarificationState from previous turn.
                                  Tracks how many times we've asked for
                                  clarification on the current topic.

        Returns:
            OrchestratorResponse — always includes clarification_state
            so the caller can pass it back on the next turn.
        """
        t0      = time.time()
        history = history or []
        posture = posture if posture is not None else self.posture
        cl_state = clarification_state or ClarificationState()

        try:
            # ── Override detection ─────────────────────────────────────────
            # If user says "just answer" / "skip" — force best-effort answer
            if message.lower().strip() in OVERRIDE_PHRASES:
                return self._best_effort_answer(
                    cl_state = cl_state,
                    session  = session,
                    history  = history,
                    posture  = posture,
                    t0       = t0,
                )

            # ── Step 1: Intent resolution ──────────────────────────────────
            if session is None:
                intake = self._classifier.process_intake(message)
                result = self._handle_intake(
                    intake, message, history, posture, t0, cl_state
                )
            else:
                result = self._handle_query(
                    message, session, history, posture, t0, cl_state
                )

            return result

        except Exception as e:
            elapsed = round((time.time() - t0) * 1000)
            return OrchestratorResponse(
                answer_text            = None,
                needs_clarification    = False,
                clarification_question = None,
                session                = session,
                updated_history        = history,
                intent                 = None,
                question_type          = None,
                confidence             = 0.0,
                node_count             = 0,
                primary_node_count     = 0,
                neo4j_ms               = 0,
                total_ms               = elapsed,
                model_used             = self.config.answer_model,
                verified               = False,
                was_corrected          = False,
                cited_refs             = [],
                posture_findings       = {},
                error                  = str(e),
            )

    def process_clarification(
        self,
        user_choice:   str,
        prior_intake:  IntakeResult,
        history:       list[dict] | None = None,
        posture:       dict | None       = None,
    ) -> OrchestratorResponse:
        """
        Process the user's response to a clarification question.
        Called when a previous chat() returned needs_clarification=True.
        """
        t0      = time.time()
        history = history or []
        posture = posture if posture is not None else self.posture

        resolved = self._classifier.process_clarification(
            user_choice, prior_intake
        )

        if resolved.state == IntakeState.CLEAR and resolved.session:
            # Now we have a session — run the pipeline
            return self._run_pipeline(
                query   = prior_intake.raw_input,
                session = resolved.session,
                history = history,
                posture = posture,
                t0      = t0,
            )

        # Still ambiguous
        return self._clarification_response(
            question = resolved.clarification or "Could you clarify further?",
            session  = None,
            history  = history,
            t0       = t0,
        )

    # ── Intake and query handlers ───────────────────────────────────────────

    def _handle_intake(
        self,
        intake:   IntakeResult,
        message:  str,
        history:  list[dict],
        posture:  dict,
        t0:       float,
        cl_state: "ClarificationState | None" = None,
    ) -> OrchestratorResponse:
        """Handle the first message in a new session."""
        cl_state = cl_state or ClarificationState()

        if intake.state == IntakeState.AMBIGUOUS:
            candidate_ids = [
                f"{c.standard}:{ref}"
                for c in (intake.clusters or [])
                for ref in (c.top_refs or [])
            ]
            # Increment count — topic_hash irrelevant, just count turns
            # Store original message in topic_hash on first attempt
            new_cl = ClarificationState(
                count         = cl_state.count + 1,
                topic_hash    = cl_state.topic_hash or message,
                last_node_ids = candidate_ids or cl_state.last_node_ids,
                MAX           = cl_state.MAX,
            )

            if new_cl.exhausted():
                return self._best_effort_answer(
                    cl_state       = new_cl,
                    session        = None,
                    history        = history,
                    posture        = posture,
                    t0             = t0,
                    original_query = cl_state.topic_hash or message,
                )

            return self._clarification_response(
                question  = intake.clarification,
                session   = None,
                history   = history,
                t0        = t0,
                cl_state  = new_cl,
            )

        if intake.state == IntakeState.NO_MATCH:
            new_cl = ClarificationState(
                count         = cl_state.count + 1,
                topic_hash    = cl_state.topic_hash or message,
                last_node_ids = cl_state.last_node_ids,
                MAX           = cl_state.MAX,
            )
            if new_cl.exhausted():
                return self._best_effort_answer(
                    cl_state       = new_cl,
                    session        = None,
                    history        = history,
                    posture        = posture,
                    t0             = t0,
                    original_query = cl_state.topic_hash or message,
                )
            return self._clarification_response(
                question  = intake.clarification,
                session   = None,
                history   = history,
                t0        = t0,
                cl_state  = new_cl,
            )

        # CLEAR or EXPLICIT — run pipeline, reset counter
        session = intake.session
        return self._run_pipeline(
            message, session, history, posture, t0,
            cl_state=ClarificationState(),
        )

    def _handle_query(
        self,
        message:  str,
        session:  SessionContext,
        history:  list[dict],
        posture:  dict,
        t0:       float,
        cl_state: "ClarificationState | None" = None,
    ) -> OrchestratorResponse:
        """Handle a follow-up query within an established session."""
        cl_state = cl_state or ClarificationState()
        intent   = self._classifier.classify_query(message, session, history)

        if intent.clarification_question:
            new_cl = ClarificationState(
                count         = cl_state.count + 1,
                topic_hash    = cl_state.topic_hash or "query",
                last_node_ids = cl_state.last_node_ids,
                MAX           = cl_state.MAX,
            )

            if new_cl.exhausted():
                return self._best_effort_answer(
                    cl_state       = new_cl,
                    session        = session,
                    history        = history,
                    posture        = posture,
                    t0             = t0,
                    original_query = message,
                )

            return self._clarification_response(
                question  = intent.clarification_question,
                session   = session,
                history   = history,
                t0        = t0,
                cl_state  = new_cl,
            )

        # Clear intent — reset count
        # Only update session with refs from THIS query, not stale session refs
        session.update_refs(intent.cited_refs or intent.resolved_refs[:3])

        return self._run_pipeline(
            query    = message,
            session  = session,
            history  = history,
            posture  = posture,
            t0       = t0,
            intent   = intent,
            cl_state = ClarificationState(),
        )

    # ── Core pipeline ──────────────────────────────────────────────────────

    def _run_pipeline(
        self,
        query:    str,
        session:  SessionContext,
        history:  list[dict],
        posture:  dict,
        t0:       float,
        intent:   QueryIntent | None          = None,
        cl_state: "ClarificationState | None" = None,
    ) -> OrchestratorResponse:
        """
        Run the full retrieval → expansion → assembly → answer pipeline.
        """
        # ── Step 2: Intent (if not already resolved) ───────────────────────
        if intent is None:
            intent = self._classifier.classify_query(query, session, history)
            if intent.clarification_question:
                return self._clarification_response(
                    intent.clarification_question, session, history, t0
                )

        # ── Step 3: Vector retrieval ───────────────────────────────────────
        search_results = self._retriever.search(
            query     = query,
            n         = 15,
            standards = intent.standards_scope,
        )

        # Combine cited refs with vector results for expansion
        # When we have explicit cited_refs (phrase match or explicit ref query),
        # put them first and limit vector results to avoid flooding the context.
        # When no cited refs, use full vector results.
        anchor_refs = intent.cited_refs if intent.cited_refs else intent.resolved_refs
        cited_node_ids = [
            f"{s}:{r}"
            for s in intent.standards_scope
            for r in anchor_refs
            if self._node_exists(s, r)
        ]
        # Limit vector results when we have strong cited refs — prevents
        # irrelevant vector matches from displacing the primary focus nodes
        vector_node_ids = search_results.node_ids()
        if cited_node_ids:
            # Strong signal — take only top 5 vector results as supplementary
            vector_node_ids = vector_node_ids[:5]
        node_ids = list(dict.fromkeys(
            cited_node_ids +
            vector_node_ids
        ))[:15]

        # ── Step 4: Graph expansion ────────────────────────────────────────
        t_neo4j = time.time()
        expanded = self._expander.expand(node_ids, intent)
        neo4j_ms = round((time.time() - t_neo4j) * 1000)

        # ── Step 5: Context assembly ───────────────────────────────────────
        assembled = self._assembler.assemble(
            expanded         = expanded,
            intent           = intent,
            posture          = posture,
            document_alerts  = self.document_alerts,
        )

        # ── Step 6: LLM answer + verification ─────────────────────────────
        answer = self._llm.answer(query, assembled)

        # ── Update history ─────────────────────────────────────────────────
        updated_history = self._update_history(history, query, answer.answer_text)

        # ── Update session ─────────────────────────────────────────────────
        # Use query's cited_refs as the session anchor — not answer.cited_refs
        # (answer refs include tangential controls the LLM mentioned,
        # which pollute the next query's context)
        # Fall back to answer refs only if no cited refs in the query
        session_refs = intent.cited_refs if intent.cited_refs else answer.cited_refs[:3]
        session.update_refs(session_refs)

        total_ms = round((time.time() - t0) * 1000)

        return OrchestratorResponse(
            answer_text            = answer.answer_text,
            needs_clarification    = False,
            clarification_question = None,
            session                = session,
            updated_history        = updated_history,
            intent                 = intent,
            question_type          = intent.question_type,
            confidence             = intent.confidence,
            node_count             = expanded.total_nodes,
            primary_node_count     = len(expanded.primary_nodes),
            neo4j_ms               = neo4j_ms,
            total_ms               = total_ms,
            model_used             = self.config.answer_model,
            verified               = answer.verified,
            was_corrected          = answer.was_corrected,
            cited_refs             = answer.cited_refs,
            posture_findings       = answer.posture_findings,
            clarification_state    = cl_state or ClarificationState(),
            expanded               = expanded,
            assembled              = assembled,
            answer_obj             = answer,
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _best_effort_answer(
        self,
        cl_state:       "ClarificationState",
        session:        SessionContext | None,
        history:        list[dict],
        posture:        dict,
        t0:             float,
        original_query: str = "",
    ) -> OrchestratorResponse:
        """
        Force an answer after clarification limit is reached or user overrides.

        Uses the last known candidate node IDs from ClarificationState,
        or falls back to a broad vector search on the original query.
        Prefixes the answer with a note explaining the best-effort nature.
        """
        node_ids = cl_state.last_node_ids

        # If no candidate nodes, do a broad vector search
        if not node_ids and original_query:
            results  = self._retriever.search(
                original_query,
                n         = 10,
                standards = self.tenant.applicable_standards,
            )
            node_ids = results.node_ids()[:10]

        # Need a session to run the pipeline
        if session is None and node_ids:
            # Build a minimal session from the candidate nodes
            from rag.classifier import SessionContext
            session = SessionContext(
                tenant_profile = self.tenant,
                standards      = self.tenant.applicable_standards,
                role           = self.tenant.role[0] if self.tenant.role else None,
                intent_type    = None,
                active_refs    = [],
                active_cluster = None,
            )

        if not node_ids or session is None:
            # Absolute fallback — nothing to work with
            total_ms = round((time.time() - t0) * 1000)
            return OrchestratorResponse(
                answer_text            = (
                    "I wasn't able to find a specific match for your question "
                    "in the ISO 27001 and GDPR knowledge base. Could you try "
                    "rephrasing — for example, mentioning a specific article "
                    "number (Art.32, Art.33) or control (A.8.24), or describing "
                    "what you're trying to achieve?"
                ),
                needs_clarification    = False,
                clarification_question = None,
                session                = session,
                updated_history        = history,
                intent                 = None,
                question_type          = None,
                confidence             = 0.0,
                node_count             = 0,
                primary_node_count     = 0,
                neo4j_ms               = 0,
                total_ms               = total_ms,
                model_used             = self.config.answer_model,
                verified               = False,
                was_corrected          = False,
                cited_refs             = [],
                posture_findings       = {},
                clarification_state    = cl_state.reset(),
            )

        # Use classifier.answer_best_effort to build a proper intent
        # from whatever node IDs we have — no further LLM classification
        intent = self._classifier.answer_best_effort(
            node_ids       = node_ids,
            session        = session,
            original_query = original_query or "",
        )

        response = self._run_pipeline(
            query    = original_query or "Tell me about our compliance obligations",
            session  = session,
            history  = history,
            posture  = posture,
            t0       = t0,
            intent   = intent,
            cl_state = cl_state.reset(),
        )

        # Prepend a note so the user knows this is best-effort
        if response.answer_text:
            note = (
                "*Based on my best understanding of your question:*\n\n"
            )
            response.answer_text = note + response.answer_text

        return response

    def _clarification_response(
        self,
        question:  str,
        session:   SessionContext | None,
        history:   list[dict],
        t0:        float,
        cl_state:  "ClarificationState | None" = None,
    ) -> OrchestratorResponse:
        """Build a clarification-only response."""
        total_ms  = round((time.time() - t0) * 1000)
        cl_state  = cl_state or ClarificationState()
        remaining = cl_state.MAX - cl_state.count

        # Append remaining attempts note to question
        if remaining == 1:
            question = (
                question.rstrip() +
                "\n\n(If this still isn't clear, just say 'just answer' "
                "and I'll give you my best answer.)"
            )

        return OrchestratorResponse(
            answer_text            = None,
            needs_clarification    = True,
            clarification_question = question,
            session                = session,
            updated_history        = history,
            intent                 = None,
            question_type          = None,
            confidence             = 0.0,
            node_count             = 0,
            primary_node_count     = 0,
            neo4j_ms               = 0,
            total_ms               = total_ms,
            model_used             = self.config.clarify_model,
            verified               = False,
            was_corrected          = False,
            cited_refs             = [],
            posture_findings       = {},
            clarification_state    = cl_state,
        )

    def _update_history(
        self,
        history:     list[dict],
        user_msg:    str,
        assistant_msg: str,
    ) -> list[dict]:
        """Append turn to history, trim to max_history_turns."""
        updated = history + [
            {"role": "user",      "content": user_msg},
            {"role": "assistant", "content": assistant_msg or ""},
        ]
        # Keep last N complete turns (each turn = 2 messages)
        max_messages = self.config.max_history_turns * 2
        return updated[-max_messages:]

    def _node_exists(self, standard_id: str, ref: str) -> bool:
        """
        Check if a ref is likely valid before building node ID.
        Simple heuristic — proper node existence check is in ChromaDB.
        """
        if standard_id == "GDPR:2016/679":
            return ref.startswith("Art.")
        if standard_id == "ISO27001:2022":
            return (ref.startswith("A.") or
                    bool(__import__('re').match(r'^\d+\.\d', ref)))
        return False

    # ── Component builders ─────────────────────────────────────────────────

    def _build_retriever(self) -> VectorRetriever:
        cfg = self.config
        return VectorRetriever(
            persist_dir     = cfg.chroma_db_path,
            provider        = "openai",
            embedding_model = cfg.embedding_model,
            chroma_host     = cfg.chroma_host,
            chroma_port     = cfg.chroma_port,
        )

    def _build_expander(self) -> GraphExpander:
        cfg = self.config
        return GraphExpander(
            neo4j_uri      = cfg.neo4j_uri,
            neo4j_user     = cfg.neo4j_user,
            neo4j_password = cfg.neo4j_password,
            retriever      = self._retriever,
        )
