---
name: frontier-explorer
description: Portable Codex subagent skill for Iteris frontier exploration. Use when the active route map is blocked, frontier health recommends exploration, or the main loop needs non-obvious route proposals, candidate facts, task-pool additions, or frontier updates without depending on the iteris CLI.
---

# Frontier Explorer

Use this skill for route discovery and frontier reassessment.

Before acting:

- read the workspace contract from `scripts/workspace_contract.py`
- build a context snapshot with `scripts/context_snapshot.py`
- inspect `tasks/TASK_POOL.json`, `memory/facts/FRONTIER_INDEX.json`, and recent verification results

Behavior:

- focus on one frontier or blocker pattern at a time
- prefer targeted reads over broad summaries
- propose candidate facts, task updates, and frontier updates
- keep durable outputs in the provided artifact workspace and update its manifest
- do not claim goal completion

Output expectations:

- summary
- insights
- candidate facts
- task-pool updates
- frontier updates
- created artifacts
- verification requests
- next actions
