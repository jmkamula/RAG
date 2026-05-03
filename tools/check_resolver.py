"""
Quick sanity check after any resolver.py or arion_graph.py update.
Run: python3 tools/check_resolver.py
"""
import ast, re, sys

errors = []

# 1. Syntax check
for path in ['rag/resolver.py', 'rag/arion_graph.py', 'rag/graph_expander.py']:
    try:
        ast.parse(open(path).read())
        print(f"✓ Syntax: {path}")
    except SyntaxError as e:
        print(f"✗ Syntax: {path} — {e}")
        errors.append(path)

# 2. Dataclass field ordering — no default field before non-default
with open('rag/resolver.py') as f:
    lines = f.readlines()

field_errors = []
for cls_name in ['GraphResult', 'ResolveRequest', 'ResolvedContext', 'ResolverTrace']:
    start = next((i for i, l in enumerate(lines) if f'class {cls_name}' in l), None)
    if start is None:
        continue
    has_default = False
    for i in range(start + 1, min(start + 70, len(lines))):
        l = lines[i]
        if l.startswith('    def ') or (l.startswith('class ') and i > start + 1):
            break
        stripped = l.strip()
        if not stripped:
            continue
        if stripped.startswith(('#', '"""', "'''", '@', 'pass')):
            continue
        if ':' in stripped and not stripped.startswith('->'):
            field_has_default = '=' in stripped.split(':')[1] if ':' in stripped else False
            if field_has_default:
                has_default = True
            elif has_default:
                field_errors.append(f"{cls_name} line {i+1}: '{stripped[:60]}'")

if field_errors:
    for e in field_errors:
        print(f"✗ Field order: {e}")
    errors.extend(['field_order'] * len(field_errors))
else:
    print("✓ Field order: all dataclasses OK")

# 3. scope_na regex check
TESTS = [
    ('what are our physical security gaps?', True),
    ('what are our software development security gaps?', True),
    ('what are our access rights gaps?', False),
]
PATTERNS = [
    r'\bphysical\s+security\s+(?:gaps?|findings?|controls?|posture)\b',
    r'\bsoftware\s+(?:development|dev)\s+security\s+(?:gaps?|findings?|controls?)\b',
]
scope_ok = True
for q, expected in TESTS:
    result = any(re.search(p, q, re.IGNORECASE) for p in PATTERNS)
    if result != expected:
        print(f"✗ scope_na: '{q}' expected={expected} got={result}")
        errors.append('scope_na')
        scope_ok = False
if scope_ok:
    print("✓ scope_na: patterns correct")

# Also verify the patterns are actually in arion_graph.py correctly
with open('rag/arion_graph.py') as f:
    ag = f.read()
if 'rphysical' in ag or "r'\\bphysical" not in ag:
    # Check if the import-from-scope_na pattern is used instead
    if 'from rag.scope_na import' not in ag:
        print("✗ scope_na: arion_graph.py has broken regex (missing quotes)")
        errors.append('scope_na_file')
    else:
        print("✓ scope_na: using rag.scope_na module import")
else:
    print("✓ scope_na: arion_graph.py regex intact")

# 4. ClientDocument / DETECTED_IN check
for path in ['rag/graph_expander.py']:
    content = open(path).read()
    bad = [
        l for l in content.splitlines()
        if ('ClientDocument' in l or 'DETECTED_IN' in l)
        and not l.strip().startswith('#')
        and not l.strip().startswith('"""')
        and 'no ClientDocument' not in l
        and 'DETECTED_IN references' not in l
    ]
    if bad:
        print(f"✗ ClientDocument/DETECTED_IN still in {path}:")
        for b in bad[:5]:
            print(f"  {b.strip()}")
        errors.append('client_doc')
    else:
        print(f"✓ No ClientDocument/DETECTED_IN: {path}")

print()
if errors:
    print(f"FAILED — fix before running eval: {errors}")
    sys.exit(1)
else:
    print("All checks passed — safe to run eval.")
