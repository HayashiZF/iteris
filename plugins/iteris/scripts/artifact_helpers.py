from __future__ import annotations

import argparse
import json
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create-workspace")
    p_create.add_argument("project_root")
    p_create.add_argument("--run-id", required=True)
    p_create.add_argument("--role")
    p_create.add_argument("--mode")
    p_create.add_argument("--task-id")
    p_create.add_argument("--focus")
    p_create.add_argument("--agent-run-dir", required=True)

    p_gate = sub.add_parser("gate")
    p_gate.add_argument("project_root")

    p_sync = sub.add_parser("sync-manifest")
    p_sync.add_argument("project_root")
    p_sync.add_argument("--request-json", required=True)
    p_sync.add_argument("--output-json")
    p_sync.add_argument("--status", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "create-workspace":
        payload = create_workspace(
            args.project_root,
            run_id=args.run_id,
            role=args.role,
            mode=args.mode,
            task_id=args.task_id,
            focus=args.focus,
            agent_run_dir=args.agent_run_dir,
        )
    elif args.cmd == "gate":
        payload = gate(args.project_root)
    else:
        request = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
        output = json.loads(Path(args.output_json).read_text(encoding="utf-8")) if args.output_json else None
        sync_manifest(args.project_root, request, output, status=args.status)
        payload = {"ok": True}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
