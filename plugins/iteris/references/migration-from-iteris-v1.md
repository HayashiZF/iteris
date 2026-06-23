# Migration From Iteris v1

The older `.codex/agents/*.toml` files are treated as legacy v1 prompt assets.

What changes in v2:

- Codex skills become the canonical interface
- Python helpers replace `iteris tool ...` for deterministic repo-state operations
- runtime prompt loading reads plugin-owned skills instead of repo-local `.toml` prompt assets
- subagent prompts must absorb newer runtime rules that had drifted into Python prompt builders

What stays compatible:

- repo-local workflow files
- artifact workspace layout
- fact files and fact index
- frontier index and health heuristics
- verification result shapes
