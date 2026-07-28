#!/usr/bin/env bash
# scripts/ops/diagnose.sh — ArionComply deployment diagnostic bundle.
#
# Runs on a customer VM and produces /tmp/arion-diag-<host>-<date>.tar.gz
# containing structured system/service/database/config snapshots for
# support (human or Claude Code) to diagnose without SSH.
#
# Privacy invariants:
#   - .env values are redacted; only variable names visible
#   - No evidence text, chat prose, LLM prompts/completions
#   - No api_key raw values (only hashes/prefixes)
#   - Tenant names + control refs OK (non-secret compliance vocabulary)
#
# Usage:
#   bash scripts/ops/diagnose.sh              # write /tmp/arion-diag-...tar.gz
#   bash scripts/ops/diagnose.sh --stdout     # write to stdout instead
#   bash scripts/ops/diagnose.sh --no-journal # skip journalctl (if not systemd)

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────
ARION_ROOT="${ARION_ROOT:-/data/arioncomply}"
ENV_FILE="${ARION_ROOT}/.env"
JOURNAL_LINES="${JOURNAL_LINES:-500}"
LOG_TAIL_LINES="${LOG_TAIL_LINES:-500}"

STDOUT_MODE=0
SKIP_JOURNAL=0
for arg in "$@"; do
  case "$arg" in
    --stdout)     STDOUT_MODE=1 ;;
    --no-journal) SKIP_JOURNAL=1 ;;
    --help|-h)
      grep '^#' "$0" | head -25 | sed 's/^# \?//'
      exit 0 ;;
  esac
done

HOSTNAME_SHORT="$(hostname -s 2>/dev/null || echo unknown)"
STAMP="$(date -u +%Y%m%d-%H%M%SZ)"
BUNDLE_DIR="$(mktemp -d /tmp/arion-diag-XXXXXX)"
BUNDLE_NAME="arion-diag-${HOSTNAME_SHORT}-${STAMP}"
BUNDLE_ROOT="${BUNDLE_DIR}/${BUNDLE_NAME}"
mkdir -p "${BUNDLE_ROOT}"

# ── Helpers ───────────────────────────────────────────────────────
write() { printf '%s\n' "$@" >> "${BUNDLE_ROOT}/$1"; }
section() { printf '\n=== %s ===\n' "$1" >> "${BUNDLE_ROOT}/$2"; }
capture() {
  # capture <cmd> <file> [label] — run cmd, redirect stdout+stderr
  local file="$1"; shift
  local label="${!#}"
  # If last arg looks like a label (starts with #), pop it as label
  # Otherwise use command line as label.
  echo "\$ $*" >> "${BUNDLE_ROOT}/${file}"
  ( "$@" ) >> "${BUNDLE_ROOT}/${file}" 2>&1 || echo "[command failed: exit $?]" >> "${BUNDLE_ROOT}/${file}"
  echo "" >> "${BUNDLE_ROOT}/${file}"
}

have() { command -v "$1" >/dev/null 2>&1; }

# Load env if present (for DB creds) — but redact when we write it out.
if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

# ── 01. system.txt ────────────────────────────────────────────────
{
  echo "# ArionComply diagnostic bundle"
  echo "# generated: ${STAMP}"
  echo "# host: $(hostname -f 2>/dev/null || hostname)"
  echo "# bundle: ${BUNDLE_NAME}"
} > "${BUNDLE_ROOT}/README.txt"

{
  echo "=== uname -a ==="
  uname -a
  echo ""
  echo "=== /etc/os-release ==="
  cat /etc/os-release 2>/dev/null || echo "(not readable)"
  echo ""
  echo "=== uptime ==="
  uptime
  echo ""
  echo "=== disk (df -h) ==="
  df -h 2>/dev/null || true
  echo ""
  echo "=== memory (free -h) ==="
  free -h 2>/dev/null || true
  echo ""
  echo "=== timezone ==="
  timedatectl 2>/dev/null | head -10 || date
  echo ""
  echo "=== whoami ==="
  echo "user: $(id -un)   uid: $(id -u)"
  echo "groups: $(id -Gn 2>/dev/null || id)"
} > "${BUNDLE_ROOT}/system.txt"

# ── 02. services.txt ──────────────────────────────────────────────
{
  echo "=== systemd services ==="
  for svc in arioncomply-api arioncomply-chroma arioncomply-jaeger arioncomply-phoenix; do
    echo ""
    echo "--- ${svc} ---"
    if have systemctl; then
      systemctl is-enabled "${svc}" 2>&1 || true
      systemctl status "${svc}" --no-pager 2>&1 | head -25 || true
    else
      echo "(systemctl not available)"
    fi
  done
  echo ""
  echo "=== timers ==="
  if have systemctl; then
    systemctl list-timers 'arioncomply-*' --all --no-pager 2>&1 || true
  fi
  echo ""
  echo "=== port bindings ==="
  # Show what's listening on our known ports without exposing PID names to whoever reads bundle
  if have ss; then
    ss -tlnp 2>&1 | grep -E ':(7474|7687|8000|8001|8080|6006|6317|16686|4317) ' 2>&1 || echo "(no listeners on arion ports)"
  elif have lsof; then
    lsof -iTCP -sTCP:LISTEN -P -n 2>&1 | grep -E ':(7474|7687|8000|8001|8080|6006|6317|16686|4317) ' || echo "(no listeners)"
  fi
} > "${BUNDLE_ROOT}/services.txt"

# ── 03. journal-*.txt (if systemd) ────────────────────────────────
if [[ "${SKIP_JOURNAL}" -eq 0 ]] && have journalctl; then
  for svc in arioncomply-api arioncomply-chroma; do
    journalctl -u "${svc}" -n "${JOURNAL_LINES}" --no-pager 2>&1 \
      > "${BUNDLE_ROOT}/journal-${svc#arioncomply-}.txt" || true
  done
fi

# ── 04. api-log.txt ───────────────────────────────────────────────
for log in /tmp/arioncomply-api.log /tmp/api.log; do
  if [[ -f "${log}" ]]; then
    {
      echo "=== ${log} (tail -${LOG_TAIL_LINES}) ==="
      tail -n "${LOG_TAIL_LINES}" "${log}" 2>&1 || echo "(read failed)"
    } > "${BUNDLE_ROOT}/api-log.txt"
    break
  fi
done

for log in /tmp/arioncomply-chroma.log /tmp/chroma.log; do
  if [[ -f "${log}" ]]; then
    {
      echo "=== ${log} (tail -${LOG_TAIL_LINES}) ==="
      tail -n "${LOG_TAIL_LINES}" "${log}" 2>&1 || echo "(read failed)"
    } > "${BUNDLE_ROOT}/chroma-log.txt"
    break
  fi
done

# ── 05. postgres.txt ──────────────────────────────────────────────
if have psql; then
  # Prefer PGPASSWORD from env; fall back to DATABASE_URL parsing.
  PG_ENV="${DATABASE_URL:-}"
  if [[ -n "${PG_ENV}" ]]; then
    export PGCONNSTR="${PG_ENV}"
    {
      echo "=== version ==="
      psql "${PGCONNSTR}" -tAc "SELECT version();" 2>&1 || echo "(auth failed)"
      echo ""
      echo "=== databases (\\l+) ==="
      psql "postgresql://${PGUSER:-arioncomply_app}:${PGPASSWORD:-}@${PGHOST:-127.0.0.1}/postgres" \
        -c "\\l+" 2>&1 | head -30 || echo "(could not list DBs)"
      echo ""
      echo "=== connection count ==="
      psql "${PGCONNSTR}" -tAc "SELECT count(*) FROM pg_stat_activity;" 2>&1 || true
      echo ""
      echo "=== active queries (5s+) ==="
      psql "${PGCONNSTR}" -c "SELECT pid, state, wait_event, now()-query_start AS runtime, LEFT(query, 100) FROM pg_stat_activity WHERE state='active' AND now()-query_start > interval '5 seconds' ORDER BY runtime DESC LIMIT 10;" 2>&1 || true
      echo ""
      echo "=== compliance DB tables (top 20 by rows) ==="
      psql "${PGCONNSTR}" -c "SELECT schemaname, relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 20;" 2>&1 || true
      echo ""
      echo "=== extensions ==="
      psql "${PGCONNSTR}" -c "SELECT extname, extversion FROM pg_extension ORDER BY extname;" 2>&1 || true
      echo ""
      echo "=== RLS-enabled tables (top 20) ==="
      psql "${PGCONNSTR}" -c "SELECT schemaname, tablename FROM pg_tables t JOIN pg_class c ON c.relname=t.tablename WHERE c.relrowsecurity=true LIMIT 20;" 2>&1 || true
      echo ""
      echo "=== DB size ==="
      psql "${PGCONNSTR}" -c "SELECT pg_size_pretty(pg_database_size(current_database())) AS compliance_db_size;" 2>&1 || true
      if [[ -n "${SESSIONS_DATABASE_URL:-}" ]]; then
        echo ""
        echo "=== sessions DB size ==="
        psql "${SESSIONS_DATABASE_URL}" -c "SELECT pg_size_pretty(pg_database_size(current_database())) AS sessions_db_size;" 2>&1 || true
      fi
    } > "${BUNDLE_ROOT}/postgres.txt"
  else
    echo "(no DATABASE_URL in env; skipping postgres diagnostics)" > "${BUNDLE_ROOT}/postgres.txt"
  fi
else
  echo "(psql not installed)" > "${BUNDLE_ROOT}/postgres.txt"
fi

# ── 06. neo4j.txt ─────────────────────────────────────────────────
if [[ -n "${NEO4J_URI:-}" ]] && have python3; then
  python3 <<'PYEOF' > "${BUNDLE_ROOT}/neo4j.txt" 2>&1 || echo "[neo4j probe failed]" >> "${BUNDLE_ROOT}/neo4j.txt"
import os, sys
try:
    from neo4j import GraphDatabase
except ImportError:
    print("(neo4j driver not installed)")
    sys.exit(0)
uri = os.getenv("NEO4J_URI") or "bolt://127.0.0.1:7687"
user = os.getenv("NEO4J_USER") or "neo4j"
pw = os.getenv("NEO4J_PASSWORD") or ""
if not pw:
    print("(NEO4J_PASSWORD not set)")
    sys.exit(0)
try:
    d = GraphDatabase.driver(uri, auth=(user, pw))
    with d.session() as s:
        print("=== node counts by label ===")
        for r in s.run("CALL db.labels() YIELD label RETURN label"):
            label = r["label"]
            c = s.run(f"MATCH (n:`{label}`) RETURN count(n) AS c").single()["c"]
            print(f"  {label}: {c}")
        print()
        print("=== edge counts by type ===")
        for r in s.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"):
            t = r["relationshipType"]
            c = s.run(f"MATCH ()-[e:`{t}`]->() RETURN count(e) AS c").single()["c"]
            print(f"  {t}: {c}")
        print()
        print("=== schema constraints ===")
        for r in s.run("SHOW CONSTRAINTS"):
            print(f"  {r.get('name','?')}: {r.get('type','?')} on {r.get('labelsOrTypes','?')}")
    d.close()
except Exception as e:
    print(f"(neo4j probe error: {e})")
PYEOF
else
  echo "(neo4j not configured or python3 missing)" > "${BUNDLE_ROOT}/neo4j.txt"
fi

# ── 07. chroma.txt ────────────────────────────────────────────────
if have python3; then
  python3 <<'PYEOF' > "${BUNDLE_ROOT}/chroma.txt" 2>&1 || echo "[chroma probe failed]" >> "${BUNDLE_ROOT}/chroma.txt"
import os, sys
host = os.getenv("CHROMA_HOST") or "127.0.0.1"
port = int(os.getenv("CHROMA_PORT") or "8000")
try:
    import chromadb
except ImportError:
    print("(chromadb client not installed)")
    sys.exit(0)
try:
    c = chromadb.HttpClient(host=host, port=port)
    cols = c.list_collections()
    print(f"=== collections on {host}:{port} ({len(cols)} total) ===")
    for col in cols:
        try:
            n = col.count()
        except Exception as e:
            n = f"err: {e}"
        print(f"  {col.name}: {n} docs")
    print()
    try:
        v = c.get_version()
        print(f"=== server version === {v}")
    except Exception as e:
        print(f"(version probe error: {e})")
except Exception as e:
    print(f"(chroma probe error: {e})")
PYEOF
else
  echo "(python3 not available)" > "${BUNDLE_ROOT}/chroma.txt"
fi

# ── 08. tenants.txt ───────────────────────────────────────────────
# Non-sensitive tenant list: name + slug + created_at + framework enrolment + counts.
if have psql && [[ -n "${DATABASE_URL:-}" ]]; then
  {
    echo "=== tenants ==="
    psql "${DATABASE_URL}" -c \
      "SELECT id, name, slug, industry, created_at FROM tenants ORDER BY created_at LIMIT 50;" 2>&1 || echo "(query failed)"
    echo ""
    echo "=== framework enrolment (top 20) ==="
    psql "${DATABASE_URL}" -c \
      "SELECT tenant_id, standard_id, status FROM tenant_framework_enrolment ORDER BY tenant_id LIMIT 20;" 2>&1 || echo "(no enrolment table or query failed)"
    echo ""
    echo "=== posture counts per tenant × standard ==="
    psql "${DATABASE_URL}" -c \
      "SELECT tenant_id, standard_id, finding, count(*) FROM posture_controls WHERE is_active=true GROUP BY 1,2,3 ORDER BY 1,2,3;" 2>&1 || echo "(query failed)"
    echo ""
    echo "=== api_keys (metadata only, no raw values) ==="
    psql "${DATABASE_URL}" -c \
      "SELECT id, tenant_id, name, scopes, is_active, last_used_at, created_at FROM api_keys ORDER BY created_at DESC LIMIT 20;" 2>&1 || echo "(query failed)"
  } > "${BUNDLE_ROOT}/tenants.txt"
else
  echo "(no DATABASE_URL; skipping tenants probe)" > "${BUNDLE_ROOT}/tenants.txt"
fi

# ── 09. env.redacted.txt ──────────────────────────────────────────
if [[ -f "${ENV_FILE}" ]]; then
  # Redact everything after `=` unless it's a public-safe key (host/port/flag).
  # Whitelist keys that are safe to show verbatim.
  # Everything else → ***REDACTED*** (variable name preserved).
  awk '
    BEGIN {
      # keys safe to show as-is
      safe["API_PORT"]=1; safe["CHROMA_HOST"]=1; safe["CHROMA_PORT"]=1;
      safe["PGHOST"]=1; safe["PGDATABASE"]=1; safe["PGUSER"]=1;
      safe["NEO4J_URI"]=1; safe["NEO4J_USER"]=1;
      safe["DEPLOYMENT_ENV"]=1; safe["CORS_ORIGINS"]=1; safe["MAX_UPLOAD_MB"]=1;
      safe["USE_CONSENSUS_EXTRACTION"]=1; safe["OTEL_ENABLED"]=1;
      safe["OTEL_PRIVACY_LEVEL"]=1; safe["OTEL_EXPORTER_OTLP_ENDPOINT"]=1;
      safe["LLM_ENDPOINT_OPENAI"]=1; safe["LLM_ENDPOINT_ANTHROPIC"]=1;
      safe["LOCAL_LLM_BASE_URL"]=1; safe["LOCAL_LLM_MODEL"]=1;
      safe["JOURNAL_LINES"]=1; safe["LOG_TAIL_LINES"]=1;
    }
    /^[[:space:]]*#/ || NF==0 { print; next }
    /=/ {
      eq=index($0,"=");
      key=substr($0,1,eq-1);
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", key);
      if (key in safe) { print }
      else if (substr($0,eq+1)=="") { print }
      else { printf "%s=***REDACTED***\n", key }
      next
    }
    { print }
  ' "${ENV_FILE}" > "${BUNDLE_ROOT}/env.redacted.txt"
else
  echo "(no .env file at ${ENV_FILE})" > "${BUNDLE_ROOT}/env.redacted.txt"
fi

# ── 10. versions.txt ──────────────────────────────────────────────
{
  echo "=== ArionComply codebase ==="
  if [[ -d "${ARION_ROOT}/.git" ]]; then
    ( cd "${ARION_ROOT}" && git rev-parse HEAD 2>&1 )
    ( cd "${ARION_ROOT}" && git log -1 --format='%s (%ci)' 2>&1 )
    ( cd "${ARION_ROOT}" && git status --short 2>&1 | head -10 )
  else
    echo "(not a git checkout)"
  fi
  echo ""
  echo "=== Python ==="
  python3 --version 2>&1 || echo "(python3 missing)"
  echo ""
  echo "=== Postgres ==="
  psql --version 2>&1 || echo "(psql missing)"
  pg_config --version 2>&1 || true
  echo ""
  echo "=== Neo4j ==="
  neo4j --version 2>&1 | head -3 || echo "(neo4j CLI missing)"
  echo ""
  echo "=== Chroma (via pip) ==="
  python3 -c "import chromadb; print(chromadb.__version__)" 2>&1 || echo "(chromadb not importable)"
  echo ""
  echo "=== pip freeze (top-level ArionComply deps only) ==="
  pip3 freeze 2>&1 | grep -Ei '^(fastapi|langgraph|langchain|neo4j|chromadb|psycopg|openai|anthropic|opentelemetry|pydantic|uvicorn)' | sort || true
} > "${BUNDLE_ROOT}/versions.txt"

# ── 11. deploy_state.md ───────────────────────────────────────────
{
  echo "# Deployment state"
  echo ""
  echo "- **Bundle timestamp**: ${STAMP}"
  echo "- **Hostname**:         $(hostname -f 2>/dev/null || hostname)"
  echo "- **Install root**:     ${ARION_ROOT}"
  echo "- **Env file**:         ${ENV_FILE} $(if [[ -f "${ENV_FILE}" ]]; then echo "(present)"; else echo "(MISSING)"; fi)"
  echo ""
  echo "## Systemd unit states"
  for svc in arioncomply-api arioncomply-chroma arioncomply-jaeger arioncomply-phoenix; do
    if have systemctl; then
      state="$(systemctl is-active "${svc}" 2>/dev/null || echo unknown)"
      enabled="$(systemctl is-enabled "${svc}" 2>/dev/null || echo unknown)"
      echo "- ${svc}: active=${state} enabled=${enabled}"
    else
      echo "- ${svc}: (systemctl unavailable)"
    fi
  done
  echo ""
  echo "## Port listeners"
  for port in 8080 8000 8001 7474 7687 16686 6006; do
    if have ss && ss -tln 2>/dev/null | grep -q ":${port} "; then
      echo "- :${port} — bound"
    elif have lsof && lsof -iTCP:${port} -sTCP:LISTEN -P -n >/dev/null 2>&1; then
      echo "- :${port} — bound"
    else
      echo "- :${port} — not listening"
    fi
  done
  echo ""
  echo "## What to look at first"
  echo ""
  echo "1. \`services.txt\` — did any systemd unit fail?"
  echo "2. \`deploy_state.md\` — port listeners match expected services?"
  echo "3. \`journal-api.txt\` (last ${JOURNAL_LINES} lines) — API startup errors?"
  echo "4. \`postgres.txt\` — DB reachable, expected extensions?"
  echo "5. \`neo4j.txt\` — RequirementNode + ChecklistItem counts non-zero?"
  echo "6. \`chroma.txt\` — 5 collections present with non-zero counts?"
} > "${BUNDLE_ROOT}/deploy_state.md"

# ── Package ───────────────────────────────────────────────────────
cd "${BUNDLE_DIR}"
if [[ "${STDOUT_MODE}" -eq 1 ]]; then
  tar -czf - "${BUNDLE_NAME}"
  rm -rf "${BUNDLE_DIR}"
  exit 0
fi

OUT="/tmp/${BUNDLE_NAME}.tar.gz"
tar -czf "${OUT}" "${BUNDLE_NAME}"
rm -rf "${BUNDLE_DIR}"

echo ""
echo "Diagnostic bundle written: ${OUT}"
echo "Size: $(du -h "${OUT}" | cut -f1)"
echo ""
echo "To share with support, upload this tarball or attach to an email."
echo "Contents are structured plain text; unpack locally to inspect first:"
echo "    tar -tzf ${OUT}"
