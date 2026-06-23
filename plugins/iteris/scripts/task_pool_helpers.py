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

from iteris.tasks import ensure_task_pool, load_task_pool, select_ready_tasks, update_pool_task, upsert_pool_task


def load(project_root: str | Path) -> dict[str, Any]:
    return load_task_pool(Path(project_root))


def ensure(project_root: str | Path) -> dict[str, Any]:
    return ensure_task_pool(Path(project_root))


def select_ready(project_root: str | Path, *, limit: int = 5, mode: str | None = None) -> list[dict[str, Any]]:
    return select_ready_tasks(Path(project_root), limit=limit, mode=mode)


def upsert(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    return upsert_pool_task(Path(project_root), **kwargs)


def update(project_root: str | Path, task_id: str, **updates: Any) -> dict[str, Any]:
    return update_pool_task(Path(project_root), task_id, **updates)
