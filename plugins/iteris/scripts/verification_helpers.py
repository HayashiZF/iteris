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

from iteris.verification.agent import normalize_agent_output
from iteris.verification.local import verify_local
from iteris.verification.panel import verify_panel


def structural_verify(
    project_root: str | Path,
    *,
    mode: str,
    claim: str,
    artifacts: list[str],
    fact_ids: list[str] | None = None,
    target_artifact: str | None = None,
) -> dict[str, Any]:
    return verify_local(
        Path(project_root),
        mode=mode,
        claim=claim,
        artifacts=[Path(item) for item in artifacts],
        fact_ids=fact_ids,
        target_artifact=Path(target_artifact) if target_artifact else None,
    )


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
    return verify_panel(
        Path(project_root),
        mode=mode,
        claim=claim,
        artifacts=[Path(item) for item in artifacts],
        fact_ids=fact_ids,
        target_artifact=Path(target_artifact) if target_artifact else None,
        runs=runs,
        executor=executor,
        seat_runner=seat_runner,
    )


def normalize_agent_result(
    *,
    request: dict[str, Any],
    payload: dict[str, Any],
    run_dir: str | Path,
    log_path: str | Path,
) -> dict[str, Any]:
    return normalize_agent_output(
        request=request,
        payload=payload,
        run_dir=Path(run_dir),
        log_path=Path(log_path),
    )


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
