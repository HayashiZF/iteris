# Repository Guidelines

## Project Structure & Module Organization
Core Python code lives in `src/iteris/`. Use `commands/` for Typer CLI entrypoints, `agents/` for loop execution, `supervision/` for monitoring logic, `verification/` for verification flows, and `memory/`, `guide/`, `tools/`, and `data/` for supporting subsystems and packaged assets. Tests live in `tests/` and generally mirror the feature or command name, such as `tests/test_monitor_command.py`. Docs live in `docs/`. The Codex plugin bundle is under `plugins/iteris/`. Frontend code for `iteris dashboard` is packaged inside `src/iteris/ui/server` and `src/iteris/ui/client`.

## Build, Test, and Development Commands
Install editable dev dependencies with `python -m pip install -e ".[dev]"`. Run the Python suite with `pytest`. Validate shell scripts with `bash -n install.sh scripts/deploy.sh`. Build distribution artifacts with `python -m build`, then verify them with `twine check dist/*`.

For dashboard work, run `npm ci` once in both `src/iteris/ui/server` and `src/iteris/ui/client`. Use `npx tsc --noEmit` in the server package and `npm run build` in the client package before submitting UI changes.

## Coding Style & Naming Conventions
Follow existing Python style: 4-space indentation, type hints where practical, module docstrings, and `snake_case` for functions, modules, and test names. CLI wiring belongs in `src/iteris/cli.py` or `src/iteris/commands/*.py`; keep business logic in non-command modules. Prefer small focused helpers over large command bodies. TypeScript files in the dashboard use `camelCase` for variables and React component conventions in `*.tsx`.

## Testing Guidelines
Add or update `pytest` coverage for every behavior change. Keep test filenames as `test_<feature>.py`, and favor scenario-oriented names like `test_monitor_setup_fails_without_executor`. For CLI behavior, use `typer.testing.CliRunner`. When touching dashboard packaging or install flows, also run the relevant Node/TypeScript checks.

## Commit & Pull Request Guidelines
This repository currently uses short imperative commit subjects with an optional scope prefix, for example `release: initial public snapshot`. Keep subjects concise and descriptive. Pull requests should explain the user-visible change, note any new commands or flags, link related issues, and include screenshots only for dashboard/UI changes. Mention the exact verification you ran, such as `pytest` or `npm run build`.

## Security & Agent Notes
Iteris launches agents with broad workspace access. Do not hardcode secrets, and avoid checking in generated workspace state from live research runs. When changing project layout, prompts, or plugin contract files under `plugins/iteris/`, update the related docs and tests in the same change.
