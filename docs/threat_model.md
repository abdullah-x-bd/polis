# Threat model

## Protected objective

A restriction attached to a task should continue to apply when an agent delegates that task.

## Actors

**Principal:** defines the task and its restriction.

**Primary agent:** receives the task and may delegate work.

**Delegate agent:** executes delegated work.

**Institution:** evaluates structured actions and enforces the delegation rule.

## Initial adversarial behaviour

The primary agent attempts to transfer a restricted task to the delegate agent. The coded regulator can inspect the structured delegation request. It cannot inspect private model reasoning.

## Extensions

Later versions should test indirect descriptions, task decomposition, false task labels, tool-mediated delegation, collusion, regulator shopping, and attacks on audit logs.

## Out of scope for v0.1

POLIS v0.1 does not model real-world cyber exploitation, biological procedures, financial transfers, or physical actions. It tests the structure of institutional enforcement through abstract tasks.
