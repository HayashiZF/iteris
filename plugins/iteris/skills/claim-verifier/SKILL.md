---
name: claim-verifier
description: Portable Codex verification skill for Iteris-style workspaces. Use when Codex needs to verify facts, proofs, experiments, assemblies, goal success, code claims, or principled stops against the Iteris adversarial verification contract while preserving repo-local verification records and result schemas.
---

# Claim Verifier

Use this skill for adversarial verification.

Keep these distinctions intact:

- structural precheck
- single-agent verification
- panel verification

Supported modes:

- `source`
- `fact`
- `assembly`
- `goal_success`
- `proof`
- `experiment`
- `code`
- `claim_firewall`
- `principled_stop`

Behavior:

- verify the claim against the cited artifacts and fact graph, not just schema shape
- report `critical_errors`, `gaps`, and `repair_hints`
- preserve checked artifact and checked fact reporting
- treat principled stop as distinct from full success

Use `references/verification-modes.md` for the mode contract and `scripts/verification_helpers.py` for deterministic normalization and persistence.
