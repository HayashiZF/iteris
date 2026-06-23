# Repo State Schema

The default workspace contract assumes these repo-local paths:

- `sources/`
- `references/`
- `results/`
- `tasks/TASK_POOL.json`
- `memory/facts/`
- `memory/facts/FACT_INDEX.jsonl`
- `memory/facts/FRONTIER_INDEX.json`
- `artifacts/`
- `artifacts/ARTIFACT_INDEX.jsonl`
- `verification/requests/`
- `verification/results/`

Per-run artifact workspaces remain:

- `artifacts/<kind>/<task-label>/<run-id>/artifact_manifest.json`

The plugin should prefer compatibility with existing Iteris repos over inventing a new storage layout.
