from __future__ import annotations

import argparse
import json

from _common import read_json, read_jsonl, read_text, resolve_root


def snapshot(project_root: str) -> dict:
    root = resolve_root(project_root)
    task_pool = read_json(root / "tasks" / "TASK_POOL.json", default={}) or {}
    frontier = read_json(root / "memory" / "facts" / "FRONTIER_INDEX.json", default={}) or {}
    fact_index = read_jsonl(root / "memory" / "facts" / "FACT_INDEX.jsonl")
    artifacts = read_jsonl(root / "artifacts" / "ARTIFACT_INDEX.jsonl")
    verifications = read_jsonl(root / "verification" / "VERIFICATION_INDEX.jsonl")
    inbox = read_jsonl(root / "messages" / "inbox.jsonl")
    acks = read_jsonl(root / "messages" / "ack.jsonl")
    acked = {str(item.get("msg_id")) for item in acks if item.get("msg_id")}
    unread = [item for item in inbox if str(item.get("msg_id") or "") not in acked]
    tasks = [task for task in task_pool.get("tasks", []) if isinstance(task, dict)]
    return {
        "project_root": str(root),
        "status_text": read_text(root / "STATUS.md"),
        "roadmap_text": read_text(root / "ROADMAP.md"),
        "task_pool": task_pool,
        "task_count": len(tasks),
        "ready_tasks": [task for task in tasks if task.get("status") == "ready"],
        "review_tasks": [task for task in tasks if task.get("status") == "review"],
        "running_tasks": [task for task in tasks if task.get("status") == "running"],
        "frontier_index": frontier,
        "active_frontier_count": len(frontier.get("active_frontiers", []) or []),
        "fact_index_count": len(fact_index),
        "artifact_index_count": len(artifacts),
        "verification_count": len(verifications),
        "recent_verifications": verifications[-5:],
        "unread_messages": unread,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("project_root")
    args = parser.parse_args(argv)
    print(json.dumps(snapshot(args.project_root), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
