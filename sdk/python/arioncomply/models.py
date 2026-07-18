"""
Pydantic response models for the ArionComply external API.

These mirror the server-side models in `rag/external/endpoints/*.py`
so that consumers get typed access to every response field.

Kept in sync manually — if the server-side model changes, this
file needs a matching update. A future generator could derive
these from the OpenAPI JSON automatically.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── /status ───────────────────────────────────────────────────────────

class RateLimitState(BaseModel):
    limit:       int
    remaining:   int
    reset_epoch: int


class StatusResponse(BaseModel):
    ok:                   bool
    tenant_id:            str
    tenant_display_name:  Optional[str] = None
    queryable_standards:  list[str]
    scopes:               list[str]
    rate_limit:           RateLimitState
    server_time:          str


# ── /query ────────────────────────────────────────────────────────────

class Citation(BaseModel):
    ref:      str
    standard: Optional[str] = None
    posture:  Optional[str] = None


class QueryResponse(BaseModel):
    answer:                 str
    question_type:          Optional[str] = None
    citations:              list[Citation] = []
    session_id:             str
    request_id:             str
    latency_ms:             int
    needs_clarification:    bool = False
    clarification_question: Optional[str] = None


# ── /posture family ───────────────────────────────────────────────────

class FrameworkInfo(BaseModel):
    standard_id:   str
    display_name:  str
    control_count: int


class FrameworksResponse(BaseModel):
    tenant_id:  str
    frameworks: list[FrameworkInfo]


class PostureControl(BaseModel):
    ref:                 str
    standard_id:         str
    finding:             Optional[str] = None
    confirmation_status: Optional[str] = None
    last_updated:        Optional[str] = None
    gap_summary:         Optional[str] = None


class PostureSnapshotResponse(BaseModel):
    tenant_id:               str
    generated_at:            str
    controls:                list[PostureControl]
    summary:                 dict
    total_before_pagination: int


class EngineProposal(BaseModel):
    status:  Optional[str] = None
    finding: Optional[str] = None
    reason:  Optional[str] = None


class PostureControlDetail(BaseModel):
    tenant_id:           str
    ref:                 str
    standard_id:         str
    title:               Optional[str] = None
    finding:             Optional[str] = None
    confirmation_status: Optional[str] = None
    confidence:          Optional[str] = None
    last_updated:        Optional[str] = None
    gap_description:     Optional[str] = None
    action_required:     Optional[str] = None
    engine_proposal:     Optional[EngineProposal] = None


# ── /notifications ────────────────────────────────────────────────────

class Notification(BaseModel):
    id:                    str
    kind:                  str
    title:                 str
    body:                  Optional[str] = None
    severity:              str
    fired_at:              str
    read_at:               Optional[str] = None
    dismissed_at:          Optional[str] = None
    related_entity_kind:   Optional[str] = None
    related_entity_id:     Optional[str] = None
    related_control_ref:   Optional[str] = None
    related_event_type:    Optional[str] = None


class NotificationsSummary(BaseModel):
    total:  int
    unread: int
    urgent: int


class NotificationsResponse(BaseModel):
    tenant_id:               str
    generated_at:            str
    notifications:           list[Notification]
    summary:                 NotificationsSummary
    total_before_pagination: int


# ── /documents + /evidence ────────────────────────────────────────────

class UploadResponse(BaseModel):
    upload_id:           str
    filename:            str
    sha256:              str
    byte_size:           int
    extraction_status:   str
    canonical_upload_id: Optional[str] = None


class DocumentStatus(BaseModel):
    upload_id:         str
    filename:          str
    uploaded_at:       Optional[str] = None
    processed_at:      Optional[str] = None
    extraction_status: str
    extraction_path:   Optional[str] = None
    findings_count:    Optional[int] = None
    doc_type:          Optional[str] = None
    standard_ids:      Optional[list[str]] = None
    error_message:     Optional[str] = None
    token_estimate:    Optional[int] = None
    sha256:            Optional[str] = None
    byte_size:         Optional[int] = None


class EvidenceItem(BaseModel):
    finding_id:         str
    upload_id:          str
    filename:           Optional[str] = None
    status:             str
    confidence:         str
    excerpt:            Optional[str] = None
    inference_source:   Optional[str] = None
    checklist_item_id:  Optional[str] = None
    extracted_at:       Optional[str] = None
    confirmed_at:       Optional[str] = None


class EvidenceResponse(BaseModel):
    tenant_id:    str
    control_ref:  str
    standard_id:  str
    evidence:     list[EvidenceItem]
    count:        int


# ── /cascade + /bridges ───────────────────────────────────────────────

class CascadeEvent(BaseModel):
    kind:                   str
    id:                     str
    ts:                     str
    event_type:             str
    expected_action:        Optional[str] = None
    control_ref:            Optional[str] = None
    standard_id:            Optional[str] = None
    cascade_path:           Optional[list] = None
    cascade_depth:          Optional[int] = None
    status:                 Optional[str] = None
    resolved_at:            Optional[str] = None
    resolved_evidence_kind: Optional[str] = None
    dismissed_reason:       Optional[str] = None
    rationale:              Optional[str] = None
    due_date:               Optional[str] = None
    clock_anchor:           Optional[str] = None
    scope_kind:             Optional[str] = None
    expected_event_type:    Optional[str] = None
    window_days:            Optional[int] = None
    expires_at:             Optional[str] = None


class CascadeTimelineResponse(BaseModel):
    tenant_id:               str
    generated_at:            str
    since_days:              int
    events:                  list[CascadeEvent]
    summary:                 dict
    total_before_pagination: int


class ImplicationDetail(BaseModel):
    id:                     str
    tenant_id:              str
    fired_at:               str
    source_event_type:      str
    source_verification_id: Optional[str] = None
    expected_action:        str
    target_control_ref:     str
    target_standard_id:     str
    target_requirement_id:  str
    cascade_path:           list
    cascade_depth:          int
    status:                 str
    resolved_at:            Optional[str] = None
    resolved_by:            Optional[str] = None
    resolved_evidence_kind: Optional[str] = None
    resolved_evidence_id:   Optional[str] = None
    dismissed_reason:       Optional[str] = None
    rationale:              Optional[str] = None
    deadline_string:        Optional[str] = None
    due_date:               Optional[str] = None
    scope_kind:             Optional[str] = None
    clock_anchor:           str


class Bridge(BaseModel):
    id:          str
    ref:         Optional[str] = None
    standard_id: Optional[str] = None
    title:       Optional[str] = None
    rel:         str


class BridgesResponse(BaseModel):
    source_id:   str
    control_ref: str
    standard_id: str
    outbound:    list[Bridge]
    inbound:     list[Bridge]
