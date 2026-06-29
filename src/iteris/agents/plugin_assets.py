"""Plugin skill asset helpers for the canonical Iteris prompt surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


ASSET_ALIASES = {
    "math-explorer": "frontier-explorer",
    "executor": "task-executor",
    "verifier": "claim-verifier",
    "frontier-curator": "frontier-curator",
    "generalization-analyst": "generalization-analyst",
    "reporter": "reporter",
}


def plugin_root(project_root: Path) -> Path:
    return project_root.resolve() / "plugins" / "iteris"


def plugin_skill_dir(project_root: Path, asset_name: str) -> Path:
    skill_name = ASSET_ALIASES.get(asset_name, asset_name)
    return plugin_root(project_root) / "skills" / skill_name


def load_openai_yaml(project_root: Path, asset_name: str) -> dict[str, Any] | None:
    path = plugin_skill_dir(project_root, asset_name) / "agents" / "openai.yaml"
    if not path.is_file():
        return None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def asset_default_prompt(project_root: Path, asset_name: str) -> str | None:
    payload = load_openai_yaml(project_root, asset_name)
    interface = payload.get("interface") if isinstance(payload, dict) else None
    text = interface.get("default_prompt") if isinstance(interface, dict) else None
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()


def skill_body(project_root: Path, asset_name: str) -> str | None:
    path = plugin_skill_dir(project_root, asset_name) / "SKILL.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return text


def asset_instructions(project_root: Path, asset_name: str) -> str | None:
    body = skill_body(project_root, asset_name)
    if body:
        return body
    return asset_default_prompt(project_root, asset_name)


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
