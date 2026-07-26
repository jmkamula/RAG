---
name: ship-44-prime-a-addendum-llm-instrumentation-2026-07-26
description: "Ship 44'.a addendum — adopt OpenLLMetry (Traceloop) for LLM/LangGraph/Chroma auto-instrumentation + OTel GenAI semantic conventions for portability + 3-tier OTEL_PRIVACY_LEVEL (off / observability / debug). Supersedes Ship 44'.a's plan to hand-roll LLM spans. Ship 44'.b installs via pip; Traceloop init supersedes ~150 LOC of custom LLM instrumentation."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 44'.a addendum after community research. Three decisions
locked; supersedes the LLM-specific portions of the original
44'.a memo.

## Decision 1 — adopt OpenLLMetry for LLM stack

Instead of hand-rolling LLM spans in `rag/llm_client.py` and
per-node spans in `rag/arion_graph.py`, install the community
Traceloop instrumentations:

- `opentelemetry-instrumentation-openai` — auto-spans on every
  OpenAI SDK call (Chat, Embeddings, etc.) with model, tokens,
  latency
- `opentelemetry-instrumentation-langchain` — auto-spans on
  LangChain + **LangGraph** node execution. Arion's chat
  pipeline is LangGraph-based (`arion_graph.py`), so this
  auto-covers classify/retrieve/rank_and_answer node timings
  without manual `tracer.start_as_current_span` boilerplate.
- `opentelemetry-instrumentation-chromadb` — auto-spans on
  Chroma queries (used by consensus's `must_semantic_topk` +
  `per_protocol_scope` + chat retrieval).

These emit spans conforming to OpenTelemetry **Semantic
Conventions for Generative AI** (`gen_ai.system`,
`gen_ai.request.model`, `gen_ai.usage.input_tokens`,
`gen_ai.prompt.{n}.content`, etc.). Portable to any OTel-native
LLM observability tool (Jaeger, Arize Phoenix, Langfuse, Grafana
Tempo, Honeycomb) without rewriting spans.

**What stays hand-rolled**:
- `rag/intake/consensus_extraction/orchestrator.py` — per-signal
  spans + aggregator decision (no community instrumentation for
  our consensus pipeline)
- `rag/posture/fulfilment_engine.py::compute_engine_verdicts`
  — engine verdict computation
- `rag/posture_loader.py::load_posture` — posture load
- `rag/intake/posture_writer.py::write_findings` — write
- `rag/casefile/{digest,preservation,repair}.py` — case-file
  build + preservation-check

These are ArionComply-specific pipeline stages the community
doesn't cover.

## Decision 2 — OTel GenAI semantic conventions

Our custom spans (consensus, engine, writer) use ArionComply-
specific attribute names (`arion.consensus.signal_name`,
`arion.engine.control_ref`, etc.).

LLM + LangGraph + Chroma spans (auto-instrumented) use
**`gen_ai.*` semantic conventions** — the emerging OTel standard
that Traceloop, Arize, Langfuse, Datadog, Honeycomb all target.

Two attribute namespaces coexist:
- `arion.*` — proprietary (consensus, engine, writer semantics
  the community doesn't standardize)
- `gen_ai.*` — community (LLM calls, LangChain/LangGraph, vector
  DB queries)

Portability benefit: if we later swap Jaeger for Arize Phoenix
(LLM-first UI) or Langfuse (LLM cost dashboards), the `gen_ai.*`
spans render natively without any changes to our code.

## Decision 3 — 3-tier privacy levels

New env var: `OTEL_PRIVACY_LEVEL={off,observability,debug}`.

| Tier | Purpose | What's captured |
|---|---|---|
| **off** | Disable tracing entirely | Nothing |
| **observability** | Prod / prod-like | Request paths, method, endpoint, latency, DB query templates (no bind params), LLM model + purpose + token counts, span counts, error status. **NO** query strings, LLM prompts, LLM completions, evidence excerpts. |
| **debug** | Internal engineering only | Everything in observability **plus** truncated content (500c cap) on chat queries + LLM prompts + LLM completions + evidence excerpts. Sensitive data flows here — never enable on production. |

**Default**: `observability`. Safe by default.

**Implementation**:
1. `OTEL_ENABLED=1` gates whether OTel runs at all
2. `OTEL_PRIVACY_LEVEL` sets the tier when enabled
3. Traceloop's `TRACELOOP_TRACE_CONTENT` env is set true/false
   based on tier (`true` only when debug)
4. Our custom span code checks `_privacy_level_capture_content()`
   before adding content attributes
5. All content attributes truncate to 500c even in debug

## Package changes (Ship 44'.b implementation)

Original 44'.a plan:
```
pip install opentelemetry-instrumentation-{fastapi,psycopg2,httpx,requests}
```

Updated Ship 44'.b plan:
```
pip install opentelemetry-instrumentation-{fastapi,psycopg2,httpx,requests}
pip install opentelemetry-instrumentation-openai
pip install opentelemetry-instrumentation-langchain
pip install opentelemetry-instrumentation-chromadb
```

Not installing the meta `traceloop-sdk` — too much magic, and
we want explicit control over which instrumentations register
so we don't accidentally enable a downstream one on data we
haven't classified for the privacy tiers.

## rag/telemetry.py updates

Original 44'.a `rag/telemetry.py` bootstrap plan gains:

```python
def _privacy_level() -> str:
    return os.getenv("OTEL_PRIVACY_LEVEL", "observability").lower()

def _capture_content() -> bool:
    """Return True when spans may include content attributes
    (chat query text, LLM prompts, evidence excerpts). Set by
    OTEL_PRIVACY_LEVEL=debug. Guard EVERY content-attribute
    write with this."""
    return _privacy_level() == "debug"

def bootstrap_telemetry():
    if os.getenv("OTEL_ENABLED", "0") != "1":
        return

    # Traceloop captures LLM prompt/completion when this env is true
    os.environ["TRACELOOP_TRACE_CONTENT"] = (
        "true" if _capture_content() else "false"
    )
    # ...set up tracer provider, register auto-instrumentations, etc.
```

Every custom span that would write chat query text, LLM prompt,
or evidence excerpt content wraps the attribute set with:

```python
if telemetry.capture_content():
    span.set_attribute("arion.chat.query", query[:500])
```

Never captures content unconditionally.

## Ship 44'.c-.d scope changes

Original 44'.c planned LLM spans in `llm_client.py` — that
work is now covered by `opentelemetry-instrumentation-openai`.

Revised Ship 44'.c scope: **consensus_extraction orchestrator**
spans only. Signal fires, aggregator counts, arbiter calls.

Revised Ship 44'.d scope: **engine + posture writer + case-file**
spans only. LangGraph nodes are covered by
`opentelemetry-instrumentation-langchain`; we don't add manual
spans on them.

Net effect: Ship 44 ships FASTER because Traceloop covers
~150 LOC of what we'd have hand-rolled.

## What Ship 44 does NOT do (unchanged)

- Metrics (Ship 45+)
- Logs OTel exporter
- Trace-log correlation
- Persistent Jaeger storage (in-memory sufficient for demo)

## Related

- [[ship-44-prime-a-otel-jaeger-design-2026-07-26]] — the
  original design memo this addendum supersedes for LLM
  instrumentation choice
- OpenTelemetry Semantic Conventions for GenAI —
  the community standard `gen_ai.*` attribute names conform to
- OpenLLMetry (Traceloop) — the community-maintained
  auto-instrumentations we adopt

## Confirmation of Ship 44'.b plan

1. Install Jaeger v1.63+ binary + systemd unit + install script
2. `pip install --break-system-packages
   opentelemetry-instrumentation-{fastapi,psycopg2,httpx,requests,openai,langchain,chromadb}`
3. Write `rag/telemetry.py` with `bootstrap_telemetry()` +
   `capture_content()` helper + privacy-tier gating
4. Wire into `api_server.py` startup event
5. Set `OTEL_ENABLED=1` + `OTEL_PRIVACY_LEVEL=debug` on Arion
   demo (VM is internal engineering only)
6. Restart API + verify traces in Jaeger UI
