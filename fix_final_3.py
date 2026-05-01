"""
Fix 3 remaining issues. Run from $INGESTION:
    python3 fix_final_3.py
"""
import re, ast

print("=" * 60)
print("FIX 1: scope N/A — move BEFORE Resolver in arion_graph.py")
print("=" * 60)
with open('rag/arion_graph.py') as f:
    content = f.read()

scope_idx    = content.find('        if _is_scope_na_query(state["query"]):\n')
resolver_idx = content.find('        # ── Resolver: dispatch')

print(f"  scope at line {content[:scope_idx].count(chr(10))+1}, resolver at line {content[:resolver_idx].count(chr(10))+1}")

if scope_idx > resolver_idx:
    # Find block boundaries
    blk_start = scope_idx
    blk_end   = content.find('\n\n        ', scope_idx) + 2
    blk       = content[blk_start:blk_end]
    # Remove block
    content   = content[:blk_start] + content[blk_end:]
    # Insert before Resolver
    ins       = content.find('        # ── Resolver: dispatch')
    content   = content[:ins] + blk + '\n' + content[ins:]
    with open('rag/arion_graph.py', 'w') as f:
        f.write(content)
    ast.parse(open('rag/arion_graph.py').read())
    s2 = content.find('        if _is_scope_na_query')
    r2 = content.find('        # ── Resolver: dispatch')
    print(f"  After: scope line {content[:s2].count(chr(10))+1}, resolver line {content[:r2].count(chr(10))+1}")
    print(f"  ✓ Order {'CORRECT' if s2 < r2 else 'STILL WRONG'}")
else:
    print("  Already correct")


print("\n" + "=" * 60)
print("FIX 2: _resolve_document_content — add vector fallback")
print("=" * 60)
with open('rag/resolver.py') as f:
    content = f.read()

# Show current handler
idx = content.find('def _resolve_document_content')
end = content.find('\n    def _resolve_', idx + 50)
print(content[idx:end][:600])


print("\n" + "=" * 60)
print("FIX 3: _resolve_cross_framework — add posture NC/OFI node_ids")
print("=" * 60)
with open('rag/resolver.py') as f:
    content = f.read()

idx = content.find('def _resolve_cross_framework')
end = content.find('\n    def _resolve_', idx + 50)
handler = content[idx:end]
# Find the node_ids line
node_ids_line = re.search(r'node_ids\s*=.*', handler)
if node_ids_line:
    print(f"  node_ids: {node_ids_line.group()}")
else:
    print("  No node_ids line found — showing first 600 chars:")
    print(handler[:600])
