from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from iteris.project import init_project


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "iteris"


def _load_script(name: str):
    path = PLUGIN_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"iteris_v2_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_plugin_manifest_and_skills_exist():
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "iteris"
    assert manifest["skills"] == "./skills/"
    for skill in [
        "iteris-math",
        "frontier-explorer",
        "task-executor",
        "claim-verifier",
        "frontier-curator",
        "generalization-analyst",
        "reporter",
    ]:
        assert (PLUGIN_ROOT / "skills" / skill / "SKILL.md").exists()
        assert (PLUGIN_ROOT / "skills" / skill / "agents" / "openai.yaml").exists()


def test_workspace_contract_matches_iteris_repo_layout(tmp_path):
    module = _load_script("workspace_contract")
    project = tmp_path / "project"
    init_project(project)

    contract = module.build_workspace_contract(project)

    assert contract["tasks_path"].endswith(str(Path("tasks") / "TASK_POOL.json"))
    assert contract["frontier_index_path"].endswith(str(Path("memory") / "facts" / "FRONTIER_INDEX.json"))
    assert contract["artifact_index_path"].endswith(str(Path("artifacts") / "ARTIFACT_INDEX.jsonl"))
    assert contract["verification_results_dir"].endswith(str(Path("verification") / "results"))


def test_plugin_helpers_are_portable_and_standalone(tmp_path):
    workspace = _load_script("workspace_contract")
    artifacts = _load_script("artifact_helpers")
    facts = _load_script("fact_helpers")
    context = _load_script("context_snapshot")
    verification = _load_script("verification_helpers")

    project = tmp_path / "project"
    init_project(project)
    contract = workspace.build_workspace_contract(project)
    assert Path(contract["project_root"]) == project.resolve()

    created = facts.add_fact(
        project,
        fact_id="fact:project:test-fact",
        source_task="task-test",
        claim_summary="A portable plugin fact.",
        statement="The plugin helper can create a fact file.",
    )
    assert Path(created).exists()
    rebuilt = facts.rebuild_index(project)
    assert rebuilt >= 1

    gate = artifacts.create_workspace(
        project,
        run_id="run-001",
        role="execute",
        mode="proof",
        task_id="task-test",
        focus="portable plugin",
        agent_run_dir=project / "artifacts" / "agent_runs" / "run-001",
    )
    assert gate["artifact_manifest"].endswith("artifact_manifest.json")

    snapshot = context.snapshot(project, limit=3)
    assert snapshot["workflow_authority"].startswith("Use tasks/TASK_POOL.json")

    result = verification.structural_verify(
        project,
        mode="fact",
        claim="Verify the plugin-created fact.",
        artifacts=[str(Path(created).relative_to(project))],
    )
    assert result["mode"] == "fact"
    assert result["request_id"].startswith("verify-")


def test_plugin_scripts_do_not_import_iteris_runtime():
    for path in (PLUGIN_ROOT / "scripts").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "import iteris" not in text
        assert "from iteris" not in text
        assert "_runtime.py" not in text
