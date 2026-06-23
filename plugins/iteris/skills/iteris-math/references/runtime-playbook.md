# Runtime Playbook

Use this order of operations:

1. Read a snapshot with `scripts/workspace_state.py snapshot`.
2. Check unread operator messages before opening new work.
3. If multiple tasks are in `review`, prefer harvesting them before launching more work.
4. If `running` tasks are stale, inspect them before assigning new execution.
5. If frontier health recommends exploration, prefer a frontier-explorer subagent.
6. Otherwise pick the highest-priority ready task and use a task-executor subagent.
7. If a durable claim is load-bearing, prepare verification before building more downstream work on it.
8. Use reporting when a human-readable handoff, review bundle, or progress summary is needed.

Status meanings:

- `ready`: eligible to run when dependencies are satisfied
- `running`: work assigned or in progress
- `review`: output exists and should be harvested or judged
- `blocked`: waits on a concrete blocker
- `done`: task-level completion, not project completion
- `rejected`: disproved or abandoned route
- `paused`: intentionally deferred
