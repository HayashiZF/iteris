---
name: iteris-math
description: Portable master skill for Iteris-style mathematical operator/runtime behavior over repo-local state. Use when Codex should supervise an Iteris workspace without relying on the installed `iteris` package, including reading universal file memory, managing the main agentic loop, triaging review debt, handling inbox/operator messages, selecting and orchestrating subagents, maintaining task/frontier state, preparing verification or reporting actions, and driving generalization analysis from files under tasks/, memory/, artifacts/, verification/, results/, and messages/.
---

# Iteris Math

Use this skill as the top-level operator/runtime layer for an Iteris-style mathematical workspace when the workflow should be driven from repo files and bundled scripts rather than the installed `iteris` package.

Start with:

- `python scripts/workspace_state.py snapshot <project-root>`
- `python scripts/operator_loop.py next <project-root>`

Treat these paths as authoritative:

- `tasks/TASK_POOL.json`
- `memory/facts/FACT_INDEX.jsonl`
- `memory/facts/FRONTIER_INDEX.json`
- `verification/requests/`
- `verification/results/`
- `artifacts/ARTIFACT_INDEX.jsonl`
- `messages/inbox.jsonl`
- `messages/ack.jsonl`
- `STATUS.md`

Core runtime loop:

1. Read workspace state, unread messages, recent verification, and task/frontier health.
2. Drain stale `review` or `running` debt before launching new execution when possible.
3. Use `operator_loop.py next` to choose the next control action:
   `harvest_review`, `resolve_messages`, `explore_frontier`, `execute_task`,
   `verify_claim`, `report_state`, or `idle`.
4. Launch the appropriate contracted subagent:
   `frontier-explorer`, `task-executor`, `claim-verifier`, frontier curation,
   generalization analysis, or reporting.
5. Keep durable state changes auditable through task, frontier, fact, artifact,
   message, and verification files.
6. Do not treat a terminal artifact as complete until it has passed both
   assembly-style support checks and goal-success checks in the surrounding workflow.

Failure-handling rules:

- A repeated rejection streak means stop revising the same proof directly; pivot to falsification or decomposition changes.
- A stale verification with a dead verifier is salvage or resubmit work, not a reason to stall the loop.
- An under-verified keystone fact should be panel-verified before further downstream buildout.
- A principled stop is a distinct terminal: use it only for a verified obstruction or verified reduction to an open subproblem.

Read these references when needed:

- `references/repo-state-schema.md`
- `references/runtime-playbook.md`
- `references/subagent-contracts.md`
- `references/verification-modes.md`
- `references/migration-from-iteris-v1.md`

Use these bundled scripts:

- `scripts/workspace_state.py` for compact repo-state snapshots
- `scripts/task_pool.py` for task-pool reads and updates
- `scripts/frontier_state.py` for frontier reads and health heuristics
- `scripts/messages_state.py` for operator inbox and acknowledgement handling
- `scripts/artifacts_state.py` for artifact workspace and manifest bookkeeping
- `scripts/verification_state.py` for verification request/result summaries
- `scripts/operator_loop.py` for next-action selection and orchestration hints

Treat subagent-facing helper commands as a separate plugin surface. In the repo-local plugin,
subagents may call helper scripts under `plugins/iteris/scripts/`, but this master skill should
stay focused on portable state inspection, loop control, and orchestration policy.
