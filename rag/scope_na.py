"""
Arion Networks — scope N/A query detection.
Controls that are out of scope for Arion (cloud-only, no physical premises,
no software development) get deterministic answers without calling the LLM.
"""
import re

_PHYSICAL = re.compile(
    r'\bphysical\s+security\s+(?:gaps?|findings?|controls?|posture)\b',
    re.IGNORECASE
)
_SOFTDEV = re.compile(
    r'\bsoftware\s+(?:development|dev)\s+security\s+(?:gaps?|findings?|controls?)\b',
    re.IGNORECASE
)

def is_scope_na_query(query: str) -> bool:
    """True if query is about controls N/A for Arion Networks."""
    return bool(_PHYSICAL.search(query)) or bool(_SOFTDEV.search(query))
