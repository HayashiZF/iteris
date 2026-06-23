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


def build_workspace_contract(project_root: str | Path) -> dict[str, str]:
    root = Path(project_root).resolve()
    return {
        "project_root": str(root),
        "sources_dir": str(root / "sources"),
        "references_dir": str(root / "references"),
        "results_dir": str(root / "results"),
        "tasks_path": str(root / "tasks" / "TASK_POOL.json"),
        "frontier_index_path": str(root / "memory" / "facts" / "FRONTIER_INDEX.json"),
        "facts_dir": str(root / "memory" / "facts"),
        "fact_index_path": str(root / "memory" / "facts" / "FACT_INDEX.jsonl"),
        "artifacts_dir": str(root / "artifacts"),
        "artifact_index_path": str(root / "artifacts" / "ARTIFACT_INDEX.jsonl"),
        "verification_requests_dir": str(root / "verification" / "requests"),
        "verification_results_dir": str(root / "verification" / "results"),
    }
