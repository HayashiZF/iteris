from __future__ import annotations

from pathlib import Path
from typing import Any

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

from iteris.artifacts import artifact_gate, create_artifact_workspace, update_manifest_from_agent_output


def create_workspace(
    project_root: str | Path,
    *,
    run_id: str,
    role: str | None,
    mode: str | None,
    task_id: str | None,
    focus: str | None,
    agent_run_dir: str | Path,
) -> dict[str, Any]:
    return create_artifact_workspace(
        Path(project_root),
        run_id=run_id,
        role=role,
        mode=mode,
        task_id=task_id,
        focus=focus,
        agent_run_dir=Path(agent_run_dir),
    )


def gate(project_root: str | Path) -> dict[str, Any]:
    return artifact_gate(Path(project_root))


def sync_manifest(
    project_root: str | Path,
    request: dict[str, Any],
    output: dict[str, Any] | None,
    *,
    status: str,
) -> None:
    update_manifest_from_agent_output(Path(project_root), request, output, status=status)
