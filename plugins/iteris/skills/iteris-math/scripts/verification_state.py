from __future__ import annotations

import argparse
import json

from _common import read_jsonl, resolve_root


def summary(project_root: str, limit: int = 10) -> dict:
    root = resolve_root(project_root)
    results = read_jsonl(root / "verification" / "VERIFICATION_INDEX.jsonl")
    requests = read_jsonl(root / "verification" / "requests.jsonl")
    return {
        "verification_count": len(results),
        "recent_results": results[-limit:],
        "request_count": len(requests),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    print(json.dumps(summary(args.project_root, limit=args.limit), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
