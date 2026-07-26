---
name: ship-44-prime-a-otel-jaeger-design-2026-07-26
description: "Ship 44'.a design memo — OpenTelemetry SDK integration + Jaeger backend on Azure VM. Jaeger v1.63+ standalone binary via systemd (matches Ship 3'.a sweep timer pattern). OTLP gRPC exporter on 4317. Auto-instrument FastAPI + psycopg2 + httpx; custom spans on consensus signals + LLM calls + chat pipeline + engine. In-memory storage v1; local-only (127.0.0.1 bind). Redact evidence excerpts + LLM prompts to bounded lengths."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 44'.a — OpenTelemetry + Jaeger instrumentation design memo.

## Motivation

User ask (2026-07-26):

> instrument every data point in our app so that we have community
> backed tracing and this will help debugging the app

Current debugging state: structured logs in `/tmp/api.log` +
per-domain telemetry tables (`intake_consensus_log`,
`chat_casefile_log`, `chat_consensus_log`, `chat_llm_decision_trail`
view). Good for compliance-load-bearing audit but not for
"why is this request slow?" or "what path did this request take
through the pipeline?" questions.

OpenTelemetry adds: distributed tracing with cross-service span
propagation, automatic HTTP + DB span capture, a UI (Jaeger) to
navigate + filter traces by service, endpoint, duration, status.

## Deployment shape — systemd + local binary

Match existing pattern (`ops/systemd/arioncomply-sweep.service`):
- Jaeger v1.63+ all-in-one binary at `/opt/jaeger/`
- systemd unit at `/etc/systemd/system/arioncomply-jaeger.service`
- Bind 127.0.0.1 only (no external exposure — traces contain
  tenant data, evidence text, LLM prompt fragments)
- In-memory storage (default) — fine for dev + first-week
  production; badger persistence is a later arc
- OTLP gRPC receiver on 4317; UI on 16686

**Alternative rejected**: Docker (not installed on VM); Jaeger v2
(more complex — v1 all-in-one is battle-tested).

**Ports**:
- 4317 OTLP gRPC receiver (SDK → Jaeger)
- 4318 OTLP HTTP receiver (unused; kept for flexibility)
- 16686 Jaeger UI
- 14268 Jaeger HTTP (legacy)
- 6831/6832 UDP Jaeger agent (legacy, not used)

All ports bind 127.0.0.1 by design.

## OTel packages needed

Already installed:
- `opentelemetry-api` 1.41.1
- `opentelemetry-sdk` 1.41.1
- `opentelemetry-exporter-otlp-proto-grpc` 1.41.1

To install:
- `opentelemetry-instrumentation-fastapi` — auto request spans
- `opentelemetry-instrumentation-psycopg2` — DB query spans
- `opentelemetry-instrumentation-httpx` — outbound HTTP spans
- `opentelemetry-instrumentation-requests` — legacy requests calls

Not using:
- `opentelemetry-distro` — meta-package; too much magic
- `opentelemetry-instrumentation-logging` — trace-log correlation
  is a Ship 44'.d candidate, not blocker

## Instrumentation surface

**Automatic** (via auto-instrumentation):
- FastAPI: request span per endpoint (method + path + status + duration)
- psycopg2: query span per SQL statement (statement + duration; NOT bind params)
- httpx: request span per outbound HTTP call (target + status + duration)

**Custom** (via manual `tracer.start_as_current_span`):
- `rag/intake/consensus_extraction/orchestrator.py` — per-signal
  spans + aggregator decision + arbiter call
- `rag/llm_client.py` — LLM API call span with model, purpose,
  token counts, latency; prompt content truncated to 500 chars
- `rag/arion_graph.py` — one span per LangGraph node
  (classify, retrieve, rank_and_answer)
- `rag/casefile/digest.py` — case-file build span
- `rag/casefile/repair.py` — preservation-check repair span
  (span attribute: repair_events_count)
- `rag/posture/fulfilment_engine.py::compute_engine_verdicts`
  — engine verdict computation span
- `rag/posture_loader.py::load_posture` — posture load span
- `rag/intake/posture_writer.py::write_findings` — write span
  (attributes: n_findings, n_written, n_skipped)

## Bootstrap module

New file: `rag/telemetry.py`:

```python
"""ArionComply telemetry — OpenTelemetry SDK bootstrap.

Called once from api_server.py startup. Sets up:
- Tracer provider with OTLP gRPC exporter to local Jaeger
- Resource attributes (service.name, service.version, deploy.environment)
- Auto-instrumentation registration (FastAPI, psycopg2, httpx)

Feature-flagged via OTEL_ENABLED env var (default off; on when
Jaeger is running). Silent-fail on collector unreachable — API
never blocks on telemetry.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
# ...
```

## Sampling strategy

**Default**: 100% (parent-based sampler + always_on root).

Rationale: dev + Arion demo tenant load is low; every trace
matters for debugging. Production tuning is a later arc if
volume grows.

**Override**: `OTEL_TRACES_SAMPLER=parentbased_traceidratio`
+ `OTEL_TRACES_SAMPLER_ARG=0.1` for 10% sampling.

## Privacy + security

Traces will contain sensitive data:
- Query strings (chat queries may reveal tenant intent)
- LLM prompts (evidence text, MUST content)
- Evidence excerpts (potentially PII if tenant docs have it)
- Tenant IDs (routing info)

**Mitigations**:
- Jaeger binds 127.0.0.1 only — no external network exposure
- Custom span attributes truncate content to 500 chars
  (`text[:500] + '...'`)
- LLM prompt content NOT captured verbatim — only length +
  model + purpose. If a specific span needs prompt for debugging,
  it can be enabled per-span via attribute.
- Postgres bind parameters NOT captured (psycopg2
  instrumentation default). Only SQL statement templates.

## Impact on chat + extraction latency

OTel span overhead: ~1-5μs per span, negligible vs per-request
latency (100ms-60s range). No user-visible impact.

Batch span processor default: 512-span buffer, 5s flush interval.
Backpressure on Jaeger downtime is bounded (drops spans past
buffer, doesn't block).

## Ship 44'.b bootstrap plan

1. Download Jaeger v1.63.0 all-in-one binary
2. Install to `/opt/jaeger/`
3. Create systemd unit at
   `/data/arioncomply/ops/systemd/arioncomply-jaeger.service`
4. Install script `ops/install_jaeger.sh` (idempotent, mirrors
   `install_sweep_timer.sh`)
5. Enable + start jaeger service
6. `pip install --break-system-packages opentelemetry-instrumentation-{fastapi,psycopg2,httpx,requests}`
7. Write `rag/telemetry.py` with bootstrap function
8. Wire into `api_server.py` startup event
9. Restart API + verify traces in Jaeger UI at
   `http://localhost:16686` (SSH tunnel from workstation:
   `ssh -L 16686:localhost:16686 arionlabs@172.211.244.144`)

## Ship 44'.c custom spans on consensus + LLM

Wrap orchestrator body in a tracer span; each signal's compute()
in a child span (name = signal_name); aggregator + arbiter in
child spans with attributes for verdict counts.

LLM client: span per API call with attributes (model, purpose,
prompt_len, response_len, tokens_input, tokens_output,
latency_ms).

## Ship 44'.d chat + engine spans

`arion_graph.py`: one span per node (classify, retrieve,
rank_and_answer). LangGraph doesn't expose per-node hooks
cleanly; manual `tracer.start_as_current_span` inside each
node function.

`fulfilment_engine.compute_engine_verdicts`: outer span; each
control's verdict computation as child span (may be too many —
consider only spanning slow ones via conditional
`if elapsed > 100ms: start_span`).

## What Ship 44 does NOT do

- **Metrics** (OTel metrics API) — traces first; metrics is Ship 45+
- **Logs** (OTel logs API) — separate arc; logs still go to
  `/tmp/api.log`
- **Trace-log correlation** — deferred; needs logs-side wiring
- **Distributed context propagation across processes** — API is
  single-process on Arion; if we split later, W3C traceparent
  header is already auto-configured
- **Custom Jaeger UI dashboards / saved queries** — post-arc
- **Persistent storage for Jaeger** — in-memory sufficient for
  demo tenant load

## Framework role + case-file alignment

**Orthogonal**. Tracing is an observability layer; doesn't touch
role model classification or case-file digest semantics. Spans
capture the SHAPE of processing (which node ran, which signal
fired) without altering behavior.

**Case-file lens**: adding spans inside `_casefile_flow` gives
us "why did this turn take 8s?" answers — case-file build vs
LLM call vs preservation-check vs graph expansion. Complements
`chat_casefile_log`'s post-hoc telemetry with in-flight tracing.

## Ship 44'.e retro topics

- Sampling: was 100% sustainable at Arion's request volume?
- What debugging value did the first trace surface?
- Any span attributes we regret capturing (privacy) or wish we
  did (utility)?
- Chat pipeline hotspots surfaced by trace waterfall
- Consensus signal timing distribution
- Ship 45 candidates: metrics + trace-log correlation + Jaeger
  persistence

## Ship 45 preview candidates (deferred)

- OTel metrics + Prometheus scrape endpoint
- Trace-log correlation via `opentelemetry-instrumentation-logging`
- Jaeger badger persistence for cross-restart trace history
- Custom UI dashboards (if traces reveal patterns worth
  surfacing to non-ops users)

## Related

- [[ship-43-prime-arc-retrospective-2026-07-26]] — closes Ship
  43; opens Ship 44
- `ops/systemd/arioncomply-sweep.service` — the systemd shape
  Ship 44 mirrors for Jaeger
- `rag/telemetry.py` (new) — OTel bootstrap module
- `docs/memory/ship-3-prime-a-sweep-timer` — the install script
  precedent
