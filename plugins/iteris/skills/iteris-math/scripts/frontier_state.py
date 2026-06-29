from __future__ import annotations

import argparse
import json

from _common import read_json, resolve_root
from task_pool import load as load_task_pool


def load(project_root: str) -> dict:
    root = resolve_root(project_root)
    payload = read_json(root / "memory" / "facts" / "FRONTIER_INDEX.json", default={})
    return payload if isinstance(payload, dict) else {}


def health(project_root: str) -> dict:
    frontier = load(project_root)
    pool = load_task_pool(project_root)
    tasks = [task for task in pool.get("tasks", []) if isinstance(task, dict)]
    active = frontier.get("active_frontiers", []) or []
    blocked = [task for task in tasks if task.get("status") == "blocked"]
    ready = [task for task in tasks if task.get("status") == "ready"]
    review = [task for task in tasks if task.get("status") == "review"]
    explore = bool(not active or (len(blocked) >= 3 and not ready))
    focus = ""
    if active and isinstance(active[0], dict):
        focus = str(active[0].get("title") or active[0].get("summary") or "")
    elif blocked:
        focus = str(blocked[0].get("objective") or blocked[0].get("task_id") or "")
    return {
        "ok": True,
        "explore_recommended": explore,
        "recommended_focus": focus,
        "active_frontier_count": len(active),
        "blocked_task_count": len(blocked),
        "ready_task_count": len(ready),
        "review_task_count": len(review),
        "reason": "explore recommended by portable frontier heuristic" if explore else "no frontier exploration trigger",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("load", "health"):
        p = sub.add_parser(name)
        p.add_argument("project_root")
    args = parser.parse_args(argv)
    payload = load(args.project_root) if args.cmd == "load" else health(args.project_root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
