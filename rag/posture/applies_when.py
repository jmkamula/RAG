"""ArionComply — applies_when DSL.

Tiny boolean DSL that gates whether a FulfilmentSpec or :REQUIRES_EVIDENCE
edge applies to a tenant at posture time.

Phase 1 primitives:
  fact(slug)             -> bool   (reads client_facts.<slug>)
  fact_eq(slug, value)   -> bool   (text-valued facts; today: 'sector')
  supply_exists(target)  -> bool   (any matching artifact uploaded)
  supply_count(target)   -> int    (count; comparison only)

Combinators: and, or, not
Comparisons: >=, >, <=, <, =, !=   (int operands only)

Phase 2 reservations (parser-known, eval-rejected):
  fact_value(slug), register_count(subtype), date_after(slug, date_literal)

Target convention for supply_exists/supply_count:
  "ER:<leaf-id>"  → strict leaf id (mandatory prefix)
  any other slug  → role tag

Empty source string is an error. NULL on the storage side means "always
applies" — that's the caller's job to short-circuit.

Public API:
  parse(source)                          -> Ast
  validate(ast, validation_ctx)          -> None
  evaluate(ast, eval_ctx)                -> bool | int
  render(ast)                            -> str
  parse_validate_evaluate(source, ...)   -> bool
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Union


# ── AST ────────────────────────────────────────────────────────────────────────

@dataclass
class IntLit:
    value: int

@dataclass
class FuncCall:
    name: str
    args: list  # list[str | int]; string literals stay str, int literals stay int

@dataclass
class UnaryNot:
    operand: "AstNode"

@dataclass
class BinOp:
    op: str             # 'and' | 'or' | one of CMP_OPS
    left: "AstNode"
    right: "AstNode"

AstNode = Union[IntLit, FuncCall, UnaryNot, BinOp]


# ── Constants ──────────────────────────────────────────────────────────────────

CMP_OPS = {">=", ">", "<=", "<", "=", "!="}

# Functions known to the parser; (returns_int, fixed arity)
KNOWN_FUNCS: dict[str, tuple[str, int]] = {
    # name              : (return_type,  arity)
    "fact":               ("bool", 1),
    "fact_eq":            ("bool", 2),
    "supply_exists":      ("bool", 1),
    "supply_count":       ("int",  1),
    # Phase 2 reservations — recognised by parser, rejected at evaluate time
    "fact_value":         ("PHASE2", 1),
    "register_count":     ("PHASE2", 1),
    "date_after":         ("PHASE2", 2),
}

PHASE2_FUNCS = {n for n, (rt, _) in KNOWN_FUNCS.items() if rt == "PHASE2"}


# ── Errors ─────────────────────────────────────────────────────────────────────

class AppliesWhenError(Exception): pass
class LexError(AppliesWhenError): pass
class ParseError(AppliesWhenError): pass
class ValidationError(AppliesWhenError): pass
class EvalError(AppliesWhenError): pass


# ── Lexer ──────────────────────────────────────────────────────────────────────

@dataclass
class Token:
    kind: str   # 'IDENT' | 'STRING' | 'INT' | 'OP' | 'LPAREN' | 'RPAREN' | 'COMMA' | 'EOF'
    value: str
    pos: int

def tokenize(source: str) -> list[Token]:
    if source == "":
        raise LexError("applies_when source is empty; use NULL on the storage side for 'always applies'")
    tokens: list[Token] = []
    i, n = 0, len(source)
    while i < n:
        c = source[i]
        if c.isspace():
            i += 1
            continue
        if c == "(":
            tokens.append(Token("LPAREN", "(", i)); i += 1
        elif c == ")":
            tokens.append(Token("RPAREN", ")", i)); i += 1
        elif c == ",":
            tokens.append(Token("COMMA", ",", i)); i += 1
        elif c == '"':
            end = source.find('"', i + 1)
            if end < 0:
                raise LexError(f"unterminated string literal at pos {i}")
            tokens.append(Token("STRING", source[i + 1:end], i))
            i = end + 1
        elif c.isdigit():
            j = i
            while j < n and source[j].isdigit():
                j += 1
            tokens.append(Token("INT", source[i:j], i))
            i = j
        elif c.isalpha() and c.islower():
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            tokens.append(Token("IDENT", source[i:j], i))
            i = j
        elif c in "<>=!":
            if i + 1 < n and source[i + 1] == "=":
                tokens.append(Token("OP", source[i:i + 2], i)); i += 2
            elif c in "<>=":
                tokens.append(Token("OP", c, i)); i += 1
            else:  # '!' without '='
                raise LexError(f"unexpected character {c!r} at pos {i} (did you mean '!='?)")
        else:
            raise LexError(f"unexpected character {c!r} at pos {i}")
    tokens.append(Token("EOF", "", n))
    return tokens


# ── Parser ─────────────────────────────────────────────────────────────────────

class _Parser:
    def __init__(self, tokens: list[Token]):
        self.toks = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.toks[self.i]

    def eat(self, kind: str, value: str | None = None) -> Token:
        t = self.toks[self.i]
        if t.kind != kind or (value is not None and t.value != value):
            want = f"{kind}({value!r})" if value else kind
            raise ParseError(f"expected {want} at pos {t.pos}, got {t.kind}({t.value!r})")
        self.i += 1
        return t

    def parse(self) -> AstNode:
        node = self._or_expr()
        self.eat("EOF")
        return node

    def _or_expr(self) -> AstNode:
        node = self._and_expr()
        while self.peek().kind == "IDENT" and self.peek().value == "or":
            self.eat("IDENT", "or")
            right = self._and_expr()
            node = BinOp("or", node, right)
        return node

    def _and_expr(self) -> AstNode:
        node = self._not_expr()
        while self.peek().kind == "IDENT" and self.peek().value == "and":
            self.eat("IDENT", "and")
            right = self._not_expr()
            node = BinOp("and", node, right)
        return node

    def _not_expr(self) -> AstNode:
        if self.peek().kind == "IDENT" and self.peek().value == "not":
            self.eat("IDENT", "not")
            return UnaryNot(self._not_expr())
        return self._comparison()

    def _comparison(self) -> AstNode:
        left = self._primary()
        if self.peek().kind == "OP" and self.peek().value in CMP_OPS:
            op = self.eat("OP").value
            right = self._primary()
            return BinOp(op, left, right)
        return left

    def _primary(self) -> AstNode:
        t = self.peek()
        if t.kind == "LPAREN":
            self.eat("LPAREN")
            node = self._or_expr()
            self.eat("RPAREN")
            return node
        if t.kind == "INT":
            self.eat("INT")
            return IntLit(int(t.value))
        if t.kind == "IDENT":
            # Reject bare keywords that aren't function calls here
            if t.value in ("and", "or", "not"):
                raise ParseError(f"unexpected keyword {t.value!r} at pos {t.pos}")
            name = self.eat("IDENT").value
            self.eat("LPAREN")
            args: list = []
            if self.peek().kind != "RPAREN":
                args.append(self._arg())
                while self.peek().kind == "COMMA":
                    self.eat("COMMA")
                    args.append(self._arg())
            self.eat("RPAREN")
            return FuncCall(name, args)
        raise ParseError(f"unexpected token {t.kind}({t.value!r}) at pos {t.pos}")

    def _arg(self):
        t = self.peek()
        if t.kind == "STRING":
            self.eat("STRING")
            return t.value
        if t.kind == "INT":
            self.eat("INT")
            return int(t.value)
        raise ParseError(f"expected STRING or INT arg at pos {t.pos}, got {t.kind}")


def parse(source: str) -> AstNode:
    return _Parser(tokenize(source)).parse()


# ── Validator ──────────────────────────────────────────────────────────────────

@dataclass
class ValidationContext:
    boolean_fact_slugs: set[str] = field(default_factory=set)
    text_fact_slugs:    set[str] = field(default_factory=set)
    leaf_ids:           set[str] = field(default_factory=set)   # full ids incl. 'ER:' prefix? See note.
    role_tags:          set[str] | None = None   # None disables role validation

def _node_type(node: AstNode, ctx: ValidationContext) -> str:
    """Recursively type-check and return 'bool' or 'int'. Raises ValidationError."""
    if isinstance(node, IntLit):
        return "int"
    if isinstance(node, UnaryNot):
        t = _node_type(node.operand, ctx)
        if t != "bool":
            raise ValidationError(f"'not' requires a bool operand, got {t}")
        return "bool"
    if isinstance(node, BinOp):
        if node.op in ("and", "or"):
            for side in (node.left, node.right):
                if _node_type(side, ctx) != "bool":
                    raise ValidationError(f"'{node.op}' requires bool operands")
            return "bool"
        # comparison ops
        lt = _node_type(node.left, ctx)
        rt = _node_type(node.right, ctx)
        if lt != "int" or rt != "int":
            raise ValidationError(f"comparison '{node.op}' requires int operands, got {lt} {node.op} {rt}")
        return "bool"
    if isinstance(node, FuncCall):
        spec = KNOWN_FUNCS.get(node.name)
        if spec is None:
            raise ValidationError(f"unknown function {node.name!r}")
        ret_type, arity = spec
        if ret_type == "PHASE2":
            # Parses but won't validate as a typed node — caller can choose to
            # tolerate at validate time and fail at evaluate time. We mark it
            # 'bool' so callers can compose with it; evaluator will reject.
            if len(node.args) != arity:
                raise ValidationError(f"{node.name} expects {arity} arg(s), got {len(node.args)}")
            return "bool" if node.name != "fact_value" else "int"
        if len(node.args) != arity:
            raise ValidationError(f"{node.name} expects {arity} arg(s), got {len(node.args)}")
        if node.name == "fact":
            slug = node.args[0]
            if not isinstance(slug, str):
                raise ValidationError("fact(slug) requires a string slug")
            if slug not in ctx.boolean_fact_slugs:
                raise ValidationError(f"unknown boolean fact slug {slug!r}")
        elif node.name == "fact_eq":
            slug, value = node.args
            if not isinstance(slug, str) or not isinstance(value, str):
                raise ValidationError("fact_eq(slug, value) requires two string args")
            if slug not in ctx.text_fact_slugs:
                raise ValidationError(f"unknown text fact slug {slug!r}")
        elif node.name in ("supply_exists", "supply_count"):
            target = node.args[0]
            if not isinstance(target, str):
                raise ValidationError(f"{node.name}(target) requires a string target")
            if target.startswith("ER:"):
                if target not in ctx.leaf_ids:
                    raise ValidationError(f"unknown leaf id {target!r}")
            else:
                if ctx.role_tags is not None and target not in ctx.role_tags:
                    raise ValidationError(f"unknown role tag {target!r}")
        return ret_type
    raise ValidationError(f"unknown AST node type: {type(node).__name__}")


def validate(ast: AstNode, ctx: ValidationContext) -> None:
    t = _node_type(ast, ctx)
    if t != "bool":
        raise ValidationError(f"top-level expression must be bool, got {t}")


# ── Evaluator ──────────────────────────────────────────────────────────────────

@dataclass
class EvalContext:
    facts:            dict[str, object]            # client_facts row as dict
    supply_exists_fn: Callable[[str], bool]
    supply_count_fn:  Callable[[str], int]


def evaluate(node: AstNode, ctx: EvalContext):
    if isinstance(node, IntLit):
        return node.value
    if isinstance(node, UnaryNot):
        return not evaluate(node.operand, ctx)
    if isinstance(node, BinOp):
        if node.op == "and":
            return bool(evaluate(node.left, ctx)) and bool(evaluate(node.right, ctx))
        if node.op == "or":
            return bool(evaluate(node.left, ctx)) or bool(evaluate(node.right, ctx))
        # comparison
        lv = evaluate(node.left, ctx)
        rv = evaluate(node.right, ctx)
        if node.op == ">=": return lv >= rv
        if node.op == ">":  return lv >  rv
        if node.op == "<=": return lv <= rv
        if node.op == "<":  return lv <  rv
        if node.op == "=":  return lv == rv
        if node.op == "!=": return lv != rv
        raise EvalError(f"unknown comparison op {node.op!r}")
    if isinstance(node, FuncCall):
        if node.name in PHASE2_FUNCS:
            raise EvalError(f"{node.name!r} is reserved for Phase 2 — not yet implemented")
        if node.name == "fact":
            return bool(ctx.facts.get(node.args[0], False))
        if node.name == "fact_eq":
            return ctx.facts.get(node.args[0]) == node.args[1]
        if node.name == "supply_exists":
            return bool(ctx.supply_exists_fn(node.args[0]))
        if node.name == "supply_count":
            return int(ctx.supply_count_fn(node.args[0]))
        raise EvalError(f"unknown function {node.name!r}")
    raise EvalError(f"unknown AST node type {type(node).__name__}")


# ── Renderer ───────────────────────────────────────────────────────────────────

_FACT_HUMAN = {
    "uses_cloud_services":      "uses cloud services",
    "processes_personal_data":  "processes personal data",
    "eu_data_subjects":         "has EU data subjects",
    "uk_data_subjects":         "has UK data subjects",
    "role_controller":          "acts as data controller",
    "role_processor":           "acts as data processor",
    "high_risk_processing":     "has high-risk processing",
    "public_authority":         "is a public authority",
    "employee_count_250_plus":  "has 250+ employees",
    "uses_processors":          "uses processors",
    "has_remote_workers":       "has remote workers",
    "develops_software":        "develops software",
    "transfers_data_outside_eu":"transfers data outside the EU",
}

def _humanize_slug(slug: str) -> str:
    return _FACT_HUMAN.get(slug, slug.replace("_", " "))

def render(node: AstNode) -> str:
    """Human-readable English approximation; used in gap-list copy & Review UI."""
    if isinstance(node, IntLit):
        return str(node.value)
    if isinstance(node, UnaryNot):
        return f"NOT ({render(node.operand)})"
    if isinstance(node, BinOp):
        if node.op in ("and", "or"):
            return f"({render(node.left)}) {node.op.upper()} ({render(node.right)})"
        return f"{render(node.left)} {node.op} {render(node.right)}"
    if isinstance(node, FuncCall):
        if node.name == "fact":
            return f"tenant {_humanize_slug(node.args[0])}"
        if node.name == "fact_eq":
            return f"{_humanize_slug(node.args[0])} = {node.args[1]!r}"
        if node.name == "supply_exists":
            tgt = node.args[0]
            label = tgt[3:] if tgt.startswith("ER:") else f"role {tgt!r}"
            return f"there is evidence for {label}"
        if node.name == "supply_count":
            tgt = node.args[0]
            label = tgt[3:] if tgt.startswith("ER:") else f"role {tgt!r}"
            return f"count of evidence for {label}"
        return f"{node.name}({', '.join(repr(a) for a in node.args)})"
    return "?"


# ── Convenience ────────────────────────────────────────────────────────────────

def parse_validate_evaluate(
    source: str,
    validation_ctx: ValidationContext,
    eval_ctx: EvalContext,
) -> bool:
    ast = parse(source)
    validate(ast, validation_ctx)
    result = evaluate(ast, eval_ctx)
    return bool(result)
