---
name: iteris-math
description: Portable Codex orchestration skill for Iteris-style mathematical research workspaces. Use when Codex should run the main Iteris research loop in a repo that stores workflow state in tasks/TASK_POOL.json, memory/facts/FRONTIER_INDEX.json, verification/, artifacts/, and results/. This skill replaces the older iteris CLI goal loop with direct repo-state inspection, Codex subagents, and bundled Python helpers.
---

# Iteris Math

Use this skill as the main entrypoint for an Iteris-style mathematical research project.

Start by reading the context snapshot from `scripts/context_snapshot.py` and the workspace contract from `scripts/workspace_contract.py`. Treat these repo files as authoritative workflow state:

- `tasks/TASK_POOL.json`
- `memory/facts/FRONTIER_INDEX.json`
- `memory/facts/FACT_INDEX.jsonl`
- `verification/results/`
- `artifacts/ARTIFACT_INDEX.jsonl`

Core loop:

1. Inspect context, recent verification, frontier health, unread messages, and review debt before starting new work.
2. Prefer harvesting stale `review` work and resolving `attention` issues before launching new execution.
3. Launch the `frontier-explorer` subagent when frontier health recommends exploration or blocker patterns repeat.
4. Launch the `task-executor` subagent for focused `foundation`, `proof`, `experiment`, or `algorithm` tasks from `TASK_POOL.json`.
5. Use `claim-verifier` plus `scripts/verification_helpers.py` for real verification work. Preserve the distinction between structural precheck, single-agent verification, and panel verification.
6. Do not mark the project complete until the terminal artifact passes both `assembly` and `goal_success`.

Failure-handling rules:

- A repeated rejection streak means stop revising the same proof directly; pivot to falsification or decomposition changes.
- A stale verification with a dead verifier is salvage or resubmit work, not a reason to stall the loop.
- An under-verified keystone fact should be panel-verified before further downstream buildout.
- A principled stop is a distinct terminal: use it only for a verified obstruction or verified reduction to an open subproblem.

Read these references as needed:

- `references/runtime-contract.md`
- `references/repo-state-schema.md`
- `references/verification-modes.md`
- `references/migration-from-iteris-v1.md`
