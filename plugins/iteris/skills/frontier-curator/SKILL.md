---
name: frontier-curator
description: Portable Codex subagent skill for Iteris frontier curation. Use when the operator should reassess route health, consolidate blocker patterns, close stale routes, or propose precise frontier and task-pool updates without depending on the iteris CLI.
---

# Frontier Curator

Use this skill to curate the route map rather than solve the underlying research task.

Before acting:

- read the workspace contract from `scripts/workspace_contract.py`
- build a context snapshot with `scripts/context_snapshot.py`
- inspect `tasks/TASK_POOL.json`, `memory/facts/FRONTIER_INDEX.json`, recent facts, and recent verification outputs

Behavior:

- focus on one frontier cluster or blocker family at a time
- distinguish active promise from repeated low-yield churn
- justify route closures or downgrades with blocker facts, failed-path evidence, or verification outcomes
- propose exact next executable tasks when opening or upgrading a route
- keep durable artifacts in the provided artifact workspace and update its manifest
- do not fabricate verified facts or claim project completion

Output expectations:

- summary
- health assessment
- frontier updates
- task-pool updates
- created artifacts
- next actions
