---
name: task-executor
description: Codex subagent skill for Iteris task execution. Use when a TASK_POOL item should be advanced in foundation, proof, experiment, or algorithm mode while preserving Iteris artifact manifests, candidate facts, task/frontier updates, and verification handoff without calling iteris tool commands.
---

# Task Executor

Use this skill to advance exactly one `TASK_POOL.json` task.

Read:

- the workspace contract from `scripts/workspace_contract.py`
- the task-pool entry and its dependencies
- relevant facts, frontier data, artifacts, and verification context

Rules:

- operate within the supplied mode: `foundation`, `proof`, `experiment`, or `algorithm`
- keep shared-file edits minimal and observable
- write durable outputs into the provided artifact workspace
- update the artifact manifest as you create artifacts or submit verification
- report blockers explicitly
- do not declare the whole project complete

Use the Python helpers for deterministic operations such as fact writing, manifest updates, task-pool updates, and verification result handling.
