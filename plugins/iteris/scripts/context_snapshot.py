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

from iteris.artifacts import artifact_layout_summary
from iteris.frontier import frontier_health, frontier_summary, load_frontier_index
from iteris.memory.facts import validate_project_facts
from iteris.project import read_json, source_file
from iteris.tasks import load_task_pool
from iteris.verification.local import latest_results


def snapshot(project_root: str | Path, *, query: str | None = None, limit: int = 5) -> dict[str, Any]:
    root = Path(project_root).resolve()
    source = source_file(root)
    task_pool = load_task_pool(root)
    frontier = load_frontier_index(root)
    facts = validate_project_facts(root, rebuild=False)
    verifications = latest_results(root)[-limit:]
    return {
        "project_path": str(root),
        "source_file": str(source.relative_to(root)) if source else None,
        "status_text": _read_short(root / "STATUS.md"),
        "roadmap_text": _read_short(root / "ROADMAP.md"),
        "fact_count": facts["count"],
        "fact_type_counts": facts.get("fact_type_counts") or {},
        "facts_ok": facts["ok"],
        "task_pool": task_pool,
        "frontier_index": frontier,
        "frontier_summary": frontier_summary(frontier),
        "frontier_health": frontier_health(root),
        "verification_results": verifications,
        "artifact_layout": artifact_layout_summary(),
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
