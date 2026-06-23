from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import FACT_REF_RE, now_iso, read_jsonl, resolve_root, slugify, write_jsonl


def _facts_dir(root: Path) -> Path:
    return root / "memory" / "facts"


def _fact_index_path(root: Path) -> Path:
    return _facts_dir(root) / "FACT_INDEX.jsonl"


def _fact_path(root: Path, fact_id: str) -> Path:
    filename = f"{slugify(fact_id.replace('fact:', ''), 80)}.md"
    return _facts_dir(root) / filename


def _load_fact(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---\n"):
        _, frontmatter, body = text.split("---\n", 2)
        payload: dict[str, Any] = {}
        for line in frontmatter.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            payload[key.strip()] = value.strip()
        return payload, body.lstrip()
    return {}, text


def _write_fact(path: Path, metadata: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = "\n".join(f"{key}: {value}" for key, value in metadata.items())
    path.write_text(f"---\n{frontmatter}\n---\n\n{body.rstrip()}\n", encoding="utf-8")


def add_fact(
    project_root: str | Path,
    *,
    fact_id: str,
    source_task: str,
    claim_summary: str,
    statement: str,
    status: str = "submitted",
    fact_type: str = "claim",
    predecessors: list[str] | None = None,
    notes: str = "",
    verification: str | None = None,
    claim_policy: str = "stable_claim",
    review_level: str = "none",
) -> str:
    root = resolve_root(project_root)
    path = _fact_path(root, fact_id)
    metadata = {
        "fact_id": fact_id,
        "source_task": source_task,
        "claim_summary": claim_summary,
        "status": status,
        "fact_type": fact_type,
        "verification": verification or "",
        "claim_policy": claim_policy,
        "review_level": review_level,
        "updated_at": now_iso(),
    }
    preds = predecessors or []
    body = "\n".join(
        [
            f"Statement: {statement}",
            f"Predecessors: {', '.join(preds) if preds else '(none)'}",
            f"Notes: {notes or '(none)'}",
        ]
    )
    _write_fact(path, metadata, body)
    rebuild_index(root)
    return str(path)


def promote_fact(
    project_root: str | Path,
    *,
    fact_id: str,
    verification: str,
    status: str = "verified",
    review_level: str = "verified",
) -> str:
    root = resolve_root(project_root)
    path = _fact_path(root, fact_id)
    metadata, body = _load_fact(path)
    metadata["verification"] = verification
    metadata["status"] = status
    metadata["review_level"] = review_level
    metadata["updated_at"] = now_iso()
    _write_fact(path, metadata, body)
    rebuild_index(root)
    return str(path)


def rebuild_index(project_root: str | Path) -> int:
    root = resolve_root(project_root)
    facts_dir = _facts_dir(root)
    rows: list[dict[str, Any]] = []
    if facts_dir.exists():
        for path in sorted(facts_dir.glob("*.md")):
            metadata, body = _load_fact(path)
            fact_id = str(metadata.get("fact_id") or f"fact:{path.stem}")
            rows.append(
                {
                    "fact_id": fact_id,
                    "path": str(path.relative_to(root)),
                    "status": str(metadata.get("status") or "submitted"),
                    "fact_type": str(metadata.get("fact_type") or "claim"),
                    "claim_summary": str(metadata.get("claim_summary") or ""),
                    "verification": str(metadata.get("verification") or ""),
                    "review_level": str(metadata.get("review_level") or "none"),
                    "predecessors": sorted(set(FACT_REF_RE.findall(body))),
                    "updated_at": str(metadata.get("updated_at") or ""),
                }
            )
    write_jsonl(_fact_index_path(root), rows)
    return len(rows)


def validate(project_root: str | Path, *, rebuild: bool = False) -> dict[str, Any]:
    root = resolve_root(project_root)
    if rebuild:
        rebuild_index(root)
    rows = read_jsonl(_fact_index_path(root))
    errors: list[str] = []
    type_counts: dict[str, int] = {}
    for row in rows:
        fact_id = str(row.get("fact_id") or "")
        if not fact_id.startswith("fact:"):
            errors.append(f"invalid fact id: {fact_id}")
        fact_type = str(row.get("fact_type") or "claim")
        type_counts[fact_type] = type_counts.get(fact_type, 0) + 1
        path = root / str(row.get("path") or "")
        if not path.exists():
            errors.append(f"missing fact file: {path}")
    return {
        "ok": not errors,
        "count": len(rows),
        "errors": errors,
        "fact_type_counts": type_counts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("project_root")
    p_add.add_argument("--fact-id", required=True)
    p_add.add_argument("--source-task", required=True)
    p_add.add_argument("--claim-summary", required=True)
    p_add.add_argument("--statement", required=True)
    p_add.add_argument("--status", default="submitted")
    p_add.add_argument("--fact-type", default="claim")
    p_add.add_argument("--predecessor", action="append", default=[])
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--verification")
    p_add.add_argument("--claim-policy", default="stable_claim")
    p_add.add_argument("--review-level", default="none")

    p_promote = sub.add_parser("promote")
    p_promote.add_argument("project_root")
    p_promote.add_argument("--fact-id", required=True)
    p_promote.add_argument("--verification", required=True)
    p_promote.add_argument("--status", default="verified")
    p_promote.add_argument("--review-level", default="verified")

    p_rebuild = sub.add_parser("rebuild-index")
    p_rebuild.add_argument("project_root")

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("project_root")
    p_validate.add_argument("--rebuild", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "add":
        payload = {
            "path": add_fact(
                args.project_root,
                fact_id=args.fact_id,
                source_task=args.source_task,
                claim_summary=args.claim_summary,
                statement=args.statement,
                status=args.status,
                fact_type=args.fact_type,
                predecessors=args.predecessor,
                notes=args.notes,
                verification=args.verification,
                claim_policy=args.claim_policy,
                review_level=args.review_level,
            )
        }
    elif args.cmd == "promote":
        payload = {
            "path": promote_fact(
                args.project_root,
                fact_id=args.fact_id,
                verification=args.verification,
                status=args.status,
                review_level=args.review_level,
            )
        }
    elif args.cmd == "rebuild-index":
        payload = {"count": rebuild_index(args.project_root)}
    else:
        payload = validate(args.project_root, rebuild=args.rebuild)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
