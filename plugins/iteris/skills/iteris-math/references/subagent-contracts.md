# Subagent Contracts

The master skill should orchestrate these roles:

- `frontier-explorer`: propose non-obvious routes and frontier/task suggestions
- `task-executor`: advance exactly one `TASK_POOL.json` item
- `claim-verifier`: adversarially verify facts, proofs, assemblies, or principled stops
- `frontier-curator`: consolidate route health and blocker patterns
- `generalization-analyst`: map verified results into portable future directions
- `reporter`: summarize verified progress, active work, blockers, and next actions

Expected orchestration pattern:

1. Snapshot current repo state.
2. Choose one role for one narrow unit of work.
3. Allocate or reuse a canonical artifact workspace.
4. Let the subagent produce structured output.
5. Harvest the output back into task/frontier/artifact/verification/message state.
6. Repeat from a fresh snapshot.
