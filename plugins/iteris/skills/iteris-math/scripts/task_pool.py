from __future__ import annotations

import argparse
import json

from _common import now_iso, read_json, resolve_root, write_json


def _default_pool(root):
    return {"schema_version": "iteris.task_pool.v0", "project_id": root.name, "updated_at": now_iso(), "active_frontier": "", "tasks": []}


def load(project_root: str) -> dict:
    root = resolve_root(project_root)
    pool = read_json(root / "tasks" / "TASK_POOL.json", default=None)
    return pool if isinstance(pool, dict) else _default_pool(root)


def ensure(project_root: str) -> dict:
    root = resolve_root(project_root)
    path = root / "tasks" / "TASK_POOL.json"
    if not path.exists():
        pool = _default_pool(root)
        write_json(path, pool)
        return pool
    return load(project_root)


def select_ready(project_root: str, limit: int = 5) -> list[dict]:
    tasks = [task for task in load(project_root).get("tasks", []) if isinstance(task, dict) and task.get("status") == "ready"]
    tasks.sort(key=lambda task: (-int(task.get("priority") or 0), str(task.get("task_id") or "")))
    return tasks[:limit]


def update(project_root: str, task_id: str, **updates) -> dict:
    root = resolve_root(project_root)
    pool = ensure(project_root)
    for task in pool.get("tasks", []):
        if isinstance(task, dict) and task.get("task_id") == task_id:
            task.update({k: v for k, v in updates.items() if v is not None})
            task["updated_at"] = now_iso()
            write_json(root / "tasks" / "TASK_POOL.json", pool)
            return task
    raise KeyError(task_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("load", "ensure"):
        p = sub.add_parser(name)
        p.add_argument("project_root")
    p_select = sub.add_parser("select-ready")
    p_select.add_argument("project_root")
    p_select.add_argument("--limit", type=int, default=5)
    p_update = sub.add_parser("update")
    p_update.add_argument("project_root")
    p_update.add_argument("--task-id", required=True)
    p_update.add_argument("--status")
    p_update.add_argument("--assigned-agent-run")
    args = parser.parse_args(argv)
    if args.cmd == "load":
        payload = load(args.project_root)
    elif args.cmd == "ensure":
        payload = ensure(args.project_root)
    elif args.cmd == "select-ready":
        payload = select_ready(args.project_root, limit=args.limit)
    else:
        payload = update(args.project_root, args.task_id, status=args.status, assigned_agent_run=args.assigned_agent_run)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
