from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import read_json, read_jsonl, read_text, rel_or_abs, resolve_root
from fact_helpers import validate as validate_facts
from frontier_helpers import health as frontier_health, load as load_frontier
from task_pool_helpers import load as load_task_pool


def snapshot(project_root: str | Path, *, query: str | None = None, limit: int = 5) -> dict[str, Any]:
    root = resolve_root(project_root)
    task_pool = load_task_pool(root)
    frontier = load_frontier(root)
    facts = validate_facts(root, rebuild=False)
    verifications = read_jsonl(root / "verification" / "VERIFICATION_INDEX.jsonl")[-limit:]
    artifacts = read_jsonl(root / "artifacts" / "ARTIFACT_INDEX.jsonl")[-limit:]
    source_file = _first_existing(root, ["sources/problem.md", "sources/problem.txt", "PROJECT.md"])
    return {
        "project_path": str(root),
        "workflow_authority": "Use tasks/TASK_POOL.json and memory/facts/FRONTIER_INDEX.json as the route state authority.",
        "source_file": rel_or_abs(source_file, root) if source_file else None,
        "status_text": _read_short(root / "STATUS.md"),
        "roadmap_text": _read_short(root / "ROADMAP.md"),
        "fact_count": facts["count"],
        "fact_type_counts": facts.get("fact_type_counts") or {},
        "facts_ok": facts["ok"],
        "task_pool": task_pool,
        "frontier_index": frontier,
        "frontier_summary": _frontier_summary(frontier),
        "frontier_health": frontier_health(root),
        "verification_results": verifications,
        "recent_artifacts": artifacts,
        "config": read_json(root / ".iteris" / "config.json", default={}),
        "search_query": query,
        "search_results": [],
        "recommended_commands": [
            "python plugins/iteris/scripts/context_snapshot.py .",
            "python plugins/iteris/scripts/task_pool_helpers.py load .",
            "python plugins/iteris/scripts/task_pool_helpers.py select-ready . --limit 5",
            "python plugins/iteris/scripts/frontier_helpers.py load .",
            "python plugins/iteris/scripts/frontier_helpers.py refresh .",
            "python plugins/iteris/scripts/frontier_helpers.py health .",
            "python plugins/iteris/scripts/fact_helpers.py add ...",
            "python plugins/iteris/scripts/fact_helpers.py promote ...",
            "python plugins/iteris/scripts/artifact_helpers.py gate .",
            "python plugins/iteris/scripts/verification_helpers.py structural . --mode fact --claim ... --artifact ...",
            "python plugins/iteris/scripts/verification_helpers.py panel . --mode fact --claim ... --artifact ... --runs 2",
            "python plugins/iteris/scripts/generalize_helpers.py validate-analysis generalize/analysis.json",
        ],
    }


def _read_short(path: Path, limit: int = 2000) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]


def _first_existing(root: Path, candidates: list[str]) -> Path | None:
    for candidate in candidates:
        path = root / candidate
        if path.exists():
            return path
    return None


def _frontier_summary(frontier: dict[str, Any]) -> dict[str, Any]:
    active = [item for item in frontier.get("active_frontiers", []) if isinstance(item, dict)]
    return {
        "active_count": len(active),
        "titles": [str(item.get("title") or item.get("summary") or "") for item in active[:5]],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)
    print(json.dumps(snapshot(args.project_root, query=args.query, limit=args.limit), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
