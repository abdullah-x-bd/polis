# POLIS v2 Protocol Change Policy

Before freeze, changes motivated by code correctness, impossible states, or zero-cost scripted validation are allowed and documented by Git history.

After freeze, the following require a new protocol version and study fingerprint:

- changing any model slug
- changing governance treatments
- changing pressure values
- changing scenario generation logic
- changing outcome definitions
- changing sample sizes
- changing primary statistical specifications
- changing action limits or friction parameters

Purely operational changes that do not alter the generated prompts, state transitions, scenario assignment, model calls, outcome computation, or analysis estimand may be made only with an explicit audit note.

No paid result may be discarded or rerun under the same experimental key solely because its outcome is inconvenient.
