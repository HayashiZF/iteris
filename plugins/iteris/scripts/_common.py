from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


FACT_REF_RE = re.compile(r"\b(fact:[A-Za-z0-9._:-]+)\b")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def resolve_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def read_text(path: Path, limit: int = 4000) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]


def status_order(status: str) -> int:
    ranking = {
        "review": 0,
        "running": 1,
        "ready": 2,
        "blocked": 3,
        "paused": 4,
        "done": 5,
        "rejected": 6,
    }
    return ranking.get(status, 99)


def slugify(value: str, max_length: int = 64) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    text = text or "item"
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip("-") or "item"


def rel_or_abs(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def infer_project_id(root: Path) -> str:
    status = read_text(root / "STATUS.md", limit=2000)
    for line in status.splitlines():
        if line.lower().startswith("project_id:"):
            return line.split(":", 1)[1].strip() or root.name
    return root.name


def stable_uuid() -> str:
    return str(uuid.uuid4())


def collect_fact_refs(paths: Iterable[Path]) -> list[str]:
    refs: set[str] = set()
    for path in paths:
        if not path.exists() or path.is_dir():
            continue
        refs.update(FACT_REF_RE.findall(path.read_text(encoding="utf-8", errors="replace")))
    return sorted(refs)


def build_verification_request_id(mode: str, claim: str) -> str:
    return f"verify-{now_stamp()}-{slugify(mode + '-' + claim, 40)}"
