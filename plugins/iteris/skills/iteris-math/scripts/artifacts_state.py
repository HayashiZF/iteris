from __future__ import annotations

import argparse
import json

from _common import now_iso, read_json, read_jsonl, resolve_root, write_json


def create_workspace(project_root: str, *, run_id: str, kind: str, task_label: str) -> dict:
    root = resolve_root(project_root)
    workspace = root / "artifacts" / kind / task_label / run_id
    workspace.mkdir(parents=True, exist_ok=True)
    manifest = workspace / "artifact_manifest.json"
    payload = {
        "schema_version": "iteris.artifact_manifest.v0",
        "run_id": run_id,
        "artifact_workspace": str(workspace.relative_to(root)),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "created_artifacts": [],
    }
    write_json(manifest, payload)
    return payload


def gate(project_root: str) -> dict:
    root = resolve_root(project_root)
    index = read_jsonl(root / "artifacts" / "ARTIFACT_INDEX.jsonl")
    manifests = list((root / "artifacts").glob("*/*/*/artifact_manifest.json"))
    return {
        "ok": True,
        "artifact_index_records": len(index),
        "manifest_count": len(manifests),
        "warnings": [],
    }


def sync_manifest(project_root: str, *, manifest_path: str, created_artifacts: list[str]) -> dict:
    root = resolve_root(project_root)
    path = root / manifest_path
    payload = read_json(path, default={}) or {}
    payload["created_artifacts"] = created_artifacts
    payload["updated_at"] = now_iso()
    write_json(path, payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_create = sub.add_parser("create-workspace")
    p_create.add_argument("project_root")
    p_create.add_argument("--run-id", required=True)
    p_create.add_argument("--kind", required=True)
    p_create.add_argument("--task-label", required=True)
    p_gate = sub.add_parser("gate")
    p_gate.add_argument("project_root")
    p_sync = sub.add_parser("sync-manifest")
    p_sync.add_argument("project_root")
    p_sync.add_argument("--manifest-path", required=True)
    p_sync.add_argument("--created-artifact", action="append", default=[])
    args = parser.parse_args(argv)
    if args.cmd == "create-workspace":
        payload = create_workspace(args.project_root, run_id=args.run_id, kind=args.kind, task_label=args.task_label)
    elif args.cmd == "gate":
        payload = gate(args.project_root)
    else:
        payload = sync_manifest(args.project_root, manifest_path=args.manifest_path, created_artifacts=args.created_artifact)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
