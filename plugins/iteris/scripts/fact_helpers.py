from __future__ import annotations

from pathlib import Path

try:
    from ._runtime import ensure_repo_imports
except ImportError:  # pragma: no cover - direct script loading in tests
    import importlib.util

    _RUNTIME_PATH = Path(__file__).with_name("_runtime.py")
    _SPEC = importlib.util.spec_from_file_location("iteris_v2_runtime", _RUNTIME_PATH)
    _MODULE = importlib.util.module_from_spec(_SPEC)
    assert _SPEC is not None and _SPEC.loader is not None
    _SPEC.loader.exec_module(_MODULE)
    ensure_repo_imports = _MODULE.ensure_repo_imports

ensure_repo_imports()

from iteris.memory.facts import rebuild_fact_index, update_fact_metadata, validate_project_facts, write_fact


def add_fact(
    project_root: str | Path,
    *,
    fact_id: str,
    source_task: str,
    claim_summary: str,
    statement: str,
    status: str = "submitted",
    fact_type: str = "claim",
    predecessors: list[str] | None = None,
    notes: str = "",
    verification: str | None = None,
    claim_policy: str = "stable_claim",
    review_level: str = "none",
) -> str:
    path = write_fact(
        Path(project_root),
        fact_id=fact_id,
        source_task=source_task,
        claim_summary=claim_summary,
        statement=statement,
        status=status,
        fact_type=fact_type,
        predecessors=predecessors,
        notes=notes,
        verification=verification,
        claim_policy=claim_policy,
        review_level=review_level,
    )
    return str(path)


def promote_fact(
    project_root: str | Path,
    *,
    fact_id: str,
    verification: str,
    status: str = "verified",
    review_level: str = "verified",
) -> str:
    path = update_fact_metadata(
        Path(project_root),
        fact_id=fact_id,
        status=status,
        verification=verification,
        review_level=review_level,
    )
    rebuild_fact_index(Path(project_root))
    return str(path)


def rebuild_index(project_root: str | Path) -> int:
    return rebuild_fact_index(Path(project_root))


def validate(project_root: str | Path, *, rebuild: bool = False) -> dict:
    return validate_project_facts(Path(project_root), rebuild=rebuild)
