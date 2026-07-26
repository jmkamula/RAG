#!/bin/bash
# ArionComply — Jaeger + Phoenix installer
# Ship 44'.b — idempotent installer for OTel tracing backends
set -euo pipefail

JAEGER_VERSION="1.63.0"
JAEGER_BIN="/opt/jaeger/jaeger-all-in-one"

echo "==> Installing Jaeger v${JAEGER_VERSION}..."
if [ ! -x "$JAEGER_BIN" ]; then
    curl -sL "https://github.com/jaegertracing/jaeger/releases/download/v${JAEGER_VERSION}/jaeger-${JAEGER_VERSION}-linux-amd64.tar.gz" \
        -o /tmp/jaeger-${JAEGER_VERSION}-linux-amd64.tar.gz
    cd /tmp && tar xzf jaeger-${JAEGER_VERSION}-linux-amd64.tar.gz
    sudo mkdir -p /opt/jaeger
    sudo cp jaeger-${JAEGER_VERSION}-linux-amd64/jaeger-all-in-one "$JAEGER_BIN"
    sudo chmod +x "$JAEGER_BIN"
    echo "  ✓ Jaeger binary installed at $JAEGER_BIN"
else
    echo "  ✓ Jaeger binary already present"
fi

echo "==> Installing Phoenix (pip)..."
if ! python3 -c "import phoenix" 2>/dev/null; then
    pip install --break-system-packages arize-phoenix
    echo "  ✓ Phoenix installed"
else
    echo "  ✓ Phoenix already installed"
fi

echo "==> Installing OTel auto-instrumentation packages..."
pip install --break-system-packages -q \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-psycopg2 \
    opentelemetry-instrumentation-httpx \
    opentelemetry-instrumentation-requests \
    openinference-instrumentation-langchain \
    openinference-instrumentation-openai || echo "  ⚠ some instrumentation packages failed (Python 3.12 gaps)"
echo "  ✓ Auto-instrumentation packages"

echo "==> Installing systemd units..."
sudo cp /data/arioncomply/ops/systemd/arioncomply-jaeger.service /etc/systemd/system/
sudo cp /data/arioncomply/ops/systemd/arioncomply-phoenix.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "==> Enabling + starting services..."
sudo systemctl enable --now arioncomply-jaeger
sudo systemctl enable --now arioncomply-phoenix

sleep 3

echo "==> Verifying..."
if curl -sf http://127.0.0.1:16686/ > /dev/null; then
    echo "  ✓ Jaeger UI:    http://127.0.0.1:16686  (OTLP gRPC: 4317)"
else
    echo "  ✗ Jaeger not responding on :16686"
fi
if curl -sf http://127.0.0.1:6006/ > /dev/null; then
    echo "  ✓ Phoenix UI:   http://127.0.0.1:6006   (OTLP gRPC: 6317)"
else
    echo "  ✗ Phoenix not responding on :6006"
fi

cat <<INFO

To enable OTel on the API:
  OTEL_ENABLED=1 OTEL_PRIVACY_LEVEL=debug PYTHONPATH=/data/arioncomply \\
    python3 api_server.py > /tmp/api.log 2>&1 &

Privacy tiers:
  OTEL_PRIVACY_LEVEL=off           — no tracing
  OTEL_PRIVACY_LEVEL=observability — paths + latencies + counts, NO content (default)
  OTEL_PRIVACY_LEVEL=debug         — + truncated content (500c), INTERNAL ENGINEERING ONLY

To view traces from a remote workstation:
  ssh -L 16686:127.0.0.1:16686 -L 6006:127.0.0.1:6006 arionlabs@172.211.244.144
INFO
