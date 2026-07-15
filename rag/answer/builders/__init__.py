"""Per-taxonomy AnswerPayload builders.

Each builder is a pure function:
    build(intent, tenant_context, resolver, neo_driver=None,
          chroma_retriever=None) -> AnswerPayloadBase

Builders own their data-fetch shape. They read from resolver output
(GraphResult + posture) and produce a typed payload. No LLM in the
builder path.

Builders don't self-register — the dispatcher explicitly imports and
maps each into `_BUILDERS`. This keeps the wiring in one place and
avoids circular imports.
"""
