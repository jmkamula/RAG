"""
Enrich ISO nodes with canonical text from ISO 27001 and implementation
guidance from ISO 27002. Updates both obligation_text and business_description.

Usage:
  python3 enrichment/enrich_from_standards.py \
      --nodes iso_nodes_phase1.json \
      --iso27001 /path/to/iso27001_canonical_text.json \
      --iso27002 /path/to/iso27002_guidance.json \
      --output iso_nodes_phase1.json   # overwrites in place
      --dry-run                        # preview only
"""

import json, sys, argparse
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.requirement_node import RequirementNode

# ── Business description template ─────────────────────────────────────────────

def build_business_description(ref: str, node_title: str,
                                ctrl_statement: str,
                                purpose: str,
                                guidance: str,
                                control_type: str,
                                cia: list) -> str:
    """
    Build a structured business_description from 27001 + 27002 sources.
    Combines purpose (WHY) with a condensed guidance summary (HOW).
    """
    parts = []

    # Lead with purpose from 27002 — canonical WHY
    if purpose:
        parts.append(purpose.rstrip('.') + '.')

    # Add condensed guidance — first 400 chars covers the key points
    if guidance:
        # Take first meaningful chunk — stops at first complete sentence
        condensed = guidance[:500]
        last_period = condensed.rfind('.')
        if last_period > 200:
            condensed = condensed[:last_period+1]
        parts.append(condensed)

    # Add attribute context if available
    if control_type and cia:
        cia_str = ', '.join(cia)
        parts.append(
            f"This is a {control_type.lower()} control addressing {cia_str.lower()}."
        )
    elif control_type:
        parts.append(f"This is a {control_type.lower()} control.")

    if parts:
        return ' '.join(parts)

    # Fallback: use control statement only
    return f"{node_title}: {ctrl_statement}" if ctrl_statement else node_title


# ── Main enrichment ────────────────────────────────────────────────────────────

def enrich(nodes_path: Path,
           iso27001_path: Path,
           iso27002_path: Path,
           output_path: Path,
           dry_run: bool = False):

    # Load source data
    with open(nodes_path) as f:
        raw_nodes = json.load(f)
    nodes = [RequirementNode.from_dict(n) for n in raw_nodes]

    with open(iso27001_path) as f:
        canonical = json.load(f)   # ref -> obligation_text string

    with open(iso27002_path) as f:
        guidance = json.load(f)    # ref -> {purpose, guidance, control_type, cia_properties}

    print(f"Loaded {len(nodes)} nodes")
    print(f"27001 canonical texts: {len(canonical)}")
    print(f"27002 guidance entries: {len(guidance)}")
    print()

    stats = {
        'obligation_text_added':    0,
        'obligation_text_existed':  0,
        'bd_added_from_27002':      0,
        'bd_added_fallback':        0,
        'bd_existed':               0,
        'attributes_added':         0,
        'no_data':                  0,
    }

    for n in nodes:
        ref = n.ref
        g   = guidance.get(ref, {})
        c27 = canonical.get(ref, '')

        # ── obligation_text ──────────────────────────────────────────────────
        if n.obligation_text:
            stats['obligation_text_existed'] += 1
        elif c27:
            if not dry_run:
                n.obligation_text = c27
            stats['obligation_text_added'] += 1

        # ── business_description ─────────────────────────────────────────────
        purpose      = g.get('purpose', '')
        guide_text   = g.get('guidance', '')
        control_type = g.get('control_type', '')
        cia          = g.get('cia_properties', [])

        if n.business_description:
            stats['bd_existed'] += 1
            # Still add attributes even if BD already exists
            if control_type and not getattr(n, 'control_type', None):
                if not dry_run:
                    n.control_type   = control_type
                    n.cia_properties = cia
                stats['attributes_added'] += 1
        elif purpose or guide_text:
            # Build from 27002
            bd = build_business_description(
                ref, n.title or ref,
                c27, purpose, guide_text,
                control_type, cia
            )
            if not dry_run:
                n.business_description = bd
                n.control_type         = control_type
                n.cia_properties       = cia
            stats['bd_added_from_27002'] += 1
        elif c27:
            # Fallback: obligation text as business description
            if not dry_run:
                n.business_description = c27[:500]
            stats['bd_added_fallback'] += 1
        else:
            stats['no_data'] += 1

    # Report
    print("─" * 50)
    print("  ENRICHMENT REPORT")
    print("─" * 50)
    for k, v in stats.items():
        if v:
            print(f"  {k:35s}: {v}")
    print()

    # Enrichment coverage
    after_text = sum(1 for n in nodes if n.obligation_text)
    after_bd   = sum(1 for n in nodes if n.business_description)
    print(f"  obligation_text coverage:    {after_text}/{len(nodes)}")
    print(f"  business_description coverage: {after_bd}/{len(nodes)}")
    print("─" * 50)

    if dry_run:
        print("\n[DRY RUN] No files written.")
        return

    # Save — convert back to dicts, preserving new fields
    out_nodes = []
    for n in nodes:
        d = asdict(n) if hasattr(n, '__dataclass_fields__') else vars(n)
        # Ensure new fields are included
        if not hasattr(n, '__dataclass_fields__'):
            d = n.__dict__.copy()
        out_nodes.append(d)

    with open(output_path, 'w') as f:
        json.dump(out_nodes, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Written: {output_path}")
    print(f"  Nodes: {len(out_nodes)}")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodes",   required=True)
    parser.add_argument("--iso27001",required=True)
    parser.add_argument("--iso27002",required=True)
    parser.add_argument("--output",  required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    enrich(
        nodes_path   = Path(args.nodes),
        iso27001_path= Path(args.iso27001),
        iso27002_path= Path(args.iso27002),
        output_path  = Path(args.output),
        dry_run      = args.dry_run,
    )
