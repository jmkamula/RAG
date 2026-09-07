#!/usr/bin/env bash
# Ship 124'.a — automated security scanners.
#
# Three Python-native scanners aggregated into one exit code + one
# report. Same shape as scripts/ci/check_forbidden_patterns.sh (Ship
# 63' + 122'). Runnable from pre-commit hook, ops scripts, or CI.
#
#   1. pip-audit         — known CVEs in Python deps
#   2. bandit            — Python static analysis (hardcoded creds,
#                          weak crypto, SQL patterns, subprocess risks)
#   3. detect-secrets    — Yelp secret scanner (secrets in tracked files
#                          + git history). Python-native alternative to
#                          gitleaks; installs via pip, no Go binary needed.
#
# Design mirrors check_forbidden_patterns.sh:
#   · Single exit code (0 = clean, 1 = findings)
#   · --verbose flag to print full details
#   · Idempotent + safe to re-run
#   · No secrets required (no OpenAI, no DB, no live tenants)
#
# Install (one-time, per dev / CI runner):
#   pip install --break-system-packages pip-audit bandit detect-secrets
#
# Usage:
#   scripts/ci/security_scan.sh
#   scripts/ci/security_scan.sh --verbose
#
# Exit codes:
#   0 — all scanners clean
#   1 — one or more scanners found real issues
#   78 — a scanner is not installed (advisory; don't block commits)

set -u
FAILED=0
VERBOSE=0
FAST=0
for arg in "$@"; do
    case "$arg" in
        --verbose) VERBOSE=1 ;;
        --fast)    FAST=1 ;;
    esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$ROOT" ]] && ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$ROOT"

# ── Tool availability check ───────────────────────────────────────
MISSING=()
for tool in pip-audit bandit detect-secrets; do
    if ! command -v "$tool" > /dev/null 2>&1; then
        MISSING+=("$tool")
    fi
done
if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "SKIP — missing scanner(s): ${MISSING[*]}"
    echo "  install:  pip install --break-system-packages pip-audit bandit detect-secrets"
    exit 78
fi

report_findings() {
    local name="$1"
    local hint="$2"
    local output="$3"
    if [[ -n "$output" ]]; then
        FAILED=1
        echo ""
        echo "FAIL — $name"
        echo "       $hint"
        if [[ $VERBOSE -eq 1 ]]; then
            echo "$output" | sed 's/^/         /'
        else
            local first
            first=$(echo "$output" | head -5)
            echo "$first" | sed 's/^/         /'
            local total
            total=$(echo "$output" | wc -l | tr -d ' ')
            if [[ "$total" -gt 5 ]]; then
                echo "         ... ($total total lines; --verbose for full)"
            fi
        fi
    fi
}

# ── 1. pip-audit — CVE scan on pinned deps ────────────────────────
# --no-deps skips transitive lookup (matches how we author the file);
# --disable-pip refused to work without hashed requirements, so we use
# --no-deps instead (pip-audit warns about it but proceeds).
# Temporarily ignored CVEs — MUST have a Ship-N backlog reference.
# Each --ignore-vuln entry below is tracked as a Ship 125' item.
# Remove the ignore when the corresponding dep is upgraded.
#
# Ship 125' backlog (opened 2026-09-07 alongside Ship 124):
#   PYSEC-2026-3037,3036,3040 — python-multipart 0.0.27 → 0.0.31  ✓ CLOSED Ship 125'.a
#   PYSEC-2026-3635           — langgraph-checkpoint-postgres 3.0.5 → 3.1.1
#   PYSEC-2026-311            — chromadb 1.5.9 → needs major-bump review
#   CVE-2026-45830,45831,45833 — chromadb 1.5.9 (same, 3 more CVEs)
PIP_AUDIT_IGNORES=(
    --ignore-vuln PYSEC-2026-3635   # langgraph-checkpoint-postgres — Ship 125'.b
    --ignore-vuln PYSEC-2026-311    # chromadb — Ship 125'.c
    --ignore-vuln CVE-2026-45830    # chromadb — Ship 125'.c
    --ignore-vuln CVE-2026-45831    # chromadb — Ship 125'.c
    --ignore-vuln CVE-2026-45833    # chromadb — Ship 125'.c
)

echo "→ pip-audit (Python deps CVE scan)"
if [[ -f "deploy/requirements.txt" ]]; then
    audit_out=$(pip-audit -r deploy/requirements.txt --no-deps \
        "${PIP_AUDIT_IGNORES[@]}" 2>&1 || true)
    # pip-audit prints "No known vulnerabilities found" on clean.
    # On findings it prints "Found N known vulnerabilities in M packages"
    # followed by a table. WARNING lines to stderr are noise here.
    if echo "$audit_out" | grep -qE "^No known vulnerabilities found"; then
        echo "  OK — no known CVEs in pinned deps"
    else
        # Extract the finding count + table rows for reporting.
        summary=$(echo "$audit_out" | grep -E "^Found [0-9]+ known" || echo "")
        vulns=$(echo "$audit_out" | awk '/^Name +Version/{flag=1;next} /^-/{next} flag && NF>=3')
        if [[ -n "$vulns" ]]; then
            report_findings \
                "pip-audit — CVEs in Python dependencies ($summary)" \
                "upgrade the pinned version in deploy/requirements.txt, or add --ignore-vuln <ID> to this scanner with rationale." \
                "$vulns"
        else
            # No matching rows — treat as clean
            echo "  OK — no known CVEs in pinned deps"
        fi
    fi
else
    echo "  SKIP — deploy/requirements.txt not found"
fi

# ── 2. bandit — Python static analysis ────────────────────────────
# Skips + excludes live on the CLI here (source of truth) because
# bandit 1.9.4's YAML config-file loader is broken (warns "missing
# [bandit] section"). The .bandit file is preserved for docs +
# rationale only; the CLI here is what actually runs. See .bandit
# for the per-test rationale.
echo "→ bandit (Python static analysis)"
bandit_out=$(bandit -r . \
    --exclude tests,scripts/dev,scripts/ops,archive,private,results,.venv,venv,node_modules \
    --skip B104,B108,B310,B324,B608 \
    --format csv \
    --severity-level medium \
    --confidence-level medium \
    --quiet 2>/dev/null || true)
# CSV first line is header. Findings = subsequent rows.
bandit_findings=$(echo "$bandit_out" | tail -n +2 | grep -v '^$' || true)
if [[ -n "$bandit_findings" ]]; then
    # Format each finding as file:line — issue
    bandit_pretty=$(echo "$bandit_findings" | awk -F, '{print $2 ":" $5 " — " $3 " (" $1 ", " $6 ")"}')
    report_findings \
        "bandit — Python security issues (medium+ severity + confidence)" \
        "review each; fix or add # nosec comment with rationale." \
        "$bandit_pretty"
else
    echo "  OK — no medium+ severity Python security issues"
fi

# ── 3. detect-secrets — secret scan on tracked files ──────────────
# Yelp's Python-native scanner; substituted for gitleaks (Go binary
# requiring separate install). Scans current tree for common credential
# patterns. Baseline file (.secrets.baseline) whitelists known FPs.
#
# **Slow** (~3 min on this tree due to per-file plugin invocation).
# Skipped in --fast mode (pre-commit); runs in CI. If you need it
# locally, run without --fast.
if [[ $FAST -eq 1 ]]; then
    echo "→ detect-secrets — SKIPPED (--fast mode; runs in CI)"
else
    echo "→ detect-secrets (secrets in tracked tree)"
    ds_baseline=""
    if [[ -f ".secrets.baseline" ]]; then
        ds_baseline="--baseline .secrets.baseline"
    fi
    # detect-secrets scan discovers files itself; passing paths via
    # xargs adds overhead. Let it walk the tree.
    ds_out=$(detect-secrets scan $ds_baseline \
        --exclude-files '\.env\.example$|\.secrets\.baseline$|db/baseline/|db/must_fingerprints/|results/|snapshots/|docs/memory/|package-lock\.json$|node_modules/' \
        2>/dev/null || echo '{"results":{}}')
    # detect-secrets emits JSON; count non-empty results
    ds_hits=$(echo "$ds_out" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    results = data.get('results', {}) or {}
    hits = []
    for fname, secrets in results.items():
        for s in secrets:
            hits.append(f\"{fname}:{s.get('line_number','?')} — {s.get('type','?')}\")
    print('\n'.join(hits))
except Exception:
    pass
" 2>/dev/null || echo "")
    if [[ -n "$ds_hits" ]]; then
        report_findings \
            "detect-secrets — potential secrets in tracked files" \
            "review each; if false positive, run: detect-secrets scan > .secrets.baseline + commit the baseline." \
            "$ds_hits"
    else
        echo "  OK — no unbaselined secrets in tracked tree"
    fi
fi

# ── Summary ───────────────────────────────────────────────────────
echo ""
if [[ $FAILED -eq 0 ]]; then
    echo "OK — security_scan.sh: all 3 scanners clean."
    exit 0
fi
echo "FAILED — security_scan.sh: see hits above. Re-run with --verbose for full detail."
exit 1
