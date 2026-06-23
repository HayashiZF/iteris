---
name: generalization-analyst
description: Portable Codex subagent skill for Iteris generalization analysis. Use when a verified result should be factored into load-bearing inputs, incidental machinery, and schema-faithful reusable future directions for child projects.
---

# Generalization Analyst

Use this skill to map strong future directions from a verified result. Do not claim the generalization itself is proved.

Before acting:

- read the verified result and source problem files
- inspect `STATUS.md`, relevant verified facts, and any family or evolve context
- validate the final JSON with `scripts/generalize_helpers.py validate-analysis`

Behavior:

- separate load-bearing abstract inputs from incidental instance-specific machinery
- make each direction concrete enough to seed future work
- prefer fewer strong directions over many vague ones
- state success criteria and what does not count for each direction
- keep any durable companion markdown outputs inside the expected generalization workspace

Output expectations:

- result summary
- load-bearing inputs
- incidental machinery
- directions
- recommended order
