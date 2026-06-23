"""Frontier curation subagent prompt and launcher."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from iteris.agents.prompt_assets import append_runtime_context, asset_instructions
from iteris.agents.runtime import create_agent_run


def build_frontier_curator_prompt(request: dict[str, Any]) -> str:
    root = Path(str(request["project_path"]))
    curated = asset_instructions(root, "frontier-curator")
    if curated:
        return append_runtime_context(
            curated,
            title="Runtime Request Context",
            sections={
                "Focus": str(request.get("focus") or "Curate the active frontier and blocker patterns."),
                "Artifact Workspace": json.dumps(
                    {
                        "artifact_workspace": request["artifact_workspace"],
                        "artifact_manifest": request["artifact_manifest"],
                        "artifact_index": request["artifact_index"],
                        "recommended_artifacts": request.get("recommended_artifacts") or {},
                        "run_id": request["run_id"],
                        "output_markdown": request["output_markdown"],
                        "output_json": request["output_json"],
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
            },
        )
    return (
        "Curate the current frontier state. Reassess route health, consolidate blocker "
        "patterns, and produce precise frontier/task updates in the required output files.\n"
    )


def launch_frontier_curator_agent(
    project_root: Path,
    *,
    focus: str,
    detached: bool = False,
    dry_run: bool = False,
    executor: str | None = None,
    executable: str | None = None,
    model: str | None = None,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    return create_agent_run(
        project_root,
        role="frontier_curate",
        focus=focus,
        prompt_builder=build_frontier_curator_prompt,
        detached=detached,
        dry_run=dry_run,
        executor=executor,
        executable=executable,
        model=model,
        reasoning_effort=reasoning_effort,
    )
