from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TOP_LEVEL = {"schema_version", "parent_project", "source_result", "result_summary", "load_bearing_inputs", "incidental_machinery", "directions", "recommended_order"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_validate = sub.add_parser("validate-analysis")
    p_validate.add_argument("analysis_json")
    args = parser.parse_args(argv)
    payload = validate_analysis_file(Path(args.analysis_json))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get("ok") else 1


def validate_analysis_file(path: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"ok": False, "errors": [f"missing analysis file: {path}"], "warnings": [], "direction_count": 0}
    except json.JSONDecodeError as exc:
        return {"ok": False, "errors": [f"invalid JSON: {exc}"], "warnings": [], "direction_count": 0}
    if not isinstance(payload, dict):
        return {"ok": False, "errors": ["analysis payload must be a JSON object"], "warnings": [], "direction_count": 0}
    missing = sorted(REQUIRED_TOP_LEVEL - set(payload))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")
    directions = payload.get("directions")
    if not isinstance(directions, list) or not directions:
        errors.append("directions must be a non-empty list")
        directions = []
    ids: set[str] = set()
    for idx, direction in enumerate(directions, start=1):
        if not isinstance(direction, dict):
            errors.append(f"direction {idx} must be an object")
            continue
        for key in ("id", "title", "axis", "kind", "target_statement", "first_steps", "success_criteria", "does_not_count", "markdown_file"):
            if key not in direction:
                errors.append(f"direction {idx} missing field: {key}")
        direction_id = str(direction.get("id") or "")
        if direction_id:
            if direction_id in ids:
                errors.append(f"duplicate direction id: {direction_id}")
            ids.add(direction_id)
        if not isinstance(direction.get("first_steps"), list) or not direction.get("first_steps"):
            errors.append(f"direction {idx} requires non-empty first_steps")
        if not isinstance(direction.get("success_criteria"), list) or not direction.get("success_criteria"):
            errors.append(f"direction {idx} requires non-empty success_criteria")
        if not isinstance(direction.get("does_not_count"), list) or not direction.get("does_not_count"):
            warnings.append(f"direction {idx} has empty does_not_count")
    recommended = payload.get("recommended_order")
    if not isinstance(recommended, list):
        errors.append("recommended_order must be a list")
    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "direction_count": len(directions),
    }


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
