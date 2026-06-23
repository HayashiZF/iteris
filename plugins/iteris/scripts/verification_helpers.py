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

from iteris.verification.agent import normalize_agent_output
from iteris.verification.local import verify_local
from iteris.verification.panel import verify_panel


def structural_verify(
    project_root: str | Path,
    *,
    mode: str,
    claim: str,
    artifacts: list[str],
    fact_ids: list[str] | None = None,
    target_artifact: str | None = None,
) -> dict[str, Any]:
    return verify_local(
        Path(project_root),
        mode=mode,
        claim=claim,
        artifacts=[Path(item) for item in artifacts],
        fact_ids=fact_ids,
        target_artifact=Path(target_artifact) if target_artifact else None,
    )


def panel_verify(
    project_root: str | Path,
    *,
    mode: str,
    claim: str,
    artifacts: list[str],
    fact_ids: list[str] | None = None,
    target_artifact: str | None = None,
    runs: int = 2,
    executor: str | None = None,
    seat_runner=None,
) -> dict[str, Any]:
    return verify_panel(
        Path(project_root),
        mode=mode,
        claim=claim,
        artifacts=[Path(item) for item in artifacts],
        fact_ids=fact_ids,
        target_artifact=Path(target_artifact) if target_artifact else None,
        runs=runs,
        executor=executor,
        seat_runner=seat_runner,
    )


def normalize_agent_result(
    *,
    request: dict[str, Any],
    payload: dict[str, Any],
    run_dir: str | Path,
    log_path: str | Path,
) -> dict[str, Any]:
    return normalize_agent_output(
        request=request,
        payload=payload,
        run_dir=Path(run_dir),
        log_path=Path(log_path),
    )
