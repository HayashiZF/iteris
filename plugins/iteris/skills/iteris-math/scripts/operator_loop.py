from __future__ import annotations

import argparse
import json

from _common import status_order
from frontier_state import health as frontier_health
from messages_state import list_messages
from task_pool import ensure as ensure_task_pool
from workspace_state import snapshot


def next_action(project_root: str) -> dict:
    snap = snapshot(project_root)
    unread = list_messages(project_root, unread_only=True)
    if unread:
        return {"action": "resolve_messages", "reason": "unread operator messages present", "messages": unread[:5]}
    review = sorted(snap.get("review_tasks", []), key=lambda t: str(t.get("updated_at") or ""))
    if review:
        return {"action": "harvest_review", "reason": "review debt should be drained first", "task": review[0]}
    running = sorted(snap.get("running_tasks", []), key=lambda t: str(t.get("updated_at") or ""))
    if running:
        return {"action": "inspect_running", "reason": "running task already exists", "task": running[0]}
    health = frontier_health(project_root)
    if health.get("explore_recommended"):
        return {"action": "explore_frontier", "reason": health.get("reason"), "focus": health.get("recommended_focus")}
    ready = sorted(snap.get("ready_tasks", []), key=lambda t: (status_order(str(t.get("status") or "")), -int(t.get("priority") or 0), str(t.get("task_id") or "")))
    if ready:
        return {"action": "execute_task", "reason": "highest-priority ready task", "task": ready[0]}
    return {"action": "report_state", "reason": "no runnable work found; summarize state and gaps"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("next")
    p.add_argument("project_root")
    p2 = sub.add_parser("ensure")
    p2.add_argument("project_root")
    args = parser.parse_args(argv)
    if args.cmd == "ensure":
        payload = ensure_task_pool(args.project_root)
    else:
        payload = next_action(args.project_root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
