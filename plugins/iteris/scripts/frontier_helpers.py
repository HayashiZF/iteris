from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import now_iso, read_json, resolve_root, write_json
from task_pool_helpers import load as load_task_pool


def _frontier_path(root: Path) -> Path:
    return root / "memory" / "facts" / "FRONTIER_INDEX.json"


def load(project_root: str | Path) -> dict[str, Any]:
    root = resolve_root(project_root)
    payload = read_json(_frontier_path(root), default={})
    return payload if isinstance(payload, dict) else {}


def refresh(project_root: str | Path) -> dict[str, Any]:
    root = resolve_root(project_root)
    frontier = load(root)
    frontier.setdefault("schema_version", "iteris.frontier_index.v0")
    frontier.setdefault("active_frontiers", [])
    frontier["updated_at"] = now_iso()
    write_json(_frontier_path(root), frontier)
    return frontier


def health(project_root: str | Path) -> dict[str, Any]:
    root = resolve_root(project_root)
    frontier = load(root)
    pool = load_task_pool(root)
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
    for name in ("load", "refresh", "health"):
        p = sub.add_parser(name)
        p.add_argument("project_root")
    args = parser.parse_args(argv)
    if args.cmd == "load":
        payload = load(args.project_root)
    elif args.cmd == "refresh":
        payload = refresh(args.project_root)
    else:
        payload = health(args.project_root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
