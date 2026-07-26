---
name: ship-44-prime-arc-retrospective-2026-07-26
description: "Ship 44' arc closer — OpenTelemetry + Jaeger + Arize Phoenix dual-backend distributed tracing live. Community-backed auto-instrumentation for OpenAI SDK + LangGraph + psycopg2 + httpx; manual spans on consensus signals + LLM client (urllib) + engine + posture + writer + case-file. OTEL_PRIVACY_LEVEL 3-tier gating (off / observability / debug). First real debugging insights: retrieve node 11.7s dominates chat latency; fingerprint_keyword 7.8s dominates consensus latency."
metadata:
  node_type: memory
  type: project
  originSessionId: 5808ba74-b22a-4a68-b4f1-19f18ce079cd
---

Ship 44' arc retrospective — 4 delivery sub-arcs + addendum + closer,
single session 2026-07-26. Distributed tracing arc after user asked
to "instrument every data point in our app so that we have community
backed tracing".

## What shipped

| Sub-arc | Delivery | Commit |
|---|---|---|
| 44'.a | Design memo — OTel + Jaeger, systemd deployment | d13ae7b |
| 44'.a addendum | OpenLLMetry + GenAI semconv + 3-tier privacy | 14f1f25 |
| Path B pick | Jaeger + Arize Phoenix dual export | (question) |
| 44'.b | Jaeger + Phoenix binaries + systemd + rag/telemetry.py | b1c18b4 |
| 44'.c | Consensus signals + LLM client custom spans | c5692df |
| 44'.d | Engine + posture loader + writer + case-file spans | 28ade84 |
| **44'.e** | **Retro (this)** | pending |

## Architecture landed

**Two OSS tracing backends** running as systemd services on the
Azure VM, both bind 127.0.0.1 only (traces contain sensitive
content):

- **Jaeger v1.63.0** — general trace UI, service map, dependency
  graph. UI on 16686; OTLP gRPC on 4317.
  Service: `arioncomply-jaeger.service`
- **Arize Phoenix 19.6.0** — LLM-first UI with prompt/completion
  viewer, RAG eval framework. UI on 6006; OTLP gRPC on 6317.
  Service: `arioncomply-phoenix.service`

**SDK fan-out**: OTel SDK exports every span to both backends
simultaneously via `BatchSpanProcessor` × 2 (Jaeger endpoint +
Phoenix endpoint).

**Bootstrap module** `rag/telemetry.py`:
- `bootstrap_telemetry(fastapi_app)` — reads OTEL_ENABLED +
  OTEL_PRIVACY_LEVEL, registers auto-instrumentation, sets up
  tracer provider with dual exporters. Silent-fail on backend
  unreachable — API never blocks on telemetry.
- `capture_content()` — content-attribute gate helper for
  privacy-sensitive spans. Returns True only when
  `OTEL_PRIVACY_LEVEL=debug`.
- `get_tracer(name)` — tracer factory with NoOp fallback.

**Install script** `ops/install_jaeger.sh` — idempotent,
mirrors `install_sweep_timer.sh` pattern.

## Auto-instrumentation adopted

Via `opentelemetry-instrumentation-*` (Apache 2.0) and
OpenInference (from Arize Phoenix — permissive):

- `opentelemetry-instrumentation-psycopg2` — SQL query spans
  (statement templates, no bind params)
- `opentelemetry-instrumentation-httpx` — outbound HTTP spans
  (captures Chroma HTTP client calls via httpx)
- `opentelemetry-instrumentation-requests` — legacy HTTP
- `openinference-instrumentation-openai` — OpenAI SDK spans
  with `gen_ai.*` semantic conventions
- `openinference-instrumentation-langchain` — LangChain +
  **LangGraph** node spans (arion_graph's classify/retrieve/
  rank_and_answer auto-covered)

**Skipped**:
- `openinference-instrumentation-chromadb` — no Python 3.12
  wheels; Chroma HTTP captured via httpx instrumentation instead
- `opentelemetry-instrumentation-fastapi` — instrument_app()
  didn't produce server spans on FastAPI 0.140 + Starlette 1.x;
  worked around with manual span in @app.middleware

## Manual spans added

`arion.*` attribute namespace for pipeline stages the community
doesn't standardize:

**Consensus** (Ship 44'.c):
- `arion.consensus.run` (outer) + 9 `arion.consensus.signal.<name>`
  spans + `arion.consensus.aggregate` + `arion.consensus.arbitrate`
- Attributes: n_candidates per signal, verdict counts, latency

**LLM client** (Ship 44'.c):
- `gen_ai.chat.<purpose>` on every `llm_client.call()` invocation
  (urllib path — NOT covered by openinference-instrumentation-openai)
- `gen_ai.*` semantic-convention attributes: system, operation,
  model, max_tokens, temperature, input_tokens, output_tokens,
  prompt/completion content (debug tier only)

**Engine + posture + writer** (Ship 44'.d):
- `arion.engine.compute_verdicts` — n_controls, n_verdicts, latency
- `arion.posture.load` — n_controls + per-verdict counts +
  engine_overrides + demonstrates counts + latency
- `arion.writer.write_findings` — n_findings_input/written/skipped +
  posture updated/created

**Case-file** (Ship 44'.d):
- `arion.casefile.build_structured_prompt_pair` — system/user char
  counts, token estimates, n_posture_lines, n_bridges
- `arion.casefile.extract_preservation_spec` — n_required_refs,
  n_draft_refs, n_verdicts, n_bridge_articles
- `arion.casefile.check_and_repair` — events_count, footers_added,
  per-repair-kind counts

**Server request** (Ship 44'.b):
- Wrapped in existing `@app.middleware("http") add_trace_id` —
  emits SERVER-kind span with method + path + status. FastAPI
  auto-instrumentation didn't work on Starlette 1.x; manual is
  the workaround.

## Privacy tiers implemented

`OTEL_PRIVACY_LEVEL` env var:

- **off** — OTel disabled entirely (default when unset)
- **observability** — paths, latencies, model+tokens, DB query
  templates. NO content (query strings, prompts, completions,
  evidence excerpts). Default when OTEL_ENABLED=1.
- **debug** — + truncated content (500 char cap). Internal
  engineering only, never on production.

Traceloop/OpenInference content-capture env vars
(`TRACELOOP_TRACE_CONTENT`, `OPENINFERENCE_HIDE_INPUTS/OUTPUTS`)
are wired to the same tier. Our custom span code checks
`rag.telemetry.capture_content()` before setting any content
attribute.

## First debugging insights

Running on Arion demo with `OTEL_PRIVACY_LEVEL=debug` post-arc:

**Chat latency (14.8s total)**:
- `POST /api/v1/chat` = 14.8s
- `LangGraph.classify` = 3.1s (of which consensus_gatekeeper LLM = 1.08s)
- `LangGraph.retrieve` = 11.7s ← **dominant**
- `gen_ai.chat.rank_answer` = 4.06s
- Case-file build + preservation-check < 10ms combined

Insight: `retrieve` is 79% of chat latency and hasn't been
individually profiled before. Ship 45+ candidate — decompose
retrieve into embed + graph-expand + posture-load + digest-render
sub-spans.

**Consensus latency (31.5s on DPIA)**:
- `arion.consensus.run` = 31.5s
- `arion.consensus.signal.fingerprint_keyword` = 7.8s ← **dominant**
- `arion.consensus.signal.bm25_topk` = 1.5s
- `arion.consensus.signal.must_semantic_topk` = 682ms
- `arion.consensus.signal.per_protocol_scope` = 665ms
- Other signals < 20ms each

Insight: fingerprint_keyword's Ship 28+29 catalog walk is the
consensus latency floor. Ship 45+ candidate — decompose
fingerprint matching into per-leaf timing.

## Codified 3 lessons

### 1. Adopt the emerging semantic conventions, don't invent them

OTel Semantic Conventions for GenAI (`gen_ai.*` attributes)
plus OpenInference for RAG-specific extensions are the de facto
standard. Every LLM observability tool (Jaeger, Arize Phoenix,
Langfuse, Grafana Tempo, Honeycomb, Datadog) renders them
natively. Traces are portable — swap Jaeger for Phoenix without
touching our code.

**Rule**: for cross-industry concerns (LLM calls, HTTP, DB),
use the semantic conventions. For product-specific spans
(consensus signals, case-file digest), use a private namespace
(`arion.*`). Never invent an attribute name where a semantic
convention exists.

### 2. Privacy tiers must be foundational, not retrofitted

Building `OTEL_PRIVACY_LEVEL` tier gating into the bootstrap
module before shipping any spans made every subsequent
instrumentation site trivially safe. Compare with the
Traceloop-only approach (TRACELOOP_TRACE_CONTENT single toggle)
which forces a binary all-or-nothing content decision.

**Rule**: when adding observability, ship the privacy tier
FIRST. Every span callsite becomes a `if capture_content():`
guard call. Zero risk of accidental content dumps.

### 3. Auto-instrumentation saves LOC but doesn't solve everything

Community auto-instrumentation covered ~150 LOC of hand-rolled
spans (LangGraph nodes, OpenAI SDK, DB queries). But two gaps
required manual work:
- FastAPI 0.140 + Starlette 1.x wasn't tested by
  `opentelemetry-instrumentation-fastapi` — manual span in
  existing middleware fixed it
- `llm_client.call()` uses urllib (not OpenAI Python SDK), so
  `openinference-instrumentation-openai` didn't cover it —
  manual `gen_ai.*` span emission

**Rule**: verify each auto-instrumentation package covers your
actual code paths. Adjacent-but-not-identical implementations
(urllib vs OpenAI SDK; Starlette 0.x vs 1.x) may need manual
bridging even when the community package exists.

## What Ship 44 did NOT do

- **Metrics** (OTel metrics API) — traces only; Ship 45 candidate
- **Logs OTel exporter** — logs still write to /tmp/api.log;
  Ship 45 candidate
- **Trace-log correlation** — needs logging-side wiring; Ship 45
- **Persistent Jaeger storage** — in-memory sufficient for demo
  load; badger persistence is a later concern
- **Sampling strategy tuning** — 100% default; production would
  tune based on volume
- **Retention policies** — Phoenix accumulates traces; needs
  a periodic prune job at some point

## SSH access for tenant / engineering

Both UIs bound to 127.0.0.1. To view from a workstation:

```bash
ssh -L 16686:127.0.0.1:16686 -L 6006:127.0.0.1:6006 \
    -i ~/.ssh/arioncomplySK.pem arionlabs@172.211.244.144
```

Then:
- Jaeger UI: `http://localhost:16686`
- Phoenix UI: `http://localhost:6006`

## Deferred / follow-on candidates

- **Ship 45**: OTel metrics + Prometheus scrape endpoint
- **Ship 46**: trace-log correlation via
  `opentelemetry-instrumentation-logging`
- **Broader-doc eval on Arion's 68 other docs** (Ship 41 legacy
  backlog, unchanged)
- **retrieve decomposition** — profile the 11.7s retrieve node
  into embed + Chroma + graph-expand + posture-load sub-spans
- **fingerprint_keyword decomposition** — per-leaf matching
  timing to find the specific hot spots
- **Persistent Phoenix storage** — currently SQLite in
  /data/arioncomply/.phoenix; may want Postgres backing
- **Retention prune job** — sweep old traces from Phoenix DB

## Related

- [[ship-43-prime-arc-retrospective-2026-07-26]] — the arc that
  closed just before Ship 44 opened
- [[ship-44-prime-a-otel-jaeger-design-2026-07-26]] — original
  design memo (Jaeger-only plan)
- [[ship-44-prime-a-addendum-llm-instrumentation-2026-07-26]] —
  addendum locking in OpenLLMetry + GenAI semconv + privacy tiers
- `rag/telemetry.py` — bootstrap + `capture_content()` gate
- `ops/systemd/arioncomply-{jaeger,phoenix}.service` — the
  two systemd units
- `ops/install_jaeger.sh` — idempotent installer
- Ship 45 (next) — TBD (metrics? logs? something else?)
