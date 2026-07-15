"""
Ship 2: AnswerPayload — deterministic content assembly.

The design principle carried from Ship 1: deterministic signals
lead, LLM fills gaps. Ship 1 handled intent classification; Ship 2
handles CONTENT ASSEMBLY. Given (question_type, refs, framework)
from Ship 1's consensus, per-taxonomy builders assemble a typed
AnswerPayload with every ref, finding, and bridge that MUST appear
in the answer. No LLM in the builder path.

Ship 3 (later) constrains the prose layer with preservation checks
over the AnswerPayload. Ship 2 alone renders raw templates as a
fallback; the current rank_and_answer LLM continues to write prose
with the payload as extra structured context (additive, not
replacing).

Public surface:
    dispatch_builder(intent, tenant_context, resolver, ...) -> AnswerPayloadBase
    validate(payload, tenant_context) -> ValidationReport
    from rag.answer.types import (
        AnswerPayloadBase, PostureStatusPayload, DocumentContentPayload,
        DocumentStatusPayload, RemediationGuidePayload,
        StandardKnowledgePayload, CrossFrameworkPayload, FreeformPayload,
        RefRecord, PostureFacet, BridgeRecord, ChecklistItem,
        DocumentRequirement, GapEntry,
    )
"""
from rag.answer.types import (
    AnswerPayloadBase,
    PostureStatusPayload,
    DocumentStatusPayload,
    RemediationGuidePayload,
    DocumentContentPayload,
    StandardKnowledgePayload,
    CrossFrameworkPayload,
    FreeformPayload,
    RefRecord,
    PostureFacet,
    BridgeRecord,
    ChecklistItem,
    DocumentRequirement,
    GapEntry,
    ValidationReport,
)
from rag.answer.dispatcher import dispatch_builder
from rag.answer.validator  import validate

__all__ = [
    "AnswerPayloadBase",
    "PostureStatusPayload",
    "DocumentStatusPayload",
    "RemediationGuidePayload",
    "DocumentContentPayload",
    "StandardKnowledgePayload",
    "CrossFrameworkPayload",
    "FreeformPayload",
    "RefRecord",
    "PostureFacet",
    "BridgeRecord",
    "ChecklistItem",
    "DocumentRequirement",
    "GapEntry",
    "ValidationReport",
    "dispatch_builder",
    "validate",
]
