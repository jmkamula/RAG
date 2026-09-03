"""
Ship 111'.b — env-var naming guard.

Regression guard against a class of latent bugs where runtime code
reads a Postgres password from an env variable that doesn't appear in
`.env` — leading to silent auth failure on customer boxes.

Two live issues surfaced during Ship 110' PoC deployment (2026-09-03):

  1. `install.sh` used install-time names (`OPENAI_KEY`, `NEO4J_PW`)
     that didn't match runtime `.env` names (`OPENAI_API_KEY`,
     `NEO4J_PASSWORD`) — the update-mode loader couldn't source them.
  2. Five runtime call sites (in `rag/arion_graph.py` +
     `rag/incident_materializer.py`) read `POSTGRES_PASSWORD` which
     was never in `.env` — silent auth failure on any box where the
     dev hadn't manually exported the variable.

Canonical scheme (Ship 111'.a):

    App-role Postgres pw       = PGPASSWORD           (widely-known name;
                                                       set by install.sh
                                                       step 6 writer)
    Owner-role Postgres pw     = ARION_OWNER_PW       (Ship 104'.a
                                                       introduced;
                                                       Ship 111'.a stashes
                                                       in .env)
    Neo4j pw                   = NEO4J_PASSWORD       (Ship 111'.a
                                                       renamed install.sh
                                                       internal to match)
    OpenAI key                 = OPENAI_API_KEY       (same)

Runtime code MUST NOT read `POSTGRES_PASSWORD` — it doesn't exist in
the canonical .env template. Dev/curation scripts (`scripts/ship*.py`)
grandfathered — they run only on the dev box where the dev may have
POSTGRES_PASSWORD in their shell env.

This test does a static grep. It runs cheap (<100ms) and doesn't need
a DB connection.
"""
from __future__ import annotations
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Runtime code paths — auth failures here impact customers.
RUNTIME_PATHS = [
    REPO_ROOT / "rag",
    REPO_ROOT / "api_server.py",
]

# Grandfathered — dev-only scripts + one-off curation. If any of these
# graduate to being invoked on customer boxes, remove from this list
# and migrate to the canonical scheme.
GRANDFATHERED_STEMS = {
    "ship78c_dogfood", "ship80c_dogfood", "ship80d_dogfood",
    "ship81a_signal_analysis", "ship81a_fingerprint_uniqueness",
    "ship81c_dogfood", "ship81d_dogfood", "ship82a_gt_authoring",
    "ship83c_dogfood", "ship86a_workbook_curator",
    "ship90a_cite_columns_sweep", "ship91f_hyperlink_audit",
    "sweep_legacy_xfw_bridges", "backfill_neo4j_subject_role",
    "audit_gdpr_curation_wide_73a",
}


def _iter_python_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def test_runtime_code_does_not_read_postgres_password():
    """Runtime code (rag/ + api_server.py) must not read POSTGRES_PASSWORD.

    Only PGPASSWORD (app-role) or ARION_OWNER_PW (owner-role) should
    appear. POSTGRES_PASSWORD in a comment or a docstring is fine —
    only actual reads (`os.getenv("POSTGRES_PASSWORD")` etc.) fail.
    """
    pattern = re.compile(
        r'''os\.(?:getenv|environ\.get|environ\[)\s*\(?\s*['"]POSTGRES_PASSWORD['"]''',
    )
    offenders: list[tuple[str, int, str]] = []
    for path in RUNTIME_PATHS:
        for py in _iter_python_files(path):
            for i, line in enumerate(py.read_text().splitlines(), start=1):
                if pattern.search(line):
                    offenders.append((str(py.relative_to(REPO_ROOT)), i, line.strip()))

    # incident_materializer.py has a `POSTGRES_PASSWORD` fallback string
    # inside a `X or Y` expression. That's a migration-window fallback,
    # not the primary read. Filter it out.
    offenders = [
        (p, i, l) for (p, i, l) in offenders
        if not (
            "ARION_OWNER_PW" in l  # legit fallback pattern
            or "ARION_APP_PW"  in l
        )
    ]

    assert not offenders, (
        "Runtime code reads POSTGRES_PASSWORD (not in canonical .env "
        "template). Migrate to PGPASSWORD (app role) or ARION_OWNER_PW "
        "(owner role). Offenders:\n"
        + "\n".join(f"  {p}:{i}  {l}" for (p, i, l) in offenders)
    )


def test_install_sh_uses_canonical_env_names():
    """install.sh's prompt_pw + writer must use canonical runtime names
    for the four secrets it manages. Guards against a rename regression
    where install.sh drifts back to install-time aliases.
    """
    install_sh = (REPO_ROOT / "deploy" / "install.sh").read_text()

    # Must-be-present canonical names in prompt_pw + writer path.
    for canonical in ("ARION_OWNER_PW", "ARION_APP_PW",
                       "NEO4J_PASSWORD", "OPENAI_API_KEY"):
        assert f"prompt_pw {canonical}" in install_sh, (
            f"install.sh must have a `prompt_pw {canonical}` call — "
            f"canonical env-var scheme (Ship 111'.a). Grep result: "
            f"{[l for l in install_sh.splitlines() if 'prompt_pw' in l]}"
        )

    # Retired legacy names (Ship 111'.a) must not resurface.
    for legacy in ("NEO4J_PW", "OPENAI_KEY"):
        # Word-boundary — allow NEO4J_PASSWORD, OPENAI_API_KEY.
        pattern = re.compile(rf"\b{legacy}\b")
        offenders = [
            (i, l) for i, l in enumerate(install_sh.splitlines(), start=1)
            if pattern.search(l)
        ]
        assert not offenders, (
            f"install.sh contains retired legacy name `{legacy}` "
            f"(Ship 111'.a canonicalization). Offenders:\n"
            + "\n".join(f"  L{i}  {l}" for (i, l) in offenders)
        )


def test_env_example_has_arion_owner_pw():
    """The .env template must document ARION_OWNER_PW so fresh
    installs get it in .env — future updates then find it without
    prompting.
    """
    env_example = (REPO_ROOT / "deploy" / ".env.example").read_text()
    assert re.search(r"^ARION_OWNER_PW=", env_example, re.M), (
        "deploy/.env.example must have an `ARION_OWNER_PW=` line "
        "(Ship 111'.a) so fresh installs stash the owner pw."
    )


if __name__ == "__main__":
    test_runtime_code_does_not_read_postgres_password()
    test_install_sh_uses_canonical_env_names()
    test_env_example_has_arion_owner_pw()
    print("OK — all env-var convention guards pass")
