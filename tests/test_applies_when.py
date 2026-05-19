"""
Unit tests for rag/posture/applies_when.py — the applies_when DSL.

Standalone script. Each test returns (ok, message). main() prints PASS/FAIL
and returns exit code 0 iff all pass.

Run:
  PYTHONPATH=/data/arioncomply python3 tests/test_applies_when.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))

from rag.posture.applies_when import (
    EvalContext,
    EvalError,
    LexError,
    ParseError,
    ValidationContext,
    ValidationError,
    evaluate,
    parse,
    parse_validate_evaluate,
    render,
    tokenize,
    validate,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _vctx() -> ValidationContext:
    return ValidationContext(
        boolean_fact_slugs={
            "uses_cloud_services", "public_authority", "processes_personal_data",
            "high_risk_processing", "develops_software", "uses_processors",
        },
        text_fact_slugs={"sector"},
        leaf_ids={"ER:risk_register", "ER:cloud_services_register"},
        role_tags={"policy", "register", "procedure", "drill_record"},
    )

def _ectx(**overrides) -> EvalContext:
    facts = {
        "uses_cloud_services":     True,
        "public_authority":        False,
        "processes_personal_data": True,
        "high_risk_processing":    False,
        "develops_software":       True,
        "uses_processors":         False,
        "sector":                  "technology",
    }
    facts.update(overrides.get("facts", {}))
    supply_exists = overrides.get("supply_exists_fn", lambda t: False)
    supply_count  = overrides.get("supply_count_fn",  lambda t: 0)
    return EvalContext(facts=facts, supply_exists_fn=supply_exists, supply_count_fn=supply_count)


# ── Lexer tests ───────────────────────────────────────────────────────────────

def test_lex_basic():
    toks = tokenize('fact("x") and not supply_count("ER:r") >= 1')
    kinds = [t.kind for t in toks]
    expect = ['IDENT', 'LPAREN', 'STRING', 'RPAREN',
              'IDENT', 'IDENT', 'IDENT', 'LPAREN', 'STRING', 'RPAREN',
              'OP', 'INT', 'EOF']
    if kinds != expect:
        return False, f"kind sequence {kinds!r} != {expect!r}"
    return True, "10 tokens + EOF as expected"

def test_lex_empty_source_rejected():
    try:
        tokenize("")
    except LexError as e:
        return True, f"empty source raises LexError: {e}"
    return False, "empty source did not raise"

def test_lex_unterminated_string():
    try:
        tokenize('fact("oops')
    except LexError:
        return True, "unterminated string raises LexError"
    return False, "unterminated string did not raise"

def test_lex_bare_bang_rejected():
    try:
        tokenize('not fact("x") ! 1')
    except LexError:
        return True, "bare '!' raises LexError"
    return False, "bare '!' did not raise"


# ── Parser tests ──────────────────────────────────────────────────────────────

def test_parse_precedence_and_or():
    # a or b and c  →  a or (b and c)
    ast = parse('fact("a") or fact("b") and fact("c")')
    from rag.posture.applies_when import BinOp, FuncCall
    if not isinstance(ast, BinOp) or ast.op != "or":
        return False, f"top-level should be 'or', got {ast!r}"
    if not isinstance(ast.right, BinOp) or ast.right.op != "and":
        return False, "right side should be the 'and'"
    return True, "and binds tighter than or"

def test_parse_not_applies_to_immediate():
    # not a and b  →  (not a) and b
    ast = parse('not fact("a") and fact("b")')
    from rag.posture.applies_when import BinOp, UnaryNot
    if not isinstance(ast, BinOp) or ast.op != "and":
        return False, "top-level should be 'and'"
    if not isinstance(ast.left, UnaryNot):
        return False, "left side should be 'not'"
    return True, "not binds tighter than and"

def test_parse_comparison_returns_binop():
    ast = parse('supply_count("policy") >= 2')
    from rag.posture.applies_when import BinOp
    if not isinstance(ast, BinOp) or ast.op != ">=":
        return False, f"expected '>=' BinOp, got {ast!r}"
    return True, ">= parsed as BinOp"

def test_parse_parens_override():
    # (a or b) and c
    ast = parse('(fact("a") or fact("b")) and fact("c")')
    from rag.posture.applies_when import BinOp
    if not isinstance(ast, BinOp) or ast.op != "and":
        return False, "top-level should be 'and'"
    if not isinstance(ast.left, BinOp) or ast.left.op != "or":
        return False, "parens should make left side an 'or'"
    return True, "parens overrode precedence"

def test_parse_rejects_dangling_keyword():
    try:
        parse('and fact("a")')
    except ParseError:
        return True, "dangling 'and' rejected"
    return False, "dangling 'and' parsed somehow"


# ── Validator tests ───────────────────────────────────────────────────────────

def test_validate_unknown_function():
    ast = parse('something_made_up("x")')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "unknown function" in str(e):
            return True, "unknown function rejected"
    return False, "unknown function not caught"

def test_validate_unknown_fact_slug():
    ast = parse('fact("never_heard_of_this")')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "unknown boolean fact slug" in str(e):
            return True, "unknown fact slug rejected"
    return False, "unknown fact slug not caught"

def test_validate_unknown_leaf_id():
    ast = parse('supply_exists("ER:does_not_exist")')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "unknown leaf id" in str(e):
            return True, "unknown leaf id rejected"
    return False, "unknown leaf id not caught"

def test_validate_unknown_role_tag():
    ast = parse('supply_exists("not_a_real_role")')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "unknown role tag" in str(e):
            return True, "unknown role tag rejected"
    return False, "unknown role tag not caught"

def test_validate_top_level_must_be_bool():
    ast = parse('supply_count("policy")')   # returns int
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "must be bool" in str(e):
            return True, "int-typed top-level rejected"
    return False, "int-typed top-level not caught"

def test_validate_text_fact_via_fact_eq():
    ast = parse('fact_eq("sector", "technology")')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        return False, f"valid fact_eq rejected: {e}"
    return True, "fact_eq on text fact validates"

def test_validate_fact_eq_unknown_slug():
    ast = parse('fact_eq("not_a_text_fact", "x")')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "unknown text fact slug" in str(e):
            return True, "unknown text fact rejected"
    return False, "unknown text fact not caught"

def test_validate_comparison_requires_int_operands():
    # supply_exists returns bool, can't be compared
    ast = parse('supply_exists("policy") >= 1')
    try:
        validate(ast, _vctx())
    except ValidationError as e:
        if "requires int operands" in str(e):
            return True, "bool >= int rejected"
    return False, "bool in comparison not caught"


# ── Evaluator tests ───────────────────────────────────────────────────────────

def test_eval_fact_true():
    ast = parse('fact("uses_cloud_services")')
    if not evaluate(ast, _ectx()):
        return False, "uses_cloud_services should be True"
    return True, "fact() returns True"

def test_eval_not_inverts():
    ast = parse('not fact("uses_cloud_services")')
    if evaluate(ast, _ectx()):
        return False, "not True should be False"
    return True, "not inverts"

def test_eval_and_short_circuit_value():
    ast = parse('fact("uses_cloud_services") and not fact("public_authority")')
    if not evaluate(ast, _ectx()):
        return False, "True and not False should be True"
    return True, "and composes correctly"

def test_eval_or_composition():
    ast = parse('fact("public_authority") or fact("processes_personal_data")')
    if not evaluate(ast, _ectx()):
        return False, "False or True should be True"
    return True, "or composes correctly"

def test_eval_fact_eq():
    ast = parse('fact_eq("sector", "technology")')
    if not evaluate(ast, _ectx()):
        return False, "fact_eq sector=technology should be True"
    ast2 = parse('fact_eq("sector", "finance")')
    if evaluate(ast2, _ectx()):
        return False, "fact_eq sector=finance should be False"
    return True, "fact_eq works for both true and false cases"

def test_eval_supply_exists_via_injected_fn():
    ast = parse('supply_exists("policy")')
    ec = _ectx(supply_exists_fn=lambda t: t == "policy")
    if not evaluate(ast, ec):
        return False, "policy should exist"
    ec2 = _ectx(supply_exists_fn=lambda t: False)
    if evaluate(ast, ec2):
        return False, "nothing should exist"
    return True, "supply_exists wired through context"

def test_eval_supply_count_with_comparison():
    ast = parse('supply_count("policy") >= 2')
    ec_with    = _ectx(supply_count_fn=lambda t: 3)
    ec_without = _ectx(supply_count_fn=lambda t: 1)
    if not evaluate(ast, ec_with):
        return False, "3 >= 2 should be True"
    if evaluate(ast, ec_without):
        return False, "1 >= 2 should be False"
    return True, "supply_count comparisons work"

def test_eval_phase2_rejected():
    ast = parse('fact_value("headcount") >= 100')
    try:
        evaluate(ast, _ectx())
    except EvalError as e:
        if "Phase 2" in str(e):
            return True, "fact_value rejected at eval time"
    return False, "Phase 2 function not rejected"


# ── Renderer tests ────────────────────────────────────────────────────────────

def test_render_humanizes_known_slugs():
    ast = parse('fact("uses_cloud_services") and not fact("public_authority")')
    rendered = render(ast)
    if "uses cloud services" not in rendered:
        return False, f"expected humanised slug, got: {rendered!r}"
    if "is a public authority" not in rendered:
        return False, f"expected humanised public_authority, got: {rendered!r}"
    return True, f"rendered: {rendered}"

def test_render_supply_exists_strips_er_prefix():
    ast = parse('supply_exists("ER:risk_register")')
    rendered = render(ast)
    if "risk_register" not in rendered or "ER:" in rendered:
        return False, f"ER: prefix should be stripped in display: {rendered!r}"
    return True, f"rendered: {rendered}"


# ── End-to-end convenience ────────────────────────────────────────────────────

def test_parse_validate_evaluate_happy_path():
    src = 'fact("uses_cloud_services") and not fact("public_authority")'
    result = parse_validate_evaluate(src, _vctx(), _ectx())
    if result is not True:
        return False, f"expected True, got {result!r}"
    return True, "parse_validate_evaluate happy path OK"


# ── Test runner ───────────────────────────────────────────────────────────────

TESTS = [
    # Lexer
    test_lex_basic,
    test_lex_empty_source_rejected,
    test_lex_unterminated_string,
    test_lex_bare_bang_rejected,
    # Parser
    test_parse_precedence_and_or,
    test_parse_not_applies_to_immediate,
    test_parse_comparison_returns_binop,
    test_parse_parens_override,
    test_parse_rejects_dangling_keyword,
    # Validator
    test_validate_unknown_function,
    test_validate_unknown_fact_slug,
    test_validate_unknown_leaf_id,
    test_validate_unknown_role_tag,
    test_validate_top_level_must_be_bool,
    test_validate_text_fact_via_fact_eq,
    test_validate_fact_eq_unknown_slug,
    test_validate_comparison_requires_int_operands,
    # Evaluator
    test_eval_fact_true,
    test_eval_not_inverts,
    test_eval_and_short_circuit_value,
    test_eval_or_composition,
    test_eval_fact_eq,
    test_eval_supply_exists_via_injected_fn,
    test_eval_supply_count_with_comparison,
    test_eval_phase2_rejected,
    # Renderer
    test_render_humanizes_known_slugs,
    test_render_supply_exists_strips_er_prefix,
    # End-to-end
    test_parse_validate_evaluate_happy_path,
]


def main() -> int:
    print("─" * 70)
    print("  applies_when DSL — unit tests")
    print("─" * 70)
    failures = 0
    for t in TESTS:
        try:
            ok, msg = t()
        except Exception as e:
            ok, msg = False, f"raised {type(e).__name__}: {e}"
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {t.__name__}")
        print(f"         {msg}")
        if not ok:
            failures += 1
    print("─" * 70)
    print(f"  {len(TESTS) - failures}/{len(TESTS)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
