# Institution specification

A POLIS institution sits outside the agent prompt and evaluates structured actions.

Each institution must:

1. accept an explicit action schema
2. apply a public rule
3. return an enforceable decision
4. record a human-readable reason
5. identify any detected violation
6. preserve an audit trail

The v0.1 delegation regulator applies one rule:

> An agent may not delegate a task that the principal marked as restricted.

The regulator permits legitimate delegation. It blocks restricted delegation before execution. Later institutions may distribute authority across several regulators or add review procedures.
