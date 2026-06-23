from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import resolve_root


def build_workspace_contract(project_root: str | Path) -> dict[str, str]:
    root = resolve_root(project_root)
    return {
        "project_root": str(root),
        "project_id": root.name,
        "sources_dir": str(root / "sources"),
        "references_dir": str(root / "references"),
        "results_dir": str(root / "results"),
        "tasks_path": str(root / "tasks" / "TASK_POOL.json"),
        "frontier_index_path": str(root / "memory" / "facts" / "FRONTIER_INDEX.json"),
        "facts_dir": str(root / "memory" / "facts"),
        "fact_index_path": str(root / "memory" / "facts" / "FACT_INDEX.jsonl"),
        "artifacts_dir": str(root / "artifacts"),
        "artifact_index_path": str(root / "artifacts" / "ARTIFACT_INDEX.jsonl"),
        "verification_requests_dir": str(root / "verification" / "requests"),
        "verification_results_dir": str(root / "verification" / "results"),
        "messages_inbox_path": str(root / "messages" / "inbox.jsonl"),
        "messages_ack_path": str(root / "messages" / "ack.jsonl"),
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        print("usage: python plugins/iteris/scripts/workspace_contract.py <project_root>", file=sys.stderr)
        return 2
    print(json.dumps(build_workspace_contract(args[0]), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
