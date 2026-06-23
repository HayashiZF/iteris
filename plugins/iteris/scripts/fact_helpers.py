from __future__ import annotations

import argparse
import json
from pathlib import Path

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

from iteris.memory.facts import rebuild_fact_index, update_fact_metadata, validate_project_facts, write_fact


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
    path = write_fact(
        Path(project_root),
        fact_id=fact_id,
        source_task=source_task,
        claim_summary=claim_summary,
        statement=statement,
        status=status,
        fact_type=fact_type,
        predecessors=predecessors,
        notes=notes,
        verification=verification,
        claim_policy=claim_policy,
        review_level=review_level,
    )
    return str(path)


def promote_fact(
    project_root: str | Path,
    *,
    fact_id: str,
    verification: str,
    status: str = "verified",
    review_level: str = "verified",
) -> str:
    path = update_fact_metadata(
        Path(project_root),
        fact_id=fact_id,
        status=status,
        verification=verification,
        review_level=review_level,
    )
    rebuild_fact_index(Path(project_root))
    return str(path)


def rebuild_index(project_root: str | Path) -> int:
    return rebuild_fact_index(Path(project_root))


def validate(project_root: str | Path, *, rebuild: bool = False) -> dict:
    return validate_project_facts(Path(project_root), rebuild=rebuild)


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
        payload = {"path": add_fact(
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
        )}
    elif args.cmd == "promote":
        payload = {"path": promote_fact(
            args.project_root,
            fact_id=args.fact_id,
            verification=args.verification,
            status=args.status,
            review_level=args.review_level,
        )}
    elif args.cmd == "rebuild-index":
        payload = {"count": rebuild_index(args.project_root)}
    else:
        payload = validate(args.project_root, rebuild=args.rebuild)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
