# Iteris Workflow Map

This document explains how the repository works end-to-end and where to edit code for each workflow stage. The canonical portable runtime contract is the Iteris plugin under `plugins/iteris/`; `src/iteris/` is the compatibility bridge and local CLI/runtime adapter.

## 1. CLI Entry and Command Routing

All public entrypoints are registered in `src/iteris/cli.py`. If you add a new top-level command or regroup existing ones, start there.

- `iteris monitor` -> `src/iteris/commands/monitor.py`
- `iteris new` -> `src/iteris/commands/new.py`
- `iteris run` -> `src/iteris/commands/run.py`
- `iteris status|attach|stop|review` -> `src/iteris/commands/workflow.py`
- `iteris dashboard` -> `src/iteris/commands/dashboard.py`
- `iteris evolve ...` -> `src/iteris/commands/evolve.py`
- `iteris tool ...` style subsystems live under `src/iteris/commands/`

When behavior feels "global", check `cli.py`, `commands/common.py`, and `project.py` first.

## 2. Project Creation Workflow

Project creation starts in `src/iteris/commands/new.py`, which delegates filesystem layout to `src/iteris/project.py`.

Main flow:

1. Validate source and target directory in `perform_new_project()`.
2. Create the canonical workspace layout with `init_project()` in `project.py`.
3. Import references with `references.py`.
4. Run deterministic first-pass intake with `bootstrap.run_once()`.
5. Initialize git/checkpoint state via `gitops.py`.
6. Write status and guide files such as `STATUS.md`, `.iteris/INDEX.md`, and `docs/OPERATOR.md`.

Edit here when changing project skeletons, default files, or initial checkpoint contents.

## 3. Bootstrap and Initial Memory

Bootstrap logic lives in `src/iteris/bootstrap.py`. It reads the copied source from `sources/`, extracts a rough problem statement, creates a first task, writes an initial fact, and submits a structural verification.

Key side effects:

- `artifacts/runs/run-*/`
- `tasks/TASK_POOL.json`
- `memory/facts/FACT_INDEX.jsonl`
- `verification/results/*.json`
- `STATUS.md`

If initialization should create different first tasks, facts, or verification claims, edit `run_once()`.

## 4. Human Supervision Workflow

`iteris monitor` is the human-facing coordinator in `src/iteris/commands/monitor.py`.

It:

- checks environment readiness through `guide/environment.py`
- refreshes guide/index files via `guide/index.py`
- builds lookup context with `guide/lookups.py`
- writes a handoff markdown file with `guide/context.py`
- launches Codex or Claude using executor helpers in `executors.py`

Change monitor behavior here if you want different setup gating, handoff prompts, locale behavior, or wizard flow.

## 5. Main Agent Run Workflow

`iteris run` in `src/iteris/commands/run.py` is the core research-loop launcher.

Main responsibilities:

1. Resolve goal and target artifact.
2. Rebuild prompt context, including generalization lineage from `generalize.py`.
3. Write `.iteris/goal_prompt.txt`.
4. Prepare executor home directories and environment.
5. Launch the worker in tmux or foreground mode.
6. Record run metadata and log paths.

Supporting logic is split across:

- `commands/goal/` for prompt assembly, tmux helpers, trust setup, and log plumbing
- `executors.py` for Codex/Claude command construction
- `codex_logs.py` for child environment normalization

If a run launches incorrectly, inspect `run.py` first, then `commands/goal/`.

## 6. Status, Recovery, and Review

Operational control sits in `src/iteris/commands/workflow.py` and `src/iteris/commands/recover.py`.

- `status()` reads `.iteris/current_run.json`, liveness, fact summaries, verification results, and git state.
- `attach()` and `stop()` manage tmux sessions.
- `review()` bundles reviewer-facing artifacts and finalization signals.
- `recover()` repairs dead sessions, orphaned work, and stale task ownership.

For bugs around session naming, liveness, or recovery semantics, also inspect `project.session_slug()`, `liveness.py`, and `commands/goal/`.

## 7. Verification Workflow

Verification entrypoints are in `src/iteris/commands/verification.py`.

- structural/local verification -> `verification/local.py`
- agent-based verification -> `verification/agent.py`
- multi-seat panel verification -> `verification/panel.py`

This layer writes requests and normalized results under `verification/`. If a workflow should gate on stronger or weaker evidence, update verification modes before changing downstream status logic.

## 8. Dashboard Workflow

`iteris dashboard` launches from `src/iteris/commands/dashboard.py`.

Backend/frontend split:

- server: `src/iteris/ui/server`
- client: `src/iteris/ui/client`
- JSON data contract: `src/iteris/commands/ui.py` and `ui_evolve.py`

The dashboard installs Node dependencies, builds the client when stale, starts the local server, and serves project data by shelling back into `iteris tool ui ...`.

## 9. Evolve Family Workflow

Family generalization is driven by:

- CLI: `src/iteris/commands/evolve.py`
- state model: `src/iteris/evolve.py`
- supervisor policy: `src/iteris/supervision/profiles/evolve.py`
- child seeding/context: `src/iteris/generalize.py` and `generalize_analyze.py`

The evolve supervisor reads each child project's published state, schedules or curates directions, launches child runs, and records family memory. Edit `supervision/profiles/evolve.py` for orchestration policy; edit `evolve.py` for durable state semantics.

## 10. Canonical Plugin Runtime

The Codex plugin lives in `plugins/iteris/`.

- manifest: `plugins/iteris/.codex-plugin/plugin.json`
- shared scripts: `plugins/iteris/scripts/`
- skills: `plugins/iteris/skills/`
- contract/reference docs: `plugins/iteris/references/`

This is now the authoritative portable workflow layer:

- `skills/iteris-math/` is the master orchestration contract
- the six subagent skills hold curated role prompts
- `scripts/*.py` are the standalone deterministic helpers for Python-ready devices

Use `src/iteris/` when you need CLI adapters, executor launch glue, or local desktop/runtime conveniences that bridge onto the plugin contract.
