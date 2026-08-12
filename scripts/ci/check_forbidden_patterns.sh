#!/usr/bin/env bash
# Ship 63' — CI grep guards against patterns we've root-caused.
#
# Two tight guards where the pattern has a canonical location and
# any new occurrence is a genuine regression. Broader disciplines
# (hardcoded model strings, uncoordinated document_findings reads,
# direct openai imports) are documented in the codebase memory but
# not enforced here — the false-positive rate on those grep
# patterns is too high to be actionable in CI.
#
#   1. Naive `if ref in answer:` in the forbidden_refs / expected_refs
#      assertion loops in tests/eval_suite.py. Ship 60'.k root-caused
#      the "stochastic physical-leak" FAIL to this substring check.
#      Pattern to use:
#          re.search(re.escape(ref) + r'(?!\.\d)', answer)
#      (word boundary + drop when followed by ".digit" subref).
#
#   2. Direct evaluate_one_control() outside its owner module + the
#      Ship 60'.b advisory fallback + Stage-2 detail UI. Ships 58/60/61
#      consolidated per-MUST fulfilment reads on
#      rag.posture.must_verdicts.read_must_verdicts_by_control. New
#      callers should read SSoT, not re-run the engine.
#
#   3. `finding == 'N/A'` scope-check outside the Ship 66' allowlist.
#      Ship 66'.a split scope from evidence assessment: new consumers
#      that gate on N/A should read `applicability_status == 'na'`
#      per [[feedback-na-dominance-via-applicability-column]]. Five
#      pre-Ship-66' sites are allowlisted; the guard fails on any
#      NEW addition.
#
# Usage:
#   scripts/ci/check_forbidden_patterns.sh
#   scripts/ci/check_forbidden_patterns.sh --verbose   # print hit lines

set -u
FAILED=0
VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$ROOT" ]] && ROOT="$(dirname "$(dirname "$(readlink -f "$0")")")"
cd "$ROOT"

report() {
    local name="$1"
    local hint="$2"
    shift 2
    local hits
    hits="$(git grep -nE "$@" 2>/dev/null || true)"
    if [[ -n "$hits" ]]; then
        FAILED=1
        echo ""
        echo "FAIL — $name"
        echo "       $hint"
        if [[ $VERBOSE -eq 1 ]]; then
            echo "$hits" | sed 's/^/         /'
        else
            local count
            count=$(echo "$hits" | wc -l | tr -d ' ')
            echo "       $count hit(s); re-run with --verbose to list."
        fi
    fi
}

# 1 — naive substring on forbidden_refs / expected_refs. The correct
#     pattern uses re.search with word-boundary + negative lookahead.
#     Scope: eval_suite.py only. Ship 60'.k documented the collision
#     between "A.7.1" (forbidden) and "A.7.1.5" (legitimate ISO 27701
#     sub-clause). The fix lives at lines 4885-ish; guarding against
#     a re-introduction there.
report \
    "Naive 'if ref in answer:' in eval_suite forbidden_refs loop" \
    "Ship 60'.k — use re.search(re.escape(ref) + r'(?!\\.\\d)', answer)." \
    'for ref in case\.forbidden_refs:' \
    -- tests/eval_suite.py \
    | true
# The above catches the loop header. Now catch the substring itself
# only WITHIN the forbidden loop body. `git grep -A` isn't
# universally available, so we do a two-line window check via awk.
subs_hits=$(awk '
    /for ref in case\.forbidden_refs:/ { in_loop=1; next }
    in_loop && /if ref in answer:/ { print FILENAME ":" NR ":" $0; in_loop=0 }
    /^def / { in_loop=0 }
' tests/eval_suite.py)
if [[ -n "$subs_hits" ]]; then
    FAILED=1
    echo ""
    echo "FAIL — Naive substring in forbidden_refs loop (no lookahead)"
    echo "       Ship 60'.k — pattern must include (?!\\.\\d) negative lookahead."
    if [[ $VERBOSE -eq 1 ]]; then
        echo "$subs_hits" | sed 's/^/         /'
    else
        count=$(echo "$subs_hits" | wc -l | tr -d ' ')
        echo "       $count hit(s); re-run with --verbose to list."
    fi
fi

# 2 — direct evaluate_one_control() outside the allowlist.
#     Allowlist:
#       - engine_runner.py (owner)
#       - advisory.py (Ship 60'.b legacy fallback)
#       - api_server.py:~2252 (Stage-2 detail UI — evaluate_one_control's
#         documented intended user per its docstring)
#       - scripts/dev/** (audit + repro scripts)
report \
    "Direct evaluate_one_control() outside owner + allowed fallback sites" \
    "Ship 60'.b — read from SSoT via rag.posture.must_verdicts instead." \
    'evaluate_one_control\(' \
    -- '*.py' \
    ':!rag/posture/engine_runner.py' \
    ':!rag/posture/advisory.py' \
    ':!api_server.py' \
    ':!scripts/**' \
    ':!tests/**'

# 3 — `finding == 'N/A'` scope-check outside the Ship 66' allowlist.
#     Ship 66'.a split scope (applicability_status) from evidence
#     assessment (finding). New consumers should read
#     applicability_status == 'na' instead. Five pre-Ship-66' sites
#     are allowlisted; guard fails on new additions.
#     When a deferred site migrates: remove its allowlist entry.
report \
    "finding == 'N/A' scope check outside Ship 66' allowlist" \
    "Ship 66' — use applicability_status == 'na' (see [[feedback-na-dominance-via-applicability-column]])." \
    '(finding\s*==\s*.N/A.|finding.*=\s*.N/A.|"finding":\s*"N/A")' \
    -- '*.py' \
    ':!rag/scope_filter.py' \
    ':!rag/resolver.py' \
    ':!rag/arion_graph.py' \
    ':!rag/posture_loader.py' \
    ':!tests/**' \
    ':!scripts/**' \
    ':!snapshots/**' \
    ':!db/workbook_importer.py' \
    ':!rag/llm_answer.py'

if [[ $FAILED -eq 0 ]]; then
    echo "OK — no forbidden patterns."
    exit 0
fi
echo ""
echo "FAILED — see hits above. Re-run with --verbose for line numbers."
exit 1
