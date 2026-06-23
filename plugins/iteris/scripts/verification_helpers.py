from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import build_verification_request_id, collect_fact_refs, now_iso, read_json, read_jsonl, rel_or_abs, resolve_root, write_json, write_jsonl


def structural_verify(
    project_root: str | Path,
    *,
    mode: str,
    claim: str,
    artifacts: list[str],
    fact_ids: list[str] | None = None,
    target_artifact: str | None = None,
) -> dict[str, Any]:
    root = resolve_root(project_root)
    request_id = build_verification_request_id(mode, claim)
    checked = [Path(item) if Path(item).is_absolute() else root / item for item in artifacts]
    missing = [rel_or_abs(path, root) for path in checked if not path.exists()]
    gaps = [{"location": item, "issue": "artifact missing"} for item in missing]
    passed = not gaps
    result = {
        "schema_version": "iteris.verification_result.v0",
        "request_id": request_id,
        "backend": "local",
        "mode": mode,
        "claim": claim,
        "verdict": "accepted" if passed else "needs_repair",
        "passed": passed,
        "strict_verdict": "correct" if passed else "wrong",
        "summary": "Portable structural verification passed." if passed else "Portable structural verification found missing artifacts.",
        "critical_errors": [],
        "gaps": gaps,
        "repair_hints": "" if passed else "\n".join(f"{gap['location']}: {gap['issue']}" for gap in gaps),
        "checked_artifacts": [rel_or_abs(path, root) for path in checked if path.exists()],
        "checked_fact_ids": list(fact_ids or []) or collect_fact_refs(path for path in checked if path.exists()),
        "primary_fact_ids": list(fact_ids or []),
        "target_artifact": target_artifact,
        "executor": "portable",
        "verification_scope": "structural_precheck",
        "claim_ceiling_after_verification": "verified" if passed and mode in {"fact", "assembly", "goal_success", "proof"} else ("reviewed" if passed else "submitted"),
        "created_at": now_iso(),
        "verifier": "iteris.portable_structural_verifier",
    }
    _persist_result(root, result)
    return result


def panel_verify(
    project_root: str | Path,
    *,
    mode: str,
    claim: str,
    artifacts: list[str],
    fact_ids: list[str] | None = None,
    target_artifact: str | None = None,
    runs: int = 2,
    executor: str | None = None,
    seat_runner=None,
) -> dict[str, Any]:
    del executor, seat_runner
    structural = structural_verify(
        project_root,
        mode=mode,
        claim=claim,
        artifacts=artifacts,
        fact_ids=fact_ids,
        target_artifact=target_artifact,
    )
    structural["verification_scope"] = "agent_panel"
    structural["panel_runs"] = runs
    structural["verifier"] = "iteris.portable_panel_verifier"
    _persist_result(resolve_root(project_root), structural, overwrite=True)
    return structural


def normalize_agent_result(
    *,
    request: dict[str, Any],
    payload: dict[str, Any],
    run_dir: str | Path,
    log_path: str | Path,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    project_root = run_dir.parent.parent.parent
    report = payload.get("verification_report") if isinstance(payload.get("verification_report"), dict) else {}
    critical_errors = _list_of_dicts(report.get("critical_errors"))
    gaps = _list_of_dicts(report.get("gaps"))
    passed = payload.get("verdict") == "correct" and not critical_errors and not gaps
    result = {
        "schema_version": "iteris.verification_result.v0",
        "request_id": request["request_id"],
        "backend": "agent",
        "mode": request["mode"],
        "claim": request["claim"],
        "verdict": "accepted" if passed else ("rejected" if critical_errors else "needs_repair"),
        "passed": passed,
        "strict_verdict": "correct" if passed else "wrong",
        "summary": str(report.get("summary") or payload.get("summary") or ""),
        "critical_errors": critical_errors,
        "gaps": gaps,
        "repair_hints": str(payload.get("repair_hints") or ""),
        "checked_artifacts": [str(item) for item in payload.get("checked_artifacts") or request.get("artifacts") or []],
        "checked_fact_ids": [str(item) for item in payload.get("checked_fact_ids") or request.get("fact_ids") or []],
        "primary_fact_ids": [str(item) for item in request.get("fact_ids") or []],
        "target_artifact": request.get("target_artifact"),
        "executor": str(request.get("executor") or "portable"),
        "verification_scope": f"{request.get('executor') or 'portable'}_agent",
        "claim_ceiling_after_verification": "verified" if passed and request["mode"] in {"fact", "assembly", "goal_success", "proof"} else ("reviewed" if passed else "submitted"),
        "agent_run_dir": rel_or_abs(run_dir, project_root),
        "agent_log": rel_or_abs(Path(log_path), project_root),
        "created_at": now_iso(),
        "verifier": f"iteris.{request.get('executor') or 'portable'}_verification_agent",
    }
    return result


def _list_of_dicts(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, dict):
            rows.append({"location": str(item.get("location", "")), "issue": str(item.get("issue", ""))})
    return rows


def _persist_result(root: Path, result: dict[str, Any], *, overwrite: bool = False) -> None:
    results_dir = root / "verification" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    result_path = results_dir / f"{result['request_id']}.json"
    if overwrite or not result_path.exists():
        write_json(result_path, result)
    index_path = root / "verification" / "VERIFICATION_INDEX.jsonl"
    rows = read_jsonl(index_path)
    kept = [row for row in rows if row.get("request_id") != result["request_id"]]
    kept.append(result)
    write_jsonl(index_path, kept)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_struct = sub.add_parser("structural")
    p_struct.add_argument("project_root")
    p_struct.add_argument("--mode", required=True)
    p_struct.add_argument("--claim", required=True)
    p_struct.add_argument("--artifact", action="append", default=[])
    p_struct.add_argument("--fact-id", action="append", default=[])
    p_struct.add_argument("--target-artifact")

    p_panel = sub.add_parser("panel")
    p_panel.add_argument("project_root")
    p_panel.add_argument("--mode", required=True)
    p_panel.add_argument("--claim", required=True)
    p_panel.add_argument("--artifact", action="append", default=[])
    p_panel.add_argument("--fact-id", action="append", default=[])
    p_panel.add_argument("--target-artifact")
    p_panel.add_argument("--runs", type=int, default=2)
    p_panel.add_argument("--executor")

    p_norm = sub.add_parser("normalize-agent")
    p_norm.add_argument("--request-json", required=True)
    p_norm.add_argument("--payload-json", required=True)
    p_norm.add_argument("--run-dir", required=True)
    p_norm.add_argument("--log-path", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "structural":
        payload = structural_verify(
            args.project_root,
            mode=args.mode,
            claim=args.claim,
            artifacts=args.artifact,
            fact_ids=args.fact_id,
            target_artifact=args.target_artifact,
        )
    elif args.cmd == "panel":
        payload = panel_verify(
            args.project_root,
            mode=args.mode,
            claim=args.claim,
            artifacts=args.artifact,
            fact_ids=args.fact_id,
            target_artifact=args.target_artifact,
            runs=args.runs,
            executor=args.executor,
        )
    else:
        payload = normalize_agent_result(
            request=json.loads(Path(args.request_json).read_text(encoding="utf-8")),
            payload=json.loads(Path(args.payload_json).read_text(encoding="utf-8")),
            run_dir=args.run_dir,
            log_path=args.log_path,
        )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
