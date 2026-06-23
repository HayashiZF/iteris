# Runtime Contract

Iteris V2 preserves the current Iteris runtime semantics while removing the dependency on the installed `iteris` CLI.

Important preserved behaviors:

- repo-local workflow authority lives in `tasks/TASK_POOL.json` and `memory/facts/FRONTIER_INDEX.json`
- every subagent run gets a canonical artifact workspace and `artifact_manifest.json`
- durable facts remain structured markdown files plus `FACT_INDEX.jsonl`
- frontier health still decides when fresh exploration is warranted
- verification remains layered: structural, single-agent, and panel
- waits and liveness checks must resolve dead workers or dead verifiers instead of hanging forever

The plugin surface is Codex-first:

- skills hold workflow policy
- Python helpers hold deterministic state mutation and validation
- subagents exchange structured input/output contracts
