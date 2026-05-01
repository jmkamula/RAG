"""
Fix script for resolver.py and arion_graph.py bugs.
Run from $INGESTION directory:
    python3 fix_resolver_bugs.py
"""
import re, ast, sys

print("=" * 60)
print("FIX 1: remove node_ids kwarg from get_document_inventory")
print("=" * 60)

with open('rag/resolver.py') as f:
    content = f.read()

before = content.count('node_ids   = node_ids') + content.count('node_ids   = [],') + content.count('node_ids   = []')
fixed = re.sub(
    r'\s*node_ids\s*=\s*(?:node_ids|\[\]),?\s*\n(\s*)',
    r'\n\1',
    content
)
# Clean up any double blank lines created
fixed = re.sub(r'\n{3,}', '\n\n', fixed)

after = fixed.count('node_ids   = node_ids') + fixed.count('node_ids   = [],')
print(f"  Removed {before - after} node_ids kwargs")

# Verify calls look right
calls = re.findall(r'get_document_inventory\(.*?\)', fixed, re.DOTALL)
for c in calls:
    clean = ' '.join(c.split())
    print(f"  Call: {clean[:100]}")

with open('rag/resolver.py', 'w') as f:
    f.write(fixed)

ast.parse(open('rag/resolver.py').read())
print("  ✓ Syntax clean\n")


print("=" * 60)
print("FIX 2: move scope N/A check BEFORE Resolver in arion_graph.py")
print("=" * 60)

with open('rag/arion_graph.py') as f:
    content = f.read()

# Check if scope N/A is already before Resolver
resolver_idx = content.find('# ── Resolver: dispatch')
scope_idx    = content.find('if _is_scope_na_query(state["query"])')
print(f"  Resolver at char {resolver_idx}, scope N/A at char {scope_idx}")

if scope_idx > resolver_idx:
    # Scope check is AFTER resolver — need to move it BEFORE
    # Extract the scope N/A block
    block_start = content.rfind('\n        # ── Scope N/A', 0, scope_idx)
    block_end   = content.find('\n\n', scope_idx) + 2
    scope_block = content[block_start:block_end]
    
    # Remove it from current position
    content = content[:block_start] + content[block_end:]
    
    # Insert before Resolver
    resolver_idx2 = content.find('        # ── Resolver: dispatch')
    content = content[:resolver_idx2] + scope_block.lstrip('\n') + '\n' + content[resolver_idx2:]
    
    with open('rag/arion_graph.py', 'w') as f:
        f.write(content)
    
    ast.parse(open('rag/arion_graph.py').read())
    
    # Verify order
    with open('rag/arion_graph.py') as f:
        c2 = f.read()
    new_scope   = c2.find('if _is_scope_na_query')
    new_resolver = c2.find('# ── Resolver: dispatch')
    print(f"  After fix: scope at {new_scope}, resolver at {new_resolver}")
    print(f"  Order correct: {new_scope < new_resolver}")
    print("  ✓ Syntax clean\n")
else:
    print("  ✓ Already in correct order — no change needed\n")


print("=" * 60)
print("FIX 3: inspect _resolve_cross_framework node_ids")
print("=" * 60)

with open('rag/resolver.py') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def _resolve_cross_framework' in line:
        print(f"  Handler at line {i+1}:")
        for j in range(i, min(i+35, len(lines))):
            print(f"  {j+1:4d}: {lines[j].rstrip()}")
        break

print("\nDone. Run: python3 tests/eval_suite.py --tag core --trace --pause 3")
