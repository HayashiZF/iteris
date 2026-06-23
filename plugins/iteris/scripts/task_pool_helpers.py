from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import infer_project_id, now_iso, read_json, resolve_root, write_json


def _pool_path(root: Path) -> Path:
    return root / "tasks" / "TASK_POOL.json"


def _default_pool(root: Path) -> dict[str, Any]:
    return {
        "schema_version": "iteris.task_pool.v0",
        "project_id": infer_project_id(root),
        "updated_at": now_iso(),
        "active_frontier": "",
        "tasks": [],
    }


def load(project_root: str | Path) -> dict[str, Any]:
    root = resolve_root(project_root)
    payload = read_json(_pool_path(root), default=None)
    return payload if isinstance(payload, dict) else _default_pool(root)


def ensure(project_root: str | Path) -> dict[str, Any]:
    root = resolve_root(project_root)
    path = _pool_path(root)
    if path.exists():
        return load(root)
    payload = _default_pool(root)
    write_json(path, payload)
    return payload


def _normalize_task(task: dict[str, Any]) -> dict[str, Any]:
    out = dict(task)
    out.setdefault("priority", 0)
    out.setdefault("dependencies", [])
    out.setdefault("inputs", [])
    out.setdefault("expected_outputs", [])
    out.setdefault("notes", [])
    out.setdefault("status", "ready")
    return out


def select_ready(project_root: str | Path, *, limit: int = 5, mode: str | None = None) -> list[dict[str, Any]]:
    tasks = [task for task in load(project_root).get("tasks", []) if isinstance(task, dict)]
    ready = [task for task in tasks if task.get("status") == "ready" and (mode is None or task.get("mode") == mode)]
    ready.sort(key=lambda task: (-int(task.get("priority") or 0), str(task.get("task_id") or "")))
    return ready[:limit]


def upsert(project_root: str | Path, **kwargs: Any) -> dict[str, Any]:
    root = resolve_root(project_root)
    pool = ensure(root)
    task_id = str(kwargs["task_id"])
    tasks = [task for task in pool.get("tasks", []) if isinstance(task, dict)]
    for task in tasks:
        if task.get("task_id") == task_id:
            task.update({k: v for k, v in kwargs.items() if v is not None})
            task["updated_at"] = now_iso()
            pool["updated_at"] = now_iso()
            write_json(_pool_path(root), pool)
            return _normalize_task(task)
    task = _normalize_task(
        {
            "task_id": task_id,
            "mode": kwargs.get("mode"),
            "objective": kwargs.get("objective"),
            "status": kwargs.get("status", "ready"),
            "priority": kwargs.get("priority", 0),
            "dependencies": kwargs.get("dependencies") or [],
            "inputs": kwargs.get("inputs") or [],
            "expected_outputs": kwargs.get("expected_outputs") or [],
            "assigned_agent_run": kwargs.get("assigned_agent_run"),
            "notes": kwargs.get("notes") or [],
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
    )
    tasks.append(task)
    pool["tasks"] = tasks
    pool["updated_at"] = now_iso()
    write_json(_pool_path(root), pool)
    return task


def update(project_root: str | Path, task_id: str, **updates: Any) -> dict[str, Any]:
    root = resolve_root(project_root)
    pool = ensure(root)
    tasks = [task for task in pool.get("tasks", []) if isinstance(task, dict)]
    for task in tasks:
        if task.get("task_id") != task_id:
            continue
        append_notes = updates.pop("append_notes", None) or []
        task.update({k: v for k, v in updates.items() if v is not None})
        if append_notes:
            notes = list(task.get("notes") or [])
            notes.extend(str(item) for item in append_notes)
            task["notes"] = notes
        task["updated_at"] = now_iso()
        pool["updated_at"] = now_iso()
        write_json(_pool_path(root), pool)
        return _normalize_task(task)
    raise KeyError(task_id)


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
