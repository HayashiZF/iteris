from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from _common import now_iso, read_json, read_jsonl, rel_or_abs, resolve_root, slugify, write_json


def create_workspace(
    project_root: str | Path,
    *,
    run_id: str,
    role: str | None,
    mode: str | None,
    task_id: str | None,
    focus: str | None,
    agent_run_dir: str | Path,
) -> dict[str, Any]:
    root = resolve_root(project_root)
    normalized_role = slugify(role or "agent", 24)
    task_label = slugify(task_id or focus or mode or normalized_role, 44)
    workspace = root / "artifacts" / normalized_role / task_label / run_id
    workspace.mkdir(parents=True, exist_ok=True)
    manifest_path = workspace / "artifact_manifest.json"
    payload = {
        "schema_version": "iteris.artifact_manifest.v0",
        "run_id": run_id,
        "role": role,
        "mode": mode,
        "task_id": task_id,
        "focus": focus,
        "agent_run_dir": rel_or_abs(Path(agent_run_dir), root),
        "artifact_workspace": rel_or_abs(workspace, root),
        "artifact_manifest": rel_or_abs(manifest_path, root),
        "artifact_index": "artifacts/ARTIFACT_INDEX.jsonl",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "created_artifacts": [],
    }
    write_json(manifest_path, payload)
    return payload


def gate(project_root: str | Path) -> dict[str, Any]:
    root = resolve_root(project_root)
    index = read_jsonl(root / "artifacts" / "ARTIFACT_INDEX.jsonl")
    manifests = list((root / "artifacts").glob("*/*/*/artifact_manifest.json"))
    warnings: list[str] = []
    for manifest in manifests:
        payload = read_json(manifest, default={}) or {}
        for rel in payload.get("created_artifacts") or []:
            path = root / str(rel)
            if not path.exists():
                warnings.append(f"manifest references missing artifact: {rel}")
    return {
        "ok": not warnings,
        "artifact_index_records": len(index),
        "manifest_count": len(manifests),
        "warnings": warnings,
    }


def sync_manifest(
    project_root: str | Path,
    request: dict[str, Any],
    output: dict[str, Any] | None,
    *,
    status: str,
) -> dict[str, Any]:
    root = resolve_root(project_root)
    manifest_rel = str(request.get("artifact_manifest") or "")
    if not manifest_rel:
        return {"ok": False, "error": "artifact_manifest missing from request"}
    path = root / manifest_rel
    payload = read_json(path, default={}) or {}
    created_artifacts = list(payload.get("created_artifacts") or [])
    if isinstance(output, dict):
        for item in output.get("created_artifacts") or []:
            value = str(item)
            if value and value not in created_artifacts:
                created_artifacts.append(value)
    payload["created_artifacts"] = created_artifacts
    payload["status"] = status
    payload["updated_at"] = now_iso()
    write_json(path, payload)
    index_path = root / "artifacts" / "ARTIFACT_INDEX.jsonl"
    rows = read_jsonl(index_path)
    rows.append(
        {
            "run_id": request.get("run_id"),
            "role": request.get("role"),
            "mode": request.get("mode"),
            "task_id": request.get("task_id"),
            "artifact_workspace": payload.get("artifact_workspace"),
            "artifact_manifest": manifest_rel,
            "status": status,
            "created_artifacts": created_artifacts,
            "updated_at": payload["updated_at"],
        }
    )
    with index_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create-workspace")
    p_create.add_argument("project_root")
    p_create.add_argument("--run-id", required=True)
    p_create.add_argument("--role")
    p_create.add_argument("--mode")
    p_create.add_argument("--task-id")
    p_create.add_argument("--focus")
    p_create.add_argument("--agent-run-dir", required=True)

    p_gate = sub.add_parser("gate")
    p_gate.add_argument("project_root")

    p_sync = sub.add_parser("sync-manifest")
    p_sync.add_argument("project_root")
    p_sync.add_argument("--request-json", required=True)
    p_sync.add_argument("--output-json")
    p_sync.add_argument("--status", required=True)

    args = parser.parse_args(argv)
    if args.cmd == "create-workspace":
        payload = create_workspace(
            args.project_root,
            run_id=args.run_id,
            role=args.role,
            mode=args.mode,
            task_id=args.task_id,
            focus=args.focus,
            agent_run_dir=args.agent_run_dir,
        )
    elif args.cmd == "gate":
        payload = gate(args.project_root)
    else:
        request = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
        output = json.loads(Path(args.output_json).read_text(encoding="utf-8")) if args.output_json else None
        payload = sync_manifest(args.project_root, request, output, status=args.status)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
