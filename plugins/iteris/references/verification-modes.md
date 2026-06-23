# Verification Modes

The portable plugin preserves the current verification vocabulary:

- `source`
- `fact`
- `assembly`
- `goal_success`
- `proof`
- `experiment`
- `code`
- `claim_firewall`
- `principled_stop`

Guidelines:

- `fact` verifies a durable claim and its predecessor evidence
- `assembly` verifies that the terminal artifact is supported by cited verified facts
- `goal_success` verifies the original goal, not a solver-narrowed sub-goal
- `principled_stop` is a verified terminal for obstruction or open-problem reduction, not full success

Panel verification aggregates multiple independent agent verifications and passes only on unanimous accept.
