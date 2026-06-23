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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_load = sub.add_parser("load")
    p_load.add_argument("project_root")

    p_ensure = sub.add_parser("ensure")
    p_ensure.add_argument("project_root")

    p_select = sub.add_parser("select-ready")
    p_select.add_argument("project_root")
    p_select.add_argument("--limit", type=int, default=5)
    p_select.add_argument("--mode")

    p_upsert = sub.add_parser("upsert")
    p_upsert.add_argument("project_root")
    p_upsert.add_argument("--task-id", required=True)
    p_upsert.add_argument("--mode", required=True)
    p_upsert.add_argument("--objective", required=True)
    p_upsert.add_argument("--status", default="ready")
    p_upsert.add_argument("--priority", type=int, default=0)
    p_upsert.add_argument("--dependency", action="append", default=[])
    p_upsert.add_argument("--input", action="append", default=[])
    p_upsert.add_argument("--expected-output", action="append", default=[])
    p_upsert.add_argument("--assigned-agent-run")
    p_upsert.add_argument("--note", action="append", default=[])

    p_update = sub.add_parser("update")
    p_update.add_argument("project_root")
    p_update.add_argument("--task-id", required=True)
    p_update.add_argument("--status")
    p_update.add_argument("--priority", type=int)
    p_update.add_argument("--assigned-agent-run")
    p_update.add_argument("--append-note", action="append", default=[])

    args = parser.parse_args(argv)
    if args.cmd == "load":
        payload = load(args.project_root)
    elif args.cmd == "ensure":
        payload = ensure(args.project_root)
    elif args.cmd == "select-ready":
        payload = select_ready(args.project_root, limit=args.limit, mode=args.mode)
    elif args.cmd == "upsert":
        payload = upsert(
            args.project_root,
            task_id=args.task_id,
            mode=args.mode,
            objective=args.objective,
            status=args.status,
            priority=args.priority,
            dependencies=args.dependency,
            inputs=args.input,
            expected_outputs=args.expected_output,
            assigned_agent_run=args.assigned_agent_run,
            notes=args.note,
        )
    else:
        updates: dict[str, Any] = {}
        if args.status is not None:
            updates["status"] = args.status
        if args.priority is not None:
            updates["priority"] = args.priority
        if args.assigned_agent_run is not None:
            updates["assigned_agent_run"] = args.assigned_agent_run
        if args.append_note:
            updates["append_notes"] = args.append_note
        payload = update(args.project_root, args.task_id, **updates)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
