"""Helpers for repo-local `.codex/agents/*.toml` prompt assets.

These prompt assets are curated alongside the repo, but the runtime still
launches subagents through Python. This module bridges the two: when a matching
asset exists, the launcher can prepend its curated developer instructions and
append the concrete runtime request context.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def repo_agent_asset_path(project_root: Path, asset_name: str) -> Path:
    return project_root.resolve() / ".codex" / "agents" / f"{asset_name}.toml"


def load_agent_asset(project_root: Path, asset_name: str) -> dict[str, Any] | None:
    path = repo_agent_asset_path(project_root, asset_name)
    if not path.is_file():
        return None
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def asset_instructions(project_root: Path, asset_name: str) -> str | None:
    payload = load_agent_asset(project_root, asset_name)
    text = payload.get("developer_instructions") if isinstance(payload, dict) else None
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()


def append_runtime_context(base: str | None, *, title: str, sections: dict[str, str]) -> str:
    parts: list[str] = []
    if base and base.strip():
        parts.append(base.strip())
    parts.append(title)
    for heading, body in sections.items():
        body = body.strip()
        if not body:
            continue
        parts.append(f"## {heading}\n{body}")
    return "\n\n".join(parts).rstrip() + "\n"
