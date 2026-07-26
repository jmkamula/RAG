"""ArionComply telemetry — OpenTelemetry SDK bootstrap + privacy tiers.

Ship 44 arc. Sets up distributed tracing to two OSS backends:

- **Jaeger** (127.0.0.1:4317, UI 16686) — general trace UI, service
  map, dependency graph, DB + HTTP + FastAPI spans.
- **Arize Phoenix** (127.0.0.1:6317, UI 6006) — LLM-first UI with
  prompt/completion viewer, RAG eval framework. Ingests
  `gen_ai.*` semantic-convention spans natively.

Both consume OTLP; SDK exports to both simultaneously via
BatchSpanProcessor * 2.

## Environment configuration

- `OTEL_ENABLED=1` — gates whether OTel runs at all (default off)
- `OTEL_PRIVACY_LEVEL={off,observability,debug}` — content
  gating tier (default: observability)
- `OTEL_JAEGER_ENDPOINT` — override Jaeger endpoint
  (default `http://127.0.0.1:4317`)
- `OTEL_PHOENIX_ENDPOINT` — override Phoenix endpoint
  (default `http://127.0.0.1:6317`)
- `OTEL_SERVICE_NAME` — service name in spans
  (default `arioncomply-api`)

## Privacy tiers

- **off**: OTel disabled entirely
- **observability** (default): paths, latencies, model names,
  token counts, DB query templates. **NO** content (query
  strings, prompts, completions, evidence excerpts).
- **debug**: everything in observability plus truncated content
  (500 char cap) — internal engineering only, never on production.

## Usage from custom spans

```python
from rag.telemetry import get_tracer, capture_content

tracer = get_tracer(__name__)

with tracer.start_as_current_span("consensus.run") as span:
    span.set_attribute("arion.consensus.doc_name", doc.name)
    if capture_content():
        span.set_attribute("arion.consensus.query", query[:500])
    result = run_consensus(...)
    span.set_attribute("arion.consensus.n_accept", result.n_accept)
```
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


_INITIALIZED = False


def _privacy_level() -> str:
    return os.getenv("OTEL_PRIVACY_LEVEL", "observability").lower()


def capture_content() -> bool:
    """Return True when spans may include content attributes
    (chat query text, LLM prompts, evidence excerpts). Guard EVERY
    content-attribute write with this — never capture content
    unconditionally.

    Returns True only when `OTEL_PRIVACY_LEVEL=debug`."""
    return _privacy_level() == "debug"


def _content_cap() -> int:
    """Max chars for any content attribute. Guards against
    accidental full-document dumps in spans."""
    return 500


def _truncate(s: Optional[str]) -> Optional[str]:
    """Apply content_cap + ellipsis marker so downstream systems
    know the value was truncated."""
    if s is None:
        return None
    cap = _content_cap()
    if len(s) <= cap:
        return s
    return s[:cap] + "…[truncated]"


def get_tracer(name: str):
    """Return an OTel Tracer for the given module name. Safe to
    call before bootstrap — returns a no-op tracer until OTel is
    initialized."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except Exception:
        # Fallback: OTel not available → NoOpTracer via a shim
        class _NoOp:
            def start_as_current_span(self, *a, **kw):
                from contextlib import contextmanager
                @contextmanager
                def _ctx():
                    yield _NoOpSpan()
                return _ctx()
        class _NoOpSpan:
            def set_attribute(self, *a, **kw): pass
            def add_event(self, *a, **kw): pass
            def set_status(self, *a, **kw): pass
        return _NoOp()


def bootstrap_telemetry(fastapi_app=None) -> None:
    """Initialise OTel providers + register auto-instrumentation.

    Called once from api_server.py startup event. Idempotent.
    Silent-fail on backend unreachable — API never blocks on
    telemetry.

    Args:
        fastapi_app: FastAPI app instance for FastAPI
            auto-instrumentation. If None, FastAPI instrumentation
            is skipped (other instrumentations still run).
    """
    global _INITIALIZED
    if _INITIALIZED:
        return

    if os.getenv("OTEL_ENABLED", "0") != "1":
        logger.info("telemetry: OTEL_ENABLED != 1 — skipping OTel bootstrap")
        return

    level = _privacy_level()
    if level == "off":
        logger.info("telemetry: OTEL_PRIVACY_LEVEL=off — skipping OTel bootstrap")
        return

    logger.info(f"telemetry: initializing OTel with privacy_level={level}")

    # Traceloop / OpenLLMetry / OpenInference content-capture env:
    # only capture LLM prompts + completions when privacy_level=debug.
    if level == "debug":
        os.environ.setdefault("TRACELOOP_TRACE_CONTENT", "true")
        os.environ.setdefault("OPENINFERENCE_HIDE_INPUTS", "false")
        os.environ.setdefault("OPENINFERENCE_HIDE_OUTPUTS", "false")
    else:
        os.environ["TRACELOOP_TRACE_CONTENT"] = "false"
        os.environ["OPENINFERENCE_HIDE_INPUTS"] = "true"
        os.environ["OPENINFERENCE_HIDE_OUTPUTS"] = "true"
        os.environ["OPENINFERENCE_HIDE_INPUT_MESSAGES"] = "true"
        os.environ["OPENINFERENCE_HIDE_OUTPUT_MESSAGES"] = "true"

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
    except Exception as e:
        logger.warning(f"telemetry: OTel SDK import failed: {e} — skipping")
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "arioncomply-api")
    resource = Resource.create({
        "service.name":         service_name,
        "service.version":      "1.0",
        "deployment.environment": os.getenv("DEPLOYMENT_ENV", "arion-demo"),
    })

    provider = TracerProvider(resource=resource)

    # Jaeger exporter (general trace UI)
    jaeger_endpoint = os.getenv("OTEL_JAEGER_ENDPOINT", "http://127.0.0.1:4317")
    try:
        jaeger_exporter = OTLPSpanExporter(endpoint=jaeger_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
        logger.info(f"telemetry: Jaeger exporter → {jaeger_endpoint}")
    except Exception as e:
        logger.warning(f"telemetry: Jaeger exporter failed: {e}")

    # Phoenix exporter (LLM-first UI)
    phoenix_endpoint = os.getenv("OTEL_PHOENIX_ENDPOINT", "http://127.0.0.1:6317")
    try:
        phoenix_exporter = OTLPSpanExporter(endpoint=phoenix_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(phoenix_exporter))
        logger.info(f"telemetry: Phoenix exporter → {phoenix_endpoint}")
    except Exception as e:
        logger.warning(f"telemetry: Phoenix exporter failed: {e}")

    trace.set_tracer_provider(provider)

    # Auto-instrumentation registration. Each is optional; import
    # failures degrade gracefully so partial-install environments
    # (e.g. missing openinference-instrumentation-langchain) don't
    # block bootstrap.
    _register_auto_instrumentation(fastapi_app)

    _INITIALIZED = True
    logger.info("telemetry: OTel bootstrap complete")


def _register_auto_instrumentation(fastapi_app=None) -> None:
    """Register community auto-instrumentation packages. Each in
    a try/except so a missing dependency doesn't block the rest."""

    # FastAPI / ASGI request spans. FastAPI 0.140 + Starlette 1.x are
    # newer than opentelemetry-instrumentation-fastapi's tested surface;
    # instrument_app() registers cleanly but produces no server spans on
    # this stack. Fall back to adding OpenTelemetryMiddleware directly —
    # this is what FastAPIInstrumentor does under the hood, minus the
    # newer-Starlette compatibility issues.
    if fastapi_app is not None:
        try:
            from opentelemetry import trace
            from opentelemetry.instrumentation.asgi import (
                OpenTelemetryMiddleware,
            )
            # Pass the current tracer_provider explicitly so the middleware
            # doesn't pick up a NoOp provider if bootstrap ordering is odd.
            tp = trace.get_tracer_provider()
            fastapi_app.add_middleware(
                OpenTelemetryMiddleware,
                tracer_provider=tp,
            )
            logger.info(f"telemetry: ASGI (FastAPI) instrumentation registered "
                        f"(tracer_provider={type(tp).__name__})")
        except Exception as e:
            logger.warning(f"telemetry: ASGI instrumentation failed: {e}")

    # psycopg2 DB spans (SQL template, no bind params by default)
    try:
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
        Psycopg2Instrumentor().instrument()
        logger.info("telemetry: psycopg2 instrumentation registered")
    except Exception as e:
        logger.warning(f"telemetry: psycopg2 instrumentation failed: {e}")

    # httpx outbound HTTP spans
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPXClientInstrumentor().instrument()
        logger.info("telemetry: httpx instrumentation registered")
    except Exception as e:
        logger.warning(f"telemetry: httpx instrumentation failed: {e}")

    # requests library
    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        RequestsInstrumentor().instrument()
        logger.info("telemetry: requests instrumentation registered")
    except Exception as e:
        logger.warning(f"telemetry: requests instrumentation failed: {e}")

    # OpenAI SDK — auto-emits gen_ai.* semconv spans
    try:
        from openinference.instrumentation.openai import OpenAIInstrumentor
        OpenAIInstrumentor().instrument()
        logger.info("telemetry: OpenAI (OpenInference) instrumentation registered")
    except Exception as e:
        logger.warning(f"telemetry: OpenAI instrumentation failed: {e}")

    # LangChain / LangGraph — arion_graph is LangGraph-based, so this
    # auto-covers classify/retrieve/rank_and_answer node spans without
    # manual wrapping.
    try:
        from openinference.instrumentation.langchain import LangChainInstrumentor
        LangChainInstrumentor().instrument()
        logger.info("telemetry: LangChain (OpenInference) instrumentation registered")
    except Exception as e:
        logger.warning(f"telemetry: LangChain instrumentation failed: {e}")

    # Chroma — openinference-instrumentation-chromadb doesn't ship
    # for Python 3.12 yet; skip. Chroma HTTP calls are captured via
    # httpx instrumentation instead (Chroma client uses httpx).
    logger.info("telemetry: chromadb instrumentation SKIPPED (Python 3.12 gap; "
                "Chroma HTTP calls captured via httpx instrumentation)")


# Convenience export for span-writing modules
__all__ = ["bootstrap_telemetry", "capture_content", "get_tracer"]
