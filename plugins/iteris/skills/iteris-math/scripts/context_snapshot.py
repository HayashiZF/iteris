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

from iteris.commands.context import build_context


def snapshot(project_root: str | Path, *, query: str | None = None, limit: int = 5) -> dict[str, Any]:
    return build_context(Path(project_root), query=query, limit=limit)
